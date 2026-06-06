#!/usr/bin/env python3
"""
Quick API test script for Virtuoso Portfolio
Tests all endpoints to verify functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:7860"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\n🔍 Testing Chat Endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "Tell me about your experience"}
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint working")
            print(f"   Action: {result.get('action')}")
            print(f"   Message: {result.get('message', result.get('error', 'N/A'))[:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_resume_download():
    """Test resume download endpoint"""
    print("\n🔍 Testing Resume Download Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/download-resume")
        if response.status_code == 200:
            size = len(response.content)
            print("✅ Resume download working")
            print(f"   File size: {size} bytes")
            return True
        else:
            print(f"❌ Resume download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_interview_scheduling():
    """Test interview scheduling endpoint"""
    print("\n🔍 Testing Interview Scheduling Endpoint...")
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        payload = {
            "date": tomorrow,
            "time": "14:00",
            "topic": "Full Stack Engineer Role",
            "link": "https://zoom.us/j/123456789",
            "address": "123 Main Street, Johannesburg",
            "timezone": "US/Eastern"
        }
        response = requests.post(
            f"{BASE_URL}/api/schedule-interview",
            json=payload
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Interview scheduling working")
            print(f"   Action: {result.get('action')}")
            print(f"   Message: {result.get('message', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ Interview scheduling failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Virtuoso Portfolio API Test Suite")
    print("=" * 60)
    
    tests = [
        test_health,
        test_chat,
        test_resume_download,
        test_interview_scheduling,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! API is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
