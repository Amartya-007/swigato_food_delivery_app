import customtkinter as ctk
from gui_Light import (
    BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, 
    SUCCESS_COLOR, SECONDARY_COLOR, GRAY_TEXT_COLOR, ERROR_COLOR,
    FRAME_FG_COLOR, FRAME_BORDER_COLOR
)
from users.favorites_ui import FavoritesListComponent
from gui_components.restaurant_list_component import RestaurantListComponent
from gui_components.order_history_component import OrderHistoryComponent
from gui_components.cart_component import CartComponent
from gui_components.navigation_component import NavigationComponent
from utils.logger import log


class SimpleMainAppScreen(ctk.CTkFrame):
    """Simplified main app screen with better organization"""
    
    def __init__(self, app_ref, user, show_menu_callback, logout_callback):
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)
        
        self.app_ref = app_ref
        self.user = user
        self.show_menu_callback = show_menu_callback
        self.logout_callback = logout_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Header
        self.create_header()
        
        # Main content area
        self.create_content_area()
        
        # Navigation
        self.create_navigation()
        
        # Show restaurants by default
        self.show_content("home")
        
    def create_header(self):
        """Create simple header"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=f"Welcome back, {self.user.username}! 👋",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_COLOR
        )
        welcome_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Discover amazing restaurants near you",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Admin button (if admin)
        if hasattr(self.user, "is_admin") and self.user.is_admin:
            admin_btn = ctk.CTkButton(
                header_frame,
                text="Admin Panel",
                width=120,
                height=35,
                fg_color=SECONDARY_COLOR,
                hover_color="#B91C1C",
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=8,
                command=lambda: self.app_ref.show_admin_screen(self.user)
            )
            admin_btn.grid(row=0, column=1, padx=10)
            
    def create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize all content components
        self.setup_content_components()
        
    def setup_content_components(self):
        """Setup all content components"""
        # Restaurant list with search
        self.restaurant_container = ctk.CTkFrame(self.content_frame, fg_color=BACKGROUND_COLOR)
        self.restaurant_container.grid_columnconfigure(0, weight=1)
        self.restaurant_container.grid_rowconfigure(1, weight=1)
        
        # Search bar
        self.create_search_bar()
        
        # Restaurant list
        self.restaurant_list = RestaurantListComponent(
            self.restaurant_container,
            self.app_ref,
            self.show_menu_callback
        )
        self.restaurant_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Order history
        self.order_history = OrderHistoryComponent(self.content_frame, self.user)
        
        # Favorites
        self.favorites_list = FavoritesListComponent(
            self.content_frame,
            user=self.user,
            app_ref=self.app_ref,
            show_menu_callback=self.show_menu_callback,
            fg_color=BACKGROUND_COLOR
        )
        
        # Cart
        self.cart_component = CartComponent(self.content_frame, self.app_ref)
        
        # Hide all except restaurants initially
        self.order_history.grid_remove()
        self.favorites_list.grid_remove()
        self.cart_component.grid_remove()
        
    def create_search_bar(self):
        """Create search bar for restaurants"""
        search_frame = ctk.CTkFrame(
            self.restaurant_container,
            fg_color=FRAME_FG_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Search icon
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=16)
        ).grid(row=0, column=0, padx=15, pady=10)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search restaurants or cuisine...",
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="white",
            text_color=TEXT_COLOR,
            placeholder_text_color=GRAY_TEXT_COLOR,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
    def create_navigation(self):
        """Create navigation bar"""
        self.navigation = NavigationComponent(
            self,
            nav_callback=self.show_content,
            logout_callback=self.logout_callback
        )
        self.navigation.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
    def show_content(self, tab_name):
        """Show content based on tab selection"""
        # Hide all content
        self.restaurant_container.grid_remove()
        self.order_history.grid_remove()
        self.favorites_list.grid_remove()
        self.cart_component.grid_remove()
        
        # Show selected content
        if tab_name == "home":
            self.restaurant_container.grid(row=0, column=0, sticky="nsew")
            self.restaurant_list.load_restaurants()
            
        elif tab_name == "orders":
            self.order_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.order_history.load_orders()
            
        elif tab_name == "favorites":
            self.favorites_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.favorites_list.load_favorites()
            
        elif tab_name == "cart":
            self.cart_component.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.cart_component.load_cart()
            
        # Update navigation
        self.navigation.set_active_tab(tab_name)
        
    def on_search_change(self, event):
        """Handle search input changes"""
        search_text = self.search_entry.get()
        self.restaurant_list.filter_restaurants(search_text)
        
    def set_active_nav_tab(self, tab_name):
        """Set active navigation tab (for external calls)"""
        self.navigation.set_active_tab(tab_name)
        
    def show_cart_content(self):
        """Show cart content (for external calls)"""
        self.show_content("cart")
        
    def show_restaurants_content(self):
        """Show restaurants content (for external calls)"""
        self.show_content("home")
        
    def handle_nav_click(self, tab_name):
        """Handle navigation clicks (for external calls)"""
        self.show_content(tab_name)
        
    def update_user_info(self, user):
        """Update user information"""
        self.user = user
        log("User information updated in SimpleMainAppScreen")
