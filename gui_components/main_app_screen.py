import customtkinter as ctk
import os
from PIL import Image, ImageTk
from gui_Light import BACKGROUND_COLOR, SUCCESS_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR, GRAY_TEXT_COLOR, SEMI_TRANSPARENT_OVERLAY, CLOSE_BUTTON_BG, CLOSE_BUTTON_TEXT, ERROR_COLOR, BUTTON_TEXT_COLOR, set_swigato_icon
from utils.image_loader import load_image
from utils.logger import log
from orders.models import get_orders_by_user_id

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
        self.grid_rowconfigure(2, weight=0)  # Bottom nav bar

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1) # Welcome message
        header_frame.grid_columnconfigure(1, weight=0) # Spacer
        header_frame.grid_columnconfigure(2, weight=0) # Admin Panel (if admin)
        header_frame.grid_columnconfigure(3, weight=0) # Theme button

        welcome_text = f"Welcome, {self.user.username}!"
        self.welcome_label = ctk.CTkLabel(header_frame, text=welcome_text,
                                          text_color=PRIMARY_COLOR,
                                          font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w")
          # Admin Panel button (if admin) - keep in header
        if hasattr(self.user, "is_admin") and self.user.is_admin:
            admin_panel_button = ctk.CTkButton(
                header_frame,
                text="Admin Panel",
                fg_color=FRAME_FG_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(size=14, weight="bold"),  # Added explicit size 14
                command=lambda: self.app_ref.show_admin_screen(self.user)
            )
            admin_panel_button.grid(row=0, column=2, sticky="e", padx=(0, 10))
            
        # Theme Toggle Button in top-right corner
        theme_btn = ctk.CTkButton(
            header_frame,
            text="🌙",
            width=50,
            height=35,
            fg_color="transparent",
            hover_color=BUTTON_HOVER_COLOR,
            text_color=PRIMARY_COLOR,
            font=ctk.CTkFont(size=20),
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=8,
            command=self.toggle_theme
        )
        # Position theme button at far right, or next to admin button if admin
        theme_col = 3 if hasattr(self.user, "is_admin") and self.user.is_admin else 2
        theme_btn.grid(row=0, column=theme_col, sticky="e")
        
        # --- Main Content Area ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.main_content_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Initialize content areas
        self.setup_content_areas()
          # Show restaurants by default
        self.show_restaurants_content()
        
        # --- Bottom Navigation Bar ---
        self.create_bottom_nav_bar()

    def create_bottom_nav_bar(self):
        """Create the bottom navigation bar with icon buttons"""
        bottom_nav_frame = ctk.CTkFrame(self, fg_color=FRAME_FG_COLOR, height=80, corner_radius=12)
        bottom_nav_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="ew")
        bottom_nav_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Equal spacing for 6 columns
        bottom_nav_frame.pack_propagate(False)
        
        # Store navigation buttons for state management
        self.nav_buttons = {}
        
        # Icon button style (default/inactive state)
        button_style = {
            "width": 80,
            "height": 50,
            "fg_color": "transparent",
            "hover_color": BUTTON_HOVER_COLOR,
            "text_color": PRIMARY_COLOR,
            "font": ctk.CTkFont(size=28),  # Increased from 24 to 28
            "border_width": 0
        }
        
        # Active button style 
        active_button_style = {
            "width": 80,
            "height": 50,
            "fg_color": PRIMARY_COLOR,
            "hover_color": BUTTON_HOVER_COLOR,
            "text_color": "white",
            "font": ctk.CTkFont(size=28),
            "border_width": 0        }
        
        # Cart Button 🛒
        cart_btn = ctk.CTkButton(bottom_nav_frame, text="🛒", 
                                command=lambda: self.handle_nav_click("cart"), **button_style)
        cart_btn.grid(row=0, column=0, padx=10, pady=(15, 5))
        self.nav_buttons["cart"] = cart_btn
        
        # Create tooltip for cart
        cart_label = ctk.CTkLabel(bottom_nav_frame, text="Cart", 
                                 font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        cart_label.grid(row=1, column=0, pady=(0, 5))
          # Restaurants Button 🍽️
        restaurants_btn = ctk.CTkButton(bottom_nav_frame, text="🍽️", 
                                      command=lambda: self.handle_nav_click("home"), **active_button_style)
        restaurants_btn.grid(row=0, column=1, padx=10, pady=(15, 5))
        self.nav_buttons["home"] = restaurants_btn
        
        restaurants_label = ctk.CTkLabel(bottom_nav_frame, text="Home", 
                                       font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        restaurants_label.grid(row=1, column=1, pady=(0, 5))

        # Only show Orders button if user is not an admin
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            orders_btn = ctk.CTkButton(bottom_nav_frame, text="📋", 
                                     command=lambda: self.handle_nav_click("orders"), **button_style)
            orders_btn.grid(row=0, column=2, padx=10, pady=(15, 5))
            self.nav_buttons["orders"] = orders_btn
            
            orders_label = ctk.CTkLabel(bottom_nav_frame, text="Orders", 
                                       font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
            orders_label.grid(row=1, column=2, pady=(0, 5))

        # Favorites Button ❤️
        favorites_btn = ctk.CTkButton(bottom_nav_frame, text="❤️", 
                                    command=lambda: self.handle_nav_click("favorites"), **button_style)
        next_col = 3 if not (hasattr(self.user, "is_admin") and self.user.is_admin) else 2
        favorites_btn.grid(row=0, column=next_col, padx=10, pady=(15, 5))
        self.nav_buttons["favorites"] = favorites_btn
        
        favorites_label = ctk.CTkLabel(bottom_nav_frame, text="Favorites", 
                                     font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        favorites_label.grid(row=1, column=next_col, pady=(0, 5))
        
        # Profile Button 👤
        profile_btn = ctk.CTkButton(bottom_nav_frame, text="👤", 
                                command=lambda: self.handle_nav_click("profile"), **button_style)
        next_col += 1
        profile_btn.grid(row=0, column=next_col, padx=10, pady=(15, 5))
        self.nav_buttons["profile"] = profile_btn
        
        profile_label = ctk.CTkLabel(bottom_nav_frame, text="Profile", 
                                 font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        profile_label.grid(row=1, column=next_col, pady=(0, 5))
        
        # Logout Button (larger, different style)
        logout_btn = ctk.CTkButton(bottom_nav_frame, text="Logout", 
                                  command=self.logout_callback,
                                  fg_color=SECONDARY_COLOR,
                                  hover_color=BUTTON_HOVER_COLOR,
                                  text_color=BUTTON_TEXT_COLOR,
                                  font=ctk.CTkFont(size=16, weight="bold"),  # Increased from 14 to 16
                                  width=100, height=45, corner_radius=8)
        logout_btn.grid(row=0, column=5, rowspan=2, padx=20, pady=15)
        
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
        elif tab_name == "profile":
            self.show_profile_popup()
    
    def set_active_nav_tab(self, active_tab):
        """Set the active navigation tab and update button styles"""
        self.current_nav_tab = active_tab
        
        # Define styles
        inactive_style = {
            "fg_color": "transparent",
            "text_color": PRIMARY_COLOR
        }
        active_style = {
            "fg_color": PRIMARY_COLOR,
            "text_color": "white"
        }
        
        # Update all navigation buttons
        for tab_name, button in self.nav_buttons.items():
            if tab_name == active_tab:
                button.configure(**active_style)
            else:
                button.configure(**inactive_style)

    def toggle_theme(self):
        """Toggle between light and dark theme (placeholder for now)"""
        # For now, just show a message. In the future, this could switch themes
        import tkinter.messagebox as msgbox
        msgbox.showinfo("Theme", "Theme toggle feature coming soon!")

    def setup_content_areas(self):
        """Setup all content areas in the main content frame"""
        # Restaurant List Scrollable Frame
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR, border_width=0)
        self.restaurant_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)

        # Favorites content frame
        self.favorites_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.favorites_content_frame.grid_columnconfigure(0, weight=1)
        self.favorites_content_frame.grid_rowconfigure(1, weight=1)

        favorites_heading = ctk.CTkLabel(
            self.favorites_content_frame,
            text="Your Favorites",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        favorites_heading.grid(row=0, column=0, pady=(10, 5), sticky="n")

        self.favorites_scroll_frame = ctk.CTkScrollableFrame(self.favorites_content_frame, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        self.favorites_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.favorites_scroll_frame.grid_columnconfigure(0, weight=1)

        # Orders content frame
        self.orders_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.orders_content_frame.grid_columnconfigure(0, weight=1)
        self.orders_content_frame.grid_rowconfigure(1, weight=1)

        orders_heading = ctk.CTkLabel(
            self.orders_content_frame,
            text="Your Order History",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        orders_heading.grid(row=0, column=0, pady=(10, 5), sticky="n")

        self.orders_scroll_frame = ctk.CTkScrollableFrame(self.orders_content_frame, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        self.orders_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.orders_scroll_frame.grid_columnconfigure(0, weight=1)

        # Cart content frame
        self.cart_content_frame = ctk.CTkFrame(self.main_content_frame, fg_color=BACKGROUND_COLOR)
        self.cart_content_frame.grid_columnconfigure(0, weight=1)
        self.cart_content_frame.grid_rowconfigure(1, weight=1)

        cart_heading = ctk.CTkLabel(
            self.cart_content_frame,
            text="Your Shopping Cart",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        cart_heading.grid(row=0, column=0, pady=(10, 5), sticky="n")

        self.cart_scroll_frame = ctk.CTkScrollableFrame(self.cart_content_frame, fg_color=FRAME_FG_COLOR, 
                                                       corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        self.cart_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.cart_scroll_frame.grid_columnconfigure(0, weight=1)        # Hide all content frames initially
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

    def change_password(self):
        """Handle password change"""
        # This method would be implemented if profile tab is added back
        pass

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
            restaurant_card = ctk.CTkFrame(self.restaurant_scroll_frame,
                                           fg_color=FRAME_FG_COLOR,
                                           border_color=FRAME_BORDER_COLOR,
                                           border_width=1,
                                           corner_radius=8)
            restaurant_card.grid(row=i, column=0, pady=(0, 10), sticky="ew")
            restaurant_card.grid_columnconfigure(0, weight=0) # Image
            restaurant_card.grid_columnconfigure(1, weight=1) # Details
            restaurant_card.grid_columnconfigure(2, weight=0) # Button
            restaurant_card.grid_columnconfigure(3, weight=0) # Heart

            image_label = None
            if restaurant.image_filename:
                project_root = self.app_ref.project_root # Use app_ref
                image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
                log(f"Attempting to load restaurant image from: {image_path}")
                ctk_image = load_image(image_path, size=(120, 120))
                if ctk_image:
                    image_label = ctk.CTkLabel(restaurant_card, image=ctk_image, text="")
                    image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")
            if not image_label:
                image_label = ctk.CTkLabel(restaurant_card, text="No Image", width=120, height=120, fg_color=GRAY_TEXT_COLOR, text_color=BUTTON_TEXT_COLOR)
                image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

            details_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, rowspan=3, padx=(0,10), pady=10, sticky="nsew")
            details_frame.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(details_frame, text=restaurant.name,
                                      font=ctk.CTkFont(size=18, weight="bold"),
                                      text_color=TEXT_COLOR, anchor="w")
            name_label.grid(row=0, column=0, pady=(0, 2), sticky="ew")

            cuisine_text = f"Cuisine: {restaurant.cuisine_type}"
            cuisine_label = ctk.CTkLabel(details_frame, text=cuisine_text,
                                         font=ctk.CTkFont(size=12),
                                         text_color=TEXT_COLOR, anchor="w")
            cuisine_label.grid(row=1, column=0, pady=(0, 2), sticky="ew")

            rating_text = f"Rating: {restaurant.rating:.1f}/5.0 ({restaurant.get_review_count()} reviews)"
            rating_label = ctk.CTkLabel(details_frame, text=rating_text,
                                        font=ctk.CTkFont(size=12),
                                        text_color=TEXT_COLOR, anchor="w")
            rating_label.grid(row=2, column=0, pady=(0, 5), sticky="ew")            # Heart/Favorite button
            is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
            heart_text = "\u2665" if is_fav else "\u2661"  # ♥ or ♡
            heart_button = ctk.CTkButton(restaurant_card, text=heart_text, width=40, fg_color="transparent", text_color=(ERROR_COLOR if is_fav else GRAY_TEXT_COLOR), font=ctk.CTkFont(size=26), hover_color=FRAME_BORDER_COLOR,  # Increased from 22 to 26
                                         command=lambda r=restaurant, b=None: self._toggle_favorite_restaurant(r, b))
            # Use a lambda to pass the button itself after creation
            heart_button.grid(row=0, column=3, rowspan=3, padx=(0, 10), pady=10, sticky="e")
            # Patch the button reference for lambda
            heart_button.configure(command=lambda r=restaurant, b=heart_button: self._toggle_favorite_restaurant(r, b))

            view_menu_button = ctk.CTkButton(restaurant_card, text="View Menu",
                                             fg_color=PRIMARY_COLOR,
                                             hover_color=BUTTON_HOVER_COLOR,
                                             text_color=TEXT_COLOR,
                                             font=ctk.CTkFont(size=14, weight="bold"),  # Added explicit size 14
                                             width=100,
                                             command=lambda r=restaurant: self.show_menu_callback(r))
            view_menu_button.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="e")

    def _toggle_favorite_restaurant(self, restaurant, button):
        is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        if is_fav:
            self.user.remove_favorite_restaurant(restaurant.restaurant_id)
        else:
            self.user.add_favorite_restaurant(restaurant.restaurant_id)
        # Update button appearance
        new_is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        button.configure(text=("\u2665" if new_is_fav else "\u2661"), text_color=(ERROR_COLOR if new_is_fav else GRAY_TEXT_COLOR))

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
                rest_label = ctk.CTkLabel(scroll_frame, text=rest.name, font=ctk.CTkFont(size=15), text_color=TEXT_COLOR)
                rest_label.grid(row=row, column=0, sticky="w", pady=(0, 4))
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
                date_str,
                f"{order.total_amount:.2f}",
                order.status,
                items_str,
                address_str
            ])

        if len(table_data) == 1:
            ctk.CTkLabel(scroll_frame, text="No orders found.", font=ctk.CTkFont(size=12), text_color=TEXT_COLOR, fg_color="transparent").pack(expand=True, anchor="center", padx=20, pady=20)
            return

        from CTkTable import CTkTable
        # Font variables for table styling (used in CTkTable constructor)
        cell_font = ctk.CTkFont(size=11)
        header_font = ctk.CTkFont(size=12, weight="bold")  # Note: Currently not used but available for header styling
        
        orders_table = CTkTable(
            master=scroll_frame,
            values=table_data,
            font=cell_font,  # type: ignore[arg-type]
            header_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR,
            hover_color=PRIMARY_COLOR,
            colors=[FRAME_FG_COLOR, BACKGROUND_COLOR],
            corner_radius=10,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        orders_table.pack(expand=True, fill="both", padx=8, pady=8)

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
        """Load and display favorite restaurants and menu items in the favorites tab"""
        # Clear existing widgets
        for widget in self.favorites_scroll_frame.winfo_children():
            widget.destroy()

        # Get favorite restaurants and menu items
        fav_restaurants = self.user.get_favorite_restaurants()
        fav_menu_items = self.user.get_favorite_menu_items()
        
        row = 0
        
        # Display favorite restaurants
        if fav_restaurants:
            ctk.CTkLabel(self.favorites_scroll_frame, text="Favorite Restaurants", 
                        font=ctk.CTkFont(size=18, weight="bold"), 
                        text_color=PRIMARY_COLOR).grid(row=row, column=0, sticky="w", pady=(10, 8))
            row += 1
            
            for restaurant in fav_restaurants:
                fav_card = ctk.CTkFrame(self.favorites_scroll_frame, fg_color=BACKGROUND_COLOR, 
                                       border_width=1, border_color=FRAME_BORDER_COLOR, corner_radius=8)
                fav_card.grid(row=row, column=0, pady=(0, 8), sticky="ew", padx=10)
                fav_card.grid_columnconfigure(0, weight=1)                
                ctk.CTkLabel(fav_card, text=restaurant.name, font=ctk.CTkFont(size=16, weight="bold"), 
                           text_color=TEXT_COLOR).pack(pady=8)
                ctk.CTkButton(fav_card, text="View Menu", fg_color=PRIMARY_COLOR, 
                            hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=14, weight="bold"),  # Added explicit size 14
                            command=lambda r=restaurant: self.show_menu_callback(r)).pack(pady=(0, 8))
                row += 1

        # Display favorite menu items
        if fav_menu_items:
            ctk.CTkLabel(self.favorites_scroll_frame, text="Favorite Menu Items", 
                        font=ctk.CTkFont(size=18, weight="bold"), 
                        text_color=PRIMARY_COLOR).grid(row=row, column=0, sticky="w", pady=(20, 8))
            row += 1
            
            for menu_item in fav_menu_items:
                item_card = ctk.CTkFrame(self.favorites_scroll_frame, fg_color=BACKGROUND_COLOR, 
                                        border_width=1, border_color=FRAME_BORDER_COLOR, corner_radius=8)
                item_card.grid(row=row, column=0, pady=(0, 8), sticky="ew", padx=10)
                item_card.grid_columnconfigure(0, weight=1)
                
                ctk.CTkLabel(item_card, text=f"{menu_item.name} - ₹{menu_item.price}", 
                           font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_COLOR).pack(pady=8)
                row += 1

        # If no favorites
        if not fav_restaurants and not fav_menu_items:
            ctk.CTkLabel(self.favorites_scroll_frame, text="No favorites yet! Start exploring restaurants and adding your favorites.", 
                        font=ctk.CTkFont(size=16), text_color=GRAY_TEXT_COLOR).grid(row=0, column=0, pady=50)

    def load_order_history(self):
        """Load and display order history in the orders tab"""
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
            ctk.CTkLabel(self.orders_scroll_frame, text="No orders yet! Browse restaurants and place your first order.", 
                        font=ctk.CTkFont(size=16), text_color=GRAY_TEXT_COLOR).grid(row=0, column=0, pady=50)
            return

        # Display orders
        for i, order in enumerate(orders):
            order_card = ctk.CTkFrame(self.orders_scroll_frame, fg_color=BACKGROUND_COLOR, 
                                     border_width=1, border_color=FRAME_BORDER_COLOR, corner_radius=8)
            order_card.grid(row=i, column=0, pady=(0, 10), sticky="ew", padx=10)
            order_card.grid_columnconfigure(0, weight=1)            # Order details
            header_text = f"Order #{order.order_id} - {order.status}"
            ctk.CTkLabel(order_card, text=header_text, font=ctk.CTkFont(size=16, weight="bold"), 
                        text_color=PRIMARY_COLOR).pack(pady=(10, 5))
            
            ctk.CTkLabel(order_card, text=f"Total: ₹{order.total_amount}", 
                        font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=2)
            
            if hasattr(order, 'created_at'):
                ctk.CTkLabel(order_card, text=f"Ordered: {order.created_at}", 
                           font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR).pack(pady=(2, 10))

    def show_profile_popup(self):
        """Show profile popup window with user data and options using CTkTabview"""        # Destroy any previous profile popup
        if hasattr(self, 'profile_popup') and self.profile_popup and self.profile_popup.winfo_exists():
            self.profile_popup.destroy()
            
        self.profile_popup = ctk.CTkToplevel(self)
        self.profile_popup.title("User Profile")
        self.profile_popup.geometry("550x650")
        
        # Center the popup window
        self.profile_popup.update_idletasks()  # Ensure geometry is updated
        width = 550
        height = 650
        screen_width = self.profile_popup.winfo_screenwidth()
        screen_height = self.profile_popup.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.profile_popup.geometry(f"{width}x{height}+{x}+{y}")
        
        set_swigato_icon(self.profile_popup)
        self.profile_popup.grab_set()
        self.profile_popup.configure(fg_color=BACKGROUND_COLOR)
        self.profile_popup.grid_columnconfigure(0, weight=1)
        self.profile_popup.grid_rowconfigure(1, weight=1)

        # Header with gradient-like effect
        header_frame = ctk.CTkFrame(self.profile_popup, fg_color=PRIMARY_COLOR, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.pack_propagate(False)

        header_label = ctk.CTkLabel(
            header_frame,
            text="👤 User Profile",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        header_label.grid(row=0, column=0, pady=20)        # Main TabView with proper theme colors
        tabview = ctk.CTkTabview(
            self.profile_popup, 
            width=520, 
            height=550, 
            corner_radius=15,
            fg_color=FRAME_FG_COLOR,
            segmented_button_fg_color=BACKGROUND_COLOR,
            segmented_button_selected_color=PRIMARY_COLOR,
            segmented_button_selected_hover_color=BUTTON_HOVER_COLOR,
            segmented_button_unselected_color=FRAME_FG_COLOR,
            segmented_button_unselected_hover_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR,
            text_color_disabled=GRAY_TEXT_COLOR
        )
        tabview.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        
        # Add tabs
        tabview.add("Account Info")
        tabview.add("Change Password")
        tabview.add("Change Username")
          # --- Account Info Tab ---
        account_tab = tabview.tab("Account Info")
        account_tab.grid_columnconfigure(0, weight=1)
        account_tab.configure(fg_color=BACKGROUND_COLOR)
        
        # Account info section
        info_frame = ctk.CTkFrame(account_tab, fg_color=FRAME_FG_COLOR, corner_radius=12, border_width=1, border_color=FRAME_BORDER_COLOR)
        info_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="📋 Account Information", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=0, column=0, columnspan=2, pady=(15, 20))
        
        # Username row
        ctk.CTkLabel(info_frame, text="Username:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=1, column=0, sticky="w", padx=(15, 10), pady=8)
        ctk.CTkLabel(info_frame, text=self.user.username, 
                    font=ctk.CTkFont(size=14), 
                    text_color=TEXT_COLOR).grid(row=1, column=1, sticky="w", padx=(0, 15), pady=8)

        # Email row
        email = getattr(self.user, 'email', 'N/A')
        ctk.CTkLabel(info_frame, text="Email:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=2, column=0, sticky="w", padx=(15, 10), pady=8)
        ctk.CTkLabel(info_frame, text=email, 
                    font=ctk.CTkFont(size=14), 
                    text_color=TEXT_COLOR).grid(row=2, column=1, sticky="w", padx=(0, 15), pady=8)

        # Address row
        address = getattr(self.user, 'address', 'N/A')
        ctk.CTkLabel(info_frame, text="Address:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=3, column=0, sticky="w", padx=(15, 10), pady=(8, 15))
        ctk.CTkLabel(info_frame, text=address, 
                    font=ctk.CTkFont(size=14), 
                    text_color=TEXT_COLOR).grid(row=3, column=1, sticky="w", padx=(0, 15), pady=(8, 15))
        
        # --- Change Password Tab ---
        password_tab = tabview.tab("Change Password")
        password_tab.grid_columnconfigure(0, weight=1)
        password_tab.configure(fg_color=BACKGROUND_COLOR)
        
        password_frame = ctk.CTkFrame(password_tab, fg_color=FRAME_FG_COLOR, corner_radius=12, border_width=1, border_color=FRAME_BORDER_COLOR)
        password_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(password_frame, text="🔒 Change Password", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=0, column=0, pady=(20, 15))

        # Password fields with modern styling and proper theme colors
        self.old_password_entry = ctk.CTkEntry(password_frame, 
                                             show="*", 
                                             placeholder_text="Current Password", 
                                             width=350, 
                                             height=40,
                                             font=ctk.CTkFont(size=14),
                                             corner_radius=10,
                                             fg_color=BACKGROUND_COLOR,
                                             border_color=FRAME_BORDER_COLOR,
                                             text_color=TEXT_COLOR,
                                             placeholder_text_color=GRAY_TEXT_COLOR)
        self.old_password_entry.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="ew")

        self.new_password_entry = ctk.CTkEntry(password_frame, 
                                             show="*", 
                                             placeholder_text="New Password", 
                                             width=350, 
                                             height=40,
                                             font=ctk.CTkFont(size=14),
                                             corner_radius=10,
                                             fg_color=BACKGROUND_COLOR,
                                             border_color=FRAME_BORDER_COLOR,
                                             text_color=TEXT_COLOR,
                                             placeholder_text_color=GRAY_TEXT_COLOR)
        self.new_password_entry.grid(row=2, column=0, pady=(0, 15), padx=20, sticky="ew")

        self.confirm_password_entry = ctk.CTkEntry(password_frame, 
                                                 show="*", 
                                                 placeholder_text="Confirm New Password", 
                                                 width=350, 
                                                 height=40,
                                                 font=ctk.CTkFont(size=14),
                                                 corner_radius=10,
                                                 fg_color=BACKGROUND_COLOR,
                                                 border_color=FRAME_BORDER_COLOR,
                                                 text_color=TEXT_COLOR,
                                                 placeholder_text_color=GRAY_TEXT_COLOR)
        self.confirm_password_entry.grid(row=3, column=0, pady=(0, 15), padx=20, sticky="ew")

        # Password message label
        self.password_message = ctk.CTkLabel(password_frame, text="", 
                                           font=ctk.CTkFont(size=12), 
                                           text_color=SUCCESS_COLOR)
        self.password_message.grid(row=4, column=0, pady=(0, 15))

        # Change password button with modern styling
        change_pw_btn = ctk.CTkButton(password_frame, 
                                     text="🔐 Change Password", 
                                     fg_color=PRIMARY_COLOR, 
                                     hover_color=BUTTON_HOVER_COLOR, 
                                     text_color="white", 
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     height=45,
                                     corner_radius=10,
                                     command=self.change_password_popup)
        change_pw_btn.grid(row=5, column=0, pady=(0, 20), padx=20)
        
        # --- Change Username Tab ---
        username_tab = tabview.tab("Change Username")
        username_tab.grid_columnconfigure(0, weight=1)
        username_tab.configure(fg_color=BACKGROUND_COLOR)
        
        username_frame = ctk.CTkFrame(username_tab, fg_color=FRAME_FG_COLOR, corner_radius=12, border_width=1, border_color=FRAME_BORDER_COLOR)
        username_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        username_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(username_frame, text="✏️ Change Username", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=PRIMARY_COLOR).grid(row=0, column=0, pady=(20, 15))

        # Username field with modern styling and proper theme colors
        self.new_username_entry = ctk.CTkEntry(username_frame, 
                                             placeholder_text="New Username", 
                                             width=350, 
                                             height=40,
                                             font=ctk.CTkFont(size=14),
                                             corner_radius=10,
                                             fg_color=BACKGROUND_COLOR,
                                             border_color=FRAME_BORDER_COLOR,
                                             text_color=TEXT_COLOR,
                                             placeholder_text_color=GRAY_TEXT_COLOR)
        self.new_username_entry.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="ew")

        # Username message label
        self.username_message = ctk.CTkLabel(username_frame, text="", 
                                           font=ctk.CTkFont(size=12), 
                                           text_color=SUCCESS_COLOR)
        self.username_message.grid(row=2, column=0, pady=(0, 15))

        # Change username button with modern styling
        change_username_btn = ctk.CTkButton(username_frame, 
                                           text="👤 Change Username", 
                                           fg_color=PRIMARY_COLOR, 
                                           hover_color=BUTTON_HOVER_COLOR, 
                                           text_color="white", 
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           height=45,
                                           corner_radius=10,
                                           command=self.change_username_popup)
        change_username_btn.grid(row=3, column=0, pady=(0, 20), padx=20)

        # Close button at the bottom
        close_btn = ctk.CTkButton(self.profile_popup, 
                                 text="❌ Close", 
                                 fg_color=ERROR_COLOR, 
                                 hover_color=BUTTON_HOVER_COLOR, 
                                 text_color="white", 
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 height=40,
                                 width=120,
                                 corner_radius=10,
                                 command=self.profile_popup.destroy)
        close_btn.grid(row=2, column=0, pady=(0, 15))

    def change_password_popup(self):
        """Handle password change from popup"""
        old = self.old_password_entry.get()
        new = self.new_password_entry.get()
        confirm = self.confirm_password_entry.get()
        
        if not old or not new or not confirm:
            self.password_message.configure(text="All fields are required.", text_color=ERROR_COLOR)
            return
            
        if new != confirm:
            self.password_message.configure(text="New passwords do not match.", text_color=ERROR_COLOR)
            return
            
        if not self.user.verify_password(old):
            self.password_message.configure(text="Current password is incorrect.", text_color=ERROR_COLOR)
            return
            
        # Attempt to update password
        try:
            success = self.user.update_password(new)
            if success:
                self.password_message.configure(text="Password changed successfully!", text_color=SUCCESS_COLOR)
                # Clear fields
                self.old_password_entry.delete(0, 'end')
                self.new_password_entry.delete(0, 'end')
                self.confirm_password_entry.delete(0, 'end')
            else:
                self.password_message.configure(text="Failed to change password.", text_color=ERROR_COLOR)
        except Exception as e:
            self.password_message.configure(text=f"Error: {str(e)}", text_color=ERROR_COLOR)

    def change_username_popup(self):
        """Handle username change from popup"""
        new_username = self.new_username_entry.get().strip()
        
        if not new_username:
            self.username_message.configure(text="Username cannot be empty.", text_color=ERROR_COLOR)
            return
            
        if new_username == self.user.username:
            self.username_message.configure(text="New username is the same as current.", text_color=ERROR_COLOR)
            return
            
        # Attempt to update username
        try:
            # Check if username is already taken
            from users.models import User
            existing_user = User.get_by_username(new_username)
            if existing_user:
                self.username_message.configure(text="Username already exists.", text_color=ERROR_COLOR)
                return
                
            # Update username
            old_username = self.user.username
            self.user.username = new_username
            success = self.user.save()  # Assuming there's a save method
            
            if success:
                self.username_message.configure(text="Username changed successfully!", text_color=SUCCESS_COLOR)
                # Update welcome label
                self.welcome_label.configure(text=f"Welcome, {self.user.username}!")
                # Clear field
                self.new_username_entry.delete(0, 'end')
            else:
                self.user.username = old_username  # Revert on failure
                self.username_message.configure(text="Failed to change username.", text_color=ERROR_COLOR)
        except Exception as e:
            self.username_message.configure(text=f"Error: {str(e)}", text_color=ERROR_COLOR)

    def load_cart_items(self):
        """Load and display cart items in the cart tab"""
        # Clear existing widgets
        for widget in self.cart_scroll_frame.winfo_children():
            widget.destroy()

        # Get cart from the app reference
        cart = getattr(self.app_ref, 'cart', None)
        
        if not cart or not cart.items:
            # Empty cart message
            empty_label = ctk.CTkLabel(
                self.cart_scroll_frame, 
                text="Your cart is empty.\nBrowse restaurants and add items to get started!",
                font=ctk.CTkFont(size=16), 
                text_color=GRAY_TEXT_COLOR,
                justify="center"
            )
            empty_label.pack(pady=50)
            return

        # Display cart items
        for i, cart_item in enumerate(cart.items.values()):
            self._add_cart_item_card(self.cart_scroll_frame, cart_item)

        # Add checkout section at the bottom
        checkout_frame = ctk.CTkFrame(self.cart_scroll_frame, fg_color=FRAME_FG_COLOR, corner_radius=12)
        checkout_frame.pack(fill="x", pady=(20, 10), padx=10)
        checkout_frame.grid_columnconfigure(0, weight=1)
        checkout_frame.grid_columnconfigure(1, weight=0)

        total_price = cart.get_total_price()
        total_label = ctk.CTkLabel(
            checkout_frame, 
            text=f"Total: ₹{total_price:.2f}", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=PRIMARY_COLOR
        )
        total_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        checkout_button = ctk.CTkButton(
            checkout_frame,
            text="Proceed to Checkout",
            command=self._handle_checkout,
            fg_color=SUCCESS_COLOR,
            hover_color="#00C78C",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=40,
            corner_radius=8
        )
        checkout_button.grid(row=0, column=1, padx=15, pady=15)

    def _add_cart_item_card(self, parent_frame, cart_item):
        """Add a cart item card to the parent frame"""
        item_card = ctk.CTkFrame(
            parent_frame, 
            fg_color=BACKGROUND_COLOR, 
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=12
        )
        item_card.pack(pady=8, padx=10, fill="x")
        item_card.grid_columnconfigure(1, weight=1)

        # Item name
        item_name_label = ctk.CTkLabel(
            item_card, 
            text=cart_item.menu_item.name, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=TEXT_COLOR,
            anchor="w"
        )
        item_name_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="ew")

        # Item price
        item_price_label = ctk.CTkLabel(
            item_card, 
            text=f"₹{cart_item.menu_item.price:.2f} each", 
            font=ctk.CTkFont(size=12), 
            text_color=GRAY_TEXT_COLOR,
            anchor="w"
        )
        item_price_label.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        # Quantity controls
        quantity_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        quantity_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="e")

        minus_button = ctk.CTkButton(
            quantity_frame, 
            text="−", 
            width=32, 
            height=32,
            fg_color=SECONDARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda ci=cart_item: self._update_cart_quantity(ci, -1)
        )
        minus_button.pack(side="left", padx=(0, 5))

        quantity_label = ctk.CTkLabel(
            quantity_frame, 
            text=str(cart_item.quantity), 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=TEXT_COLOR,
            width=40
        )
        quantity_label.pack(side="left", padx=5)

        plus_button = ctk.CTkButton(
            quantity_frame, 
            text="+", 
            width=32, 
            height=32,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda ci=cart_item: self._update_cart_quantity(ci, 1)
        )
        plus_button.pack(side="left", padx=(5, 0))

        # Item total
        item_total_label = ctk.CTkLabel(
            item_card, 
            text=f"₹{cart_item.item_total:.2f}", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        item_total_label.grid(row=0, column=3, rowspan=2, padx=15, pady=10, sticky="e")
        
        # Remove button
        remove_button = ctk.CTkButton(
            item_card, 
            text="Remove", 
            width=80, 
            height=32,
            fg_color=ERROR_COLOR, 
            hover_color="#C00000",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda item_id=cart_item.menu_item.item_id: self._remove_cart_item(item_id)
        )
        remove_button.grid(row=0, column=4, rowspan=2, padx=15, pady=10, sticky="e")

    def _update_cart_quantity(self, cart_item, change):
        """Update quantity of an item in the cart"""
        cart = getattr(self.app_ref, 'cart', None)
        if not cart:
            return
            
        new_quantity = cart_item.quantity + change
        if new_quantity <= 0:
            self._remove_cart_item(cart_item.menu_item.item_id)
        else:
            if change > 0:
                cart.add_item(cart_item.menu_item, change)
            elif change < 0:
                cart.remove_item(cart_item.menu_item.item_id, abs(change))
        self.load_cart_items()

    def _remove_cart_item(self, menu_item_id):
        """Remove an item from the cart"""
        cart = getattr(self.app_ref, 'cart', None)
        if cart:
            cart.remove_item(menu_item_id)
            self.load_cart_items()

    def _handle_checkout(self):
        """Handle checkout process"""
        # Use the original cart screen checkout functionality
        if hasattr(self.app_ref, 'handle_checkout'):
            self.app_ref.handle_checkout()
        else:
            # Fallback to showing cart screen
            self.show_cart_callback()

    def refresh_cart_if_visible(self):
        """Refresh cart content if cart is currently visible"""
        if hasattr(self, 'current_nav_tab') and self.current_nav_tab == "cart":
            self.load_cart_items()
