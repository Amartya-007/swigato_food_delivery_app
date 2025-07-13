# Swigato 🍔🍕🍟 – The Food App

## *A Python Project by Amartya Vishwakarma (a.k.a. That Guy Who Codes at 2AM)*

Hey there, fellow coder, foodie, or random internet traveler! I’m **Amartya Vishwakarma**, and this is **Swigato** – my not-so-humble attempt to bring Swiggy/Zomato vibes to my laptop (minus the actual food delivery, sorry, you still gotta walk to the mess).

This project started as a CLI app for a college assignment, but then I got carried away. Now it’s a full-blown GUI food ordering platform with admin superpowers, a database, and more features than my college canteen menu. Grab a snack and read on!

---

## 🚀 What Can You Do With Swigato?

### 👀 If You’re Just Browsing (Guest Mode)

- Browse all the restaurants (even the ones with suspicious hygiene).
- Check out detailed menus with prices and descriptions.
- Add food to your cart and place orders as a guest (no commitment, no judgment).
- Leave reviews and ratings (because everyone’s a critic).

### 🧑‍💻 If You’re a Registered User

- Sign up with a super-secure (bcrypt-hashed!) password.
- Log in and keep your foodie history forever (or until you uninstall).
- Everything a guest can do, plus:
  - See your order history (so you can regret your choices later).
  - Leave reviews that actually update the restaurant’s average rating.

### 🦸‍♂️ If You’re The Admin (a.k.a. Me)

- Access the secret Admin Dashboard (no cape required).
- Manage users: view, add, edit, or delete anyone (except yourself, for safety!).
- Manage restaurants: add new places, edit details, or nuke them (deletes their menu & reviews too – use wisely).
- Menu management: add, edit, or remove dishes for any restaurant.
- Order management: see all orders (user & guest), update statuses (Pending → Out for Delivery → Delivered), and judge people’s food choices.
- Review moderation: read and delete reviews if they’re spammy, mean, or just plain weird.

---

## 🛠️ Tech Stack (a.k.a. How I Made This Monster)

- **Python 3.x** – The brains of the operation.
- **CustomTkinter** – For that modern, not-ugly GUI.
- **SQLite** – File-based database, because I’m not paying for AWS.
- **bcrypt** – For password hashing, so even I can’t see your secrets.
- **Rich** – For making the CLI version look less like Notepad.
- **CTkTable** – For pretty tables in the GUI.
- **Pillow** – For images, because food apps need food pics.

---

## 🏗️ How It’s All Organized (a.k.a. My Digital Mess)

```text
📁 swigato_food_delivery_app/
├── 📂 admin/                    # Admin functionalities
│   └── actions.py              # All admin operations & database management
├── 📂 assets/                  # All the visual goodies
│   ├── swigato_icon.ico        # Our brand identity
│   ├── swigato_icon.png        # Brand logo (PNG version)
│   ├── 📂 menu_items/          # Food pics to make you hungry
│   └── 📂 restaurants/         # Restaurant images & banners
├── 📂 cart/                    # Shopping cart logic
│   └── models.py              # Cart data models & operations
├── 📂 data/                    # Where all the magic is stored
│   ├── swigato.db             # SQLite database (the heart)
│   ├── swigato_app.log        # Debug logs (my debugging diary)
│   └── remember_me.json       # For "Remember Me" functionality
├── 📂 delivery/                # Delivery tracking (future scope)
│   └── tracker.py             # Order status tracking
├── 📂 gui_components/          # All the GUI screens & dialogs
│   ├── admin_dashboard.py     # Admin control panel
│   ├── admin_orders_screen.py # Order management for admin
│   ├── admin_restaurants_screen.py # Restaurant management
│   ├── admin_reviews_screen.py # Review moderation panel
│   ├── admin_users_screen.py  # User management dashboard
│   ├── cart_screen.py         # Shopping cart interface
│   ├── login_screen.py        # User authentication
│   ├── main_app_screen.py     # Main application window
│   ├── menu_screen.py         # Restaurant menu display
│   ├── restaurant_management_screen.py # Restaurant operations
│   └── signup_screen.py       # New user registration
├── 📂 orders/                  # Order processing logic
│   └── models.py              # Order data models & database ops
├── 📂 restaurants/             # Restaurant management
│   └── models.py              # Restaurant data & menu operations
├── 📂 reviews/                 # Rating & review system
│   └── models.py              # Review data models
├── 📂 users/                   # User management & authentication
│   ├── auth.py                # Password hashing & validation
│   └── models.py              # User data models
├── 📂 utils/                   # Helper utilities
│   ├── database.py            # Database initialization & setup
│   ├── image_loader.py        # Image loading utilities
│   ├── logger.py              # Logging configuration
│   └── validation.py          # Input validation functions
├── gui_app.py                 # 🚀 Main GUI application (start here!)
├── gui_Light.py               # UI theme & styling constants
├── main.py                    # CLI version (for the retro feel)
├── requirements.txt           # Dependencies (the essentials)
└── README.md                  # You're reading this! 📖

```

---

## 🖥️ Main Features

- **Modern GUI**: CustomTkinter-powered, looks good even at 3AM.
- **Authentication**: Sign up, log in, bcrypt-hashed passwords (no plain text, promise).
- **Restaurant Discovery**: Browse, search, and drool over menus.
- **Cart System**: Add, remove, and update items before you commit to your cravings.
- **Order Placement**: Place orders as guest or user, with real-time status updates.
- **Order History**: Users can see all their past (questionable) food decisions.
- **Review System**: Leave reviews, rate restaurants, and see average ratings update live.
- **Admin Panel**: Manage users, restaurants, menus, orders, and reviews from a slick dashboard.
- **Review Moderation**: Admin can delete reviews that are too spicy (or just spam).
- **Database Integration**: All data is persistent – your midnight orders are safe forever.
- **Security**: bcrypt for passwords, input validation everywhere, and no SQL injection allowed.
- **Logging**: Everything gets logged, so I can debug your weird bugs.

---

Here's your updated **"How To Run (a.k.a. Become a Swigato Power User)"** guide with virtual environment setup included:

---

## 🧑‍🔬 How To Run (a.k.a. Become a Swigato Power User)

1. **Clone the repo:**

   ```bash
   git clone https://github.com/Amartya-007/swigato_project
   cd swigato_project
   ```

2. **(Optional but Recommended) Create and activate a virtual environment:**

   **Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the GUI app:**

   ```bash
   python gui_app.py
   ```

   Or, for nostalgia, run the CLI version:

   ```bash
   python main.py
   ```

5. **First run?**
   - The app creates the database, tables, and a default admin user for you.
   - Sample restaurants and menu items are added so you’re not staring at an empty screen.

**Default Admin Login:**

- Username: `admin`
- Password: `admin123`

(Please change these if you’re not me. Seriously.)

---

## 🏆 Project Highlights & Fun Facts

- Started as a one-night assignment, became a semester-long obsession.
- Learned more about CTkinter, databases, and debugging than any textbook could teach.
- The admin can’t delete themselves (learned that the hard way).
- Every feature was tested by ordering imaginary biryani at 1AM.
- The codebase is modular, so adding new features is (almost) painless.

---

## 🔮 What’s Next? (a.k.a. My Wish List)

- Real-time order tracking (with fake delivery boys?)
- Payment gateway integration (Monopoly money, maybe?)
- Restaurant owner dashboard
- Mobile app (if I ever learn Kivy or Flutter)
- More analytics for admins (because graphs are cool)

---

## 👨‍💻 How it completed

This project is the result of too much caffeine, too little sleep, and a lot of Stack Overflow and of course **AI (My Partner in crime)**. If you read this far, you deserve a samosa. Or at least a star on GitHub. 😉

*“Why settle for basic when you can go big?”* – That’s how Swigato happened.

---

© 2025 Amartya Vishwakarma | Built with ❤️, Python, and way too much ☕
