import React from 'react';
import './Dashboard.css';
import { BookOpen, Terminal, HelpCircle, Mail } from 'lucide-react';

const HowToUse = () => {
  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>DocuAI</h2>
        <ul>
          <li><a href="/dashboard">Dashboard</a></li>
          <li><a href="/information">Information</a></li>
          <li><a href="/how-to-use" className="active">How To Use</a></li>
          <li><a href="/settings">Settings</a></li>
        </ul>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="header">
          <h1>How To Use DocuAI</h1>
        </div>

        {/* Getting Started Section */}
        <div className="guide-section">
          <div className="guide-header">
            <BookOpen className="guide-icon" size={24} />
            <h2>Getting Started</h2>
          </div>
          <div className="guide-card">
            <h3>Quick Start Guide</h3>
            <ol>
              <li>
                <strong>Set Up Your Account</strong>
                <p>Use your API key found in the dashboard to authenticate your requests.</p>
              </li>
              <li>
                <strong>Upload Documents</strong>
                <p>Upload your documents through the dashboard or via API endpoints.</p>
              </li>
              <li>
                <strong>Track Usage</strong>
                <p>Monitor your document processing and API calls in the dashboard.</p>
              </li>
            </ol>
          </div>
        </div>

        {/* API Documentation Section */}
        <div className="guide-section">
          <div className="guide-header">
            <Terminal className="guide-icon" size={24} />
            <h2>API Documentation</h2>
          </div>
          <div className="guide-card">
            <h3>Authentication</h3>
            <div className="code-example">
              <code>
                Authorization: Bearer YOUR_API_KEY
              </code>
            </div>

            <h3>Common Endpoints</h3>
            <div className="endpoint-list">
              <div className="endpoint-item">
                <span className="method">GET</span>
                <code>/documents</code>
                <p>List all documents</p>
              </div>
              <div className="endpoint-item">
                <span className="method">POST</span>
                <code>/documents/upload</code>
                <p>Upload a new document</p>
              </div>
              <div className="endpoint-item">
                <span className="method">GET</span>
                <code>/documents/{'{id}'}</code>
                <p>Get document details</p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="guide-section">
          <div className="guide-header">
            <HelpCircle className="guide-icon" size={24} />
            <h2>Frequently Asked Questions</h2>
          </div>
          <div className="guide-card">
            <div className="faq-list">
              <div className="faq-item">
                <h3>What file types are supported?</h3>
                <p>We support PDF, DOCX, TXT, and other common document formats.</p>
              </div>
              <div className="faq-item">
                <h3>How are API calls counted?</h3>
                <p>Each request to our API endpoints counts as one API call.</p>
              </div>
              <div className="faq-item">
                <h3>Is there a rate limit?</h3>
                <p>Yes, free accounts are limited to 1000 API calls per month.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Support Section */}
        <div className="guide-section">
          <div className="guide-header">
            <Mail className="guide-icon" size={24} />
            <h2>Need Help?</h2>
          </div>
          <div className="guide-card">
            <p>Our support team is available 24/7 to help you with any questions.</p>
            <div className="support-contact">
              <p>Email: support@docuai.com</p>
              <button className="contact-button">Contact Support</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowToUse;