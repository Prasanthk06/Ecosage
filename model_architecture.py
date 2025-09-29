"""
Model Architecture Definition for EcoSage Waste Classifier
This file defines the exact model architecture used during training
"""

import torch
import torch.nn as nn
from torchvision import models

class WasteClassifierModel(nn.Module):
    def __init__(self, num_classes=6, model_name='resnet18'):
        super(WasteClassifierModel, self).__init__()
        self.num_classes = num_classes
        self.model_name = model_name
        
        # Create base model
        if model_name == 'resnet18':
            self.model = models.resnet18(pretrained=True)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        elif model_name == 'resnet34':
            self.model = models.resnet34(pretrained=True)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        elif model_name == 'mobilenet_v2':
            self.model = models.mobilenet_v2(pretrained=True)
            self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, num_classes)
        else:
            # Default to ResNet18
            self.model = models.resnet18(pretrained=True)
            self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
    
    def forward(self, x):
        return self.model(x)

def load_waste_classifier(model_path, device='cpu'):
    """
    Load a waste classifier model from file
    
    Args:
        model_path (str): Path to the saved model
        device (str): Device to load model on
        
    Returns:
        torch.nn.Module: Loaded model
    """
    try:
        # Try to load checkpoint
        checkpoint = torch.load(model_path, map_location=device)
        
        # Different possible formats
        if isinstance(checkpoint, dict):
            # Extract model info if available
            num_classes = checkpoint.get('num_classes', 6)
            model_name = checkpoint.get('model_name', 'resnet18')
            
            # Create model with correct architecture
            model = WasteClassifierModel(num_classes=num_classes, model_name=model_name)
            
            # Load state dict
            if 'state_dict' in checkpoint:
                model.load_state_dict(checkpoint['state_dict'])
            elif 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                # Assume checkpoint is the state dict
                model.load_state_dict(checkpoint)
                
        else:
            # Assume it's a complete model
            model = checkpoint
        
        model.to(device)
        model.eval()
        return model
        
    except Exception as e:
        print(f"Failed to load model with custom loader: {e}")
        
        # Fallback: try different architectures
        for model_name in ['resnet18', 'resnet34', 'mobilenet_v2']:
            try:
                print(f"Trying {model_name} architecture...")
                model = WasteClassifierModel(num_classes=6, model_name=model_name)
                
                checkpoint = torch.load(model_path, map_location=device)
                if isinstance(checkpoint, dict):
                    for key in ['state_dict', 'model_state_dict']:
                        if key in checkpoint:
                            checkpoint = checkpoint[key]
                            break
                
                model.load_state_dict(checkpoint)
                model.to(device)
                model.eval()
                print(f"✅ Successfully loaded with {model_name}!")
                return model
                
            except Exception as arch_error:
                print(f"❌ {model_name} failed: {arch_error}")
                continue
        
        raise Exception("Could not load model with any architecture")

if __name__ == "__main__":
    # Test the model loading
    import os
    
    model_paths = [
        "waste_classifier_model_v2.pth",
        "waste_classifier_model.pth"
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            print(f"\n🧪 Testing model loading for: {path}")
            try:
                model = load_waste_classifier(path)
                print(f"✅ Model loaded successfully!")
                print(f"📊 Model type: {type(model)}")
                
                # Test forward pass
                test_input = torch.randn(1, 3, 224, 224)
                with torch.no_grad():
                    output = model(test_input)
                    print(f"📈 Output shape: {output.shape}")
                    print(f"🎯 Predictions: {torch.softmax(output, dim=1)}")
                
            except Exception as e:
                print(f"❌ Failed to load {path}: {e}")
    
    print("\n🏁 Model loading test complete!")