import customtkinter as ctk
from PIL import Image, ImageTk
from gui_Light import (
    BACKGROUND_COLOR, FRAME_FG_COLOR, FRAME_BORDER_COLOR, PRIMARY_COLOR,
    BUTTON_HOVER_COLOR, TEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_TEXT_COLOR,
    GRAY_TEXT_COLOR, SECONDARY_COLOR
)
from utils.image_loader import load_image
from cart.models import CartItem

class CartScreen(ctk.CTkFrame):
    def __init__(self, master, user, cart, show_main_app_callback, show_menu_callback, checkout_callback):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.app = master
        self.user = user 
        self.cart = cart 
        self.show_main_app_callback = show_main_app_callback
        self.show_menu_callback = show_menu_callback
        self.checkout_callback = checkout_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header Frame
        self.grid_rowconfigure(1, weight=1)  # Scrollable Frame
        self.grid_rowconfigure(2, weight=0)  # Bottom Navigation Bar

        # Modern Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Title - centered, modern styling
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Your Shopping Cart", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color=PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0, sticky="ew")

        # Scrollable Frame for Cart Items
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=BACKGROUND_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        self.scrollable_frame.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Footer Frame for Total and Checkout
        self.footer_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=FRAME_FG_COLOR, corner_radius=12)
        
        self.footer_frame.grid_columnconfigure(0, weight=1)  # Total label side
        self.footer_frame.grid_columnconfigure(1, weight=0)  # Button (natural width)        self.footer_frame.grid_columnconfigure(2, weight=1)  # Right spacer for centering button

        self.total_price_label = ctk.CTkLabel(
            self.footer_frame, 
            text="Total: ₹0.00", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=PRIMARY_COLOR
        )
        self.total_price_label.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="w")

        self.checkout_button = ctk.CTkButton(
            self.footer_frame,
            text="Proceed to Checkout",
            command=self.checkout_callback,
            fg_color=SUCCESS_COLOR,
            hover_color="#00C78C",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=40,
            corner_radius=8
        )
        self.checkout_button.grid(row=0, column=1, padx=15, pady=15)

        self.empty_cart_label = ctk.CTkLabel(
            self.scrollable_frame, 
            text="Your cart is empty.\nBrowse restaurants and add items to get started!", 
            font=ctk.CTkFont(size=16), 
            text_color=GRAY_TEXT_COLOR,
            justify="center"        )
        
        self.load_cart_items()

        # --- Bottom Navigation Bar ---
        self.create_bottom_nav_bar()

    def load_cart_items(self):
        # Clear previous item cards only
        for widget in self.scrollable_frame.winfo_children():
            if widget not in [self.empty_cart_label, self.footer_frame] and isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        # Ensure footer and empty_cart_label are initially unmanaged by pack before repacking
        self.empty_cart_label.pack_forget()
        self.footer_frame.pack_forget()

        if not self.cart or not self.cart.items:
            self.empty_cart_label.pack(pady=20, padx=10, anchor="center", fill="x")
            self.total_price_label.configure(text="Total: ₹0.00")
            self.checkout_button.configure(state="disabled")
        else:
            self.checkout_button.configure(state="normal")
            cart_items = self.cart.items.values()
            for i, cart_item_obj in enumerate(cart_items):
                self._add_cart_item_card(self.scrollable_frame, cart_item_obj, i)

        # Always pack the footer at the bottom of the scrollable_frame's content
        self.footer_frame.pack(side="bottom", fill="x", pady=(15,5), padx=5)

        self.update_total_price()

    def _add_cart_item_card(self, parent_frame, cart_item: CartItem, index: int):
        item_card = ctk.CTkFrame(
            parent_frame, 
            fg_color=FRAME_FG_COLOR, 
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            corner_radius=12
        )
        item_card.pack(pady=8, padx=10, fill="x")
        item_card.grid_columnconfigure(1, weight=1)
        item_card.grid_columnconfigure(3, weight=0)
        item_card.grid_columnconfigure(5, weight=0)

        item_name_label = ctk.CTkLabel(
            item_card, 
            text=cart_item.menu_item.name, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=TEXT_COLOR,
            anchor="w"
        )
        item_name_label.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="ew")

        item_price_label = ctk.CTkLabel(
            item_card, 
            text=f"₹{cart_item.menu_item.price:.2f} each", 
            font=ctk.CTkFont(size=12), 
            text_color=GRAY_TEXT_COLOR,
            anchor="w"
        )
        item_price_label.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        quantity_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        quantity_frame.grid(row=0, column=3, rowspan=2, padx=10, pady=10, sticky="e")

        minus_button = ctk.CTkButton(
            quantity_frame, 
            text="−", 
            width=32, 
            height=32,
            fg_color=SECONDARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),            command=lambda ci=cart_item: self._update_quantity(ci, -1)
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
            command=lambda ci=cart_item: self._update_quantity(ci, 1)
        )
        plus_button.pack(side="left", padx=(5, 0))

        item_total_label = ctk.CTkLabel(
            item_card, 
            text=f"₹{cart_item.item_total:.2f}", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        item_total_label.grid(row=0, column=4, rowspan=2, padx=15, pady=10, sticky="e")
        
        remove_button = ctk.CTkButton(
            item_card, 
            text="Remove", 
            width=80, 
            height=32,
            fg_color=ERROR_COLOR, 
            hover_color="#C00000",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda item_id=cart_item.menu_item.item_id: self._remove_item(item_id)
        )
        remove_button.grid(row=0, column=5, rowspan=2, padx=15, pady=10, sticky="e")

    def _update_quantity(self, cart_item: CartItem, change: int):
        new_quantity = cart_item.quantity + change
        if new_quantity <= 0:
            self._remove_item(cart_item.menu_item.item_id)
        else:
            if self.cart:
                if change > 0:
                    self.cart.add_item(cart_item.menu_item, change)
                elif change < 0:
                    self.cart.remove_item(cart_item.menu_item.item_id, abs(change))
            self.load_cart_items()

    def _remove_item(self, menu_item_id: str):
        if self.cart:
            self.cart.remove_item(menu_item_id)
            self.load_cart_items()

    def update_total_price(self):
        if self.cart:
            total = self.cart.get_total_price()
            self.total_price_label.configure(text=f"Total: ₹{total:.2f}")
        else:
            self.total_price_label.configure(text="Total: ₹0.00")

    def update_cart_display(self, user, cart):
        self.user = user
        self.cart = cart
        self.load_cart_items()
        if self.user:
            self.title_label.configure(text=f"{self.user.username}'s Shopping Cart")
        else:
            self.title_label.configure(text="Your Shopping Cart")

    def create_bottom_nav_bar(self):
        """Create the bottom navigation bar with icon buttons"""
        bottom_nav_frame = ctk.CTkFrame(self, fg_color=FRAME_FG_COLOR, height=80, corner_radius=12)
        bottom_nav_frame.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="ew")
        bottom_nav_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Equal spacing for 6 columns
        bottom_nav_frame.pack_propagate(False)        # Icon button style (default/inactive state)
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
            "border_width": 0
        }        # Cart Button 🛒 (highlighted/active)
        cart_btn = ctk.CTkButton(bottom_nav_frame, text="🛒", 
                                command=lambda: None,  # Cart is already active
                                **active_button_style)
        cart_btn.grid(row=0, column=0, padx=10, pady=(15, 5), sticky="")
        
        cart_label = ctk.CTkLabel(bottom_nav_frame, text="Cart", 
                                 font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        cart_label.grid(row=1, column=0, pady=(0, 5), sticky="")

        # Restaurants Button 🍽️
        restaurants_btn = ctk.CTkButton(bottom_nav_frame, text="🍽️", 
                                      command=self.go_home, **button_style)
        restaurants_btn.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="")
        
        restaurants_label = ctk.CTkLabel(bottom_nav_frame, text="Home", 
                                       font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        restaurants_label.grid(row=1, column=1, pady=(0, 5), sticky="")# Orders Button 📋 (only for non-admin)
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            orders_btn = ctk.CTkButton(bottom_nav_frame, text="📋", 
                                     command=self.show_orders, **button_style)
            orders_btn.grid(row=0, column=2, padx=10, pady=(15, 5), sticky="")
            
            orders_label = ctk.CTkLabel(bottom_nav_frame, text="Orders", 
                                       font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
            orders_label.grid(row=1, column=2, pady=(0, 5), sticky="")

        # Favorites Button ❤️
        favorites_btn = ctk.CTkButton(bottom_nav_frame, text="❤️", 
                                    command=self.show_favorites, **button_style)
        next_col = 3 if not (hasattr(self.user, "is_admin") and self.user.is_admin) else 2
        favorites_btn.grid(row=0, column=next_col, padx=10, pady=(15, 5), sticky="")
        
        favorites_label = ctk.CTkLabel(bottom_nav_frame, text="Favorites", 
                                     font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        favorites_label.grid(row=1, column=next_col, pady=(0, 5), sticky="")

        # Profile Button 👤
        profile_btn = ctk.CTkButton(bottom_nav_frame, text="👤", 
                                   command=self.show_profile, **button_style)
        next_col += 1
        profile_btn.grid(row=0, column=next_col, padx=10, pady=(15, 5), sticky="")
        
        profile_label = ctk.CTkLabel(bottom_nav_frame, text="Profile", 
                                    font=ctk.CTkFont(size=12), text_color=GRAY_TEXT_COLOR)
        profile_label.grid(row=1, column=next_col, pady=(0, 5), sticky="")
        
        # Logout Button (larger, different style)
        logout_btn = ctk.CTkButton(bottom_nav_frame, text="Logout", 
                                  command=self.logout,
                                  fg_color=SECONDARY_COLOR,
                                  hover_color=BUTTON_HOVER_COLOR,
                                  text_color=BUTTON_TEXT_COLOR,
                                  font=ctk.CTkFont(size=16, weight="bold"),  # Increased from 14 to 16
                                  width=100, height=45, corner_radius=8)
        logout_btn.grid(row=0, column=5, rowspan=2, padx=20, pady=15, sticky="")

    def go_home(self):
        """Navigate back to the main app/restaurant list"""
        self.show_main_app_callback(self.user)

    def show_orders(self):
        """Show orders - navigate to main app and switch to orders content"""
        # Navigate to main app first
        self.show_main_app_callback(self.user)
        # Schedule switching to orders content after the main app loads
        self.after(100, self._switch_to_orders)

    def show_favorites(self):
        """Show favorites - navigate to main app and switch to favorites content"""
        # Navigate to main app first
        self.show_main_app_callback(self.user)
        # Schedule switching to favorites content after the main app loads
        self.after(100, self._switch_to_favorites)

    def show_profile(self):
        """Show profile - navigate to main app and switch to profile content"""
        # Navigate to main app first
        self.show_main_app_callback(self.user)
        # Schedule switching to profile content after the main app loads
        self.after(100, self._switch_to_profile)

    def logout(self):
        """Handle logout functionality"""
        # Navigate to main app and trigger logout
        self.show_main_app_callback(self.user)
        # Schedule logout after main app loads
        self.after(100, self._trigger_logout)

    def _trigger_logout(self):
        """Helper method to trigger logout after main app loads"""
        if hasattr(self.app, 'current_screen_frame') and hasattr(self.app.current_screen_frame, 'logout_callback'):
            self.app.current_screen_frame.logout_callback()

    def _switch_to_orders(self):
        """Helper method to switch to orders content after main app loads"""
        if hasattr(self.app, 'current_screen_frame') and hasattr(self.app.current_screen_frame, 'show_orders_content'):
            self.app.current_screen_frame.show_orders_content()

    def _switch_to_favorites(self):
        """Helper method to switch to favorites content after main app loads"""
        if hasattr(self.app, 'current_screen_frame') and hasattr(self.app.current_screen_frame, 'show_favorites_content'):
            self.app.current_screen_frame.show_favorites_content()

    def _switch_to_profile(self):
        """Helper method to switch to profile content after main app loads"""
        if hasattr(self.app, 'current_screen_frame') and hasattr(self.app.current_screen_frame, 'show_profile_popup'):
            self.app.current_screen_frame.show_profile_popup()


