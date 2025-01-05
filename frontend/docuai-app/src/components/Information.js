import React, { useState, useEffect } from 'react';
import { Upload, Link, Trash2 } from 'lucide-react';
import './Information.css';

const Information = () => {
  const [files, setFiles] = useState([]);
  const [githubLink, setGithubLink] = useState('');
  const [websiteLinks, setWebsiteLinks] = useState(['']);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [refreshDocuments, setRefreshDocuments] = useState(false);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles((prevFiles) => {
      const uniqueFiles = [...prevFiles, ...newFiles].reduce((acc, file) => {
        if (!acc.find((existingFile) => existingFile.name === file.name)) {
          acc.push(file);
        }
        return acc;
      }, []);
      return uniqueFiles;
    });
  };

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch('http://localhost:8000/documents/', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('apiKey')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch documents');
        }

        const data = await response.json();
        console.log('Fetched Documents:', data);
        setDocuments(data.documents || []);
      } catch (error) {
        console.error('Error fetching documents:', error);
        setDocuments([]);
      }
    };

    fetchDocuments();
  }, [refreshDocuments]);

  const removeFile = (index) => {
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  };

  const handleWebsiteLinkChange = (index, value) => {
    const newLinks = [...websiteLinks];
    newLinks[index] = value;
    setWebsiteLinks(newLinks);
  };

  const addWebsiteLink = () => {
    setWebsiteLinks([...websiteLinks, '']);
  };

  const removeWebsiteLink = (index) => {
    const newLinks = websiteLinks.filter((_, i) => i !== index);
    setWebsiteLinks(newLinks);
  };

  const handleSubmit = async () => {
    setUploading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));
      if (githubLink) {
        formData.append('github_repo_link', githubLink);
      }
      websiteLinks.forEach((link) => {
        if (link) {
          formData.append('website_link', link);
        }
      });

      const response = await fetch('http://localhost:8000/doc_upload/', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('apiKey')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      setFiles([]);
      setGithubLink('');
      setWebsiteLinks(['']);
      setRefreshDocuments((prev) => !prev);
    } catch (error) {
      console.error('Error uploading:', error);
    } finally {
      setUploading(false);
    }
  };

  const generate_embedding = async () => {
    try {
      console.log('Generating embeddings...');
    } catch (error) {
      console.error('Error generating embeddings:', error);
    }
  };

  const handleDocumentDelete = async (docId) => {
    try {
      const response = await fetch(`http://localhost:8000/doc_delete/${docId}/`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('apiKey')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      setRefreshDocuments((prev) => !prev);
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>DocuAI</h2>
        </div>
        <nav className="sidebar-nav">
          <a href="/dashboard">Dashboard</a>
          <a href="#" className="active">Add Information</a>
          <a href="/settings">Settings</a>
        </nav>
      </div>

      <div className="main-content">
        <h1 className="page-title">Add Information</h1>
        <div className="upload-sections">
          <div className="upload-card">
            <div className="card-header">
              <h2>
                <Upload size={20} />
                Upload Documents
              </h2>
            </div>
            <div className="card-content">
              <input
                type="file"
                multiple
                accept=".txt,.pdf"
                onChange={handleFileChange}
                className="file-input"
              />
              <div className="file-types">Supported formats: PDF, TXT</div>
              {files.length > 0 && (
                <div className="selected-files">
                  <h4>Selected files:</h4>
                  <ul>
                    {files.map((file, index) => (
                      <li key={index} className="file-item">
                        {file.name}
                        <button onClick={() => removeFile(index)} className="remove-button">
                          Remove
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="upload-card">
            <div className="card-header">
              <h2>
                <Link size={20} />
                Website Links
              </h2>
            </div>
            <div className="card-content">
              {websiteLinks.map((link, index) => (
                <div key={index} className="website-link-input">
                  <input
                    type="url"
                    placeholder="Enter website URL"
                    value={link}
                    onChange={(e) => handleWebsiteLinkChange(index, e.target.value)}
                    className="text-input"
                  />
                  {websiteLinks.length > 1 && (
                    <button onClick={() => removeWebsiteLink(index)} className="remove-button">
                      Remove
                    </button>
                  )}
                </div>
              ))}
              <button onClick={addWebsiteLink} className="add-button">
                Add Another Website Link
              </button>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={
              uploading || (files.length === 0 && !githubLink && websiteLinks.every((link) => !link))
            }
            className="submit-button"
          >
            {uploading ? 'Uploading...' : 'Upload All'}
          </button>
          <button
            onClick={generate_embedding}
            disabled={
              uploading || (documents.length === 0 && !githubLink && websiteLinks.every((link) => !link))
            }
            className="generate-api"
          >
            {uploading ? 'Generating...' : 'Generate API Key'}
          </button>

          <div className="documents-section">
            <h2>All Documents</h2>
            {Array.isArray(documents) && documents.length > 0 ? (
              <ul className="documents-list">
                {documents.map((doc, index) => (
                  <li key={doc._id || doc.id || index} className="document-item">
                    <span className="document-name">
                      {doc.filename || doc.website_link|| doc.url}
                    </span>
                    <button
                      onClick={() => handleDocumentDelete(doc._id || doc.id)}
                      className="delete-document-button"
                    >
                      <Trash2 size={16} /> Delete
                    </button>
                  </li>
                ))}
              </ul>
            ) : Array.isArray(documents) && documents.length === 0 ? (
              <p>No documents available</p>
            ) : (
              <p>Loading...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Information;
