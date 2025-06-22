import customtkinter as ctk
from PIL import Image
import os
import json

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

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, show_signup_screen_callback, login_success_callback):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.master = master
        self.show_signup_screen_callback = show_signup_screen_callback
        self.login_success_callback = login_success_callback
        self.password_visible = False

        # Outer Card
        card = ctk.CTkFrame(self, fg_color=FRAME_FG_COLOR, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.95)

        # Logo
        try:
            self.logo_img = ctk.CTkImage(light_image=Image.open(APP_LOGO_PATH), size=(120, 120))
            logo_label = ctk.CTkLabel(card, image=self.logo_img, text="")
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_label = ctk.CTkLabel(card, text="Swigato", font=("Segoe UI", 30, "bold"), text_color=PRIMARY_COLOR)
        logo_label.pack(pady=(20, 0))

        # Form Section
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(pady=10, padx=20, fill="both", expand=True)

        # Username Field
        ctk.CTkLabel(form, text="Username or Email:", font=(FONT_FAMILY, 14), text_color=TEXT_COLOR).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(form, height=40, fg_color=ENTRY_BG_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=6,
                                           placeholder_text="Enter your username or email")
        self.username_entry.pack(fill="x", pady=5)

        # Password Field
        ctk.CTkLabel(form, text="Password:", font=(FONT_FAMILY, 14), text_color=TEXT_COLOR).pack(anchor="w", pady=(10, 0))
        password_row = ctk.CTkFrame(form, fg_color="transparent")
        password_row.pack(fill="x", pady=5)

        self.password_entry = ctk.CTkEntry(password_row, height=40, fg_color=ENTRY_BG_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=6,
                                           placeholder_text="Enter your password")
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.password_entry.bind("<Return>", self.login_event)

        self.toggle_password_button = ctk.CTkButton(password_row, text="Show", width=50,
                                                    command=self.toggle_password_visibility,
                                                    fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                                    hover_color=PRIMARY_COLOR)
        self.toggle_password_button.pack(side="left", padx=(5, 0))

        # Remember Me
        self.remember_me_checkbox = ctk.CTkCheckBox(form, text="Remember Me", text_color=TEXT_COLOR,
                                                    fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                                    border_color=PRIMARY_COLOR)
        self.remember_me_checkbox.pack(anchor="w", pady=(0, 15))

        # Login Button
        self.login_button = ctk.CTkButton(form, text="Login",
                                          command=self.login_event,
                                          fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                          font=(FONT_FAMILY, 16, "bold"), height=40)
        self.login_button.pack(fill="x", pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(form, text="", font=(FONT_FAMILY, 12))
        self.status_label.pack()

        # Bottom section (Sign Up + Forgot Password)
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(pady=(2, 10), fill="x")

        # Sign Up Prompt
        signup_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        signup_row.pack(pady=(0, 4))
        ctk.CTkLabel(signup_row, text="Don't have an account?", font=(FONT_FAMILY, 12), text_color=TEXT_COLOR).pack(side="left")
        ctk.CTkButton(signup_row, text="Sign Up", font=(FONT_FAMILY, 12, "bold"),
                      command=self.show_signup_screen_callback,
                      fg_color="transparent", text_color=PRIMARY_COLOR,
                      hover_color=BACKGROUND_COLOR, width=60).pack(side="left", padx=(4, 0))

        # Forgot Password Button (centered)
        ctk.CTkButton(bottom_frame, text="Forgot Password?",
                      command=self.forgot_password_event,
                      font=(FONT_FAMILY, 12), fg_color="transparent", text_color=PRIMARY_COLOR,
                      hover_color=BACKGROUND_COLOR, width=140).pack()

        # Load remembered username
        self._load_remembered_user()

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.toggle_password_button.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_password_button.configure(text="Hide")
            self.password_visible = True

    def login_event(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.configure(text="Username and password are required.", text_color="red")
            return
        print(f"Attempting login with Username: {username}")
        self.status_label.configure(text="Login logic not implemented.", text_color="orange")

    def forgot_password_event(self):
        print("Forgot password clicked!")
        self.status_label.configure(text="Forgot password logic not implemented.", text_color="orange")

    def _load_remembered_user(self):
        remember_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "remember_me.json")
        try:
            if os.path.exists(remember_path):
                with open(remember_path, "r") as f:
                    data = json.load(f)
                    remembered_username = data.get("username")
                    if remembered_username:
                        self.username_entry.insert(0, remembered_username)
                        self.remember_me_checkbox.select()
        except Exception as e:
            print(f"Error loading remembered user: {e}")
