import customtkinter as ctk
import os
from PIL import Image
from gui_Light import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, ERROR_COLOR, GRAY_TEXT_COLOR, ACCENT_COLOR, MODERN_BORDER, HOVER_BG_COLOR
from restaurants.models import MenuItem
from utils.image_loader import load_image
from utils.logger import log
from reviews.models import get_reviews_for_restaurant, add_review
from users.models import User
from tkinter import messagebox

class MenuScreen(ctk.CTkFrame):
    def __init__(self, app_ref, user, restaurant, show_cart_callback):
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)
        self.app_ref = app_ref
        self.user = user
        self.restaurant = restaurant
        self.show_cart_callback = show_cart_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Modern Header Frame
        self.grid_rowconfigure(1, weight=1)  # Main Scrollable Frame
        self.grid_rowconfigure(2, weight=0)  # Status Label

        # Attributes for inline review form
        self.is_review_form_visible = False
        self.rating_var = ctk.IntVar(value=0)
        self.star_button_widgets = []
        self.comment_textbox_widget = None
        self.write_review_button_widget = None
        self.inline_review_form_actual_frame = None

        # --- Modern Header Frame with Enhanced Styling ---
        self._create_modern_header()
        
        # --- Main Scrollable Frame ---
        self.main_scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=BACKGROUND_COLOR, 
            border_width=0,
            corner_radius=0
        )
        self.main_scroll_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.main_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self._populate_main_scroll_content()

        # --- Modern Status Label ---
        self.status_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=SUCCESS_COLOR
        )
        self.status_label.grid(row=2, column=0, pady=(0, 15), sticky="ew")

    def _create_modern_header(self):
        """Create a modern, elegant header with better visual hierarchy"""
        header_frame = ctk.CTkFrame(
            self, 
            fg_color=FRAME_FG_COLOR,
            corner_radius=20,
            border_width=1,
            border_color=MODERN_BORDER
        )
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Modern back button
        back_button = ctk.CTkButton(
            header_frame, 
            text="← Back",
            command=self.go_back_to_main_app,
            fg_color="transparent",
            text_color=GRAY_TEXT_COLOR,
            hover_color=HOVER_BG_COLOR,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80,
            height=36,
            corner_radius=12
        )
        back_button.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Restaurant info section
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        restaurant_name_text = self.restaurant.name if self.restaurant else "Menu"
        restaurant_name_label = ctk.CTkLabel(
            info_frame, 
            text=restaurant_name_text,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        restaurant_name_label.pack(anchor="w")

        if self.restaurant and hasattr(self.restaurant, 'description') and self.restaurant.description:
            restaurant_desc_label = ctk.CTkLabel(
                info_frame, 
                text=self.restaurant.description,
                text_color=GRAY_TEXT_COLOR,
                font=ctk.CTkFont(size=14),
                wraplength=400,
                anchor="w"
            )
            restaurant_desc_label.pack(anchor="w", pady=(5, 0))

        # Modern view cart button
        view_cart_button = ctk.CTkButton(
            header_frame, 
            text="🛒 View Cart",
            command=self.show_cart_callback,
            fg_color=ACCENT_COLOR,
            hover_color="#7C3AED",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=16
        )
        view_cart_button.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def _clear_main_scroll_content(self):
        for widget in self.main_scroll_frame.winfo_children():
            widget.destroy()
        self.write_review_button_widget = None
        self.inline_review_form_actual_frame = None
        self.comment_textbox_widget = None
        self.star_button_widgets = []

    def _populate_main_scroll_content(self):
        log("MenuScreen._populate_main_scroll_content called")
        self._clear_main_scroll_content()
        
        current_row = 0
        current_row = self._populate_menu_items_to_scroll_frame(self.main_scroll_frame, current_row)
        current_row = self._build_review_section_with_form_container(self.main_scroll_frame, current_row)
        current_row = self._populate_reviews_to_scroll_frame(self.main_scroll_frame, current_row)

    def _populate_menu_items_to_scroll_frame(self, parent_frame, start_row):
        """Create modern, beautiful food item cards with enhanced styling"""
        current_row = start_row
        log(f"_populate_menu_items_to_scroll_frame for restaurant: {self.restaurant.name if self.restaurant else 'None'}")

        if not self.restaurant:
            # Modern empty state
            empty_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=20,
                border_width=1,
                border_color=MODERN_BORDER
            )
            empty_frame.grid(row=current_row, column=0, pady=20, sticky="ew")
            
            no_restaurant_label = ctk.CTkLabel(
                empty_frame,
                text="🍽️ No restaurant selected",
                text_color=GRAY_TEXT_COLOR,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            no_restaurant_label.pack(pady=40)
            return current_row + 1

        menu_items = self.restaurant.menu
        if not menu_items:
            # Modern empty menu state
            empty_frame = ctk.CTkFrame(
                parent_frame,
                fg_color=FRAME_FG_COLOR,
                corner_radius=20,
                border_width=1,
                border_color=MODERN_BORDER
            )
            empty_frame.grid(row=current_row, column=0, pady=20, sticky="ew")
            
            no_items_label = ctk.CTkLabel(
                empty_frame,
                text="📋 Menu coming soon!",
                text_color=GRAY_TEXT_COLOR,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            no_items_label.pack(pady=40)
            return current_row + 1

        # Categorize menu items
        categorized_menu = {}
        for item in menu_items:
            if item.category not in categorized_menu:
                categorized_menu[item.category] = []
            categorized_menu[item.category].append(item)

        # Display each category with modern styling
        for category, items_in_category in categorized_menu.items():
            # Modern category header
            category_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
            category_container.grid(row=current_row, column=0, pady=(30, 15), sticky="ew")
            
            category_label = ctk.CTkLabel(
                category_container,
                text=category,
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color=TEXT_COLOR
            )
            category_label.pack(anchor="w")
            
            # Category underline
            underline = ctk.CTkFrame(
                category_container,
                fg_color=ACCENT_COLOR,
                height=3,
                corner_radius=2
            )
            underline.pack(anchor="w", fill="x", pady=(5, 0))
            
            current_row += 1

            # Display items in this category
            for item in items_in_category:
                # Modern food item card
                item_card = ctk.CTkFrame(
                    parent_frame,
                    fg_color=FRAME_FG_COLOR,
                    corner_radius=20,
                    border_width=1,
                    border_color=MODERN_BORDER
                )
                item_card.grid(row=current_row, column=0, pady=(0, 15), sticky="ew")
                item_card.grid_columnconfigure(1, weight=1)

                # Food image
                self._create_food_image(item_card, item)

                # Item details section
                details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                details_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
                details_frame.grid_columnconfigure(0, weight=1)

                # Item name
                item_name_label = ctk.CTkLabel(
                    details_frame,
                    text=item.name,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=TEXT_COLOR,
                    anchor="w"
                )
                item_name_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

                # Item description
                item_desc_label = ctk.CTkLabel(
                    details_frame,
                    text=item.description,
                    font=ctk.CTkFont(size=14),
                    text_color=GRAY_TEXT_COLOR,
                    wraplength=350,
                    justify="left",
                    anchor="w"
                )
                item_desc_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

                # Price and actions row
                bottom_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                bottom_frame.grid(row=2, column=0, sticky="ew")
                bottom_frame.grid_columnconfigure(0, weight=1)

                # Price
                price_label = ctk.CTkLabel(
                    bottom_frame,
                    text=f"₹{item.price:.2f}",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=ACCENT_COLOR,
                    anchor="w"
                )
                price_label.grid(row=0, column=0, sticky="w")

                # Action buttons container
                actions_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                actions_frame.grid(row=0, column=1, sticky="e")

                # Heart/Favorite button
                is_fav = self.user.is_favorite_menu_item(item.item_id)
                heart_text = "❤️" if is_fav else "🤍"
                heart_button = ctk.CTkButton(
                    actions_frame,
                    text=heart_text,
                    width=45,
                    height=45,
                    fg_color="transparent",
                    hover_color=HOVER_BG_COLOR,
                    font=ctk.CTkFont(size=18),
                    corner_radius=12,
                    command=lambda i=item, b=None: self._toggle_favorite_menu_item(i, b)
                )
                heart_button.pack(side="left", padx=(0, 10))
                heart_button.configure(command=lambda i=item, b=heart_button: self._toggle_favorite_menu_item(i, b))

                # Modern Add to Cart button
                add_to_cart_button = ctk.CTkButton(
                    actions_frame,
                    text="+ Add to Cart",
                    fg_color=ACCENT_COLOR,
                    hover_color="#7C3AED",
                    text_color="white",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    height=45,
                    corner_radius=16,
                    command=lambda i=item: self._add_to_cart(i)
                )
                add_to_cart_button.pack(side="left")

                current_row += 1
        return current_row

    def _create_food_image(self, parent_frame, item):
        """Create a modern food image with rounded corners and fallback"""
        if item.image_filename:
            project_root = self.app_ref.project_root
            image_path = os.path.join(project_root, "assets", "menu_items", item.image_filename)
            ctk_image = load_image(image_path, size=(120, 120))
            if ctk_image:
                image_label = ctk.CTkLabel(
                    parent_frame,
                    image=ctk_image,
                    text="",
                    corner_radius=16
                )
                image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
                return

        # Modern fallback image
        fallback_label = ctk.CTkLabel(
            parent_frame,
            text="🍽️",
            width=120,
            height=120,
            fg_color=HOVER_BG_COLOR,
            text_color=GRAY_TEXT_COLOR,
            font=ctk.CTkFont(size=40),
            corner_radius=16
        )
        fallback_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

    def _toggle_favorite_menu_item(self, menu_item, button):
        is_fav = self.user.is_favorite_menu_item(menu_item.item_id)
        if is_fav:
            self.user.remove_favorite_menu_item(menu_item.item_id)
        else:
            self.user.add_favorite_menu_item(menu_item.item_id)
        # Update button appearance
        new_is_fav = self.user.is_favorite_menu_item(menu_item.item_id)
        button.configure(text=("\u2665" if new_is_fav else "\u2661"), text_color=("#E53935" if new_is_fav else "#888"))

    def _build_review_section_with_form_container(self, parent_frame, start_row):
        current_row = start_row
        log("_build_review_section_with_form_container called")
        
        separator = ctk.CTkFrame(parent_frame, height=2, fg_color=FRAME_BORDER_COLOR)
        separator.grid(row=current_row, column=0, sticky="ew", pady=(20,10))
        current_row +=1

        review_header_internal_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        review_header_internal_frame.grid(row=current_row, column=0, pady=(10, 5), sticky="ew")
        review_header_internal_frame.grid_columnconfigure(0, weight=1)
        review_header_internal_frame.grid_columnconfigure(1, weight=0)

        reviews_title_label = ctk.CTkLabel(review_header_internal_frame, text="Customer Reviews",
                                           font=ctk.CTkFont(size=20, weight="bold"),
                                           text_color=PRIMARY_COLOR)
        reviews_title_label.grid(row=0, column=0, sticky="w")

        button_text = "Cancel Review" if self.is_review_form_visible else "Write a Review"
        self.write_review_button_widget = ctk.CTkButton(review_header_internal_frame, text=button_text,
                                                        command=self._on_write_review_button_click,
                                                        fg_color=SUCCESS_COLOR if not self.is_review_form_visible else ERROR_COLOR, 
                                                        text_color=TEXT_COLOR,
                                                        hover_color=BUTTON_HOVER_COLOR,
                                                        font=ctk.CTkFont(weight="bold"))
        self.write_review_button_widget.grid(row=0, column=1, sticky="e")
        current_row += 1

        self.inline_review_form_actual_frame = ctk.CTkFrame(parent_frame, fg_color=FRAME_FG_COLOR, corner_radius=8)

        if self.is_review_form_visible:
            self._build_actual_inline_form_content(self.inline_review_form_actual_frame)
            self.inline_review_form_actual_frame.grid(row=current_row, column=0, pady=(10, 15), padx=5, sticky="ew")
            current_row += 1
        else:
            if self.inline_review_form_actual_frame and self.inline_review_form_actual_frame.winfo_ismapped():
                self.inline_review_form_actual_frame.grid_forget()
        
        return current_row

    def _build_actual_inline_form_content(self, container_frame):
        log("_build_actual_inline_form_content called")
        container_frame.grid_columnconfigure(0, weight=1)

        self.star_button_widgets = []

        rating_prompt_label = ctk.CTkLabel(container_frame, text="Your Rating:", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_COLOR)
        rating_prompt_label.grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        stars_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        stars_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="w")

        for i in range(1, 6):
            star_btn = ctk.CTkButton(stars_frame, text="☆", width=35, height=35,
                                     font=ctk.CTkFont(size=20),
                                     fg_color="transparent",
                                     hover_color=BUTTON_HOVER_COLOR,
                                     text_color=PRIMARY_COLOR,
                                     command=lambda r=i: self._set_rating(r))
            star_btn.pack(side="left", padx=2)
            self.star_button_widgets.append(star_btn)
        self._update_star_buttons_display()

        comment_prompt_label = ctk.CTkLabel(container_frame, text="Your Review:", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_COLOR)
        comment_prompt_label.grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")
        
        self.comment_textbox_widget = ctk.CTkTextbox(container_frame, height=100, border_width=1, border_color=FRAME_BORDER_COLOR, fg_color=FRAME_FG_COLOR, text_color=TEXT_COLOR, wrap="word")
        self.comment_textbox_widget.grid(row=3, column=0, padx=10, pady=(0,10), sticky="ew")

        action_buttons_frame = ctk.CTkFrame(container_frame, fg_color="transparent")
        action_buttons_frame.grid(row=4, column=0, padx=10, pady=(0,10), sticky="e")        
        cancel_button = ctk.CTkButton(action_buttons_frame, text="Cancel",
                                        command=self._on_write_review_button_click,
                                        fg_color=SECONDARY_COLOR, hover_color=BUTTON_HOVER_COLOR)
        cancel_button.pack(side="left", padx=(0,10))
        
        submit_button = ctk.CTkButton(action_buttons_frame, text="Submit Review",
                                      command=self._submit_inline_review_action,
                                      fg_color=PRIMARY_COLOR, 
                                      hover_color=BUTTON_HOVER_COLOR)
        submit_button.pack(side="left", padx=(10, 0))

    def _set_rating(self, rating_value):
        self.rating_var.set(rating_value)
        self._update_star_buttons_display()

    def _update_star_buttons_display(self):
        current_rating = self.rating_var.get()
        for i, btn in enumerate(self.star_button_widgets):
            if (i + 1) <= current_rating:
                btn.configure(text="★", fg_color=PRIMARY_COLOR, text_color="yellow")
            else:
                btn.configure(text="☆", fg_color="transparent", text_color=PRIMARY_COLOR)

    def _submit_inline_review_action(self):
        log("_submit_inline_review_action called")
        rating = self.rating_var.get()
        
        if not self.comment_textbox_widget:
            log("Error: Comment textbox widget not found during submission.")
            return
        comment = self.comment_textbox_widget.get("1.0", "end-1c").strip()
        
        if rating == 0:
            self.status_label.configure(text="Please select a rating (1-5 stars).", text_color=ERROR_COLOR)
            self.after(3000, lambda: self.status_label.configure(text=""))
            return
            
        if not self.user:
            messagebox.showwarning("Login Required", "You must be logged in to submit a review.")
            log("Warning: Attempted to submit review without logged in user.")
            return
            
        if not self.restaurant:
            log("Error: Restaurant context lost for review submission.")
            self.status_label.configure(text="Error: Restaurant context lost. Cannot submit.", text_color=ERROR_COLOR)
            self.after(3000, lambda: self.status_label.configure(text=""))
            return

        try:
            log(f"Submitting review: User {self.user.user_id}, Username {self.user.username}, Rest {self.restaurant.restaurant_id}, Rating {rating}, Comment: '{comment[:50]}...'")
            success = add_review(
                user_id=self.user.user_id,
                username=self.user.username,
                restaurant_id=self.restaurant.restaurant_id,
                rating=rating,
                comment=comment
            )
            if success:
                self.status_label.configure(text="Review submitted successfully!", text_color=SUCCESS_COLOR)
                self.is_review_form_visible = False
                self.rating_var.set(0)
                if self.comment_textbox_widget and self.comment_textbox_widget.winfo_exists():
                     self.comment_textbox_widget.delete("1.0", "end")
                self.refresh_reviews()
            else:
                self.status_label.configure(text="Failed to submit review. Please try again.", text_color=ERROR_COLOR)
        except Exception as e:
            log(f"Error: Exception submitting review: {e}")
            self.status_label.configure(text="An error occurred while submitting your review.", text_color=ERROR_COLOR)
        
        self.after(4000, lambda: self.status_label.configure(text=""))

    def _populate_reviews_to_scroll_frame(self, parent_frame, start_row):
        current_row = start_row
        log(f"_populate_reviews_to_scroll_frame for restaurant: {self.restaurant.name if self.restaurant else 'None'}")

        if not self.restaurant:
            no_restaurant_label = ctk.CTkLabel(parent_frame,
                                               text="No restaurant selected to display reviews.",
                                               text_color=TEXT_COLOR, font=ctk.CTkFont(size=16))
            no_restaurant_label.grid(row=current_row, column=0, pady=20, sticky="ew")
            return current_row + 1

        reviews = get_reviews_for_restaurant(self.restaurant.restaurant_id)
        log(f"Found {len(reviews)} reviews for restaurant ID {self.restaurant.restaurant_id}")

        if not reviews:
            no_reviews_label = ctk.CTkLabel(parent_frame,
                                            text="Be the first to review this restaurant!",
                                            text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
            no_reviews_label.grid(row=current_row, column=0, pady=20, sticky="ew")
            return current_row + 1

        for review_data in reviews:
            review_card = ctk.CTkFrame(parent_frame, fg_color=FRAME_FG_COLOR,
                                     border_color=FRAME_BORDER_COLOR, border_width=1, corner_radius=8)
            review_card.grid(row=current_row, column=0, pady=(0, 10), padx=5, sticky="ew")
            review_card.grid_columnconfigure(0, weight=1)

            reviewer = User.get_by_id(review_data.user_id)
            username = reviewer.username if reviewer else "Anonymous"
            
            reviewer_rating_frame = ctk.CTkFrame(review_card, fg_color="transparent")
            reviewer_rating_frame.grid(row=0, column=0, padx=10, pady=(5,2), sticky="ew")
            reviewer_rating_frame.grid_columnconfigure(0, weight=1)
            reviewer_rating_frame.grid_columnconfigure(1, weight=0)

            username_label = ctk.CTkLabel(reviewer_rating_frame, text=username,
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          text_color=TEXT_COLOR)
            username_label.grid(row=0, column=0, sticky="w")

            rating_text = f"{'★' * review_data.rating}{'☆' * (5 - review_data.rating)}"
            rating_label = ctk.CTkLabel(reviewer_rating_frame, text=rating_text,
                                        font=ctk.CTkFont(size=14), text_color=PRIMARY_COLOR)
            rating_label.grid(row=0, column=1, sticky="e")
            
            if review_data.comment:
                comment_label = ctk.CTkLabel(review_card, text=review_data.comment,
                                             font=ctk.CTkFont(size=12), text_color=TEXT_COLOR,
                                             wraplength=self.winfo_width() - 60,
                                             justify="left", anchor="w")
                comment_label.grid(row=1, column=0, padx=10, pady=(0,5), sticky="ew")

            date_label = ctk.CTkLabel(review_card, text=review_data.review_date.strftime("%Y-%m-%d"),
                                      font=ctk.CTkFont(size=10), text_color=SECONDARY_COLOR)
            date_label.grid(row=2, column=0, padx=10, pady=(0,5), sticky="e")
            current_row += 1
        return current_row

    def _add_to_cart(self, menu_item: MenuItem):
        if self.app_ref.cart:
            added = self.app_ref.cart.add_item(menu_item, 1)
            if added:
                self.status_label.configure(text=f"'{menu_item.name}' added to cart!", text_color=SUCCESS_COLOR)
            else:
                self.status_label.configure(text=f"Failed to add '{menu_item.name}'.", text_color=ERROR_COLOR)
        else:
            self.status_label.configure(text="Error: Cart not available.", text_color=ERROR_COLOR)
        self.after(3000, lambda: self.status_label.configure(text=""))

    def go_back_to_main_app(self):        self.app_ref.show_main_app_screen(self.user)

    def _on_write_review_button_click(self):
        log(f"_on_write_review_button_click called. Current form visibility: {self.is_review_form_visible}")
        if not self.user:
            messagebox.showwarning("Login Required", "Please log in to write a review.")
            log("User not logged in. Cannot write review.")
            return
        
        self.is_review_form_visible = not self.is_review_form_visible
        log(f"Toggled form visibility to: {self.is_review_form_visible}")

        if not self.is_review_form_visible:
            self.rating_var.set(0)
            if self.comment_textbox_widget and self.comment_textbox_widget.winfo_exists():
                 self.comment_textbox_widget.delete("1.0", "end")
            log("Review form hidden, rating reset.")

        self.refresh_reviews()

    def refresh_reviews(self):
        log("MenuScreen.refresh_reviews called, will repopulate main scroll content.")
        self._populate_main_scroll_content()
