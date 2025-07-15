import customtkinter as ctk
import os
from gui_Light import *
from restaurants.models import Restaurant
from utils.image_loader import load_image
from utils.logger import log


class RestaurantListComponent(ctk.CTkScrollableFrame):
    """Simplified restaurant list component"""
    
    def __init__(self, parent, app_ref, show_menu_callback, **kwargs):
        super().__init__(parent, fg_color=BACKGROUND_COLOR, border_width=0, corner_radius=0, **kwargs)
        
        self.app_ref = app_ref
        self.show_menu_callback = show_menu_callback
        self.restaurants = []
        self.grid_columnconfigure(0, weight=1)
        
    def load_restaurants(self):
        """Load restaurants from database"""
        log("RestaurantListComponent.load_restaurants called")
        self.restaurants = Restaurant.get_all()
        log(f"Loaded {len(self.restaurants)} restaurants.")
        self.display_restaurants(self.restaurants)
        
    def display_restaurants(self, restaurants):
        """Display restaurants in a simple, clean layout"""
        log(f"Displaying {len(restaurants)} restaurants.")
        
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        if not restaurants:
            no_restaurants_label = ctk.CTkLabel(
                self,
                text="No restaurants available.",
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(size=16)
            )
            no_restaurants_label.grid(row=0, column=0, pady=20)
            return
            
        # Display restaurants in simple cards
        for i, restaurant in enumerate(restaurants):
            self.create_restaurant_card(restaurant, i)
            
    def create_restaurant_card(self, restaurant, row):
        """Create a simplified restaurant card"""
        # Simple restaurant card
        card = ctk.CTkFrame(
            self,
            fg_color=FRAME_FG_COLOR,
            border_color=FRAME_BORDER_COLOR,
            border_width=1,
            corner_radius=12,
            height=120
        )
        card.grid(row=row, column=0, pady=10, padx=20, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        card.pack_propagate(False)
        
        # Restaurant image (simplified)
        image_label = self.create_restaurant_image(card, restaurant)
        image_label.grid(row=0, column=0, padx=15, pady=15, sticky="ns")
        
        # Restaurant info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=restaurant.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        )
        name_label.pack(anchor="w", pady=(0, 5))
        
        # Cuisine
        cuisine_label = ctk.CTkLabel(
            info_frame,
            text=f"🍴 {restaurant.cuisine_type or 'Variety'}",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR,
            anchor="w"
        )
        cuisine_label.pack(anchor="w", pady=(0, 5))
        
        # Rating
        rating_label = ctk.CTkLabel(
            info_frame,
            text=f"⭐ {restaurant.rating:.1f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PRIMARY_COLOR,
            anchor="w"
        )
        rating_label.pack(anchor="w")
        
        # View Menu button
        menu_btn = ctk.CTkButton(
            card,
            text="View Menu",
            command=lambda r=restaurant: self.show_menu_callback(r),
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=35,
            corner_radius=8
        )
        menu_btn.grid(row=0, column=2, padx=15, pady=15)
        
    def create_restaurant_image(self, parent, restaurant):
        """Create restaurant image with fallback"""
        if restaurant.image_filename:
            project_root = self.app_ref.project_root
            image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
            ctk_image = load_image(image_path, size=(90, 90))
            
            if ctk_image:
                return ctk.CTkLabel(parent, image=ctk_image, text="", corner_radius=8)
        
        # Fallback placeholder
        return ctk.CTkLabel(
            parent,
            text="🍽️",
            width=90,
            height=90,
            fg_color=PRIMARY_COLOR,
            text_color="white",
            font=ctk.CTkFont(size=32),
            corner_radius=8
        )
        
    def filter_restaurants(self, search_text=""):
        """Filter restaurants based on search text"""
        if not search_text:
            filtered = self.restaurants
        else:
            search_lower = search_text.lower()
            filtered = [
                r for r in self.restaurants
                if search_lower in r.name.lower() or 
                   search_lower in (r.cuisine_type or "").lower()
            ]
        
        self.display_restaurants(filtered)
