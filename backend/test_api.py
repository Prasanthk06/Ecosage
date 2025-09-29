"""
Test script for EcoSage Backend API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_get_events():
    """Test get events endpoint"""
    print("\n📅 Testing get events...")
    try:
        response = requests.get(f"{BASE_URL}/events")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Events count: {data.get('count', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get events failed: {e}")
        return False

def test_create_event():
    """Test create event endpoint"""
    print("\n📝 Testing create event...")
    try:
        event_data = {
            "title": "API Test Event",
            "date": "2025-11-01",
            "time": "10:00 AM",
            "location": "Test Location",
            "description": "This is a test event created via API",
            "category": "Testing",
            "attendees": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/events",
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Event created successfully")
            print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Create event failed: {e}")
        return False

def test_calculate_carbon():
    """Test carbon calculation endpoint"""
    print("\n🧮 Testing carbon calculation...")
    try:
        calculation_data = {
            "electricity": 350,
            "transportation": 1200,
            "natural_gas": 80,
            "water": 300,
            "waste": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/calculate_carbon",
            json=calculation_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Calculation successful")
            print(f"Total emissions: {data['data']['total_emissions']} kg CO₂")
            print(f"Comparison: {data['data']['comparison']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Carbon calculation failed: {e}")
        return False

def test_leaderboard():
    """Test leaderboard endpoint"""
    print("\n🏆 Testing leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/leaderboard")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Leaderboard retrieved successfully")
            print(f"Top users: {len(data['data'])}")
            for i, user in enumerate(data['data'][:3]):
                print(f"  {i+1}. {user['username']}: {user['score']} points")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Leaderboard test failed: {e}")
        return False

def test_image_classification():
    """Test image classification endpoint (without actual image)"""
    print("\n🖼️ Testing image classification...")
    try:
        # This will test the endpoint but expect it to fail gracefully
        response = requests.post(f"{BASE_URL}/classify")
        print(f"Status: {response.status_code}")
        if response.status_code == 400:  # Expected for no image
            print("✅ Endpoint correctly requires image file")
            return True
        return False
    except Exception as e:
        print(f"❌ Image classification test failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting EcoSage API Tests...\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Get Events", test_get_events),
        ("Create Event", test_create_event),
        ("Calculate Carbon", test_calculate_carbon),
        ("Leaderboard", test_leaderboard),
        ("Image Classification", test_image_classification),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*50)
    print("🎯 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API server and dependencies.")

if __name__ == "__main__":
    run_all_tests()