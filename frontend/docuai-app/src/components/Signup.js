import React from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();

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
        </div>
      </header>
      <main>
        <h1>Create an Account</h1>
        <form className="auth-form">
          <input type="text" placeholder="User Name" required className="auth-input" />
          <input type="email" placeholder="Email" required className="auth-input" />
          <input type="password" placeholder="Password" required className="auth-input" />
          <input type="password" placeholder="Confirm Password" required className="auth-input" />
          <button type="submit" className="btn btn-primary cta-btn">Sign Up</button>
        </form>
        <p className="terms">
          By signing up, you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>
        </p>
      </main>
    </div>
  );
};

export default Signup;