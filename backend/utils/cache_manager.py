import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, ttl: int = 3600):
        """
        Initialize the cache manager with a default TTL of 1 hour
        
        Args:
            ttl (int): Time to live in seconds for cached items
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
        logger.info("CacheManager initialized with TTL: %d seconds", ttl)

    def get_cached(self, category: str, key: str) -> Optional[Any]:
        """
        Get a cached value if it exists and hasn't expired
        
        Args:
            category (str): The category of the cached item (e.g., 'geocode', 'places')
            key (str): The unique key for the cached item
            
        Returns:
            Optional[Any]: The cached value if it exists and hasn't expired, None otherwise
        """
        logger.debug(f"Getting cached value for category: {category}, key: {key}")
        logger.debug(f"Current cache state: {self.cache}")
        
        if category not in self.cache:
            logger.debug(f"Category {category} not found in cache")
            return None
            
        if key not in self.cache[category]:
            logger.debug(f"Key {key} not found in category {category}")
            return None
            
        cache_entry = self.cache[category][key]
        if time.time() - cache_entry['timestamp'] > self.ttl:
            logger.debug("Cache entry expired for %s/%s", category, key)
            del self.cache[category][key]
            return None
            
        logger.debug("Cache hit for %s/%s", category, key)
        return cache_entry['value']

    def set_cached(self, category: str, key: str, value: Any) -> None:
        """
        Set a value in the cache with the current timestamp
        
        Args:
            category (str): The category of the cached item
            key (str): The unique key for the cached item
            value (Any): The value to cache
        """
        if category not in self.cache:
            self.cache[category] = {}
            
        self.cache[category][key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug("Cached value for %s/%s", category, key)

    def get_cache_size(self) -> Dict[str, int]:
        """
        Get the current size of each cache category
        
        Returns:
            Dict[str, int]: Dictionary mapping categories to their cache sizes
        """
        return {category: len(entries) for category, entries in self.cache.items()}

    def clear_cache(self, category: Optional[str] = None) -> None:
        """
        Clear the cache for a specific category or all categories
        
        Args:
            category (Optional[str]): The category to clear. If None, clears all categories.
        """
        if category is None:
            self.cache.clear()
            logger.info("Cleared all cache categories")
        elif category in self.cache:
            del self.cache[category]
            logger.info("Cleared cache category: %s", category) 