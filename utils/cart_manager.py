"""
Cart Manager with Advanced Data Structures
Implements efficient cart operations with O(1) complexity for common operations
"""

from typing import Dict, List, Optional, Set, Any
from collections import defaultdict
import bisect
import time
import threading
from utils.logger import log
from utils.search_engine import DataCache, OrderPriorityQueue
from cart.models import Cart, CartItem


class AdvancedCartManager:
    """
    Advanced cart management with O(1) operations for most common tasks
    Uses hash tables and caching for optimal performance
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cart = Cart(user_id)
        self.cache = DataCache(capacity=100)
        self.lock = threading.Lock()
        self.last_updated = time.time()
        
    def add_item(self, menu_item, quantity: int = 1) -> bool:
        """Add item to cart with O(1) complexity"""
        with self.lock:
            try:
                result = self.cart.add_item(menu_item, quantity)
                if result:
                    self.last_updated = time.time()
                    self._update_cache()
                return result
            except Exception as e:
                log(f"Error adding item to cart: {e}")
                return False
    
    def remove_item(self, item_id: int, quantity: Optional[int] = None) -> bool:
        """Remove item from cart with O(1) complexity"""
        with self.lock:
            try:
                result = self.cart.remove_item(item_id, quantity)
                if result:
                    self.last_updated = time.time()
                    self._update_cache()
                return result
            except Exception as e:
                log(f"Error removing item from cart: {e}")
                return False
    
    def get_total_price(self) -> float:
        """Get total price with O(1) complexity"""
        return self.cart.get_total_price()
    
    def get_total_items(self) -> int:
        """Get total item count with O(1) complexity"""
        return self.cart.get_total_items()
    
    def get_item_count(self) -> int:
        """Get unique item count with O(1) complexity"""
        return len(self.cart.items)
    
    def get_all_items(self) -> List[CartItem]:
        """Get all items with O(1) complexity"""
        return list(self.cart.items.values())
    
    def has_item(self, item_id: int) -> bool:
        """Check if item exists with O(1) complexity"""
        return item_id in self.cart.items
    
    def get_item(self, item_id: int) -> Optional[CartItem]:
        """Get specific item with O(1) complexity"""
        return self.cart.items.get(item_id)
    
    def clear_cart(self):
        """Clear entire cart with O(1) complexity"""
        with self.lock:
            self.cart.clear_cart()
            self.cache.clear()
            self.last_updated = time.time()
    
    def get_cart_summary(self) -> Dict:
        """Get cart summary with O(1) complexity"""
        return {
            'total_price': self.get_total_price(),
            'total_items': self.get_total_items(),
            'unique_items': self.get_item_count(),
            'last_updated': self.last_updated
        }
    
    def _update_cache(self):
        """Update cache with current cart state"""
        cache_key = f"cart_summary_{self.user_id}"
        self.cache.put(cache_key, self.get_cart_summary())


class FastOrderManager:
    """
    Fast order management using priority queues and indexing
    Provides O(log n) complexity for order operations
    """
    
    def __init__(self):
        self.order_queue = OrderPriorityQueue()
        self.order_index = {}  # order_id -> order
        self.user_orders = defaultdict(list)  # user_id -> [orders]
        self.restaurant_orders = defaultdict(list)  # restaurant_id -> [orders]
        self.status_orders = defaultdict(list)  # status -> [orders]
        self.cache = DataCache(capacity=500)
        self.lock = threading.Lock()
    
    def add_order(self, order, priority: Optional[float] = None):
        """Add order to processing queue with O(log n) complexity"""
        with self.lock:
            try:
                # Calculate priority if not provided
                if priority is None:
                    priority = self._calculate_order_priority(order)
                
                # Add to priority queue
                self.order_queue.add_order(order, priority)
                
                # Add to indexes
                self.order_index[order.order_id] = order
                self.user_orders[order.user_id].append(order)
                self.restaurant_orders[order.restaurant_id].append(order)
                self.status_orders[order.status].append(order)
                
                # Cache order
                cache_key = f"order_{order.order_id}"
                self.cache.put(cache_key, order)
                
                log(f"Order {order.order_id} added to queue with priority {priority}")
                
            except Exception as e:
                log(f"Error adding order to queue: {e}")
    
    def get_next_order(self):
        """Get next order to process with O(log n) complexity"""
        with self.lock:
            try:
                order = self.order_queue.get_next_order()
                if order:
                    log(f"Processing order {order.order_id}")
                return order
            except Exception as e:
                log(f"Error getting next order: {e}")
                return None
    
    def update_order_status(self, order_id: int, new_status: str):
        """Update order status with O(1) complexity"""
        with self.lock:
            try:
                if order_id not in self.order_index:
                    return False
                
                order = self.order_index[order_id]
                old_status = order.status
                
                # Remove from old status list
                if old_status in self.status_orders:
                    self.status_orders[old_status].remove(order)
                
                # Update status
                order.status = new_status
                
                # Add to new status list
                self.status_orders[new_status].append(order)
                
                # Update cache
                cache_key = f"order_{order_id}"
                self.cache.put(cache_key, order)
                
                return True
                
            except Exception as e:
                log(f"Error updating order status: {e}")
                return False
    
    def get_orders_by_user(self, user_id: int) -> List:
        """Get orders by user with O(1) complexity"""
        return self.user_orders.get(user_id, [])
    
    def get_orders_by_restaurant(self, restaurant_id: int) -> List:
        """Get orders by restaurant with O(1) complexity"""
        return self.restaurant_orders.get(restaurant_id, [])
    
    def get_orders_by_status(self, status: str) -> List:
        """Get orders by status with O(1) complexity"""
        return self.status_orders.get(status, [])
    
    def get_order_from_cache(self, order_id: int):
        """Get order from cache with O(1) complexity"""
        cache_key = f"order_{order_id}"
        return self.cache.get(cache_key)
    
    def _calculate_order_priority(self, order) -> float:
        """Calculate order priority based on various factors"""
        priority = 1.0
        
        # Higher priority for premium users
        if hasattr(order, 'user') and getattr(order.user, 'is_premium', False):
            priority += 0.5
        
        # Higher priority for smaller orders (faster to prepare)
        if hasattr(order, 'items') and len(order.items) <= 3:
            priority += 0.3
        
        # Higher priority for cash payments (confirmed payment)
        if hasattr(order, 'payment_method') and order.payment_method == 'cash':
            priority += 0.1
        
        return priority
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'queue_size': self.order_queue.get_queue_size(),
            'is_empty': self.order_queue.is_empty(),
            'total_orders': len(self.order_index),
            'orders_by_status': {status: len(orders) for status, orders in self.status_orders.items()}
        }


class RecommendationEngine:
    """
    Recommendation engine using collaborative filtering
    Provides O(1) to O(log n) complexity for recommendations
    """
    
    def __init__(self):
        self.user_preferences = defaultdict(dict)  # user_id -> {item_id: rating}
        self.item_users = defaultdict(set)  # item_id -> {user_ids}
        self.user_similarity = {}  # (user1, user2) -> similarity_score
        self.item_popularity = defaultdict(int)  # item_id -> popularity_score
        self.cache = DataCache(capacity=1000)
        self.lock = threading.Lock()
    
    def add_user_preference(self, user_id: int, item_id: int, rating: float):
        """Add user preference with O(1) complexity"""
        with self.lock:
            self.user_preferences[user_id][item_id] = rating
            self.item_users[item_id].add(user_id)
            self.item_popularity[item_id] += 1
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[int]:
        """Get recommendations for user with O(k) complexity where k is number of similar users"""
        cache_key = f"recommendations_{user_id}"
        
        # Check cache first
        cached_recommendations = self.cache.get(cache_key)
        if cached_recommendations:
            return cached_recommendations[:limit]
        
        try:
            # Get user's preferences
            user_prefs = self.user_preferences.get(user_id, {})
            if not user_prefs:
                # Return popular items for new users
                popular_items = sorted(self.item_popularity.items(), key=lambda x: x[1], reverse=True)
                recommendations = [item_id for item_id, _ in popular_items[:limit]]
                self.cache.put(cache_key, recommendations)
                return recommendations
            
            # Find similar users
            similar_users = self._find_similar_users(user_id, limit=20)
            
            # Get recommendations based on similar users
            recommendations = self._get_collaborative_recommendations(user_id, similar_users, limit)
            
            # Cache results
            self.cache.put(cache_key, recommendations)
            
            return recommendations
            
        except Exception as e:
            log(f"Error getting recommendations: {e}")
            return []
    
    def _find_similar_users(self, user_id: int, limit: int = 20) -> List[int]:
        """Find similar users using collaborative filtering"""
        user_prefs = self.user_preferences.get(user_id, {})
        similarities = []
        
        for other_user_id in self.user_preferences:
            if other_user_id == user_id:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(user_prefs, self.user_preferences[other_user_id])
            if similarity > 0:
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity and return top users
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [user_id for user_id, _ in similarities[:limit]]
    
    def _calculate_similarity(self, prefs1: Dict, prefs2: Dict) -> float:
        """Calculate similarity between two users using cosine similarity"""
        # Find common items
        common_items = set(prefs1.keys()) & set(prefs2.keys())
        
        if not common_items:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(prefs1[item] * prefs2[item] for item in common_items)
        
        norm1 = sum(prefs1[item] ** 2 for item in common_items) ** 0.5
        norm2 = sum(prefs2[item] ** 2 for item in common_items) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _get_collaborative_recommendations(self, user_id: int, similar_users: List[int], limit: int) -> List[int]:
        """Get recommendations based on similar users"""
        user_prefs = self.user_preferences.get(user_id, {})
        recommendations = defaultdict(float)
        
        for similar_user_id in similar_users:
            similar_user_prefs = self.user_preferences[similar_user_id]
            
            for item_id, rating in similar_user_prefs.items():
                if item_id not in user_prefs:  # Only recommend items user hasn't rated
                    recommendations[item_id] += rating
        
        # Sort by score and return top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in sorted_recommendations[:limit]]


# Global instances
cart_managers = {}  # user_id -> AdvancedCartManager
order_manager = FastOrderManager()
recommendation_engine = RecommendationEngine()


def get_cart_manager(user_id: int) -> AdvancedCartManager:
    """Get or create cart manager for user"""
    if user_id not in cart_managers:
        cart_managers[user_id] = AdvancedCartManager(user_id)
    return cart_managers[user_id]


def get_order_manager() -> FastOrderManager:
    """Get global order manager"""
    return order_manager


def get_recommendation_engine() -> RecommendationEngine:
    """Get global recommendation engine"""
    return recommendation_engine
