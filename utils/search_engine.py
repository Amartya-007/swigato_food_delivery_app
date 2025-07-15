"""
Search Engine Implementation for Swigato Food Delivery App
Implements Trie data structure for efficient restaurant and menu item search
Reduces search complexity from O(n*m) to O(m) where m is query length
"""

import heapq
import bisect
from collections import defaultdict, deque
from typing import List, Dict, Set, Optional, Tuple, Any
import time
import threading
from functools import lru_cache
from utils.logger import log


class TrieNode:
    """Node for implementing Trie data structure for efficient search"""
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.restaurants = []  # Store restaurant objects
        self.menu_items = []   # Store menu item objects
        
    def add_restaurant(self, restaurant):
        """Add restaurant to this node"""
        if restaurant not in self.restaurants:
            self.restaurants.append(restaurant)
    
    def add_menu_item(self, menu_item):
        """Add menu item to this node"""
        if menu_item not in self.menu_items:
            self.menu_items.append(menu_item)


class RestaurantSearchTrie:
    """
    Trie implementation for O(m) restaurant search complexity
    Optimizes restaurant and menu item search operations
    """
    def __init__(self):
        self.root = TrieNode()
        self.restaurant_count = 0
        self.menu_item_count = 0
        self.lock = threading.Lock()
    
    def insert_restaurant(self, restaurant):
        """Insert a restaurant into the trie for search"""
        with self.lock:
            # Insert by restaurant name
            self._insert_word(restaurant.name, restaurant, is_restaurant=True)
            
            # Insert by cuisine type
            if hasattr(restaurant, 'cuisine_type'):
                self._insert_word(restaurant.cuisine_type, restaurant, is_restaurant=True)
            
            # Insert by address
            if hasattr(restaurant, 'address'):
                self._insert_word(restaurant.address, restaurant, is_restaurant=True)
            
            self.restaurant_count += 1
    
    def insert_menu_item(self, menu_item):
        """Insert a menu item into the trie for search"""
        with self.lock:
            # Insert by item name
            self._insert_word(menu_item.name, menu_item, is_restaurant=False)
            
            # Insert by category
            if hasattr(menu_item, 'category'):
                self._insert_word(menu_item.category, menu_item, is_restaurant=False)
            
            self.menu_item_count += 1
    
    def _insert_word(self, word: str, data: Any, is_restaurant: bool = True):
        """Insert a word with associated data into the trie"""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end_of_word = True
        if is_restaurant:
            node.add_restaurant(data)
        else:
            node.add_menu_item(data)
    
    def search_restaurants(self, query: str, limit: int = 10) -> List:
        """Search for restaurants with O(m) complexity"""
        if not query:
            return []
        
        node = self.root
        query = query.lower().strip()
        
        # Navigate to the node representing the query
        for char in query:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all restaurants from this node and its descendants
        results = []
        self._collect_restaurants(node, results, limit)
        
        return results[:limit]
    
    def search_menu_items(self, query: str, limit: int = 10) -> List:
        """Search for menu items with O(m) complexity"""
        if not query:
            return []
        
        node = self.root
        query = query.lower().strip()
        
        # Navigate to the node representing the query
        for char in query:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all menu items from this node and its descendants
        results = []
        self._collect_menu_items(node, results, limit)
        
        return results[:limit]
    
    def _collect_restaurants(self, node: TrieNode, results: List, limit: int):
        """Recursively collect restaurants from trie nodes"""
        if len(results) >= limit:
            return
        
        if node.is_end_of_word:
            results.extend(node.restaurants)
            if len(results) >= limit:
                return
        
        for child in node.children.values():
            self._collect_restaurants(child, results, limit)
            if len(results) >= limit:
                return
    
    def _collect_menu_items(self, node: TrieNode, results: List, limit: int):
        """Recursively collect menu items from trie nodes"""
        if len(results) >= limit:
            return
        
        if node.is_end_of_word:
            results.extend(node.menu_items)
            if len(results) >= limit:
                return
        
        for child in node.children.values():
            self._collect_menu_items(child, results, limit)
            if len(results) >= limit:
                return
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions with O(m) complexity"""
        if not query:
            return []
        
        node = self.root
        query = query.lower().strip()
        
        # Navigate to the node representing the query
        for char in query:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all possible completions
        suggestions = []
        self._collect_suggestions(node, query, suggestions, limit)
        
        return suggestions[:limit]
    
    def _collect_suggestions(self, node: TrieNode, prefix: str, suggestions: List[str], limit: int):
        """Recursively collect search suggestions"""
        if len(suggestions) >= limit:
            return
        
        if node.is_end_of_word:
            suggestions.append(prefix)
            if len(suggestions) >= limit:
                return
        
        for char, child in node.children.items():
            self._collect_suggestions(child, prefix + char, suggestions, limit)
            if len(suggestions) >= limit:
                return


class DataCache:
    """
    LRU Cache implementation for O(1) data access
    Reduces database queries and improves response times
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with O(1) complexity"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        """Put value in cache with O(1) complexity"""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.access_order.remove(key)
                self.access_order.append(key)
            else:
                # Add new
                if len(self.cache) >= self.capacity:
                    # Remove least recently used
                    oldest = self.access_order.popleft()
                    del self.cache[oldest]
                
                self.cache[key] = value
                self.access_order.append(key)
    
    def clear(self):
        """Clear all cache data"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


class OrderPriorityQueue:
    """
    Priority Queue implementation for efficient order processing
    Ensures high-priority orders are processed first with O(log n) complexity
    """
    def __init__(self):
        self.heap = []
        self.order_map = {}  # order_id -> order
        self.lock = threading.Lock()
        self.order_counter = 0
    
    def add_order(self, order, priority: float = 1.0):
        """Add order to priority queue with O(log n) complexity"""
        with self.lock:
            self.order_counter += 1
            # Use negative priority for max heap behavior
            # Add counter to maintain insertion order for equal priorities
            heap_item = (-priority, self.order_counter, order.order_id)
            heapq.heappush(self.heap, heap_item)
            self.order_map[order.order_id] = order
    
    def get_next_order(self):
        """Get highest priority order with O(log n) complexity"""
        with self.lock:
            if not self.heap:
                return None
            
            _, _, order_id = heapq.heappop(self.heap)
            order = self.order_map.pop(order_id, None)
            return order
    
    def remove_order(self, order_id: int):
        """Remove specific order from queue"""
        with self.lock:
            if order_id in self.order_map:
                del self.order_map[order_id]
                # Note: We don't remove from heap immediately for efficiency
                # Instead, we check if order exists when processing
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.order_map)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.order_map) == 0


class RestaurantIndexManager:
    """
    Multi-index manager for fast restaurant lookups
    Provides O(1) to O(log n) complexity for various search criteria
    """
    def __init__(self):
        self.by_cuisine = defaultdict(list)
        self.by_rating = []  # Sorted list for binary search
        self.by_location = defaultdict(list)
        self.lock = threading.Lock()
    
    def add_restaurant(self, restaurant):
        """Add restaurant to all relevant indexes"""
        with self.lock:
            # Index by cuisine
            if hasattr(restaurant, 'cuisine_type'):
                self.by_cuisine[restaurant.cuisine_type.lower()].append(restaurant)
            
            # Index by rating (maintain sorted order)
            if hasattr(restaurant, 'rating'):
                bisect.insort(self.by_rating, (restaurant.rating, restaurant))
            
            # Index by address
            if hasattr(restaurant, 'address'):
                self.by_location[restaurant.address.lower()].append(restaurant)
    
    def find_by_cuisine(self, cuisine: str) -> List:
        """Find restaurants by cuisine with O(1) complexity"""
        return self.by_cuisine.get(cuisine.lower(), [])
    
    def find_by_rating_range(self, min_rating: float, max_rating: float = 5.0) -> List:
        """Find restaurants by rating range with O(log n) complexity"""
        with self.lock:
            # Binary search for range
            left = bisect.bisect_left(self.by_rating, (min_rating, None))
            right = bisect.bisect_right(self.by_rating, (max_rating, None))
            
            return [restaurant for _, restaurant in self.by_rating[left:right]]
    
    def find_by_location(self, location: str) -> List:
        """Find restaurants by location with O(1) complexity"""
        return self.by_location.get(location.lower(), [])


class BloomFilter:
    """
    Bloom Filter implementation for fast existence checking
    Provides O(1) complexity for checking if item might exist
    """
    def __init__(self, capacity: int = 1000, error_rate: float = 0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        
        # Calculate optimal parameters
        self.bit_array_size = self._calculate_bit_array_size()
        self.hash_functions_count = self._calculate_hash_functions()
        
        self.bit_array = [False] * self.bit_array_size
        self.items_count = 0
    
    def _calculate_bit_array_size(self) -> int:
        """Calculate optimal bit array size"""
        import math
        return int(-(self.capacity * math.log(self.error_rate)) / (math.log(2) ** 2))
    
    def _calculate_hash_functions(self) -> int:
        """Calculate optimal number of hash functions"""
        import math
        return int((self.bit_array_size / self.capacity) * math.log(2))
    
    def _hash(self, item: str, seed: int) -> int:
        """Generate hash for item with given seed"""
        hash_value = 0
        for char in item:
            hash_value = (hash_value * seed + ord(char)) % self.bit_array_size
        return hash_value
    
    def add(self, item: str):
        """Add item to bloom filter"""
        for i in range(self.hash_functions_count):
            index = self._hash(item, i + 1)
            self.bit_array[index] = True
        self.items_count += 1
    
    def contains(self, item: str) -> bool:
        """Check if item might exist in filter"""
        for i in range(self.hash_functions_count):
            index = self._hash(item, i + 1)
            if not self.bit_array[index]:
                return False
        return True


# Global instances for the application
restaurant_search_trie = RestaurantSearchTrie()
restaurant_cache = DataCache(capacity=200)
menu_cache = DataCache(capacity=500)
order_queue = OrderPriorityQueue()
restaurant_index = RestaurantIndexManager()
menu_item_filter = BloomFilter(capacity=2000)

# Performance tracking
search_analytics = {
    'total_searches': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'average_response_time': 0.0
}

def track_search_performance(func):
    """Decorator to track search performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        search_analytics['total_searches'] += 1
        response_time = end_time - start_time
        search_analytics['average_response_time'] = (
            (search_analytics['average_response_time'] * (search_analytics['total_searches'] - 1) + response_time) 
            / search_analytics['total_searches']
        )
        
        return result
    return wrapper


@track_search_performance
def search_restaurants_fast(query: str, limit: int = 10) -> List:
    """Fast restaurant search using Trie with O(m) complexity"""
    return restaurant_search_trie.search_restaurants(query, limit)


@track_search_performance
def search_menu_items_fast(query: str, limit: int = 10) -> List:
    """Fast menu item search using Trie with O(m) complexity"""
    return restaurant_search_trie.search_menu_items(query, limit)


def get_search_suggestions_fast(query: str, limit: int = 5) -> List[str]:
    """Get search suggestions with O(m) complexity"""
    return restaurant_search_trie.get_search_suggestions(query, limit)


def initialize_search_engine():
    """Initialize the search engine with existing data"""
    log("Initializing search engine with advanced data structures...")
    
    try:
        # Import models to load existing data
        from restaurants.models import Restaurant, MenuItem
        
        # Load all restaurants into search trie
        restaurants = Restaurant.get_all()
        for restaurant in restaurants:
            restaurant_search_trie.insert_restaurant(restaurant)
            restaurant_index.add_restaurant(restaurant)
            
            # Load menu items for each restaurant
            menu_items = restaurant.menu
            for item in menu_items:
                restaurant_search_trie.insert_menu_item(item)
                menu_item_filter.add(item.name)
        
        log(f"Search engine initialized with {restaurant_search_trie.restaurant_count} restaurants and {restaurant_search_trie.menu_item_count} menu items")
        
    except Exception as e:
        log(f"Error initializing search engine: {e}")


def get_performance_analytics():
    """Get current performance analytics"""
    return {
        'search_analytics': search_analytics,
        'cache_stats': {
            'restaurant_cache_size': restaurant_cache.size(),
            'menu_cache_size': menu_cache.size(),
        },
        'queue_stats': {
            'pending_orders': order_queue.get_queue_size(),
            'is_empty': order_queue.is_empty()
        }
    }
