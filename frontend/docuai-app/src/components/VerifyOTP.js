import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const CustomAlert = ({ message, type }) => (
  <div className={`alert ${type === 'error' ? 'alert-error' : 'alert-success'}`}>
    {message}
  </div>
);

const OTPVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [otp, setOtp] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpExpirationTime, setOtpExpirationTime] = useState(60);

  const email = location.state?.email;

  useEffect(() => {
    if (!email) {
      navigate('/login');
    }
  }, [email, navigate]);

  useEffect(() => {
    let expirationInterval;
    if (otpExpirationTime > 0) {
      expirationInterval = setInterval(() => {
        setOtpExpirationTime((prevTime) => prevTime - 1);
      }, 1000);
    }

    return () => clearInterval(expirationInterval);
  }, [otpExpirationTime]);

  const handleLogin = () => {
    navigate('/login');
  };

  const handleResendOTP = async () => {
    try {
      setLoading(true);
      setError('');
      setMessage('');

      const response = await fetch('http://localhost:8000/resend-verification-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to resend OTP');
      }

      setMessage('Verification email sent successfully. Please check your inbox.');
      setOtpExpirationTime(60); // Reset the timer to 60 seconds
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/verify-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          otp: otp,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'OTP verification failed');
      }

      setMessage('Email verified successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const buttonStyle = {
    opacity: loading || otpExpirationTime > 0 ? 0.5 : 1,
    cursor: loading || otpExpirationTime > 0 ? 'not-allowed' : 'pointer',
    transition: 'opacity 0.3s ease',
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
        <form className="auth-form" onSubmit={handleSubmit}>
          <input 
            type="text" 
            placeholder="6 digit OTP" 
            required 
            className="auth-input"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength={6}
          />
          <button type="submit" className="btn btn-primary cta-btn" disabled={loading}>
            {loading ? 'Verifying...' : 'Submit'}
          </button>
        </form>
        {loading && <p className="loading-text">Processing...</p>}
        {message && <CustomAlert message={message} type="success" />}
        {error && <CustomAlert message={error} type="error" />}

        <p className="terms">
          Please enter the OTP sent to your email. 
          {otpExpirationTime > 0 ? ` OTP expires in ${otpExpirationTime} seconds.` : ' OTP has expired.'}
        </p>

        <button 
          className="btn btn-secondary" 
          onClick={handleResendOTP} 
          disabled={loading || otpExpirationTime > 0}
          style={buttonStyle}
        >
          Resend OTP
        </button>
      </main>
    </div>
  );
};

export default OTPVerification;