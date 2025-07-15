"""
Integration layer for optimized search functionality
This file provides drop-in replacements for existing methods with improved performance
"""

import time
from utils.optimized_search_service import OptimizedSearchService, OptimizedMainAppScreen
from utils.optimized_models import OptimizedCart, restaurant_cache, menu_cache, order_manager
from restaurants.models import Restaurant, MenuItem
from utils.logger import log


class OptimizedMainAppIntegration:
    """
    Integration layer that provides optimized methods for MainAppScreen
    """
    
    def __init__(self, main_app_instance):
        self.main_app = main_app_instance
        self.search_service = OptimizedSearchService()
        self.search_service.initialize_search_indexes()
        
    def optimized_search(self, query: str):
        """
        Optimized search method that replaces the original on_search_change
        Time Complexity: O(m) where m is query length (vs original O(n*m))
        """
        if not query.strip():
            return self.main_app.load_restaurants()
        
        # Use optimized search
        results = OptimizedMainAppScreen.optimized_search(self.main_app, query)
        
        # Display results using existing UI method
        self.main_app.display_restaurants(results)
        
        log(f"Optimized search for '{query}' completed with {len(results)} results")
    
    def optimized_cart_operations(self):
        """
        Optimized cart operations with O(1) complexity
        """
        return OptimizedMainAppScreen.optimized_cart_operations(self.main_app)
    
    def optimized_order_loading(self):
        """
        Optimized order loading with caching and preloading
        """
        return OptimizedMainAppScreen.optimized_order_loading(self.main_app)
    
    def get_recommendations(self, limit: int = 10):
        """
        Get personalized recommendations for the current user
        """
        return OptimizedMainAppScreen.get_personalized_recommendations(self.main_app, limit)
    
    def get_search_suggestions(self, query: str, limit: int = 5):
        """
        Get search suggestions for autocomplete
        """
        return OptimizedMainAppScreen.get_search_suggestions(self.main_app, query, limit)
    
    def get_similar_restaurants(self, restaurant_id: int, limit: int = 5):
        """
        Get restaurants similar to the given one
        """
        return self.search_service.get_similar_restaurants(restaurant_id, limit)
    
    def update_user_preferences(self, item_id: int, rating: float):
        """
        Update user preferences for better recommendations
        """
        user_id = self.main_app.user.user_id
        self.search_service.update_user_rating(user_id, item_id, rating)
    
    def get_analytics(self):
        """
        Get search and queue analytics
        """
        return {
            'search_analytics': self.search_service.get_search_analytics(),
            'queue_analytics': self.search_service.get_queue_analytics()
        }


def integrate_optimized_search(main_app_instance):
    """
    Integration function to add optimized search to existing MainAppScreen instance
    """
    # Create optimization integration
    optimization = OptimizedMainAppIntegration(main_app_instance)
    
    # Replace the original search method
    original_search = main_app_instance.on_search_change
    
    def optimized_search_wrapper(event=None):
        query = main_app_instance.search_entry.get()
        optimization.optimized_search(query)
    
    # Replace the search method
    main_app_instance.on_search_change = optimized_search_wrapper
    main_app_instance.optimized_search = optimization.optimized_search
    main_app_instance.get_recommendations = optimization.get_recommendations
    main_app_instance.get_search_suggestions = optimization.get_search_suggestions
    main_app_instance.get_similar_restaurants = optimization.get_similar_restaurants
    main_app_instance.update_user_preferences = optimization.update_user_preferences
    main_app_instance.get_analytics = optimization.get_analytics
    
    # Store optimization instance
    main_app_instance.optimization = optimization
    
    log("Optimized search integration completed")
    
    return optimization


def create_optimized_cart(user_id=None):
    """
    Factory function to create optimized cart
    """
    return OptimizedCart(user_id)


def preload_data_structures():
    """
    Preload all data structures with existing data for better performance
    """
    log("Preloading optimized data structures...")
    
    try:
        # Load restaurants
        restaurants = Restaurant.get_all()
        for restaurant in restaurants:
            restaurant_cache.add_restaurant(restaurant)
            
            # Load menu items
            menu_items = restaurant.menu
            for item in menu_items:
                menu_cache.add_menu_item(item)
        
        log(f"Preloaded {len(restaurants)} restaurants and menu items")
        
        # Initialize search service
        search_service = OptimizedSearchService()
        search_service.initialize_search_indexes()
        
        log("Data structures preloaded successfully")
        
    except Exception as e:
        log(f"Error preloading data structures: {e}")


# Performance measurement decorator
def measure_performance(func):
    """
    Decorator to measure performance improvements
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        log(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper


# Example usage for measuring performance improvements
@measure_performance
def benchmark_search_performance():
    """
    Benchmark search performance comparison
    """
    from restaurants.models import Restaurant
    
    # Initialize data
    restaurants = Restaurant.get_all()
    
    # Test queries
    test_queries = ["biryani", "pizza", "indian", "coffee", "chicken"]
    
    # Benchmark original search (simulation)
    original_times = []
    for query in test_queries:
        start = time.time()
        # Simulate O(n*m) search
        results = [r for r in restaurants if query.lower() in r.name.lower() or 
                  (r.cuisine_type and query.lower() in r.cuisine_type.lower())]
        end = time.time()
        original_times.append(end - start)
    
    # Benchmark optimized search
    search_service = OptimizedSearchService()
    search_service.initialize_search_indexes()
    
    optimized_times = []
    for query in test_queries:
        start = time.time()
        results = search_service.search_restaurants_optimized(query)
        end = time.time()
        optimized_times.append(end - start)
    
    # Calculate improvements
    avg_original = sum(original_times) / len(original_times)
    avg_optimized = sum(optimized_times) / len(optimized_times)
    improvement = (avg_original - avg_optimized) / avg_original * 100
    
    log(f"Search performance improvement: {improvement:.2f}%")
    log(f"Average original time: {avg_original:.4f}s")
    log(f"Average optimized time: {avg_optimized:.4f}s")
    
    return improvement


if __name__ == "__main__":
    # Run performance benchmark
    benchmark_search_performance()
