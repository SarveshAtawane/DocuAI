import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';  // Ensure you link your CSS file

const Home = () => {
  const navigate = useNavigate();

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleLogin = () => {
    navigate('/login');
  };
  const handleHome = () => {
    navigate('/');
  }

  return (
    <div className="container">
      <header>
        <div className="logo" onClick={handleHome}>DocuAI</div>
        <div className="auth-buttons">
          <button className="btn btn-secondary" onClick={handleLogin}>Login</button>
          <button className="btn btn-primary" onClick={handleSignup}>Sign Up</button>
        </div>
      </header>
      <main>
        <h1>Transform Your Documentation into an AI-Powered Chatbot</h1>
        <p>Upload your docs, get an API, and integrate a custom AI assistant into your product in minutes.</p>
        <button className="btn btn-primary cta-btn"  onClick={handleSignup}>Start Free Trial</button>
        <div className="features">
          {/* Uncomment this section if you want to show features */}
          {/* 
          <div className="feature">
            <h3>Easy Upload</h3>
            <p>Simply upload your documentation files and let DocuAI do the rest.</p>
          </div>
          <div className="feature">
            <h3>Custom API</h3>
            <p>Get a unique API tailored to your documentation for seamless integration.</p>
          </div>
          <div className="feature">
            <h3>Intelligent Assistance</h3>
            <p>Our AI understands context and provides accurate, helpful responses.</p>
          </div>
          */}
        </div>
      </main>
    </div>
  );
};

export default Home;