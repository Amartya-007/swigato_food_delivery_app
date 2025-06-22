import os

folders = [
    "admin",
    "assets/menu_items",
    "assets/restaurants",
    "cart",
    "data",
    "delivery",
    "gui_components",
    "orders",
    "restaurants",
    "reviews",
    "users",
    "utils"
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Optional: Create placeholder files (uncomment to include dummy files)
placeholder_files = {
    "admin/__init__.py": "",
    "admin/actions.py": "",
    "cart/__init__.py": "",
    "cart/models.py": "",
    "data/remember_me.json": "",
    "data/swigato_app.log": "",
    "data/swigato.db": "",
    "delivery/__init__.py": "",
    "delivery/tracker.py": "",
    "orders/__init__.py": "",
    "orders/models.py": "",
    "restaurants/__init__.py": "",
    "restaurants/models.py": "",
    "reviews/__init__.py": "",
    "reviews/models.py": "",
    "users/__init__.py": "",
    "users/auth.py": "",
    "users/models.py": "",
    "utils/__init__.py": "",
    "utils/database.py": "",
    "utils/image_loader.py": "",
    "utils/logger.py": "",
    "utils/update_schema.py": "",
    "utils/validation.py": "",
    "gui_app.py": "",
    "gui_constants.py": "",
    "main.py": "",
    "README.md": "",
    ".gitignore": "",
}

# Create placeholder files (if needed)
for path, content in placeholder_files.items():
    with open(path, "w") as f:
        f.write(content)

print("Project structure created.")
