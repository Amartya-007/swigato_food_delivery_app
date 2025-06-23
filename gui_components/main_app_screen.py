import customtkinter as ctk
import os
from PIL import Image, ImageTk
from gui_Light import BACKGROUND_COLOR, SUCCESS_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR, GRAY_TEXT_COLOR, SEMI_TRANSPARENT_OVERLAY, CLOSE_BUTTON_BG, CLOSE_BUTTON_TEXT, ERROR_COLOR, BUTTON_TEXT_COLOR, CARD_SHADOW_COLOR, GLASS_BG_COLOR, LIGHT_ORANGE_BG, LIGHT_PURPLE_BG, HOVER_BG_COLOR, MODERN_BORDER, set_swigato_icon, ENTRY_BG_COLOR
from utils.image_loader import load_image
from utils.logger import log
from orders.models import get_orders_by_user_id
from cart.models import Cart

class MainAppScreen(ctk.CTkFrame):
    def __init__(self, app_ref, user, show_menu_callback, show_cart_callback, logout_callback):
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)
        self.app_ref = app_ref # Store reference to the main SwigatoApp instance
        self.user = user
        self.show_menu_callback = show_menu_callback
        self.show_cart_callback = show_cart_callback
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
            command=self.show_profile_popup
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
                    if f"{tab_name}_label" in self.nav_buttons:                        self.nav_buttons[f"{tab_name}_label"].configure(text_color=GRAY_TEXT_COLOR)

    def setup_content_areas(self):
        """Setup all content areas in the main content frame"""
        
        # Modern Restaurant List Scrollable Frame
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(
            self.main_content_frame, 
            fg_color=BACKGROUND_COLOR, 
            border_width=0,
            corner_radius=0
        )
        self.restaurant_scroll_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)        # Modern Favorites content frame
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
        
        # Show restaurants
        self.restaurant_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_restaurants()

    def show_favorites_content(self):
        """Show favorites content"""
        # Hide other content
        self.restaurant_scroll_frame.grid_remove()
        self.orders_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
        
        # Show favorites
        self.favorites_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_favorites()

    def show_orders_content(self):
        """Show orders content"""
        # Hide other content
        self.restaurant_scroll_frame.grid_remove()
        self.favorites_content_frame.grid_remove()
        self.cart_content_frame.grid_remove()
        
        # Show orders
        self.orders_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_order_history()

    def show_cart_content(self):
        """Show cart content"""
        # Hide other content
        self.restaurant_scroll_frame.grid_remove()
        self.favorites_content_frame.grid_remove()
        self.orders_content_frame.grid_remove()
        
        # Show cart
        self.cart_content_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.load_cart_items()

    def load_restaurants(self):
        log("MainAppScreen.load_restaurants called")
        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()

        from restaurants.models import Restaurant # Local import to avoid circular dependency issues at module level
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
            name_label.grid(row=0, column=0, pady=(0, 8), sticky="ew")            # Modern cuisine tag with pill-style design
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
            
            rating_text = f"{restaurant.rating:.1f} • {restaurant.get_review_count()} reviews"
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
                fg_color="#FFE4E6" if is_fav else "transparent",  # Light pink background when favorited
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

    def _toggle_favorite_restaurant(self, restaurant, button):
        is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        if is_fav:
            self.user.remove_favorite_restaurant(restaurant.restaurant_id)
        else:
            self.user.add_favorite_restaurant(restaurant.restaurant_id)
        
        # Update button appearance with clear visual states
        new_is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
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
            button.configure(
                fg_color="transparent",
                text_color="#9CA3AF",
                border_color="#E5E7EB",
                hover_color="#FEF2F2"
            )

    def show_favorites_section(self):
        # Destroy any previous favorites window
        if hasattr(self, 'favorites_window') and self.favorites_window:
            self.favorites_window.destroy()
        self.favorites_window = ctk.CTkToplevel(self)
        self.favorites_window.title("Your Favorites")
        self.favorites_window.geometry("900x500")
        set_swigato_icon(self.favorites_window)
        self.favorites_window.grab_set()
        self.favorites_window.configure(fg_color=FRAME_FG_COLOR)
        self.favorites_window.grid_columnconfigure(0, weight=1)
        self.favorites_window.grid_rowconfigure(0, weight=0)
        self.favorites_window.grid_rowconfigure(1, weight=1)

        heading_label = ctk.CTkLabel(
            self.favorites_window,
            text="Your Favorites",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR,
            fg_color="transparent",
            anchor="center",
            justify="center"
        )
        heading_label.grid(row=0, column=0, pady=(18, 0), padx=20, sticky="n")

        scroll_frame = ctk.CTkScrollableFrame(self.favorites_window, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        scroll_frame.grid(row=1, column=0, padx=24, pady=24, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        # Favorite Restaurants
        fav_restaurants = self.user.get_favorite_restaurants()
        fav_menu_items = self.user.get_favorite_menu_items()
        row = 0
        if fav_restaurants:
            ctk.CTkLabel(scroll_frame, text="Favorite Restaurants", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY_COLOR).grid(row=row, column=0, sticky="w", pady=(0, 8))
            row += 1
            for rest in fav_restaurants:
                rest_card = ctk.CTkFrame(scroll_frame, fg_color=BACKGROUND_COLOR, 
                                       border_width=1, border_color=FRAME_BORDER_COLOR, corner_radius=8)
                rest_card.grid(row=row, column=0, sticky="ew", padx=10, pady=(0, 8))
                rest_card.grid_columnconfigure(0, weight=1)                
                ctk.CTkLabel(rest_card, text=rest.name, font=ctk.CTkFont(size=16, weight="bold"), 
                           text_color=TEXT_COLOR).pack(pady=8)
                ctk.CTkButton(rest_card, text="View Menu", fg_color=PRIMARY_COLOR, 
                            hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=14, weight="bold"),  # Added explicit size 14
                            command=lambda r=rest: self.show_menu_callback(r)).pack(pady=(0, 8))
                row += 1
        else:
            ctk.CTkLabel(scroll_frame, text="No favorite restaurants yet.", font=ctk.CTkFont(size=13), text_color=GRAY_TEXT_COLOR).grid(row=row, column=0, sticky="w", pady=(0, 8))
            row += 1
        # Favorite Menu Items
        if fav_menu_items:
            ctk.CTkLabel(scroll_frame, text="Favorite Dishes", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY_COLOR).grid(row=row, column=0, sticky="w", pady=(16, 8))
            row += 1
            from restaurants.models import Restaurant, MenuItem
            for item in fav_menu_items:
                # Get restaurant name for this menu item
                rest_name = ""
                if hasattr(item, 'restaurant_id') and item.restaurant_id:
                    rest_obj = Restaurant.get_by_id(item.restaurant_id)
                    if rest_obj:
                        rest_name = rest_obj.name
                # Row frame for dish + button
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.grid(row=row, column=0, sticky="ew", pady=(0, 4))
                row_frame.grid_columnconfigure(0, weight=1)
                # Dish label
                item_label = ctk.CTkLabel(row_frame, text=f"{item.name} ({rest_name})" if rest_name else item.name, font=ctk.CTkFont(size=15), text_color=TEXT_COLOR)
                item_label.grid(row=0, column=0, sticky="w")                # Quick Order button
                quick_order_btn = ctk.CTkButton(row_frame, text="Quick Order", width=90, fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=14, weight="bold"),  # Increased from 12 to 14
                    command=lambda i=item: self._quick_order_from_favorites(i))
                quick_order_btn.grid(row=0, column=1, padx=(10,0), sticky="e")
                row += 1
        else:
            ctk.CTkLabel(scroll_frame, text="No favorite dishes yet.", font=ctk.CTkFont(size=13), text_color=GRAY_TEXT_COLOR).grid(row=row, column=0, sticky="w", pady=(0, 8))

    def _quick_order_from_favorites(self, menu_item):
        # Add the item to the user's cart (quantity 1)
        if hasattr(self.app_ref, 'cart') and self.app_ref.cart:
            # Set the current_restaurant to the menu item's restaurant
            if hasattr(menu_item, 'restaurant_id') and menu_item.restaurant_id:
                from restaurants.models import Restaurant
                rest_obj = Restaurant.get_by_id(menu_item.restaurant_id)
                if rest_obj:
                    self.app_ref.current_restaurant = rest_obj
            added = self.app_ref.cart.add_item(menu_item, 1)
            if added:
                ctk.CTkLabel(self.favorites_window, text=f"'{menu_item.name}' added to cart!", font=ctk.CTkFont(size=12), text_color=SUCCESS_COLOR, fg_color="transparent").place(relx=0.5, rely=0.98, anchor="s")
            else:
                ctk.CTkLabel(self.favorites_window, text=f"Failed to add '{menu_item.name}'.", font=ctk.CTkFont(size=12), text_color=ERROR_COLOR, fg_color="transparent").place(relx=0.5, rely=0.98, anchor="s")
        else:
            ctk.CTkLabel(self.favorites_window, text="Error: Cart not available.", font=ctk.CTkFont(size=12), text_color=ERROR_COLOR, fg_color="transparent").place(relx=0.5, rely=0.98, anchor="s")

    def update_user_info(self, user):
        self.user = user
        self.welcome_label.configure(text=f"Welcome, {self.user.username}!")
        self.load_restaurants() # Reload restaurants, in case of user-specific content in future

    def show_order_history(self):
        # Destroy any previous order history window
        if hasattr(self, 'order_history_window') and self.order_history_window:
            self.order_history_window.destroy()
        self.order_history_window = ctk.CTkToplevel(self)
        self.order_history_window.title("Order History")
        self.order_history_window.geometry("900x500")
        set_swigato_icon(self.order_history_window)
        self.order_history_window.grab_set()

        # Light theme: white background, dark text
        self.order_history_window.configure(fg_color=FRAME_FG_COLOR)
        self.order_history_window.grid_columnconfigure(0, weight=1)
        self.order_history_window.grid_rowconfigure(0, weight=0)
        self.order_history_window.grid_rowconfigure(1, weight=1)

        # Add heading label (centered, no corners, transparent background, orange text)
        heading_label = ctk.CTkLabel(
            self.order_history_window,
            text="Order History",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR,
            fg_color="transparent",
            anchor="center",
            justify="center"
        )
        heading_label.grid(row=0, column=0, pady=(18, 0), padx=20, sticky="n")

        orders = get_orders_by_user_id(self.user.user_id)
        orders = orders[:20]

        # --- Scrollable Frame for Table ---
        scroll_frame = ctk.CTkScrollableFrame(self.order_history_window, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        scroll_frame.grid(row=1, column=0, padx=24, pady=24, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        headers = ["Order ID", "Restaurant", "Date", "Total (₹)", "Status", "Items", "Address"]
        table_data = [headers]
        
        for order in orders:
            date_str = order.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order.order_date, 'strftime') else str(order.order_date)
            items_str = ", ".join([f"{item.name} x{item.quantity}" for item in getattr(order, 'items', [])])
            if len(items_str) > 60:
                items_str = items_str[:57] + "..."
            
            address_str = order.delivery_address or "N/A"
            if len(address_str) > 30:
                address_str = address_str[:27] + "..."
            
            table_data.append([
                order.order_id,
                order.restaurant_name,
                date_str,                f"{order.total_amount:.2f}",
                order.status,
                items_str,
                address_str
            ])

        if len(table_data) == 1:
            ctk.CTkLabel(scroll_frame, text="No orders found.", font=ctk.CTkFont(size=12), text_color=TEXT_COLOR, fg_color="transparent").pack(expand=True, anchor="center", padx=20, pady=20)
            return

        # Create a custom order history display instead of using CTkTable for better color support
        # Header row
        header_frame = ctk.CTkFrame(scroll_frame, fg_color=FRAME_BORDER_COLOR, corner_radius=8)
        header_frame.pack(fill="x", padx=8, pady=(8, 4))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            header_label.grid(row=0, column=i, padx=5, pady=8, sticky="ew")
        
        # Data rows with colored status
        for row_idx, row_data in enumerate(table_data[1:]):  # Skip header
            row_frame = ctk.CTkFrame(
                scroll_frame, 
                fg_color=FRAME_FG_COLOR if row_idx % 2 == 0 else BACKGROUND_COLOR,
                corner_radius=4
            )
            row_frame.pack(fill="x", padx=8, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
            
            for col_idx, cell_data in enumerate(row_data):
                if col_idx == 4:  # Status column
                    status_color = self.get_status_color(cell_data)
                    cell_label = ctk.CTkLabel(
                        row_frame,
                        text=f"● {cell_data}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=status_color
                    )
                else:
                    cell_label = ctk.CTkLabel(
                        row_frame,
                        text=str(cell_data),
                        font=ctk.CTkFont(size=11),
                        text_color=TEXT_COLOR
                    )
                cell_label.grid(row=0, column=col_idx, padx=5, pady=6, sticky="ew")

    def show_profile_panel(self):
        # Destroy previous panel if exists
        if hasattr(self, 'profile_panel') and self.profile_panel and self.profile_panel.winfo_exists():
            self.profile_panel.destroy()
      
      
        # Overlay to catch outside clicks
        if hasattr(self, 'profile_overlay') and self.profile_overlay and self.profile_overlay.winfo_exists():
            self.profile_overlay.destroy()
        self.profile_overlay = ctk.CTkFrame(self, fg_color=SEMI_TRANSPARENT_OVERLAY, width=self.winfo_width(), height=self.winfo_height())
        self.profile_overlay.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        self.profile_overlay.bind("<Button-1>", lambda e: self.hide_profile_panel())
        # Side panel (wider)
        self.profile_panel = ctk.CTkFrame(self.profile_overlay, fg_color=FRAME_FG_COLOR, width=420, corner_radius=16, border_width=2, border_color=FRAME_BORDER_COLOR)
        self.profile_panel.place(relx=1.0, rely=0, anchor="ne", relheight=1.0, x=0, y=0)
        # Prevent overlay click from closing if click inside panel
        self.profile_panel.bind("<Button-1>", lambda e: e.stop_propagation() if hasattr(e, 'stop_propagation') else None)
        # Tabs
        tabview = ctk.CTkTabview(self.profile_panel, width=400, height=520, fg_color=FRAME_FG_COLOR)
        tabview.pack(padx=16, pady=16, fill="both", expand=True)
        tabview.add("Profile")
        tabview.add("Password")
        tabview.add("Logout")

        # --- Profile Tab ---
        tab_profile = tabview.tab("Profile")
        ctk.CTkLabel(tab_profile, text="Account Info", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(24,8))
        ctk.CTkLabel(tab_profile, text=f"Username: {self.user.username}", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR).pack(pady=(8,4))
        ctk.CTkLabel(tab_profile, text=f"Email: {getattr(self.user, 'email', 'N/A')}", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=(4,4))
        ctk.CTkLabel(tab_profile, text=f"Address: {getattr(self.user, 'address', 'N/A')}", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=(4,12))


        # --- Password Tab ---
        tab_password = tabview.tab("Password")
        ctk.CTkLabel(tab_password, text="Change Password", font=ctk.CTkFont(size=20, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(24,8))
        old_pw = ctk.CTkEntry(tab_password, show="*", placeholder_text="Current Password")
        old_pw.pack(pady=6)
        new_pw = ctk.CTkEntry(tab_password, show="*", placeholder_text="New Password")
        new_pw.pack(pady=6)
        confirm_pw = ctk.CTkEntry(tab_password, show="*", placeholder_text="Confirm New Password")
        confirm_pw.pack(pady=6)
        pw_msg = ctk.CTkLabel(tab_password, text="", text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=12))
        pw_msg.pack(pady=4)
        def do_change_pw():
            old = old_pw.get()
            new = new_pw.get()
            confirm = confirm_pw.get()
            if not old or not new or not confirm:
                pw_msg.configure(text="All fields required.", text_color=ERROR_COLOR)
                return
            if new != confirm:
                pw_msg.configure(text="New passwords do not match.", text_color=ERROR_COLOR)
                return
            if not self.user.verify_password(old):
                pw_msg.configure(text="Current password is incorrect.", text_color=ERROR_COLOR)
                return
            ok = self.user.update_password(new)
            if ok:
                pw_msg.configure(text="Password changed successfully!", text_color=SUCCESS_COLOR)
            else:
                pw_msg.configure(text="Failed to change password.", text_color=ERROR_COLOR)
        ctk.CTkButton(tab_password, text="Change Password", command=do_change_pw, fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=12)  # Added explicit size 14
       
       
        # --- Logout Tab ---
        tab_logout = tabview.tab("Logout")
        ctk.CTkLabel(tab_logout, text="Are you sure you want to logout?", font=ctk.CTkFont(size=16, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(32,12))
        ctk.CTkButton(tab_logout, text="Logout", fg_color=SECONDARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=14, weight="bold"), command=self.logout_callback).pack(pady=16)  # Added explicit size 14
       
       
        # Close button (top right)
        ctk.CTkButton(self.profile_panel, text="✕", width=32, height=32, fg_color=CLOSE_BUTTON_BG, text_color=CLOSE_BUTTON_TEXT, font=ctk.CTkFont(size=18, weight="bold"), command=self.hide_profile_panel).place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)  # Increased from 16 to 18

    def hide_profile_panel(self):
        if hasattr(self, 'profile_panel') and self.profile_panel and self.profile_panel.winfo_exists():
            self.profile_panel.destroy()
            self.profile_panel = None
        if hasattr(self, 'profile_overlay') and self.profile_overlay and self.profile_overlay.winfo_exists():
            self.profile_overlay.destroy()
            self.profile_overlay = None

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

    def load_order_history(self):
        """Load and display order history with modern design"""
        # Clear existing widgets
        for widget in self.orders_scroll_frame.winfo_children():
            widget.destroy()

        orders = get_orders_by_user_id(self.user.user_id)
        orders = orders[:20]  # Limit to latest 20 orders

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
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR
            )
            empty_label.pack(pady=(0, 5))
            
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Your order history will appear here\nafter you make your first order.",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                justify="center"
            )
            empty_desc.pack(pady=(0, 30))
            return

        for i, order in enumerate(orders):
            order_card = ctk.CTkFrame(
                self.orders_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=16,
                border_width=1,
                border_color=FRAME_BORDER_COLOR
            )
            order_card.grid(row=i, column=0, pady=(0, 15), padx=20, sticky="ew")
            order_card.grid_columnconfigure(0, weight=1)

            # Order header
            header_frame = ctk.CTkFrame(order_card, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
            header_frame.grid_columnconfigure(0, weight=1)
            header_frame.grid_columnconfigure(1, weight=0)

            order_title = ctk.CTkLabel(
                header_frame,
                text=f"Order #{order.order_id}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            order_title.grid(row=0, column=0, sticky="w")

            order_total = ctk.CTkLabel(
                header_frame,
                text=f"₹{order.total_amount:.2f}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=PRIMARY_COLOR
            )
            order_total.grid(row=0, column=1, sticky="e")            # Order details with color-coded status
            details_frame = ctk.CTkFrame(order_card, fg_color="transparent")
            details_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
            details_frame.grid_columnconfigure(0, weight=1)
            details_frame.grid_columnconfigure(1, weight=0)
            
            # Date and restaurant info
            date_label = ctk.CTkLabel(
                details_frame,
                text=f"📅 {order.order_date}",
                font=ctk.CTkFont(size=13),
                text_color=GRAY_TEXT_COLOR,
                anchor="w"
            )
            date_label.grid(row=0, column=0, sticky="w")
            
            # Status with color coding
            status_color = self.get_status_color(order.status)
            status_label = ctk.CTkLabel(
                details_frame,
                text=f"● {order.status}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=status_color,
                anchor="e"            )
            status_label.grid(row=0, column=1, sticky="e")

    def load_cart_items(self):
        """Load and display cart items with modern design"""
        # Clear existing widgets
        for widget in self.cart_scroll_frame.winfo_children():
            widget.destroy()

        if hasattr(self.app_ref, 'cart') and self.app_ref.cart and self.app_ref.cart.items:                # Display cart items with enhanced styling
            for i, (item_id, cart_item) in enumerate(self.app_ref.cart.items.items()):
                item_card = ctk.CTkFrame(
                    self.cart_scroll_frame,
                    fg_color=FRAME_FG_COLOR,
                    corner_radius=16,
                    border_width=1,
                    border_color=FRAME_BORDER_COLOR
                )
                item_card.grid(row=i, column=0, pady=(0, 15), padx=20, sticky="ew")
                item_card.grid_columnconfigure(0, weight=1)

                # Top row with item name and total price
                top_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
                top_frame.grid_columnconfigure(0, weight=1)
                
                # Item name
                item_label = ctk.CTkLabel(
                    top_frame,
                    text=f"{cart_item.menu_item.name}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=TEXT_COLOR,
                    anchor="w"
                )
                item_label.grid(row=0, column=0, sticky="w")
                
                # Total price for this item
                item_total = cart_item.quantity * cart_item.menu_item.price
                item_total_label = ctk.CTkLabel(
                    top_frame,
                    text=f"₹{item_total:.2f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=PRIMARY_COLOR,
                    anchor="e"
                )
                item_total_label.grid(row=0, column=1, sticky="e")

                # Bottom row with quantity and unit price
                details_label = ctk.CTkLabel(
                    item_card,
                    text=f"Qty: {cart_item.quantity} • ₹{cart_item.menu_item.price} each",
                    font=ctk.CTkFont(size=13),
                    text_color=GRAY_TEXT_COLOR,
                    anchor="w"
                )
                details_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))# Add modern checkout section
            total_amount = self.app_ref.cart.get_total_price()
              # Modern checkout container with elegant styling
            checkout_container = ctk.CTkFrame(
                self.cart_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=20,
                border_width=1,
                border_color=MODERN_BORDER
            )
            checkout_container.grid(row=len(self.app_ref.cart.items), column=0, pady=(30, 20), padx=20, sticky="ew")
            checkout_container.grid_columnconfigure(0, weight=1)
            
            # Order summary header
            summary_header = ctk.CTkLabel(
                checkout_container,
                text="Order Summary",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=TEXT_COLOR
            )
            summary_header.grid(row=0, column=0, pady=(25, 15), padx=25, sticky="w")
            
            # Subtotal row
            subtotal_frame = ctk.CTkFrame(checkout_container, fg_color="transparent")
            subtotal_frame.grid(row=1, column=0, pady=(0, 8), padx=25, sticky="ew")
            subtotal_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                subtotal_frame,
                text="Subtotal",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                subtotal_frame,
                text=f"₹{total_amount:.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_COLOR
            ).grid(row=0, column=1, sticky="e")
            
            # Delivery fee row
            delivery_frame = ctk.CTkFrame(checkout_container, fg_color="transparent")
            delivery_frame.grid(row=2, column=0, pady=(0, 8), padx=25, sticky="ew")
            delivery_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                delivery_frame,
                text="Delivery Fee",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                delivery_frame,
                text="Free",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=SUCCESS_COLOR
            ).grid(row=0, column=1, sticky="e")
            
            # Divider line
            divider = ctk.CTkFrame(
                checkout_container,
                fg_color=MODERN_BORDER,
                height=1
            )
            divider.grid(row=3, column=0, pady=(15, 15), padx=25, sticky="ew")
            
            # Total row with emphasis
            total_frame = ctk.CTkFrame(checkout_container, fg_color="transparent")
            total_frame.grid(row=4, column=0, pady=(0, 25), padx=25, sticky="ew")
            total_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                total_frame,
                text="Total",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=TEXT_COLOR
            ).grid(row=0, column=0, sticky="w")
            
            ctk.CTkLabel(
                total_frame,
                text=f"₹{total_amount:.2f}",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=PRIMARY_COLOR
            ).grid(row=0, column=1, sticky="e")
              # Modern gradient checkout button
            checkout_button = ctk.CTkButton(
                self.cart_scroll_frame,
                text="🛍️ Proceed to Checkout",
                command=self.handle_checkout,
                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=16, weight="bold"),
                height=56,
                corner_radius=20,
                border_width=0            )
            checkout_button.grid(row=len(self.app_ref.cart.items) + 1, column=0, pady=(10, 30), padx=20, sticky="ew")

        else:            # Modern empty cart state with enhanced styling
            empty_frame = ctk.CTkFrame(
                self.cart_scroll_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=24,
                border_width=1,
                border_color=MODERN_BORDER
            )
            empty_frame.grid(row=0, column=0, padx=20, pady=40, sticky="ew")
            
            # Empty cart icon with gradient effect
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="🛒",
                font=ctk.CTkFont(size=64),
                text_color=GRAY_TEXT_COLOR
            )
            empty_icon.pack(pady=(40, 15))
            
            # Main empty state message
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="Your cart is empty!",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=TEXT_COLOR
            )
            empty_label.pack(pady=(0, 8))
            
            # Descriptive text
            empty_desc = ctk.CTkLabel(
                empty_frame,
                text="Discover amazing restaurants and add\ndelicious items to your cart.",
                font=ctk.CTkFont(size=16),
                text_color=GRAY_TEXT_COLOR,
                justify="center"
            )
            empty_desc.pack(pady=(0, 25))
            
            # Call-to-action button to browse restaurants
            browse_button = ctk.CTkButton(
                empty_frame,
                text="🍽️ Browse Restaurants",
                command=lambda: self.show_restaurants_content(),                fg_color=PRIMARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=16, weight="bold"),
                height=48,
                corner_radius=16,
                width=220
            )
            browse_button.pack(pady=(0, 40))

    def handle_checkout(self):
        """Handle checkout process from the cart"""
        if hasattr(self.app_ref, 'handle_checkout'):
            self.app_ref.handle_checkout()
        else:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "Checkout functionality not available")

    def show_profile_popup(self):
        """Show modern profile popup with enhanced styling and full functionality"""
        # Destroy any previous profile window
        if hasattr(self, 'profile_window') and self.profile_window:
            self.profile_window.destroy()
            
        self.profile_window = ctk.CTkToplevel(self)
        self.profile_window.title("Profile")
        self.profile_window.geometry("500x650")
        self.profile_window.configure(fg_color=BACKGROUND_COLOR)
        
        # Set Swigato icon
        set_swigato_icon(self.profile_window)
        
        # Center the window
        self.profile_window.grab_set()
        
        # Calculate position to center the window
        self.profile_window.update_idletasks()
        x = (self.profile_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.profile_window.winfo_screenheight() // 2) - (650 // 2)
        self.profile_window.geometry(f"500x650+{x}+{y}")
        
        # Modern header
        header_frame = ctk.CTkFrame(self.profile_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))
        
        profile_icon = ctk.CTkLabel(
            header_frame,
            text="👤",
            font=ctk.CTkFont(size=40),
            text_color=PRIMARY_COLOR
        )
        profile_icon.pack(pady=(0, 10))
        
        profile_title = ctk.CTkLabel(
            header_frame,
            text="Your Profile",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_COLOR
        )
        profile_title.pack()
        
        # Modern tabview for profile sections
        tabview = ctk.CTkTabview(
            self.profile_window,
            corner_radius=16,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            fg_color=FRAME_FG_COLOR
        )
        tabview.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Account Info Tab
        tabview.add("Account")
        account_tab = tabview.tab("Account")
        
        info_frame = ctk.CTkFrame(account_tab, fg_color=BACKGROUND_COLOR, corner_radius=12)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        username_label = ctk.CTkLabel(
            info_frame,
            text=f"Username: {self.user.username}",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        username_label.pack(fill="x", padx=20, pady=(20, 10))
        
        if hasattr(self.user, 'email') and self.user.email:
            email_label = ctk.CTkLabel(
                info_frame,
                text=f"Email: {self.user.email}",
                font=ctk.CTkFont(size=16),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            email_label.pack(fill="x", padx=20, pady=(0, 20))
        
        # Change Username Tab
        tabview.add("Username")
        username_tab = tabview.tab("Username")
        
        username_frame = ctk.CTkFrame(username_tab, fg_color=BACKGROUND_COLOR, corner_radius=12)
        username_frame.pack(fill="x", padx=20, pady=20)
        
        username_title = ctk.CTkLabel(
            username_frame,
            text="Change Username",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR
        )
        username_title.pack(pady=(20, 15))
        
        # Current username display
        current_username_label = ctk.CTkLabel(
            username_frame,
            text=f"Current Username: {self.user.username}",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR
        )
        current_username_label.pack(pady=(0, 15))
        
        # New username entry
        new_username_label = ctk.CTkLabel(
            username_frame,
            text="New Username:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        new_username_label.pack(anchor="w", padx=20)
        
        self.new_username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="Enter new username",
            font=ctk.CTkFont(size=14),
            width=300,
            height=40,
            fg_color=ENTRY_BG_COLOR,
            border_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR
        )
        self.new_username_entry.pack(pady=(5, 15), padx=20)
        
        change_username_btn = ctk.CTkButton(
            username_frame,
            text="Change Username",
            command=self.change_username,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            height=40
        )
        change_username_btn.pack(pady=(0, 20))
        
        # Change Password Tab
        tabview.add("Password")
        password_tab = tabview.tab("Password")
        
        password_frame = ctk.CTkFrame(password_tab, fg_color=BACKGROUND_COLOR, corner_radius=12)
        password_frame.pack(fill="x", padx=20, pady=20)
        
        password_title = ctk.CTkLabel(
            password_frame,
            text="Change Password",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR
        )
        password_title.pack(pady=(20, 15))
        
        # Current password
        current_password_label = ctk.CTkLabel(
            password_frame,
            text="Current Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        current_password_label.pack(anchor="w", padx=20)
        
        self.current_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter current password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=40,
            fg_color=ENTRY_BG_COLOR,
            border_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR
        )
        self.current_password_entry.pack(pady=(5, 10), padx=20)
        
        # New password
        new_password_label = ctk.CTkLabel(
            password_frame,
            text="New Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        new_password_label.pack(anchor="w", padx=20)
        
        self.new_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter new password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=40,
            fg_color=ENTRY_BG_COLOR,
            border_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR
        )
        self.new_password_entry.pack(pady=(5, 10), padx=20)
        
        # Confirm new password
        confirm_password_label = ctk.CTkLabel(
            password_frame,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR
        )
        confirm_password_label.pack(anchor="w", padx=20)
        
        self.confirm_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Confirm new password",
            show="*",
            font=ctk.CTkFont(size=14),
            width=300,
            height=40,
            fg_color=ENTRY_BG_COLOR,
            border_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR
        )
        self.confirm_password_entry.pack(pady=(5, 15), padx=20)
        
        change_password_btn = ctk.CTkButton(
            password_frame,
            text="Change Password",
            command=self.change_password,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            height=40
        )
        change_password_btn.pack(pady=(0, 20))
          # Settings Tab
        tabview.add("Settings")
        settings_tab = tabview.tab("Settings")
        
        settings_frame = ctk.CTkFrame(settings_tab, fg_color=BACKGROUND_COLOR, corner_radius=12)
        settings_frame.pack(fill="x", padx=20, pady=20)
        
        # Placeholder for future settings
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="More settings coming soon!",
            font=ctk.CTkFont(size=16),
            text_color=GRAY_TEXT_COLOR
        )
        settings_label.pack(pady=40)

    def change_username(self):
        """Handle username change"""
        new_username = self.new_username_entry.get().strip()
        
        if not new_username:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "Please enter a new username.")
            return
        
        if new_username == self.user.username:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("Warning", "New username is the same as current username.")
            return
        
        try:
            # Check if username already exists
            from users.models import User
            if User.get_by_username(new_username):
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Username already exists. Please choose a different one.")
                return
            
            # Update username
            success = self.user.update_username(new_username)
            if success:
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Success", "Username changed successfully!")
                # Update the welcome label
                self.welcome_label.configure(text=f"Welcome back, {self.user.username}! 👋")
                # Clear the entry
                self.new_username_entry.delete(0, 'end')
                # Close profile window
                if hasattr(self, 'profile_window') and self.profile_window:
                    self.profile_window.destroy()
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Failed to change username. Please try again.")
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"An error occurred: {str(e)}")

    def change_password(self):
        """Handle password change"""
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not all([current_password, new_password, confirm_password]):
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "Please fill in all password fields.")
            return
        
        if new_password != confirm_password:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "New passwords do not match.")
            return
        if len(new_password) < 6:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", "New password must be at least 6 characters long.")
            return
        
        try:
            # Verify current password using the user object's method
            if not self.user.verify_password(current_password):
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Current password is incorrect.")
                return
            
            # Update password
            success = self.user.update_password(new_password)
            if success:
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Success", "Password changed successfully!")
                # Clear the entries
                self.current_password_entry.delete(0, 'end')
                self.new_password_entry.delete(0, 'end')
                self.confirm_password_entry.delete(0, 'end')
                # Close profile window
                if hasattr(self, 'profile_window') and self.profile_window:
                    self.profile_window.destroy()
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", "Failed to change password. Please try again.")
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"An error occurred: {str(e)}")

    def get_status_color(self, status):
        """Get color code for order status"""
        status_colors = {
            "Pending Confirmation": "#DC3545",  # Red
            "Preparing": "#FFC107",             # Orange
            "Confirmed": "#17A2B8",             # Teal/Light Blue
            "Out for Delivery": "#2ECC71",      # Bright Green
            "Delivered": "#008000",             # Darker Green
            "Cancelled": "#6C757D",             # Muted Grey
            "Failed": "#A50000"                 # Dark Red
        }
        return status_colors.get(status, GRAY_TEXT_COLOR)  # Default to gray if status not found

    def add_to_cart_from_favorites(self, menu_item):
        """Add a favorite menu item to the cart"""
        try:
            # Ensure cart exists
            if not hasattr(self.app_ref, 'cart') or not self.app_ref.cart:
                self.app_ref.cart = Cart(user_id=self.user.user_id)
            
            # Add item to cart
            success = self.app_ref.cart.add_item(menu_item, quantity=1)
            
            if success:                # Show subtle success toast
                try:
                    # Create a temporary success notification
                    success_frame = ctk.CTkFrame(
                        self.favorites_scroll_frame,
                        fg_color="#2ECC71",
                        corner_radius=8,
                        width=250,
                        height=40
                    )
                    success_frame.place(relx=0.5, rely=0.0, anchor="n", y=10)
                    
                    success_label = ctk.CTkLabel(
                        success_frame,
                        text=f"✓ {menu_item.name} added to cart!",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="white"
                    )
                    success_label.pack(pady=10)
                    
                    # Remove the notification after 2 seconds
                    def remove_notification():
                        if success_frame.winfo_exists():
                            success_frame.destroy()
                    
                    self.after(2000, remove_notification)
                except:
                    # Fallback - just log success
                    pass
                
                # Update cart display if cart tab is active
                if hasattr(self, 'current_nav_tab') and self.current_nav_tab == "cart":
                    self.load_cart_items()
                    
                log(f"Added {menu_item.name} to cart from favorites")
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Error", f"Failed to add {menu_item.name} to cart")
                
        except Exception as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Error", f"An error occurred while adding to cart: {str(e)}")
            log(f"Error adding {menu_item.name} to cart: {str(e)}")
