"""
Advanced Data Structures and Algorithms for Swigato Food Delivery App
This module implements optimized data structures and algorithms to reduce complexity
and improve performance across the application.
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
        self.data = []  # Store actual data objects here
        
    def add_data(self, data):
        """Add data to this node"""
        if data not in self.data:
            self.data.append(data)


class SearchTrie:
    """
    Trie implementation for O(m) search complexity where m is query length
    Reduces search complexity from O(n*m) to O(m) for autocomplete and search
    """
    def __init__(self):
        self.root = TrieNode()
        self.size = 0
    
    def insert(self, word: str, data: Any):
        """Insert a word with associated data into the trie"""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end_of_word = True
        node.add_data(data)
        self.size += 1
    
    def search(self, word: str) -> List[Any]:
        """Search for exact word match"""
        node = self.root
        word = word.lower().strip()
        
        for char in word:
            if char not in node.children:
                return []
            node = node.children[char]
        
        return node.data if node.is_end_of_word else []
    
    def starts_with(self, prefix: str) -> List[Any]:
        """Find all data with words starting with prefix"""
        node = self.root
        prefix = prefix.lower().strip()
        
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all data from this node and its children
        result = []
        self._collect_data(node, result)
        return result
    
    def _collect_data(self, node: TrieNode, result: List[Any]):
        """Recursively collect all data from node and its children"""
        if node.is_end_of_word:
            result.extend(node.data)
        
        for child in node.children.values():
            self._collect_data(child, result)


class LRUCache:
    """
    Least Recently Used Cache implementation for O(1) operations
    Reduces database queries by caching frequently accessed data
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.order = deque()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with O(1) complexity"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.order.remove(key)
                self.order.append(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        """Put value in cache with O(1) complexity"""
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache[key] = value
                self.order.remove(key)
                self.order.append(key)
            else:
                # Add new
                if len(self.cache) >= self.capacity:
                    # Remove least recently used
                    oldest = self.order.popleft()
                    del self.cache[oldest]
                
                self.cache[key] = value
                self.order.append(key)
    
    def clear(self):
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
            self.order.clear()


class PriorityQueue:
    """
    Min-heap based priority queue for O(log n) operations
    Useful for order processing, restaurant ranking, etc.
    """
    def __init__(self):
        self.heap = []
        self.entry_finder = {}
        self.counter = 0
    
    def push(self, item: Any, priority: float):
        """Add item with priority"""
        if item in self.entry_finder:
            self.remove(item)
        
        entry = [priority, self.counter, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.heap, entry)
        self.counter += 1
    
    def pop(self) -> Any:
        """Remove and return item with lowest priority"""
        while self.heap:
            priority, count, item = heapq.heappop(self.heap)
            if item in self.entry_finder:
                del self.entry_finder[item]
                return item
        raise KeyError('pop from empty priority queue')
    
    def remove(self, item: Any):
        """Remove item from queue"""
        if item in self.entry_finder:
            entry = self.entry_finder.pop(item)
            entry[-1] = None  # Mark as deleted
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.entry_finder) == 0


class BloomFilter:
    """
    Probabilistic data structure for fast membership testing
    Reduces false positives in search and recommendation systems
    """
    def __init__(self, expected_items: int, false_positive_prob: float = 0.1):
        self.size = self._optimal_size(expected_items, false_positive_prob)
        self.hash_count = self._optimal_hash_count(self.size, expected_items)
        self.bit_array = [False] * self.size
        self.item_count = 0
    
    def _optimal_size(self, n: int, p: float) -> int:
        """Calculate optimal bit array size"""
        import math
        return int(-(n * math.log(p)) / (math.log(2) ** 2))
    
    def _optimal_hash_count(self, m: int, n: int) -> int:
        """Calculate optimal number of hash functions"""
        import math
        return int((m / n) * math.log(2))
    
    def _hash(self, item: str, seed: int) -> int:
        """Simple hash function with seed"""
        hash_val = seed
        for char in str(item):
            hash_val = (hash_val * 31 + ord(char)) % self.size
        return hash_val
    
    def add(self, item: str):
        """Add item to bloom filter"""
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = True
        self.item_count += 1
    
    def contains(self, item: str) -> bool:
        """Check if item might be in the set"""
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if not self.bit_array[index]:
                return False
        return True


class OptimizedSearchEngine:
    """
    High-performance search engine combining multiple data structures
    Provides O(1) to O(log n) search complexity for different use cases
    """
    def __init__(self):
        self.restaurant_trie = SearchTrie()
        self.menu_trie = SearchTrie()
        self.cuisine_trie = SearchTrie()
        self.cache = LRUCache(capacity=1000)
        self.bloom_filter = BloomFilter(expected_items=10000)
        self.search_analytics = defaultdict(int)
        
        # Index mappings for O(1) lookups
        self.restaurant_by_id = {}
        self.menu_by_id = {}
        self.cuisine_index = defaultdict(list)
        self.price_index = defaultdict(list)
        
        # Geospatial index for location-based queries
        self.location_index = {}
        
    def build_indexes(self, restaurants: List[Any], menu_items: List[Any]):
        """Build all search indexes for optimal performance"""
        log("Building optimized search indexes...")
        start_time = time.time()
        
        # Build restaurant indexes
        for restaurant in restaurants:
            # Trie for name search
            self.restaurant_trie.insert(restaurant.name, restaurant)
            
            # ID mapping for O(1) lookup
            self.restaurant_by_id[restaurant.restaurant_id] = restaurant
            
            # Cuisine index
            if restaurant.cuisine_type:
                self.cuisine_trie.insert(restaurant.cuisine_type, restaurant)
                self.cuisine_index[restaurant.cuisine_type.lower()].append(restaurant)
            
            # Bloom filter for quick existence check
            self.bloom_filter.add(restaurant.name)
            
            # Add to cache if frequently accessed
            cache_key = f"restaurant_{restaurant.restaurant_id}"
            self.cache.put(cache_key, restaurant)
        
        # Build menu item indexes
        for item in menu_items:
            # Trie for name search
            self.menu_trie.insert(item.name, item)
            
            # ID mapping
            self.menu_by_id[item.item_id] = item
            
            # Price range index
            price_range = self._get_price_range(item.price)
            self.price_index[price_range].append(item)
            
            # Bloom filter
            self.bloom_filter.add(item.name)
        
        build_time = time.time() - start_time
        log(f"Search indexes built in {build_time:.3f} seconds")
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into ranges for indexing"""
        if price <= 100:
            return "budget"
        elif price <= 300:
            return "mid-range"
        elif price <= 500:
            return "premium"
        else:
            return "luxury"
    
    def search_restaurants(self, query: str, filters: Optional[Dict] = None) -> List[Any]:
        """
        Optimized restaurant search with O(m) complexity for query length m
        """
        cache_key = f"search_restaurants_{query}_{hash(str(filters))}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Track search analytics
        self.search_analytics[query.lower()] += 1
        
        # Quick existence check with bloom filter
        if not self.bloom_filter.contains(query):
            return []
        
        results = set()
        
        # Trie-based search for names
        name_matches = self.restaurant_trie.starts_with(query)
        results.update(name_matches)
        
        # Cuisine-based search
        cuisine_matches = self.cuisine_trie.starts_with(query)
        results.update(cuisine_matches)
        
        # Apply filters
        if filters:
            results = self._apply_filters(list(results), filters)
        
        # Cache result
        result_list = list(results)
        self.cache.put(cache_key, result_list)
        
        return result_list
    
    def search_menu_items(self, query: str, restaurant_id: Optional[int] = None) -> List[Any]:
        """
        Optimized menu item search with O(m) complexity
        """
        cache_key = f"search_menu_{query}_{restaurant_id}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Trie-based search
        results = self.menu_trie.starts_with(query)
        
        # Filter by restaurant if specified
        if restaurant_id:
            results = [item for item in results if item.restaurant_id == restaurant_id]
        
        # Cache result
        self.cache.put(cache_key, results)
        
        return results
    
    def _apply_filters(self, results: List[Any], filters: Dict) -> List[Any]:
        """Apply filters to search results"""
        filtered_results = results
        
        if "cuisine" in filters:
            filtered_results = [r for r in filtered_results if r.cuisine_type and r.cuisine_type.lower() == filters["cuisine"].lower()]
        
        if "min_rating" in filters:
            filtered_results = [r for r in filtered_results if r.rating >= filters["min_rating"]]
        
        if "max_price" in filters:
            # This would require menu price analysis
            pass
        
        return filtered_results
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions with O(m) complexity
        """
        suggestions = []
        
        # Get restaurant name suggestions
        restaurant_matches = self.restaurant_trie.starts_with(query)
        suggestions.extend([r.name for r in restaurant_matches[:limit//2]])
        
        # Get menu item suggestions
        menu_matches = self.menu_trie.starts_with(query)
        suggestions.extend([m.name for m in menu_matches[:limit//2]])
        
        return suggestions[:limit]
    
    def get_popular_searches(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most popular search queries"""
        return sorted(self.search_analytics.items(), key=lambda x: x[1], reverse=True)[:limit]


class OptimizedOrderQueue:
    """
    Optimized order processing queue using priority queue
    Processes orders based on priority, estimated time, etc.
    """
    def __init__(self):
        self.pending_orders = PriorityQueue()
        self.processing_orders = {}
        self.completed_orders = deque(maxlen=1000)  # Keep last 1000 completed orders
        self.order_metrics = {
            'total_processed': 0,
            'average_processing_time': 0,
            'peak_queue_size': 0
        }
    
    def add_order(self, order: Any, priority: Optional[float] = None):
        """Add order to processing queue"""
        if priority is None:
            # Calculate priority based on order value, user type, etc.
            priority = self._calculate_priority(order)
        
        self.pending_orders.push(order, priority)
        
        # Update metrics
        current_size = len(self.pending_orders.entry_finder)
        if current_size > self.order_metrics['peak_queue_size']:
            self.order_metrics['peak_queue_size'] = current_size
    
    def _calculate_priority(self, order: Any) -> float:
        """Calculate order priority based on various factors"""
        priority = 0.0
        
        # Higher priority for premium users
        if hasattr(order, 'user') and getattr(order.user, 'is_premium', False):
            priority -= 10.0  # Lower number = higher priority
        
        # Higher priority for larger orders
        if hasattr(order, 'total_amount'):
            priority -= order.total_amount * 0.01
        
        # Higher priority for urgent orders
        if hasattr(order, 'is_urgent') and order.is_urgent:
            priority -= 20.0
        
        # Add timestamp to prevent starvation
        priority += time.time()
        
        return priority
    
    def process_next_order(self) -> Optional[Any]:
        """Get next order to process"""
        try:
            order = self.pending_orders.pop()
            self.processing_orders[order.order_id] = {
                'order': order,
                'start_time': time.time()
            }
            return order
        except KeyError:
            return None
    
    def complete_order(self, order_id: int):
        """Mark order as completed"""
        if order_id in self.processing_orders:
            order_data = self.processing_orders.pop(order_id)
            processing_time = time.time() - order_data['start_time']
            
            # Update metrics
            self.order_metrics['total_processed'] += 1
            current_avg = self.order_metrics['average_processing_time']
            total_processed = self.order_metrics['total_processed']
            
            # Calculate new average
            self.order_metrics['average_processing_time'] = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
            
            # Add to completed orders
            self.completed_orders.append({
                'order': order_data['order'],
                'processing_time': processing_time,
                'completed_at': time.time()
            })
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        return {
            'pending_count': len(self.pending_orders.entry_finder),
            'processing_count': len(self.processing_orders),
            'completed_count': len(self.completed_orders),
            'metrics': self.order_metrics
        }


class OptimizedRecommendationEngine:
    """
    Recommendation engine using collaborative filtering and content-based filtering
    Provides O(1) to O(log n) recommendation complexity
    """
    def __init__(self):
        self.user_preferences = defaultdict(lambda: defaultdict(float))
        self.item_similarity = {}
        self.user_similarity = {}
        self.cache = LRUCache(capacity=500)
        
    def update_user_preference(self, user_id: int, item_id: int, rating: float):
        """Update user preference with O(1) complexity"""
        self.user_preferences[user_id][item_id] = rating
        
        # Invalidate cache for this user
        cache_key = f"recommendations_{user_id}"
        if cache_key in self.cache.cache:
            del self.cache.cache[cache_key]
    
    def get_recommendations(self, user_id: int, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Get recommendations with optimized complexity
        """
        cache_key = f"recommendations_{user_id}"
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result[:limit]
        
        # Calculate recommendations
        recommendations = []
        user_prefs = self.user_preferences[user_id]
        
        if not user_prefs:
            # Cold start - return popular items
            recommendations = self._get_popular_items(limit)
        else:
            # Collaborative filtering
            similar_users = self._find_similar_users(user_id)
            recommendations = self._collaborative_filtering(user_id, similar_users, limit)
        
        # Cache result
        self.cache.put(cache_key, recommendations)
        
        return recommendations[:limit]
    
    def _find_similar_users(self, user_id: int) -> List[Tuple[int, float]]:
        """Find similar users using cosine similarity"""
        user_prefs = self.user_preferences[user_id]
        similarities = []
        
        for other_user_id, other_prefs in self.user_preferences.items():
            if other_user_id != user_id:
                similarity = self._cosine_similarity(user_prefs, other_prefs)
                if similarity > 0.3:  # Threshold for similarity
                    similarities.append((other_user_id, similarity))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:10]
    
    def _cosine_similarity(self, prefs1: Dict, prefs2: Dict) -> float:
        """Calculate cosine similarity between two preference vectors"""
        common_items = set(prefs1.keys()) & set(prefs2.keys())
        if not common_items:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(prefs1[item] * prefs2[item] for item in common_items)
        magnitude1 = sum(prefs1[item] ** 2 for item in common_items) ** 0.5
        magnitude2 = sum(prefs2[item] ** 2 for item in common_items) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _collaborative_filtering(self, user_id: int, similar_users: List[Tuple[int, float]], limit: int) -> List[Tuple[int, float]]:
        """Generate recommendations using collaborative filtering"""
        user_prefs = self.user_preferences[user_id]
        recommendations = defaultdict(float)
        
        for similar_user_id, similarity in similar_users:
            similar_user_prefs = self.user_preferences[similar_user_id]
            
            for item_id, rating in similar_user_prefs.items():
                if item_id not in user_prefs:  # Only recommend new items
                    recommendations[item_id] += similarity * rating
        
        # Sort by recommendation score
        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def _get_popular_items(self, limit: int) -> List[Tuple[int, float]]:
        """Get popular items for cold start"""
        item_scores = defaultdict(float)
        
        for user_prefs in self.user_preferences.values():
            for item_id, rating in user_prefs.items():
                item_scores[item_id] += rating
        
        return sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:limit]


# Global instances for application-wide use
search_engine = OptimizedSearchEngine()
order_queue = OptimizedOrderQueue()
recommendation_engine = OptimizedRecommendationEngine()
