#!/usr/bin/env bash
set -euo pipefail

# Bird-PAM Pipeline Runner
# Usage:
#   ./run_pipeline.sh setup     # Print environment setup instructions
#   ./run_pipeline.sh convert   # Convert MP3 to WAV
#   ./run_pipeline.sh extract   # Extract mel spectrograms
#   ./run_pipeline.sh train     # Train baseline model
#   ./run_pipeline.sh eval      # Run evaluation

COMMAND=${1:-help}

case "$COMMAND" in
  setup)
    echo "=== Bird-PAM Environment Setup ==="
    echo "1. Create conda environment:"
    echo "   conda env create -f environment.yml"
    echo ""
    echo "2. Activate environment:"
    echo "   conda activate bird-pam"
    echo ""
    echo "3. Install system dependencies (if needed):"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg libsndfile1"
    echo "   - macOS: brew install ffmpeg libsndfile"
    echo "   - Windows: Install via conda or package manager"
    ;;
  convert)
    echo "Converting audio files (MP3 -> WAV)..."
    python -m src.data.convert_audio --config conf/config.yaml
    ;;
  extract)
    echo "Extracting mel spectrograms..."
    python -m src.features.extract_mels --config conf/config.yaml
    ;;
  train)
    echo "Training baseline model..."
    python -m src.models.train --config conf/config.yaml
    ;;
  eval)
    echo "Running evaluation..."
    python -m src.eval.evaluate --config conf/config.yaml
    ;;
  *)
    echo "Bird-PAM Pipeline Runner"
    echo ""
    echo "Usage: $0 {setup|convert|extract|train|eval}"
    echo ""
    echo "Commands:"
    echo "  setup    - Show environment setup instructions"
    echo "  convert  - Convert audio files from MP3 to WAV"
    echo "  extract  - Extract mel spectrogram features"
    echo "  train    - Train the baseline model"
    echo "  eval     - Run evaluation and generate metrics"
    exit 1
    ;;
esac
