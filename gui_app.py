import customtkinter as ctk
import os

# Import GUI components
from gui_components.login_screen import LoginScreen
from gui_components.signup_screen import SignupScreen

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

class SwigatoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("Swigato - Food Delivery App")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Set Windows icon
        if os.name == 'nt':
            try:
                self.iconbitmap("swigato_icon.ico")
            except Exception as e:
                print(f"Could not load icon: {e}")
        
        # Initialize current screen
        self.current_screen = None
        
        # Show login screen initially
        self.show_login_screen()

    def show_login_screen(self):
        """Display the login screen"""
        if self.current_screen:
            self.current_screen.destroy()
        
        self.current_screen = LoginScreen(            self, 
            show_signup_screen_callback=self.show_signup_screen,
            login_success_callback=self.handle_login_success
        )
        self.current_screen.pack(fill="both", expand=True)
        # Focus on username entry if it's empty, password entry if username is filled
        self.after(100, self._focus_login_field)

    def show_signup_screen(self):
        """Display the signup screen"""
        if self.current_screen:
            self.current_screen.destroy()
        
        self.current_screen = SignupScreen(
            self,
            show_login_screen_callback=self.show_login_screen,
            signup_success_callback=self.handle_signup_success
        )
        self.current_screen.pack(fill="both", expand=True)
        # Focus on username entry
        self.after(100, self._focus_signup_field)

    def _focus_login_field(self):
        """Focus on the appropriate field in login screen"""
        if (hasattr(self.current_screen, 'username_entry') and 
            hasattr(self.current_screen, 'password_entry')):
            try:
                if self.current_screen.username_entry.get():
                    self.current_screen.password_entry.focus()
                else:
                    self.current_screen.username_entry.focus()
            except Exception:
                pass  # Ignore if fields don't exist or can't be focused

    def _focus_signup_field(self):
        """Focus on username entry in signup screen"""
        if hasattr(self.current_screen, 'username_entry'):
            try:
                self.current_screen.username_entry.focus()
            except Exception:
                pass  # Ignore if field doesn't exist or can't be focused

    def handle_login_success(self, user):
        """Handle successful login"""
        print(f"Login successful for user: {user}")
        # TODO: Navigate to main app screen
        self.show_main_app()

    def handle_signup_success(self, user):
        """Handle successful signup"""
        print(f"Signup successful for user: {user}")
        # TODO: Navigate to main app screen or back to login
        self.show_login_screen()

    def show_main_app(self):
        """Show the main application interface"""
        if self.current_screen:
            self.current_screen.destroy()
        
        # TODO: Create and show main app screen
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)
        
        welcome_label = ctk.CTkLabel(
            main_frame, 
            text="Welcome to Swigato!\nMain app coming soon...", 
            font=("Segoe UI", 20, "bold"),
            text_color=PRIMARY_COLOR
        )
        welcome_label.pack(expand=True)
        
        logout_button = ctk.CTkButton(
            main_frame,
            text="Logout",
            command=self.show_login_screen,
            fg_color=PRIMARY_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        logout_button.pack(pady=20)
        
        self.current_screen = main_frame

if __name__ == "__main__":
    # Set appearance mode and theme
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    app = SwigatoApp()
    app.mainloop()
