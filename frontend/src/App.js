import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Extract ProfileForm component outside to prevent re-renders
const ProfileForm = React.memo(({ userProfile, onInputChange, onSubmit, loading }) => {
  return (
    <div className="profile-form-container">
      <div className="profile-form-card">
        <h1 className="form-title">Experience Profile Extraction</h1>
        <p className="form-subtitle">Provide detailed technical and professional data for precise archetype matching against expert individuals.</p>
        
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
            <label htmlFor="industry_sector">Industry Sector</label>
            <input
              type="text"
              id="industry_sector"
              name="industry_sector"
              value={userProfile.industry_sector}
              onChange={(e) => onInputChange('industry_sector', e.target.value)}
              placeholder="e.g., SaaS, FinTech, Biotech, Manufacturing, Consulting"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="current_role">Current Role & Level</label>
            <input
              type="text"
              id="current_role"
              name="current_role"
              value={userProfile.current_role}
              onChange={(e) => onInputChange('current_role', e.target.value)}
              placeholder="e.g., Senior Software Engineer, VP Product, Managing Director"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="technical_stack">Technical Stack / Core Skills</label>
            <textarea
              id="technical_stack"
              name="technical_stack"
              value={userProfile.technical_stack}
              onChange={(e) => onInputChange('technical_stack', e.target.value)}
              placeholder="List specific technologies, methodologies, frameworks, tools you work with regularly"
              rows="3"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="career_trajectory">Career Trajectory & Key Achievements</label>
            <textarea
              id="career_trajectory"
              name="career_trajectory"
              value={userProfile.career_trajectory}
              onChange={(e) => onInputChange('career_trajectory', e.target.value)}
              placeholder="Timeline of roles, promotions, major projects, quantified achievements, company stages (startup to enterprise)"
              rows="4"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="educational_background">Educational & Certification Background</label>
            <textarea
              id="educational_background"
              name="educational_background"
              value={userProfile.educational_background}
              onChange={(e) => onInputChange('educational_background', e.target.value)}
              placeholder="Degrees, institutions, certifications, specialized training programs, self-taught domains"
              rows="3"
              required
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="leadership_experience">Leadership & Management Experience</label>
            <textarea
              id="leadership_experience"
              name="leadership_experience"
              value={userProfile.leadership_experience}
              onChange={(e) => onInputChange('leadership_experience', e.target.value)}
              placeholder="Team sizes managed, P&L responsibility, cross-functional leadership, mentoring, board interactions"
              rows="3"
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="external_activities">External Professional Activities</label>
            <textarea
              id="external_activities"
              name="external_activities"
              value={userProfile.external_activities}
              onChange={(e) => onInputChange('external_activities', e.target.value)}
              placeholder="Speaking engagements, publications, advisory roles, board positions, open source contributions, patents"
              rows="3"
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="investment_financial">Investment & Financial Activities</label>
            <textarea
              id="investment_financial"
              name="investment_financial"
              value={userProfile.investment_financial}
              onChange={(e) => onInputChange('investment_financial', e.target.value)}
              placeholder="Angel investing, trading, real estate, business ownership, financial instruments experience"
              rows="2"
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="serious_hobbies">Serious Hobbies & Skill Development</label>
            <textarea
              id="serious_hobbies"
              name="serious_hobbies"
              value={userProfile.serious_hobbies}
              onChange={(e) => onInputChange('serious_hobbies', e.target.value)}
              placeholder="High-skill hobbies requiring significant time investment, competitive activities, artistic pursuits, physical challenges"
              rows="3"
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label htmlFor="network_connections">Professional Network & Connections</label>
            <textarea
              id="network_connections"
              name="network_connections"
              value={userProfile.network_connections}
              onChange={(e) => onInputChange('network_connections', e.target.value)}
              placeholder="Industry connections, alumni networks, professional associations, mentors, notable collaborations"
              rows="2"
              autoComplete="off"
            />
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Processing Profile...' : 'Extract Experience Archetypes'}
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
    industry_sector: '',
    current_role: '',
    technical_stack: '',
    career_trajectory: '',
    educational_background: '',
    leadership_experience: '',
    external_activities: '',
    investment_financial: '',
    serious_hobbies: '',
    network_connections: ''
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
          industry_sector: userProfile.industry_sector,
          current_role: userProfile.current_role,
          technical_stack: userProfile.technical_stack,
          career_trajectory: userProfile.career_trajectory,
          educational_background: userProfile.educational_background,
          leadership_experience: userProfile.leadership_experience,
          external_activities: userProfile.external_activities,
          investment_financial: userProfile.investment_financial,
          serious_hobbies: userProfile.serious_hobbies,
          network_connections: userProfile.network_connections
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
                  industry_sector: '',
                  current_role: '',
                  technical_stack: '',
                  career_trajectory: '',
                  educational_background: '',
                  leadership_experience: '',
                  external_activities: '',
                  investment_financial: '',
                  serious_hobbies: '',
                  network_connections: ''
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
      {currentStep === 'profile' ? (
        <ProfileForm 
          userProfile={userProfile}
          onInputChange={handleInputChange}
          onSubmit={handleProfileSubmit}
          loading={loading}
        />
      ) : (
        <RecommendationsView />
      )}
    </div>
  );
}

export default App;