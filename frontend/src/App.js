import React, { useState } from 'react';
import axios from 'axios';
import './styles/App.css';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    if (!repoUrl.includes('github.com')) {
      setError('Please enter a valid GitHub repository URL');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/generate-docs', {
        repo_url: repoUrl.trim()
      });

      setResult(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while generating documentation');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setRepoUrl('');
    setResult(null);
    setError('');
  };

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <h1 className="title">
            <span className="title-icon">📚</span>
            ConductDoc
          </h1>
          <p className="subtitle">
            AI-Powered Python Documentation Generator
          </p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <div className="card">
            <div className="card-header">
              <h2>Generate Documentation</h2>
              <p>Enter a GitHub repository URL to automatically generate comprehensive documentation</p>
            </div>

            <form onSubmit={handleSubmit} className="form">
              <div className="input-group">
                <label htmlFor="repo-url">GitHub Repository URL</label>
                <input
                  id="repo-url"
                  type="url"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  className="input"
                  disabled={loading}
                />
              </div>

              <div className="button-group">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-primary"
                >
                  {loading ? (
                    <>
                      <span className="spinner"></span>
                      Generating...
                    </>
                  ) : (
                    'Generate Documentation'
                  )}
                </button>
                
                {(result || error) && (
                  <button
                    type="button"
                    onClick={handleReset}
                    className="btn btn-secondary"
                  >
                    Reset
                  </button>
                )}
              </div>
            </form>

            {error && (
              <div className="alert alert-error">
                <span className="alert-icon">⚠️</span>
                {error}
              </div>
            )}

            {result && (
              <div className="result">
                <div className="alert alert-success">
                  <span className="alert-icon">✅</span>
                  {result.message}
                </div>
                
                <div className="result-content">
                  <h3>Documentation Generated Successfully!</h3>
                  <p>Your documentation has been generated and is ready to view.</p>
                  
                  <div className="result-actions">
                    <a
                      href={`http://localhost:8000${result.doc_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                    >
                      View Documentation
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="features">
            <h3>Features</h3>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h4>AI-Powered</h4>
                <p>Uses GPT-4 to generate comprehensive and understandable documentation</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">⚡</div>
                <h4>Fast Processing</h4>
                <p>Shallow cloning and efficient parsing for quick documentation generation</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">💾</div>
                <h4>Smart Caching</h4>
                <p>Caches results to reduce API costs and improve response times</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h4>Architecture Diagrams</h4>
                <p>Automatically generates visual architecture diagrams using Mermaid</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 ConductDoc. Built with React and FastAPI.</p>
        </div>
      </footer>
    </div>
  );
}

export default App; 