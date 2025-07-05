from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
from typing import Optional

from services.repo_processor import RepoProcessor
from services.doc_generator import DocGenerator
from services.cache_manager import CacheManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ConductDoc API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated documentation
os.makedirs("sample_output", exist_ok=True)
app.mount("/docs", StaticFiles(directory="sample_output"), name="docs")

class RepoRequest(BaseModel):
    repo_url: str

class DocResponse(BaseModel):
    status: str
    doc_url: Optional[str] = None
    message: str
    task_id: Optional[str] = None

# Global services
repo_processor = RepoProcessor()
doc_generator = DocGenerator()
cache_manager = CacheManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await cache_manager.initialize()
    logger.info("ConductDoc API started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ConductDoc API is running"}

@app.post("/generate-docs", response_model=DocResponse)
async def generate_docs(request: RepoRequest):
    """Generate documentation for a GitHub repository"""
    try:
        # Validate repository URL
        if not request.repo_url.startswith(("https://github.com/", "http://github.com/")):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
        
        logger.info(f"Processing repository: {request.repo_url}")
        
        # Check if documentation already exists in cache
        cache_key = cache_manager.get_cache_key(request.repo_url)
        cached_result = await cache_manager.get_cached_result(cache_key)
        
        if cached_result:
            logger.info(f"Returning cached result for {request.repo_url}")
            return DocResponse(
                status="success",
                doc_url=cached_result["doc_url"],
                message="Documentation retrieved from cache"
            )
        
        # Process repository
        repo_data = await repo_processor.process_repository(request.repo_url)
        
        # Generate documentation
        doc_result = await doc_generator.generate_documentation(repo_data)
        
        # Cache the result
        await cache_manager.cache_result(cache_key, doc_result)
        
        logger.info(f"Successfully generated documentation for {request.repo_url}")
        
        return DocResponse(
            status="success",
            doc_url=doc_result["doc_url"],
            message="Documentation generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "repo_processor": "active",
            "doc_generator": "active",
            "cache_manager": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 