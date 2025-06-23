"""
Check what files were created by training
"""
import os
from pathlib import Path

print("Checking project files...\n")

# Check models directory
models_path = Path("models")
if models_path.exists():
    print("📁 models/")
    for file in models_path.iterdir():
        print(f"   - {file.name}")
else:
    print("❌ models/ directory not found")

print()

# Check processed_data directory
processed_path = Path("processed_data")
if processed_path.exists():
    print("📁 processed_data/")
    for file in processed_path.iterdir():
        print(f"   - {file.name}")
else:
    print("❌ processed_data/ directory not found")

print()

# Check if we can load the model
try:
    import sys
    sys.path.append('.')
    from recommendation_models import HybridRecommender
    
    print("Attempting to load model...")
    model = HybridRecommender.load_model("models")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")