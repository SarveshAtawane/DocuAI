import React from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate('/login');
  };

  return (
    <div className="container">
      <header>
        <div className="logo">DocuAI</div>
        <div className="auth-buttons">
          <button className="btn btn-secondary" onClick={handleLogin}>Login</button>
        </div>
      </header>
      <main>
        <h1>Verify OTP</h1>
        <form className="auth-form">
          <input type="text" placeholder="6 digit otp" required className="auth-input" />
            <button type="submit" className="btn btn-primary cta-btn">submit</button>
        </form>
        <p className="terms">
         Please enter the otp sent to your email
        </p>
      </main>
    </div>
  );
};

export default Signup;