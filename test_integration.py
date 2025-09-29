import requests
import json

def test_integration():
    print("🧪 Testing EcoSage Full-Stack Integration\n")
    
    # Test 1: Model Server Health
    print("1️⃣ Testing Model Server...")
    try:
        response = requests.get("http://127.0.0.1:8080/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Model Server: {data['status']}")
            print(f"   🧠 Model Loaded: {data['model_loaded']}")
            print(f"   🎯 Device: {data['device']}")
        else:
            print(f"   ❌ Model Server Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model Server Connection Failed: {e}")
    
    # Test 2: Backend API
    print("\n2️⃣ Testing Backend API...")
    try:
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend API: {data['status']}")
            print(f"   📅 Timestamp: {data['timestamp']}")
        else:
            print(f"   ❌ Backend API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend API Connection Failed: {e}")
    
    # Test 3: Events Endpoint
    print("\n3️⃣ Testing Events API...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/events")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Events API: Working")
            print(f"   📊 Events Count: {len(data['events'])}")
        else:
            print(f"   ❌ Events API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Events API Connection Failed: {e}")
    
    # Test 4: Carbon Calculator
    print("\n4️⃣ Testing Carbon Calculator...")
    try:
        test_data = {
            "energy": {"electricity": 350},
            "transportation": {"car": 1200}
        }
        response = requests.post("http://127.0.0.1:5000/api/calculate_carbon", 
                               json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Calculator API: Working")
            print(f"   🌱 Total Carbon: {data['total_carbon']} kg CO₂")
        else:
            print(f"   ❌ Calculator API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Calculator API Connection Failed: {e}")
    
    # Test 5: Image Classification (Demo)
    print("\n5️⃣ Testing Image Classification...")
    try:
        # Create a simple test image bytes
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc` `\x01\x00\x00\x0e\x00\x02\xac\xfa\x96\xd2\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {'image': ('test.png', test_image_data, 'image/png')}
        response = requests.post("http://127.0.0.1:8080/predictions/waste_classifier", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Classification API: Working")
            print(f"   🗂️ Prediction: {data['prediction']}")
            print(f"   📊 Confidence: {data['confidence']:.2f}")
            print(f"   🎭 Mode: {data['mode']}")
        else:
            print(f"   ❌ Classification API Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Classification API Connection Failed: {e}")
    
    print("\n🎉 Integration Test Complete!")
    print("\n🌐 Access Your Application:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend API: http://localhost:5000")
    print("   • Model Server: http://127.0.0.1:8080")

if __name__ == "__main__":
    test_integration()