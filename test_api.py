#!/usr/bin/env python3
"""
Simple test script to verify the API is working
"""
import requests
import json

def test_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_meme_generation():
    try:
        payload = {
            "text_prompt": "testing API fix with image URLs",
            "max_dimension": 300
        }
        
        print(f"Testing meme generation with: {payload}")
        response = requests.post(
            "http://localhost:8000/api/v1/generate-meme",
            json=payload,
            timeout=60
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Generated {data['count']} memes")
            print(f"Files saved in: {data['output_directory']}")
            print(f"Generation time: {data['generation_time']:.2f} seconds")
            
            print(f"\n📷 Meme Image URLs ({len(data['meme_list'])} total):")
            for i, url in enumerate(data['meme_list'][:3], 1):  # Show first 3 URLs
                print(f"  {i}. {url}")
            if len(data['meme_list']) > 3:
                print(f"  ... and {len(data['meme_list']) - 3} more memes")
            
            print(f"\n🔗 You can access any meme by visiting the URL in your browser!")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Testing Meme Generator API...")
    
    if test_health():
        print("\n🚀 Testing meme generation...")
        test_meme_generation()
    else:
        print("❌ Server not responding") 