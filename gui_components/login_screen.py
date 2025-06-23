import customtkinter as ctk
from PIL import Image
import os
import json  # Added for remember me
from users.auth import log_in
from gui_Light import PRIMARY_COLOR, BACKGROUND_COLOR, ENTRY_BG_COLOR, TEXT_COLOR, BUTTON_HOVER_COLOR, SUCCESS_COLOR, DISABLED_BUTTON_COLOR

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, show_signup_screen_callback, login_success_callback):  # Modified signature
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.master = master
        self.show_signup_screen_callback = show_signup_screen_callback
        self.login_success_callback = login_success_callback  # Store the new generic callback
        self.password_visible = False  # State for password visibility

        # Define path for remember_me.json
        self.remember_me_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "remember_me.json")        # Load Swigato image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "..", "assets", "swigato_icon.png")  # Fixed path
        try:
            self.swigato_image = ctk.CTkImage(light_image=Image.open(image_path), size=(100, 100))
            self.swigato_image_label = ctk.CTkLabel(self, image=self.swigato_image, text="")
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 5), sticky="s")
        except Exception as e:
            print(f"Error loading Swigato icon in LoginScreen: {e}")
            self.swigato_image_label = ctk.CTkLabel(self, text="Swigato", text_color=PRIMARY_COLOR, font=ctk.CTkFont(size=36, weight="bold"))
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 10), sticky="s")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50, pady=(5, 20), sticky="nwe")
        form_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(form_frame, text="Welcome Back!", text_color=TEXT_COLOR, font=ctk.CTkFont(size=24, weight="bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        username_label = ctk.CTkLabel(form_frame, text="Username or Email:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        username_label.grid(row=1, column=0, columnspan=2, pady=(0, 0), sticky="sw")
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=5, placeholder_text="Enter your username or email")
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        self.username_entry.bind("<Return>", self.login_event)

        password_label = ctk.CTkLabel(form_frame, text="Password:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        password_label.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="sw")

        password_input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_input_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        password_input_frame.grid_columnconfigure(0, weight=1)
        password_input_frame.grid_columnconfigure(1, weight=0)

        self.password_entry = ctk.CTkEntry(password_input_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=5, placeholder_text="Enter your password")
        self.password_entry.grid(row=0, column=0, sticky="nwe")
        self.password_entry.bind("<Return>", self.login_event)

        self.toggle_password_button = ctk.CTkButton(password_input_frame, text="Show", width=40, height=40,
                                                    fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR,
                                                    command=self.toggle_password_visibility)
        self.toggle_password_button.grid(row=0, column=1, padx=(5, 0), sticky="nwe")        # Create a frame for Remember Me and Forgot Password on the same row
        remember_forgot_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        remember_forgot_frame.grid(row=5, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        remember_forgot_frame.grid_columnconfigure(0, weight=1)  # Left side for remember me
        remember_forgot_frame.grid_columnconfigure(1, weight=0)  # Right side for forgot password

        self.remember_me_checkbox = ctk.CTkCheckBox(remember_forgot_frame, text="Remember Me", text_color=TEXT_COLOR,
                                                    fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                                    border_color=PRIMARY_COLOR)
        self.remember_me_checkbox.grid(row=0, column=0, sticky="w")

        # Forgot Password Button (moved to same row as Remember Me)
        forgot_pw_btn = ctk.CTkButton(remember_forgot_frame, text="Forgot Password?", 
                                     fg_color="transparent", text_color=PRIMARY_COLOR, 
                                     hover_color=BACKGROUND_COLOR, 
                                     font=ctk.CTkFont(size=12, underline=True), 
                                     width=120, command=self.forgot_password_dialog)
        forgot_pw_btn.grid(row=0, column=1, sticky="e")

        self._load_remembered_user()  # Load remembered user

        self.login_button = ctk.CTkButton(form_frame, text="Login", command=self.login_event, width=300, height=40,
                                          fg_color=PRIMARY_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                          font=ctk.CTkFont(size=16, weight="bold"), corner_radius=5)
        self.login_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="nwe")

        self.status_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky="nwe")

        signup_prompt_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        signup_prompt_frame.grid(row=8, column=0, columnspan=2, pady=(5, 0), sticky="nwe")
        signup_prompt_frame.grid_columnconfigure(0, weight=1)  # Center the content

        signup_text = ctk.CTkLabel(signup_prompt_frame, text="Don't have an account?", text_color=TEXT_COLOR, font=ctk.CTkFont(size=12))
        signup_text.pack(side="left", padx=(0, 5))  # Pack to allow side-by-side

        signup_button = ctk.CTkButton(signup_prompt_frame, text="Sign Up",
                                      command=self.show_signup_screen_callback,  # Use stored callback
                                      fg_color="transparent", text_color=PRIMARY_COLOR,
                                      hover_color=BACKGROUND_COLOR,  # Subtle hover
                                      font=ctk.CTkFont(size=12, underline=True, weight="bold"),
                                      width=50)
        signup_button.pack(side="left")

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
        self.status_label.configure(text="")
        original_button_text = "Login"
        self.login_button.configure(state="disabled", text="Logging in...", fg_color=DISABLED_BUTTON_COLOR)

        username = self.username_entry.get()
        password = self.password_entry.get()
        remember_me = self.remember_me_checkbox.get() == 1  # Get checkbox state

        def process_login_attempt():
            if not username or not password:
                self.status_label.configure(text="Username and Password are required.", text_color=PRIMARY_COLOR)
                self.login_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)
                return

            user = log_in(username, password)
            if user:
                if remember_me:
                    self._save_remembered_user(username)
                else:
                    self._clear_remembered_user()
                self.status_label.configure(text=f"Welcome back, {user.username}!", text_color=SUCCESS_COLOR)
                # Schedule the screen transition using the new callback
                self.master.after(0, lambda: self.login_success_callback(user))  # MODIFIED THIS LINE
            else:
                self.status_label.configure(text="Invalid username or password.", text_color=PRIMARY_COLOR)
                # Only re-enable the button if login failed and the widget still exists
                if self.login_button.winfo_exists():
                    self.login_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)

        self.after(100, process_login_attempt)

    def forgot_password_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Password")
        dialog.geometry("340x260")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Reset Password", font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(18, 8))
        ctk.CTkLabel(dialog, text="Enter your username or email:").pack(pady=(4, 2))
        user_entry = ctk.CTkEntry(dialog, width=220)
        user_entry.pack(pady=(2, 8))
        ctk.CTkLabel(dialog, text="New Password:").pack(pady=(4, 2))
        new_pw_entry = ctk.CTkEntry(dialog, show="*", width=220)
        new_pw_entry.pack(pady=(2, 8))
        msg_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=12))
        msg_label.pack(pady=(4, 2))
        def do_reset():
            username_or_email = user_entry.get().strip()
            new_pw = new_pw_entry.get().strip()
            if not username_or_email or not new_pw:
                msg_label.configure(text="All fields required.", text_color=PRIMARY_COLOR)
                return
            from users.models import User
            user = User.get_by_username(username_or_email)
            if not user:
                msg_label.configure(text="User not found.", text_color="#D32F2F")
                return
            user.update_password(new_pw)
            msg_label.configure(text="Password reset! You can now log in.", text_color=SUCCESS_COLOR)
        ctk.CTkButton(dialog, text="Reset Password", command=do_reset, fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=TEXT_COLOR).pack(pady=10)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy, fg_color="#eee", text_color="#333").pack(pady=(2, 8))

    def _load_remembered_user(self):
        try:
            if os.path.exists(self.remember_me_file_path):
                with open(self.remember_me_file_path, "r") as f:
                    data = json.load(f)
                    remembered_username = data.get("username")
                    if remembered_username:
                        self.username_entry.insert(0, remembered_username)
                        self.remember_me_checkbox.select()  # Check the box if user was loaded
                        # Do not set focus here; let App.show_login_screen handle it
                        return
        except Exception as e:
            print(f"Error loading remembered user: {e}")
        # Do not set focus here; let App.show_login_screen handle it

    def _save_remembered_user(self, username):
        try:
            os.makedirs(os.path.dirname(self.remember_me_file_path), exist_ok=True)  # Ensure data directory exists
            with open(self.remember_me_file_path, "w") as f:
                json.dump({"username": username}, f)
        except Exception as e:
            print(f"Error saving remembered user: {e}")

    def _clear_remembered_user(self):
        try:
            if os.path.exists(self.remember_me_file_path):
                os.remove(self.remember_me_file_path)
        except Exception as e:
            print(f"Error clearing remembered user: {e}")

