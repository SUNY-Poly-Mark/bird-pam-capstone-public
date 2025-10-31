# src/features/melspec.py
import os, argparse, yaml, numpy as np
import soundfile as sf
import librosa
from glob import glob

def load_cfg(path="conf/config.yaml"):
    """Load the YAML configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def wav_to_logmel(y, sr, cfg):
    """Convert waveform to a log-mel spectrogram."""
    mel = librosa.feature.melspectrogram(
        y=y, sr=sr,
        n_fft=cfg["audio"]["n_fft"],
        hop_length=cfg["audio"]["hop_length"],
        n_mels=cfg["audio"]["n_mels"],
        fmin=cfg["audio"]["fmin"],
        fmax=cfg["audio"]["fmax"],
        power=2.0
    )
    mel = librosa.power_to_db(mel, ref=np.max).astype(np.float32)
    return mel

def chop_windows(mel, sr, cfg):
    """Split spectrogram into overlapping 5-second windows."""
    win_s = cfg["audio"]["window_seconds"]
    hop_s = cfg["audio"]["hop_seconds"]
    frames_per_sec = sr / cfg["audio"]["hop_length"]
    win_f = int(round(win_s * frames_per_sec))
    hop_f = int(round(hop_s * frames_per_sec))
    chunks = []
    for start in range(0, mel.shape[1] - win_f + 1, hop_f):
        chunks.append(mel[:, start:start+win_f])
    if not chunks:
        return np.empty((0, mel.shape[0], win_f), dtype=np.float32)
    return np.stack(chunks)

def process_one(wav_path, out_dir, cfg):
    """Process one .wav file and save feature windows."""
    y, sr = sf.read(wav_path, always_2d=False)
    if cfg["audio"]["mono"] and y.ndim == 2:
        y = y.mean(axis=1)
    if sr != cfg["audio"]["sample_rate"]:
        y = librosa.resample(y, orig_sr=sr, target_sr=cfg["audio"]["sample_rate"])
        sr = cfg["audio"]["sample_rate"]
    mel = wav_to_logmel(y, sr, cfg)
    wins = chop_windows(mel, sr, cfg)
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(wav_path))[0]
    np.save(os.path.join(out_dir, f"{base}.npy"), wins)
    return wins.shape[0]

def main():
    ap = argparse.ArgumentParser(description="Convert WAV files to log-mel features")
    ap.add_argument("--input_glob", required=True, help='Pattern like "data/raw/*.wav"')
    ap.add_argument("--out", default="data/processed/mels")
    ap.add_argument("--cfg", default="conf/config.yaml")
    args = ap.parse_args()

    cfg = load_cfg(args.cfg)
    paths = glob(args.input_glob)
    total_files, total_windows = 0, 0
    for p in paths:
        total_files += 1
        total_windows += process_one(p, args.out, cfg)
    print(f"Processed {total_files} files → {total_windows} windows saved in {args.out}")

if __name__ == "__main__":
    main()
