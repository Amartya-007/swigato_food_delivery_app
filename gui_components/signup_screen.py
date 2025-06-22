import customtkinter as ctk
from PIL import Image
import os

# GUI Constants
from gui_constants import (
    PRIMARY_COLOR,
    BACKGROUND_COLOR,
    ENTRY_BG_COLOR,
    TEXT_COLOR,
    BUTTON_HOVER_COLOR,
    SUCCESS_COLOR,
    DISABLED_BUTTON_COLOR,
    FRAME_FG_COLOR
)

# Define constants
APP_LOGO_PATH = "assets/swigato_icon.png"
FONT_FAMILY = "Segoe UI"

class SignupScreen(ctk.CTkFrame):
    def __init__(self, master, show_login_screen_callback, signup_success_callback):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.master = master
        self.show_login_screen_callback = show_login_screen_callback
        self.signup_success_callback = signup_success_callback
        self.password_visible = False
        self.confirm_password_visible = False

        # Outer Card
        card = ctk.CTkFrame(self, fg_color=FRAME_FG_COLOR, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.95)

        # Logo
        try:
            self.logo_img = ctk.CTkImage(light_image=Image.open(APP_LOGO_PATH), size=(100, 100))
            logo_label = ctk.CTkLabel(card, image=self.logo_img, text="")
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_label = ctk.CTkLabel(card, text="Swigato", font=("Segoe UI", 28, "bold"), text_color=PRIMARY_COLOR)
        logo_label.pack(pady=(15, 0))

        # Title
        title_label = ctk.CTkLabel(card, text="Create Account", font=(FONT_FAMILY, 20, "bold"), text_color=TEXT_COLOR)
        title_label.pack(pady=(5, 0))

        # Form Section
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(pady=10, padx=20, fill="both", expand=True)        # Username Field
        ctk.CTkLabel(form, text="Username:", font=(FONT_FAMILY, 14), text_color=TEXT_COLOR).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(form, height=40, fg_color=ENTRY_BG_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=6,
                                           placeholder_text="Choose a username")
        self.username_entry.pack(fill="x", pady=5)

        # Password Field
        ctk.CTkLabel(form, text="Password:", font=(FONT_FAMILY, 14), text_color=TEXT_COLOR).pack(anchor="w", pady=(10, 0))
        password_row = ctk.CTkFrame(form, fg_color="transparent")
        password_row.pack(fill="x", pady=5)

        self.password_entry = ctk.CTkEntry(password_row, height=40, fg_color=ENTRY_BG_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=6,
                                           placeholder_text="Create a password")
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.toggle_password_button = ctk.CTkButton(password_row, text="Show", width=50,
                                                    command=self.toggle_password_visibility,
                                                    fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                                    hover_color=PRIMARY_COLOR)
        self.toggle_password_button.pack(side="left", padx=(5, 0))

        # Confirm Password Field
        ctk.CTkLabel(form, text="Confirm Password:", font=(FONT_FAMILY, 14), text_color=TEXT_COLOR).pack(anchor="w", pady=(10, 0))
        confirm_password_row = ctk.CTkFrame(form, fg_color="transparent")
        confirm_password_row.pack(fill="x", pady=5)

        self.confirm_password_entry = ctk.CTkEntry(confirm_password_row, height=40, fg_color=ENTRY_BG_COLOR,
                                                   border_color=PRIMARY_COLOR, show="*", corner_radius=6,
                                                   placeholder_text="Confirm your password")
        self.confirm_password_entry.pack(side="left", fill="x", expand=True)
        self.confirm_password_entry.bind("<Return>", self.signup_event)

        self.toggle_confirm_password_button = ctk.CTkButton(confirm_password_row, text="Show", width=50,
                                                            command=self.toggle_confirm_password_visibility,
                                                            fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                                            hover_color=PRIMARY_COLOR)
        self.toggle_confirm_password_button.pack(side="left", padx=(5, 0))

        # Sign Up Button
        self.signup_button = ctk.CTkButton(form, text="Create Account",
                                           command=self.signup_event,
                                           fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                           font=(FONT_FAMILY, 16, "bold"), height=40)
        self.signup_button.pack(fill="x", pady=(15, 10))

        # Status Label
        self.status_label = ctk.CTkLabel(form, text="", font=(FONT_FAMILY, 12))
        self.status_label.pack()

        # Bottom section (Login link)
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(pady=(2, 10), fill="x")

        # Login Prompt
        login_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        login_row.pack()
        ctk.CTkLabel(login_row, text="Already have an account?", font=(FONT_FAMILY, 12), text_color=TEXT_COLOR).pack(side="left")
        ctk.CTkButton(login_row, text="Log In", font=(FONT_FAMILY, 12, "bold"),
                      command=self.show_login_screen_callback,
                      fg_color="transparent", text_color=PRIMARY_COLOR,
                      hover_color=BACKGROUND_COLOR, width=60).pack(side="left", padx=(4, 0))

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.toggle_password_button.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_password_button.configure(text="Hide")
            self.password_visible = True

    def toggle_confirm_password_visibility(self):
        if self.confirm_password_visible:
            self.confirm_password_entry.configure(show="*")
            self.toggle_confirm_password_button.configure(text="Show")
            self.confirm_password_visible = False
        else:
            self.confirm_password_entry.configure(show="")
            self.toggle_confirm_password_button.configure(text="Hide")
            self.confirm_password_visible = True

    def signup_event(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Basic validation
        if not username or not password or not confirm_password:
            self.status_label.configure(text="All fields are required.", text_color="red")
            return

        if password != confirm_password:
            self.status_label.configure(text="Passwords do not match.", text_color="red")
            return

        if len(password) < 6:
            self.status_label.configure(text="Password must be at least 6 characters.", text_color="red")
            return

        # TODO: Add actual signup logic here
        print(f"Attempting signup - Username: {username}")
        self.status_label.configure(text="Signup logic not implemented.", text_color="orange")
