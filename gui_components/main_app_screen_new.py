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
        self.app_ref = app_ref
        self.user = user
        self.show_menu_callback = show_menu_callback
        self.show_cart_callback = show_cart_callback
        self.logout_callback = logout_callback
        self.restaurants = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        welcome_text = f"Welcome, {self.user.username}!"
        self.welcome_label = ctk.CTkLabel(header_frame, text=welcome_text,
                                          text_color=PRIMARY_COLOR,
                                          font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w")

        # --- Top-Right Buttons Frame ---
        top_right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_right_frame.grid(row=0, column=1, sticky="e")
        
        # Load cart icon
        icon_size = (28, 28)
        icon_path = lambda name: os.path.join(self.app_ref.project_root, "assets", "Icons", name)
        cart_icon = load_image(icon_path("cart.png"), size=icon_size)

        # Cart Button
        cart_btn = ctk.CTkButton(top_right_frame, text="", image=cart_icon, width=40, height=40, 
                                fg_color=FRAME_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                                command=self.show_cart_callback)
        cart_btn.pack(side="left", padx=(0, 8))

        # Admin Panel button (if admin)
        if hasattr(self.user, "is_admin") and self.user.is_admin:
            admin_panel_button = ctk.CTkButton(
                top_right_frame,
                text="Admin Panel",
                fg_color=FRAME_FG_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(weight="bold"),
                command=lambda: self.app_ref.show_admin_screen(self.user)
            )
            admin_panel_button.pack(side="left", padx=(12, 0))

        # --- Main Tab View ---
        self.main_tabview = ctk.CTkTabview(self, width=800, height=600, fg_color=BACKGROUND_COLOR)
        self.main_tabview.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        
        # Add tabs
        self.main_tabview.add("🍽️ Restaurants")
        self.main_tabview.add("⭐ Favorites")
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            self.main_tabview.add("📋 Orders")
        self.main_tabview.add("👤 Profile")

        # Set default tab
        self.main_tabview.set("🍽️ Restaurants")

        # Initialize tabs
        self.setup_restaurants_tab()
        self.setup_favorites_tab()
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            self.setup_orders_tab()
        self.setup_profile_tab()

    def setup_restaurants_tab(self):
        """Setup the main restaurants browsing tab"""
        restaurants_tab = self.main_tabview.tab("🍽️ Restaurants")
        restaurants_tab.grid_columnconfigure(0, weight=1)
        restaurants_tab.grid_rowconfigure(0, weight=1)

        # Restaurant List Scrollable Frame
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(restaurants_tab, fg_color=BACKGROUND_COLOR, border_width=0)
        self.restaurant_scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)

        self.load_restaurants()

    def setup_favorites_tab(self):
        """Setup the favorites tab"""
        favorites_tab = self.main_tabview.tab("⭐ Favorites")
        favorites_tab.grid_columnconfigure(0, weight=1)
        favorites_tab.grid_rowconfigure(1, weight=1)

        heading_label = ctk.CTkLabel(
            favorites_tab,
            text="Your Favorites",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        heading_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

        self.favorites_scroll_frame = ctk.CTkScrollableFrame(favorites_tab, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        self.favorites_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.favorites_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_favorites()

    def setup_orders_tab(self):
        """Setup the order history tab"""
        orders_tab = self.main_tabview.tab("📋 Orders")
        orders_tab.grid_columnconfigure(0, weight=1)
        orders_tab.grid_rowconfigure(1, weight=1)

        heading_label = ctk.CTkLabel(
            orders_tab,
            text="Your Order History",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        heading_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

        self.orders_scroll_frame = ctk.CTkScrollableFrame(orders_tab, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        self.orders_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.orders_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.load_order_history()

    def setup_profile_tab(self):
        """Setup the profile management tab"""
        profile_tab = self.main_tabview.tab("👤 Profile")
        profile_tab.grid_columnconfigure(0, weight=1)
        profile_tab.grid_rowconfigure(0, weight=1)

        # Profile content frame
        profile_content = ctk.CTkFrame(profile_tab, fg_color=FRAME_FG_COLOR, border_width=1, border_color=FRAME_BORDER_COLOR, corner_radius=14)
        profile_content.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        profile_content.grid_columnconfigure(0, weight=1)

        # Profile sub-tabs
        profile_tabview = ctk.CTkTabview(profile_content, width=500, height=400, fg_color=FRAME_FG_COLOR)
        profile_tabview.pack(padx=20, pady=20, fill="both", expand=True)
        profile_tabview.add("Account Info")
        profile_tabview.add("Change Password")
        profile_tabview.add("Logout")

        # --- Account Info Tab ---
        account_tab = profile_tabview.tab("Account Info")
        ctk.CTkLabel(account_tab, text="Account Information", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(20,15))
        ctk.CTkLabel(account_tab, text=f"Username: {self.user.username}", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR).pack(pady=(8,4))
        ctk.CTkLabel(account_tab, text=f"Email: {getattr(self.user, 'email', 'N/A')}", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=(4,4))
        ctk.CTkLabel(account_tab, text=f"Address: {getattr(self.user, 'address', 'N/A')}", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=(4,12))

        # --- Password Tab ---
        password_tab = profile_tabview.tab("Change Password")
        ctk.CTkLabel(password_tab, text="Change Password", font=ctk.CTkFont(size=20, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(20,15))
        
        self.old_pw_entry = ctk.CTkEntry(password_tab, show="*", placeholder_text="Current Password", width=300)
        self.old_pw_entry.pack(pady=6)
        self.new_pw_entry = ctk.CTkEntry(password_tab, show="*", placeholder_text="New Password", width=300)
        self.new_pw_entry.pack(pady=6)
        self.confirm_pw_entry = ctk.CTkEntry(password_tab, show="*", placeholder_text="Confirm New Password", width=300)
        self.confirm_pw_entry.pack(pady=6)
        
        self.pw_msg_label = ctk.CTkLabel(password_tab, text="", text_color=SUCCESS_COLOR, font=ctk.CTkFont(size=12))
        self.pw_msg_label.pack(pady=4)
        
        ctk.CTkButton(password_tab, text="Change Password", command=self.change_password, 
                     fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                     text_color=TEXT_COLOR, width=200).pack(pady=12)

        # --- Logout Tab ---
        logout_tab = profile_tabview.tab("Logout")
        ctk.CTkLabel(logout_tab, text="Logout", font=ctk.CTkFont(size=22, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(30,15))
        ctk.CTkLabel(logout_tab, text="Are you sure you want to logout?", font=ctk.CTkFont(size=16), text_color=TEXT_COLOR).pack(pady=(0,20))
        ctk.CTkButton(logout_tab, text="Logout", fg_color=SECONDARY_COLOR, hover_color=BUTTON_HOVER_COLOR, 
                     text_color=BUTTON_TEXT_COLOR, command=self.logout_callback, width=200).pack(pady=10)

    def change_password(self):
        """Handle password change"""
        old = self.old_pw_entry.get()
        new = self.new_pw_entry.get()
        confirm = self.confirm_pw_entry.get()
        
        if not old or not new or not confirm:
            self.pw_msg_label.configure(text="All fields required.", text_color=ERROR_COLOR)
            return
        if new != confirm:
            self.pw_msg_label.configure(text="New passwords do not match.", text_color=ERROR_COLOR)
            return
        if not self.user.verify_password(old):
            self.pw_msg_label.configure(text="Current password is incorrect.", text_color=ERROR_COLOR)
            return
        
        ok = self.user.update_password(new)
        if ok:
            self.pw_msg_label.configure(text="Password changed successfully!", text_color=SUCCESS_COLOR)
            # Clear fields
            self.old_pw_entry.delete(0, 'end')
            self.new_pw_entry.delete(0, 'end')
            self.confirm_pw_entry.delete(0, 'end')
        else:
            self.pw_msg_label.configure(text="Failed to change password.", text_color=ERROR_COLOR)

    def load_restaurants(self):
        """Load and display restaurants"""
        log("MainAppScreen.load_restaurants called")
        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()

        from restaurants.models import Restaurant
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
            restaurant_card.grid_columnconfigure(0, weight=0)  # Image
            restaurant_card.grid_columnconfigure(1, weight=1)  # Details
            restaurant_card.grid_columnconfigure(2, weight=0)  # Button
            restaurant_card.grid_columnconfigure(3, weight=0)  # Heart

            # Restaurant image
            image_label = None
            if restaurant.image_filename:
                project_root = self.app_ref.project_root
                image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
                log(f"Attempting to load restaurant image from: {image_path}")
                ctk_image = load_image(image_path, size=(120, 120))
                if ctk_image:
                    image_label = ctk.CTkLabel(restaurant_card, image=ctk_image, text="")
                    image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")
            if not image_label:
                image_label = ctk.CTkLabel(restaurant_card, text="No Image", width=120, height=120, 
                                         fg_color=GRAY_TEXT_COLOR, text_color=BUTTON_TEXT_COLOR)
                image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

            # Restaurant details
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
            rating_label.grid(row=2, column=0, pady=(0, 5), sticky="ew")

            # Heart/Favorite button
            is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
            heart_text = "\u2665" if is_fav else "\u2661"  # ♥ or ♡
            heart_button = ctk.CTkButton(restaurant_card, text=heart_text, width=40, fg_color="transparent", 
                                       text_color=(ERROR_COLOR if is_fav else GRAY_TEXT_COLOR), 
                                       font=ctk.CTkFont(size=22), hover_color=FRAME_BORDER_COLOR,
                                       command=lambda r=restaurant: self._toggle_favorite_restaurant(r))
            heart_button.grid(row=0, column=3, rowspan=3, padx=(0, 10), pady=10, sticky="e")

            # View Menu button
            view_menu_button = ctk.CTkButton(restaurant_card, text="View Menu",
                                             fg_color=PRIMARY_COLOR,
                                             hover_color=BUTTON_HOVER_COLOR,
                                             text_color=TEXT_COLOR,
                                             font=ctk.CTkFont(weight="bold"),
                                             width=100,
                                             command=lambda r=restaurant: self.show_menu_callback(r))
            view_menu_button.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="e")

    def _toggle_favorite_restaurant(self, restaurant):
        """Toggle favorite status for a restaurant"""
        is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
        if is_fav:
            self.user.remove_favorite_restaurant(restaurant.restaurant_id)
        else:
            self.user.add_favorite_restaurant(restaurant.restaurant_id)
        
        # Refresh restaurants and favorites tabs
        self.load_restaurants()
        self.load_favorites()

    def load_favorites(self):
        """Load and display favorite restaurants and menu items"""
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
                            hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR,
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
        """Load and display order history"""
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
            order_card.grid_columnconfigure(0, weight=1)

            # Order details
            header_text = f"Order #{order.order_id} - {order.status}"
            ctk.CTkLabel(order_card, text=header_text, font=ctk.CTkFont(size=16, weight="bold"), 
                        text_color=PRIMARY_COLOR).pack(pady=(10, 5))
            
            ctk.CTkLabel(order_card, text=f"Total: ₹{order.total_amount}", 
                        font=ctk.CTkFont(size=14), text_color=TEXT_COLOR).pack(pady=2)
            
            if hasattr(order, 'created_at'):
                ctk.CTkLabel(order_card, text=f"Ordered: {order.created_at}", 
                           font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR).pack(pady=(2, 10))
