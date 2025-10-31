import os
import numpy as np
import yaml
from tqdm import tqdm

def load_config(path="conf/config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def gather_all_mels(cfg):
    """Load all mel files from all splits and concatenate into one big array."""
    all_values = []
    base_dir = os.path.join("data", "processed", "mels")
    for split in ["train", "val", "test_ood"]:
        split_dir = os.path.join(base_dir, split)
        if not os.path.exists(split_dir):
            print(f"⚠️ No folder for {split}")
            continue
        for file in tqdm(os.listdir(split_dir), desc=f"Reading {split}"):
            if not file.endswith(".npy"):
                continue
            mel = np.load(os.path.join(split_dir, file))
            all_values.append(mel.flatten())
    return np.concatenate(all_values)

def compute_stats(values):
    """Compute mean and standard deviation."""
    mean = np.mean(values)
    std = np.std(values)
    return float(mean), float(std)

if __name__ == "__main__":
    cfg = load_config()
    values = gather_all_mels(cfg)
    mean, std = compute_stats(values)
    print(f"\n✅ Mel stats → mean={mean:.4f}, std={std:.4f}")

    # Save results to conf/normalization.yaml
    norm_path = "conf/normalization.yaml"
    with open(norm_path, "w") as f:
        yaml.dump({"mel_mean": mean, "mel_std": std}, f)
    print(f"📁 Saved normalization values → {norm_path}")
