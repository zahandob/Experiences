import requests
import json
import sys
import time
from datetime import datetime

class ExperienceRecommenderTester:
    def __init__(self, base_url="https://ba9c4fba-7e59-4e76-9046-432c1a2b5e28.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.seen_recommendations = []
        
    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
    
    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            print(f"Health check response: {response}")
        return success
    
    def test_create_profile(self, profile_data):
        """Test creating a user profile"""
        success, response = self.run_test(
            "Create Profile",
            "POST",
            "api/profile",
            200,
            data=profile_data
        )
        if success and 'user_id' in response:
            self.user_id = response['user_id']
            print(f"Created profile with user_id: {self.user_id}")
            return True
        return False
    
    def test_get_recommendations(self):
        """Test getting recommendations for a user"""
        if not self.user_id:
            print("❌ Cannot test recommendations without a user_id")
            return False
        
        success, response = self.run_test(
            "Get Recommendations",
            "GET",
            f"api/recommendations/{self.user_id}",
            200
        )
        if success:
            if 'recommendations' in response and len(response['recommendations']) > 0:
                print(f"Received {len(response['recommendations'])} recommendations")
                print(f"First recommendation: {response['recommendations'][0]['title']}")
                return True
            else:
                print("❌ No recommendations returned")
                return False
        return False
    
    def test_next_recommendation(self):
        """Test getting the next recommendation"""
        if not self.user_id:
            print("❌ Cannot test next recommendation without a user_id")
            return False
        
        success, response = self.run_test(
            "Get Next Recommendation",
            "GET",
            f"api/next-recommendation/{self.user_id}",
            200
        )
        if success:
            if 'title' in response:
                print(f"Next recommendation: {response['title']}")
                self.recommendation_id = response.get('id')
                
                # Check if this is an AI-generated recommendation (should have reasoning)
                if 'reasoning' in response:
                    print(f"✅ AI reasoning provided: {response['reasoning'][:100]}...")
                else:
                    print("❌ No AI reasoning found in recommendation")
                
                # Check for diversity (not seen before)
                is_duplicate = response['title'] in self.seen_recommendations
                if is_duplicate:
                    print(f"❌ Duplicate recommendation: {response['title']}")
                else:
                    print(f"✅ New unique recommendation: {response['title']}")
                    self.seen_recommendations.append(response['title'])
                
                return True
            else:
                print("❌ No next recommendation returned or invalid format")
                return False
        return False
    
    def test_interaction(self, action="liked"):
        """Test recording a user interaction"""
        if not self.user_id or not hasattr(self, 'recommendation_id'):
            print("❌ Cannot test interaction without user_id and recommendation_id")
            return False
        
        interaction_data = {
            "user_id": self.user_id,
            "experience_id": self.recommendation_id,
            "action": action
        }
        
        success, response = self.run_test(
            f"Record {action.capitalize()} Interaction",
            "POST",
            "api/interaction",
            200,
            data=interaction_data
        )
        return success

def main():
    # Setup
    tester = ExperienceRecommenderTester()
    
    # Sample profile data
    profile_data = {
        "age": 28,
        "work_group": "Technology",
        "work_role": "Software Engineer",
        "work_resume": "5 years of full-stack development experience, worked at 2 startups",
        "hobbies_interests": "coding, reading, hiking, photography"
    }
    
    # Run tests
    print("\n===== TESTING EXPERIENCE RECOMMENDER API =====\n")
    
    # Test health check
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test profile creation
    if not tester.test_create_profile(profile_data):
        print("❌ Profile creation failed, stopping tests")
        return 1
    
    # Test getting recommendations
    if not tester.test_get_recommendations():
        print("❌ Getting recommendations failed")
    
    # Test getting next recommendation
    if not tester.test_next_recommendation():
        print("❌ Getting next recommendation failed")
    else:
        # Test recording interaction
        if not tester.test_interaction("liked"):
            print("❌ Recording interaction failed")
        
        # Test getting another recommendation after interaction
        if not tester.test_next_recommendation():
            print("❌ Getting next recommendation after interaction failed")
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())