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
        self.grid_rowconfigure(2, weight=0)  # Bottom nav bar        # --- Modern Header Frame with Enhanced Styling ---
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
          # --- Enhanced Main Content Area ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.main_content_frame.grid(row=1, column=0, padx=30, pady=(10, 15), sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Initialize content areas
        self.setup_content_areas()
          # Show restaurants by default
        self.show_restaurants_content()        # --- Bottom Navigation Bar ---
        self.create_bottom_nav_bar()

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

        self.favorites_scroll_frame = ctk.CTkScrollableFrame(
            self.favorites_content_frame, 
            fg_color=BACKGROUND_COLOR, 
            corner_radius=0, 
            border_width=0
        )
        self.favorites_scroll_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.favorites_scroll_frame.grid_columnconfigure(0, weight=1)

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
        self.load_favorites()

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
        log("MainAppScreen.load_restaurants called")        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()

        self.restaurants = Restaurant.get_all()
        log(f"Loaded {len(self.restaurants)} restaurants.")

        if not self.restaurants:
            no_restaurants_label = ctk.CTkLabel(self.restaurant_scroll_frame,
                                                text="No restaurants available at the moment.",
                                                text_color=TEXT_COLOR,
                                                font=ctk.CTkFont(size=16))
            no_restaurants_label.grid(row=0, column=0, pady=20)
            return

        for i, restaurant in enumerate(self.restaurants):
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
                    font=ctk.CTkFont(size=40),
                    corner_radius=16
                )
                image_label.pack()

            # Enhanced details section with modern typography
            details_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, rowspan=3, padx=(15, 20), pady=25, sticky="nsew")
            details_frame.grid_columnconfigure(0, weight=1)

            # Restaurant name with enhanced typography
            name_label = ctk.CTkLabel(
                details_frame, 
                text=restaurant.name,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=TEXT_COLOR, 
                anchor="w"
            )
            name_label.grid(row=0, column=0, pady=(0, 8), sticky="ew")            
            
            # Modern cuisine tag with pill-style design
            cuisine_container = ctk.CTkFrame(details_frame, fg_color="transparent")
            cuisine_container.grid(row=1, column=0, pady=(0, 8), sticky="ew")
            cuisine_container.grid_columnconfigure(0, weight=0)
            cuisine_container.grid_columnconfigure(1, weight=1)
            
            cuisine_tag = ctk.CTkFrame(
                cuisine_container,
                fg_color=LIGHT_ORANGE_BG,  # Light orange background
                corner_radius=12,
                height=24
            )
            cuisine_tag.grid(row=0, column=0, sticky="w")
            cuisine_tag.pack_propagate(False)
            
            cuisine_label = ctk.CTkLabel(
                cuisine_tag,
                text=f"🍴 {restaurant.cuisine_type}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=PRIMARY_COLOR
            )
            cuisine_label.pack(padx=12, pady=2)

            # Enhanced rating with star display and modern styling
            rating_container = ctk.CTkFrame(details_frame, fg_color="transparent")
            rating_container.grid(row=2, column=0, sticky="ew")
            rating_container.grid_columnconfigure(0, weight=0)
            rating_container.grid_columnconfigure(1, weight=1)
            
            # Improved star rating
            stars_filled = int(restaurant.rating)
            stars_text = "⭐" * stars_filled + "☆" * (5 - stars_filled)
            stars_label = ctk.CTkLabel(
                rating_container, 
                text=stars_text,
                font=ctk.CTkFont(size=16),
                text_color="#FFD700"
            )
            stars_label.grid(row=0, column=0, padx=(0, 12))
            
            # Show "No reviews yet" for restaurants with 0 reviews, otherwise show rating and count
            review_count = restaurant.get_review_count()
            if review_count == 0:
                rating_text = "No reviews yet"
            else:
                rating_text = f"{restaurant.rating:.1f} • {review_count} review{'s' if review_count != 1 else ''}"
            
            rating_label = ctk.CTkLabel(
                rating_container, 
                text=rating_text,
                font=ctk.CTkFont(size=13),
                text_color=GRAY_TEXT_COLOR, 
                anchor="w"
            )
            rating_label.grid(row=0, column=1, sticky="w")

            # Ultra-modern actions column
            actions_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            actions_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=25, sticky="ns")
            actions_frame.grid_rowconfigure(0, weight=1)
            actions_frame.grid_rowconfigure(1, weight=0)
            actions_frame.grid_rowconfigure(2, weight=1)            # Modern favorite button with enhanced styling and clear visual states
            is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
            heart_button = ctk.CTkButton(
                actions_frame, 
                text="♥",  # Use solid heart symbol for both states
                width=45, 
                height=45,
                fg_color="#FFE4E6" if is_fav else FRAME_FG_COLOR,  # Light pink background
                hover_color="#FECACA" if is_fav else "#FEF2F2",
                text_color="#DC2626" if is_fav else "#9CA3AF",  # Red when favorited, gray when not
                font=ctk.CTkFont(size=18, weight="bold"),
                corner_radius=22,
                border_width=2,
                border_color="#DC2626" if is_fav else "#E5E7EB",  # Red border when favorited, gray when not
                command=lambda r=restaurant, b=None: self._toggle_favorite_restaurant(r, b)
            )
            heart_button.grid(row=0, column=0, pady=(0, 15))
            heart_button.configure(command=lambda r=restaurant, b=heart_button: self._toggle_favorite_restaurant(r, b))

            # Ultra-modern View Menu button with enhanced styling
            view_menu_button = ctk.CTkButton(
                actions_frame, 
                text="View Menu",
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                width=130,
                height=50,
                corner_radius=25,
                border_width=0,
                command=lambda r=restaurant: self.show_menu_callback(r)
            )
            view_menu_button.grid(row=2, column=0)

    def _toggle_favorite_restaurant(self, restaurant, button=None):
        is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        if is_fav:
            self.user.remove_favorite_restaurant(restaurant.restaurant_id)
        else:
            self.user.add_favorite_restaurant(restaurant.restaurant_id)
        
        # Update button appearance with clear visual states
        new_is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        if button:  # Only update button if one is provided
            if new_is_fav:
                # Favorited state: light pink background, red heart and border
                button.configure(
                    fg_color="#FFE4E6",
                    text_color="#DC2626",
                    border_color="#DC2626",
                    hover_color="#FECACA"
                )
            else:
                # Not favorited state: transparent background, gray heart and border
                button.configure(                    fg_color="transparent",                    text_color="#9CA3AF",
                    border_color="#E5E7EB",
                    hover_color="#FEF2F2"
                )

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
        
        self.create_stat_card(stats_frame, "🛒", "Total Orders", str(total_orders), 0)
        self.create_stat_card(stats_frame, "💰", "Total Spent", f"₹{total_spent:.2f}", 1)
        
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

    def on_search_change(self, event=None):
        """Handle search input changes with debouncing"""
        # Debounce mechanism: wait for user to stop typing
        if hasattr(self, 'search_job'):
            self.after_cancel(self.search_job)
        
        self.search_job = self.after(500, self.perform_search)

    def perform_search(self):
        """Perform the actual search for restaurants and menu items"""
        search_term = self.search_entry.get().strip().lower()
        
        # If search term is empty, load all restaurants
        if not search_term:
            self.load_restaurants()
            return
            
        # Search both restaurant names and menu items
        restaurants_by_name = Restaurant.search_by_name(search_term)
        restaurants_with_items, menu_items = Restaurant.search_by_menu_item(search_term)
        
        # Combine results, avoiding duplicates
        restaurant_ids = set(r.restaurant_id for r in restaurants_by_name)
        combined_restaurants = list(restaurants_by_name)
        
        for r, items in restaurants_with_items:
            if r.restaurant_id not in restaurant_ids:
                restaurant_ids.add(r.restaurant_id)
                combined_restaurants.append(r)
                
        # Sort combined results by name
        combined_restaurants.sort(key=lambda r: r.name)
        
        # Display results with highlights for menu items
        self.display_restaurants_with_highlights(combined_restaurants, restaurants_with_items, search_term)

    def show_filter_options(self):
        """Show filter options popup menu"""
        # This is a placeholder for a more advanced filter menu
        messagebox.showinfo("Filter", "Filter options are not yet implemented.")

    def update_cart_count_in_nav(self):
        """Update the cart count in the bottom navigation bar"""
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            count = self.app_ref.cart.get_total_items()
        else:
            count = 0
        
        # Update the text of the cart button in the bottom navigation
        if 'cart' in self.nav_buttons:
            self.nav_buttons['cart'].configure(text=f"🛒 Cart ({count})")

    def update_profile_info(self):
        """Update user profile information"""
        try:
            # Get values from entries
            new_username = self.username_entry.get().strip()
            new_email = self.email_entry.get().strip()
            new_address = self.address_entry.get().strip()
            new_phone = self.phone_entry.get().strip()
            
            # Validate required fields
            if not new_username:
                self.show_message("Username cannot be empty!", ERROR_COLOR)
                return
            
            # Update user object using the model methods
            success = True
            
            # Update username if changed
            if new_username != self.user.username:
                if not self.user.update_username(new_username):
                    success = False
            
            # Update email if changed
            if new_email != getattr(self.user, 'email', ''):
                if not self.user.update_email(new_email if new_email else None):
                    success = False
            
            # Update address if changed
            if new_address != getattr(self.user, 'address', ''):
                if not self.user.update_address(new_address if new_address else None):
                    success = False
            
            # Update phone if changed
            if new_phone != getattr(self.user, 'phone', ''):
                if not self.user.update_phone(new_phone if new_phone else None):
                    success = False
            
            if success:
                # Update the welcome label in main screen
                self.welcome_label.configure(text=f"Welcome back, {self.user.username}! 👋")
                self.show_message("Profile updated successfully! ✅", SUCCESS_COLOR)
            else:
                self.show_message("Some updates failed! Please try again. ❌", ERROR_COLOR)
                
        except Exception as e:
            log(f"Error updating profile: {e}")
            self.show_message("Failed to update profile! ❌", ERROR_COLOR)

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

    def load_favorites(self):
        """Load and display favorite restaurants and menu items with modern design"""
        # Clear existing widgets
        for widget in self.favorites_scroll_frame.winfo_children():
            widget.destroy()

        # Get favorites
        fav_restaurants = self.user.get_favorite_restaurants()
        fav_menu_items = self.user.get_favorite_menu_items()

        row = 0

        # Modern empty state
        if not fav_restaurants and not fav_menu_items:
            empty_frame = ctk.CTkFrame(
                self.favorites_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            empty_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="⭐",
                font=ctk.CTkFont(size=48),
                text_color=GRAY_TEXT_COLOR
            )
            empty_icon.pack(pady=(30, 10))
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No favorites yet!",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR
            )
            empty_label.pack(pady=(0, 5))
            
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Start exploring restaurants and add your favorites\nto see them here.",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                justify="center"
            )
            empty_desc.pack(pady=(0, 30))
            return

        # Favorite Restaurants Section
        if fav_restaurants:
            section_header = ctk.CTkLabel(
                self.favorites_scroll_frame,
                text="🏪 Favorite Restaurants",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            section_header.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 10))
            row += 1

            for rest in fav_restaurants:
                rest_card = ctk.CTkFrame(
                    self.favorites_scroll_frame,
                    fg_color=FRAME_FG_COLOR,
                    corner_radius=12,
                    border_width=1,
                    border_color=FRAME_BORDER_COLOR
                )
                rest_card.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
                rest_card.grid_columnconfigure(0, weight=1)
                rest_card.grid_columnconfigure(1, weight=0)
                
                # Restaurant info
                info_frame = ctk.CTkFrame(rest_card, fg_color="transparent")
                info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
                
                rest_label = ctk.CTkLabel(
                    info_frame,
                    text=f"🍽️ {rest.name}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=TEXT_COLOR,
                    anchor="w"
                )
                rest_label.pack(anchor="w")
                
                # Add cuisine type if available
                if hasattr(rest, 'cuisine_type') and rest.cuisine_type:
                    rest_label = ctk.CTkLabel(
                        info_frame,
                        text=f"🍽️ {rest.name}",
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=TEXT_COLOR,
                        anchor="w"
                    )
                    rest_label.pack(anchor="w")
                
                # Add cuisine type if available
                if hasattr(rest, 'cuisine_type') and rest.cuisine_type:
                    cuisine_label = ctk.CTkLabel(
                        info_frame,
                        text=f"🍴 {rest.cuisine_type}",
                        font=ctk.CTkFont(size=12),
                        text_color=GRAY_TEXT_COLOR,
                        anchor="w"
                    )
                    cuisine_label.pack(anchor="w", pady=(2, 0))
                
                # View Menu button
                view_menu_btn = ctk.CTkButton(
                    rest_card,
                    text="View Menu",
                    command=lambda r=rest: self.show_menu_callback(r),
                    fg_color=PRIMARY_COLOR,
                    hover_color=BUTTON_HOVER_COLOR,
                    text_color="white",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=100,
                    height=35,
                    corner_radius=8
                )
                view_menu_btn.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="e")
                row += 1

        # Favorite Menu Items Section
        if fav_menu_items:
            section_header = ctk.CTkLabel(
                self.favorites_scroll_frame,
                text="🍕 Favorite Dishes",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            section_header.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 10))
            row += 1

            for item in fav_menu_items:
                item_card = ctk.CTkFrame(
                    self.favorites_scroll_frame,
                    fg_color=FRAME_FG_COLOR,
                    corner_radius=12,
                    border_width=1,
                    border_color=FRAME_BORDER_COLOR
                )
                item_card.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
                item_card.grid_columnconfigure(0, weight=1)
                item_card.grid_columnconfigure(1, weight=0)
                
                # Item info
                info_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                info_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
                
                item_label = ctk.CTkLabel(
                    info_frame,
                    text=f"🍽️ {item.name}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=TEXT_COLOR,
                    anchor="w"
                )
                item_label.pack(anchor="w")
                
                price_label = ctk.CTkLabel(
                    info_frame,
                    text=f"💰 ₹{item.price}",
                    font=ctk.CTkFont(size=12),
                    text_color=GRAY_TEXT_COLOR,
                    anchor="w"
                )
                price_label.pack(anchor="w", pady=(2, 0))
                
                # Add to Cart button
                add_to_cart_btn = ctk.CTkButton(
                    item_card,
                    text="Add to Cart",
                    command=lambda i=item: self.add_to_cart_from_favorites(i),
                    fg_color=SUCCESS_COLOR,
                    hover_color="#388E3C",
                    text_color="white",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=100,
                    height=35,
                    corner_radius=8
                )
                add_to_cart_btn.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="e")
                row += 1

    def display_restaurants_with_highlights(self, restaurants, restaurants_with_items, search_term):
        """Display restaurants with highlighting for menu item matches"""
        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()
            
        if not restaurants:
            no_restaurants_label = ctk.CTkLabel(self.restaurant_scroll_frame,
                                                text="No restaurants available at the moment.",
                                                text_color=TEXT_COLOR,
                                                font=ctk.CTkFont(size=16))
            no_restaurants_label.grid(row=0, column=0, pady=20)
            return

        # Create a dict for quick lookup of restaurants with matching items
        restaurants_with_matching_items = {r[0].restaurant_id: r[1] for r in restaurants_with_items}

        for i, restaurant in enumerate(restaurants):
            # Create modern restaurant card with enhanced visual design
            restaurant_card = ctk.CTkFrame(
                self.restaurant_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                border_color=FRAME_BORDER_COLOR,
                border_width=1,
                corner_radius=16,
                height=200
            )
            restaurant_card.grid(row=i, column=0, padx=10, pady=(0, 15), sticky="ew")
            restaurant_card.grid_columnconfigure(0, weight=0)  # Image
            restaurant_card.grid_columnconfigure(1, weight=1)  # Content
            restaurant_card.grid_columnconfigure(2, weight=0)  # Actions
            restaurant_card.grid_propagate(False)

            # Restaurant Image section
            image_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            image_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

            # Load and display restaurant image
            if restaurant.image_filename:
                project_root = self.app_ref.project_root
                image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
                ctk_image = load_image(image_path, size=(140, 140))
                if ctk_image:
                    image_label = ctk.CTkLabel(image_frame, image=ctk_image, text="", corner_radius=12)
                    image_label.pack()
                else:
                    # Fallback placeholder
                    image_label = ctk.CTkLabel(image_frame, text="🍽️", font=ctk.CTkFont(size=48), 
                                             width=140, height=140, fg_color=GRAY_TEXT_COLOR, 
                                             text_color=BUTTON_TEXT_COLOR, corner_radius=12)
                    image_label.pack()
            else:
                # Default placeholder
                image_label = ctk.CTkLabel(image_frame, text="🍽️", font=ctk.CTkFont(size=48), 
                                         width=140, height=140, fg_color=GRAY_TEXT_COLOR, 
                                         text_color=BUTTON_TEXT_COLOR, corner_radius=12)
                image_label.pack()

            # Restaurant Details section
            details_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
            details_frame.grid_columnconfigure(0, weight=1)

            # Restaurant name with enhanced typography
            name_label = ctk.CTkLabel(
                details_frame, 
                text=restaurant.name,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            name_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))

            # Cuisine type with modern badge design
            cuisine_frame = ctk.CTkFrame(details_frame, fg_color=PRIMARY_COLOR, corner_radius=8, height=28)
            cuisine_frame.grid(row=1, column=0, sticky="w", pady=(0, 12))
            cuisine_frame.grid_propagate(False)
            
            cuisine_label = ctk.CTkLabel(
                cuisine_frame, 
                text=restaurant.cuisine_type,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            cuisine_label.pack(padx=12, pady=6)

            # Restaurant rating with star display
            rating_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            rating_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))

            review_count = restaurant.get_review_count()
            if review_count == 0:
                rating_text = "No reviews yet"
                rating_color = GRAY_TEXT_COLOR
            else:
                # Create star display
                full_stars = int(restaurant.rating)
                half_star = restaurant.rating - full_stars >= 0.5
                stars = "★" * full_stars + ("⭐" if half_star else "") + "☆" * (5 - full_stars - (1 if half_star else 0))
                rating_text = f"{stars} {restaurant.rating:.1f} ({review_count} review{'s' if review_count != 1 else ''})"
               
                rating_color = PRIMARY_COLOR

            rating_label = ctk.CTkLabel(
                rating_frame, 
                text=rating_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=rating_color,
                anchor="w"
            )
            rating_label.pack(side="left")

            # Check if this restaurant has matching menu items and show them
            if restaurant.restaurant_id in restaurants_with_matching_items:
                matching_items = restaurants_with_matching_items[restaurant.restaurant_id]
                
                # Add a highlighted section for matching menu items
                items_frame = ctk.CTkFrame(details_frame, fg_color="#FFF3CD", corner_radius=8, border_width=1, border_color="#FFE69C")
                items_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))
                
                items_label = ctk.CTkLabel(
                    items_frame,
                    text=f"🍴 Found: {', '.join([item.name for item in matching_items[:3]])}{'...' if len(matching_items) > 3 else ''}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#856404",
                    anchor="w"
                )
                items_label.pack(padx=10, pady=6, fill="x")

            # Action buttons section
            action_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            action_frame.grid(row=0, column=2, padx=20, pady=20, sticky="ns")

            # Heart/Favorite button with improved feedback
            is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
            heart_button = ctk.CTkButton(
                action_frame,
                text="♥" if is_fav else "♡",
                width=50,
                height=50,
                fg_color=ERROR_COLOR if is_fav else FRAME_FG_COLOR,
                text_color="white" if is_fav else ERROR_COLOR,
                font=ctk.CTkFont(size=24),
                hover_color=BUTTON_HOVER_COLOR,
                corner_radius=25,
                border_width=2 if not is_fav else 0,
                border_color=ERROR_COLOR if not is_fav else ERROR_COLOR,
                command=lambda r=restaurant: self._toggle_favorite_restaurant(r)
            )
            heart_button.grid(row=0, column=0, pady=(0, 12))

            # View Menu button with modern design
            view_menu_button = ctk.CTkButton(
                action_frame,
                text="View Menu →",
                width=120,
                height=45,
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=12,
                command=lambda r=restaurant: self.show_menu_callback(r)
            )
            view_menu_button.grid(row=1, column=0)

    def proceed_to_checkout(self):
        """Handle checkout process within the main app"""
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart and self.app_ref.cart.items:
            # Show checkout dialog within the main app instead of redirecting
            self.show_checkout_dialog()
        else:
            # Show message if cart is empty
            messagebox.showinfo("Empty Cart", "Your cart is empty! Add some items before checkout.")

    def show_checkout_dialog(self):
        """Show checkout dialog within the main app"""
        # Create checkout dialog window
        checkout_window = ctk.CTkToplevel(self)
        checkout_window.title("Checkout")
        checkout_window.geometry("600x500")
        checkout_window.resizable(False, False)
        checkout_window.grab_set()  # Make it modal
        
        # Center the window
        screen_width = checkout_window.winfo_screenwidth()
        screen_height = checkout_window.winfo_screenheight()
        center_x = int(screen_width/2 - 300)
        center_y = int(screen_height/2 - 250)
        checkout_window.geometry(f"600x500+{center_x}+{center_y}")
        
        # Configure window with light theme
        checkout_window.configure(fg_color="white")
        checkout_window.grid_columnconfigure(0, weight=1)
        checkout_window.grid_rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(checkout_window, fg_color="white", corner_radius=0)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text="🛒 Checkout",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        header_label.grid(row=0, column=0, pady=(0, 20))
        
        # Order summary
        summary_frame = ctk.CTkFrame(main_frame, fg_color="#F9FAFB", corner_radius=10)
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        summary_frame.grid_columnconfigure(0, weight=1)
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text="📋 Order Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR
        )
        summary_label.grid(row=0, column=0, pady=(15, 10))
        
        # Display cart items
        for i, (item_id, cart_item) in enumerate(self.app_ref.cart.items.items()):
            item_label = ctk.CTkLabel(
                summary_frame,
                text=f"• {cart_item.menu_item.name} x{cart_item.quantity} = ₹{cart_item.item_total:.2f}",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_COLOR
            )
            item_label.grid(row=i+1, column=0, sticky="w", padx=20, pady=2)
        
        # Total amount
        total_amount = self.app_ref.cart.get_total_price()
        total_label = ctk.CTkLabel(
            summary_frame,
            text=f"💰 Total Amount: ₹{total_amount:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        total_label.grid(row=len(self.app_ref.cart.items)+1, column=0, pady=15)
        
        # Delivery address section
        address_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        address_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        address_frame.grid_columnconfigure(1, weight=1)
        
        address_label = ctk.CTkLabel(
            address_frame,
            text="📍 Delivery Address:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        address_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.checkout_address_entry = ctk.CTkEntry(
            address_frame,
            placeholder_text="Enter your delivery address",
            font=ctk.CTkFont(size=14),
            height=40,
            width=400
        )
        self.checkout_address_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=checkout_window.destroy,
            fg_color=SECONDARY_COLOR,
            hover_color="#B91C1C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=40,
            corner_radius=10
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Place Order button
        place_order_btn = ctk.CTkButton(
            buttons_frame,
            text="Place Order",
            command=lambda: self.place_order(checkout_window),
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=40,
            corner_radius=10
        )
        place_order_btn.grid(row=0, column=1, padx=(10, 0))

    def place_order(self, checkout_window):
        """Place the order"""
        # Prevent multiple order placements by disabling the window
        if not checkout_window.winfo_exists():
            return
            
        delivery_address = self.checkout_address_entry.get().strip()
        
        if not delivery_address:
            messagebox.showerror("Missing Address", "Please enter a delivery address!")
            return
        
        try:
            # Disable window interaction during order placement
            checkout_window.grab_release()
            checkout_window.withdraw()  # Hide the window immediately
            
            cart = self.app_ref.cart
            if not cart or not cart.items:
                messagebox.showerror("Empty Cart", "Cannot place an order with an empty cart.")
                checkout_window.destroy()
                return

            # Assuming all items in the cart are from the same restaurant
            first_item = next(iter(cart.items.values()))
            restaurant_id = first_item.menu_item.restaurant_id
            restaurant = Restaurant.get_by_id(restaurant_id)
            restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"

            # Create the order
            order = create_order(
                user_id=self.user.user_id,
                restaurant_id=restaurant_id,
                restaurant_name=restaurant_name,
                cart_items=cart.get_items_for_order(),
                total_amount=cart.get_total_price(),
                user_address=delivery_address
            )

            if order:
                messagebox.showinfo("Order Placed!", f"Your order #{order.order_id} has been placed successfully!\n\nDelivery Address: {delivery_address}\n\nThank you for using Swigato!")
                
                # Clear the cart after successful order
                cart.clear_cart()
                self.load_cart_items()  # Refresh cart display
                self.load_order_history() # Refresh order history
                self.update_profile_stats() # Refresh profile stats
            else:
                messagebox.showerror("Order Failed", "There was an issue placing your order. Please try again.")

            # Close checkout window safely
            if checkout_window.winfo_exists():
                checkout_window.destroy()
            
        except Exception as e:
            log(f"Error placing order: {e}")
            # Restore window if there's an error
            if checkout_window.winfo_exists():
                checkout_window.deiconify()
                checkout_window.grab_set()
            messagebox.showerror("Order Failed", f"Failed to place order: {str(e)}")

    def update_profile_stats(self):
        """Update the statistics on the profile page after an order."""
        # This is a simplified way to trigger an update.
        # A more robust solution might involve a direct update of the labels.
        if hasattr(self, 'profile_window') and self.profile_window.winfo_exists():
            # If profile window is open, refresh its contents
            self.setup_profile_tab()

    def load_cart_items(self):
        """Load and display cart items in the cart content area"""
        # Clear existing widgets
        for widget in self.cart_scroll_frame.winfo_children():
            widget.destroy()

        # Update navigation cart count
        self.update_cart_count_in_nav()

        # Check if cart exists and has items
        if not hasattr(self.app_ref, 'cart') or not self.app_ref.cart or not self.app_ref.cart.items:
            # Modern empty state
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
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR
            )
            empty_label.pack(pady=(0, 5))
            
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Browse restaurants and add items to your cart\nto see them here.",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                justify="center"
            )
            empty_desc.pack(pady=(0, 30))
            return        # Display cart items
        cart_items = self.app_ref.cart.items
        total_amount = 0
        
        for i, cart_item in enumerate(cart_items.values()):
            menu_item = cart_item.menu_item
            quantity = cart_item.quantity
            item_total = menu_item.price * quantity
            total_amount += item_total
            
            item_card = ctk.CTkFrame(
                self.cart_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=12,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            item_card.grid(row=i, column=0, pady=(0, 10), padx=20, sticky="ew")
            item_card.grid_columnconfigure(0, weight=1)
            item_card.grid_columnconfigure(1, weight=0)
            item_card.grid_columnconfigure(2, weight=0)

            # Item details
            details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            details_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
            
            item_label = ctk.CTkLabel(
                details_frame,
                text=f"🍽️ {menu_item.name}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            item_label.pack(anchor="w")
            
            price_label = ctk.CTkLabel(
                details_frame,
                text=f"💰 ₹{menu_item.price} x {quantity} = ₹{item_total}",
                font=ctk.CTkFont(size=12),
                text_color=GRAY_TEXT_COLOR,
                anchor="w"
            )
            price_label.pack(anchor="w", pady=(2, 0))

            # Quantity controls
            qty_frame = ctk.CTkFrame(item_card, fg_color="transparent")
            qty_frame.grid(row=0, column=1, padx=(0, 10), pady=15)
            
            qty_label = ctk.CTkLabel(
                qty_frame,
                text=f"Qty: {quantity}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT_COLOR
            )
            qty_label.pack()

            # Remove button
            remove_btn = ctk.CTkButton(
                item_card,
                text="Remove",
                command=lambda item=menu_item: self.remove_from_cart(item),
                fg_color=SECONDARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=80,
                height=30,
                corner_radius=8
            )
            remove_btn.grid(row=0, column=2, padx=(0, 20), pady=15)

        # Total amount section
        total_frame = ctk.CTkFrame(
            self.cart_scroll_frame,
            fg_color=PRIMARY_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        total_frame.grid(row=len(cart_items), column=0, pady=(20, 10), padx=20, sticky="ew")
        
        total_label = ctk.CTkLabel(
            total_frame,
            text=f"🛒 Total Amount: ₹{total_amount}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        total_label.pack(pady=15)        # Checkout button
        checkout_btn = ctk.CTkButton(
            self.cart_scroll_frame,
            text="Proceed to Checkout",
            command=self.proceed_to_checkout,  # Use internal checkout method
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=40,
            corner_radius=12
        )
        checkout_btn.grid(row=len(cart_items) + 1, column=0, pady=(10, 20))

    def get_status_color(self, status):
        """Get color for order status (Bootstrap-inspired palette)"""
        status_colors = {
            'pending confirmation': '#DC3545',   # Red
            'preparing': '#FFC107',             # Orange
            'confirmed': '#17A2B8',             # Teal/Light Blue
            'out for delivery': '#2ECC71',      # Bright Green
            'delivered': '#008000',             # Darker Green
            'cancelled': '#6C757D',             # Muted Grey
            'failed': '#A50000'                 # Dark Red
        }
        return status_colors.get(status.lower(), '#757575')  # Default gray

    def add_to_cart_from_favorites(self, menu_item):
        """Add a menu item to cart from favorites"""
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:            # Set the current_restaurant to the menu item's restaurant if available
            if hasattr(menu_item, 'restaurant_id') and menu_item.restaurant_id:
                rest_obj = Restaurant.get_by_id(menu_item.restaurant_id)
                if rest_obj:
                    self.app_ref.current_restaurant = rest_obj
            
            # Add item to cart
            added = self.app_ref.cart.add_item(menu_item, 1)
            if added:
                # Show success message
                success_label = ctk.CTkLabel(
                    self.favorites_scroll_frame,
                    text=f"✅ '{menu_item.name}' added to cart!",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=SUCCESS_COLOR
                )
                success_label.grid(row=999, column=0, pady=10)
                # Remove the message after 3 seconds
                self.after(3000, lambda: success_label.destroy() if success_label.winfo_exists() else None)
            else:
                # Show error message
                error_label = ctk.CTkLabel(
                    self.favorites_scroll_frame,
                    text=f"❌ Failed to add '{menu_item.name}' to cart",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=ERROR_COLOR
                )
                error_label.grid(row=999, column=0, pady=10)
                # Remove the message after 3 seconds
                self.after(3000, lambda: error_label.destroy() if error_label.winfo_exists() else None)
        else:
            # Show error - cart not available
            error_label = ctk.CTkLabel(
                self.favorites_scroll_frame,
                text="❌ Cart not available",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=ERROR_COLOR
            )
            error_label.grid(row=999, column=0, pady=10)
            # Remove the message after 3 seconds
            self.after(3000, lambda: error_label.destroy() if error_label.winfo_exists() else None)

    def remove_from_cart(self, menu_item):
        """Remove an item from the cart"""
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            self.app_ref.cart.remove_item(menu_item.item_id)
            # Refresh cart display
            self.load_cart_items()
