import customtkinter as ctk
from gui_Light import *
from orders.models import get_orders_by_user_id
from utils.logger import log


class OrderHistoryComponent(ctk.CTkScrollableFrame):
    """Simplified order history component"""
    
    def __init__(self, parent, user, **kwargs):
        super().__init__(parent, fg_color=BACKGROUND_COLOR, border_width=0, corner_radius=0, **kwargs)
        
        self.user = user
        self.grid_columnconfigure(0, weight=1)
        
    def load_orders(self):
        """Load and display order history"""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Get user orders
        try:
            orders = get_orders_by_user_id(self.user.user_id)
        except Exception as e:
            log(f"Error loading orders: {e}")
            orders = []
            
        if not orders:
            self.show_empty_state()
            return
            
        # Display orders
        for i, order in enumerate(orders):
            self.create_order_card(order, i)
            
    def show_empty_state(self):
        """Show empty state when no orders"""
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
            text="📋",
            font=ctk.CTkFont(size=48),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="No orders yet!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="Your order history will appear here",
            font=ctk.CTkFont(size=14),
            text_color=GRAY_TEXT_COLOR
        ).pack(pady=(0, 30))
        
    def create_order_card(self, order, row):
        """Create a simplified order card"""
        card = ctk.CTkFrame(
            self,
            fg_color=FRAME_FG_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        card.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        
        # Status icon
        status_icon = "✅" if order.status.lower() == "delivered" else "🕒"
        status_label = ctk.CTkLabel(
            card,
            text=status_icon,
            font=ctk.CTkFont(size=24),
            text_color=SUCCESS_COLOR if order.status.lower() == "delivered" else PRIMARY_COLOR
        )
        status_label.grid(row=0, column=0, padx=20, pady=15)
        
        # Order details
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Order header
        header_text = f"Order #{order.order_id} • {order.order_date.strftime('%B %d, %Y')}"
        ctk.CTkLabel(
            details_frame,
            text=header_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        # Restaurant name
        if hasattr(order, 'restaurant_name') and order.restaurant_name:
            ctk.CTkLabel(
                details_frame,
                text=f"🏪 {order.restaurant_name}",
                font=ctk.CTkFont(size=14),
                text_color=GRAY_TEXT_COLOR,
                anchor="w"
            ).pack(anchor="w", pady=(0, 5))
        
        # Total amount
        ctk.CTkLabel(
            details_frame,
            text=f"💰 Total: ₹{order.total_amount:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PRIMARY_COLOR,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        # Status
        status_color = self.get_status_color(order.status)
        ctk.CTkLabel(
            details_frame,
            text=f"📦 Status: {order.status.title()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=status_color,
            anchor="w"
        ).pack(anchor="w")
        
    def get_status_color(self, status):
        """Get color based on order status"""
        status = status.lower()
        if status == "delivered":
            return SUCCESS_COLOR
        elif status == "pending":
            return "#FFA500"  # Orange
        elif status == "cancelled":
            return ERROR_COLOR
        else:
            return PRIMARY_COLOR
