import os
import numpy as np
import librosa
import yaml
import pandas as pd
from tqdm import tqdm

def load_config(path="conf/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_metadata(cfg):
    return pd.read_csv(cfg["data"]["metadata"])

def load_split_ids(cfg, split):
    path = cfg["data"]["splits"][split]
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def make_mels(y, sr, n_mels=128, hop_length=512, n_fft=2048):
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels,
                                       n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.power_to_db(S, ref=np.max)
    return S_db

def process_split(cfg, split):
    meta = load_metadata(cfg)
    ids = load_split_ids(cfg, split)
    subset = meta[meta["clip_id"].isin(ids)]
    out_dir = os.path.join("data", "processed", "mels", split)
    os.makedirs(out_dir, exist_ok=True)

    for _, row in tqdm(subset.iterrows(), total=len(subset), desc=f"Building {split}"):
        audio_path = os.path.join("data", "raw", row["filename"])
        if not os.path.exists(audio_path):
            print(f"⚠️ Missing: {audio_path}")
            continue
        y, sr = librosa.load(audio_path, sr=32000)
        mel = make_mels(y, sr)
        out_path = os.path.join(out_dir, f"{row['clip_id']}.npy")
        np.save(out_path, mel)

    print(f"✅ {split} done — {len(subset)} clips processed → {out_dir}")

if __name__ == "__main__":
    cfg = load_config()
    for split in ["train", "val", "test_ood"]:
        process_split(cfg, split)
