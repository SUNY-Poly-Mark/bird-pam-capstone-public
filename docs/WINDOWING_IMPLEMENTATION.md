# Fixed-Length Window Handling Implementation

## Overview
This document describes the implementation of fixed-length window handling for variable-length audio clips, addressing GitHub issue #1.

## Problem Statement
Bird audio recordings from Xeno-canto have variable durations (typically 5-60 seconds). Machine learning models require fixed-length inputs for efficient batching and training. We needed a solution to:
1. **Pad short clips** (<5s) to the target length
2. **Crop long clips** (>5s) into overlapping windows
3. **Handle exact-length clips** (~5s) efficiently
4. **Support efficient batching** with PyTorch DataLoader

## Solution Design

### Configuration
From `conf/config.yaml`:
```yaml
audio:
  sample_rate: 32000      # 32 kHz sampling
  window_seconds: 5.0     # Target window length
  hop_seconds: 2.5        # Stride between overlapping windows
```

This means:
- **Target window**: 5 seconds = 160,000 samples
- **Hop/stride**: 2.5 seconds = 80,000 samples
- **Overlap**: 50% between consecutive windows

### Core Windowing Function

The `create_fixed_windows()` function in `src/data/dataset_loader.py` handles three cases:

#### Case 1: Short Audio (<5s)
```python
if audio_length < window_samples:
    # Pad with zeros to reach target length
    padded = np.zeros(window_samples, dtype=waveform.dtype)
    padded[:audio_length] = waveform
    return [padded]
```
- **Example**: 3-second clip → padded to 5 seconds with 2 seconds of silence
- **Output**: Single window of 160,000 samples

#### Case 2: Exact Length (~5s)
```python
if audio_length <= window_samples + hop_samples // 2:
    # Audio is approximately the target length
    return [waveform[:window_samples]]
```
- **Example**: 5.5-second clip → cropped to exactly 5 seconds
- **Output**: Single window of 160,000 samples
- **Rationale**: Clips within ~1.25s of target don't need multiple windows

#### Case 3: Long Audio (>6.25s)
```python
windows = []
start = 0
while start + window_samples <= audio_length:
    windows.append(waveform[start:start + window_samples])
    start += hop_samples

# Handle last segment
if start < audio_length and len(windows) > 0:
    windows.append(waveform[-window_samples:])
```
- **Example**: 15-second clip → 6 overlapping windows
  - Window 0: 0.0-5.0s
  - Window 1: 2.5-7.5s
  - Window 2: 5.0-10.0s
  - Window 3: 7.5-12.5s
  - Window 4: 10.0-15.0s
  - Window 5: Last 5 seconds (10.0-15.0s, same as window 4 start)
- **Output**: Multiple windows of 160,000 samples each

### PyTorch Dataset Integration

The `BirdAudioDataset` class provides PyTorch-compatible data loading:

```python
class BirdAudioDataset(Dataset):
    def __init__(self, cfg, split_name, use_windowing=True):
        # Load metadata and build index of (clip, window) pairs
        # Each entry represents one fixed-length window
        
    def __getitem__(self, idx):
        # Load audio file
        # Apply windowing to extract the specific window
        # Return dict with waveform, label, metadata
```

**Key features**:
- **Lazy loading**: Audio files loaded on-demand
- **Index mapping**: Pre-computes (clip_index, window_index) pairs for efficient access
- **Metadata tracking**: Preserves clip_id, species, and window position
- **Optional windowing**: Can disable for variable-length use cases

### Batching with Collate Function

The `bucket_collate_fn()` function handles batching:

```python
def bucket_collate_fn(batch):
    waveforms = torch.stack([item["waveform"] for item in batch])
    labels = torch.stack([item["label"] for item in batch])
    # ... preserve metadata lists
    return {"waveforms": waveforms, "labels": labels, ...}
```

Since all windows are fixed-length (160,000 samples), batching is straightforward:
- **Input**: List of dict items from Dataset
- **Output**: Batch dict with stacked tensors
- **Shape**: `(batch_size, 160000)` for waveforms

## Testing Results

Tested with synthetic audio of various lengths:

| Audio Length | Expected Windows | Actual Windows | Status |
|--------------|------------------|----------------|--------|
| 3.0s         | 1 (padded)       | 1              | ✅     |
| 5.0s         | 1 (exact)        | 1              | ✅     |
| 6.0s         | 1 (cropped)      | 1              | ✅     |
| 15.0s        | 6 (overlapping)  | 6              | ✅     |

All windows verified to be exactly 160,000 samples.

## Usage Examples

### Basic Usage (without PyTorch)
```python
from src.data.dataset_loader import load_audio, create_fixed_windows
import yaml

# Load config
with open("conf/config.yaml") as f:
    cfg = yaml.safe_load(f)

# Load audio
audio, sr = load_audio("path/to/audio.wav", sr=cfg["audio"]["sample_rate"])

# Create fixed-length windows
windows = create_fixed_windows(
    audio, 
    sr, 
    window_seconds=cfg["audio"]["window_seconds"],
    hop_seconds=cfg["audio"]["hop_seconds"]
)

print(f"Generated {len(windows)} windows")
print(f"Each window shape: {windows[0].shape}")
```

### PyTorch DataLoader Usage (requires PyTorch)
```python
from src.data.dataset_loader import BirdAudioDataset, bucket_collate_fn
from torch.utils.data import DataLoader

# Create dataset with windowing enabled
dataset = BirdAudioDataset(cfg, split_name="train", use_windowing=True)

# Create DataLoader
dataloader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,
    collate_fn=bucket_collate_fn,
    num_workers=4
)

# Iterate over batches
for batch in dataloader:
    waveforms = batch["waveforms"]  # Shape: (32, 160000)
    labels = batch["labels"]        # Shape: (32,)
    # ... train model
```

## Implementation Notes

### Design Decisions

1. **Zero-padding for short clips**: Simple and preserves all original audio. Alternative (repeating audio) would introduce artifacts.

2. **50% overlap for long clips**: Balances:
   - Data augmentation (more training examples)
   - Temporal coverage (captures transitions)
   - Computational cost (2x windows vs. no overlap)

3. **Final window handling**: Long clips get a final window from the end, which may overlap significantly with the previous window. This ensures no audio is lost.

4. **Optional PyTorch dependency**: Core windowing logic (`create_fixed_windows()`) works without PyTorch, making it reusable for preprocessing or other frameworks.

### Limitations

1. **Padding strategy**: Zero-padding may confuse models if not handled during training (e.g., attention masks, or training with mixed-length clips)

2. **Fixed parameters**: Window and hop lengths are global. Future enhancement could support per-species or per-recording adaptive windowing.

3. **Memory usage**: Dataset loads entire audio file into memory for each `__getitem__` call. For very large datasets, consider:
   - Pre-processing windows to disk
   - Memory-mapped numpy arrays
   - Streaming audio loading

4. **Window count estimation**: The Dataset class pre-estimates window counts based on duration metadata. If duration is inaccurate, this could cause index errors.

## Future Enhancements

1. **Attention masks**: Add binary masks to indicate padding regions
2. **Adaptive windowing**: Adjust window length based on species vocalizations
3. **Pre-computed windows**: Cache windows to disk for faster training
4. **Data augmentation**: Time-stretching, pitch-shifting within windows
5. **Multi-label support**: Handle clips with multiple species
6. **Validation metrics**: Per-window and per-clip accuracy comparison

## Related Files

- `src/data/dataset_loader.py`: Main implementation
- `conf/config.yaml`: Configuration parameters
- `test_windowing.py`: Unit tests for windowing logic
- `conf/metadata.csv`: Audio metadata with duration information

## Testing

Run tests with:
```bash
python test_windowing.py
```

Or test with actual data splits:
```bash
python src/data/dataset_loader.py
```
(Requires audio files in `data/raw/` directory)

## References

- GitHub Issue #1: Implement fixed-length window handling
- Project configuration: `conf/config.yaml`
- Audio processing pipeline: `docs/WORKFLOW_GUIDE.md`
