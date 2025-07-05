import os
import sqlite3
import json
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Service for caching LLM responses and documentation results"""
    
    def __init__(self, db_path: str = "cache.db"):
        self.db_path = db_path
        self.cache_duration_days = 7  # Cache expires after 7 days
    
    async def initialize(self):
        """Initialize the cache database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key TEXT UNIQUE NOT NULL,
                        repo_url TEXT NOT NULL,
                        result_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                ''')
                
                # Create index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_cache_key ON cache (cache_key)
                ''')
                
                conn.commit()
                logger.info("Cache database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing cache database: {str(e)}")
            raise Exception(f"Cache initialization failed: {str(e)}")
    
    def get_cache_key(self, repo_url: str) -> str:
        """Generate a unique cache key for a repository URL"""
        # Use SHA256 hash of the repo URL for consistent caching
        return hashlib.sha256(repo_url.encode()).hexdigest()
    
    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if it exists and is not expired"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT result_data, expires_at 
                    FROM cache 
                    WHERE cache_key = ? AND expires_at > ?
                ''', (cache_key, datetime.now().isoformat()))
                
                result = cursor.fetchone()
                
                if result:
                    result_data, expires_at = result
                    logger.info(f"Cache hit for key: {cache_key}")
                    return json.loads(result_data)
                else:
                    logger.info(f"Cache miss for key: {cache_key}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    async def cache_result(self, cache_key: str, result_data: Dict[str, Any]):
        """Cache a documentation result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate expiration date
                expires_at = datetime.now() + timedelta(days=self.cache_duration_days)
                
                # Get repo URL from result data
                repo_url = result_data.get('documentation', {}).get('metadata', {}).get('repo_url', '')
                
                # Insert or update cache entry
                cursor.execute('''
                    INSERT OR REPLACE INTO cache (cache_key, repo_url, result_data, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (cache_key, repo_url, json.dumps(result_data), expires_at.isoformat()))
                
                conn.commit()
                logger.info(f"Result cached for key: {cache_key}")
                
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
            # Don't raise exception here to avoid breaking the main flow
    
    async def clear_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete expired entries
                cursor.execute('''
                    DELETE FROM cache WHERE expires_at < ?
                ''', (datetime.now().isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired cache entries")
                    
        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total cache entries
                cursor.execute('SELECT COUNT(*) FROM cache')
                total_entries = cursor.fetchone()[0]
                
                # Get expired entries
                cursor.execute('SELECT COUNT(*) FROM cache WHERE expires_at < ?', 
                             (datetime.now().isoformat(),))
                expired_entries = cursor.fetchone()[0]
                
                # Get cache size (approximate)
                cursor.execute('SELECT SUM(LENGTH(result_data)) FROM cache')
                cache_size = cursor.fetchone()[0] or 0
                
                return {
                    'total_entries': total_entries,
                    'active_entries': total_entries - expired_entries,
                    'expired_entries': expired_entries,
                    'cache_size_bytes': cache_size,
                    'cache_size_mb': round(cache_size / (1024 * 1024), 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                'total_entries': 0,
                'active_entries': 0,
                'expired_entries': 0,
                'cache_size_bytes': 0,
                'cache_size_mb': 0
            }
    
    async def clear_cache(self, repo_url: Optional[str] = None):
        """Clear cache entries (all or for specific repo)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if repo_url:
                    # Clear cache for specific repository
                    cursor.execute('DELETE FROM cache WHERE repo_url = ?', (repo_url,))
                    logger.info(f"Cleared cache for repository: {repo_url}")
                else:
                    # Clear all cache
                    cursor.execute('DELETE FROM cache')
                    logger.info("Cleared all cache entries")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            raise Exception(f"Cache clearing failed: {str(e)}")
    
    async def close(self):
        """Close database connection (if needed)"""
        # SQLite connections are automatically closed when exiting with statement
        pass 