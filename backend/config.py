import os
from typing import Optional

# Environment Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
HOST: str = os.getenv('HOST', '0.0.0.0')
PORT: int = int(os.getenv('PORT', '8000'))
DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

# Cache Configuration
CACHE_DB_PATH: str = os.getenv('CACHE_DB_PATH', 'cache.db')
CACHE_DURATION_DAYS: int = int(os.getenv('CACHE_DURATION_DAYS', '7'))

# Output Configuration
OUTPUT_DIR: str = os.getenv('OUTPUT_DIR', 'sample_output')

# Validation
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable is not set!")
    print("Please set your OpenAI API key in the environment or .env file") 