"""
Optimized Search Service for Swigato Food Delivery App
Integrates advanced data structures with existing models for improved performance
"""

from typing import List, Dict, Optional, Tuple, Any
from utils.advanced_data_structures import (
    search_engine, 
    order_queue, 
    recommendation_engine,
    OptimizedSearchEngine
)
from restaurants.models import Restaurant, MenuItem
from orders.models import Order, get_orders_by_user_id
from users.models import User
from utils.logger import log
import time


class OptimizedSearchService:
    """
    Service layer that integrates advanced data structures with existing models
    Provides high-performance search, recommendations, and analytics
    """
    
    def __init__(self):
        self.search_engine = search_engine
        self.order_queue = order_queue
        self.recommendation_engine = recommendation_engine
        self.last_index_update = 0
        self.index_update_interval = 300  # 5 minutes
        
    def initialize_search_indexes(self):
        """Initialize all search indexes with current data"""
        log("Initializing optimized search indexes...")
        
        try:
            # Load all data
            restaurants = Restaurant.get_all()
            menu_items = []
            
            # Collect all menu items
            for restaurant in restaurants:
                menu_items.extend(restaurant.menu)
            
            # Build indexes
            self.search_engine.build_indexes(restaurants, menu_items)
            self.last_index_update = time.time()
            
            log(f"Search indexes initialized with {len(restaurants)} restaurants and {len(menu_items)} menu items")
            
        except Exception as e:
            log(f"Error initializing search indexes: {e}")
    
    def search_restaurants_optimized(self, query: str, filters: Optional[Dict] = None) -> List[Restaurant]:
        """
        Optimized restaurant search with O(m) complexity
        """
        # Check if indexes need updating
        if time.time() - self.last_index_update > self.index_update_interval:
            self.initialize_search_indexes()
        
        # Use optimized search engine
        results = self.search_engine.search_restaurants(query, filters)
        
        # Log search analytics
        log(f"Search query '{query}' returned {len(results)} results")
        
        return results
    
    def search_menu_items_optimized(self, query: str, restaurant_id: Optional[int] = None) -> List[MenuItem]:
        """
        Optimized menu item search with O(m) complexity
        """
        # Check if indexes need updating
        if time.time() - self.last_index_update > self.index_update_interval:
            self.initialize_search_indexes()
        
        # Use optimized search engine
        results = self.search_engine.search_menu_items(query, restaurant_id)
        
        return results
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions with O(m) complexity
        """
        return self.search_engine.get_suggestions(query, limit)
    
    def get_popular_searches(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get popular search queries for analytics
        """
        return self.search_engine.get_popular_searches(limit)
    
    def add_order_to_queue(self, order: Order, priority: Optional[float] = None):
        """
        Add order to optimized processing queue
        """
        self.order_queue.add_order(order, priority)
        
        # Update recommendation engine with order data
        if hasattr(order, 'items'):
            for item in order.items:
                self.recommendation_engine.update_user_preference(
                    order.user_id, 
                    item.item_id, 
                    5.0  # Implicit rating for purchased items
                )
    
    def get_recommendations_for_user(self, user_id: int, limit: int = 10) -> List[MenuItem]:
        """
        Get personalized recommendations for user
        """
        # Get recommendation scores
        recommendation_scores = self.recommendation_engine.get_recommendations(user_id, limit)
        
        # Convert to MenuItem objects
        recommended_items = []
        for item_id, score in recommendation_scores:
            if item_id in self.search_engine.menu_by_id:
                recommended_items.append(self.search_engine.menu_by_id[item_id])
        
        return recommended_items
    
    def get_similar_restaurants(self, restaurant_id: int, limit: int = 5) -> List[Restaurant]:
        """
        Get restaurants similar to the given restaurant
        """
        target_restaurant = self.search_engine.restaurant_by_id.get(restaurant_id)
        if not target_restaurant:
            return []
        
        # Find restaurants with similar cuisine
        similar_restaurants = []
        if target_restaurant.cuisine_type:
            cuisine_matches = self.search_engine.cuisine_index.get(
                target_restaurant.cuisine_type.lower(), []
            )
            similar_restaurants = [r for r in cuisine_matches if r.restaurant_id != restaurant_id]
        
        # Sort by rating and return top matches
        similar_restaurants.sort(key=lambda x: x.rating, reverse=True)
        return similar_restaurants[:limit]
    
    def get_restaurants_by_price_range(self, price_range: str) -> List[Restaurant]:
        """
        Get restaurants filtered by price range
        """
        if price_range not in self.search_engine.price_index:
            return []
        
        # Get menu items in price range
        menu_items = self.search_engine.price_index[price_range]
        
        # Extract unique restaurants
        restaurant_ids = {item.restaurant_id for item in menu_items}
        restaurants = [
            self.search_engine.restaurant_by_id[rid] 
            for rid in restaurant_ids 
            if rid in self.search_engine.restaurant_by_id
        ]
        
        return restaurants
    
    def get_queue_analytics(self) -> Dict:
        """
        Get order queue analytics
        """
        return self.order_queue.get_queue_status()
    
    def get_search_analytics(self) -> Dict:
        """
        Get search analytics data
        """
        return {
            'popular_searches': self.get_popular_searches(),
            'total_searches': sum(self.search_engine.search_analytics.values()),
            'unique_queries': len(self.search_engine.search_analytics),
            'cache_stats': {
                'cache_size': len(self.search_engine.cache.cache),
                'cache_capacity': self.search_engine.cache.capacity
            }
        }
    
    def update_user_rating(self, user_id: int, item_id: int, rating: float):
        """
        Update user rating for recommendation engine
        """
        self.recommendation_engine.update_user_preference(user_id, item_id, rating)
    
    def preload_user_data(self, user_id: int):
        """
        Preload user data for better performance
        """
        try:
            # Preload user orders
            orders = get_orders_by_user_id(user_id)
            
            # Update recommendation engine with historical data
            for order in orders:
                if hasattr(order, 'items'):
                    for item in order.items:
                        # Use order frequency as implicit rating
                        self.recommendation_engine.update_user_preference(
                            user_id, 
                            item.item_id, 
                            4.0  # Base rating for ordered items
                        )
            
            # Preload recommendations
            self.get_recommendations_for_user(user_id)
            
        except Exception as e:
            log(f"Error preloading user data for user {user_id}: {e}")


class OptimizedMainAppScreen:
    """
    Optimized methods for MainAppScreen to reduce complexity
    """
    
    @staticmethod
    def optimized_search(main_app_instance, query: str):
        """
        Optimized search method for MainAppScreen
        Reduces complexity from O(n*m) to O(m)
        """
        if not hasattr(main_app_instance, 'search_service'):
            main_app_instance.search_service = OptimizedSearchService()
            main_app_instance.search_service.initialize_search_indexes()
        
        search_service = main_app_instance.search_service
        
        if not query.strip():
            # Return all restaurants for empty query
            return Restaurant.get_all()
        
        # Use optimized search
        results = search_service.search_restaurants_optimized(query)
        
        # Also search menu items and get their restaurants
        menu_matches = search_service.search_menu_items_optimized(query)
        restaurant_ids_from_menu = {item.restaurant_id for item in menu_matches}
        
        # Add restaurants from menu matches
        menu_restaurants = [
            search_service.search_engine.restaurant_by_id[rid]
            for rid in restaurant_ids_from_menu
            if rid in search_service.search_engine.restaurant_by_id
        ]
        
        # Combine and deduplicate
        all_results = results + menu_restaurants
        unique_results = {r.restaurant_id: r for r in all_results}.values()
        
        return list(unique_results)
    
    @staticmethod
    def optimized_cart_operations(main_app_instance):
        """
        Optimized cart operations with O(1) complexity
        """
        cart = main_app_instance.app_ref.cart
        
        # Use hash map for O(1) item lookup and updates
        if not hasattr(cart, 'item_lookup'):
            cart.item_lookup = {}
            for item_id, cart_item in cart.items.items():
                cart.item_lookup[item_id] = cart_item
        
        # Optimized total calculation with memoization
        if not hasattr(cart, '_cached_total'):
            cart._cached_total = None
            cart._total_dirty = True
        
        if cart._total_dirty:
            cart._cached_total = sum(item.item_total for item in cart.items.values())
            cart._total_dirty = False
        
        return cart._cached_total
    
    @staticmethod
    def optimized_order_loading(main_app_instance):
        """
        Optimized order loading with pagination and caching
        """
        user_id = main_app_instance.user.user_id
        
        # Initialize search service if not exists
        if not hasattr(main_app_instance, 'search_service'):
            main_app_instance.search_service = OptimizedSearchService()
        
        # Preload user data for better performance
        main_app_instance.search_service.preload_user_data(user_id)
        
        # Get orders (this would be optimized with pagination in production)
        orders = get_orders_by_user_id(user_id)
        
        # Sort orders by date (using Python's optimized Timsort)
        orders.sort(key=lambda x: x.order_date, reverse=True)
        
        return orders
    
    @staticmethod
    def get_personalized_recommendations(main_app_instance, limit: int = 10) -> List[MenuItem]:
        """
        Get personalized recommendations for the user
        """
        if not hasattr(main_app_instance, 'search_service'):
            main_app_instance.search_service = OptimizedSearchService()
            main_app_instance.search_service.initialize_search_indexes()
        
        user_id = main_app_instance.user.user_id
        return main_app_instance.search_service.get_recommendations_for_user(user_id, limit)
    
    @staticmethod
    def get_search_suggestions(main_app_instance, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions with O(m) complexity
        """
        if not hasattr(main_app_instance, 'search_service'):
            main_app_instance.search_service = OptimizedSearchService()
            main_app_instance.search_service.initialize_search_indexes()
        
        return main_app_instance.search_service.get_search_suggestions(query, limit)


# Global search service instance
optimized_search_service = OptimizedSearchService()
