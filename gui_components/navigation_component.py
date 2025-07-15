import customtkinter as ctk
from gui_Light import *


class NavigationComponent(ctk.CTkFrame):
    """Simplified navigation component"""
    
    def __init__(self, parent, nav_callback, logout_callback, **kwargs):
        super().__init__(parent, fg_color=FRAME_FG_COLOR, height=80, corner_radius=15, 
                         border_width=1, border_color=FRAME_BORDER_COLOR, **kwargs)
        
        self.nav_callback = nav_callback
        self.logout_callback = logout_callback
        self.current_tab = "home"
        self.nav_buttons = {}
        
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        
        self.create_navigation()
        
    def create_navigation(self):
        """Create navigation buttons"""
        # Navigation container
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=0, column=1, pady=15)
        
        # Navigation items
        nav_items = [
            ("home", "🏠", "Home"),
            ("orders", "📋", "Orders"),
            ("favorites", "⭐", "Favorites"),
            ("cart", "🛒", "Cart")
        ]
        
        # Create buttons
        for i, (key, icon, label) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_frame,
                text=icon,
                width=50,
                height=50,
                fg_color="transparent",
                hover_color=HOVER_BG_COLOR,
                text_color=GRAY_TEXT_COLOR,
                font=ctk.CTkFont(size=20),
                corner_radius=12,
                command=lambda k=key: self.handle_nav_click(k)
            )
            btn.grid(row=0, column=i, padx=10)
            self.nav_buttons[key] = btn
            
        # Logout button
        logout_btn = ctk.CTkButton(
            self,
            text="Logout",
            command=self.logout_callback,
            fg_color=SECONDARY_COLOR,
            hover_color="#B91C1C",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80,
            height=35,
            corner_radius=8
        )
        logout_btn.grid(row=0, column=2, padx=20, pady=15)
        
        # Set initial active tab
        self.set_active_tab("home")
        
    def handle_nav_click(self, tab_name):
        """Handle navigation button clicks"""
        self.set_active_tab(tab_name)
        self.nav_callback(tab_name)
        
    def set_active_tab(self, active_tab):
        """Set the active navigation tab"""
        self.current_tab = active_tab
        
        # Update button styles
        for tab_name, button in self.nav_buttons.items():
            if tab_name == active_tab:
                button.configure(
                    fg_color=PRIMARY_COLOR,
                    text_color="white"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=GRAY_TEXT_COLOR
                )
