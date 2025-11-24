"""
Quick test of the data loading pipeline without full PyTorch training.
Tests that we can load audio, generate mel spectrograms, and prepare data.
"""
import os
import sys
import yaml
import numpy as np
import librosa
from tqdm import tqdm

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.features.melspec import wav_to_logmel
from src.data.dataset_loader import load_config

def test_data_pipeline():
    """Test the data loading and mel generation pipeline."""
    print("="*60)
    print("Testing Data Pipeline (without PyTorch)")
    print("="*60)
    
    # Load config
    cfg = load_config("conf/config.yaml")
    print(f"\n✓ Config loaded")
    print(f"  Sample rate: {cfg['audio']['sample_rate']}")
    print(f"  Window: {cfg['audio']['window_seconds']}s")
    print(f"  Mels: {cfg['audio']['n_mels']}")
    
    # Load metadata
    import pandas as pd
    meta = pd.read_csv(cfg["data"]["metadata"])
    print(f"\n✓ Metadata loaded: {len(meta)} clips")
    
    # Load split IDs
    splits = {}
    for split_name in ["train", "val", "test_ood"]:
        with open(cfg["data"]["splits"][split_name], "r") as f:
            ids = [line.strip() for line in f if line.strip()]
        splits[split_name] = ids
        print(f"  {split_name}: {len(ids)} clips")
    
    # Test loading a few audio files and generating mels
    print(f"\n{'='*60}")
    print("Testing Audio Loading & Mel Generation")
    print("="*60)
    
    train_subset = meta[meta["clip_id"].isin(splits["train"])][:5]
    
    for idx, row in tqdm(train_subset.iterrows(), total=len(train_subset), desc="Processing"):
        try:
            # Load audio
            audio_path = os.path.join(cfg["data"]["raw_dir"], row["filename"])
            if not os.path.exists(audio_path):
                print(f"\n⚠️  File not found: {audio_path}")
                continue
            
            y, sr = librosa.load(audio_path, sr=cfg["audio"]["sample_rate"])
            
            # Generate mel spectrogram
            mel = wav_to_logmel(y, sr, cfg)
            
            print(f"\n✓ {row['clip_id']} ({row['species_code']})")
            print(f"  Audio: {len(y)/sr:.1f}s, {len(y)} samples")
            print(f"  Mel shape: {mel.shape} (n_mels × time_frames)")
            
        except Exception as e:
            print(f"\n❌ Error processing {row['clip_id']}: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Data pipeline test completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Fix PyTorch installation issues (DLL dependencies)")
    print("2. Run full training: python src/models/train.py")
    print("3. Implement evaluation scripts (Issue #3)")

if __name__ == "__main__":
    test_data_pipeline()
