import torch
import torch.nn as nn
from torchvision import models
import os

def load_direct_resnet_model(model_path):
    """
    Load a ResNet model directly without wrapper class
    """
    try:
        # Load the state dict
        checkpoint = torch.load(model_path, map_location='cpu')
        
        # Create ResNet18 model
        model = models.resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 6)  # 6 classes
        
        try:
            model.load_state_dict(checkpoint)
            print(f"✅ Successfully loaded ResNet18 from {model_path}")
            return model
        except Exception as e:
            print(f"❌ ResNet18 failed: {e}")
            
        # Try ResNet34
        model = models.resnet34(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 6)  # 6 classes
        
        try:
            model.load_state_dict(checkpoint)
            print(f"✅ Successfully loaded ResNet34 from {model_path}")
            return model
        except Exception as e:
            print(f"❌ ResNet34 failed: {e}")
            
        # If both fail, try to inspect the checkpoint structure
        print(f"📋 Model keys in checkpoint: {list(checkpoint.keys())[:10]}...")
        return None
        
    except Exception as e:
        print(f"❌ Failed to load {model_path}: {e}")
        return None

def test_model_loading():
    """Test loading both model files"""
    models_to_test = [
        "waste_classifier_model_v2.pth",
        "waste_classifier_model.pth"
    ]
    
    for model_file in models_to_test:
        print(f"\n🧪 Testing model loading for: {model_file}")
        if os.path.exists(model_file):
            model = load_direct_resnet_model(model_file)
            if model:
                model.eval()
                print(f"✅ Model loaded successfully and set to eval mode")
            else:
                print(f"❌ Failed to load {model_file}")
        else:
            print(f"❌ Model file not found: {model_file}")

if __name__ == "__main__":
    test_model_loading()