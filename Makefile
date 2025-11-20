.PHONY: help setup convert extract train eval clean

help:
	@echo "Bird-PAM Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup    - Show environment setup instructions"
	@echo "  convert  - Convert audio files from MP3 to WAV"
	@echo "  extract  - Extract mel spectrogram features"
	@echo "  train    - Train the baseline model"
	@echo "  eval     - Run evaluation and generate metrics"
	@echo "  clean    - Remove generated files and caches"

setup:
	./run_pipeline.sh setup

convert:
	./run_pipeline.sh convert

extract:
	./run_pipeline.sh extract

train:
	./run_pipeline.sh train

eval:
	./run_pipeline.sh eval

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
