# 📚 ConductDoc

**AI-Powered Python Documentation Generator**

ConductDoc automatically generates comprehensive, user-friendly documentation for Python GitHub repositories using GPT-4. Simply provide a repository URL and get beautiful, navigable documentation in minutes.


## 🌟 Features

- **🤖 AI-Powered Documentation**: Uses GPT-4 to generate comprehensive explanations
- **📊 Architecture Diagrams**: Automatic Mermaid diagrams showing code structure
- **💾 Smart Caching**: Reduces API costs with intelligent caching system
- **🎨 Beautiful UI**: Modern, responsive interface with mobile support
- **⚡ Fast Processing**: Shallow cloning and efficient parsing
- **🔍 Symbol-Level Docs**: Detailed documentation for classes, functions, and constants
- **📱 Responsive Design**: Works seamlessly across all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd conductdoc
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start the frontend development server**
   ```bash
   cd frontend
   npm start
   ```

3. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎯 Usage

1. **Enter a Repository URL**: Input a GitHub repository URL (e.g., `https://github.com/ahmernajar/digit-recogniser-cnn`)
2. **Generate Documentation**: Click "Generate Documentation" and wait for processing
3. **View Results**: Browse the generated documentation with navigation and search

### Example URLs to Try

- `https://github.com/ahmernajar/digit-recogniser-cnn`

## 📁 Project Structure

```
conductdoc/
├── backend/                 # FastAPI backend
│   ├── services/           # Core business logic
│   │   ├── repo_processor.py    # Repository cloning and parsing
│   │   ├── doc_generator.py     # GPT-4 integration and HTML generation
│   │   └── cache_manager.py     # Caching system
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── App.js        # Main application component
│   │   ├── styles/       # CSS styling
│   │   └── index.js      # React DOM rendering
│   ├── public/           # Static assets
│   └── package.json      # Node.js dependencies
├── sample_output/         # Sample generated documentation
│   ├── README.md         # Sample documentation overview
│   └── manim_docs.html   # Sample HTML documentation
└── NOTES.md              # Design decisions and implementation details
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=False
CACHE_DB_PATH=cache.db
CACHE_DURATION_DAYS=7
```

### API Configuration

The backend supports several configuration options:

- **Output Directory**: Where generated documentation is saved
- **Cache Duration**: How long to keep cached results
- **API Rate Limits**: Control OpenAI API usage
- **Quality Settings**: Balance between speed and documentation quality

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services  │
│   (React)       │────│   (FastAPI)     │────│    (GPT-4)      │
│                 │    │                 │    │                 │
│ - URL Input     │    │ - API Routes    │    │ - Doc Generation│
│ - Progress UI   │    │ - Services      │    │ - Summarization │
│ - Results View  │    │ - Caching       │    │ - Architecture  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

1. **RepoProcessor**: Handles repository cloning and Python code analysis
2. **DocGenerator**: Orchestrates GPT-4 integration and HTML generation
3. **CacheManager**: Implements intelligent caching to reduce API costs
4. **React Frontend**: Provides modern, responsive user interface

## 📊 Performance

### Typical Performance Metrics

- **Processing Time**: 2-5 minutes for most repositories
- **Cache Hit Rate**: 95% for repeated requests
- **API Efficiency**: ~26 API calls for large repositories
- **Generated Size**: 1-3MB HTML files

### Optimization Features

- **Shallow Cloning**: Faster repository downloads
- **Smart Caching**: Reduced API costs and improved response times
- **Efficient Parsing**: AST-based code analysis
- **Compressed Output**: Optimized HTML generation

## 🎨 Sample Documentation

Check out the `sample_output/` directory for examples of generated documentation:

- **manim_docs.html**: Complete documentation for the Manim animation library
- **README.md**: Overview of the sample documentation features

The generated documentation includes:
- **Overview**: High-level project summary and getting started guide
- **Architecture**: Visual diagrams showing code structure
- **Module Documentation**: Detailed explanations of each Python module
- **Symbol Documentation**: Comprehensive docs for classes, functions, and constants

## 🚢 Deployment

### Docker Deployment

```dockerfile
# Backend
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend
FROM node:16-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
CMD ["npx", "serve", "-s", "build"]
```

### Cloud Deployment

**Recommended Platforms:**
- **Backend**: Railway, Heroku, Google Cloud Run
- **Frontend**: Vercel, Netlify, AWS S3 + CloudFront

## 🔒 Security

- **API Key Management**: Securely store OpenAI API keys
- **Input Validation**: Sanitize repository URLs
- **Rate Limiting**: Prevent abuse and manage costs
- **Output Sanitization**: Clean generated content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use Prettier for JavaScript formatting
- Add comprehensive docstrings
- Write meaningful commit messages
- Update NOTES.md for significant changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- **Large Repositories**: May timeout on very large codebases
- **API Rate Limits**: OpenAI API has request limits
- **Memory Usage**: Large repositories consume significant memory

See [NOTES.md](NOTES.md) for detailed information about limitations and solutions.

## 🛣️ Roadmap

### Short-term
- Multi-language support (JavaScript, TypeScript, Java)
- Batch processing for multiple repositories
- Export options (PDF, Markdown, JSON)

### Medium-term
- Interactive documentation with search
- Version comparison across commits
- CI/CD integration via webhooks

### Long-term
- Fine-tuned AI models for better documentation
- Enterprise features and team management
- Analytics dashboard and usage metrics

---
