from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import io
import os
# Model loading handled directly in the class

app = Flask(__name__)
CORS(app)

class WasteClassifierServer:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
        
        # Define transforms (same as training)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Load model
        self.load_model()
    
    def create_model_architecture(self):
        """Create the same model architecture used during training"""
        from torchvision import models
        import torch.nn as nn
        
        # Use ResNet18 as base (common for waste classification)
        model = models.resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, len(self.classes))
        return model
    
    def load_model(self):
        try:
            import torch.nn as nn
            from torchvision import models
            
            # Try to find your trained model
            model_paths = [
                "waste_classifier_model_v2.pth",
                "waste_classifier_model.pth",
                "backend/waste_classifier_model_v2.pth",
                "backend/waste_classifier_model.pth"
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path):
                    try:
                        print(f"🔍 Found model at: {model_path}")
                        
                        # Load checkpoint
                        checkpoint = torch.load(model_path, map_location=self.device)
                        
                        # Try different architectures based on the keys in the checkpoint
                        if 'fc.1.weight' in checkpoint:
                            # v2 model has Sequential final layer: fc = nn.Sequential(nn.Dropout(), nn.Linear(...))
                            print("🔧 Detected v2 model architecture with Sequential final layer")
                            model = models.resnet18(pretrained=False)
                            model.fc = nn.Sequential(
                                nn.Dropout(0.5),
                                nn.Linear(model.fc.in_features, 6)
                            )
                        elif 'fc.weight' in checkpoint:
                            # v1 model has simple Linear final layer
                            print("🔧 Detected v1 model architecture with Linear final layer")  
                            model = models.resnet18(pretrained=False)
                            model.fc = nn.Linear(model.fc.in_features, 6)
                        else:
                            print("⚠️ Unknown model structure, trying default ResNet18")
                            model = models.resnet18(pretrained=False)
                            model.fc = nn.Linear(model.fc.in_features, 6)
                        
                        # Load state dict
                        model.load_state_dict(checkpoint)
                        model.eval()
                        model.to(self.device)
                        
                        self.model = model
                        print(f"✅ Successfully loaded trained ResNet18 from {model_path}")
                        return
                        
                    except Exception as e:
                        print(f"❌ Failed to load {model_path}: {e}")
                        continue
            
            print("⚠️ No trained model found, using demo mode")
            self.model = None
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            print("⚠️ Falling back to demo mode")
            self.model = None
    
    def predict(self, image_bytes):
        # Import all needed modules at the top
        import random
        import io
        from PIL import Image
        import numpy as np
        
        if self.model is None:
            # Smarter demo predictions based on simple image analysis
            
            try:
                # Analyze image for basic properties
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                
                # Get average color
                img_array = np.array(image.resize((64, 64)))
                avg_color = np.mean(img_array, axis=(0, 1))
                
                # Simple heuristics based on color
                predictions = {
                    "cardboard": 0.1,
                    "glass": 0.1, 
                    "metal": 0.1,
                    "paper": 0.1,
                    "plastic": 0.1,
                    "trash": 0.1
                }
                
                # Color-based predictions (very basic)
                if avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:  # Green-ish
                    predictions["glass"] = 0.7
                elif avg_color[2] > 150:  # Blue-ish
                    predictions["plastic"] = 0.6
                elif avg_color[0] > 200 and avg_color[1] > 200 and avg_color[2] > 200:  # White-ish
                    predictions["paper"] = 0.5
                elif avg_color[0] > 150 and avg_color[1] < 100:  # Red-ish/brown
                    predictions["cardboard"] = 0.6
                elif sum(avg_color) < 300:  # Dark
                    predictions["metal"] = 0.5
                else:
                    predictions["plastic"] = 0.4
                
                # Add some randomness
                for key in predictions:
                    predictions[key] += random.uniform(-0.1, 0.1)
                    predictions[key] = max(0.05, min(0.9, predictions[key]))
                
            except Exception as e:
                print(f"Demo prediction error: {e}")
                predictions = {
                    "cardboard": random.uniform(0.1, 0.3),
                    "glass": random.uniform(0.1, 0.8),  # Higher chance for glass
                    "metal": random.uniform(0.1, 0.3),
                    "paper": random.uniform(0.1, 0.3),
                    "plastic": random.uniform(0.1, 0.6),
                    "trash": random.uniform(0.1, 0.3)
                }
            
            # Normalize to sum to 1
            total = sum(predictions.values())
            predictions = {k: v/total for k, v in predictions.items()}
            
            # Get top prediction
            best_class = max(predictions, key=predictions.get)
            confidence = predictions[best_class]
            
            return {
                "prediction": best_class,
                "confidence": float(confidence),
                "all_predictions": predictions,
                "mode": "demo",
                "environmental_impact": self.get_environmental_impact(best_class),
                "suggestions": self.get_suggestions(best_class)
            }
        
        try:
            # Real model prediction - simplified approach
            print(f"📸 Processing image data of size: {len(image_bytes)} bytes")
            
            # Try direct PIL loading first
            try:
                from PIL import Image
                import io
                
                # Method 1: Direct BytesIO approach
                image_buffer = io.BytesIO(image_bytes)
                image_buffer.seek(0)
                image = Image.open(image_buffer)
                image = image.convert('RGB')
                print(f"✅ Method 1 success: {image.format}, {image.size}")
                
            except Exception as e1:
                print(f"⚠️ Method 1 failed: {e1}")
                
                try:
                    # Method 2: Save to temp file and reload
                    import tempfile
                    import os
                    
                    # Try different extensions
                    for ext in ['.jpg', '.png', '.jpeg', '.bmp']:
                        try:
                            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                                temp_file.write(image_bytes)
                                temp_file_path = temp_file.name
                            
                            image = Image.open(temp_file_path)
                            image = image.convert('RGB') 
                            print(f"✅ Method 2 success with {ext}: {image.size}")
                            
                            # Clean up
                            try:
                                os.unlink(temp_file_path)
                            except:
                                pass
                            break
                            
                        except Exception as ext_error:
                            print(f"⚠️ Extension {ext} failed: {ext_error}")
                            try:
                                os.unlink(temp_file_path)
                            except:
                                pass
                            continue
                    else:
                        raise Exception("All image loading methods failed")
                        
                except Exception as e2:
                    print(f"❌ Method 2 also failed: {e2}")
                    raise Exception("Cannot load image with any method")
            
            # Apply transforms and predict
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            print(f"🧠 Input tensor shape: {image_tensor.shape}")
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                predictions = F.softmax(outputs, dim=1)
                confidence, predicted_class = torch.max(predictions, 1)
                
                class_name = self.classes[predicted_class.item()]
                confidence_score = float(confidence.item())
                
                print(f"🎯 Prediction: {class_name} ({confidence_score:.3f})")
                
                all_preds = {
                    self.classes[i]: float(predictions[0][i].item()) 
                    for i in range(len(self.classes))
                }
                
                return {
                    "prediction": class_name,
                    "confidence": confidence_score,
                    "all_predictions": all_preds,
                    "mode": "real",
                    "environmental_impact": self.get_environmental_impact(class_name),
                    "suggestions": self.get_suggestions(class_name)
                }
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                "error": str(e),
                "prediction": "unknown",
                "confidence": 0.0
            }
    
    def get_environmental_impact(self, waste_type):
        impacts = {
            "cardboard": "Positive - Highly recyclable, biodegradable material",
            "glass": "Positive - 100% recyclable without quality loss",
            "metal": "Positive - Infinitely recyclable, high value material",
            "paper": "Neutral - Recyclable but degrades with each cycle",
            "plastic": "Negative - Can take 500+ years to decompose",
            "trash": "Negative - Likely to end up in landfill or environment"
        }
        return impacts.get(waste_type, "Unknown environmental impact")
    
    def get_suggestions(self, waste_type):
        suggestions = {
            "cardboard": ["Remove tape and staples", "Flatten boxes", "Keep dry for recycling"],
            "glass": ["Rinse clean", "Remove caps and lids", "Separate by color if required"],
            "metal": ["Clean off food residue", "Remove labels if possible", "Separate aluminum and steel"],
            "paper": ["Keep dry", "Remove plastic windows", "Separate by type (newspaper, office paper)"],
            "plastic": ["Check recycling number", "Clean thoroughly", "Remove caps if different plastic type"],
            "trash": ["Consider if any parts can be recycled", "Dispose of properly", "Look for alternative products"]
        }
        return suggestions.get(waste_type, ["Dispose of responsibly"])

# Initialize classifier
classifier = WasteClassifierServer()

@app.route('/predictions/waste_classifier', methods=['POST'])
def predict():
    try:
        # Handle different input formats
        image_bytes = None
        
        print(f"🔍 Request content-type: {request.content_type}")
        print(f"🔍 Request has files: {'image' in request.files}")
        print(f"🔍 Request has json: {request.json is not None}")
        print(f"🔍 Request has data: {len(request.data) if request.data else 0} bytes")
        
        if request.json and 'image' in request.json:
            # Base64 encoded image (PRIORITY - this is what we're getting!)
            import base64
            image_data = request.json['image']
            print(f"📦 JSON base64 data length: {len(image_data)}")
            print(f"📦 First 50 chars: {image_data[:50]}")
            
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
                print(f"📦 After removing data URL prefix: {len(image_data)}")
            
            try:
                image_bytes = base64.b64decode(image_data)
                print(f"✅ Successfully decoded base64 to {len(image_bytes)} bytes")
                
                # Save debug image
                with open('debug_image.jpg', 'wb') as f:
                    f.write(image_bytes)
                print("💾 Saved debug image to debug_image.jpg")
                
            except Exception as decode_error:
                print(f"❌ Base64 decode error: {decode_error}")
                return jsonify({"error": f"Base64 decode error: {decode_error}"}), 400
        elif 'image' in request.files:
            file = request.files['image']
            image_bytes = file.read()
            print(f"📁 File upload: {len(image_bytes)} bytes")
        elif 'file' in request.files:
            file = request.files['file']
            image_bytes = file.read() 
            print(f"📁 File upload (alt): {len(image_bytes)} bytes")
        elif request.data:
            image_bytes = request.data
            print(f"📄 Raw data: {len(image_bytes)} bytes")

        else:
            print("❌ No image data found in request")
            return jsonify({"error": "No image data provided"}), 400
        
        # Get prediction
        result = classifier.predict(image_bytes)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in predict endpoint: {e}")
        return jsonify({
            "error": str(e),
            "prediction": "plastic",
            "confidence": 0.75,
            "mode": "fallback"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": classifier.model is not None,
        "device": str(classifier.device),
        "classes": classifier.classes
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "EcoSage Waste Classifier",
        "status": "running",
        "endpoints": {
            "predict": "/predictions/waste_classifier",
            "health": "/health"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting EcoSage Model Server...")
    print("📡 Server will run on http://127.0.0.1:8080")
    print("🧠 Model status:", "✅ Loaded" if classifier.model else "⚠️ Demo Mode")
    print("🎯 Device:", classifier.device)
    print("📝 Available classes:", classifier.classes)
    print("\n🔗 Available endpoints:")
    print("   • http://127.0.0.1:8080/health")
    print("   • http://127.0.0.1:8080/predictions/waste_classifier")
    print("\n🌱 Ready to classify waste images!")
    
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)