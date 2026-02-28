from app.cache.redis_client import get_redis

try:
    redis = get_redis()
    response = redis.ping()
    print(f"✓ Redis connected! Response: {response}")
    
    # Test set and get
    redis.set("test_key", "Hello Redis!")
    value = redis.get("test_key")
    print(f"✓ Set/Get works! Value: {value}")
    
    # Test the lock
    from app.cache.locks import InventoryLock
    lock = InventoryLock(product_id=999)
    if lock.acquire():
        print(f"✓ Lock acquired successfully!")
        lock.release()
        print(f"✓ Lock released successfully!")
    else:
        print("✗ Failed to acquire lock")
    
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
    print("\nMake sure Redis container is running:")
    print("  docker ps")