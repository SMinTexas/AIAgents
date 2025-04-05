from functools import lru_cache
import time
from typing import Any, Dict, Optional, Tuple

class CacheManager:
    def __init__(self):
        """ Initialize cache dictionaries for different types of data """
        self.geocode_cache: Dict[str, Tuple[Any, float]] = {}
        self.weather_cache: Dict[str, Tuple[Any, float]] = {}
        self.places_cache: Dict[str, Tuple[Any, float]] = {}
        self.route_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_ttl = 3600  # 1 hour in seconds

    def get_cached(self, cache_type: str, key: str) -> Optional[Any]:
        """
        Retrieve cached data if it exists and has not expired

        Args:
            cache_type:  Type of cache ('geocode', 'weather', 'places', 'route')
            key: Cache key

        Returns:
            Cached data if valid, None otherwise
        """

        if cache_type in self.__dict__:
            cache = self.__dict__[cache_type]
            if key in cache:
                data, timestamp = cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return data
        return None
    
    def set_cached(self, cache_type: str, key: str, value: Any) -> None:
        """
        Store data in cache with current timestamp

        Args:
            cache_type: Type of cache ('geocode', 'weather', 'places', 'route')
            key: Cache key
            value:  Data to cache
        """

        if cache_type in self.__dict__:
            self.__dict__[cache_type][key] = (value, time.time())

    def clear_cache(self, cache_type: Optional[str] = None) -> None:
        """
        Clear cache for specified type or all caches is no type specified

        Args:
            cache_type: Optional type of cache to clear
        """

        if cache_type:
            if cache_type in self.__dict__:
                self.__dict__[cache_type].clear()
        else:
            for cache in self.__dict__.values():
                if isinstance(cache, dict):
                    cache.clear()

    def get_cache_size(self, cache_type: Optional[str] = None) -> Dict[str, int]:
        """
        Get the size of specified cache or all caches

        Args:
            cache_type: Optional type of cache to check

        Returns:
            Dictionary with cache sizes
        """

        sizes = {}
        if cache_type:
            if cache_type in self.__dict__:
                sizes[cache_type] = len(self.__dict__[cache_type])
        else:
            for name, cache in self.__dict__.items():
                if isinstance(cache, dict):
                    sizes[name] = len(cache)
        return sizes