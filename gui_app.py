import customtkinter as ctk
import os
import json
from tkinter import messagebox

# Import constants
from gui_Light import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, SUCCESS_COLOR, DISABLED_BUTTON_COLOR

# Import screen components
from Authentication.login_screen import LoginScreen
from Authentication.signup_screen import SignupScreen
from gui_components.simple_main_app_screen import SimpleMainAppScreen
from restaurants.menu_screen import MenuScreen
from cart.cart_screen import CartScreen
from admin.modern_admin_dashboard import ModernAdminDashboard  # Import Modern AdminDashboard
from cart.models import Cart
from users.auth import User
from orders.models import create_order

# Import for DB setup
from utils.database import initialize_database
from restaurants.models import populate_sample_restaurant_data

# Import logger
from utils.logger import log

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Swigato Food Delivery")

        # Define project_root early
        self.project_root = os.path.dirname(os.path.abspath(__file__))

        ctk.set_appearance_mode("Dark")
        
        # Set window icon
        icon_path = os.path.join(self.project_root, "assets", "swigato_icon.ico")  # Fixed path
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting window icon: {e}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_user: User | None = None
        self.current_restaurant = None
        self.cart: Cart | None = None

        self.current_screen_frame = None
        self.admin_dashboard_instance = None  # Initialize admin_dashboard_instance attribute

        # Master list for user data, to be managed by the App instance
        self.master_users_data = [
                        {'id': 1, 'username': 'Amartya', 'is_admin': True, 'address': 'Adhartal, Jabalpur, MP 482004'},
            {'id': 2, 'username': 'Rishabh', 'is_admin': False, 'address': 'Adhartal, Jabalpur, MP 482004'},
            {'id': 3, 'username': 'Siddharth', 'is_admin': False, 'address': 'Adhartal, Jabalpur, MP 482004'},
            {'id': 4, 'username': 'Anshul', 'is_admin': False, 'address': 'Adhartal, Jabalpur, MP 482004'},
            {'id': 5, 'username': 'Aayush', 'is_admin': False, 'address': 'Adhartal, Jabalpur, MP 482004'}
        ]

        # Initialize database and populate sample data
        initialize_database()
        populate_sample_restaurant_data()

        self.app_callbacks = {
            "show_signup_screen": self.show_signup_screen,
            "show_login_screen": self.show_login_screen,
            "_post_login_navigation": self._post_login_navigation,  # Add the post login navigation
            "show_menu_screen": self.show_menu_screen,
            "show_cart_screen": self.show_cart_screen,
            "handle_checkout": self.handle_checkout,
            "logout": self.logout,
            "show_admin_screen": self.show_admin_screen,
            "show_main_app_screen": self.show_main_app_screen  # Ensure this callback is present
        }

        self.show_login_screen()

    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (width / 2))
        y_cordinate = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def _set_window_properties(self, title, width, height, resizable=True):
        self.title(title)
        self._center_window(width, height)
        self.resizable(resizable, resizable)

    def _create_login_screen(self):
        # Pass _post_login_navigation as the success callback
        return LoginScreen(self, self.show_signup_screen, self._post_login_navigation)

    def _create_signup_screen(self):
        return SignupScreen(self, self.show_login_screen)

    def _create_main_app_screen(self):
        return SimpleMainAppScreen(self, self.current_user, self.show_menu_screen, self.logout)

    def _create_menu_screen(self, restaurant):
        # Ensure self.menu_screen_instance is created and stored
        self.menu_screen_instance = MenuScreen(
            app_ref=self,  # Pass self (the App instance) as app_ref
            user=self.current_user,
            restaurant=restaurant
        )
        return self.menu_screen_instance

    def _create_cart_screen(self):
        self.cart_screen_instance = CartScreen(
            self, 
            self.current_user, 
            self.cart, 
            self.show_main_app_screen,  # Callback for general fallback/main screen
            self.show_menu_screen,      # Callback for "Back to Menu"
            self.handle_checkout        # Callback for "Proceed to Checkout"
        )
        return self.cart_screen_instance

    def _get_or_create_admin_screen_for_switch_factory(self, user):
        # This method now returns an instance of ModernAdminDashboard
        if not hasattr(self, 'admin_dashboard_instance') or \
           not self.admin_dashboard_instance or \
           not self.admin_dashboard_instance.winfo_exists():
            log("INFO: Creating new ModernAdminDashboard instance.")
            self.admin_dashboard_instance = ModernAdminDashboard(self, self.app_callbacks, user)
        else:
            log("INFO: Returning existing ModernAdminDashboard instance.")
            # Ensure the correct user context if it could change (though typically admin user is fixed per session)
            self.admin_dashboard_instance.loggedInUser = user 
        return self.admin_dashboard_instance

    def _switch_screen(self, screen_factory_method, *factory_args, title, width, height, resizable=True):
        if self.current_screen_frame:
            self.current_screen_frame.destroy()
            self.current_screen_frame = None

        self.current_screen_frame = screen_factory_method(*factory_args)
        
        self.current_screen_frame.pack(fill="both", expand=True)
        self._set_window_properties(title, width, height, resizable)
        
        # If the current screen is ModernAdminDashboard, and it has refresh_data, call it.
        if isinstance(self.current_screen_frame, ModernAdminDashboard):
            if hasattr(self.current_screen_frame, 'refresh_data') and callable(getattr(self.current_screen_frame, 'refresh_data')):
                log("INFO: ModernAdminDashboard is packed and current. Calling refresh_data().")
                self.current_screen_frame.refresh_data()  # type: ignore[attr-defined]
            else:
                log("WARNING: ModernAdminDashboard instance does not have a callable refresh_data method.")

    def _post_login_navigation(self, user: User):
        log(f"INFO: _post_login_navigation called for user: {user.username if user else 'None'}. Admin status: {user.is_admin if user else 'N/A'}")
        self.current_user = user
        if not user:
            log(f"ERROR: _post_login_navigation called with None user.")
            self.show_login_screen()
            return

        self.cart = Cart(user_id=user.user_id)
        log(f"INFO: User {user.username} logged in. Is Admin: {user.is_admin}")
        if user.is_admin:
            self.show_admin_screen(user)
        else:
            self.show_main_app_screen(user)

    def show_login_screen(self, username_to_fill=None):
        self.current_user = None
        self.current_restaurant = None
        self.cart = None

        self._switch_screen(self._create_login_screen, title="Swigato - Login", width=400, height=550, resizable=False)

        # Bring window to front and focus
        self.lift()
        self.focus_force()
        self.after(100, self._focus_login_entries, username_to_fill)

    def _focus_login_entries(self, username_to_fill):
        if self.current_screen_frame and \
           hasattr(self.current_screen_frame, 'username_entry') and \
           self.current_screen_frame.username_entry and \
           self.current_screen_frame.username_entry.winfo_exists():
            if username_to_fill:
                self.current_screen_frame.username_entry.delete(0, 'end')
                self.current_screen_frame.username_entry.insert(0, username_to_fill)
            # Focus logic: if username entry has text, focus password, else focus username
            if self.current_screen_frame.username_entry.get():
                if hasattr(self.current_screen_frame, 'password_entry') and \
                   self.current_screen_frame.password_entry and \
                   self.current_screen_frame.password_entry.winfo_exists():
                    self.current_screen_frame.password_entry.focus_set()
            else:
                self.current_screen_frame.username_entry.focus_set()

    def show_signup_screen(self):
        self._switch_screen(self._create_signup_screen, title="Swigato - Sign Up", width=400, height=600, resizable=False)

    def show_main_app_screen(self, user: User):
        log(f"INFO: show_main_app_screen called for user: {user.username if user else 'None'}")
        self.current_user = user
        if not self.cart or self.cart.user_id != user.user_id:
            self.cart = Cart(user_id=user.user_id)
            log(f"INFO: Cart initialized/updated for user {user.user_id} in show_main_app_screen.")

        self._switch_screen(self._create_main_app_screen, title="Swigato - Home", width=900, height=700)

    def show_menu_screen(self, restaurant):
        if not self.current_user:
            print("Error: User not logged in. Cannot show menu.")
            self.show_login_screen()
            return
        self.current_restaurant = restaurant
        self._switch_screen(self._create_menu_screen, restaurant, title=f"Swigato - {restaurant.name}", width=900, height=750)

    def show_menu_screen_from_cart(self, restaurant):
        self.show_menu_screen(restaurant)

    def show_cart_screen(self):
        """Navigate to main app and show cart content (modernized cart experience)"""
        if not self.current_user:
            print("Error: User not logged in. Cannot show cart.")
            self.show_login_screen()
            return
        if not self.cart:
            print("Error: Cart not initialized. Cannot show cart.")
            self.show_main_app_screen(self.current_user)
            return
        
        # Show main app screen and navigate to cart content
        self.show_main_app_screen(self.current_user)
        
        # If main app screen exists, switch to cart content
        if hasattr(self, 'current_screen_frame') and self.current_screen_frame:
            main_screen = self.current_screen_frame
            if hasattr(main_screen, 'show_cart_content'):
                main_screen.show_cart_content()
                # Also update the navigation tab to cart
                if hasattr(main_screen, 'set_active_nav_tab'):
                    main_screen.set_active_nav_tab("cart")

    def show_admin_screen(self, user):
        if not user or not user.is_admin:
            log("ERROR: Unauthorized attempt to access admin screen.")
            try:
                messagebox.showerror("Access Denied", "You do not have permission to access the admin panel.")
            except Exception as e:
                log(f"Error showing messagebox: {e}")
            self.show_login_screen()
            return

        self.current_user = user

        def _get_or_create_admin_screen_for_switch_factory():
            return self._get_or_create_admin_screen_for_switch_factory(user)

        log(f"INFO: Switching to Admin Dashboard for user {user.username}")
        self._switch_screen(_get_or_create_admin_screen_for_switch_factory, title="Swigato - Admin Panel", width=1000, height=700)

    def handle_review_submitted(self, restaurant_id):
        if isinstance(self.current_screen_frame, MenuScreen) and self.current_screen_frame.restaurant.id == restaurant_id:
            self.current_screen_frame.refresh_reviews()

    def handle_checkout(self):
        if not self.current_user:
            try:
                messagebox.showerror("Authentication Error", "You must be logged in to checkout.")
            except Exception as e:
                print(f"Error showing messagebox: {e}")
            self.show_login_screen()
            return

        if not self.cart or not self.cart.items:
            try:
                messagebox.showwarning("Empty Cart", "Your cart is empty. Please add items before checking out.")
            except Exception as e:
                print(f"Error showing messagebox: {e}")
            if self.current_screen_frame and isinstance(self.current_screen_frame, CartScreen) and self.current_screen_frame.winfo_ismapped():
                self.current_screen_frame.load_cart_items()
            return

        if not self.current_restaurant:
            try:
                messagebox.showerror("Order Error", "Cannot determine the restaurant for this order. Please go back to the menu and try again.")
            except Exception as e:
                print(f"Error showing messagebox: {e}")
            self.show_main_app_screen(self.current_user)
            return

        user_id = self.current_user.user_id
        restaurant_id = self.current_restaurant.restaurant_id
        restaurant_name = self.current_restaurant.name
        cart_items_dict = self.cart.items 
        total_amount = self.cart.get_total_price()

        print(f"Attempting to create order: UserID: {user_id}, RestID: {restaurant_id}, RestName: {restaurant_name}, Total: {total_amount}")

        try:
            restaurant_id = self.current_restaurant.restaurant_id
            
            order_id_or_obj = create_order(
                user_id=self.current_user.user_id,
                restaurant_id=restaurant_id,
                restaurant_name=self.current_restaurant.name,
                cart_items=self.cart.get_items_for_order(),
                total_amount=self.cart.get_total_price(),
                user_address=self.current_user.address if self.current_user.address else "Not specified"
            )
            
            if order_id_or_obj and hasattr(order_id_or_obj, 'order_id'):
                actual_order_id = order_id_or_obj.order_id
                print(f"Order created successfully: Order ID {actual_order_id}")
                messagebox.showinfo("Order Placed", f"Your order has been placed successfully!\nOrder ID: {actual_order_id}")
                self.cart.items.clear()
                self.show_main_app_screen(self.current_user)
            else:
                messagebox.showerror("Order Failed", "There was an issue placing your order. Please try again.")
                print("Error: Order creation failed, create_order returned None or an unexpected object.")
        except Exception as e:
            messagebox.showerror("Order Error", f"An unexpected error occurred: {e}")
            print(f"Error: Exception during order creation or post-order actions: {e}")

    def logout(self):
        log(f"INFO: User {self.current_user.username if self.current_user else 'Unknown'} logging out.")
        self.current_user = None
        self.current_restaurant = None
        self.cart = None
        if self.admin_dashboard_instance:
            self.admin_dashboard_instance.destroy()
            self.admin_dashboard_instance = None
        self.show_login_screen()
        log(f"INFO: Logout complete. Showing login screen.")

    def show_main_app_cart(self):
        """Navigate to main app screen and show the cart tab"""
        if not self.current_user:
            print("Error: User not logged in. Cannot show cart.")
            self.show_login_screen()
            return
        
        # Switch to main app screen
        self.show_main_app_screen(self.current_user)
        
        # Navigate to cart tab in the bottom navigation
        if self.current_screen_frame and hasattr(self.current_screen_frame, 'handle_nav_click'):
            self.current_screen_frame.handle_nav_click('cart')

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
