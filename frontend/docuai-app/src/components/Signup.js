import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const CustomAlert = ({ message, type }) => (
  <div className={`alert ${type === 'error' ? 'alert-error' : 'alert-success'}`}>
    {message}
  </div>
);

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false); // New state for loading

  const handleLogin = () => {
    navigate('/login');
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
    setLoading(true); // Set loading to true when form is submitted

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords don't match");
      setLoading(false); // Stop loading
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/signin/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An error occurred during signup');
      }

      setMessage('Signup successful! Redirecting to OTP verification...');
      
      // Redirect to the VerifyOTP page after a short delay
      setTimeout(() => {
        navigate('/verify-otp', { state: { email: formData.email } });
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false); // Stop loading after the request completes
    }
  };

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
        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="username"
            placeholder="User Name"
            required
            className="auth-input"
            value={formData.username}
            onChange={handleChange}
          />
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
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            required
            className="auth-input"
            value={formData.confirmPassword}
            onChange={handleChange}
          />
          <button type="submit" className="btn btn-primary cta-btn" disabled={loading}>
            {loading ? 'Signing up...' : 'Sign Up'} {/* Show loading text */}
          </button>
        </form>
        {loading && <p className="loading-text">Processing...</p>} {/* Show loading indicator */}
        {message && <CustomAlert message={message} type="success" />}
        {error && <CustomAlert message={error} type="error" />}
        <p className="terms">
          By signing up, you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>
        </p>
      </main>
    </div>
  );
};

export default Signup;
