from .cache_manager import CacheManager

# Create a singleton instance of CacheManager
cache_manager = CacheManager()

__all__ = ['cache_manager']