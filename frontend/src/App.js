import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Extract ProfileForm component outside to prevent re-renders
const ProfileForm = React.memo(({ userProfile, onInputChange, onSubmit, loading }) => {
  return (
    <div className="profile-form-container">
      <div className="profile-form-card">
        <h1 className="form-title">Discover Your Next Adventure</h1>
        <p className="form-subtitle">Tell us about yourself and we'll suggest amazing experiences you never knew you'd love!</p>
        
        <form onSubmit={onSubmit} className="profile-form">
          <div className="form-group">
            <label htmlFor="age">Age</label>
            <input
              type="number"
              id="age"
              name="age"
              value={userProfile.age}
              onChange={(e) => onInputChange('age', e.target.value)}
              placeholder="Enter your age"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="work_group">Work Group/Industry</label>
            <input
              type="text"
              id="work_group"
              name="work_group"
              value={userProfile.work_group}
              onChange={(e) => onInputChange('work_group', e.target.value)}
              placeholder="e.g., Technology, Finance, Healthcare"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="work_role">Work Role</label>
            <input
              type="text"
              id="work_role"
              name="work_role"
              value={userProfile.work_role}
              onChange={(e) => onInputChange('work_role', e.target.value)}
              placeholder="e.g., Software Engineer, Product Manager"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="work_resume">Work Experience Summary</label>
            <textarea
              id="work_resume"
              name="work_resume"
              value={userProfile.work_resume}
              onChange={(e) => onInputChange('work_resume', e.target.value)}
              placeholder="Brief summary of your work experience and achievements"
              rows="4"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="hobbies_interests">Hobbies & Interests</label>
            <textarea
              id="hobbies_interests"
              name="hobbies_interests"
              value={userProfile.hobbies_interests}
              onChange={(e) => onInputChange('hobbies_interests', e.target.value)}
              placeholder="What do you enjoy doing in your free time?"
              rows="3"
              required
              autoComplete="off"
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Creating Profile...' : 'Discover Experiences'}
          </button>
        </form>
      </div>
    </div>
  );
});

function App() {
  const [currentStep, setCurrentStep] = useState('profile'); // 'profile', 'recommendations'
  const [userProfile, setUserProfile] = useState({
    age: '',
    work_group: '',
    work_role: '',
    work_resume: '',
    hobbies_interests: ''
  });
  const [currentRecommendation, setCurrentRecommendation] = useState(null);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cardIndex, setCardIndex] = useState(0);
  const [likedExperiences, setLikedExperiences] = useState([]);

  // Stable input change handler
  const handleInputChange = useCallback((field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Handle profile form submission
  const handleProfileSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseInt(userProfile.age),
          work_group: userProfile.work_group,
          work_role: userProfile.work_role,
          work_resume: userProfile.work_resume,
          hobbies_interests: userProfile.hobbies_interests
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setUserId(data.user_id);
        setCurrentStep('recommendations');
        loadNextRecommendation(data.user_id);
      } else {
        console.error('Failed to create profile');
      }
    } catch (error) {
      console.error('Error creating profile:', error);
    } finally {
      setLoading(false);
    }
  }, [userProfile]);

  // Load next recommendation
  const loadNextRecommendation = async (userIdToUse = userId) => {
    setLoading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/next-recommendation/${userIdToUse}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.message) {
          // No more recommendations
          setCurrentRecommendation(null);
        } else {
          setCurrentRecommendation(data);
        }
      } else {
        console.error('Failed to load recommendation');
      }
    } catch (error) {
      console.error('Error loading recommendation:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle card swipe/action
  const handleCardAction = async (action) => {
    if (!currentRecommendation) return;

    setLoading(true);
    
    try {
      // Record interaction
      await fetch(`${BACKEND_URL}/api/interaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          experience_id: currentRecommendation.id,
          action: action
        }),
      });

      // Add to liked experiences if user liked it
      if (action === 'liked') {
        setLikedExperiences(prev => [...prev, currentRecommendation]);
      }

      // Load next recommendation
      await loadNextRecommendation();
      setCardIndex(prev => prev + 1);
      
    } catch (error) {
      console.error('Error recording interaction:', error);
    } finally {
      setLoading(false);
    }
  };

  // Recommendation card component
  const RecommendationCard = ({ recommendation }) => (
    <div className="recommendation-card">
      <div className="card-header">
        <h2 className="card-title">{recommendation.title}</h2>
        <span className="card-category">{recommendation.category}</span>
      </div>
      
      <div className="card-content">
        <p className="card-description">{recommendation.description}</p>
        
        <div className="card-reasoning">
          <h3>Why This Experience?</h3>
          <p>{recommendation.reasoning}</p>
        </div>
      </div>
      
      <div className="card-actions">
        <button 
          className="dislike-btn"
          onClick={() => handleCardAction('disliked')}
          disabled={loading}
        >
          ❌ Not for me
        </button>
        <button 
          className="like-btn"
          onClick={() => handleCardAction('liked')}
          disabled={loading}
        >
          ✅ I'm interested!
        </button>
      </div>
    </div>
  );

  // Recommendations view
  const RecommendationsView = () => (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h1>Your Experience Recommendations</h1>
        <p>Swipe through suggestions tailored just for you!</p>
        {likedExperiences.length > 0 && (
          <div className="liked-count">
            💖 {likedExperiences.length} experiences you're interested in
          </div>
        )}
      </div>

      <div className="cards-container">
        {loading ? (
          <div className="loading-card">
            <div className="spinner"></div>
            <p>Finding your next adventure...</p>
          </div>
        ) : currentRecommendation ? (
          <RecommendationCard recommendation={currentRecommendation} />
        ) : (
          <div className="end-card">
            <h2>🎉 You've explored all recommendations!</h2>
            <p>Great job! You've discovered {likedExperiences.length} new experiences to try.</p>
            <button 
              className="restart-btn"
              onClick={() => {
                setCurrentStep('profile');
                setUserProfile({
                  age: '',
                  work_group: '',
                  work_role: '',
                  work_resume: '',
                  hobbies_interests: ''
                });
                setLikedExperiences([]);
                setCardIndex(0);
              }}
            >
              Start New Session
            </button>
          </div>
        )}
      </div>

      {likedExperiences.length > 0 && (
        <div className="liked-experiences">
          <h3>Your Interested Experiences</h3>
          <div className="liked-list">
            {likedExperiences.map((exp, index) => (
              <div key={index} className="liked-item">
                <span className="liked-title">{exp.title}</span>
                <span className="liked-category">{exp.category}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="App">
      {currentStep === 'profile' ? <ProfileForm /> : <RecommendationsView />}
    </div>
  );
}

export default App;