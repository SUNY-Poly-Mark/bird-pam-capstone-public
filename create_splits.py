"""
Generate train/val/test split files from downloaded audio data.
Creates stratified splits ensuring each species is represented in each split.
"""

import os
from pathlib import Path
from collections import defaultdict
import random

# Set random seed for reproducibility
random.seed(42)

# Configuration
DATA_DIR = Path(r"H:\My Drive\Colab Notebooks\DSA 598\data\raw")
SPLITS_DIR = Path(r"c:\Users\darcyme\Documents\Poly\Project\bird-pam-capstone\conf\splits")
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

print(f"Scanning audio files in: {DATA_DIR}")

# Collect all recording IDs by species
species_recordings = defaultdict(list)

for species_folder in DATA_DIR.iterdir():
    if not species_folder.is_dir():
        continue
    
    species_name = species_folder.name
    print(f"\nProcessing: {species_name}")
    
    for audio_file in species_folder.glob("*.wav"):
        # Extract recording ID (e.g., "405825" from "405825_Mike_Ashby_9s.wav")
        recording_id = audio_file.stem.split('_')[0]
        species_recordings[species_name].append(recording_id)
    
    print(f"  Found {len(species_recordings[species_name])} recordings")

# Create stratified splits
train_ids = []
val_ids = []
test_ids = []

print("\n" + "="*60)
print("Creating stratified splits...")
print("="*60)

for species, recordings in sorted(species_recordings.items()):
    # Shuffle recordings for this species
    random.shuffle(recordings)
    
    n_total = len(recordings)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    # Split recordings
    train = recordings[:n_train]
    val = recordings[n_train:n_train + n_val]
    test = recordings[n_train + n_val:]
    
    train_ids.extend(train)
    val_ids.extend(val)
    test_ids.extend(test)
    
    print(f"\n{species}:")
    print(f"  Total: {n_total} | Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")

# Sort IDs for consistency
train_ids.sort()
val_ids.sort()
test_ids.sort()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total species: {len(species_recordings)}")
print(f"Total recordings: {sum(len(r) for r in species_recordings.values())}")
print(f"\nSplit sizes:")
print(f"  Train: {len(train_ids)} ({len(train_ids)/sum(len(r) for r in species_recordings.values())*100:.1f}%)")
print(f"  Val:   {len(val_ids)} ({len(val_ids)/sum(len(r) for r in species_recordings.values())*100:.1f}%)")
print(f"  Test:  {len(test_ids)} ({len(test_ids)/sum(len(r) for r in species_recordings.values())*100:.1f}%)")

# Create splits directory if it doesn't exist
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

# Write split files
print(f"\nWriting split files to: {SPLITS_DIR}")

with open(SPLITS_DIR / 'train_ids.txt', 'w') as f:
    for recording_id in train_ids:
        f.write(f"XC{recording_id}\n")
print(f"  ✓ train_ids.txt ({len(train_ids)} IDs)")

with open(SPLITS_DIR / 'val_ids.txt', 'w') as f:
    for recording_id in val_ids:
        f.write(f"XC{recording_id}\n")
print(f"  ✓ val_ids.txt ({len(val_ids)} IDs)")

with open(SPLITS_DIR / 'test_ood_ids.txt', 'w') as f:
    for recording_id in test_ids:
        f.write(f"XC{recording_id}\n")
print(f"  ✓ test_ood_ids.txt ({len(test_ids)} IDs)")

print("\n✓ Split files created successfully!")
print("\nNext steps:")
print("  1. Open train_on_colab.ipynb in Google Colab")
print("  2. Run cell 1 to mount Drive")
print("  3. Run cell 2 and upload the new split files from conf/splits/")
