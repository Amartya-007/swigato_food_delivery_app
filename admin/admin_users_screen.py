import customtkinter as ctk
from CTkTable import CTkTable
import logging
from tkinter import messagebox
import os # For icon path

# Import the centralized modern admin theme
from admin.modern_admin_theme import (
    MODERN_ADMIN_BG, MODERN_ADMIN_CARD, MODERN_ADMIN_ACCENT, MODERN_ADMIN_TEXT,
    MODERN_ADMIN_TEXT_SECONDARY, MODERN_ADMIN_BUTTON, MODERN_ADMIN_BUTTON_HOVER,
    MODERN_ADMIN_FONT_FAMILY, MODERN_ADMIN_FONT_SIZES, MODERN_ADMIN_SPACING,
    MODERN_ADMIN_BORDER_RADIUS, MODERN_ADMIN_STATUS, 
    MODERN_ADMIN_TABLE, ERROR_COLOR
)

# Import remaining utility functions from gui_Light
from gui_Light import (
    set_swigato_icon, safe_focus, center_window
)
from users.models import User # Import the User model
from utils.database import get_db_connection # For direct DB operations if needed, though User model should handle most

logger = logging.getLogger("swigato_app.admin_users_screen") # Updated logger name

# Define icon path - ensure swigato_icon.ico is in the assets folder
ICON_PATH = os.path.join("assets", "swigato_icon.ico")

class AdminUsersScreen(ctk.CTkFrame): # Renamed class
    def __init__(self, master, app_callbacks, user, **kwargs): # Removed users_data_list
        super().__init__(master, fg_color=MODERN_ADMIN_BG, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user # Logged-in admin user
        self.current_view_users = [] # To store the currently displayed (filtered/sorted) user objects

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Controls frame (new)
        self.grid_rowconfigure(2, weight=1) # Table frame (shifted)

        self.admin_column_index = 2 # Column index for "Admin?"
        self.actions_column_index = 4 # Combined actions column
        self.current_edit_user_id = None # Will store the ID of the user being edited

        # Title with improved typography
        title_label = ctk.CTkLabel(
            self, 
            text="User Management", 
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["title"], weight="bold"), 
            text_color="#FF6B35"  # Swigato orange for visibility
        )
        title_label.grid(row=0, column=0, padx=30, pady=(25, 15), sticky="nw")

        # Controls Frame with modern styling
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, columnspan=2, padx=30, pady=(10,20), sticky="ew")

        # Left part of controls (Search, Filter, Clear)
        left_controls_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        left_controls_subframe.pack(side="left", fill="x", expand=True, padx=(0,15))

        self.search_entry = ctk.CTkEntry(
            left_controls_subframe,
            placeholder_text="Search ID, Name, Address...",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            width=320,
            height=45,
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]
        )
        self.search_entry.pack(side="left", padx=(0,15), pady=8)
        self.search_entry.bind("<Return>", lambda event: self._apply_filters_and_refresh_table())

        self.admin_filter_var = ctk.StringVar(value="All")
        self.admin_filter_menu = ctk.CTkOptionMenu(
            left_controls_subframe,
            variable=self.admin_filter_var,
            values=["All", "Admin", "Non-Admin"],
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            dropdown_font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            command=lambda choice: self._apply_filters_and_refresh_table(),
            fg_color=MODERN_ADMIN_BUTTON,
            button_color=MODERN_ADMIN_BUTTON,
            button_hover_color=MODERN_ADMIN_BUTTON_HOVER,
            text_color_disabled=MODERN_ADMIN_TEXT,
            height=45,
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"],
            width=140
        )
        self.admin_filter_menu.pack(side="left", padx=(0,15), pady=8)

        self.clear_filters_button = ctk.CTkButton(
            left_controls_subframe,
            text="Clear Filters",
            command=self._clear_filters_and_refresh_table,
            fg_color=MODERN_ADMIN_TEXT_SECONDARY,
            hover_color=MODERN_ADMIN_ACCENT,
            text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"],
            width=140,
            height=45
        )
        self.clear_filters_button.pack(side="left", padx=(0,15), pady=8)

        # Right part of controls (Add User)
        right_controls_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        right_controls_subframe.pack(side="right", fill="none", expand=False)

        self.add_user_button = ctk.CTkButton(
            right_controls_subframe,
            text="Add New User",
            command=self._open_add_user_dialog,
            fg_color=MODERN_ADMIN_BUTTON,
            hover_color=MODERN_ADMIN_BUTTON_HOVER,
            text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"],
            height=45,
            width=160
        )
        self.add_user_button.pack(pady=8)

        # Frame for the table with modern styling
        self.table_frame = ctk.CTkFrame(
            self, 
            fg_color=MODERN_ADMIN_CARD, 
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]
        )
        self.table_frame.grid(row=2, column=0, columnspan=2, padx=30, pady=(0,30), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.user_table = None
        self._load_and_display_users() # Initial load

    def _apply_filters_and_refresh_table(self):
        logger.debug("Applying filters and refreshing table.")
        self._load_and_display_users()

    def _clear_filters_and_refresh_table(self):
        logger.debug("Clearing filters and refreshing table.")
        self.search_entry.delete(0, "end")
        self.admin_filter_var.set("All")
        self._load_and_display_users()
    
    def _open_add_user_dialog(self):
        if hasattr(self, 'add_user_dialog') and self.add_user_dialog.winfo_exists():
            safe_focus(self.add_user_dialog)
            return

        self.add_user_dialog = ctk.CTkToplevel(self)
        self.add_user_dialog.title("Swigato - Add New User")
        set_swigato_icon(self.add_user_dialog)
        center_window(self.add_user_dialog, 400, 450)
        self.add_user_dialog.configure(fg_color=MODERN_ADMIN_BG) # Set Toplevel background
        self.add_user_dialog.transient(self.master)  # type: ignore[arg-type]
        self.add_user_dialog.grab_set() # Modal behavior

        dialog_main_frame = ctk.CTkFrame(self.add_user_dialog, fg_color=MODERN_ADMIN_CARD, corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]) # Use modern theme
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Username
        ctk.CTkLabel(dialog_main_frame, text="Username:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.username_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                               text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.username_entry_add.pack(fill="x", pady=(0,10))

        # Password
        ctk.CTkLabel(dialog_main_frame, text="Password:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.password_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                              text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.password_entry_add.pack(fill="x", pady=(0,10))
        
        # Confirm Password
        ctk.CTkLabel(dialog_main_frame, text="Confirm Password:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.confirm_password_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                                      text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.confirm_password_entry_add.pack(fill="x", pady=(0,10))

        # Address
        ctk.CTkLabel(dialog_main_frame, text="Address:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.address_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                             text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.address_entry_add.pack(fill="x", pady=(0,10))

        # Admin Flag
        self.is_admin_var_add = ctk.BooleanVar()
        admin_switch = ctk.CTkSwitch(dialog_main_frame, text="Is Admin?", variable=self.is_admin_var_add,
                                      font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                      text_color=MODERN_ADMIN_TEXT,
                                      progress_color=MODERN_ADMIN_ACCENT,
                                      fg_color=MODERN_ADMIN_TEXT_SECONDARY,
                                      button_color=MODERN_ADMIN_ACCENT,
                                      button_hover_color=MODERN_ADMIN_BUTTON_HOVER)
        admin_switch.pack(anchor="w", pady=(0,15))

        # Error Label (initially hidden)
        self.error_label_add_user = ctk.CTkLabel(dialog_main_frame, text="", text_color=ERROR_COLOR, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["small"]))
        self.error_label_add_user.pack(pady=(5,0))

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10,0), side="bottom") # Ensure buttons are at the bottom

        save_button = ctk.CTkButton(
            buttons_frame, text="Save User", command=self._save_new_user,
            fg_color=MODERN_ADMIN_BUTTON, hover_color=MODERN_ADMIN_BUTTON_HOVER, text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        save_button.pack(side="right", padx=(10,0))

        cancel_button = ctk.CTkButton(
            buttons_frame, text="Cancel", command=self.add_user_dialog.destroy,
            fg_color=MODERN_ADMIN_TEXT_SECONDARY, hover_color=MODERN_ADMIN_ACCENT, text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        cancel_button.pack(side="right")
        
        safe_focus(self.username_entry_add)

    def _save_new_user(self):
        username = self.username_entry_add.get().strip()
        password = self.password_entry_add.get() # No strip, keep as is for now
        confirm_password = self.confirm_password_entry_add.get()
        address = self.address_entry_add.get().strip()
        is_admin = self.is_admin_var_add.get()

        if not username:
            logger.warning("Attempted to add user with empty username.")
            self.error_label_add_user.configure(text="Username cannot be empty.")
            return
        
        if not password: # Added check for empty password
            logger.warning("Attempted to add user with empty password.")
            self.error_label_add_user.configure(text="Password cannot be empty.")
            return

        if password != confirm_password:
            logger.warning("Passwords do not match during new user creation.")
            self.error_label_add_user.configure(text="Passwords do not match.")
            return
        
        # Check for duplicate username using User model
        if User.get_by_username(username):
            logger.warning(f"Attempted to add user with duplicate username: {username}")
            self.error_label_add_user.configure(text=f"Username '{username}' already exists.")
            return

        self.error_label_add_user.configure(text="")

        # Create user using User.create()
        new_user_obj = User.create(username=username, password=password, address=address, is_admin=is_admin)

        if new_user_obj:
            logger.info(f"New user '{username}' (ID: {new_user_obj.user_id}) created successfully in DB.")
            self._load_and_display_users() # Refresh table from DB
            if hasattr(self, 'add_user_dialog') and self.add_user_dialog.winfo_exists():
                self.add_user_dialog.destroy()
        else:
            logger.error(f"Failed to create user '{username}' in database.")
            self.error_label_add_user.configure(text="Failed to save user. Check logs.")

    def _open_edit_user_dialog(self, user_id_to_edit):
        if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
            safe_focus(self.edit_user_dialog)
            return
        
        user_to_edit_obj = User.get_by_id(user_id_to_edit) # Fetch user object from DB
        if not user_to_edit_obj:
            logger.error(f"User with ID {user_id_to_edit} not found for editing in DB.")
            messagebox.showerror("Error", "Could not find the user to edit. The user list may have been updated.")
            self._load_and_display_users() # Refresh from DB
            return
        
        self.current_edit_user_id = user_id_to_edit 
        self.current_editing_username_for_dialog = user_to_edit_obj.username # Store username for delete dialog

        self.edit_user_dialog = ctk.CTkToplevel(self)
        self.edit_user_dialog.title(f"Swigato - Edit User - {user_to_edit_obj.username}")
        set_swigato_icon(self.edit_user_dialog)
        center_window(self.edit_user_dialog, 400, 530)
        self.edit_user_dialog.configure(fg_color=MODERN_ADMIN_BG) # Set Toplevel background
        self.edit_user_dialog.transient(self.master)  # type: ignore[arg-type]
        self.edit_user_dialog.grab_set()

        dialog_main_frame = ctk.CTkFrame(self.edit_user_dialog, fg_color=MODERN_ADMIN_CARD, corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]) # Use modern theme
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(dialog_main_frame, text="Username:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.username_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                                text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.username_entry_edit.insert(0, user_to_edit_obj.username)
        self.username_entry_edit.pack(fill="x", pady=(0,10))

        # Password Fields (Optional: Leave blank to keep current password)
        ctk.CTkLabel(dialog_main_frame, text="New Password (leave blank to keep current):", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(5,2))
        self.password_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                               text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.password_entry_edit.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(dialog_main_frame, text="Confirm New Password:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.confirm_password_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                                       text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.confirm_password_entry_edit.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(dialog_main_frame, text="Address:", font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]), text_color=MODERN_ADMIN_TEXT).pack(anchor="w", pady=(0,2))
        self.address_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                              text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.address_entry_edit.insert(0, user_to_edit_obj.address if user_to_edit_obj.address else '') 
        self.address_entry_edit.pack(fill="x", pady=(0,10))

        self.is_admin_var_edit = ctk.BooleanVar(value=user_to_edit_obj.is_admin)
        admin_switch_edit = ctk.CTkSwitch(dialog_main_frame, text="Is Admin?", variable=self.is_admin_var_edit,
                                      font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                      text_color=MODERN_ADMIN_TEXT,
                                      progress_color=MODERN_ADMIN_ACCENT,
                                      fg_color=MODERN_ADMIN_TEXT_SECONDARY,
                                      button_color=MODERN_ADMIN_ACCENT,
                                      button_hover_color=MODERN_ADMIN_BUTTON_HOVER)
        admin_switch_edit.pack(anchor="w", pady=(0,15))

        self.error_label_edit_user = ctk.CTkLabel(dialog_main_frame, text="", text_color=ERROR_COLOR, font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["small"]))
        self.error_label_edit_user.pack(pady=(5,0))

        # --- Buttons ---
        # Main container for all buttons, to be packed at the bottom of dialog_main_frame
        self.action_buttons_container = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        self.action_buttons_container.pack(fill="x", pady=(20,0), side="bottom") # Increased top padding

        # Frame for top row buttons (Delete, Cancel)
        top_buttons_frame = ctk.CTkFrame(self.action_buttons_container, fg_color="transparent")
        top_buttons_frame.pack(fill="x", pady=(0, 10)) # Add some padding below this row

        self.delete_button_edit_dialog = ctk.CTkButton(
            top_buttons_frame, text="Delete User",
            command=self._confirm_delete_user_from_dialog,
            fg_color=ERROR_COLOR,
            hover_color="#C00000",
            text_color="white",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"], weight="bold"),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        self.delete_button_edit_dialog.pack(side="left", padx=(0, 10))

        self.cancel_button_edit_dialog = ctk.CTkButton(
            top_buttons_frame, text="Cancel",
            command=lambda: (self.edit_user_dialog.destroy(), setattr(self, 'current_edit_user_id', None), setattr(self, 'current_editing_username_for_dialog', None)),
            fg_color=MODERN_ADMIN_TEXT_SECONDARY, hover_color=MODERN_ADMIN_ACCENT, text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        self.cancel_button_edit_dialog.pack(side="right", padx=(10, 0))

        # Frame for bottom row button (Save Changes) - to help with centering
        bottom_buttons_frame = ctk.CTkFrame(self.action_buttons_container, fg_color="transparent")
        bottom_buttons_frame.pack(fill="x")

        self.save_button_edit_dialog = ctk.CTkButton(
            bottom_buttons_frame, text="Save Changes", command=self._save_edited_user,
            fg_color=MODERN_ADMIN_BUTTON, hover_color=MODERN_ADMIN_BUTTON_HOVER, text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"],
            width=150
        )
        self.save_button_edit_dialog.pack(pady=(5,0), anchor="center")

        safe_focus(self.username_entry_edit)

    def _confirm_delete_user_from_dialog(self):
        if self.current_edit_user_id is None or self.current_editing_username_for_dialog is None:
            logger.warning("Attempted to delete user from edit dialog, but current_edit_user_id or username is not set.")
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                messagebox.showerror("Error", "Cannot identify user to delete. Please close and reopen the edit dialog.")
            return

        user_id_to_delete = self.current_edit_user_id
        username_for_dialog = self.current_editing_username_for_dialog
        if self.loggedInUser and self.loggedInUser.user_id == user_id_to_delete:
            logger.warning(f"Admin user '{self.loggedInUser.username}' (ID: {self.loggedInUser.user_id}) attempted to delete themselves (User ID to delete: {user_id_to_delete}).")
            messagebox.showerror("Action Denied", "Administrators cannot delete their own accounts through this panel.")
            return

        # Withdraw the edit dialog before showing the password prompt
        if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
            self.edit_user_dialog.withdraw() 

        # Call the new method to prompt for admin password
        self._prompt_admin_password_for_delete(user_id_to_delete, username_for_dialog)

    def _prompt_admin_password_for_delete(self, user_id_to_delete, username_for_dialog):
        if hasattr(self, 'admin_password_prompt_dialog') and self.admin_password_prompt_dialog.winfo_exists():
            safe_focus(self.admin_password_prompt_dialog)
            return

        self.admin_password_prompt_dialog = ctk.CTkToplevel(self)
        self.admin_password_prompt_dialog.title("Swigato - Admin Verification")
        set_swigato_icon(self.admin_password_prompt_dialog)
        center_window(self.admin_password_prompt_dialog, 380, 280)
        self.admin_password_prompt_dialog.configure(fg_color=MODERN_ADMIN_BG)
        self.admin_password_prompt_dialog.transient(self.master)  # type: ignore[arg-type] 
        self.admin_password_prompt_dialog.grab_set()

        prompt_main_frame = ctk.CTkFrame(self.admin_password_prompt_dialog, fg_color=MODERN_ADMIN_CARD, corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"]) # Use modern theme
        prompt_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(prompt_main_frame, text=f"Enter your admin password to authorize deletion of user '{username_for_dialog}':",
                     font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                     text_color=MODERN_ADMIN_TEXT, wraplength=360).pack(pady=(0,15))

        self.admin_password_entry_prompt = ctk.CTkEntry(prompt_main_frame, width=300, show="*",
                                                     font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
                                                     text_color=MODERN_ADMIN_TEXT, fg_color=MODERN_ADMIN_BG, border_color=MODERN_ADMIN_ACCENT, corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"])
        self.admin_password_entry_prompt.pack(fill="x", pady=(0,10))
        safe_focus(self.admin_password_entry_prompt)

        self.admin_password_error_label = ctk.CTkLabel(prompt_main_frame, text="",
                                                     text_color=ERROR_COLOR,
                                                     font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["small"]))
        self.admin_password_error_label.pack(pady=(0,15))

        buttons_prompt_frame = ctk.CTkFrame(prompt_main_frame, fg_color="transparent")
        buttons_prompt_frame.pack(fill="x", pady=(10,0), side="bottom")

        def _on_confirm_delete_with_password():
            entered_password = self.admin_password_entry_prompt.get()
            if not entered_password:
                self.admin_password_error_label.configure(text="Password cannot be empty.")
                return

            if self.loggedInUser and self.loggedInUser.verify_password(entered_password):
                logger.info(f"Admin password verified for deleting user '{username_for_dialog}'.")
                if hasattr(self, 'admin_password_prompt_dialog') and self.admin_password_prompt_dialog.winfo_exists():
                    self.admin_password_prompt_dialog.destroy()
                
                self._delete_user(user_id_to_delete, username_for_dialog) # Proceed with actual deletion
                
                if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                    self.edit_user_dialog.destroy() # Ensure edit dialog is closed
                self.current_edit_user_id = None
                self.current_editing_username_for_dialog = None
            else:
                logger.warning(f"Admin password verification failed for deleting user '{username_for_dialog}'.")
                self.admin_password_error_label.configure(text="Incorrect admin password.")
                self.admin_password_entry_prompt.delete(0, ctk.END) # Clear the password field

        def _on_cancel_password_prompt():
            if hasattr(self, 'admin_password_prompt_dialog') and self.admin_password_prompt_dialog.winfo_exists():
                self.admin_password_prompt_dialog.destroy()
            # Restore the edit dialog if deletion was cancelled
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                try:
                    self.edit_user_dialog.deiconify()
                    safe_focus(self.edit_user_dialog)
                except Exception as e:
                    logger.warning(f"Could not restore focus to edit_user_dialog: {e}")
            else:
                logger.info("Edit user dialog does not exist, skipping deiconify/focus.")
            logger.info(f"Admin password prompt cancelled for deleting user '{username_for_dialog}'.")

        confirm_delete_btn = ctk.CTkButton(
            buttons_prompt_frame, text="Confirm Delete", command=_on_confirm_delete_with_password,
            fg_color=ERROR_COLOR, hover_color="#C00000", text_color="white",
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"], weight="bold"),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        confirm_delete_btn.pack(side="right", padx=(10,0))

        cancel_prompt_btn = ctk.CTkButton(
            buttons_prompt_frame, text="Cancel", command=_on_cancel_password_prompt,
            fg_color=MODERN_ADMIN_TEXT_SECONDARY, hover_color=MODERN_ADMIN_ACCENT, text_color=MODERN_ADMIN_TEXT,
            font=ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]),
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["medium"]
        )
        cancel_prompt_btn.pack(side="right")

    def _save_edited_user(self):
        if self.current_edit_user_id is None:
            logger.error("Attempted to save edited user but no user ID was set.")
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            return

        user_to_update_obj = User.get_by_id(self.current_edit_user_id) # Get user object from DB
        if not user_to_update_obj:
            logger.error(f"User with ID {self.current_edit_user_id} not found for saving in DB.")
            self.error_label_edit_user.configure(text="User not found. Please refresh.")
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            self.current_edit_user_id = None
            self._load_and_display_users() # Refresh table
            return

        original_username = user_to_update_obj.username
        new_username = self.username_entry_edit.get().strip()
        new_password = self.password_entry_edit.get() # Get new password
        confirm_new_password = self.confirm_password_entry_edit.get() # Get confirm password
        new_address = self.address_entry_edit.get().strip()
        new_is_admin = self.is_admin_var_edit.get()

        if not new_username:
            logger.warning("Attempted to save user with empty username.")
            self.error_label_edit_user.configure(text="Username cannot be empty.")
            return

        # Password validation (only if a new password is provided)
        if new_password:
            if new_password != confirm_new_password:
                logger.warning("New passwords do not match during user edit.")
                self.error_label_edit_user.configure(text="New passwords do not match.")
                return
        
        if new_username.lower() != original_username.lower():
            existing_user_with_new_name = User.get_by_username(new_username)
            if existing_user_with_new_name and existing_user_with_new_name.user_id != self.current_edit_user_id:
                logger.warning(f"Attempted to save user with duplicate username: {new_username}")
                self.error_label_edit_user.configure(text=f"Username '{new_username}' already exists.")
                return
        
        self.error_label_edit_user.configure(text="")

        update_success = True
        # Update username (conditionally, using direct DB for now as User model doesn't have a direct method)
        if user_to_update_obj.username != new_username:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, user_to_update_obj.user_id))
                conn.commit()
                user_to_update_obj.username = new_username # Update object in memory
                logger.info(f"Username for user ID {user_to_update_obj.user_id} updated to '{new_username}'.")
            except Exception as e:
                logger.error(f"Error updating username for user ID {user_to_update_obj.user_id}: {e}")
                update_success = False
            finally:
                conn.close()

        # Update password (only if a new password was provided)
        if new_password: # Only update if a new password was entered
            if not user_to_update_obj.update_password(new_password):
                update_success = False
                logger.error(f"Failed to update password for user {user_to_update_obj.username}")

        if user_to_update_obj.address != new_address:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET address = ? WHERE user_id = ?", (new_address, user_to_update_obj.user_id))
                conn.commit()
                user_to_update_obj.address = new_address  # Update object in memory
                logger.info(f"Address for user ID {user_to_update_obj.user_id} updated to '{new_address}'.")
            except Exception as e:
                logger.error(f"Error updating address for user ID {user_to_update_obj.user_id}: {e}")
                update_success = False
            finally:
                conn.close()
        
        if user_to_update_obj.is_admin != new_is_admin:
            if not user_to_update_obj.update_admin_status(new_is_admin):
                update_success = False
                logger.error(f"Failed to update admin status for user {user_to_update_obj.username}")
        
        if update_success:
            logger.info(f"User data updated for '{user_to_update_obj.username}' (ID: {user_to_update_obj.user_id}).")
            self._load_and_display_users() # Refresh table from DB
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            self.current_edit_user_id = None
        else:
            self.error_label_edit_user.configure(text="Failed to save some changes. Check logs.")

    def _on_cell_click(self, event_data):
        row_clicked_on_gui = event_data["row"]
        column_clicked = event_data["column"]
        logger.info(f"Cell clicked: Display Row {row_clicked_on_gui}, Column {column_clicked}")

        if row_clicked_on_gui == 0: 
            return

        user_view_index = row_clicked_on_gui - 1 

        if not (0 <= user_view_index < len(self.current_view_users)):
            logger.warning(f"Clicked on table but view_index {user_view_index} is out of bounds for current_view_users (len {len(self.current_view_users)}).")
            return
        
        user_dict = self.current_view_users[user_view_index]
        user_id = user_dict['id']
        username = user_dict['username']

        if column_clicked == self.actions_column_index:
            logger.info(f"Actions column clicked for user ID {user_id}. Opening edit dialog as default.")
            self._open_edit_user_dialog(user_id)
        else:
            logger.info(f"Clicked on non-interactive column {column_clicked} for user ID {user_id}. No action.")

    def _confirm_delete_user(self, user_id_to_delete, username_for_dialog):
        user_to_delete_obj = User.get_by_id(user_id_to_delete)        
        if not user_to_delete_obj:
            logger.error(f"User with ID {user_id_to_delete} not found for deletion confirmation in DB.")
            messagebox.showerror("Error", "User not found. The list may have been updated.")
            self._load_and_display_users()
            return
        
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user '{username_for_dialog}' (ID: {user_id_to_delete})?")
        if confirm:
            self._delete_user(user_id_to_delete, username_for_dialog)

    def _delete_user(self, user_id_to_delete, username_for_logging):
        if User.delete_by_username(username_for_logging):
            logger.info(f"User '{username_for_logging}' (ID: {user_id_to_delete}) deleted successfully from DB.")
            self._load_and_display_users()        
        else:
            logger.warning(f"Failed to delete user '{username_for_logging}' (ID: {user_id_to_delete}) from DB. They might have already been deleted or an error occurred.")
            messagebox.showwarning("Deletion Failed", f"User '{username_for_logging}' could not be deleted. The list might have been updated or an error occurred.")
            self._load_and_display_users()

    def _toggle_admin_status(self, user_id_to_toggle):
        user_to_modify_obj = User.get_by_id(user_id_to_toggle)
        if not user_to_modify_obj:
            logger.error(f"User with ID {user_id_to_toggle} not found for toggling admin status in DB.")
            messagebox.showerror("Error", "User not found. The list may have been updated.")
            self._load_and_display_users()
            return
        
        old_status = user_to_modify_obj.is_admin
        new_status = not old_status
        if user_to_modify_obj.update_admin_status(new_status):
            logger.info(f"Toggled admin status for user '{user_to_modify_obj.username}' (ID: {user_id_to_toggle}) from {old_status} to {new_status} in DB.")
            self._load_and_display_users()
        else:
            logger.error(f"Failed to toggle admin status for user '{user_to_modify_obj.username}' (ID: {user_id_to_toggle}) in DB.")
            messagebox.showerror("Error", "Failed to update admin status. Check logs.")
            self._load_and_display_users()

    def _load_and_display_users(self):
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') and self.search_entry.winfo_exists() else ""
        admin_filter_status = self.admin_filter_var.get() if hasattr(self, 'admin_filter_var') else "All"
        
        logger.debug(f"Loading users from DB. Search: '{search_term}', Filter: '{admin_filter_status}'")

        all_users_from_db = User.get_all_users()
        
        self.users_data = []
        if all_users_from_db:
            for user_obj in all_users_from_db:
                self.users_data.append({
                    'id': user_obj.user_id,
                    'username': user_obj.username,
                    'is_admin': user_obj.is_admin,
                    'address': user_obj.address if user_obj.address else ""
                })

        filtered_user_list = []
        source_users = self.users_data

        for user_item in source_users:
            passes_admin_filter = False
            if admin_filter_status == "All":
                passes_admin_filter = True
            elif admin_filter_status == "Admin" and user_item['is_admin']:
                passes_admin_filter = True
            elif admin_filter_status == "Non-Admin" and not user_item['is_admin']:
                passes_admin_filter = True

            if not passes_admin_filter:
                continue

            passes_search_filter = False
            if not search_term: 
                passes_search_filter = True
            else:
                if search_term in str(user_item['id']).lower():
                    passes_search_filter = True
                elif search_term in user_item['username'].lower():
                    passes_search_filter = True
                elif 'address' in user_item and user_item['address'] and search_term in user_item['address'].lower():
                    passes_search_filter = True
            
            if not passes_search_filter:
                continue
            
            filtered_user_list.append(user_item)

        self.current_view_users = filtered_user_list 
        logger.debug(f"Displaying {len(self.current_view_users)} users after filtering.")

        # Create modern table with enhanced styling
        table_values = [["ID", "Username", "Admin?", "Address", "Actions"]]
        for user_item_view in self.current_view_users: 
            table_values.append([
                user_item_view['id'],
                user_item_view['username'],
                "Yes" if user_item_view['is_admin'] else "No",
                user_item_view.get('address', 'N/A'), 
                "Edit / Delete"
            ])

        if self.user_table:
            self.user_table.destroy()
            self.user_table = None 

        header_font = ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"]+2, weight="bold")
        cell_font = ctk.CTkFont(family=MODERN_ADMIN_FONT_FAMILY, size=MODERN_ADMIN_FONT_SIZES["medium"])
        
        if len(table_values) == 1 and (search_term or admin_filter_status != "All"):
             logger.info("No users match current filter criteria. Table will be empty or show header only.")
        elif not source_users:
             logger.info("No users in the master list. Table will be empty or show header only.")

        self.user_table = CTkTable(
            master=self.table_frame,
            values=table_values, 
            font=cell_font,  # type: ignore[arg-type]
            colors=[MODERN_ADMIN_TABLE["row_light"], MODERN_ADMIN_TABLE["row_dark"]],
            header_color=MODERN_ADMIN_TABLE["header_bg"],
            text_color=MODERN_ADMIN_TABLE["text"],
            hover_color=MODERN_ADMIN_TABLE["hover"],
            corner_radius=MODERN_ADMIN_BORDER_RADIUS["large"],
            border_width=2,
            border_color=MODERN_ADMIN_TABLE["border"],
            command=self._on_cell_click,
            wraplength=200
        )
        self.user_table.pack(expand=True, fill="both", padx=MODERN_ADMIN_SPACING["xlarge"], pady=MODERN_ADMIN_SPACING["xlarge"])

        if table_values: 
            self.user_table.edit_row(0, text_color="#FF6B35", font=header_font, fg_color=MODERN_ADMIN_TABLE["header_bg"])

        for i in range(1, len(table_values)): 
            current_bg_color = MODERN_ADMIN_TABLE["row_light"] if i % 2 != 0 else MODERN_ADMIN_TABLE["row_dark"]
            self.user_table.edit_row(i, fg_color=current_bg_color, text_color=MODERN_ADMIN_TABLE["text"], hover_color=MODERN_ADMIN_TABLE["hover"], font=cell_font)

    def refresh_data(self):
        logger.info("AdminUsersScreen: Refreshing data (called externally)...")
        self._load_and_display_users()
        self.update_idletasks()

