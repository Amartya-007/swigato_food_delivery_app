import bcrypt
import sqlite3 # Import sqlite3 for exception handling
from utils.database import get_db_connection
from utils.logger import log

class User:
    def __init__(self, user_id, username, password_hash, address=None, email=None, phone=None, created_at=None, is_admin=False):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.address = address
        self.email = email
        self.phone = phone
        self.created_at = created_at # Should be set by DB or on creation
        self.is_admin = is_admin # Added is_admin

    def __repr__(self):
        return f"<User {self.username} (ID: {self.user_id}) Admin: {self.is_admin}>" # Updated repr
    
    def update_address(self, new_address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET address = ? WHERE user_id = ?", (new_address, self.user_id))
            conn.commit()
            self.address = new_address
            log(f"Address updated for user ID {self.user_id} in DB.")
            return True
        except Exception as e:
            log(f"Error updating address for user ID {self.user_id}: {e}")
            return False
        finally:
            conn.close()

    def update_email(self, new_email):
        """Updates the user's email in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, self.user_id))
            conn.commit()
            self.email = new_email
            log(f"Email updated for user ID {self.user_id} in DB.")
            return True
        except Exception as e:
            log(f"Error updating email for user ID {self.user_id}: {e}")
            return False
        finally:
            conn.close()

    def update_phone(self, new_phone):
        """Updates the user's phone number in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (new_phone, self.user_id))
            conn.commit()
            self.phone = new_phone
            log(f"Phone updated for user ID {self.user_id} in DB.")
            return True
        except Exception as e:
            log(f"Error updating phone for user ID {self.user_id}: {e}")
            return False
        finally:
            conn.close()

    def update_username(self, new_username):
        """Updates the user's username in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, self.user_id))
            conn.commit()
            self.username = new_username
            log(f"Username updated for user ID {self.user_id} in DB.")
            return True
        except Exception as e:
            log(f"Error updating username for user ID {self.user_id}: {e}")
            return False
        finally:
            conn.close()

    def update_admin_status(self, new_admin_status: bool):
        """Updates the user's admin status in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (new_admin_status, self.user_id))
            conn.commit()
            self.is_admin = new_admin_status # Update the instance attribute as well
            log(f"Admin status for user ID {self.user_id} ('{self.username}') updated to {new_admin_status} in DB.") # Corrected f-string
            return True
        except Exception as e:
            log(f"Error updating admin status for user ID {self.user_id} ('{self.username}'): {e}") # Corrected f-string
            return False
        finally:
            conn.close()

    def update_password(self, new_password):
        """Updates the user's password in the database after hashing it."""
        if not new_password:
            log(f"Password update for user ID {self.user_id} ('{self.username}') skipped: new password is empty.")
            return False # Or raise an error

        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", 
                           (new_password_hash.decode('utf-8'), self.user_id))
            conn.commit()
            self.password_hash = new_password_hash.decode('utf-8') # Update instance attribute
            log(f"Password for user ID {self.user_id} ('{self.username}') updated successfully.")
            return True
        except Exception as e:
            log(f"Error updating password for user ID {self.user_id} ('{self.username}'): {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def create(username, password, address=None, email=None, phone=None, is_admin=False):
        """Creates a new user in the database."""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, address, email, phone, is_admin) VALUES (?, ?, ?, ?, ?, ?)", 
                           (username, password_hash.decode('utf-8'), address, email, phone, is_admin))
            conn.commit()
            user_id = cursor.lastrowid
            log(f"User '{username}' created with ID {user_id}, Admin status: {is_admin}.")            # Fetch the created_at timestamp from the DB for the new User object
            new_user_data = User.get_by_id(user_id) # Re-fetch to get all fields like created_at and is_admin
            return new_user_data
        except sqlite3.IntegrityError: # Handles unique username constraint
            log(f"Username '{username}' already exists.")
            return None
        except Exception as e:
            log(f"Error creating user '{username}': {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """Retrieves a user by username from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, username, password_hash, address, email, phone, created_at, is_admin FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return User(user_id=row['user_id'], username=row['username'], 
                            password_hash=row['password_hash'], address=row['address'], 
                            email=row['email'], phone=row['phone'], 
                            created_at=row['created_at'], is_admin=row['is_admin'])
            return None
        except Exception as e:
            log(f"Error fetching user '{username}': {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """Retrieves a user by user_id from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id, username, password_hash, address, email, phone, created_at, is_admin FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(user_id=row['user_id'], username=row['username'], 
                            password_hash=row['password_hash'], address=row['address'], 
                            email=row['email'], phone=row['phone'],
                            created_at=row['created_at'], is_admin=row['is_admin'])
            return None
        except Exception as e:
            log(f"Error fetching user ID {user_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_users():
        """Retrieves all users from the database, ordered by user_id ascending.""" # Updated docstring
        conn = get_db_connection()
        cursor = conn.cursor()
        users = []
        try:
            # Modified SQL query to order by user_id ASC
            cursor.execute("SELECT user_id, username, password_hash, address, email, phone, created_at, is_admin FROM users ORDER BY user_id ASC")
            rows = cursor.fetchall()
            for row in rows:
                users.append(User(user_id=row['user_id'], username=row['username'],
                                  password_hash=row['password_hash'], address=row['address'],
                                  email=row['email'], phone=row['phone'],
                                  created_at=row['created_at'], is_admin=row['is_admin']))
            return users
        except Exception as e:
            log(f"Error fetching all users: {e}")
            return []
        finally:
            conn.close()

    def verify_password(self, password):
        """Verifies the given password against the stored hash."""
        if self.password_hash:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        return False

    @staticmethod
    def delete_by_username(username):
        """Deletes a user by username from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                log(f"User '{username}' not found. Nothing to delete.")
                return False

            user_id_to_delete = user['user_id']

            # Optional: Delete associated reviews (if reviews table has user_id FK)
            cursor.execute("DELETE FROM reviews WHERE user_id = ?", (user_id_to_delete,))
            log(f"Deleted reviews associated with user ID {user_id_to_delete} ('{username}').")

            # Now delete the user
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id_to_delete,))
            conn.commit()
            log(f"User '{username}' (ID: {user_id_to_delete}) deleted successfully.")
            return True
        except sqlite3.Error as e:
            log(f"Database error deleting user '{username}': {e}")
            conn.rollback()
            return False
        except Exception as e:
            log(f"Unexpected error deleting user '{username}': {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_favorite_restaurant(self, restaurant_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO user_favorites (user_id, restaurant_id, item_id) VALUES (?, ?, NULL)", (self.user_id, restaurant_id))
            conn.commit()
            return True
        except Exception as e:
            log(f"Error adding favorite restaurant: {e}")
            return False
        finally:
            conn.close()

    def remove_favorite_restaurant(self, restaurant_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM user_favorites WHERE user_id = ? AND restaurant_id = ? AND item_id IS NULL", (self.user_id, restaurant_id))
            conn.commit()
            return True
        except Exception as e:
            log(f"Error removing favorite restaurant: {e}")
            return False
        finally:
            conn.close()

    def is_favorite_restaurant(self, restaurant_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM user_favorites WHERE user_id = ? AND restaurant_id = ? AND item_id IS NULL", (self.user_id, restaurant_id))
            return cursor.fetchone() is not None
        except Exception as e:
            log(f"Error checking favorite restaurant: {e}")
            return False
        finally:
            conn.close()

    def get_favorite_restaurants(self):
        from restaurants.models import Restaurant
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT restaurant_id FROM user_favorites WHERE user_id = ? AND restaurant_id IS NOT NULL", (self.user_id,))
            rows = cursor.fetchall()
            return [Restaurant.get_by_id(row[0]) for row in rows if row[0] is not None]
        except Exception as e:
            log(f"Error fetching favorite restaurants: {e}")
            return []
        finally:
            conn.close()

    def add_favorite_menu_item(self, item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR IGNORE INTO user_favorites (user_id, restaurant_id, item_id) VALUES (?, NULL, ?)", (self.user_id, item_id))
            conn.commit()
            return True
        except Exception as e:
            log(f"Error adding favorite menu item: {e}")
            return False
        finally:
            conn.close()

    def remove_favorite_menu_item(self, item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM user_favorites WHERE user_id = ? AND item_id = ? AND restaurant_id IS NULL", (self.user_id, item_id))
            conn.commit()
            return True
        except Exception as e:
            log(f"Error removing favorite menu item: {e}")
            return False
        finally:
            conn.close()

    def is_favorite_menu_item(self, item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM user_favorites WHERE user_id = ? AND item_id = ? AND restaurant_id IS NULL", (self.user_id, item_id))
            return cursor.fetchone() is not None
        except Exception as e:
            log(f"Error checking favorite menu item: {e}")
            return False
        finally:
            conn.close()

    def get_favorite_menu_items(self):
        from restaurants.models import MenuItem
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT item_id FROM user_favorites WHERE user_id = ? AND item_id IS NOT NULL", (self.user_id,))
            rows = cursor.fetchall()
            return [MenuItem.get_by_id(row[0]) for row in rows if row[0] is not None]
        except Exception as e:
            log(f"Error fetching favorite menu items: {e}")
            return []
        finally:
            conn.close()
