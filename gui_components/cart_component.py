import customtkinter as ctk
from tkinter import messagebox
from gui_Light import (
    BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, 
    SUCCESS_COLOR, SECONDARY_COLOR, GRAY_TEXT_COLOR, ERROR_COLOR,
    FRAME_FG_COLOR, FRAME_BORDER_COLOR, HOVER_BG_COLOR
)
from utils.logger import log


class CartComponent(ctk.CTkScrollableFrame):
    """Simplified cart component"""
    
    def __init__(self, parent, app_ref, **kwargs):
        super().__init__(parent, fg_color=BACKGROUND_COLOR, border_width=0, corner_radius=0, **kwargs)
        
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        
    def load_cart(self):
        """Load and display cart items"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        cart = self.app_ref.cart
        if not cart or not cart.items:
            self.show_empty_cart()
            return
            
        # Display cart items
        for i, (menu_item_id, cart_item) in enumerate(cart.items.items()):
            self.create_cart_item_card(menu_item_id, cart_item, i)
            
        # Add checkout section
        self.create_checkout_section(len(cart.items))
        
    def show_empty_cart(self):
        """Show empty cart state"""
        empty_frame = ctk.CTkFrame(
            self,
            fg_color=FRAME_FG_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        empty_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(
            empty_frame,
            text="🛒",
            font=ctk.CTkFont(size=48),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="Your cart is empty!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="Add items from restaurants to see them here.",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(0, 30))
        
    def create_cart_item_card(self, menu_item_id, cart_item, row):
        """Create a simplified cart item card"""
        card = ctk.CTkFrame(
            self,
            fg_color=FRAME_FG_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR,
            height=80
        )
        card.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        card.pack_propagate(False)
        
        # Food icon
        ctk.CTkLabel(
            card,
            text="🍽️",
            font=ctk.CTkFont(size=24),
            text_color=PRIMARY_COLOR
        ).grid(row=0, column=0, padx=15, pady=15)
        
        # Item details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Item name
        ctk.CTkLabel(
            details_frame,
            text=cart_item.menu_item.name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        # Price calculation
        price_text = f"₹{cart_item.menu_item.price:.2f} × {cart_item.quantity} = ₹{cart_item.menu_item.price * cart_item.quantity:.2f}"
        ctk.CTkLabel(
            details_frame,
            text=price_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PRIMARY_COLOR,
            anchor="w"
        ).pack(anchor="w")
        
        # Quantity controls
        controls_frame = ctk.CTkFrame(card, fg_color="transparent")
        controls_frame.grid(row=0, column=2, padx=15, pady=15)
        
        # Minus button
        minus_btn = ctk.CTkButton(
            controls_frame,
            text="−",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SECONDARY_COLOR,
            hover_color="#B91C1C",
            text_color="white",
            corner_radius=6,
            command=lambda: self.update_quantity(menu_item_id, -1)
        )
        minus_btn.pack(side="left", padx=(0, 5))
        
        # Quantity label
        ctk.CTkLabel(
            controls_frame,
            text=str(cart_item.quantity),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR,
            width=30
        ).pack(side="left", padx=5)
        
        # Plus button
        plus_btn = ctk.CTkButton(
            controls_frame,
            text="+",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            corner_radius=6,
            command=lambda: self.update_quantity(menu_item_id, 1)
        )
        plus_btn.pack(side="left", padx=(5, 10))
        
        # Remove button
        remove_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=ERROR_COLOR,
            hover_color=HOVER_BG_COLOR,
            corner_radius=6,
            command=lambda: self.remove_item(menu_item_id)
        )
        remove_btn.pack(side="left")
        
    def create_checkout_section(self, items_count):
        """Create checkout section"""
        checkout_frame = ctk.CTkFrame(
            self,
            fg_color=FRAME_FG_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        checkout_frame.grid(row=items_count, column=0, padx=20, pady=20, sticky="ew")
        checkout_frame.grid_columnconfigure(0, weight=1)
        
        # Total amount
        total_label = ctk.CTkLabel(
            checkout_frame,
            text=f"Total: ₹{self.app_ref.cart.get_total_price():.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        total_label.pack(pady=(20, 10))
        
        # Checkout button
        checkout_btn = ctk.CTkButton(
            checkout_frame,
            text="🛒 Proceed to Checkout",
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=SUCCESS_COLOR,
            hover_color="#388E3C",
            text_color="white",
            corner_radius=12,
            command=self.proceed_to_checkout
        )
        checkout_btn.pack(pady=(0, 20))
        
    def update_quantity(self, menu_item_id, quantity_change):
        """Update item quantity in cart"""
        cart = self.app_ref.cart
        current_item = cart.items.get(menu_item_id)
        
        if current_item:
            new_quantity = current_item.quantity + quantity_change
            if new_quantity > 0:
                cart.add_item(current_item.menu_item, quantity_change)
            else:
                cart.remove_item(menu_item_id)
            
            self.load_cart()  # Refresh cart view
            
    def remove_item(self, menu_item_id):
        """Remove item from cart"""
        self.app_ref.cart.remove_item(menu_item_id)
        self.load_cart()  # Refresh cart view
        
    def proceed_to_checkout(self):
        """Handle checkout process"""
        cart = self.app_ref.cart
        if not cart or not cart.items:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return
            
        # Use the app's checkout handler
        if hasattr(self.app_ref, 'handle_checkout'):
            self.app_ref.handle_checkout()
        else:
            messagebox.showinfo("Checkout", "Checkout functionality not available.")
