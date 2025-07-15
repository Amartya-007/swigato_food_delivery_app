"""
Restaurant Search Service for Swigato Food Delivery App
Integrates search engine with restaurant and menu data for fast lookups
"""

from typing import List, Dict, Optional, Tuple, Any, Union
from utils.search_engine import (
    restaurant_search_trie, 
    restaurant_cache,
    menu_cache,
    order_queue, 
    restaurant_index,
    search_restaurants_fast,
    search_menu_items_fast,
    get_search_suggestions_fast,
    get_performance_analytics
)
from restaurants.models import Restaurant
from orders.models import Order, get_orders_by_user_id
from users.models import User
from utils.logger import log
from utils.database import get_db_connection
import time


class RestaurantSearchService:
    """
    Service layer that integrates search engine with restaurant data
    Provides high-performance search, filtering, and recommendations
    """
    
    def __init__(self):
        self.last_index_update = 0
        self.index_update_interval = 300  # 5 minutes
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0
        }
        
    def initialize_search_indexes(self):
        """Initialize all search indexes with current data"""
        log("Initializing restaurant search indexes...")
        
        try:
            # Load all restaurants
            restaurants = Restaurant.get_all()
            
            # Add restaurants to search trie and indexes
            for restaurant in restaurants:
                restaurant_search_trie.insert_restaurant(restaurant)
                restaurant_index.add_restaurant(restaurant)
                
                # Cache frequently accessed restaurant data
                cache_key = f"restaurant_{restaurant.restaurant_id}"
                restaurant_cache.put(cache_key, restaurant)
                
                # Add menu items to search
                if hasattr(restaurant, 'menu') and restaurant.menu:
                    for menu_item in restaurant.menu:
                        restaurant_search_trie.insert_menu_item(menu_item)
                        menu_cache_key = f"menu_{menu_item.item_id}"
                        menu_cache.put(menu_cache_key, menu_item)
            
            self.last_index_update = time.time()
            log(f"Search indexes initialized with {len(restaurants)} restaurants")
            
        except Exception as e:
            log(f"Error initializing search indexes: {e}")

    def search_restaurants(self, query: str, filters: Optional[Dict] = None, limit: int = 10) -> List[Restaurant]:
        """
        Search restaurants with advanced filtering
        O(m) complexity where m is query length
        """
        start_time = time.time()
        
        try:
            # Check if indexes need update
            if time.time() - self.last_index_update > self.index_update_interval:
                self.initialize_search_indexes()
            
            # Basic search using trie
            results = search_restaurants_fast(query, limit * 2)  # Get more for filtering
            
            # Apply filters if provided
            if filters:
                results = self._apply_restaurant_filters(results, filters)
            
            # Update search statistics
            self.search_stats['total_searches'] += 1
            response_time = time.time() - start_time
            self.search_stats['avg_response_time'] = (
                (self.search_stats['avg_response_time'] * (self.search_stats['total_searches'] - 1) + response_time) 
                / self.search_stats['total_searches']
            )
            
            return results[:limit]
            
        except Exception as e:
            log(f"Error in restaurant search: {e}")
            return []
    
    def search_menu_items(self, query: str, restaurant_id: Optional[int] = None, limit: int = 10) -> List:
        """
        Search menu items with optional restaurant filtering
        O(m) complexity where m is query length
        """
        try:
            # Basic search using trie
            results = search_menu_items_fast(query, limit * 2)
            
            # Filter by restaurant if specified
            if restaurant_id:
                results = [item for item in results if item.restaurant_id == restaurant_id]
            
            return results[:limit]
            
        except Exception as e:
            log(f"Error in menu item search: {e}")
            return []
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions for autocomplete
        O(m) complexity where m is query length
        """
        try:
            return get_search_suggestions_fast(query, limit)
        except Exception as e:
            log(f"Error getting search suggestions: {e}")
            return []
    
    def get_restaurants_by_cuisine(self, cuisine: str, limit: int = 10) -> List[Restaurant]:
        """
        Get restaurants by cuisine type
        O(1) complexity using index
        """
        try:
            results = restaurant_index.find_by_cuisine(cuisine)
            return results[:limit]
        except Exception as e:
            log(f"Error getting restaurants by cuisine: {e}")
            return []
    
    def get_restaurants_by_rating(self, min_rating: float, max_rating: float = 5.0, limit: int = 10) -> List[Restaurant]:
        """
        Get restaurants by rating range
        O(log n) complexity using binary search
        """
        try:
            results = restaurant_index.find_by_rating_range(min_rating, max_rating)
            return results[:limit]
        except Exception as e:
            log(f"Error getting restaurants by rating: {e}")
            return []
    
    def get_restaurants_by_location(self, location: str, limit: int = 10) -> List[Restaurant]:
        """
        Get restaurants by location
        O(1) complexity using index
        """
        try:
            results = restaurant_index.find_by_location(location)
            return results[:limit]
        except Exception as e:
            log(f"Error getting restaurants by location: {e}")
            return []
    
    def get_restaurant_from_cache(self, restaurant_id: int) -> Optional[Restaurant]:
        """
        Get restaurant from cache
        O(1) complexity
        """
        cache_key = f"restaurant_{restaurant_id}"
        return restaurant_cache.get(cache_key)
    
    def get_menu_item_from_cache(self, item_id: int):
        """
        Get menu item from cache
        O(1) complexity
        """
        cache_key = f"menu_{item_id}"
        return menu_cache.get(cache_key)
    
    def get_popular_restaurants(self, limit: int = 10) -> List[Restaurant]:
        """
        Get popular restaurants based on order frequency
        Uses cached data for O(1) complexity
        """
        try:
            # Get restaurants with high ratings and order count
            popular = restaurant_index.find_by_rating_range(4.0, 5.0)
            
            # Sort by order count (if available)
            popular = sorted(popular, key=lambda r: getattr(r, 'order_count', 0), reverse=True)
            
            return popular[:limit]
        except Exception as e:
            log(f"Error getting popular restaurants: {e}")
            return []
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[Restaurant]:
        """
        Get personalized restaurant recommendations
        Uses collaborative filtering and user history
        """
        try:
            # Get user's order history
            user_orders = get_orders_by_user_id(user_id)
            
            # Extract cuisine preferences
            preferred_cuisines = self._extract_cuisine_preferences(user_orders)
            
            # Get restaurants matching preferences
            recommendations = []
            for cuisine in preferred_cuisines:
                restaurants = self.get_restaurants_by_cuisine(cuisine, limit // len(preferred_cuisines) + 1)
                recommendations.extend(restaurants)
            
            # Remove duplicates and return
            seen = set()
            unique_recommendations = []
            for restaurant in recommendations:
                if restaurant.restaurant_id not in seen:
                    seen.add(restaurant.restaurant_id)
                    unique_recommendations.append(restaurant)
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            log(f"Error getting user recommendations: {e}")
            return []
    
    def _apply_restaurant_filters(self, restaurants: List[Restaurant], filters: Dict) -> List[Restaurant]:
        """Apply filters to restaurant results"""
        filtered = restaurants
        
        if 'cuisine' in filters:
            filtered = [r for r in filtered if hasattr(r, 'cuisine_type') and r.cuisine_type.lower() == filters['cuisine'].lower()]
        
        if 'min_rating' in filters:
            filtered = [r for r in filtered if r.rating >= filters['min_rating']]
        
        if 'max_rating' in filters:
            filtered = [r for r in filtered if r.rating <= filters['max_rating']]
        
        if 'location' in filters:
            filtered = [r for r in filtered if hasattr(r, 'address') and filters['location'].lower() in r.address.lower()]
        
        if 'price_range' in filters:
            # Skip price range filter since Restaurant model doesn't have this attribute
            pass
        
        return filtered
    
    def _extract_cuisine_preferences(self, orders: List[Order]) -> List[str]:
        """Extract cuisine preferences from user's order history"""
        cuisine_counts = {}
        
        for order in orders:
            try:
                # Get restaurant from cache or database
                restaurant = self.get_restaurant_from_cache(order.restaurant_id)
                if not restaurant:
                    restaurant = Restaurant.get_by_id(order.restaurant_id)
                
                if restaurant and hasattr(restaurant, 'cuisine_type'):
                    cuisine = restaurant.cuisine_type
                    cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            except Exception as e:
                log(f"Error processing order {order.order_id}: {e}")
                continue
        
        # Sort by frequency and return top cuisines
        sorted_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)
        return [cuisine for cuisine, count in sorted_cuisines[:3]]  # Top 3 cuisines
    
    def get_analytics(self) -> Dict:
        """Get search service analytics"""
        return {
            'search_stats': self.search_stats,
            'performance_analytics': get_performance_analytics(),
            'cache_stats': {
                'restaurant_cache_size': restaurant_cache.size(),
                'menu_cache_size': menu_cache.size()
            }
        }
    
    def clear_caches(self):
        """Clear all caches"""
        restaurant_cache.clear()
        menu_cache.clear()
        log("All caches cleared")


# Global instance
restaurant_search_service = RestaurantSearchService()


def initialize_restaurant_search():
    """Initialize restaurant search service"""
    restaurant_search_service.initialize_search_indexes()


def search_restaurants_optimized(query: str, filters: Optional[Dict] = None, limit: int = 10) -> List[Restaurant]:
    """Optimized restaurant search function"""
    return restaurant_search_service.search_restaurants(query, filters, limit)


def search_menu_items_optimized(query: str, restaurant_id: Optional[int] = None, limit: int = 10) -> List:
    """Optimized menu item search function"""
    return restaurant_search_service.search_menu_items(query, restaurant_id, limit)


def get_restaurant_suggestions(query: str, limit: int = 5) -> List[str]:
    """Get restaurant search suggestions"""
    return restaurant_search_service.get_search_suggestions(query, limit)


def get_user_restaurant_recommendations(user_id: int, limit: int = 10) -> List[Restaurant]:
    """Get personalized restaurant recommendations"""
    return restaurant_search_service.get_user_recommendations(user_id, limit)
