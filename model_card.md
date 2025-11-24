# Model Card — Bird-PAM Baseline CNN

## Model Details
- **Model Name:** Bird-PAM Baseline Convolutional Neural Network
- **Version:** v1.0
- **Date:** 2025-11-22
- **Author:** Mark D'Arcy
- **Contact:** SUNY Poly MS in Data Science & Analytics
- **License:** MIT
- **Implementation:** PyTorch 2.7.0
- **Model File:** `src/models/baseline_model.py`

## Model Description
A compact 4-layer convolutional neural network (CNN) designed for classifying bird vocalizations from passive acoustic monitoring recordings. The model processes mel spectrogram representations of audio windows and outputs multi-class species predictions with probability scores.

### Architecture Details
**Input:** Mel spectrogram (1 channel, 128 mel bins, variable time frames)

**Network Structure:**
1. **Conv Block 1:** 1→32 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool(2×2)
2. **Conv Block 2:** 32→64 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool(2×2)
3. **Conv Block 3:** 64→128 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool(2×2)
4. **Conv Block 4:** 128→256 channels, 3×3 kernel, BatchNorm, ReLU, MaxPool(2×2)
5. **Global Average Pooling:** Reduces spatial dimensions to 1×1
6. **FC Layer 1:** 256→128 with ReLU and Dropout(0.3)
7. **FC Layer 2:** 128→num_species (output logits)

**Output:** Species logits (batch_size, num_species) or probabilities via sigmoid

**Parameters:** ~250K trainable parameters (varies with num_species)

**Regularization:**
- Batch normalization after each conv layer
- Dropout (rate=0.3) before FC layers
- AdamW optimizer with weight_decay=0.01

## Intended Use
### Primary Use Cases
- Research and educational purposes in passive acoustic monitoring
- Bird species classification from field audio recordings (5-second windows)
- Biodiversity monitoring and conservation research
- Baseline model for comparison with more advanced architectures

### Out-of-Scope Use Cases
- Not intended for enforcement or legal decisions without domain expert validation
- Not suitable for real-time critical wildlife management decisions
- Should not be used as sole evidence for rare species identification
- Not optimized for deployment on edge devices without quantization

## Training Data
### Data Sources
- **Xeno-canto:** Community-contributed bird sound recordings (research-use permitted subset)
  - 13 species from northeastern United States
  - Target: 120 recordings per species (~1,560 total)
  - Licenses: CC-BY, CC-BY-NC, CC-BY-SA, CC-BY-NC-SA, CC-BY-NC-ND, CC0, Public Domain
- Metadata: `conf/metadata.csv` with clip_id, filename, species_code, species_name, source, license, duration_s

### Data Splits
- **Training set:** IDs listed in `conf/splits/train_ids.txt`
- **Validation set:** IDs listed in `conf/splits/val_ids.txt`
- **Test (OOD) set:** Out-of-distribution soundscapes in `conf/splits/test_ood_ids.txt`

### Preprocessing Pipeline
1. **Audio Normalization:**
   - Format: WAV
   - Sample rate: 32kHz
   - Channels: Mono
   
2. **Windowing:**
   - Window length: 5.0 seconds
   - Hop/stride: 2.5 seconds (50% overlap)
   - Short clips (<5s): Zero-padded
   - Long clips (>5s): Segmented into overlapping windows
   
3. **Mel Spectrogram Generation:**
   - n_mels: 128 mel frequency bins
   - n_fft: 1024 samples
   - hop_length: 320 samples
   - Frequency range: 50-12000 Hz
   - Power-to-dB scaling with reference to max
   - Per-band normalization enabled

## Model Architecture

## Training Procedure
### Configuration
All training parameters are specified in `conf/config.yaml`:

**Optimizer:** AdamW
- Learning rate: 0.001
- Weight decay: 0.01
- No learning rate scheduling (baseline)

**Training Settings:**
- Loss function: CrossEntropyLoss (multi-class classification)
- Batch size: 32
- Epochs: Configurable (default: 1 for initial testing)
- Device: CPU (configurable for GPU)
- Random seed: 13 (for reproducibility)

**Data Augmentation:** (Configurable in config.yaml)
- SpecAugment: Time and frequency masking
- Background mixing: Additive noise augmentation
- Mixup: Sample mixing for regularization

**Training Script:** `src/models/train.py`
```bash
python src/models/train.py --config conf/config.yaml
```

### Checkpointing
- Model checkpoints saved to `reports/` directory
- Best model (by validation F1) saved as `reports/best_model.pth`
- Epoch checkpoints: `reports/checkpoint_epoch_{N}.pth`
- Metrics logged to `reports/metrics.json`

### Resuming Training
```bash
python src/models/train.py --resume reports/checkpoint_epoch_10.pth
```

## Evaluation Metrics
### Primary Metrics
- **Accuracy:** Overall classification accuracy
- **Macro F1 Score:** Class-balanced F1 (harmonic mean of precision/recall)
- **Per-class F1:** Individual species performance

### Secondary Metrics (Future)
- **Per-class mean Average Precision (pcmAP):** For multi-label scenarios
- **Brier Score:** Probability calibration quality
- **False positives per hour:** For soundscape analysis

## Performance

### Baseline Training Run (November 23, 2025)
**Training Configuration:**
- Platform: Google Colab (T4 GPU)
- Dataset: 13 North American bird species
- Training samples: 1,058 audio files
- Validation samples: 226 audio files
- Epochs: 10
- Batch size: 32
- Optimizer: Adam (lr=0.001, weight_decay=0.0001)
- Early stopping: Enabled (patience=5)

**Results:**
- **Training Accuracy:** 28.5%
- **Validation Accuracy:** 25.2%
- **Baseline vs Random:** ~3.5× better than random chance (7.7% for 13 classes)

**Key Observations:**
- ✅ Pipeline validated end-to-end (data loading, preprocessing, training, evaluation)
- ✅ Model learning confirmed - significantly above random baseline
- ✅ No overfitting detected - train/val accuracies close (28.5% vs 25.2%)
- ✅ Loss convergence observed
- 📊 Performance floor established for future improvements

**Interpretation:**
This initial baseline confirms the complete training pipeline is functional. The model demonstrates learning capability while maintaining good generalization (minimal train-val gap). Performance is expected to improve significantly with:
- Data augmentation (SpecAugment, mixup)
- Longer training (20-50 epochs)
- Learning rate scheduling
- Deeper architectures or attention mechanisms
- Training set normalization statistics
- Pre-trained weights (AudioSet, BirdCLEF)

### Future Performance Targets
- **Short-term goal:** >50% validation accuracy (2× current baseline)
- **Medium-term goal:** >70% macro F1 score
- **Long-term goal:** >85% accuracy (competitive with domain benchmarks)

## Usage

### Loading the Model
```python
import torch
from src.models.baseline_model import BaselineCNN

# Load configuration
import yaml
with open("conf/config.yaml") as f:
    cfg = yaml.safe_load(f)

# Create model
num_species = 13  # Or load from training metadata
model = BaselineCNN(
    num_species=num_species,
    n_mels=cfg["audio"]["n_mels"],
    dropout=cfg["model"]["dropout"]
)

# Load trained weights
checkpoint = torch.load("reports/best_model.pth")
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
```

### Making Predictions
```python
import torch
from src.features.melspec import wav_to_logmel
import librosa

# Load and process audio
audio, sr = librosa.load("path/to/audio.wav", sr=32000)
mel = wav_to_logmel(audio, sr, cfg)
mel_tensor = torch.FloatTensor(mel).unsqueeze(0).unsqueeze(0)  # (1, 1, 128, T)

# Get predictions
with torch.no_grad():
    logits = model(mel_tensor)
    probs = torch.sigmoid(logits)

# Get top prediction
predicted_idx = probs.argmax(dim=1).item()
confidence = probs[0, predicted_idx].item()
print(f"Predicted species index: {predicted_idx}")
print(f"Confidence: {confidence:.2%}")
```

## Testing
Unit tests for the model are located in `src/tests/test_baseline_model.py`:

```bash
python src/tests/test_baseline_model.py
```

Tests verify:
- Model initialization
- Forward pass correctness
- Input/output shape handling
- Variable-length input support
- Save/load functionality
- Gradient flow

## Limitations and Biases
### Known Limitations
1. **Dataset size:** Relatively small local dataset may limit generalization
2. **Class imbalance:** Some species may have limited training examples
3. **Geographic bias:** Training data may be biased toward certain recording locations
4. **Temporal bias:** Recordings may be concentrated in specific seasons or times of day
5. **Label noise:** Community-contributed data may contain labeling errors
6. **Background noise:** Performance may degrade in high-noise environments

### Recommended Mitigations
- Use ensemble methods for critical applications
- Validate predictions with domain experts for rare species
- Consider model confidence scores (calibrated probabilities)
- Test on local data before deployment in new geographic regions

## Ethical Considerations
### Privacy
- Recording locations are not published to protect sensitive habitats
- Human voices are removed or redacted where present in recordings

### Environmental Impact
- Encourages non-invasive biodiversity monitoring
- Supports conservation efforts through automated analysis

### Dual Use
- Could potentially be misused to locate rare species for poaching
- Recommend controlled access to location-specific models

## Caveats and Recommendations
- **Audio quality matters:** Model performance depends on recording quality
- **Fixed window length:** Designed for 5-second windows; other lengths require retraining
- **Probability calibration:** Use calibrated probabilities for decision-making
- **Validation required:** Always validate outputs with ornithological expertise for conservation decisions
- **Reproducibility:** Full environment and configuration provided for reproducible results

## Model Card Authors
Mark D'Arcy (SUNY Poly)

## Model Card Contact
GitHub: SUNY-Poly-Mark/bird-pam-capstone

## Citation
_To be added upon publication_

## Additional Resources
- Repository: https://github.com/SUNY-Poly-Mark/bird-pam-capstone
- Documentation: See README.md in repository
- Configuration: conf/config.yaml

---
**Last Updated:** 2025-11-18
