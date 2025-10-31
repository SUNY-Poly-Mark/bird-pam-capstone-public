import os
import yaml
import pandas as pd
import librosa
import numpy as np
from tqdm import tqdm

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

if __name__ == "__main__":
    cfg = load_config()
    for split in ["train", "val", "test_ood"]:
        data = prepare_split(cfg, split)
        print(f"\n✅ Loaded {len(data)} files for {split} split.\n")
