import customtkinter as ctk
import os
from gui_Light import (BACKGROUND_COLOR, SUCCESS_COLOR, TEXT_COLOR, PRIMARY_COLOR, 
                       BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, 
                       GRAY_TEXT_COLOR, set_swigato_icon)
from utils.logger import log
from utils.image_loader import load_image
from cart.cart_ui import CartUtilities

class FavoriteRestaurantCard(ctk.CTkFrame):
    """Card component for favorite restaurant"""
    
    def __init__(self, parent, restaurant, show_menu_callback, app_ref, **kwargs):
        super().__init__(parent, **kwargs)
        self.restaurant = restaurant
        self.show_menu_callback = show_menu_callback
        self.app_ref = app_ref
        
        self.setup_card()
    
    def setup_card(self):
        """Set up the restaurant card UI with image support"""
        self.configure(
            fg_color=FRAME_FG_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            height=120
        )
        
        self.grid_columnconfigure(0, weight=0)  # Image
        self.grid_columnconfigure(1, weight=1)  # Details
        self.grid_columnconfigure(2, weight=0)  # Button
        self.pack_propagate(False)
        
        # Restaurant image
        image_container = ctk.CTkFrame(
            self, 
            fg_color="transparent", 
            corner_radius=12
        )
        image_container.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        
        image_label = None
        if self.restaurant.image_filename:
            project_root = self.app_ref.project_root if hasattr(self.app_ref, 'project_root') else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(project_root, "assets", "restaurants", self.restaurant.image_filename)
            log(f"Attempting to load restaurant image from: {image_path}")
            ctk_image = load_image(image_path, size=(80, 80))
            if ctk_image:
                image_label = ctk.CTkLabel(
                    image_container, 
                    image=ctk_image, 
                    text="", 
                    corner_radius=12
                )
                image_label.pack()
        
        if not image_label:
            # Modern placeholder with restaurant icon
            image_label = ctk.CTkLabel(
                image_container, 
                text="🏪", 
                width=80, 
                height=80,
                fg_color=PRIMARY_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=32),
                corner_radius=12
            )
            image_label.pack()
        
        # Restaurant info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        info_frame.grid_rowconfigure(0, weight=0)
        info_frame.grid_rowconfigure(1, weight=0)
        info_frame.grid_rowconfigure(2, weight=1)
        
        rest_label = ctk.CTkLabel(
            info_frame,
            text=self.restaurant.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        rest_label.grid(row=0, column=0, sticky="ew")
        
        # Add cuisine type if available
        if hasattr(self.restaurant, 'cuisine_type') and self.restaurant.cuisine_type:
            cuisine_label = ctk.CTkLabel(
                info_frame,
                text=f"🍴 {self.restaurant.cuisine_type}",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                anchor="w"
            )
            cuisine_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # View Menu button
        view_menu_btn = ctk.CTkButton(
            self,
            text="View Menu",
            command=lambda: self.show_menu_callback(self.restaurant),
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=40,
            corner_radius=12
        )
        view_menu_btn.grid(row=0, column=2, padx=(0, 20), pady=20, sticky="e")


class FavoriteMenuItemCard(ctk.CTkFrame):
    """Card component for favorite menu item"""
    
    def __init__(self, parent, menu_item, app_ref, user, **kwargs):
        super().__init__(parent, **kwargs)
        self.menu_item = menu_item
        self.app_ref = app_ref
        self.user = user
        self.parent_widget = parent
        
        self.setup_card()
    
    def setup_card(self):
        """Set up the menu item card UI with image support"""
        self.configure(
            fg_color=FRAME_FG_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            height=120
        )
        
        self.grid_columnconfigure(0, weight=0)  # Image
        self.grid_columnconfigure(1, weight=1)  # Details
        self.grid_columnconfigure(2, weight=0)  # Button
        self.pack_propagate(False)
        
        # Menu item image
        image_container = ctk.CTkFrame(
            self, 
            fg_color="transparent", 
            corner_radius=12
        )
        image_container.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        
        image_label = None
        if hasattr(self.menu_item, 'image_filename') and self.menu_item.image_filename:
            project_root = self.app_ref.project_root if hasattr(self.app_ref, 'project_root') else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(project_root, "assets", "menu_items", self.menu_item.image_filename)
            log(f"Attempting to load menu item image from: {image_path}")
            ctk_image = load_image(image_path, size=(80, 80))
            if ctk_image:
                image_label = ctk.CTkLabel(
                    image_container, 
                    image=ctk_image, 
                    text="", 
                    corner_radius=12
                )
                image_label.pack()
        
        if not image_label:
            # Modern placeholder with food icon
            image_label = ctk.CTkLabel(
                image_container, 
                text="🍽️", 
                width=80, 
                height=80,
                fg_color=SUCCESS_COLOR,
                text_color="white",
                font=ctk.CTkFont(size=32),
                corner_radius=12
            )
            image_label.pack()
        
        # Item info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        info_frame.grid_rowconfigure(0, weight=0)
        info_frame.grid_rowconfigure(1, weight=0)
        info_frame.grid_rowconfigure(2, weight=1)
        
        item_label = ctk.CTkLabel(
            info_frame,
            text=self.menu_item.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        item_label.grid(row=0, column=0, sticky="ew")
        
        price_label = ctk.CTkLabel(
            info_frame,
            text=f"💰 ₹{self.menu_item.price}",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR,
            anchor="w"
        )
        price_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Add to Cart button
        add_to_cart_btn = ctk.CTkButton(
            self,
            text="Add to Cart",
            command=self.add_to_cart,
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=40,
            corner_radius=12
        )
        add_to_cart_btn.grid(row=0, column=2, padx=(0, 20), pady=20, sticky="e")
    
    def add_to_cart(self):
        """Add item to cart using cart utilities, with error handling"""
        try:
            CartUtilities.add_to_cart_from_favorites(
                self.app_ref, 
                self.user, 
                self.menu_item, 
                self.parent_widget
            )
        except Exception as e:
            log(f"Error adding to cart from favorites: {e}")


class FavoritesListComponent(ctk.CTkScrollableFrame):
    """Component for displaying favorites list"""
    
    def __init__(self, parent, user, app_ref, show_menu_callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.user = user
        self.app_ref = app_ref
        self.show_menu_callback = show_menu_callback
        
        self.grid_columnconfigure(0, weight=1)
        
    def load_favorites(self):
        """Load and display favorite restaurants and menu items with modern design"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Get favorites
        fav_restaurants = self.user.get_favorite_restaurants()
        fav_menu_items = self.user.get_favorite_menu_items()

        row = 0

        # Modern empty state
        if not fav_restaurants and not fav_menu_items:
            empty_frame = ctk.CTkFrame(
                self,
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
                self,
                text="🏪 Favorite Restaurants",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            section_header.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 10))
            row += 1

            for rest in fav_restaurants:
                rest_card = FavoriteRestaurantCard(
                    self,
                    restaurant=rest,
                    show_menu_callback=self.show_menu_callback,
                    app_ref=self.app_ref
                )
                rest_card.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
                row += 1

        # Favorite Menu Items Section
        if fav_menu_items:
            section_header = ctk.CTkLabel(
                self,
                text="🍕 Favorite Dishes",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=TEXT_COLOR,
                anchor="w"
            )
            section_header.grid(row=row, column=0, sticky="ew", padx=20, pady=(20, 10))
            row += 1

            for item in fav_menu_items:
                item_card = FavoriteMenuItemCard(
                    self,
                    menu_item=item,
                    app_ref=self.app_ref,
                    user=self.user
                )
                item_card.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 10))
                row += 1


class FavoritesWindow:
    """Popup window for favorites"""
    
    def __init__(self, parent, user, app_ref, show_menu_callback):
        self.parent = parent
        self.user = user
        self.app_ref = app_ref
        self.show_menu_callback = show_menu_callback
        self.favorites_window = None
        
    def show_favorites_section(self):
        """Show favorites in a popup window"""
        # Destroy any previous favorites window
        if hasattr(self, 'favorites_window') and self.favorites_window:
            self.favorites_window.destroy()
            
        self.favorites_window = ctk.CTkToplevel(self.parent)
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

        scroll_frame = ctk.CTkScrollableFrame(
            self.favorites_window, 
            fg_color=FRAME_FG_COLOR, 
            corner_radius=14, 
            border_width=1, 
            border_color=FRAME_BORDER_COLOR
        )
        scroll_frame.grid(row=1, column=0, padx=24, pady=24, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        # Use the favorites list component
        favorites_list = FavoritesListComponent(
            scroll_frame,
            user=self.user,
            app_ref=self.app_ref,
            show_menu_callback=self.show_menu_callback,
            fg_color=FRAME_FG_COLOR,
            corner_radius=0,
            border_width=0
        )
        favorites_list.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack
        favorites_list.load_favorites()
