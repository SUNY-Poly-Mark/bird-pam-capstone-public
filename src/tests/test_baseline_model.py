"""
Unit tests for the baseline CNN model.

Tests model initialization, forward pass, shapes, and save/load functionality.
"""
import sys
import os
import torch
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baseline_model import BaselineCNN, create_model


def test_model_initialization():
    """Test that model initializes correctly."""
    print("Testing model initialization...")
    
    num_species = 13
    n_mels = 128
    dropout = 0.3
    
    model = BaselineCNN(num_species=num_species, n_mels=n_mels, dropout=dropout)
    
    assert model.num_species == num_species
    assert model.n_mels == n_mels
    assert model.get_num_params() > 0
    
    print(f"✅ Model initialized with {model.get_num_params():,} parameters")


def test_forward_pass():
    """Test forward pass with dummy input."""
    print("\nTesting forward pass...")
    
    batch_size = 8
    n_mels = 128
    time_frames = 500
    num_species = 13
    
    # Create dummy input
    x = torch.randn(batch_size, 1, n_mels, time_frames)
    
    # Create model
    model = BaselineCNN(num_species=num_species, n_mels=n_mels)
    model.eval()
    
    # Forward pass
    with torch.no_grad():
        logits = model(x)
        probs = model.predict_proba(x)
    
    # Check shapes
    assert logits.shape == (batch_size, num_species), f"Expected shape ({batch_size}, {num_species}), got {logits.shape}"
    assert probs.shape == (batch_size, num_species), f"Expected shape ({batch_size}, {num_species}), got {probs.shape}"
    
    # Check probability ranges
    assert torch.all(probs >= 0) and torch.all(probs <= 1), "Probabilities out of [0, 1] range"
    
    print(f"✅ Forward pass successful")
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {logits.shape}")
    print(f"   Probability range: [{probs.min():.4f}, {probs.max():.4f}]")


def test_variable_length_input():
    """Test that model handles variable-length time dimensions."""
    print("\nTesting variable-length inputs...")
    
    n_mels = 128
    num_species = 13
    model = BaselineCNN(num_species=num_species, n_mels=n_mels)
    model.eval()
    
    # Test different time lengths
    time_lengths = [100, 250, 500, 1000]
    
    for time_frames in time_lengths:
        x = torch.randn(2, 1, n_mels, time_frames)
        
        with torch.no_grad():
            logits = model(x)
        
        assert logits.shape == (2, num_species), f"Failed for time_frames={time_frames}"
        print(f"   ✓ Time frames={time_frames}: output shape {logits.shape}")
    
    print(f"✅ Variable-length input test passed")


def test_save_and_load():
    """Test model save and load functionality."""
    print("\nTesting save/load...")
    
    import tempfile
    
    num_species = 13
    model = BaselineCNN(num_species=num_species)
    
    # Create dummy input
    x = torch.randn(4, 1, 128, 500)
    
    # Get output before saving
    model.eval()
    with torch.no_grad():
        output_before = model(x)
    
    # Save model
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pth") as f:
        temp_path = f.name
        torch.save(model.state_dict(), temp_path)
    
    # Load model
    model_loaded = BaselineCNN(num_species=num_species)
    model_loaded.load_state_dict(torch.load(temp_path))
    model_loaded.eval()
    
    # Get output after loading
    with torch.no_grad():
        output_after = model_loaded(x)
    
    # Check outputs are identical
    assert torch.allclose(output_before, output_after, atol=1e-6), "Loaded model outputs differ"
    
    # Cleanup
    os.remove(temp_path)
    
    print(f"✅ Save/load test passed")
    print(f"   Output difference: {(output_before - output_after).abs().max():.2e}")


def test_gradient_flow():
    """Test that gradients flow through the model."""
    print("\nTesting gradient flow...")
    
    num_species = 13
    model = BaselineCNN(num_species=num_species)
    model.train()
    
    # Create dummy data
    x = torch.randn(4, 1, 128, 500)
    labels = torch.randint(0, num_species, (4,))
    
    # Forward pass
    logits = model(x)
    loss = torch.nn.functional.cross_entropy(logits, labels)
    
    # Backward pass
    loss.backward()
    
    # Check that gradients exist
    has_gradients = False
    for name, param in model.named_parameters():
        if param.grad is not None:
            has_gradients = True
            assert not torch.isnan(param.grad).any(), f"NaN gradients in {name}"
            assert not torch.isinf(param.grad).any(), f"Inf gradients in {name}"
    
    assert has_gradients, "No gradients found"
    
    print(f"✅ Gradient flow test passed")
    print(f"   Loss: {loss.item():.4f}")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Running BaselineCNN Unit Tests")
    print("="*60)
    
    try:
        test_model_initialization()
        test_forward_pass()
        test_variable_length_input()
        test_save_and_load()
        test_gradient_flow()
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
