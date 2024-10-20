import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';  // Ensure you link your CSS file

const CustomAlert = ({ message, type }) => (
  <div className={`alert ${type === 'error' ? 'alert-error' : 'alert-success'}`}>
    {message}
  </div>
);

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);
  const [showVerifyButton, setShowVerifyButton] = useState(false);

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleHome = () => {
    navigate('/');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoginLoading(true);
    setShowVerifyButton(false);

    try {
      const response = await fetch('http://localhost:8000/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An error occurred during login');
      }

      setMessage('Login successful!');
      // You can add further logic here, such as storing the user token
    } catch (err) {
      if (err.message.includes('User not found')) {
        setError('User not registered');
      } else if (err.message.includes('Email not verified')) {
        setError('Email not verified');
        setShowVerifyButton(true);
      } else {
        setError(err.message);
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const handleSendVerificationOTP = async () => {
    setOtpLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await fetch('http://localhost:8000/resend-verification-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: formData.email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to send verification email');
      }

      setMessage('Verification email sent successfully. Please check your inbox.');
      setTimeout(() => {
        navigate('/verify-otp', { state: { email: formData.email } });
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setOtpLoading(false);
    }
  };

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
        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            className="auth-input"
            value={formData.email}
            onChange={handleChange}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            className="auth-input"
            value={formData.password}
            onChange={handleChange}
          />
          <button type="submit" className="btn btn-primary cta-btn" disabled={loginLoading}>
            {loginLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        {(loginLoading || otpLoading) && <p className="loading-text">Processing...</p>}
        {message && <CustomAlert message={message} type="success" />}
        {error && <CustomAlert message={error} type="error" />}
        {error === 'User not registered' && (
          <button className="btn btn-secondary" onClick={handleSignup}>
            Sign Up
          </button>
        )}
        {showVerifyButton && (
          <button className="btn btn-secondary" onClick={handleSendVerificationOTP} disabled={otpLoading}>
            {otpLoading ? 'Sending OTP...' : 'Send Verification OTP'}
          </button>
        )}
        <p className="terms">
          <a href="#">Forgot password?</a>
        </p>
      </main>
    </div>
  );
};

export default Login;