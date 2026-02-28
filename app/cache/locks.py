import time
import random
from typing import Optional
from app.cache.redis_client import get_redis


class InventoryLock:
    """Distributed lock for inventory using Redis"""
    
    def __init__(self, product_id: int, timeout: int = 10):
        """
        Initialize lock for a product.
        
        Args:
            product_id: Product to lock
            timeout: Lock expiration in seconds (prevents deadlock)
        """
        self.product_id = product_id
        self.lock_key = f"lock:product:{product_id}"
        self.timeout = timeout
        self.redis = get_redis()
    
    def acquire(self, retry_times: int = 3, retry_delay: float = 0.1) -> bool:
        """
        Try to acquire the lock with exponential backoff.
        
        Args:
            retry_times: Number of retry attempts
            retry_delay: Initial delay between retries (seconds)
        
        Returns:
            True if lock acquired, False otherwise
        """
        for attempt in range(retry_times):
            # Try to set the lock (SET NX - set if not exists)
            acquired = self.redis.set(
                self.lock_key,
                "locked",
                nx=True,  # Only set if key doesn't exist
                ex=self.timeout  # Expire after timeout seconds
            )
            
            if acquired:
                return True
            
            # Lock not acquired, wait before retry
            if attempt < retry_times - 1:
                # Exponential backoff with jitter
                wait_time = retry_delay * (2 ** attempt) + random.uniform(0, 0.1)
                time.sleep(wait_time)
        
        return False
    
    def release(self) -> bool:
        """
        Release the lock.
        
        Returns:
            True if lock was released, False if lock didn't exist
        """
        deleted = self.redis.delete(self.lock_key)
        return deleted > 0
    
    def is_locked(self) -> bool:
        """Check if lock is currently held"""
        return self.redis.exists(self.lock_key) > 0
    
    def __enter__(self):
        """Context manager entry - acquire lock"""
        if not self.acquire():
            raise Exception(f"Failed to acquire lock for product {self.product_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release lock"""
        self.release()