import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import openai
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
print(f"OpenAI API Key loaded: {'✓' if openai.api_key else '✗'}")
print(f"OpenAI API Key starts with: {openai.api_key[:20] if openai.api_key else 'None'}...")

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
    {"id": "exp10", "title": "Falconry", "description": "Train and hunt with birds of prey", "category": "Animal Training"},
    {"id": "exp11", "title": "Archery", "description": "Master the ancient art of bow and arrow", "category": "Sports"},
    {"id": "exp12", "title": "Soap Making", "description": "Create natural soaps with unique scents", "category": "Crafts"},
    {"id": "exp13", "title": "Woodworking", "description": "Build furniture and decorative pieces", "category": "Crafts"},
    {"id": "exp14", "title": "Meditation & Mindfulness", "description": "Learn techniques for mental clarity", "category": "Wellness"},
    {"id": "exp15", "title": "Urban Gardening", "description": "Grow fresh produce in small spaces", "category": "Agriculture"}
]

# Track shown recommendations per user
user_shown_recommendations = {}

def get_ai_recommendations(user_profile: dict, similar_profiles: List[dict], shown_ids: List[str] = []) -> List[dict]:
    """Use OpenAI to generate experience recommendations based on profile similarity analysis."""
    
    if not openai.api_key:
        print("OpenAI API key not found, using fallback recommendations")
        return generate_fallback_recommendations(shown_ids)
    
    # Filter out already shown experiences
    available_experiences = [exp for exp in mock_experiences if exp['id'] not in shown_ids]
    
    if not available_experiences:
        return []
    
    # Prepare the new sophisticated prompt
    prompt = f"""
You are an autonomous extractor of experiential data. Your task is to build a structured profile of a user by collecting only high-value, transferable, and concrete life and career experiences. Disregard trivial or superficial events. Operate in absolute mode: give no explanations, no clarifications, and no filler. Speak in brief, functional commands.

Your goal is to create an experience profile so detailed it can be mapped against known individuals (real-world) to match the user with compatible experts with the experience they desire. These archetypes can then serve as AI advisors.

**USER PROFILE:**
Age: {user_profile.get('age')}
Work Group: {user_profile.get('work_group')}
Work Role: {user_profile.get('work_role')}
Work Resume: {user_profile.get('work_resume')}
Hobbies & Interests: {user_profile.get('hobbies_interests')}

**PROCESS:**
1. Analyze user's profile against individuals with similar experiences (Wikipedia, biographies, forums).
2. Extract common high-value experiences shared by these similar individuals.
3. Match against available experiences below.

**AVAILABLE EXPERIENCES:**
{json.dumps(available_experiences, indent=2)}

**CRITICAL ORDERING REQUIREMENT:**
Order suggestions by discovery value, highest to lowest priority:

**HIGHEST PRIORITY:** Experiences COMPLETELY UNRELATED to user's current profile BUT statistically highly common among matched profiles. These reveal hidden dimensions and unlock new expert domains.

**LOWEST PRIORITY:** More related to user's current profile, rabbit hole extensions of existing elements.

Goal: MAXIMUM DISCOVERY of unrelated experiences.

**When generating experience suggestions, do not rely only on explicit keywords or categories. Instead, match the user's current experiences against other individuals with similar experiences. Then identify what experiences these individuals have in common and suggest these.**

**OUTPUT REQUIREMENT:**
Return exactly 1 experience suggestion as JSON:

{{
  "id": "experience_id",
  "title": "Experience Title",
  "description": "Experience Description",
  "category": "Category", 
  "reasoning": "Brief directive explanation of discovery value and real-world individual matches"
}}

Use strict, directive language. No friendly tone. Focus on maximum discovery potential.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an autonomous extractor of experiential data. Use strict, directive language. Focus on maximum discovery potential by matching user profiles against real individuals and extracting completely unrelated but statistically common experiences."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content
        print(f"OpenAI response: {ai_response}")
        
        # Try to extract JSON from the response
        try:
            # Find JSON object in the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                recommendation = json.loads(json_str)
                print(f"Parsed recommendation: {recommendation}")
                return [recommendation]  # Return as array for consistency
            else:
                print("Could not find JSON object in response, using fallback")
                return generate_fallback_recommendations(shown_ids)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}, using fallback")
            return generate_fallback_recommendations(shown_ids)
            
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        return generate_fallback_recommendations(shown_ids)

def generate_fallback_recommendations(shown_ids: List[str] = []):
    """Generate fallback recommendations when AI fails."""
    
    fallback_recommendations = [
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
        },
        {
            "id": "exp2",
            "title": "Salsa Dancing",
            "description": "Master the passionate dance of salsa",
            "category": "Dance",
            "reasoning": "Physical expression through dance provides a perfect counterbalance to analytical work."
        },
        {
            "id": "exp3",
            "title": "Beekeeping",
            "description": "Understand the fascinating world of bees",
            "category": "Agriculture",
            "reasoning": "Working with nature and understanding complex systems appeals to methodical thinkers."
        }
    ]
    
    # Filter out already shown recommendations
    available_fallbacks = [rec for rec in fallback_recommendations if rec['id'] not in shown_ids]
    
    if available_fallbacks:
        return [available_fallbacks[0]]  # Return one recommendation
    else:
        return []

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
        
        # Initialize shown recommendations for this user
        user_shown_recommendations[user_id] = []
        
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
        shown_ids = user_shown_recommendations.get(user_id, [])
        recommendations = get_ai_recommendations(user_profile, similar_profiles, shown_ids)
        
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
        
        # Add to shown recommendations for this user
        if interaction.user_id not in user_shown_recommendations:
            user_shown_recommendations[interaction.user_id] = []
        user_shown_recommendations[interaction.user_id].append(interaction.experience_id)
        
        return {"message": "Interaction recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/next-recommendation/{user_id}")
async def get_next_recommendation(user_id: str):
    """Get the next recommendation for the user."""
    try:
        # Get user profile
        user_profile = mock_profiles[0]  # In real app, get from database
        
        # Find similar profiles
        similar_profiles = find_similar_profiles(user_profile)
        
        # Get new recommendations (filter out already seen)
        shown_ids = user_shown_recommendations.get(user_id, [])
        recommendations = get_ai_recommendations(user_profile, similar_profiles, shown_ids)
        
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