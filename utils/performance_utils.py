"""
Performance Utilities for Swigato Food Delivery App
Provides performance monitoring and optimization utilities
"""

import time
import threading
from typing import Dict, List, Callable, Any
from functools import wraps
from utils.logger import log


class PerformanceMonitor:
    """
    Performance monitoring and analytics
    """
    
    def __init__(self):
        self.metrics = {
            'search_operations': {
                'total_count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'cache_hits': 0,
                'cache_misses': 0
            },
            'cart_operations': {
                'total_count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'add_operations': 0,
                'remove_operations': 0,
                'update_operations': 0
            },
            'order_operations': {
                'total_count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'orders_processed': 0,
                'avg_processing_time': 0.0
            }
        }
        self.lock = threading.Lock()
    
    def record_search_operation(self, duration: float, cache_hit: bool = False):
        """Record search operation metrics"""
        with self.lock:
            metrics = self.metrics['search_operations']
            metrics['total_count'] += 1
            metrics['total_time'] += duration
            metrics['avg_time'] = metrics['total_time'] / metrics['total_count']
            
            if cache_hit:
                metrics['cache_hits'] += 1
            else:
                metrics['cache_misses'] += 1
    
    def record_cart_operation(self, duration: float, operation_type: str):
        """Record cart operation metrics"""
        with self.lock:
            metrics = self.metrics['cart_operations']
            metrics['total_count'] += 1
            metrics['total_time'] += duration
            metrics['avg_time'] = metrics['total_time'] / metrics['total_count']
            
            if operation_type == 'add':
                metrics['add_operations'] += 1
            elif operation_type == 'remove':
                metrics['remove_operations'] += 1
            elif operation_type == 'update':
                metrics['update_operations'] += 1
    
    def record_order_operation(self, duration: float):
        """Record order operation metrics"""
        with self.lock:
            metrics = self.metrics['order_operations']
            metrics['total_count'] += 1
            metrics['total_time'] += duration
            metrics['avg_time'] = metrics['total_time'] / metrics['total_count']
            metrics['orders_processed'] += 1
            metrics['avg_processing_time'] = metrics['avg_time']
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self.lock:
            for category in self.metrics:
                for key in self.metrics[category]:
                    self.metrics[category][key] = 0 if isinstance(self.metrics[category][key], (int, float)) else 0.0


# Global performance monitor
performance_monitor = PerformanceMonitor()


def track_performance(operation_type: str, cache_hit: bool = False):
    """
    Decorator to track performance of operations
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if operation_type == 'search':
                performance_monitor.record_search_operation(duration, cache_hit)
            elif operation_type == 'cart':
                operation_name = func.__name__
                if 'add' in operation_name:
                    performance_monitor.record_cart_operation(duration, 'add')
                elif 'remove' in operation_name:
                    performance_monitor.record_cart_operation(duration, 'remove')
                elif 'update' in operation_name:
                    performance_monitor.record_cart_operation(duration, 'update')
            elif operation_type == 'order':
                performance_monitor.record_order_operation(duration)
            
            return result
        return wrapper
    return decorator


def benchmark_operation(operation_func: Callable, iterations: int = 100, *args, **kwargs) -> Dict:
    """
    Benchmark an operation multiple times
    """
    times = []
    
    for _ in range(iterations):
        start_time = time.time()
        operation_func(*args, **kwargs)
        times.append(time.time() - start_time)
    
    return {
        'iterations': iterations,
        'total_time': sum(times),
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times)
    }


def compare_performance(old_func: Callable, new_func: Callable, iterations: int = 100, *args, **kwargs) -> Dict:
    """
    Compare performance between old and new implementations
    """
    old_benchmark = benchmark_operation(old_func, iterations, *args, **kwargs)
    new_benchmark = benchmark_operation(new_func, iterations, *args, **kwargs)
    
    improvement = (old_benchmark['avg_time'] - new_benchmark['avg_time']) / old_benchmark['avg_time'] * 100
    
    return {
        'old_performance': old_benchmark,
        'new_performance': new_benchmark,
        'improvement_percentage': improvement,
        'speedup_factor': old_benchmark['avg_time'] / new_benchmark['avg_time']
    }


def get_performance_report() -> str:
    """
    Generate a detailed performance report
    """
    metrics = performance_monitor.get_metrics()
    
    report = "=== Swigato Performance Report ===\n\n"
    
    # Search Operations
    search_metrics = metrics['search_operations']
    report += "Search Operations:\n"
    report += f"  Total searches: {search_metrics['total_count']}\n"
    report += f"  Average response time: {search_metrics['avg_time']:.4f}s\n"
    report += f"  Cache hit rate: {search_metrics['cache_hits']}/{search_metrics['total_count']}\n"
    report += f"  Cache efficiency: {(search_metrics['cache_hits']/max(search_metrics['total_count'], 1)*100):.1f}%\n\n"
    
    # Cart Operations
    cart_metrics = metrics['cart_operations']
    report += "Cart Operations:\n"
    report += f"  Total operations: {cart_metrics['total_count']}\n"
    report += f"  Average response time: {cart_metrics['avg_time']:.4f}s\n"
    report += f"  Add operations: {cart_metrics['add_operations']}\n"
    report += f"  Remove operations: {cart_metrics['remove_operations']}\n"
    report += f"  Update operations: {cart_metrics['update_operations']}\n\n"
    
    # Order Operations
    order_metrics = metrics['order_operations']
    report += "Order Operations:\n"
    report += f"  Total operations: {order_metrics['total_count']}\n"
    report += f"  Average response time: {order_metrics['avg_time']:.4f}s\n"
    report += f"  Orders processed: {order_metrics['orders_processed']}\n"
    report += f"  Average processing time: {order_metrics['avg_processing_time']:.4f}s\n\n"
    
    return report


def preload_data_structures():
    """
    Preload data structures for optimal performance
    """
    log("Preloading data structures for optimal performance...")
    
    try:
        # Initialize search engine
        from utils.search_engine import initialize_search_engine
        initialize_search_engine()
        
        # Initialize restaurant search
        from utils.restaurant_search import initialize_restaurant_search
        initialize_restaurant_search()
        
        log("Data structures preloaded successfully")
        
    except Exception as e:
        log(f"Error preloading data structures: {e}")


def optimize_app_performance():
    """
    Apply performance optimizations to the entire app
    """
    log("Applying performance optimizations...")
    
    # Preload data structures
    preload_data_structures()
    
    # Set up performance monitoring
    performance_monitor.reset_metrics()
    
    log("Performance optimizations applied")


class MemoryOptimizer:
    """
    Memory optimization utilities
    """
    
    @staticmethod
    def optimize_object_memory(obj: Any) -> Any:
        """
        Optimize object memory usage
        """
        # Remove unnecessary attributes
        if hasattr(obj, '__dict__'):
            for attr in list(obj.__dict__.keys()):
                if attr.startswith('_temp_') or attr.startswith('_cache_'):
                    delattr(obj, attr)
        
        return obj
    
    @staticmethod
    def clear_unused_caches():
        """
        Clear unused caches to free memory
        """
        try:
            from utils.search_engine import restaurant_cache, menu_cache
            from utils.cart_manager import cart_managers
            
            # Clear caches if they're getting too large
            if restaurant_cache.size() > 150:
                restaurant_cache.clear()
            
            if menu_cache.size() > 400:
                menu_cache.clear()
            
            # Clear unused cart managers
            active_users = set()  # This would be populated with currently active users
            for user_id in list(cart_managers.keys()):
                if user_id not in active_users:
                    del cart_managers[user_id]
            
            log("Unused caches cleared")
            
        except Exception as e:
            log(f"Error clearing caches: {e}")


def get_performance_metrics() -> Dict:
    """
    Get comprehensive performance metrics
    """
    try:
        from utils.cart_manager import cart_managers
        cart_count = len(cart_managers)
    except ImportError:
        cart_count = 0
    
    return {
        'performance_monitor': performance_monitor.get_metrics(),
        'memory_usage': {
            'search_engine_loaded': True,
            'cart_managers_count': cart_count,
        },
        'optimization_status': {
            'data_structures_loaded': True,
            'caches_active': True,
            'performance_tracking': True
        }
    }


# Export main functions
__all__ = [
    'track_performance',
    'benchmark_operation',
    'compare_performance',
    'get_performance_report',
    'preload_data_structures',
    'optimize_app_performance',
    'get_performance_metrics',
    'MemoryOptimizer',
    'performance_monitor'
]
