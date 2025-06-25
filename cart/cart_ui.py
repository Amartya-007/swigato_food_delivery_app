import customtkinter as ctk
from tkinter import messagebox
from cart.models import Cart
from users.models import User
from restaurants.models import MenuItem
from utils.logger import log

class CartUtilities:
    @staticmethod
    def add_to_cart_from_favorites(app_ref, user, menu_item, parent_widget=None):
        """
        Adds a menu item to the user's cart from their favorites.
        Updates the cart count in the navigation.
        """
        try:
            if not app_ref or not hasattr(app_ref, 'cart'):
                log("Cart not initialized in the main application.")
                messagebox.showerror("Error", "Cart not initialized.", parent=parent_widget)
                return

            cart = app_ref.cart
            
            # Ensure cart belongs to the current user. If not, something is wrong.
            if cart.user_id != user.user_id:
                log(f"Cart user ID {cart.user_id} does not match current user ID {user.user_id}.")
                # This case might indicate a need to re-sync the cart, but for now, we'll show an error.
                messagebox.showerror("Error", "Cart-user mismatch. Please log in again.", parent=parent_widget)
                return

            # Add the menu item object to the cart
            if cart.add_item(menu_item, 1):
                log(f"Successfully added '{menu_item.name}' to cart for user '{user.username}'.")
                
                # Update cart count in the UI
                if hasattr(app_ref, 'main_app_screen') and app_ref.main_app_screen:
                    app_ref.main_app_screen.update_cart_count_in_nav()

                messagebox.showinfo("Success", f"Added '{menu_item.name}' to cart.", parent=parent_widget)
            else:
                # add_item returns False if quantity is invalid, though it's 1 here.
                log(f"Failed to add '{menu_item.name}' to cart due to an issue in cart.add_item.")
                messagebox.showwarning("Notice", "Could not add item to cart.", parent=parent_widget)

        except Exception as e:
            log(f"Error in add_to_cart_from_favorites: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_widget)
