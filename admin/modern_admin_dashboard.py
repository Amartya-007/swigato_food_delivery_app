import customtkinter as ctk
import logging
import os
from PIL import Image
from gui_Light import set_swigato_icon, safe_focus, center_window
from admin.modern_admin_theme import (
    MODERN_ADMIN_BG, MODERN_ADMIN_SIDEBAR, MODERN_ADMIN_CARD, MODERN_ADMIN_ACCENT,
    MODERN_ADMIN_TEXT, MODERN_ADMIN_TEXT_SECONDARY, MODERN_ADMIN_BUTTON,
    MODERN_ADMIN_BUTTON_HOVER, MODERN_ADMIN_FONT_FAMILY, MODERN_ADMIN_FONT_SIZES,
    MODERN_ADMIN_SPACING, MODERN_ADMIN_BORDER_RADIUS, MODERN_ADMIN_STATUS,
    MODERN_ADMIN_SIDEBAR_WIDTH, MODERN_ADMIN_HEADER_HEIGHT
)
from admin.admin_users_screen import AdminUsersScreen
from admin.admin_orders_screen import AdminOrdersScreen
from admin.admin_all_order_history_screen import AdminAllOrderHistoryScreen
from admin.admin_restaurants_screen import AdminRestaurantsScreen
from admin.admin_reviews_screen import AdminReviewsScreen
from users.models import User
from restaurants.models import Restaurant
from orders.models import Order
from reviews.models import Review

logger = logging.getLogger("swigato_app.modern_admin_dashboard")

# Modern Dark Admin Theme Colors
MODERN_ADMIN_BG = "#1a1a1a"           # Dark background
MODERN_ADMIN_SIDEBAR = "#2d2d2d"      # Sidebar background
MODERN_ADMIN_CARD = "#323232"         # Card background
MODERN_ADMIN_ACCENT = "#ff6b35"       # Swigato orange accent
MODERN_ADMIN_TEXT = "#ffffff"         # White text
MODERN_ADMIN_TEXT_SECONDARY = "#b0b0b0" # Secondary text
MODERN_ADMIN_BUTTON = "#ff6b35"       # Button color
MODERN_ADMIN_BUTTON_HOVER = "#ff5722" # Button hover
MODERN_ADMIN_SUCCESS = "#4caf50"      # Success green
MODERN_ADMIN_WARNING = "#ff9800"      # Warning orange
MODERN_ADMIN_ERROR = "#f44336"        # Error red

class ModernAdminDashboard(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=MODERN_ADMIN_BG, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_screen_frame = None
        self.sidebar_buttons = []
        self.active_button = None
        self.button_to_screen_map = {}  # Map buttons to screen IDs
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Set default screen
        self.switch_screen(AdminUsersScreen, "User Management", "users")

    def create_sidebar(self):
        """Create modern sidebar with navigation and icons"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=MODERN_ADMIN_SIDEBAR_WIDTH,
            fg_color=MODERN_ADMIN_SIDEBAR,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        
        # Brand section with improved spacing
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        brand_frame.pack(fill="x", padx=MODERN_ADMIN_SPACING["xlarge"], pady=(MODERN_ADMIN_SPACING["xlarge"], MODERN_ADMIN_SPACING["large"]))
        
        # Logo and brand name
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "swigato_icon.png")
            if os.path.exists(logo_path):
                logo_img = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(45, 45)
                )
                logo_label = ctk.CTkLabel(brand_frame, image=logo_img, text="")
                logo_label.pack(side="left", padx=(0, 12))
        except:
            pass
        
        brand_label = ctk.CTkLabel(
            brand_frame,
            text="Swigato",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["title"], weight="bold"),
            text_color=MODERN_ADMIN_ACCENT
        )
        brand_label.pack(side="left", anchor="w")
        
        admin_subtitle = ctk.CTkLabel(
            brand_frame,
            text="Admin Panel",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            text_color=MODERN_ADMIN_TEXT_SECONDARY
        )
        admin_subtitle.pack(side="left", anchor="w", padx=(8, 0))
        
        # User info section with improved styling (fixed height and padding)
        user_frame = ctk.CTkFrame(
            self.sidebar, 
            fg_color=MODERN_ADMIN_CARD, 
            height=70, 
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        user_frame.pack(fill="x", padx=MODERN_ADMIN_SPACING["xlarge"], pady=(0, 15))
        
        user_avatar = ctk.CTkLabel(
            user_frame,
            text="U",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=MODERN_ADMIN_ACCENT
        )
        user_avatar.pack(side="left", padx=(15, 12), pady=20)
        
        user_info = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_info.pack(side="left", fill="both", expand=True, pady=15)
        
        username_label = ctk.CTkLabel(
            user_info,
            text=f"Welcome, {self.loggedInUser.username}",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"], weight="bold"),
            text_color=MODERN_ADMIN_TEXT,
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 2))
        
        role_label = ctk.CTkLabel(
            user_info,
            text="Administrator",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["small"]),
            text_color=MODERN_ADMIN_TEXT_SECONDARY,
            anchor="w"
        )
        role_label.pack(fill="x")
        
        # Navigation buttons with consistent spacing
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=MODERN_ADMIN_SPACING["xlarge"], pady=15)
        
        # Navigation items with full names
        nav_items = [
            ("User Management", "User Management", AdminUsersScreen, "users"),
            ("Order Management", "Order Management", AdminOrdersScreen, "orders"),
            ("All Order History", "All Order History", AdminAllOrderHistoryScreen, "all_orders"),
            ("Restaurant Management", "Restaurant Management", AdminRestaurantsScreen, "restaurants"),
            ("Review Management", "Review Management", AdminReviewsScreen, "reviews")
        ]
        
        for text, _, screen_class, screen_id in nav_items:
            button = self.create_nav_button(nav_frame, text, screen_class, screen_id)
            self.sidebar_buttons.append(button)
            self.button_to_screen_map[button] = screen_id
        
        # Bottom section with improved spacing
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=120)
        bottom_frame.pack(fill="x", padx=MODERN_ADMIN_SPACING["xlarge"], pady=(0, 30), side="bottom")
        

        
        # Back to app button (moved to top)
        back_btn = ctk.CTkButton(
            bottom_frame,
            text="Back to App",
            command=lambda: self.app_callbacks['show_main_app_screen'](self.loggedInUser),
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            fg_color=MODERN_ADMIN_CARD,
            hover_color="#4a4a4a",
            text_color=MODERN_ADMIN_TEXT,
            height=48,
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]
        )
        back_btn.pack(fill="x", pady=(0, 12))
        
        # Logout button
        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="Logout",
            command=self.logout,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            fg_color=MODERN_ADMIN_STATUS["error"],
            hover_color="#c53030",
            text_color=MODERN_ADMIN_TEXT,
            height=48,
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]
        )
        logout_btn.pack(fill="x")

    def create_nav_button(self, parent, text, screen_class, screen_id):
        """Create a modern navigation button with full name"""
        button_frame = ctk.CTkFrame(
            parent, 
            fg_color="transparent", 
            height=48,
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        button_frame.pack(fill="x", pady=7)  # Consistent 15px spacing (7+8)
        
        def on_click():
            self.switch_screen(screen_class, text, screen_id)
        
        def on_enter(event):
            if self.active_button != button_frame:
                button_frame.configure(fg_color=MODERN_ADMIN_CARD)
        
        def on_leave(event):
            if self.active_button != button_frame:
                button_frame.configure(fg_color="transparent")
        
        button_frame.bind("<Button-1>", lambda e: on_click())
        button_frame.bind("<Enter>", on_enter)
        button_frame.bind("<Leave>", on_leave)
        
        # Full name with improved typography and alignment
        text_label = ctk.CTkLabel(
            button_frame,
            text=text,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"], weight="normal"),
            text_color=MODERN_ADMIN_ACCENT,
            anchor="w"
        )
        text_label.pack(side="left", fill="x", expand=True, padx=(18, 10), pady=12)
        text_label.bind("<Button-1>", lambda e: on_click())
        
        return button_frame

    def create_main_content(self):
        """Create main content area with modern header"""
        self.main_content = ctk.CTkFrame(self, fg_color=MODERN_ADMIN_BG)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Header with modern styling
        self.header = ctk.CTkFrame(
            self.main_content, 
            fg_color=MODERN_ADMIN_CARD, 
            height=110, 
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=MODERN_ADMIN_SPACING["xlarge"], pady=(MODERN_ADMIN_SPACING["xlarge"], MODERN_ADMIN_SPACING["xlarge"]))
        self.header.grid_columnconfigure(0, weight=1)
        
        # Title with improved typography
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["heading"], weight="bold"),
            text_color=MODERN_ADMIN_TEXT
        )
        self.title_label.grid(row=0, column=0, padx=35, pady=35, sticky="w")
        
        # Stats cards with improved layout
        self.stats_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.stats_frame.grid(row=0, column=1, padx=35, pady=25, sticky="e")
        
        self.create_stats_cards()
        
        # Content area with better spacing
        self.content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=MODERN_ADMIN_SPACING["xlarge"], pady=(0, 35))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def create_stats_cards(self):
        """Create modern stats cards with vertical layout and consistent design"""
        try:
            user_count = len(User.get_all_users())
            restaurant_count = len(Restaurant.get_all())
            order_count = len(Order.get_all_orders())
            review_count = len(Review.get_all_reviews())
            
            # Modern stats data with full names
            stats = [
                ("Users", "Users", user_count, MODERN_ADMIN_STATUS["active"]),
                ("Restaurants", "Restaurants", restaurant_count, MODERN_ADMIN_STATUS["pending"]),
                ("Orders", "Orders", order_count, MODERN_ADMIN_ACCENT),
                ("Reviews", "Reviews", review_count, "#9c27b0")
            ]
            
            for i, (name, label, count, color) in enumerate(stats):
                # Card with consistent modern styling
                card = ctk.CTkFrame(
                    self.stats_frame, 
                    fg_color=MODERN_ADMIN_CARD, 
                    width=130, 
                    height=90,
                    corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"],
                    border_width=1,
                    border_color="#404040"
                )
                card.grid(row=0, column=i, padx=8)
                card.grid_propagate(False)
                
                # Vertical content container with consistent spacing
                content_frame = ctk.CTkFrame(card, fg_color="transparent")
                content_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Category name with centered alignment and consistent size
                name_label = ctk.CTkLabel(
                    content_frame,
                    text=name,
                    font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["small"], weight="bold"),
                    text_color=color,
                    width=24,
                    height=24
                )
                name_label.pack(pady=(0, 8), anchor="center")
                
                # Count with modern typography (centered)
                count_label = ctk.CTkLabel(
                    content_frame,
                    text=str(count),
                    font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["xlarge"], weight="bold"),
                    text_color=MODERN_ADMIN_TEXT
                )
                count_label.pack(pady=(0, 4), anchor="center")
                
        except Exception as e:
            logger.error(f"Error creating stats cards: {e}")

    def switch_screen(self, screen_class, title, screen_id):
        """Switch to a different admin screen with consistent button styling"""
        # Reset all buttons to default state
        for button in self.sidebar_buttons:
            button.configure(fg_color="transparent")
            # Find text label in button and reset color
            for child in button.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=MODERN_ADMIN_ACCENT)
        
        # Find and activate the correct button
        for button in self.sidebar_buttons:
            if self.button_to_screen_map.get(button) == screen_id:
                button.configure(fg_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
                # Find text label and change to white for visibility
                for child in button.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color=MODERN_ADMIN_TEXT)
                self.active_button = button
                break
        
        # Update title
        self.title_label.configure(text=title)
        
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Create new screen
        try:
            self.current_screen_frame = screen_class(
                self.content_frame,
                self.app_callbacks,
                self.loggedInUser
            )
            self.current_screen_frame.pack(fill="both", expand=True)
        except Exception as e:
            logger.error(f"Error switching to screen {screen_class}: {e}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error loading {title}",
                font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["large"]),
                text_color=MODERN_ADMIN_STATUS["error"]
            )
            error_label.pack(expand=True)

    def logout(self):
        """Handle logout"""
        self.app_callbacks['logout']()

    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            # Refresh stats
            for widget in self.stats_frame.winfo_children():
                widget.destroy()
            self.create_stats_cards()
            
            # Refresh current screen if it has a refresh method
            if self.current_screen_frame and hasattr(self.current_screen_frame, 'refresh_data'):
                self.current_screen_frame.refresh_data()
        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")

    def show_order_history(self):
        """Show admin's personal order history by navigating to main app"""
        try:
            # Simply navigate to main app screen where admin can access their order history
            # through the bottom navigation (orders tab)
            self.app_callbacks['show_main_app_screen'](self.loggedInUser)
        except Exception as e:
            logger.error(f"Error showing order history: {e}")
