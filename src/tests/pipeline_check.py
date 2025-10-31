import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import numpy as np
import yaml
import librosa
import matplotlib.pyplot as plt
from src.data.dataset_loader import load_config, prepare_split
from src.features.compute_normalization import compute_stats

# --- Load config and normalization ---
cfg = load_config()
norm_path = "conf/normalization.yaml"
if os.path.exists(norm_path):
    with open(norm_path) as f:
        norm = yaml.safe_load(f)
    mel_mean, mel_std = norm["mel_mean"], norm["mel_std"]
else:
    mel_mean, mel_std = 0.0, 1.0
print(f"✅ Loaded normalization: mean={mel_mean:.4f}, std={mel_std:.4f}")

# --- Load one split (train) ---
data = prepare_split(cfg, "train")
print(f"\n✅ Loaded {len(data)} clips for train split.")

# --- Convert to mel spectrograms ---
for sample in data:
    y, sr = sample["waveform"], sample["sr"]
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_norm = (mel_db - mel_mean) / mel_std

    # Display shape & summary
    print(f"{sample['clip_id']}  →  mel shape {mel_norm.shape}, mean {mel_norm.mean():.3f}, std {mel_norm.std():.3f}")

    # Plot the first one only
    plt.figure(figsize=(8, 4))
    plt.imshow(mel_norm, aspect="auto", origin="lower", cmap="magma")
    plt.title(f"{sample['clip_id']} normalized mel")
    plt.colorbar(label="Normalized dB")
    plt.tight_layout()
    plt.show()
    break  # plot only first clip
