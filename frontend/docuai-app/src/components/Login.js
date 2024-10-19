import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';  // Ensure you link your CSS file
const Login = () => {
  const navigate = useNavigate();

  const handleSignup = () => {
    navigate('/signup');
  };
  const handleHome = () => {
    navigate('/');
  }
  return (
    <div className="container">
      <header>
      <div className="logo" onClick={handleHome}>DocuAI</div>

        <div className="auth-buttons">
          <button className="btn btn-secondary" onClick={handleSignup}>Sign Up</button>
        </div>
      </header>
      <main>
        <h1>Login</h1>
        <form className="auth-form">
          <input type="email" placeholder="Email" required className="auth-input" />
          <input type="password" placeholder="Password" required className="auth-input" />
          <button type="submit" className="btn btn-primary cta-btn">Login</button>
        </form>
        <p className="terms">
          <a href="#">Forgot password?</a>
        </p>
      </main>
    </div>
  );
};

export default Login;