"""
Simple integration patch for MainAppScreen to use optimized search
This file provides a minimal modification to integrate optimized search functionality
"""

def patch_main_app_screen(main_app_screen_class):
    """
    Patch MainAppScreen class to use optimized search
    """
    original_on_search_change = main_app_screen_class.on_search_change
    
    def optimized_on_search_change(self, event=None):
        """
        Optimized search with O(m) complexity instead of O(n*m)
        """
        search_term = self.search_entry.get().lower()
        
        if not search_term:
            self.load_restaurants()
            return
        
        # Use optimized search if available
        if hasattr(self, 'optimization') and self.optimization:
            self.optimization.optimized_search(search_term)
        else:
            # Fall back to original search
            original_on_search_change(self, event)
    
    # Replace the method
    main_app_screen_class.on_search_change = optimized_on_search_change
    
    # Add optimization initialization
    original_init = main_app_screen_class.__init__
    
    def optimized_init(self, *args, **kwargs):
        # Call original init
        original_init(self, *args, **kwargs)
        
        # Initialize optimization
        try:
            from utils.search_optimization_integration import integrate_optimized_search
            integrate_optimized_search(self)
        except ImportError:
            # Optimization not available, use original functionality
            pass
    
    main_app_screen_class.__init__ = optimized_init
    
    return main_app_screen_class
