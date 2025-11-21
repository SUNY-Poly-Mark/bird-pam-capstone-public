# Model Card — Bird-PAM Baseline

## Model Details
- **Model Name:** Bird-PAM baseline convnet
- **Version:** v0.1
- **Date:** 2025-11-18
- **Author:** Mark D'Arcy
- **Contact:** SUNY Poly MS in Data Science & Analytics
- **License:** MIT

## Model Description
A compact convolutional neural network for classifying bird vocalizations from passive acoustic monitoring recordings. The model processes mel spectrogram representations of short audio windows and outputs species-level predictions with calibrated probabilities.

## Intended Use
### Primary Use Cases
- Research and educational purposes in passive acoustic monitoring
- Bird species classification from field audio recordings
- Biodiversity monitoring and conservation research

### Out-of-Scope Use Cases
- Not intended for enforcement or legal decisions without domain expert validation
- Not suitable for real-time critical wildlife management decisions
- Should not be used as sole evidence for rare species identification

## Training Data
### Data Sources
- **Xeno-canto:** Community-contributed bird sound recordings (research-use permitted subset)
- **BirdCLEF:** Competition datasets from previous years
- Metadata includes: clip_id, filename, species_code, species_name, source, license, duration_s

### Data Splits
- **Training set:** IDs listed in conf/splits/train_ids.txt
- **Validation set:** IDs listed in conf/splits/val_ids.txt  
- **Test (OOD) set:** Out-of-distribution soundscapes in conf/splits/test_ood_ids.txt

### Preprocessing
- Audio standardized to WAV format, 32kHz sample rate, mono
- Segmented into 5-second windows with 2.5-second hop
- Converted to mel spectrograms:
  - 128 mel bins
  - FFT size: 1024
  - Hop length: 320 samples
  - Frequency range: 50-12000 Hz
  - Log-scaled with per-band normalization

## Model Architecture
- Compact convolutional neural network
- Input: Mel spectrogram (128 mel bins × variable time frames)
- Global pooling across time dimension
- Output: Species probabilities (number of classes varies by dataset)

## Training Procedure
- **Loss:** Binary cross-entropy (multi-label) or cross-entropy (multi-class)
- **Optimizer:** AdamW
- **Learning rate:** 0.001
- **Batch size:** 32
- **Epochs:** Configurable (early stopping enabled)
- **Augmentation:** SpecAugment, time shifting, additive noise, mixup (configurable)
- **Class balancing:** Configurable class-balanced sampling

## Evaluation Metrics
### Primary Metrics
- **Macro F1 Score:** Measures class-balanced classification performance
- **Per-class mean Average Precision (pcmAP):** For multi-label scenarios

### Calibration Metrics
- **Brier Score:** Measures probability calibration quality
- **Reliability Diagrams:** Visual assessment of calibration

### Additional Metrics
- Per-class precision and recall
- Confusion matrix
- False positives per hour (for soundscape scenarios)

## Performance
_To be completed after training and evaluation_

### Validation Set
- Macro F1: [TBD]
- Brier Score: [TBD]
- pcmAP: [TBD]

### Test (OOD) Set
- Macro F1: [TBD]
- Brier Score: [TBD]
- pcmAP: [TBD]

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
