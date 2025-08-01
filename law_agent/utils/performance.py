"""Performance monitoring and optimization utilities."""

import time
import functools
import asyncio
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
from loguru import logger


class PerformanceMonitor:
    """Monitor system performance metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.timers = {}
        self.lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a performance metric."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        with self.lock:
            self.metrics[name].append((timestamp, value))
            
            # Keep only last 1000 entries per metric
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
    
    def increment_counter(self, name: str, amount: int = 1):
        """Increment a counter metric."""
        with self.lock:
            self.counters[name] += amount
    
    def start_timer(self, name: str):
        """Start a timer."""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End a timer and record the duration."""
        if name not in self.timers:
            return 0.0
        
        duration = time.time() - self.timers[name]
        self.record_metric(f"{name}_duration", duration)
        del self.timers[name]
        return duration
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self.lock:
            summary = {
                "counters": dict(self.counters),
                "metrics": {}
            }
            
            for name, values in self.metrics.items():
                if values:
                    recent_values = [v for t, v in values if t > datetime.utcnow() - timedelta(minutes=5)]
                    if recent_values:
                        summary["metrics"][name] = {
                            "count": len(recent_values),
                            "avg": sum(recent_values) / len(recent_values),
                            "min": min(recent_values),
                            "max": max(recent_values),
                            "latest": recent_values[-1]
                        }
            
            return summary


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_performance(func_name: Optional[str] = None):
    """Decorator to measure function performance."""
    
    def decorator(func: Callable) -> Callable:
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                performance_monitor.increment_counter(f"{name}_calls")
                
                try:
                    result = await func(*args, **kwargs)
                    performance_monitor.increment_counter(f"{name}_success")
                    return result
                except Exception as e:
                    performance_monitor.increment_counter(f"{name}_errors")
                    raise
                finally:
                    duration = time.time() - start_time
                    performance_monitor.record_metric(f"{name}_duration", duration)
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                performance_monitor.increment_counter(f"{name}_calls")
                
                try:
                    result = func(*args, **kwargs)
                    performance_monitor.increment_counter(f"{name}_success")
                    return result
                except Exception as e:
                    performance_monitor.increment_counter(f"{name}_errors")
                    raise
                finally:
                    duration = time.time() - start_time
                    performance_monitor.record_metric(f"{name}_duration", duration)
            
            return sync_wrapper
    
    return decorator


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check if expired
            if time.time() - self.timestamps[key] > self.default_ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Delete value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)
    
    def cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, timestamp in self.timestamps.items():
                if current_time - timestamp > self.default_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
        
        return len(expired_keys)


# Global cache instance
cache = SimpleCache()


def cache_result(key_func: Optional[Callable] = None, ttl: int = 300):
    """Decorator to cache function results."""
    
    def decorator(func: Callable) -> Callable:
        
        def generate_key(*args, **kwargs) -> str:
            if key_func:
                return key_func(*args, **kwargs)
            else:
                # Simple key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                return ":".join(key_parts)
        
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = generate_key(*args, **kwargs)
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    performance_monitor.increment_counter("cache_hits")
                    return cached_result
                
                # Execute function and cache result
                performance_monitor.increment_counter("cache_misses")
                result = await func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                
                return result
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = generate_key(*args, **kwargs)
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    performance_monitor.increment_counter("cache_hits")
                    return cached_result
                
                # Execute function and cache result
                performance_monitor.increment_counter("cache_misses")
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                
                return result
            
            return sync_wrapper
    
    return decorator


class RateLimiter:
    """Simple rate limiter."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier."""
        current_time = time.time()
        
        with self.lock:
            # Clean old requests
            while (self.requests[identifier] and 
                   current_time - self.requests[identifier][0] > self.time_window):
                self.requests[identifier].popleft()
            
            # Check if under limit
            if len(self.requests[identifier]) < self.max_requests:
                self.requests[identifier].append(current_time)
                return True
            
            return False
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        current_time = time.time()
        
        with self.lock:
            # Clean old requests
            while (self.requests[identifier] and 
                   current_time - self.requests[identifier][0] > self.time_window):
                self.requests[identifier].popleft()
            
            return max(0, self.max_requests - len(self.requests[identifier]))


def rate_limit(max_requests: int, time_window: int):
    """Decorator for rate limiting functions."""
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use first argument as identifier (usually user_id or session_id)
            identifier = str(args[0]) if args else "default"
            
            if not limiter.is_allowed(identifier):
                raise Exception(f"Rate limit exceeded for {identifier}")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class ResourceMonitor:
    """Monitor system resources."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self.start_time
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "uptime": self.get_uptime(),
            "memory": self.get_memory_usage(),
            "cpu_percent": self.get_cpu_usage(),
            "performance_metrics": performance_monitor.get_metrics_summary(),
            "cache_stats": {
                "size": cache.size(),
                "hit_rate": self._calculate_cache_hit_rate()
            }
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        metrics = performance_monitor.get_metrics_summary()
        counters = metrics.get("counters", {})
        
        hits = counters.get("cache_hits", 0)
        misses = counters.get("cache_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return hits / total


# Global resource monitor
resource_monitor = ResourceMonitor()


def log_performance_stats():
    """Log current performance statistics."""
    stats = resource_monitor.get_system_stats()
    
    logger.info("Performance Statistics:")
    logger.info(f"  Uptime: {stats['uptime']:.1f} seconds")
    logger.info(f"  CPU Usage: {stats['cpu_percent']:.1f}%")
    
    if "error" not in stats["memory"]:
        memory = stats["memory"]
        logger.info(f"  Memory Usage: {memory['percent']:.1f}%")
        logger.info(f"  RSS: {memory['rss'] / 1024 / 1024:.1f} MB")
    
    cache_stats = stats["cache_stats"]
    logger.info(f"  Cache Size: {cache_stats['size']} entries")
    logger.info(f"  Cache Hit Rate: {cache_stats['hit_rate']:.2%}")


# Cleanup function to be called periodically
def cleanup_performance_data():
    """Clean up old performance data."""
    expired_count = cache.cleanup_expired()
    if expired_count > 0:
        logger.debug(f"Cleaned up {expired_count} expired cache entries")
    
    # Clean up old metrics (keep last 24 hours)
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    with performance_monitor.lock:
        for name, values in performance_monitor.metrics.items():
            original_count = len(values)
            performance_monitor.metrics[name] = [
                (t, v) for t, v in values if t > cutoff_time
            ]
            cleaned_count = original_count - len(performance_monitor.metrics[name])
            
            if cleaned_count > 0:
                logger.debug(f"Cleaned up {cleaned_count} old {name} metrics")
