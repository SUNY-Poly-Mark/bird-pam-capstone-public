# Training on Google Colab with VS Code

## Problem Summary

After extensive troubleshooting, Windows PyTorch installations consistently failed with DLL errors (fbgemm.dll, shm.dll) across multiple versions (2.6.0, 2.7.0, 2.9.1), even after:
- Installing Intel MKL libraries
- Installing Visual C++ Redistributables  
- Setting `KMP_DUPLICATE_LIB_OK=TRUE`
- Trying multiple PyTorch CPU builds

## Solution: VS Code Colab Extension

Use Google Colab's GPU infrastructure directly from VS Code with your local files.

## Setup Instructions

### 1. Install VS Code Colab Extension

1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search for "Colab" 
3. Install the **"Colab" extension by Google**
4. Sign in with your Google account when prompted

### 2. Open the Training Notebook

1. Open `train_on_colab.ipynb` in VS Code
2. Click **"Connect to Colab"** button in the top-right corner
3. Select a **GPU runtime** (T4 is free and sufficient)
4. Wait for the kernel to connect (you'll see "Python 3 (Google Colab)" in status bar)

### 3. Run Training

Simply run the cells sequentially! The notebook:
- ✅ Uses your local project files (no uploading)
- ✅ Accesses your Google Drive dataset directly
- ✅ Runs on Colab's GPU (free T4 with 16GB VRAM)
- ✅ Saves outputs to your local `outputs/` folder
- ✅ Bypasses all Windows DLL issues (Linux runtime)

### 4. Monitor Progress

The notebook includes:
- Real-time progress bars for training/validation
- Live loss and accuracy updates
- Training curve visualizations
- Automatic checkpointing and early stopping

## What Gets Created

After training completes, you'll have in `outputs/`:
- `best_model.pth` - Best model checkpoint (based on validation loss)
- `training_history.json` - All metrics across epochs
- `training_curves.png` - Training/validation plots
- `checkpoint_epoch_N.pth` - Periodic checkpoints (every 5 epochs)

## Expected Training Time

With T4 GPU and current dataset (~100 audio files):
- **~2-3 minutes per epoch**
- **~20-30 minutes total** (10 epochs configured)
- Early stopping may reduce this further

## Advantages Over Local Training

| Aspect | Local Windows | VS Code Colab |
|--------|---------------|---------------|
| GPU Access | ❌ CPU only | ✅ Free T4 GPU |
| PyTorch DLL Issues | ❌ Constant errors | ✅ No issues (Linux) |
| Setup Time | ❌ Hours of troubleshooting | ✅ 5 minutes |
| Training Speed | ❌ Very slow on CPU | ✅ ~10x faster on GPU |
| File Access | ✅ Direct | ✅ Direct (via extension) |
| Cost | ✅ Free | ✅ Free |

## Troubleshooting

### "Connect to Colab" button doesn't appear
- Make sure you have the Colab extension installed
- Reload VS Code window (Ctrl+Shift+P → "Reload Window")

### "Cannot access local files"
- The extension mounts your local filesystem to Colab
- Make sure paths in the notebook match your actual file locations
- Check that `PROJECT_ROOT` and `DATA_PATH` are correct in cell 2

### "GPU not available"
- In Colab menu: Runtime → Change runtime type → GPU
- Wait for kernel to restart
- Re-run the GPU check cell

### Training is slow
- Verify GPU is enabled (first cell should show CUDA available)
- Check `num_workers=2` in DataLoader isn't too high
- Consider reducing batch size if GPU memory is full

## Next Steps After Training

Once training completes:
1. ✅ Model is saved in `outputs/best_model.pth`
2. ✅ Training metrics are in `outputs/training_history.json`
3. ✅ Visualizations are in `outputs/training_curves.png`
4. **Next:** Move to Issue #3 (evaluation scripts)
5. Load the trained model for inference and evaluation

## Command Reference

If you need to run additional commands in Colab:
```python
# Install additional packages
!pip install package-name

# Check GPU info
!nvidia-smi

# List files
!ls -lh outputs/

# Check disk usage
!df -h
```

## Notes

- The free T4 GPU has a **12-hour session limit**
- Sessions may disconnect after inactivity (~90 minutes)
- All outputs are saved locally, so you can resume if disconnected
- The extension handles file syncing automatically
