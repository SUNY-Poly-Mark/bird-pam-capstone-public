# Bird-PAM Capstone - Project Context

**Project Owner:** SUNY-Poly-Mark  
**Repository:** SUNY-Poly-Mark/bird-pam-capstone  
**Last Updated:** 2025-01-19  

---

## 📋 Project Overview

**Goal:** Develop a deep learning pipeline for bird species classification from passive acoustic monitoring (PAM) data.

**Key Technologies:**
- Python 3.9
- PyTorch (deep learning framework)
- librosa (audio processing)
- scikit-learn (evaluation metrics)
- Conda (environment management)

**Dataset:** Bird vocalizations from audio recordings
**Output:** Multi-label classification model with calibrated confidence scores

---

## ✅ Current Status

### Completed ✓
- [x] Project structure setup
- [x] Created 7 comprehensive issues (#1-#7)
- [x] Infrastructure files (environment.yml, Makefile, run_pipeline.sh, model_card.md)
- [x] CI/CD pipeline configured (.github/workflows/ci.yml)
- [x] Documentation templates created

### In Progress 🔄
- [ ] Issue #1: Implement fixed-length window handling for audio input clips
- [ ] Issue #2: Build baseline convolutional model
- [ ] Issue #3: Add evaluation scripts for baseline model
- [ ] Issue #4: Implement data augmentation experiments for spectrograms
- [ ] Issue #5: Complete model card documentation and reporting
- [ ] Issue #6: Add reproducibility documentation for Bird-PAM capstone
- [ ] Issue #7: Create inference script for trained model

### Current Focus 🎯
**Working on:** Issue #1 - Fixed-length audio windowing
**Branch:** develop (or main)
**Next milestone:** Get audio preprocessing pipeline working

---

## 🔧 Key Configuration Parameters

From `conf/config.yaml`:

```yaml
Audio Processing:
- sample_rate: 32000 Hz
- window_seconds: 5.0
- hop_seconds: 2.5 (50% overlap)
- n_mels: 128
- n_fft: 1024
- fmin: 50 Hz
- fmax: 12000 Hz

Training:
- batch_size: 32
- learning_rate: 0.001
- epochs: 1 (placeholder, will increase)
- loss: Binary Cross-Entropy (BCE)
- seed: 13 (for reproducibility)

Evaluation Metrics:
- Primary: pcmAP (class-mean Average Precision)
- Secondary: macro_f1, brier score, false positives per hour
```

---

## 📁 Project Structure

```
bird-pam-capstone/
├── .github/workflows/
│   └── ci.yml              # CI/CD pipeline
├── conf/
│   └── config.yaml         # Main configuration
├── data/                   # Dataset (gitignored)
├── docs/                   # Documentation
│   └── PROJECT_CONTEXT.md  # This file
├── models/                 # Saved model checkpoints
├── notebooks/              # Jupyter notebooks for exploration
├── reports/                # Outputs (plots, metrics, figures)
├── src/
│   ├── data/              # Data loading and preprocessing
│   ├── features/          # Feature extraction (mel spectrograms)
│   ├── models/            # Model architectures and training
│   └── eval/              # Evaluation scripts
├── environment.yml         # Conda environment
├── Makefile               # Build automation
├── model_card.md          # Model documentation
└── run_pipeline.sh        # Pipeline execution script
```

---

## 🎯 Technical Decisions Log

### Decision 1: Audio Window Length
**Date:** 2025-01-19  
**Decision:** Use 5-second fixed windows with 2.5-second overlap (50%)  
**Rationale:**  
- Bird vocalizations typically 1-3 seconds
- 5 seconds provides sufficient context
- 50% overlap ensures no calls are split
**Impact:** Affects `src/data/dataset_loader.py` and all downstream processing

### Decision 2: Starting with Baseline CNN
**Date:** 2025-01-19  
**Decision:** Begin with convolutional neural network baseline  
**Rationale:**
- Establishes performance baseline
- Well-understood architecture
- Proven effective for audio classification
**Alternatives:** Transformers, EfficientNet (may explore later)  
**Impact:** Issue #2 focuses on CNN implementation

### Decision 3: Multi-label Classification
**Date:** 2025-01-19  
**Decision:** Use BCE loss for multi-label (multiple species per clip)  
**Rationale:** Real-world recordings often contain multiple species  
**Impact:** Model outputs probabilities per species, not single class

---

## 🔄 Recent Activity

### 2025-01-19
- ✅ Created all 7 project issues with detailed requirements
- ✅ Set up CI/CD workflow with GitHub Actions
- ✅ Created environment.yml with all dependencies
- ✅ Established project documentation structure
- 📝 **Next:** Begin implementing Issue #1 (audio windowing)

### Session Notes
- **Last worked on:** Setting up CI/CD pipeline
- **Blockers:** None currently
- **Questions:** None currently
- **Next session focus:** Start audio preprocessing implementation

---

## 🚀 Next Steps (Priority Order)

1. **Issue #1** - Implement audio windowing logic
   - Create `src/data/audio_utils.py`
   - Implement fixed-length window extraction
   - Handle padding/truncation for variable-length files
   - Add unit tests

2. **Issue #2** - Build baseline CNN model
   - Define model architecture in `src/models/baseline_model.py`
   - Implement training loop
   - Add checkpoint saving

3. **Issue #3** - Create evaluation pipeline
   - Implement metrics (pcmAP, macro F1, Brier score)
   - Generate confusion matrices and reliability diagrams

---

## 💡 Tips for Context Switching

### When resuming work:
1. Read this file first
2. Check "Recent Activity" section above
3. Review the relevant issue on GitHub
4. Check last commit: `git log --oneline -1`

### When switching environments (VS Code ↔️ Browser):
1. Update "Recent Activity" section above
2. Commit and push current work
3. Add progress comment on the relevant issue

### Quick context prompt for Copilot:
```
I'm working on the Bird-PAM capstone (SUNY-Poly-Mark/bird-pam-capstone).
Currently on Issue #[X]. Review docs/PROJECT_CONTEXT.md and help me
continue where I left off.
```

---

## 📚 Important Links

- **Repository:** https://github.com/SUNY-Poly-Mark/bird-pam-capstone
- **Issues:** https://github.com/SUNY-Poly-Mark/bird-pam-capstone/issues
- **Actions (CI):** https://github.com/SUNY-Poly-Mark/bird-pam-capstone/actions
- **Project Board:** (Create if needed)

---

## 🐛 Known Issues / Caveats

- CI workflow currently shows some expected failures (missing source files)
- Dataset not yet downloaded/organized
- No unit tests yet (will add with each issue)

---

## 📝 Notes

- Project seed: 13 (for reproducibility)
- Target device: CPU for development (can switch to GPU later)
- All experiments logged to `reports/` directory

---

**Remember:** Update this file as you make progress! It's your cross-environment memory.
