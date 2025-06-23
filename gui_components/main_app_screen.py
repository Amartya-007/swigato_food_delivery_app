import customtkinter as ctk
import os
from PIL import Image, ImageTk
from gui_Light import BACKGROUND_COLOR, SUCCESS_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR, GRAY_TEXT_COLOR, SEMI_TRANSPARENT_OVERLAY, CLOSE_BUTTON_BG, CLOSE_BUTTON_TEXT, ERROR_COLOR, BUTTON_TEXT_COLOR
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

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1) # Welcome message
        header_frame.grid_columnconfigure(1, weight=0) # Spacer
        header_frame.grid_columnconfigure(2, weight=0) # Top-right buttons frame

        welcome_text = f"Welcome, {self.user.username}!"
        self.welcome_label = ctk.CTkLabel(header_frame, text=welcome_text,
                                          text_color=PRIMARY_COLOR,
                                          font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w")

        # --- Top-Right Buttons Frame ---
        top_right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_right_frame.grid(row=0, column=2, sticky="e")
        # Load icons
        icon_size = (28, 28)
        icon_path = lambda name: os.path.join(self.app_ref.project_root, "assets", "Icons", name)
        cart_icon = load_image(icon_path("cart.png"), size=icon_size)
        favorite_icon = load_image(icon_path("favorite.png"), size=icon_size)
        order_icon = load_image(icon_path("order.png"), size=icon_size)
        profile_icon = load_image(icon_path("user.png"), size=icon_size)

        # Tooltip label (hidden by default)
        self._tooltip_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), fg_color="#222", text_color="#fff", corner_radius=6)
        self._tooltip_label.place_forget()
        def show_tooltip(text, event):
            self._tooltip_label.configure(text=text)
            self._tooltip_label.place(x=event.x_root - self.winfo_rootx() + 20, y=event.y_root - self.winfo_rooty() + 30)
        def hide_tooltip(event):
            self._tooltip_label.place_forget()

        # Cart Button
        cart_btn = ctk.CTkButton(top_right_frame, text="", image=cart_icon, width=40, height=40, fg_color=FRAME_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.show_cart_callback)
        cart_btn.pack(side="left", padx=(0, 8))
        cart_btn.bind("<Enter>", lambda e: show_tooltip("View Cart", e))
        cart_btn.bind("<Leave>", hide_tooltip)

        # Order History Button (only for non-admin)
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            order_btn = ctk.CTkButton(top_right_frame, text="", image=order_icon, width=40, height=40, fg_color=FRAME_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.show_order_history)
            order_btn.pack(side="left", padx=(0, 8))
            order_btn.bind("<Enter>", lambda e: show_tooltip("Order History", e))
            order_btn.bind("<Leave>", hide_tooltip)

        # Favorites Button
        favorites_btn = ctk.CTkButton(top_right_frame, text="", image=favorite_icon, width=40, height=40, fg_color=FRAME_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.show_favorites_section)
        favorites_btn.pack(side="left", padx=(0, 0))
        favorites_btn.bind("<Enter>", lambda e: show_tooltip("Favorites", e))
        favorites_btn.bind("<Leave>", hide_tooltip)

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

        # Profile Button (directly opens side panel)
        self.profile_panel = None
        profile_btn = ctk.CTkButton(top_right_frame, text="", image=profile_icon, width=40, height=40, fg_color=FRAME_FG_COLOR, hover_color=BUTTON_HOVER_COLOR, command=self.show_profile_panel)
        profile_btn.pack(side="left", padx=(12, 0))
        profile_btn.bind("<Enter>", lambda e: show_tooltip("Profile", e))
        profile_btn.bind("<Leave>", hide_tooltip)

        # --- Restaurant List Scrollable Frame ---
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BACKGROUND_COLOR, border_width=0)
        self.restaurant_scroll_frame.grid(row=1, column=0, padx=20, pady=(10,80), sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)

        # --- Sticky Bottom Bar for Logout (use .place() to avoid grid/pack conflict) ---
        self.bottom_bar = ctk.CTkFrame(self, fg_color=FRAME_FG_COLOR, height=60, corner_radius=0)
        self.bottom_bar.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw", y=0)
        self.bottom_bar.pack_propagate(0)
        border = ctk.CTkFrame(self.bottom_bar, fg_color=FRAME_BORDER_COLOR, height=2)
        border.pack(side="top", fill="x")

        self.logout_button = ctk.CTkButton(
            self.bottom_bar,
            text="Logout",
            command=self.logout_callback,
            fg_color=SECONDARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color=BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(weight="bold"),
            corner_radius=12,
            width=120,
            height=40
        )
        self.logout_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-10)

        self.load_restaurants()

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
            rating_label.grid(row=2, column=0, pady=(0, 5), sticky="ew")

            # Heart/Favorite button
            is_fav = self.user.is_favorite_restaurant(restaurant.restaurant_id)
            heart_text = "\u2665" if is_fav else "\u2661"  # ♥ or ♡
            heart_button = ctk.CTkButton(restaurant_card, text=heart_text, width=40, fg_color="transparent", text_color=(ERROR_COLOR if is_fav else GRAY_TEXT_COLOR), font=ctk.CTkFont(size=22), hover_color=FRAME_BORDER_COLOR,
                                         command=lambda r=restaurant, b=None: self._toggle_favorite_restaurant(r, b))
            # Use a lambda to pass the button itself after creation
            heart_button.grid(row=0, column=3, rowspan=3, padx=(0, 10), pady=10, sticky="e")
            # Patch the button reference for lambda
            heart_button.configure(command=lambda r=restaurant, b=heart_button: self._toggle_favorite_restaurant(r, b))

            view_menu_button = ctk.CTkButton(restaurant_card, text="View Menu",
                                             fg_color=PRIMARY_COLOR,
                                             hover_color=BUTTON_HOVER_COLOR,
                                             text_color=TEXT_COLOR,
                                             font=ctk.CTkFont(weight="bold"),
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
                item_label.grid(row=0, column=0, sticky="w")
                # Quick Order button
                quick_order_btn = ctk.CTkButton(row_frame, text="Quick Order", width=90, fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=12, weight="bold"),
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
        cell_font = ctk.CTkFont(size=11)
        header_font = ctk.CTkFont(size=12, weight="bold")
        orders_table = CTkTable(
            master=scroll_frame,
            values=table_data,
            font=cell_font,
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
        ctk.CTkButton(tab_password, text="Change Password", command=do_change_pw, fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR).pack(pady=12)
        # --- Logout Tab ---
        tab_logout = tabview.tab("Logout")
        ctk.CTkLabel(tab_logout, text="Are you sure you want to logout?", font=ctk.CTkFont(size=16, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(32,12))
        ctk.CTkButton(tab_logout, text="Logout", fg_color=SECONDARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, command=self.logout_callback).pack(pady=16)
        # Close button (top right)
        ctk.CTkButton(self.profile_panel, text="✕", width=32, height=32, fg_color=CLOSE_BUTTON_BG, text_color=CLOSE_BUTTON_TEXT, font=ctk.CTkFont(size=16, weight="bold"), command=self.hide_profile_panel).place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

    def hide_profile_panel(self):
        if hasattr(self, 'profile_panel') and self.profile_panel and self.profile_panel.winfo_exists():
            self.profile_panel.destroy()
            self.profile_panel = None
        if hasattr(self, 'profile_overlay') and self.profile_overlay and self.profile_overlay.winfo_exists():
            self.profile_overlay.destroy()
            self.profile_overlay = None
