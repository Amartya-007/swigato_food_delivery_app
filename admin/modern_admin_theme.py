# Modern Admin Theme for Swigato
# Dark theme with orange accents matching the main app
# theme.py

# 🎨 Color Palette
MODERN_ADMIN_BG = "#1a1a1a"                  # Main background
MODERN_ADMIN_SIDEBAR = "#2d2d2d"             # Sidebar background
MODERN_ADMIN_CARD = "#323232"                # Cards / panels
MODERN_ADMIN_ACCENT = "#ff6b35"              # Swigato orange
MODERN_ADMIN_TEXT = "#ffffff"                # Primary text
MODERN_ADMIN_TEXT_SECONDARY = "#b0b0b0"      # Secondary text
MODERN_ADMIN_BUTTON = "#ff6b35"              # Button color
MODERN_ADMIN_BUTTON_HOVER = "#ff5722"        # Button hover
MODERN_ADMIN_DIVIDER = "#3a3a3a"             # Divider/line
MODERN_ADMIN_TABLE_ROW_HOVER = "#393939"     # Hovered row bg

# ✅ Status colors (tags, badges, states)
MODERN_ADMIN_STATUS = {
    "active": "#4caf50",     # Green
    "pending": "#ff9800",    # Orange
    "error": "#f44336",      # Red
    "info": "#2196f3",       # Blue
}

# Legacy compatibility
ERROR_COLOR = MODERN_ADMIN_STATUS["error"]

# ✅ Font System
MODERN_ADMIN_FONT_FAMILY = "Roboto"
MODERN_ADMIN_FONT_SIZES = {
    "small": 10,
    "normal": 12,
    "medium": 14,
    "large": 16,
    "xlarge": 20,
    "title": 24,
    "heading": 28
}

def get_font(size="normal"):
    return (MODERN_ADMIN_FONT_FAMILY, MODERN_ADMIN_FONT_SIZES.get(size, 12))

# ✅ Spacing (margins, padding)
MODERN_ADMIN_SPACING = {
    "small": 5,
    "medium": 10,
    "large": 15,
    "xlarge": 20
}

# ✅ Component Sizes
MODERN_ADMIN_SIDEBAR_WIDTH = 280
MODERN_ADMIN_HEADER_HEIGHT = 80
MODERN_ADMIN_BUTTON_HEIGHT = 40
MODERN_ADMIN_CARD_HEIGHT = 60

# ✅ Border Radius
MODERN_ADMIN_BORDER_RADIUS = {
    "small": 4,
    "default": 8,
    "medium": 8,
    "large": 12
}

# ✅ Shadows (for future CTkCanvas/Toplevel overlays)
MODERN_ADMIN_SHADOW = {
    "light": "0 2px 4px rgba(0,0,0,0.1)",
    "medium": "0 4px 8px rgba(0,0,0,0.2)",
    "heavy": "0 8px 16px rgba(0,0,0,0.3)"
}

# ✅ Elevation Layering
MODERN_ADMIN_Z_INDEX = {
    "base": 0,
    "dropdown": 10,
    "modal": 20,
    "tooltip": 30
}

# ✅ Animation Duration (ms)
MODERN_ADMIN_ANIMATION_DURATION = 150

# 📊 Table styling (modern theme)
MODERN_ADMIN_TABLE = {
    "header_bg": MODERN_ADMIN_CARD,
    "header_text": MODERN_ADMIN_TEXT,
    "row_light": MODERN_ADMIN_BG,
    "row_dark": "#262626",
    "text": MODERN_ADMIN_TEXT,
    "border": MODERN_ADMIN_ACCENT,
    "hover": MODERN_ADMIN_TABLE_ROW_HOVER
}
