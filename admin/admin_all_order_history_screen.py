import customtkinter as ctk
from CTkTable import CTkTable
import logging
from gui_Light import (
    FONT_FAMILY, BODY_FONT_SIZE, HEADING_FONT_SIZE,
    ADMIN_BACKGROUND_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_TEXT_COLOR,
    ADMIN_PRIMARY_ACCENT_COLOR, ADMIN_SECONDARY_ACCENT_COLOR,
    ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR,
    ADMIN_TABLE_BORDER_COLOR, ADMIN_TABLE_TEXT_COLOR, ERROR_COLOR, ADMIN_PRIMARY_COLOR, 
    ADMIN_BUTTON_TEXT_COLOR, ADMIN_BUTTON_HOVER_COLOR, set_swigato_icon, center_window
)
from orders.models import Order, get_order_items_for_order
from users.models import User
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger("swigato_app.admin_all_order_history_screen")

class AdminAllOrderHistoryScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_orders = []
        self.filtered_orders = []
        self.filter_status = "All"
        self.filter_user = "All Users"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=0)  # Controls
        self.grid_rowconfigure(2, weight=1)  # Table
        self.grid_rowconfigure(3, weight=0)  # Summary

        # Title
        title_label = ctk.CTkLabel(self, text="Complete Order History - All Users",
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"),
                                   text_color="#FF6B35")  # Swigato orange for visibility
        title_label.grid(row=0, column=0, padx=25, pady=(20, 15), sticky="nw")

        # Control panel with filters and export
        self.create_control_panel()

        # Table frame
        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=2, column=0, padx=25, pady=(10, 15), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        # Summary frame
        self.summary_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.summary_frame.grid(row=3, column=0, padx=25, pady=(0, 25), sticky="ew")

        self.orders_table = None
        self.load_all_orders()
        logger.info("AdminAllOrderHistoryScreen initialized and all orders loaded.")

    def create_control_panel(self):
        """Create control panel with filters and actions"""
        controls_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        controls_frame.grid(row=1, column=0, padx=25, pady=(0, 10), sticky="ew")
        controls_frame.grid_columnconfigure(4, weight=1)

        # Status filter
        status_label = ctk.CTkLabel(controls_frame, text="Status:", 
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                   text_color="#FFFFFF")  # White text for visibility
        status_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")

        self.status_var = ctk.StringVar(value="All")
        status_options = ["All", "Pending Confirmation", "Confirmed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]
        self.status_dropdown = ctk.CTkComboBox(controls_frame, values=status_options, 
                                              variable=self.status_var, command=self.apply_filters,
                                              fg_color=ADMIN_BACKGROUND_COLOR, text_color="#FFFFFF",  # White text
                                              dropdown_fg_color=ADMIN_BACKGROUND_COLOR)
        self.status_dropdown.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="w")

        # User filter
        user_label = ctk.CTkLabel(controls_frame, text="User:", 
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                 text_color="#FFFFFF")  # White text for visibility
        user_label.grid(row=0, column=2, padx=(0, 5), pady=15, sticky="w")

        self.user_var = ctk.StringVar(value="All Users")
        user_options = ["All Users"] + [user.username for user in User.get_all_users()]
        self.user_dropdown = ctk.CTkComboBox(controls_frame, values=user_options, 
                                            variable=self.user_var, command=self.apply_filters,
                                            fg_color=ADMIN_BACKGROUND_COLOR, text_color="#FFFFFF",  # White text
                                            dropdown_fg_color=ADMIN_BACKGROUND_COLOR)
        self.user_dropdown.grid(row=0, column=3, padx=(0, 20), pady=15, sticky="w")

        # Refresh button
        refresh_btn = ctk.CTkButton(controls_frame, text="Refresh", command=self.load_all_orders,
                                   fg_color=ADMIN_PRIMARY_ACCENT_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                   text_color=ADMIN_BUTTON_TEXT_COLOR,
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE, weight="bold"))
        refresh_btn.grid(row=0, column=5, padx=(10, 15), pady=15, sticky="e")

    def apply_filters(self, *args):
        """Apply status and user filters to the orders"""
        status_filter = self.status_var.get()
        user_filter = self.user_var.get()

        filtered = self.current_orders.copy()

        # Apply status filter
        if status_filter != "All":
            filtered = [order for order in filtered if order.status == status_filter]

        # Apply user filter
        if user_filter != "All Users":
            filtered = [order for order in filtered if hasattr(order, 'customer_username') and order.customer_username == user_filter]

        self.filtered_orders = filtered
        self.display_orders(self.filtered_orders)
        self.update_summary()

    def load_all_orders(self):
        """Load all orders from all users"""
        try:
            all_orders = Order.get_all_orders()
            
            # Enhance orders with customer usernames and items
            for order in all_orders:
                # Get customer username
                try:
                    user = User.get_by_id(order.user_id)
                    order.customer_username = user.username if user else f"User {order.user_id}"
                except Exception as e:
                    order.customer_username = f"User {order.user_id}"
                    logger.warning(f"Could not get username for user_id {order.user_id}: {e}")
                
                # Get order items
                if not hasattr(order, 'items') or not order.items:
                    try:
                        order.items = get_order_items_for_order(order.order_id)
                    except Exception as e:
                        order.items = []
                        logger.warning(f"Could not get items for order {order.order_id}: {e}")

            # Sort by date (newest first)
            all_orders.sort(key=lambda o: o.order_date, reverse=True)
            
            self.current_orders = all_orders
            self.filtered_orders = all_orders.copy()
            self.display_orders(self.filtered_orders)
            self.update_summary()
            
            logger.info(f"Loaded {len(all_orders)} total orders for all users")
            
        except Exception as e:
            logger.error(f"Error loading all orders: {e}")
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def display_orders(self, orders):
        """Display orders in the table"""
        # Clear existing table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not orders:
            no_orders_label = ctk.CTkLabel(self.table_frame, text="No orders found matching the current filters.",
                                          font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                          text_color="#FFFFFF")  # White text for visibility
            no_orders_label.pack(expand=True)
            return

        # Create scrollable frame for the table
        self.scroll_frame = ctk.CTkScrollableFrame(self.table_frame, fg_color=ADMIN_FRAME_FG_COLOR, 
                                                  corner_radius=10)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create table headers
        headers = ["Order ID", "Customer", "Restaurant", "Date & Time", "Total (₹)", "Status", "Address", "Items", "Type"]
        table_data = [headers]

        # Add order data
        for order in orders:
            date_str = order.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order.order_date, 'strftime') else str(order.order_date)
            
            # Format items string
            items_str = ", ".join([f"{item.name} x{item.quantity}" for item in getattr(order, 'items', [])])
            if len(items_str) > 50:
                items_str = items_str[:47] + "..."
            
            # Format address
            address_str = order.delivery_address or "N/A"
            if len(address_str) > 25:
                address_str = address_str[:22] + "..."
            
            # Determine user type (Admin/Customer)
            user_type = "Admin" if hasattr(order, 'customer_username') and any(
                user.username == order.customer_username and getattr(user, 'is_admin', False) 
                for user in User.get_all_users()
            ) else "Customer"

            row = [
                str(order.order_id),
                order.customer_username,
                order.restaurant_name or "N/A",
                date_str,
                f"{order.total_amount:.2f}",
                order.status,
                address_str,
                items_str,
                user_type
            ]
            table_data.append(row)

        # Create CTkTable
        try:
            header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE, weight="bold")
            
            self.orders_table = CTkTable(
                self.scroll_frame,  # Use scrollable frame as parent
                values=table_data,
                colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
                header_color=ADMIN_TABLE_HEADER_BG_COLOR,
                text_color=ADMIN_TABLE_TEXT_COLOR,
                font=(FONT_FAMILY, BODY_FONT_SIZE-2),
                corner_radius=5
            )
            
            # Set header text color to Swigato orange for better visibility
            if table_data:
                self.orders_table.edit_row(0, text_color="#FF6B35", font=header_font, fg_color=ADMIN_TABLE_HEADER_BG_COLOR)
            
            self.orders_table.pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating orders table: {e}")
            error_label = ctk.CTkLabel(self.table_frame, text=f"Error displaying orders: {str(e)}",
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                      text_color=ERROR_COLOR)
            error_label.pack(expand=True)

    def update_summary(self):
        """Update summary statistics"""
        # Clear existing summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        orders = self.filtered_orders
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        
        # Count by status
        status_counts = {}
        user_type_counts = {"Admin": 0, "Customer": 0}
        
        for order in orders:
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by user type
            is_admin = any(
                user.username == order.customer_username and getattr(user, 'is_admin', False) 
                for user in User.get_all_users()
            )
            user_type_counts["Admin" if is_admin else "Customer"] += 1

        # Create summary layout
        summary_left = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        summary_left.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        summary_right = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        summary_right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Left side - totals
        ctk.CTkLabel(summary_left, text="Summary Statistics", 
                    font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+2, weight="bold"),
                    text_color="#FF6B35").pack(anchor="w")  # Swigato orange for visibility
        
        ctk.CTkLabel(summary_left, text=f"Total Orders: {total_orders}", 
                    font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                    text_color="#FFFFFF").pack(anchor="w", pady=(5, 0))  # White text
        
        ctk.CTkLabel(summary_left, text=f"Total Revenue: ₹{total_revenue:.2f}", 
                    font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                    text_color="#FFFFFF").pack(anchor="w")  # White text
        
        ctk.CTkLabel(summary_left, text=f"Admin Orders: {user_type_counts['Admin']}", 
                    font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                    text_color="#FFFFFF").pack(anchor="w")  # White text
        
        ctk.CTkLabel(summary_left, text=f"Customer Orders: {user_type_counts['Customer']}", 
                    font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                    text_color="#FFFFFF").pack(anchor="w")  # White text

        # Right side - status breakdown
        if status_counts:
            ctk.CTkLabel(summary_right, text="Status Breakdown", 
                        font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+2, weight="bold"),
                        text_color="#FF6B35").pack(anchor="w")  # Swigato orange for visibility
            
            for status, count in sorted(status_counts.items()):
                ctk.CTkLabel(summary_right, text=f"{status}: {count}", 
                            font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                            text_color="#FFFFFF").pack(anchor="w", pady=(2, 0))  # White text

    def refresh_data(self):
        """Refresh the order data"""
        self.load_all_orders()
