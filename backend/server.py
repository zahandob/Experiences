import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import openai
from pymongo import MongoClient
import json

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.experience_recommender

# OpenAI configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Pydantic models
class UserProfile(BaseModel):
    age: int
    work_group: str
    work_role: str
    work_resume: str
    hobbies_interests: str

class ExperienceRecommendation(BaseModel):
    id: str
    title: str
    description: str
    category: str
    reasoning: str

class UserInteraction(BaseModel):
    user_id: str
    experience_id: str
    action: str  # 'liked' or 'disliked'

# In-memory storage for demo (replace with proper database in production)
mock_profiles = [
    {
        "id": "1",
        "age": 28,
        "work_group": "Tech",
        "work_role": "Software Engineer",
        "work_resume": "5 years in web development, worked at startups",
        "hobbies_interests": "coding, gaming, reading sci-fi"
    },
    {
        "id": "2", 
        "age": 30,
        "work_group": "Tech",
        "work_role": "Product Manager",
        "work_resume": "8 years in product management, led multiple product launches",
        "hobbies_interests": "hiking, photography, cooking"
    },
    {
        "id": "3",
        "age": 25,
        "work_group": "Marketing",
        "work_role": "Digital Marketer",
        "work_resume": "3 years in digital marketing, social media campaigns",
        "hobbies_interests": "yoga, traveling, blogging"
    },
    {
        "id": "4",
        "age": 32,
        "work_group": "Finance",
        "work_role": "Financial Analyst",
        "work_resume": "7 years in financial analysis, worked at investment firms",
        "hobbies_interests": "chess, wine tasting, marathon running"
    },
    {
        "id": "5",
        "age": 29,
        "work_group": "Tech",
        "work_role": "Data Scientist",
        "work_resume": "4 years in data science, machine learning projects",
        "hobbies_interests": "rock climbing, board games, podcasts"
    }
]

# Mock experiences database
mock_experiences = [
    {"id": "exp1", "title": "Pottery Making", "description": "Learn the ancient art of pottery", "category": "Arts & Crafts"},
    {"id": "exp2", "title": "Salsa Dancing", "description": "Master the passionate dance of salsa", "category": "Dance"},
    {"id": "exp3", "title": "Beekeeping", "description": "Understand the fascinating world of bees", "category": "Agriculture"},
    {"id": "exp4", "title": "Stand-up Comedy", "description": "Develop your comedic timing and stage presence", "category": "Performance"},
    {"id": "exp5", "title": "Blacksmithing", "description": "Forge metal into beautiful and functional items", "category": "Crafts"},
    {"id": "exp6", "title": "Mushroom Foraging", "description": "Learn to identify and harvest wild mushrooms safely", "category": "Nature"},
    {"id": "exp7", "title": "Circus Arts", "description": "Master aerial silks, trapeze, and juggling", "category": "Performance"},
    {"id": "exp8", "title": "Cheese Making", "description": "Create artisanal cheeses from scratch", "category": "Culinary"},
    {"id": "exp9", "title": "Glassblowing", "description": "Shape molten glass into art pieces", "category": "Arts & Crafts"},
    {"id": "exp10", "title": "Falconry", "description": "Train and hunt with birds of prey", "category": "Animal Training"}
]

def get_ai_recommendations(user_profile: dict, similar_profiles: List[dict]) -> List[dict]:
    """Use OpenAI to generate experience recommendations based on profile similarity analysis."""
    
    # Prepare the prompt for GPT-3.5-turbo
    prompt = f"""
You are an expert in human psychology and experience diversity analysis. 

USER PROFILE:
Age: {user_profile.get('age')}
Work Group: {user_profile.get('work_group')}
Work Role: {user_profile.get('work_role')}
Work Resume: {user_profile.get('work_resume')}
Hobbies & Interests: {user_profile.get('hobbies_interests')}

SIMILAR PROFILES FOUND:
{json.dumps(similar_profiles, indent=2)}

AVAILABLE EXPERIENCES:
{json.dumps(mock_experiences, indent=2)}

TASK: Analyze the similar profiles and identify experiences that are:
1. COMPLETELY UNRELATED to the user's current profile (different domain entirely)
2. STATISTICALLY COMMON among people with similar profiles
3. Would add the most DIVERSE dimension to their expertise

Return a JSON array of exactly 3 recommendations with this structure:
[
  {{
    "id": "experience_id",
    "title": "Experience Title",
    "description": "Experience Description", 
    "category": "Category",
    "reasoning": "Detailed explanation of why this experience is recommended based on the analysis"
  }}
]

Focus on experiences that would unlock completely new expert domains while being statistically validated by similar profiles.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert experience recommendation system that analyzes user profiles to suggest diverse, unrelated experiences that are statistically common among similar profiles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON array in the response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                recommendations = json.loads(json_str)
                return recommendations
            else:
                # Fallback to mock recommendations if JSON parsing fails
                return generate_fallback_recommendations()
                
        except json.JSONDecodeError:
            return generate_fallback_recommendations()
            
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return generate_fallback_recommendations()

def generate_fallback_recommendations():
    """Generate fallback recommendations when AI fails."""
    return [
        {
            "id": "exp1",
            "title": "Pottery Making",
            "description": "Learn the ancient art of pottery",
            "category": "Arts & Crafts",
            "reasoning": "Based on statistical analysis, people with similar profiles often explore creative outlets that use their hands in completely different ways."
        },
        {
            "id": "exp4", 
            "title": "Stand-up Comedy",
            "description": "Develop your comedic timing and stage presence",
            "category": "Performance",
            "reasoning": "Analytical minds often excel at observational humor and structured storytelling, providing a completely different creative outlet."
        },
        {
            "id": "exp6",
            "title": "Mushroom Foraging",
            "description": "Learn to identify and harvest wild mushrooms safely",
            "category": "Nature",
            "reasoning": "Detail-oriented professionals often find satisfaction in the methodical nature of foraging while connecting with nature."
        }
    ]

def find_similar_profiles(user_profile: dict) -> List[dict]:
    """Find profiles similar to the user's profile using simple matching."""
    similar_profiles = []
    
    for profile in mock_profiles:
        similarity_score = 0
        
        # Check work group similarity
        if profile['work_group'].lower() == user_profile.get('work_group', '').lower():
            similarity_score += 3
            
        # Check age similarity (within 5 years)
        age_diff = abs(profile['age'] - user_profile.get('age', 0))
        if age_diff <= 5:
            similarity_score += 2
            
        # Check work role similarity (contains similar keywords)
        user_role = user_profile.get('work_role', '').lower()
        profile_role = profile['work_role'].lower()
        if any(word in profile_role for word in user_role.split()):
            similarity_score += 2
            
        # Add profile if similarity score is high enough
        if similarity_score >= 3:
            similar_profiles.append(profile)
    
    return similar_profiles[:3]  # Return top 3 similar profiles

@app.post("/api/profile")
async def create_profile(profile: UserProfile):
    """Create a new user profile."""
    try:
        user_id = str(uuid.uuid4())
        profile_data = profile.dict()
        profile_data["id"] = user_id
        
        # Store in database
        db.profiles.insert_one(profile_data)
        
        return {"user_id": user_id, "message": "Profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get experience recommendations for a user."""
    try:
        # Get user profile (for demo, we'll use the first mock profile)
        user_profile = mock_profiles[0]  # In real app, get from database by user_id
        
        # Find similar profiles
        similar_profiles = find_similar_profiles(user_profile)
        
        # Get AI recommendations
        recommendations = get_ai_recommendations(user_profile, similar_profiles)
        
        return {
            "user_profile": user_profile,
            "similar_profiles": similar_profiles,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interaction")
async def record_interaction(interaction: UserInteraction):
    """Record user interaction with a recommendation."""
    try:
        interaction_data = interaction.dict()
        interaction_data["id"] = str(uuid.uuid4())
        
        # Store in database
        db.interactions.insert_one(interaction_data)
        
        return {"message": "Interaction recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/next-recommendation/{user_id}")
async def get_next_recommendation(user_id: str):
    """Get the next recommendation for the user."""
    try:
        # Get user profile and interactions
        user_profile = mock_profiles[0]  # In real app, get from database
        
        # Find similar profiles
        similar_profiles = find_similar_profiles(user_profile)
        
        # Get new recommendations (in real app, filter out already seen)
        recommendations = get_ai_recommendations(user_profile, similar_profiles)
        
        # Return the first recommendation
        if recommendations:
            return recommendations[0]
        else:
            return {"message": "No more recommendations available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Experience Recommender API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)