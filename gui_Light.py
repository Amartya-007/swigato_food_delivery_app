import logging
import os

PRIMARY_COLOR = "#FF5722"      # Swiggy Orange
SECONDARY_COLOR = "#D32F2F"    # Zomato Red
BACKGROUND_COLOR = "#F8FAFC"   # Modern Light Background (Slightly bluer, more modern)
FRAME_FG_COLOR = "#FFFFFF"     # Card/Section Background
FRAME_BORDER_COLOR = "#E2E8F0" # Modern Light Border (Subtle gray-blue)
ENTRY_BG_COLOR = "#F1F5F9"     # Modern Input Background
TEXT_COLOR = "#1E293B"         # Modern Dark Text (Slate)
BUTTON_TEXT_COLOR = "#FFFFFF"  # White text on buttons
BUTTON_MAIN_BG_COLOR = PRIMARY_COLOR # Main background for buttons
BUTTON_HOVER_COLOR = "#E2470D" # Modern Orange Hover
SUCCESS_COLOR = "#10B981"      # Modern Green (Emerald)
ERROR_COLOR = "#EF4444"        # Modern Red
DISABLED_BUTTON_COLOR = "#94A3B8" # Modern Disabled (Slate)

GRAY_TEXT_COLOR = "#64748B"    # Modern Muted Text (Slate-500)
ACCENT_COLOR = "#8B5CF6"       # Modern Purple Accent
CARD_SHADOW_COLOR = "#0F172A10" # Subtle shadow for cards
GLASS_BG_COLOR = "#FFFFFF80"   # Semi-transparent white for glassmorphism
LIGHT_ORANGE_BG = "#FFF4F0"    # Light orange background for tags
LIGHT_PURPLE_BG = "#F3F4F6"    # Light purple/gray background
HOVER_BG_COLOR = "#F1F5F9"     # Light hover background
MODERN_BORDER = "#E5E7EB"      # Modern subtle border color
SEMI_TRANSPARENT_OVERLAY = "black"  # Use solid black for overlay (Tkinter does not support alpha)
CLOSE_BUTTON_BG = "#EEEEEE"  # For close button background
CLOSE_BUTTON_TEXT = "#333333"  # For close button text

# Font Settings - Modern Typography
FONT_FAMILY = "Inter"  # Modern, clean font
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 18

# Derived font sizes for specific UI elements
HEADING_FONT_SIZE = 24              # Larger for main headings
SUB_HEADING_FONT_SIZE = 18          # For section headers
BODY_FONT_SIZE = FONT_SIZE_NORMAL   # Standard body text
BUTTON_FONT_SIZE = FONT_SIZE_NORMAL # Button text
SMALL_FONT_SIZE = 12                # For minor text

# Font weights
FONT_WEIGHT_BOLD = "bold"
FONT_WEIGHT_MEDIUM = "normal"  # CTk doesn't support medium, using normal
FONT_WEIGHT_REGULAR = "normal"

# Other Constants
WINDOW_ICON_PATH = "assets/swigato_icon.ico"
APP_LOGO_PATH = "assets/swigato_icon.png"

# Admin Panel Modern Dark Theme Colors
ADMIN_BACKGROUND_COLOR = "#1a1a1a"     # Dark background
ADMIN_TEXT_COLOR = "#ffffff"           # White text
ADMIN_PRIMARY_COLOR = "#ff5722"        # Modern orange (toned down from bright)
ADMIN_PRIMARY_ACCENT_COLOR = "#2a2a2a" # Dark gray for accents
ADMIN_SECONDARY_ACCENT_COLOR = "#3a3a3a" # Slightly lighter dark gray

# Modern table colors with subtle contrast
ADMIN_TABLE_HEADER_BG_COLOR = "#2d2d2d"  # Neutral dark gray header
ADMIN_TABLE_HEADER_TEXT_COLOR = "#ffffff" # White header text
ADMIN_TABLE_ROW_LIGHT_COLOR = "#242424"   # Zebra stripe light
ADMIN_TABLE_ROW_DARK_COLOR = "#1f1f1f"    # Zebra stripe dark
ADMIN_TABLE_BORDER_COLOR = "#404040"      # Subtle border
ADMIN_TABLE_TEXT_COLOR = "#e0e0e0"        # Light gray text
ADMIN_FRAME_FG_COLOR = "#232323"          # Card backgrounds

# Modern button styling
ADMIN_BUTTON_FG_COLOR = "#ff5722"         # Orange buttons
ADMIN_BUTTON_HOVER_COLOR = "#e64a19"      # Darker orange hover
ADMIN_BUTTON_TEXT_COLOR = "#ffffff"       # White button text

# Additional modern colors
ADMIN_CARD_BG_COLOR = "#2a2a2a"           # Card backgrounds
ADMIN_SIDEBAR_COLOR = "#1f1f1f"           # Sidebar background
ADMIN_HOVER_COLOR = "#333333"             # Hover states
ADMIN_ACTIVE_COLOR = "#ff5722"            # Active states
ADMIN_BORDER_COLOR = "#404040"            # General borders

ICON_PATH = os.path.join("assets", "swigato_icon.ico")

def set_swigato_icon(window):
    """Set the Swigato brand icon on a Tkinter/CTk window, with error handling."""
    if hasattr(window, 'iconbitmap'):
        try:
            import os
            # Get the project root directory (assuming gui_Light.py is in the root)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "assets", "swigato_icon.ico")
            
            if os.path.exists(icon_path):
                def apply_icon():
                    try:
                        if window.winfo_exists():
                            window.iconbitmap(icon_path)
                    except:
                        pass
                
                # Set icon immediately
                apply_icon()
                # Set icon multiple times with increasing delays to override CTK
                for delay in [10, 50, 100, 200, 500, 1000]:
                    window.after(delay, apply_icon)
                    
                # Also set up a periodic check to maintain the icon
                def maintain_icon():
                    try:
                        if window.winfo_exists():
                            window.iconbitmap(icon_path)
                            window.after(2000, maintain_icon)  # Check every 2 seconds
                    except:
                        pass
                
                window.after(1500, maintain_icon)  # Start maintaining after 1.5 seconds
            else:
                logging.warning(f"Swigato icon file not found at {icon_path}.")
        except Exception as e:
            logging.error(f"Failed to set Swigato icon: {e}")
    else:
        logging.warning("Window does not support iconbitmap().")

def safe_focus(widget):
    """Safely set focus to a widget if it exists and its top-level window exists."""
    try:
        if widget and widget.winfo_exists():
            # Check if the widget's top-level window also exists
            toplevel_window = widget.winfo_toplevel()
            if toplevel_window and toplevel_window.winfo_exists():
                widget.focus()
            else:
                logging.warning(f"Could not set focus: Widget's top-level window does not exist for {widget}.")
    except Exception as e:
        # This might catch errors if winfo_exists() or winfo_toplevel() are called on an already destroyed widget
        logging.warning(f"Could not set focus due to an error: {e} for widget {widget}")

def center_window(window, width, height):
    """Center a window on the screen with the given width and height."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")