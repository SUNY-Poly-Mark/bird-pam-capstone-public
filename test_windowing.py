"""
Test the windowing logic without PyTorch dependency.
"""
import numpy as np
import yaml
from src.data.dataset_loader import create_fixed_windows, load_audio

def load_config(path="conf/config.yaml"):
    """Read project configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def test_windowing():
    """Test windowing with the existing audio files."""
    cfg = load_config()
    window_seconds = cfg["audio"]["window_seconds"]
    hop_seconds = cfg["audio"]["hop_seconds"]
    sr = cfg["audio"]["sample_rate"]
    
    print("=" * 60)
    print("Testing Fixed-Length Windowing")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Sample rate: {sr} Hz")
    print(f"  - Window length: {window_seconds} seconds ({int(window_seconds * sr)} samples)")
    print(f"  - Hop length: {hop_seconds} seconds ({int(hop_seconds * sr)} samples)")
    print()
    
    # Test with the existing mel spectrograms (we'll use the .npy files as proxies)
    test_files = [
        ("data/processed/mels/XC364119 - American Robin - Turdus migratorius.npy", "American Robin", 10),
        ("data/processed/mels/XC405825 - Northern Cardinal - Cardinalis cardinalis.npy", "Northern Cardinal", 12),
        ("data/processed/mels/XC543338 - American Crow - Corvus brachyrhynchos.npy", "American Crow", 8),
    ]
    
    # Create synthetic audio for testing (since we don't have actual .wav files yet)
    print("Testing with synthetic audio:")
    print("-" * 60)
    
    test_cases = [
        ("Short clip (3s)", 3.0),
        ("Exact window (5s)", 5.0),
        ("Slightly longer (6s)", 6.0),
        ("Long clip (15s)", 15.0),
    ]
    
    for name, duration in test_cases:
        # Create synthetic audio
        num_samples = int(duration * sr)
        audio = np.random.randn(num_samples).astype(np.float32)
        
        # Apply windowing
        windows = create_fixed_windows(audio, sr, window_seconds, hop_seconds)
        
        print(f"\n{name}:")
        print(f"  - Original length: {duration}s ({num_samples} samples)")
        print(f"  - Number of windows: {len(windows)}")
        print(f"  - Window shapes: {[w.shape[0] for w in windows]}")
        
        # Verify all windows are correct length
        expected_samples = int(window_seconds * sr)
        for i, w in enumerate(windows):
            if w.shape[0] != expected_samples:
                print(f"  ⚠️ Window {i} has incorrect length: {w.shape[0]} (expected {expected_samples})")
            else:
                print(f"  ✅ Window {i}: {w.shape[0]} samples (correct)")

if __name__ == "__main__":
    test_windowing()
