import numpy as np
import matplotlib.pyplot as plt
import os

# Path to processed features
mels_dir = "data/processed/mels"

# List of saved numpy files
files = [f for f in os.listdir(mels_dir) if f.endswith(".npy")]
print("Available feature files:", files)

# Load one
first_file = os.path.join(mels_dir, files[0])
features = np.load(first_file)  # shape: (num_windows, n_mels, frames)

print("Feature shape:", features.shape)
first_window = features[0]  # pick the first 5-second segment

# Plot it
plt.figure(figsize=(8, 4))
plt.imshow(first_window, aspect="auto", origin="lower", cmap="magma")
plt.colorbar(label="dB")
plt.title(f"Spectrogram: {os.path.basename(first_file)} (1st 5s window)")
plt.xlabel("Time frames")
plt.ylabel("Mel frequency bins")
plt.tight_layout()
plt.show()
