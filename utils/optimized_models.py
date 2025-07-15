"""
Optimized Models with Advanced Data Structures
Provides better performance for common operations
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import bisect
import time
from utils.logger import log
from utils.advanced_data_structures import LRUCache, SearchTrie


class OptimizedRestaurantCache:
    """
    Optimized restaurant data management with O(1) lookups
    """
    
    def __init__(self):
        self.cache = LRUCache(capacity=1000)
        self.id_index = {}
        self.name_index = {}
        self.cuisine_index = defaultdict(list)
        self.rating_sorted_list = []  # For range queries
        self.search_trie = SearchTrie()
        
    def add_restaurant(self, restaurant):
        """Add restaurant to optimized cache"""
        # Cache the restaurant
        cache_key = f"restaurant_{restaurant.restaurant_id}"
        self.cache.put(cache_key, restaurant)
        
        # Update indexes
        self.id_index[restaurant.restaurant_id] = restaurant
        self.name_index[restaurant.name.lower()] = restaurant
        self.cuisine_index[restaurant.cuisine_type.lower()].append(restaurant)
        
        # Add to search trie
        self.search_trie.insert(restaurant.name, restaurant)
        if restaurant.cuisine_type:
            self.search_trie.insert(restaurant.cuisine_type, restaurant)
        
        # Update rating sorted list
        self._update_rating_list(restaurant)
        
    def get_by_id(self, restaurant_id: int):
        """Get restaurant by ID with O(1) complexity"""
        return self.id_index.get(restaurant_id)
    
    def get_by_name(self, name: str):
        """Get restaurant by name with O(1) complexity"""
        return self.name_index.get(name.lower())
    
    def get_by_cuisine(self, cuisine_type: str) -> List:
        """Get restaurants by cuisine with O(1) complexity"""
        return self.cuisine_index.get(cuisine_type.lower(), [])
    
    def search(self, query: str) -> List:
        """Search restaurants with O(m) complexity"""
        return self.search_trie.starts_with(query)
    
    def get_by_rating_range(self, min_rating: float, max_rating: float) -> List:
        """Get restaurants within rating range with O(log n) complexity"""
        # Binary search for range
        left_idx = bisect.bisect_left(self.rating_sorted_list, (min_rating, None))
        right_idx = bisect.bisect_right(self.rating_sorted_list, (max_rating, None))
        
        return [item[1] for item in self.rating_sorted_list[left_idx:right_idx]]
    
    def _update_rating_list(self, restaurant):
        """Update rating sorted list"""
        rating = getattr(restaurant, 'rating', 0.0)
        item = (rating, restaurant)
        
        # Remove old entry if exists
        self.rating_sorted_list = [
            item for item in self.rating_sorted_list 
            if item[1].restaurant_id != restaurant.restaurant_id
        ]
        
        # Insert new entry in sorted order
        bisect.insort(self.rating_sorted_list, item)


class OptimizedMenuCache:
    """
    Optimized menu item management with O(1) lookups
    """
    
    def __init__(self):
        self.cache = LRUCache(capacity=5000)
        self.id_index = {}
        self.restaurant_index = defaultdict(list)
        self.category_index = defaultdict(list)
        self.price_sorted_list = []  # For price range queries
        self.search_trie = SearchTrie()
        
    def add_menu_item(self, menu_item):
        """Add menu item to optimized cache"""
        # Cache the menu item
        cache_key = f"menu_item_{menu_item.item_id}"
        self.cache.put(cache_key, menu_item)
        
        # Update indexes
        self.id_index[menu_item.item_id] = menu_item
        self.restaurant_index[menu_item.restaurant_id].append(menu_item)
        self.category_index[menu_item.category.lower()].append(menu_item)
        
        # Add to search trie
        self.search_trie.insert(menu_item.name, menu_item)
        self.search_trie.insert(menu_item.category, menu_item)
        
        # Update price sorted list
        self._update_price_list(menu_item)
        
    def get_by_id(self, item_id: int):
        """Get menu item by ID with O(1) complexity"""
        return self.id_index.get(item_id)
    
    def get_by_restaurant(self, restaurant_id: int) -> List:
        """Get menu items by restaurant with O(1) complexity"""
        return self.restaurant_index.get(restaurant_id, [])
    
    def get_by_category(self, category: str) -> List:
        """Get menu items by category with O(1) complexity"""
        return self.category_index.get(category.lower(), [])
    
    def search(self, query: str) -> List:
        """Search menu items with O(m) complexity"""
        return self.search_trie.starts_with(query)
    
    def get_by_price_range(self, min_price: float, max_price: float) -> List:
        """Get menu items within price range with O(log n) complexity"""
        # Binary search for range
        left_idx = bisect.bisect_left(self.price_sorted_list, (min_price, None))
        right_idx = bisect.bisect_right(self.price_sorted_list, (max_price, None))
        
        return [item[1] for item in self.price_sorted_list[left_idx:right_idx]]
    
    def _update_price_list(self, menu_item):
        """Update price sorted list"""
        price = getattr(menu_item, 'price', 0.0)
        item = (price, menu_item)
        
        # Remove old entry if exists
        self.price_sorted_list = [
            item for item in self.price_sorted_list 
            if item[1].item_id != menu_item.item_id
        ]
        
        # Insert new entry in sorted order
        bisect.insort(self.price_sorted_list, item)


class OptimizedCart:
    """
    Optimized cart with O(1) operations
    """
    
    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
        self.items = {}  # item_id -> CartItem
        self.item_lookup = {}  # For O(1) lookups
        self._total_cache = None
        self._total_dirty = True
        self._count_cache = None
        self._count_dirty = True
        
    def add_item(self, menu_item, quantity: int = 1):
        """Add item with O(1) complexity"""
        item_id = menu_item.item_id
        
        if item_id in self.items:
            self.items[item_id].quantity += quantity
        else:
            from cart.models import CartItem
            self.items[item_id] = CartItem(menu_item, quantity)
            self.item_lookup[item_id] = self.items[item_id]
        
        self._invalidate_cache()
        return True
    
    def remove_item(self, item_id: int, quantity: Optional[int] = None):
        """Remove item with O(1) complexity"""
        if item_id not in self.items:
            return False
        
        if quantity is None or quantity >= self.items[item_id].quantity:
            del self.items[item_id]
            if item_id in self.item_lookup:
                del self.item_lookup[item_id]
        else:
            self.items[item_id].quantity -= quantity
        
        self._invalidate_cache()
        return True
    
    def get_total_price(self) -> float:
        """Get total price with O(1) complexity (cached)"""
        if self._total_dirty:
            self._total_cache = sum(item.item_total for item in self.items.values())
            self._total_dirty = False
        
        return self._total_cache or 0.0
    
    def get_total_items(self) -> int:
        """Get total item count with O(1) complexity (cached)"""
        if self._count_dirty:
            self._count_cache = sum(item.quantity for item in self.items.values())
            self._count_dirty = False
        
        return self._count_cache or 0
    
    def clear_cart(self):
        """Clear cart with O(1) complexity"""
        self.items.clear()
        self.item_lookup.clear()
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Invalidate cached values"""
        self._total_dirty = True
        self._count_dirty = True


class OptimizedOrderManager:
    """
    Optimized order management with advanced data structures
    """
    
    def __init__(self):
        self.orders_by_user = defaultdict(list)
        self.orders_by_restaurant = defaultdict(list)
        self.orders_by_status = defaultdict(list)
        self.orders_by_date = []  # Sorted by date
        self.order_cache = LRUCache(capacity=2000)
        
    def add_order(self, order):
        """Add order to optimized structures"""
        # Cache the order
        cache_key = f"order_{order.order_id}"
        self.order_cache.put(cache_key, order)
        
        # Update indexes
        self.orders_by_user[order.user_id].append(order)
        self.orders_by_restaurant[order.restaurant_id].append(order)
        self.orders_by_status[order.status].append(order)
        
        # Insert into date sorted list
        order_date_item = (order.order_date, order)
        bisect.insort(self.orders_by_date, order_date_item)
        
    def get_orders_by_user(self, user_id: int) -> List:
        """Get orders by user with O(1) complexity"""
        return self.orders_by_user.get(user_id, [])
    
    def get_orders_by_restaurant(self, restaurant_id: int) -> List:
        """Get orders by restaurant with O(1) complexity"""
        return self.orders_by_restaurant.get(restaurant_id, [])
    
    def get_orders_by_status(self, status: str) -> List:
        """Get orders by status with O(1) complexity"""
        return self.orders_by_status.get(status, [])
    
    def get_orders_by_date_range(self, start_date, end_date) -> List:
        """Get orders within date range with O(log n) complexity"""
        left_idx = bisect.bisect_left(self.orders_by_date, (start_date, None))
        right_idx = bisect.bisect_right(self.orders_by_date, (end_date, None))
        
        return [item[1] for item in self.orders_by_date[left_idx:right_idx]]
    
    def update_order_status(self, order_id: int, new_status: str):
        """Update order status with O(1) complexity"""
        # Find order in cache
        cache_key = f"order_{order_id}"
        order = self.order_cache.get(cache_key)
        
        if order:
            old_status = order.status
            
            # Remove from old status index
            if old_status in self.orders_by_status:
                self.orders_by_status[old_status] = [
                    o for o in self.orders_by_status[old_status] 
                    if o.order_id != order_id
                ]
            
            # Update order status
            order.status = new_status
            
            # Add to new status index
            self.orders_by_status[new_status].append(order)
            
            return True
        
        return False


class OptimizedUserManager:
    """
    Optimized user management with advanced data structures
    """
    
    def __init__(self):
        self.users_by_id = {}
        self.users_by_username = {}
        self.users_by_email = {}
        self.admin_users = set()
        self.user_cache = LRUCache(capacity=1000)
        self.user_activity = defaultdict(list)  # Track user activity
        
    def add_user(self, user):
        """Add user to optimized structures"""
        # Cache the user
        cache_key = f"user_{user.user_id}"
        self.user_cache.put(cache_key, user)
        
        # Update indexes
        self.users_by_id[user.user_id] = user
        self.users_by_username[user.username.lower()] = user
        
        if user.email:
            self.users_by_email[user.email.lower()] = user
        
        if user.is_admin:
            self.admin_users.add(user.user_id)
    
    def get_by_id(self, user_id: int):
        """Get user by ID with O(1) complexity"""
        return self.users_by_id.get(user_id)
    
    def get_by_username(self, username: str):
        """Get user by username with O(1) complexity"""
        return self.users_by_username.get(username.lower())
    
    def get_by_email(self, email: str):
        """Get user by email with O(1) complexity"""
        return self.users_by_email.get(email.lower())
    
    def get_admin_users(self) -> List:
        """Get all admin users with O(1) complexity"""
        return [self.users_by_id[user_id] for user_id in self.admin_users]
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin with O(1) complexity"""
        return user_id in self.admin_users
    
    def track_user_activity(self, user_id: int, activity: str):
        """Track user activity for analytics"""
        self.user_activity[user_id].append({
            'activity': activity,
            'timestamp': time.time()
        })
        
        # Keep only last 100 activities per user
        if len(self.user_activity[user_id]) > 100:
            self.user_activity[user_id] = self.user_activity[user_id][-100:]


# Global optimized cache instances
restaurant_cache = OptimizedRestaurantCache()
menu_cache = OptimizedMenuCache()
order_manager = OptimizedOrderManager()
user_manager = OptimizedUserManager()
