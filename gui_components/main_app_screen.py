import customtkinter as ctk
import os
from tkinter import messagebox
from PIL import Image, ImageTk

from gui_Light import (
    BACKGROUND_COLOR, SUCCESS_COLOR, TEXT_COLOR, PRIMARY_COLOR, 
    BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, 
    SECONDARY_COLOR, GRAY_TEXT_COLOR, ERROR_COLOR, BUTTON_TEXT_COLOR,
    HOVER_BG_COLOR, LIGHT_ORANGE_BG, set_swigato_icon
)
from utils.image_loader import load_image
from utils.logger import log
from orders.models import get_orders_by_user_id, create_order
from cart.models import Cart
from restaurants.models import Restaurant, MenuItem
from users.favorites_ui import FavoritesListComponent

class MainAppScreen(ctk.CTkFrame):
    def __init__(self, app_ref, user, show_menu_callback, logout_callback):
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)
        self.app_ref = app_ref # Store reference to the main SwigatoApp instance
        self.user = user
        self.show_menu_callback = show_menu_callback
        self.logout_callback = logout_callback
        self.restaurants = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)  # Bottom nav bar

        # --- Enhanced Main Content Area ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.main_content_frame.grid(row=1, column=0, padx=30, pady=(10, 15), sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # --- Modern Header Frame with Enhanced Styling ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1) # Welcome message
        header_frame.grid_columnconfigure(1, weight=0) # Spacer
        header_frame.grid_columnconfigure(2, weight=0) # Admin Panel (if admin)
        header_frame.grid_columnconfigure(3, weight=0) # Profile button

        # Modern welcome message with enhanced typography
        welcome_text = f"Welcome back, {self.user.username}! 👋"
        self.welcome_label = ctk.CTkLabel(header_frame, text=welcome_text,
                                          text_color=TEXT_COLOR,
                                          font=ctk.CTkFont(size=26, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle for better hierarchy
        subtitle_label = ctk.CTkLabel(header_frame, text="Discover amazing restaurants near you",
                                     text_color=GRAY_TEXT_COLOR,
                                     font=ctk.CTkFont(size=14))
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Modern Admin Panel button (if admin)
        if hasattr(self.user, "is_admin") and self.user.is_admin:
            admin_panel_button = ctk.CTkButton(
                header_frame,
                text="⚙️ Admin Panel",
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=12,
                height=40,
                command=lambda: self.app_ref.show_admin_screen(self.user)
            )
            admin_panel_button.grid(row=0, column=2, sticky="e", padx=(0, 15))
        
        # Modern Profile button (now rightmost in header, more prominent)
        profile_btn = ctk.CTkButton(
            header_frame,
            text="👤 Profile",
            width=120,
            height=45,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            border_width=0,
            corner_radius=22,
            command=self.show_profile_panel
        )
        # Position profile button at the rightmost position
        profile_col = 3 if hasattr(self.user, "is_admin") and self.user.is_admin else 2
        profile_btn.grid(row=0, column=profile_col, sticky="e")

        # Initialize content areas
        self.setup_content_areas()
        
        # Show restaurants by default
        self.show_restaurants_content()
        
        # --- Bottom Navigation Bar ---
        self.create_bottom_nav_bar()

    def get_status_color(self, status):
        status = status.lower()
        if status == "delivered":
            return SUCCESS_COLOR  # Green
        elif status == "pending":
            return "#FFA500"  # Orange
        elif status == "cancelled":
            return ERROR_COLOR  # Red
        else: # Processing, etc.
            return PRIMARY_COLOR # Blue

    def create_bottom_nav_bar(self):
        """Create the bottom navigation bar with modern glassmorphism effects"""
        # Create a modern glassmorphism-style navigation bar
        bottom_nav_frame = ctk.CTkFrame(
            self, 
            fg_color=FRAME_FG_COLOR, 
            height=90, 
            corner_radius=20,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        bottom_nav_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # Configure grid with better column distribution for centering
        bottom_nav_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        bottom_nav_frame.grid_columnconfigure(1, weight=0)  # Nav buttons container
        bottom_nav_frame.grid_columnconfigure(2, weight=1)  # Center spacer
        bottom_nav_frame.grid_columnconfigure(3, weight=0)  # Logout button
        bottom_nav_frame.pack_propagate(False)
        # Store navigation buttons for state management
        self.nav_buttons = {}
        
        # Create a centered container for navigation items
        nav_container = ctk.CTkFrame(bottom_nav_frame, fg_color="transparent")
        nav_container.grid(row=0, column=1, pady=15, sticky="")
        
        # Navigation items with modern icons - reordered with Home first
        nav_items = [
            ("home", "🏠", "Home"),  # Home moved to leftmost position
        ]
        
        # Add Orders for non-admin users
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            nav_items.append(("orders", "📋", "Orders"))        
        nav_items.extend([
            ("favorites", "⭐", "Favorites"),
            ("cart", "🛒", "Cart")  # Cart moved to rightmost position
        ])
        
        # Add cart count if there are items in the cart
        cart_count = 0
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            cart_count = len(self.app_ref.cart.items)
        if cart_count > 0:
            cart_text = f"🛒({cart_count})"
            nav_items = [(key, icon if key != "cart" else cart_text, label) for key, icon, label in nav_items]
        
        # Configure nav container grid
        for i in range(len(nav_items)):
            nav_container.grid_columnconfigure(i, weight=0)        
        # Modern button style with enhanced effects
        button_style = {
            "width": 60,
            "height": 60,
            "fg_color": "transparent",
            "hover_color": HOVER_BG_COLOR,
            "text_color": GRAY_TEXT_COLOR,
            "font": ctk.CTkFont(size=24),
            "border_width": 0,
            "corner_radius": 15
        }
        
        # Active button style with modern accent
        active_button_style = {
            "width": 60,
            "height": 60,
            "fg_color": PRIMARY_COLOR,
            "hover_color": BUTTON_HOVER_COLOR,
            "text_color": "white",
            "font": ctk.CTkFont(size=24),
            "border_width": 0,
            "corner_radius": 15
        }
          # Create navigation buttons with modern styling and better spacing
        for i, (key, icon, label) in enumerate(nav_items):
            # Button container for better spacing
            btn_container = ctk.CTkFrame(nav_container, fg_color="transparent")
            btn_container.grid(row=0, column=i, padx=20, pady=0, sticky="")  # Increased padding from 15 to 20
            btn_container.grid_rowconfigure(0, weight=0)
            btn_container.grid_rowconfigure(1, weight=0)
            
            # Modern icon button
            style = active_button_style if key == "home" else button_style
            btn = ctk.CTkButton(
                btn_container, 
                text=icon,
                command=lambda k=key: self.handle_nav_click(k),
                **style
            )
            btn.grid(row=0, column=0, pady=(0, 5))
            self.nav_buttons[key] = btn
            
            # Modern label with better typography
            label_widget = ctk.CTkLabel(
                btn_container, 
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=PRIMARY_COLOR if key == "home" else GRAY_TEXT_COLOR
            )
            label_widget.grid(row=1, column=0)
            
            # Store label reference for active state updates
            self.nav_buttons[f"{key}_label"] = label_widget
          # Logout button positioned at the far right
        logout_container = ctk.CTkFrame(bottom_nav_frame, fg_color="transparent")
        logout_container.grid(row=0, column=3, padx=20, pady=15, sticky="e")
        
        logout_btn = ctk.CTkButton(
            logout_container,
            text="Logout",
            command=self.logout_callback,
            fg_color=SECONDARY_COLOR,
            hover_color="#B91C1C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=75, 
            height=40, 
            corner_radius=12
        )
        logout_btn.pack()
        
        # Set current active tab
        self.current_nav_tab = "home"

    def handle_nav_click(self, tab_name):
        """Handle navigation button clicks with proper state management"""
        # Update button states
        self.set_active_nav_tab(tab_name)
        
        # Handle the actual navigation
        if tab_name == "cart":
            self.show_cart_content()
        elif tab_name == "home":
            self.show_restaurants_content()
        elif tab_name == "orders":
            self.show_orders_content()
        elif tab_name == "favorites":
            self.show_favorites_content()
        # Profile is now handled from the top header, not bottom nav
    
    def set_active_nav_tab(self, active_tab):
        """Set the active navigation tab and update button styles"""
        self.current_nav_tab = active_tab
        
        # Define styles
        inactive_style = {
            "fg_color": "transparent",
            "text_color": GRAY_TEXT_COLOR
        }
        active_style = {
            "fg_color": PRIMARY_COLOR,
            "text_color": "white"
        }
        
        # Update all navigation buttons and labels
        for tab_name, button in self.nav_buttons.items():
            if "_label" not in tab_name:  # Skip label widgets
                if tab_name == active_tab:
                    button.configure(**active_style)
                    # Update corresponding label color
                    if f"{tab_name}_label" in self.nav_buttons:
                        self.nav_buttons[f"{tab_name}_label"].configure(text_color=PRIMARY_COLOR)
                else:
                    button.configure(**inactive_style)
                    # Update corresponding label color
                    if f"{tab_name}_label" in self.nav_buttons:
                        self.nav_buttons[f"{tab_name}_label"].configure(text_color=GRAY_TEXT_COLOR)

    def setup_content_areas(self):
        """Setup all content areas in the main content frame"""
        
        # Create a container for restaurants section with search
        self.restaurant_container = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.restaurant_container.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.restaurant_container.grid_columnconfigure(0, weight=1)
        self.restaurant_container.grid_rowconfigure(0, weight=0)  # Search bar
        self.restaurant_container.grid_rowconfigure(1, weight=1)  # Restaurant list        # Search bar frame
        search_frame = ctk.CTkFrame(self.restaurant_container, fg_color=FRAME_FG_COLOR, 
                                   corner_radius=12, border_width=1, border_color=FRAME_BORDER_COLOR)
        search_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        # Search icon/label
        ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=20), 
                    text_color=PRIMARY_COLOR).grid(row=0, column=0, padx=(15, 10), pady=10)        # Search entry with light theme styling
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search restaurants, cuisines, or food items...",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="white",
            text_color=TEXT_COLOR,
            placeholder_text_color=GRAY_TEXT_COLOR,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Filter button with consistent styling
        filter_btn = ctk.CTkButton(
            search_frame,
            text="🍜 Filter",
            width=100,
            height=40,
            fg_color=FRAME_FG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color=TEXT_COLOR,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=8,            command=self.show_filter_options
        )
        filter_btn.grid(row=0, column=2, padx=(0, 15), pady=10)
        
        # Modern Restaurant List Scrollable Frame
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(
            self.restaurant_container, 
            fg_color=BACKGROUND_COLOR, 
            border_width=0,
            corner_radius=0
        )
        self.restaurant_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Modern Favorites content frame
        self.favorites_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.favorites_content_frame.grid_columnconfigure(0, weight=1)
        self.favorites_content_frame.grid_rowconfigure(1, weight=1)

        favorites_heading = ctk.CTkLabel(
            self.favorites_content_frame,
            text="⭐ Your Favorites",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_COLOR
        )
        favorites_heading.grid(row=0, column=0, pady=(15, 10), sticky="n")

        # Use the FavoritesListComponent
        self.favorites_list_component = FavoritesListComponent(
            self.favorites_content_frame, 
            user=self.user, 
            app_ref=self.app_ref,
            show_menu_callback=self.show_menu_callback,
            fg_color=BACKGROUND_COLOR
        )
        self.favorites_list_component.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # Modern Orders content frame
        self.orders_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.orders_content_frame.grid_columnconfigure(0, weight=1)
        self.orders_content_frame.grid_rowconfigure(1, weight=1)

        orders_heading = ctk.CTkLabel(
            self.orders_content_frame,
            text="📋 Your Order History",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_COLOR
        )
        orders_heading.grid(row=0, column=0, pady=(15, 10), sticky="n")

        self.orders_scroll_frame = ctk.CTkScrollableFrame(
            self.orders_content_frame, 
            fg_color=BACKGROUND_COLOR, 
            corner_radius=0, 
            border_width=0
        )
        self.orders_scroll_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.orders_scroll_frame.grid_columnconfigure(0, weight=1)

        # Modern Cart content frame
        self.cart_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.cart_content_frame.grid_columnconfigure(0, weight=1)
        self.cart_content_frame.grid_rowconfigure(1, weight=1)

        cart_heading = ctk.CTkLabel(
            self.cart_content_frame,
            text="🛒 Your Shopping Cart",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT_COLOR
        )
        cart_heading.grid(row=0, column=0, pady=(15, 10), sticky="n")

        self.cart_scroll_frame = ctk.CTkScrollableFrame(
            self.cart_content_frame, 
            fg_color=BACKGROUND_COLOR, 
            corner_radius=0, 
            border_width=0
        )
        self.cart_scroll_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.cart_scroll_frame.grid_columnconfigure(0, weight=1)# Hide all content frames initially
        self.favorites_content_frame.grid_remove()
        self.orders_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()

    def show_restaurants_content(self):
        """Show restaurants content"""
        # Hide other content
        self.favorites_content_frame.grid_remove()
        self.orders_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
          # Show restaurants container (includes search bar)
        self.restaurant_container.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.load_restaurants()

    def show_favorites_content(self):
        """Show favorites content"""
        # Hide other content
        self.restaurant_container.grid_remove()
        self.orders_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
        
        # Show favorites
        self.favorites_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.favorites_list_component.load_favorites()

    def show_orders_content(self):
        """Show orders content"""
        # Hide other content
        self.restaurant_container.grid_remove()
        self.favorites_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
        
        # Show orders
        self.orders_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_order_history()

    def show_cart_content(self):
        """Show cart content"""
        # Hide other content
        self.restaurant_container.grid_remove()
        self.favorites_content_frame.grid_remove()
        self.orders_content_frame.grid_remove()
          # Show cart
        self.cart_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_cart_items()

    def load_order_history(self):
        """Load and display order history in the orders content area (only one colored status label per order)"""
        # Clear existing widgets
        for widget in self.orders_scroll_frame.winfo_children():
            widget.destroy()

        # Get user orders
        try:
            orders = get_orders_by_user_id(self.user.user_id)
        except Exception as e:
            log(f"Error loading orders: {e}")
            orders = []

        if not orders:
            # Modern empty state
            empty_frame = ctk.CTkFrame(
                self.orders_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            empty_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📋",
                font=ctk.CTkFont(size=48),
                text_color=GRAY_TEXT_COLOR
            )
            empty_icon.pack(pady=(30, 10))
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No orders yet!",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=GRAY_TEXT_COLOR
            )
            empty_label.pack(pady=(0, 10))
            
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Your order history will appear here",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR
            )
            empty_desc.pack(pady=(0, 30))
            return

        # Display orders
        for i, order in enumerate(orders):
            order_card = ctk.CTkFrame(
                self.orders_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            order_card.grid(row=i, column=0, padx=20, pady=(0, 15), sticky="ew")
            order_card.grid_columnconfigure(1, weight=1)

            # Order status icon
            status_icon = "✅" if order.status.lower() == "delivered" else "🕒"
            status_label = ctk.CTkLabel(
                order_card,
                text=status_icon,
                font=ctk.CTkFont(size=24),
                text_color=SUCCESS_COLOR if order.status.lower() == "delivered" else PRIMARY_COLOR
            )
            status_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

            # Order details
            details_frame = ctk.CTkFrame(order_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
            details_frame.grid_columnconfigure(0, weight=1)

            # Order ID and date
            order_header = ctk.CTkLabel(
                details_frame,
                text=f"Order #{order.order_id} • {order.order_date.strftime('%B %d, %Y')}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            order_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))

            # Order total
            total_label = ctk.CTkLabel(
                details_frame,
                text=f"Total: ₹{order.total_amount:.2f}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=PRIMARY_COLOR,
                anchor="w"
            )
            total_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))

            # Only one status label, below the total, with correct color
            status_color = self.get_status_color(order.status)
            status_display = ctk.CTkLabel(
                details_frame,
                text=f"Status: {order.status.title()}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color,
                anchor="w"
            )
            status_display.grid(row=2, column=0, sticky="ew", pady=(0, 5))

    def load_restaurants(self):
        log("MainAppScreen.load_restaurants called")
        self.restaurants = Restaurant.get_all()
        log(f"Loaded {len(self.restaurants)} restaurants.")
        self.display_restaurants(self.restaurants)

    def display_restaurants(self, restaurants):
        log(f"Displaying {len(restaurants)} restaurants.")
        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()

        if not restaurants:
            no_restaurants_label = ctk.CTkLabel(self.restaurant_scroll_frame,
                                                text="No restaurants match your search.",
                                                text_color=TEXT_COLOR,
                                                font=ctk.CTkFont(size=16))
            no_restaurants_label.grid(row=0, column=0, pady=20)
            return

        for i, restaurant in enumerate(restaurants):
            # Ultra-modern restaurant card with advanced styling
            restaurant_card = ctk.CTkFrame(
                self.restaurant_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                border_color=FRAME_BORDER_COLOR,
                border_width=1,
                corner_radius=20,  # More rounded for modern look
                height=160
            )
            restaurant_card.grid(row=i, column=0, pady=(0, 25), padx=20, sticky="ew")
            restaurant_card.grid_columnconfigure(0, weight=0)  # Image
            restaurant_card.grid_columnconfigure(1, weight=1)  # Details
            restaurant_card.grid_columnconfigure(2, weight=0)  # Actions
            restaurant_card.pack_propagate(False)

            # Modern image container with enhanced styling
            image_container = ctk.CTkFrame(
                restaurant_card, 
                fg_color="transparent", 
                corner_radius=16
            )
            image_container.grid(row=0, column=0, rowspan=3, padx=20, pady=20, sticky="ns")
            
            image_label = None
            if restaurant.image_filename:
                project_root = self.app_ref.project_root
                image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
                log(f"Attempting to load restaurant image from: {image_path}")
                ctk_image = load_image(image_path, size=(120, 120))
                if ctk_image:
                    image_label = ctk.CTkLabel(
                        image_container, 
                        image=ctk_image, 
                        text="", 
                        corner_radius=16
                    )
                    image_label.pack()
            
            if not image_label:
                # Modern placeholder with gradient-like effect
                image_label = ctk.CTkLabel(
                    image_container, 
                    text="🍽️", 
                    width=120, 
                    height=120,
                    fg_color=PRIMARY_COLOR,
                    text_color="white",
                    font=ctk.CTkFont(size=48),
                    corner_radius=16
                )
                image_label.pack()

            # Details frame
            details_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, rowspan=3, padx=(0, 20), pady=20, sticky="nsew")
            details_frame.grid_rowconfigure(0, weight=0)
            details_frame.grid_rowconfigure(1, weight=0)
            details_frame.grid_rowconfigure(2, weight=1) # Spacer

            # Restaurant name
            name_label = ctk.CTkLabel(
                details_frame,
                text=restaurant.name,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            name_label.grid(row=0, column=0, sticky="ew")

            # Cuisine type
            cuisine_text = restaurant.cuisine_type or "Variety"
            cuisine_label = ctk.CTkLabel(
                details_frame,
                text=f"🍴 {cuisine_text}",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                anchor="w"
            )
            cuisine_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))

            # Actions frame
            actions_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            actions_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20, sticky="nse")

            # View Menu button
            view_menu_btn = ctk.CTkButton(
                actions_frame,
                text="View Menu",
                command=lambda r=restaurant: self.show_menu_callback(r),
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=40,
                corner_radius=12
            )
            view_menu_btn.pack(expand=True, anchor="e")

    def load_cart_items(self):
        """Load and display cart items in the cart content area."""
        # Clear existing widgets
        for widget in self.cart_scroll_frame.winfo_children():
            widget.destroy()

        cart = self.app_ref.cart
        if not cart or not cart.items:
            # Modern empty cart message
            empty_frame = ctk.CTkFrame(
                self.cart_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            empty_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="🛒",
                font=ctk.CTkFont(size=48),
                text_color=GRAY_TEXT_COLOR
            )
            empty_icon.pack(pady=(30, 10))
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="Your cart is empty!",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=GRAY_TEXT_COLOR
            )
            empty_label.pack(pady=(0, 10))
            
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Add items from restaurants to see them here.",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR
            )
            empty_desc.pack(pady=(0, 30))
            return

        # Display cart items with modern design
        for i, (menu_item_id, cart_item) in enumerate(cart.items.items()):
            # Modern cart item card
            item_card = ctk.CTkFrame(
                self.cart_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR,
                height=100
            )
            item_card.grid(row=i, column=0, padx=20, pady=(0, 15), sticky="ew")
            item_card.grid_columnconfigure(1, weight=1)
            item_card.grid_columnconfigure(2, weight=0)
            item_card.pack_propagate(False)

            # Food icon
            food_icon = ctk.CTkLabel(
                item_card,
                text="🍽️",
                font=ctk.CTkFont(size=32),
                text_color=PRIMARY_COLOR
            )
            food_icon.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

            # Item details with modern layout
            details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
            details_frame.grid_rowconfigure(0, weight=0)
            details_frame.grid_rowconfigure(1, weight=0)

            item_name = ctk.CTkLabel(
                details_frame,
                text=cart_item.menu_item.name,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            item_name.grid(row=0, column=0, sticky="ew", pady=(0, 5))

            price_text = f"₹{cart_item.menu_item.price:.2f} × {cart_item.quantity} = ₹{cart_item.menu_item.price * cart_item.quantity:.2f}"
            item_price = ctk.CTkLabel(
                details_frame,
                text=price_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=PRIMARY_COLOR,
                anchor="w"
            )
            item_price.grid(row=1, column=0, sticky="ew")

            # Quantity controls and remove button
            controls_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            controls_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")

            def create_update_cmd(item_id, qty_change):
                return lambda: self.update_cart_item_quantity(item_id, qty_change)

            minus_btn = ctk.CTkButton(
                controls_frame, 
                text="−", 
                width=35, 
                height=35, 
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=SECONDARY_COLOR,
                hover_color="#B91C1C",
                text_color="white",
                corner_radius=8,
                command=create_update_cmd(menu_item_id, -1)
            )
            minus_btn.pack(side="left", padx=(0, 5))

            quantity_label = ctk.CTkLabel(
                controls_frame, 
                text=str(cart_item.quantity), 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=TEXT_COLOR,
                width=40
            )
            quantity_label.pack(side="left", padx=5)

            plus_btn = ctk.CTkButton(
                controls_frame, 
                text="+", 
                width=35, 
                height=35, 
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=SUCCESS_COLOR,
                hover_color="#388E3C",
                text_color="white",
                corner_radius=8,
                command=create_update_cmd(menu_item_id, 1)
            )
            plus_btn.pack(side="left", padx=(5, 15))

            remove_btn = ctk.CTkButton(
                controls_frame, 
                text="🗑️ Remove", 
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                text_color=ERROR_COLOR,
                hover_color=HOVER_BG_COLOR,
                width=80,
                height=30,
                corner_radius=6,
                command=lambda item_id=menu_item_id: self.remove_item_from_cart(item_id)
            )
            remove_btn.pack(side="left")

        # Modern Checkout section with enhanced styling
        checkout_frame = ctk.CTkFrame(
            self.cart_scroll_frame, 
            fg_color=FRAME_FG_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        checkout_frame.grid(row=len(cart.items), column=0, padx=20, pady=20, sticky="ew")
        checkout_frame.grid_columnconfigure(0, weight=1)
        checkout_frame.grid_columnconfigure(1, weight=0)

        # Total section with modern styling
        total_container = ctk.CTkFrame(checkout_frame, fg_color="transparent")
        total_container.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        total_icon = ctk.CTkLabel(
            total_container,
            text="💰",
            font=ctk.CTkFont(size=24),
            text_color=PRIMARY_COLOR
        )
        total_icon.pack(side="left", padx=(0, 10))
        
        total_label = ctk.CTkLabel(
            total_container,
            text=f"Total: ₹{cart.get_total_price():.2f}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        total_label.pack(side="left")

        # Modern checkout button
        checkout_btn = ctk.CTkButton(
            checkout_frame,
            text="🛒 Proceed to Checkout",
            width=200,
            height=55,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            corner_radius=15,
            command=self.proceed_to_checkout
        )
        checkout_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

    def update_cart_item_quantity(self, menu_item_id, quantity_change):
        cart = self.app_ref.cart
        current_item = cart.items.get(menu_item_id)
        if current_item:
            new_quantity = current_item.quantity + quantity_change
            if new_quantity > 0:
                cart.add_item(current_item.menu_item, quantity_change) # Use add_item to handle updates
            else:
                cart.remove_item(menu_item_id)
            
            self.load_cart_items() # Refresh cart view
            self.update_cart_count_in_nav()

    def remove_item_from_cart(self, menu_item_id):
        self.app_ref.cart.remove_item(menu_item_id)
        self.load_cart_items()
        self.update_cart_count_in_nav()

    def proceed_to_checkout(self):
        cart = self.app_ref.cart
        if not cart or not cart.items:
            messagebox.showwarning("Empty Cart", "Your cart is empty.", parent=self)
            return

        # --- This is a simplification: assumes all items are from one restaurant ---
        # Get the first item to determine the restaurant
        first_cart_item = next(iter(cart.items.values()))
        restaurant_id = first_cart_item.menu_item.restaurant_id
        
        # Fetch restaurant details
        restaurant = Restaurant.get_by_id(restaurant_id)
        if not restaurant:
            messagebox.showerror("Error", "Could not find the restaurant for this order.", parent=self)
            return

        # Modern order confirmation dialog
        self.show_order_confirmation_dialog(restaurant, cart)

    def update_user_info(self, user):
        self.user = user
        self.welcome_label.configure(text=f"Welcome, {self.user.username}!")
        self.load_restaurants() # Reload restaurants, in case of user-specific content in future

    def show_profile_panel(self):
        """Show the modern profile popup window with scrollable content"""
        log("show_profile_panel called - showing modern popup window")
        # Destroy previous profile window if exists
        if hasattr(self, 'profile_window') and self.profile_window and self.profile_window.winfo_exists():
            self.profile_window.destroy()
        self.profile_window = ctk.CTkToplevel(self)
        self.profile_window.title("User Profile")
        self.profile_window.geometry("950x900")  # Increased height for more content
        self.profile_window.resizable(False, False)
        set_swigato_icon(self.profile_window)
        self.profile_window.grab_set()  # Make it modal
        # Center the window on screen
        self.profile_window.transient(self.app_ref)
        window_width = 950
        window_height = 900
        screen_width = self.profile_window.winfo_screenwidth()
        screen_height = self.profile_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.profile_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.profile_window.configure(fg_color="white")
        self.profile_window.grid_columnconfigure(0, weight=1)
        self.profile_window.grid_rowconfigure(0, weight=1)
        # Use a scrollable frame for the main content
        main_frame = ctk.CTkScrollableFrame(
            self.profile_window,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#E5E7EB",
            width=910,
            height=860
        )
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Header section with user avatar and name
        header_frame = ctk.CTkFrame(main_frame, fg_color=PRIMARY_COLOR, corner_radius=15)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # User avatar (placeholder)
        avatar_label = ctk.CTkLabel(
            header_frame,
            text="👤",
            font=ctk.CTkFont(size=40),
            text_color="white",
            fg_color="transparent"
        )
        avatar_label.grid(row=0, column=0, padx=(20, 15), pady=20)
        
        # User info
        user_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=20)
        
        self.welcome_label = ctk.CTkLabel(
            user_info_frame,
            text=f"Welcome, {self.user.username}!",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        self.welcome_label.pack(anchor="w")
        
        status_label = ctk.CTkLabel(
            user_info_frame,
            text="🟢 Online",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Close button in header
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#DC2626",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.profile_window.destroy
        )
        close_btn.grid(row=0, column=2, padx=(0, 20), pady=20, sticky="ne")
        # Modern TabView for profile sections with light theme - larger size for no scrolling
        self.profile_tabview = ctk.CTkTabview(
            main_frame,
            width=890,
            height=780,  # Increased height for more content
            fg_color="white",
            segmented_button_fg_color="#F3F4F6",
            segmented_button_selected_color=PRIMARY_COLOR,
            segmented_button_selected_hover_color=BUTTON_HOVER_COLOR,
            text_color="#374151",
            segmented_button_unselected_color="#9CA3AF",
            segmented_button_unselected_hover_color="#D1D5DB"
        )
        self.profile_tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Add tabs
        self.profile_tabview.add("👤 Profile")
        self.profile_tabview.add("🔒 Security") 
        self.profile_tabview.add("⚙️ Settings")
        
        # Set default tab
        self.profile_tabview.set("👤 Profile")
        
        # Setup tab contents
        self.setup_profile_tab()
        self.setup_security_tab()
        self.setup_settings_tab()

    def setup_profile_tab(self):
        """Setup the profile information tab"""
        profile_tab = self.profile_tabview.tab("👤 Profile")
        profile_tab.grid_columnconfigure(0, weight=1)
          # Profile content frame - no scrolling needed with larger window
        content_frame = ctk.CTkFrame(
            profile_tab, 
            fg_color="transparent",
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Account Information Section
        section_label = ctk.CTkLabel(
            content_frame,
            text="📋 Account Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        section_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Username field
        ctk.CTkLabel(
            content_frame,
            text="Username:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.username_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter username",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        self.username_entry.insert(0, self.user.username)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Email field
        ctk.CTkLabel(
            content_frame,
            text="Email:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.email_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter email address",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        current_email = getattr(self.user, 'email', '')
        if current_email and current_email != 'N/A':
            self.email_entry.insert(0, current_email)
        self.email_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Address field
        ctk.CTkLabel(
            content_frame,
            text="Address:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.address_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter your address",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        current_address = getattr(self.user, 'address', '')
        if current_address and current_address != 'N/A':
            self.address_entry.insert(0, current_address)
        self.address_entry.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Phone field
        ctk.CTkLabel(
            content_frame,
            text="Phone:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.phone_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter phone number",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        current_phone = getattr(self.user, 'phone', '')
        if current_phone and current_phone != 'N/A':
            self.phone_entry.insert(0, current_phone)
        self.phone_entry.grid(row=4, column=1, sticky="ew", pady=5)
        
        # Update Profile Button
        update_btn = ctk.CTkButton(
            content_frame,
            text="💾 Update Profile",
            command=self.update_profile_info,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            corner_radius=10
        )
        update_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Account Statistics Section
        stats_label = ctk.CTkLabel(
            content_frame,
            text="📊 Account Statistics",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        stats_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(20, 15))
          # Stats frame with light theme
        stats_frame = ctk.CTkFrame(content_frame, fg_color="#F9FAFB", corner_radius=10, border_width=1, border_color="#E5E7EB")
        stats_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total Orders
        try:
            orders = get_orders_by_user_id(self.user.user_id)
            total_orders = len(orders)
            total_spent = sum(order.total_amount for order in orders)
        except:
            total_orders = 0
            total_spent = 0
        
        # Initialize stat_values dictionary to store references
        self.stat_values = {}
        
        self.create_stat_card(stats_frame, "🛒", "Total Orders", str(total_orders), 0)
        self.create_stat_card(stats_frame, "💰", "Total Spent", f"₹{total_spent:.2f}", 1)
        
        # Store references to the stat values for updating
        self.total_orders_value = self.stat_values.get("Total Orders")
        self.total_spent_value = self.stat_values.get("Total Spent")
        
        # Favorite Restaurants
        fav_restaurants = len(self.user.get_favorite_restaurants())
        self.create_stat_card(stats_frame, "⭐", "Favorites", str(fav_restaurants), 2)

    def create_stat_card(self, parent, icon, label, value, column):
        """Create a statistics card with light theme"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24))
        icon_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        value_label.pack()
        
        # Store reference to value label for updating
        if not hasattr(self, 'stat_values'):
            self.stat_values = {}
        self.stat_values[label] = value_label
        
        label_label = ctk.CTkLabel(
            card, 
            text=label, 
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"  # Gray for light theme
        )
        label_label.pack(pady=(0, 10))

    def setup_security_tab(self):
        """Setup the security/password tab"""
        security_tab = self.profile_tabview.tab("🔒 Security")
        security_tab.grid_columnconfigure(0, weight=1)
          # Security content frame - no scrolling needed with larger window
        content_frame = ctk.CTkFrame(
            security_tab, 
            fg_color="transparent",
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Change Password Section
        section_label = ctk.CTkLabel(
            content_frame,
            text="🔐 Change Password",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        section_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Current Password
        ctk.CTkLabel(
            content_frame,
            text="Current Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.current_pw_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter current password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        self.current_pw_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # New Password
        ctk.CTkLabel(
            content_frame,
            text="New Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.new_pw_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Enter new password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        self.new_pw_entry.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Confirm New Password
        ctk.CTkLabel(
            content_frame,
            text="Confirm Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR        ).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.confirm_pw_entry = ctk.CTkEntry(
            content_frame,
            placeholder_text="Confirm new password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=35,
            fg_color="white",  # Light background
            text_color="#1F2937",  # Dark text
            placeholder_text_color="#9CA3AF",  # Gray placeholder
            border_color="#D1D5DB",  # Light border
            border_width=1
        )
        self.confirm_pw_entry.grid(row=3, column=1, sticky="ew", pady=5)
        
        # Password message label
        self.pw_message_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=SUCCESS_COLOR
        )
        self.pw_message_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Change Password Button
        change_pw_btn = ctk.CTkButton(
            content_frame,
            text="🔒 Change Password",
            command=self.change_password,
            fg_color=SECONDARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            corner_radius=10
        )
        change_pw_btn.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Security Tips Section
        tips_label = ctk.CTkLabel(
            content_frame,
            text="💡 Security Tips",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )        
        tips_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(20, 15))
        
        tips_frame = ctk.CTkFrame(content_frame, fg_color="#F9FAFB", corner_radius=10, border_width=1, border_color="#E5E7EB")
        tips_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        
        tips_text = """
    • Use a strong password with at least 8 characters
    • Include uppercase, lowercase, numbers, and symbols
    • Don't share your password with anyone
    • Log out from shared devices
    • Enable two-factor authentication when available
        """
        
        tips_display = ctk.CTkLabel(
            tips_frame,
            text=tips_text,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_COLOR,
            justify="left"
        )
        tips_display.pack(padx=20, pady=15)

    def setup_settings_tab(self):
        """Setup the settings tab"""
        settings_tab = self.profile_tabview.tab("⚙️ Settings")
        settings_tab.grid_columnconfigure(0, weight=1)
          # Settings content frame - no scrolling needed with larger window
        content_frame = ctk.CTkFrame(
            settings_tab, 
            fg_color="transparent",
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Preferences Section
        prefs_label = ctk.CTkLabel(
            content_frame,
            text="🎨 Preferences",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        prefs_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Theme setting (placeholder for future enhancement)
        ctk.CTkLabel(
            content_frame,
            text="Theme:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.theme_var = ctk.StringVar(value="Light")
        theme_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["Light", "Dark", "Auto"],
            variable=self.theme_var,
            font=ctk.CTkFont(size=14),
            width=200
        )
        theme_menu.grid(row=1, column=1, sticky="w", pady=5)
        
        # Notifications
        ctk.CTkLabel(
            content_frame,
            text="Notifications:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.notifications_var = ctk.BooleanVar(value=True)
        notifications_switch = ctk.CTkSwitch(
            content_frame,
            text="Enable notifications",
            variable=self.notifications_var,
            font=ctk.CTkFont(size=12)
        )
        notifications_switch.grid(row=2, column=1, sticky="w", pady=5)
        
        # Save Preferences Button
        save_prefs_btn = ctk.CTkButton(
            content_frame,
            text="💾 Save Preferences",
            command=self.save_preferences,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            corner_radius=10
        )
        save_prefs_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Account Actions Section
        actions_label = ctk.CTkLabel(
            content_frame,
            text="🚪 Account Actions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        actions_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(20, 15))
        
        # Logout Button
        logout_btn = ctk.CTkButton(
            content_frame,
            text="🚪 Logout",
            command=self.logout_from_profile,
            fg_color=SECONDARY_COLOR,
            hover_color="#B91C1C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            corner_radius=10
        )
        logout_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # App Information Section
        info_label = ctk.CTkLabel(
            content_frame,
            text="ℹ️ App Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        info_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(20, 15))
        
        info_frame = ctk.CTkFrame(content_frame, fg_color=BACKGROUND_COLOR, corner_radius=10)
        info_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        
        app_info = """
🍽️ Swigato Food Delivery App
Version: 1.0.0
Developed with ❤️ using Python & CustomTkinter
        """
        
        info_display = ctk.CTkLabel(
            info_frame,
            text=app_info,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_COLOR,
            justify="center"
        )
        info_display.pack(padx=20, pady=15)

    def update_cart_count_in_nav(self):
        """Update the cart count in the bottom navigation bar with modern styling"""
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            count = self.app_ref.cart.get_total_items()
        else:
            count = 0
        
        # Update the text of the cart button in the bottom navigation
        if 'cart' in self.nav_buttons:
            if count > 0:
                self.nav_buttons['cart'].configure(text=f"🛒({count})")
                # Make cart button more prominent when it has items
                if self.current_nav_tab != "cart":
                    self.nav_buttons['cart'].configure(
                        fg_color=SUCCESS_COLOR,
                        text_color="white"
                    )
            else:
                self.nav_buttons['cart'].configure(text="🛒")
                # Reset to normal style when empty
                if self.current_nav_tab != "cart":
                    self.nav_buttons['cart'].configure(
                        fg_color="transparent",
                        text_color=GRAY_TEXT_COLOR
                    )

    def update_profile_info(self):
        """Update user profile information based on entry fields."""
        new_username = self.username_entry.get()
        new_email = self.email_entry.get()
        new_phone = self.phone_entry.get()
        new_address = self.address_entry.get()

        # Basic validation
        if not new_username or not new_email:
            messagebox.showerror("Error", "Username and email cannot be empty.", parent=self.profile_window)
            return

        # Update user object and database
        try:
            self.user.update_profile(
                username=new_username,
                email=new_email,
                phone_number=new_phone,
                address=new_address
            )
            log(f"User {self.user.user_id} profile updated successfully.")
            self.show_temporary_message("Profile updated successfully!", SUCCESS_COLOR)
            # Refresh welcome label in main screen
            self.welcome_label.configure(text=f"Welcome back, {new_username}! 👋")
            # Refresh profile stats in case username changed
            self.update_profile_stats()

        except Exception as e:
            log(f"Error updating profile for user {self.user.user_id}: {e}")
            messagebox.showerror("Error", f"Failed to update profile: {e}", parent=self.profile_window)

    def change_password(self):
        """Handle password change"""
        current_pw = self.current_pw_entry.get()
        new_pw = self.new_pw_entry.get()
        confirm_pw = self.confirm_pw_entry.get()
        
        # Validate inputs
        if not current_pw or not new_pw or not confirm_pw:
            self.pw_message_label.configure(text="All password fields are required! ❌", text_color=ERROR_COLOR)
            return
        
        if new_pw != confirm_pw:
            self.pw_message_label.configure(text="New passwords do not match! ❌", text_color=ERROR_COLOR)
            return
        
        if not self.user.verify_password(current_pw):
            self.pw_message_label.configure(text="Current password is incorrect! ❌", text_color=ERROR_COLOR)
            return
        
        # Update password
        success = self.user.update_password(new_pw)
        if success:
            self.pw_message_label.configure(text="Password changed successfully! ✅", text_color=SUCCESS_COLOR)
            # Clear password fields
            self.current_pw_entry.delete(0, 'end')
            self.new_pw_entry.delete(0, 'end')
            self.confirm_pw_entry.delete(0, 'end')
        else:
            self.pw_message_label.configure(text="Failed to change password! ❌", text_color=ERROR_COLOR)

    def save_preferences(self):
        """Save user preferences"""
        # Here you would typically save to database or config file
        # For now, just show a success message
        self.show_message("Preferences saved successfully! ✅", SUCCESS_COLOR)

    def logout_from_profile(self):
        """Logout from the profile window"""
        self.profile_window.destroy()
        self.logout_callback()

    def show_message(self, message, color):
        """Show a temporary message in the profile window"""
        if hasattr(self, 'temp_message_label'):
            self.temp_message_label.destroy()
        
        self.temp_message_label = ctk.CTkLabel(
            self.profile_window,
            text=message,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color,
            fg_color="transparent"
        )
        self.temp_message_label.place(relx=0.5, rely=0.95, anchor="center")
          # Remove message after 3 seconds
        self.profile_window.after(3000, lambda: self.temp_message_label.destroy() if hasattr(self, 'temp_message_label') else None)

    def update_profile_stats(self):
        """Update the user statistics in the profile panel."""
        try:
            orders = get_orders_by_user_id(self.user.user_id)
            total_orders = len(orders)
            total_spent = sum(order.total_amount for order in orders)

            # Update the stat values if they exist
            if hasattr(self, 'stat_values') and self.stat_values:
                if "Total Orders" in self.stat_values and self.stat_values["Total Orders"]:
                    self.stat_values["Total Orders"].configure(text=str(total_orders))
                if "Total Spent" in self.stat_values and self.stat_values["Total Spent"]:
                    self.stat_values["Total Spent"].configure(text=f"₹{total_spent:.2f}")
        except Exception as e:
            log(f"Error updating profile stats: {e}")
            # Update with N/A if there's an error and widgets exist
            if hasattr(self, 'stat_values') and self.stat_values:
                if "Total Orders" in self.stat_values and self.stat_values["Total Orders"]:
                    self.stat_values["Total Orders"].configure(text="N/A")
                if "Total Spent" in self.stat_values and self.stat_values["Total Spent"]:
                    self.stat_values["Total Spent"].configure(text="N/A")

    def show_temporary_message(self, message, color):
        """Display a temporary message in the profile window."""
        if not hasattr(self, 'profile_window') or not self.profile_window.winfo_exists():
            return # Don't show message if profile window is closed
            
        temp_label = ctk.CTkLabel(
            self.profile_window, # Anchor to profile window
            text=message,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color,
            fg_color=FRAME_FG_COLOR,
            corner_radius=8
        )
        # Place it at the bottom of the profile window
        temp_label.place(relx=0.5, rely=0.98, anchor="s")
        self.profile_window.after(3000, temp_label.destroy)

    def on_search_change(self, event=None):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.load_restaurants()
            return

        # Filter restaurants by name or cuisine
        filtered_restaurants = [
            r for r in self.restaurants 
            if search_term in r.name.lower() or 
               (r.cuisine_type and search_term in r.cuisine_type.lower())
        ]

        # Filter menu items and get their restaurant IDs
        menu_items = MenuItem.search(search_term)
        restaurant_ids_from_items = {item.restaurant_id for item in menu_items}

        # Combine and de-duplicate
        final_restaurant_ids = set(r.restaurant_id for r in filtered_restaurants) | restaurant_ids_from_items
        
        final_restaurants = [r for r in self.restaurants if r.restaurant_id in final_restaurant_ids]

        self.display_restaurants(final_restaurants)

    def show_filter_options(self):
        # This is a placeholder for a more advanced filter UI
        messagebox.showinfo("Filter", "Filter options coming soon!", parent=self)

    def show_order_confirmation_dialog(self, restaurant, cart):
        """Show a modern order confirmation dialog with address selection."""
        # Create the main dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Order Confirmation")
        dialog.geometry("550x700")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()
        
        # Set Swigato icon
        set_swigato_icon(dialog)
        
        # Center the dialog
        dialog.after(10, lambda: self.center_window(dialog))
        
        # Configure the dialog styling with light theme
        dialog.configure(fg_color="white")
        
        # Main container
        main_frame = ctk.CTkFrame(dialog, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with icon
        header_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=12, border_width=1, border_color="#E5E7EB")
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_icon = ctk.CTkLabel(
            header_frame,
            text="🛒",
            font=ctk.CTkFont(size=36),
            text_color=PRIMARY_COLOR
        )
        header_icon.pack(pady=(15, 5))
        
        header_title = ctk.CTkLabel(
            header_frame,
            text="ORDER CONFIRMATION",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        header_title.pack(pady=(0, 15))
        
        # Order details section
        details_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=12, border_width=1, border_color="#E5E7EB")
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Restaurant info
        restaurant_info = ctk.CTkLabel(
            details_frame,
            text=f"🏪 Restaurant: {restaurant.name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        restaurant_info.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Order summary
        total_items = cart.get_total_items()
        total_price = cart.get_total_price()
        
        items_info = ctk.CTkLabel(
            details_frame,
            text=f"📦 Items: {total_items}",
            font=ctk.CTkFont(size=14),
            text_color="#4B5563"
        )
        items_info.pack(anchor="w", padx=20, pady=2)
        
        price_info = ctk.CTkLabel(
            details_frame,
            text=f"💰 Total Amount: ₹{total_price:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=SUCCESS_COLOR
        )
        price_info.pack(anchor="w", padx=20, pady=(2, 15))
        
        # Delivery address section
        address_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=12, border_width=1, border_color="#E5E7EB")
        address_frame.pack(fill="x", pady=(0, 20))
        
        address_title = ctk.CTkLabel(
            address_frame,
            text="🏠 Delivery Address",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        address_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Address options
        address_var = ctk.StringVar()
        
        # Option 1: Use saved address (if available)
        if self.user.address and self.user.address.strip():
            saved_address_radio = ctk.CTkRadioButton(
                address_frame,
                text=f"Use saved address: {self.user.address}",
                variable=address_var,
                value="saved",
                font=ctk.CTkFont(size=14),
                text_color="#1F2937",
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR
            )
            saved_address_radio.pack(anchor="w", padx=30, pady=5)
            address_var.set("saved")  # Default to saved address
        
        # Option 2: Enter new address
        new_address_radio = ctk.CTkRadioButton(
            address_frame,
            text="Enter new address:",
            variable=address_var,
            value="new",
            font=ctk.CTkFont(size=14),
            text_color="#1F2937",
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        new_address_radio.pack(anchor="w", padx=30, pady=(5, 10))
        
        # If no saved address, default to new address
        if not self.user.address or not self.user.address.strip():
            address_var.set("new")
        
        # New address input
        address_entry = ctk.CTkTextbox(
            address_frame,
            height=80,
            font=ctk.CTkFont(size=14),
            fg_color="white",
            text_color="#1F2937",
            border_width=2,
            border_color="#D1D5DB",
            corner_radius=8
        )
        address_entry.pack(fill="x", padx=30, pady=(0, 10))
        address_entry.insert("0.0", "Enter your delivery address here...")
        
        # Save new address option
        save_address_var = ctk.BooleanVar(value=True)
        save_address_check = ctk.CTkCheckBox(
            address_frame,
            text="Save this address for future orders",
            variable=save_address_var,
            font=ctk.CTkFont(size=12),
            text_color="#4B5563",
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            checkmark_color="white"
        )
        save_address_check.pack(anchor="w", padx=30, pady=(0, 15))
        
        # Estimated delivery time
        delivery_info = ctk.CTkLabel(
            address_frame,
            text="⏰ Estimated delivery: 30-45 minutes",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        )
        delivery_info.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", pady=(0, 10))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancel",
            width=140,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="white",
            text_color=ERROR_COLOR,
            hover_color="#FEF2F2",
            border_width=2,
            border_color=ERROR_COLOR,
            corner_radius=10,
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        # Place order button
        place_order_btn = ctk.CTkButton(
            buttons_frame,
            text="🎉 Place Order",
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=SUCCESS_COLOR,
            hover_color="#16A34A",
            text_color="white",
            corner_radius=10,
            command=lambda: self.place_order_from_dialog(
                dialog, restaurant, cart, address_var, address_entry, save_address_var
            )
        )
        place_order_btn.pack(side="right")
        
        # Focus management
        def on_address_option_change():
            if address_var.get() == "new":
                address_entry.focus()
                if address_entry.get("0.0", "end-1c").strip() == "Enter your delivery address here...":
                    address_entry.delete("0.0", "end")
        
        new_address_radio.configure(command=on_address_option_change)
        
        # Clear placeholder text on focus
        def on_entry_focus(event):
            if address_entry.get("0.0", "end-1c").strip() == "Enter your delivery address here...":
                address_entry.delete("0.0", "end")
        
        address_entry.bind("<FocusIn>", on_entry_focus)
    
    def place_order_from_dialog(self, dialog, restaurant, cart, address_var, address_entry, save_address_var):
        """Handle order placement from the confirmation dialog."""
        # Determine delivery address
        if address_var.get() == "saved" and self.user.address and self.user.address.strip():
            delivery_address = self.user.address
        else:
            # Get address from text entry
            new_address = address_entry.get("0.0", "end-1c").strip()
            if not new_address or new_address == "Enter your delivery address here...":
                messagebox.showerror(
                    "Address Required", 
                    "Please enter a delivery address or select your saved address.",
                    parent=dialog
                )
                return
            delivery_address = new_address
            
            # Save address if requested
            if save_address_var.get():
                success = self.user.update_address(delivery_address)
                if success:
                    log(f"User {self.user.username} updated their address to: {delivery_address}")
        
        # Close dialog before proceeding
        dialog.destroy()
        
        # Place the order
        try:
            order = create_order(
                user_id=self.user.user_id,
                restaurant_id=restaurant.restaurant_id,
                restaurant_name=restaurant.name,
                cart_items=list(cart.items.values()),
                total_amount=cart.get_total_price(),
                user_address=delivery_address
            )
            
            if order:
                log(f"Order {order.order_id} created successfully for user {self.user.username}.")
                messagebox.showinfo(
                    "Order Placed Successfully!", 
                    f"🎉 Your order has been placed!\n\n"
                    f"Order ID: {order.order_id}\n"
                    f"Restaurant: {restaurant.name}\n"
                    f"Total: ₹{cart.get_total_price():.2f}\n"
                    f"Delivery to: {delivery_address}\n\n"
                    f"Estimated delivery: 30-45 minutes",
                    parent=self
                )
                
                # Clear cart and refresh UI
                self.app_ref.cart.clear_cart()
                self.update_cart_count_in_nav()
                self.load_cart_items()
                self.load_order_history()
                self.update_profile_stats()
                self.show_orders_content()
                self.set_active_nav_tab('orders')
            else:
                messagebox.showerror(
                    "Order Failed", 
                    "❌ There was an issue placing your order. Please try again.",
                    parent=self
                )
        except Exception as e:
            log(f"Error during checkout: {e}")
            messagebox.showerror(
                "Error", 
                f"❌ An unexpected error occurred: {e}",
                parent=self
            )
    
    def center_window(self, window):
        """Center a window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
