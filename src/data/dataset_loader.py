import os
import yaml
import pandas as pd
import librosa
import numpy as np
from tqdm import tqdm

# PyTorch imports are optional - only needed for Dataset class
try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available. BirdAudioDataset and DataLoader functionality will be limited.")

def load_config(path="conf/config.yaml"):
    """Read project configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_metadata(cfg):
    """Load full metadata table."""
    meta = pd.read_csv(cfg["data"]["metadata"])
    meta["filename"] = meta["filename"].apply(lambda x: x.strip())
    return meta

def load_split_ids(split_path):
    """Load IDs (XC numbers) from text files."""
    with open(split_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def subset_metadata(meta, ids):
    """Subset metadata by clip IDs."""
    return meta[meta["clip_id"].isin(ids)].reset_index(drop=True)

def load_audio(file_path, sr=32000):
    """Load a .wav file and return waveform + sample rate."""
    y, sr = librosa.load(file_path, sr=sr)
    return y, sr

def create_fixed_windows(waveform, sr, window_seconds, hop_seconds):
    """
    Convert variable-length audio to fixed-length windows.
    
    Args:
        waveform: Audio waveform array
        sr: Sample rate
        window_seconds: Target window length in seconds
        hop_seconds: Stride between overlapping windows in seconds
        
    Returns:
        List of fixed-length windows (each of length window_samples)
    """
    window_samples = int(window_seconds * sr)
    hop_samples = int(hop_seconds * sr)
    
    audio_length = len(waveform)
    
    # Case 1: Audio is shorter than window - pad with zeros
    if audio_length < window_samples:
        padded = np.zeros(window_samples, dtype=waveform.dtype)
        padded[:audio_length] = waveform
        return [padded]
    
    # Case 2: Audio is exactly window length (or very close)
    if audio_length <= window_samples + hop_samples // 2:
        # Crop or pad to exact window size
        return [waveform[:window_samples]]
    
    # Case 3: Audio is longer - create overlapping windows
    windows = []
    start = 0
    while start + window_samples <= audio_length:
        windows.append(waveform[start:start + window_samples])
        start += hop_samples
    
    # Handle last segment if there's remaining audio
    if start < audio_length and len(windows) > 0:
        # Create final window from the last window_samples of audio
        windows.append(waveform[-window_samples:])
    
    return windows


def prepare_split(cfg, split_name):
    """Load metadata and audio paths for a given split."""
    meta = load_metadata(cfg)
    ids = load_split_ids(cfg["data"]["splits"][split_name])
    subset = subset_metadata(meta, ids)

    data = []
    for _, row in tqdm(subset.iterrows(), total=len(subset), desc=f"Loading {split_name}"):
        audio_path = os.path.join("data/raw", row["filename"])
        if not os.path.exists(audio_path):
            print(f"⚠️ Missing file: {audio_path}")
            continue
        y, sr = load_audio(audio_path)
        data.append({"clip_id": row["clip_id"], "species": row["species_code"], "waveform": y, "sr": sr})
    return data


if TORCH_AVAILABLE:
    class BirdAudioDataset(Dataset):
        """PyTorch Dataset for bird audio with fixed-length windowing."""
        
        def __init__(self, cfg, split_name, use_windowing=True):
            """
            Args:
                cfg: Configuration dict
                split_name: One of 'train', 'val', 'test_ood'
                use_windowing: If True, apply fixed-length windowing
            """
            self.cfg = cfg
            self.split_name = split_name
            self.use_windowing = use_windowing
            self.window_seconds = cfg["audio"]["window_seconds"]
            self.hop_seconds = cfg["audio"]["hop_seconds"]
            self.sample_rate = cfg["audio"]["sample_rate"]
            
            # Load metadata
            self.meta = load_metadata(cfg)
            self.ids = load_split_ids(cfg["data"]["splits"][split_name])
            self.subset = subset_metadata(self.meta, self.ids)
            
            # Create mapping from species to integer labels
            self.species_list = sorted(self.subset["species_code"].unique())
            self.species_to_idx = {sp: i for i, sp in enumerate(self.species_list)}
            
            # Build index of (clip_index, window_index) pairs
            self.index = []
            for idx, row in self.subset.iterrows():
                audio_path = os.path.join("data/raw", row["filename"])
                if not os.path.exists(audio_path):
                    continue
                
                if use_windowing:
                    # Estimate number of windows based on duration
                    duration = row["duration_s"]
                    window_samples = int(self.window_seconds * self.sample_rate)
                    hop_samples = int(self.hop_seconds * self.sample_rate)
                    audio_samples = int(duration * self.sample_rate)
                    
                    if audio_samples < window_samples:
                        num_windows = 1
                    elif audio_samples <= window_samples + hop_samples // 2:
                        num_windows = 1
                    else:
                        # Calculate number of overlapping windows
                        num_windows = 1 + (audio_samples - window_samples + hop_samples - 1) // hop_samples
                    
                    for window_idx in range(num_windows):
                        self.index.append((idx, window_idx))
                else:
                    # No windowing - one entry per clip
                    self.index.append((idx, 0))
        
        def __len__(self):
            return len(self.index)
        
        def __getitem__(self, idx):
            clip_idx, window_idx = self.index[idx]
            row = self.subset.iloc[clip_idx]
            
            # Load audio
            audio_path = os.path.join("data/raw", row["filename"])
            y, sr = load_audio(audio_path, sr=self.sample_rate)
            
            # Apply windowing if enabled
            if self.use_windowing:
                windows = create_fixed_windows(y, sr, self.window_seconds, self.hop_seconds)
                waveform = windows[window_idx]
            else:
                waveform = y
            
            # Get label
            species = row["species_code"]
            label = self.species_to_idx[species]
            
            return {
                "waveform": torch.FloatTensor(waveform),
                "label": torch.LongTensor([label])[0],
                "clip_id": row["clip_id"],
                "species": species,
                "window_idx": window_idx
            }


    def bucket_collate_fn(batch):
        """
        Collate function that groups samples by similar lengths.
        For fixed-length windows, this is straightforward batching.
        """
        waveforms = torch.stack([item["waveform"] for item in batch])
        labels = torch.stack([item["label"] for item in batch])
        clip_ids = [item["clip_id"] for item in batch]
        species = [item["species"] for item in batch]
        window_indices = [item["window_idx"] for item in batch]
        
        return {
            "waveforms": waveforms,
            "labels": labels,
            "clip_ids": clip_ids,
            "species": species,
            "window_indices": window_indices
        }


if __name__ == "__main__":
    cfg = load_config()
    
    # Test original functionality
    print("=" * 60)
    print("Testing original prepare_split() function:")
    print("=" * 60)
    for split in ["train", "val", "test_ood"]:
        data = prepare_split(cfg, split)
        print(f"\n✅ Loaded {len(data)} files for {split} split.\n")
    
    # Test new windowing functionality
    if TORCH_AVAILABLE:
        print("\n" + "=" * 60)
        print("Testing new BirdAudioDataset with windowing:")
        print("=" * 60)
        
        for split in ["train", "val", "test_ood"]:
            dataset = BirdAudioDataset(cfg, split, use_windowing=True)
            print(f"\n{split} split:")
            print(f"  - Total windows: {len(dataset)}")
            print(f"  - Number of species: {len(dataset.species_list)}")
            print(f"  - Species: {dataset.species_list}")
            
            # Test loading a sample
            if len(dataset) > 0:
                sample = dataset[0]
                print(f"  - Sample shape: {sample['waveform'].shape}")
                print(f"  - Expected samples: {int(cfg['audio']['window_seconds'] * cfg['audio']['sample_rate'])}")
                print(f"  - Label: {sample['label']} ({sample['species']})")
        
        # Test DataLoader with collate function
        print("\n" + "=" * 60)
        print("Testing DataLoader with bucket_collate_fn:")
        print("=" * 60)
        
        if len(dataset) > 0:
            dataloader = DataLoader(
                dataset,
                batch_size=4,
                shuffle=True,
                collate_fn=bucket_collate_fn
            )
            
            batch = next(iter(dataloader))
            print(f"\n✅ Batch loaded successfully:")
            print(f"  - Waveforms shape: {batch['waveforms'].shape}")
            print(f"  - Labels shape: {batch['labels'].shape}")
            print(f"  - Clip IDs: {batch['clip_ids']}")
            print(f"  - Species: {batch['species']}")
    else:
        print("\n⚠️ PyTorch not available. Skipping BirdAudioDataset tests.")
