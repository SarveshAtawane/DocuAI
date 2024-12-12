import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = () => {
  const [userData, setUserData] = useState({
    username: 'User',
    totalDocuments: 0,
    apiCalls: 0,
    apiKey: 'abcd-1234-efgh-5678'
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [userResponse, activityResponse] = await Promise.all([
          axios.get('http://localhost:8000/user-stats', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('apiKey')}`,
            },
          }),
          axios.get('http://localhost:8000/logs/recent_updates', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('apiKey')}` },
            params: { limit: 3 },
          })
        ]);

        setUserData({
          username: userResponse.data.username,
          totalDocuments: userResponse.data.total_documents,
          apiCalls: userResponse.data.api_calls,
          apiKey: userResponse.data.api_key
        });
        setRecentActivity(activityResponse.data.recent_updates);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleCopyApiKey = () => {
    navigator.clipboard.writeText(userData.apiKey);
    alert('API key copied to clipboard!');
  };

  const handleResetApiKey = async () => {
    try {
      const response = await axios.post('http://localhost:8000/regenerate-api-key', {}, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('apiKey')}` }
      });
      setUserData((prevData) => ({ ...prevData, apiKey: response.data.new_api_key }));
      alert('API key reset successfully!');
    } catch (error) {
      console.error('Error resetting API key:', error);
      alert('Failed to reset API key.');
    }
  };

  const handleResetPassword = async () => {
    const email = prompt('Enter your registered email to reset the password:');
    if (email) {
      try {
        await axios.post('http://localhost:8000/reset-password', { email });
        alert('Password reset email sent successfully!');
      } catch (error) {
        console.error('Error resetting password:', error);
        alert('Failed to send password reset email.');
      }
    }
  };

  const formatTimestampToAgoIST = (timestamp) => {
    const utcDate = new Date(timestamp); // Parse UTC timestamp
    const istOffset = 5.5 * 60 * 60 * 1000; // IST offset in milliseconds
    const istDate = new Date(utcDate.getTime() + istOffset);

    const now = new Date(); // Current time in IST
    const diffInSeconds = Math.floor((now - istDate) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds} seconds ago`;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minutes ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hours ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} days ago`;
    }
  };

  if (loading) {
    return (
      <div className="loading">
        Loading...
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>DocuAI</h2>
        </div>
        <nav className="sidebar-nav">
          <a href="/dashboard">Dashboard</a>
          <a href="/information">Add Information</a>
          <a href="/settings" className="active">Settings</a>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="header">
          <h1>Welcome, <span className="username">{userData.username}</span>!</h1>
        </div>

      

     

        {/* API Key Section */}
        <div className="api-key-container">
          <h2>Your API Key</h2>
          <div className="api-key-box">{userData.apiKey}</div>
          <button onClick={handleCopyApiKey} className="copy-button">Copy API Key</button>
          <button onClick={handleResetApiKey} className="reset-button">Reset API Key</button>
        </div>

        {/* Reset Password Section */}
        <div className="reset-password-container">
          <h2>Reset Password</h2>
          <button onClick={handleResetPassword} className="reset-button">Reset Password</button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;