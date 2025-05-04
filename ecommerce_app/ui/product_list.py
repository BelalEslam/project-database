# ui/product_list.py

import tkinter as tk
from tkinter import ttk, messagebox
from services.database import get_db_connection, close_db_connection
from mysql.connector import Error
import os
from ui.cart_screen import CartScreen

# Modern Color Scheme
PRIMARY_COLOR = "#2563EB"      # Vibrant Blue
SECONDARY_COLOR = "#4F46E5"    # Indigo
ACCENT_COLOR = "#DC2626"       # Red for important actions
BACKGROUND_COLOR = "#F8FAFC"   # Light Gray
CARD_BACKGROUND = "#FFFFFF"    # White
TEXT_COLOR = "#1E293B"         # Dark Slate
SUCCESS_COLOR = "#059669"      # Green for success
WARNING_COLOR = "#D97706"      # Amber for warnings
BORDER_COLOR = "#E2E8F0"       # Light Gray for borders
DISABLED_COLOR = "#94A3B8"     # Gray for disabled elements

# Fonts
TITLE_FONT = ("Inter", 24, "bold")
HEADER_FONT = ("Inter", 16, "bold")
BODY_FONT = ("Inter", 12)
SMALL_FONT = ("Inter", 10)

def get_product_by_id(product_id):
    """
    Get a single product by its ID.
    Args:
        product_id (int): The ID of the product to retrieve.
    Returns:
        dict: Product details with category name, or None if not found.
    """
    connection = get_db_connection()
    product = None
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT p.id, p.name, p.description, p.price, p.stock, p.image_path, c.name AS category
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = %s
            ''', (product_id,))
            product = cursor.fetchone()
        except Error as e:
            print(f"Error getting product by ID: {str(e)}")
        finally:
            close_db_connection(connection)
    return product

def get_all_products():
    """
    Get all products with their category names.
    Returns:
        list of dict: All products with category names.
    """
    connection = get_db_connection()
    products = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT p.id, p.name, p.description, p.price, p.stock, p.image_path, c.name AS category
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name
            ''')
            products = cursor.fetchall()
        except Error as e:
            print(f"Error getting all products: {str(e)}")
        finally:
            close_db_connection(connection)
    return products

def search_products_by_name(name):
    """
    Search for products by (partial) name match.
    Args:
        name (str): The search string (case-insensitive, partial match).
    Returns:
        list of dict: Matching products with category names.
    """
    connection = get_db_connection()
    products = []
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT p.id, p.name, p.description, p.price, p.stock, p.image_path, c.name AS category
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.name LIKE %s
            ''', (f"%{name}%",))
            products = cursor.fetchall()
        except Error as e:
            print(f"Error searching products by name: {str(e)}")
        finally:
            close_db_connection(connection)
    return products

class ProductListScreen(tk.Frame):
    def __init__(self, master, auth):
        super().__init__(master)
        self.connection = None
        self.auth = auth
        self.connect()
        self.configure(bg=BACKGROUND_COLOR)
        
        # Initialize cart screen
        self.cart_screen = CartScreen(master, self.show_products)
        self.cart_screen.grid(row=0, column=0, sticky="nsew")
        self.cart_screen.grid_remove()  # Hide cart screen initially
        
        # Dictionary to store quantity variables for each product
        self.quantity_vars = {}
        
        # Get current user's name
        self.current_user = self.get_current_user()
        
        # Configure the main frame to expand
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main container with padding
        main_container = tk.Frame(self, bg=BACKGROUND_COLOR, padx=30, pady=30)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Header section with improved design
        header_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.grid_columnconfigure(1, weight=1)

        # Left header with logo and user info
        left_header = tk.Frame(header_frame, bg=BACKGROUND_COLOR)
        left_header.grid(row=0, column=0, sticky="w")
        
        # Logo with improved styling
        logo_frame = tk.Frame(left_header, bg=PRIMARY_COLOR, padx=15, pady=10)
        logo_frame.pack(side="left", padx=(0, 20))
        
        logo = tk.Label(logo_frame, text="CartX", font=TITLE_FONT,
                       bg=PRIMARY_COLOR, fg="white")
        logo.pack()

        # User info section
        user_frame = tk.Frame(left_header, bg=BACKGROUND_COLOR)
        user_frame.pack(side="left", padx=20)
        
        user_icon = tk.Label(user_frame, text="👤", font=HEADER_FONT,
                           bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR)
        user_icon.pack(side="left", padx=(0, 5))
        
        # Display actual username
        self.user_name_label = tk.Label(user_frame, 
                                      text=f"Welcome, {self.current_user}",
                                      font=BODY_FONT,
                                      bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.user_name_label.pack(side="left")

        # Right header with search and cart
        right_header = tk.Frame(header_frame, bg=BACKGROUND_COLOR)
        right_header.grid(row=0, column=1, sticky="e")
        
        # Search bar with improved design
        search_frame = tk.Frame(right_header, bg=BACKGROUND_COLOR)
        search_frame.pack(side="left", padx=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_products())
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                              font=BODY_FONT, bg=CARD_BACKGROUND,
                              fg=TEXT_COLOR, relief="solid",
                              borderwidth=1, width=30)
        search_entry.pack(side="left", padx=(0, 5))
        
        search_button = tk.Button(search_frame, text="🔍",
                                font=BODY_FONT, bg=PRIMARY_COLOR,
                                fg="white", relief="flat",
                                command=self.filter_products)
        search_button.pack(side="left")

        # Cart button with improved design
        cart_button = tk.Button(right_header, text="🛒",
                              font=HEADER_FONT, bg=SECONDARY_COLOR,
                              fg="white", relief="flat",
                              command=self.show_cart)
        cart_button.pack(side="left", padx=10)

        # Category filter section
        category_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        category_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Category buttons
        self.category_buttons = {}
        categories = ["All", "Clothing", "Electronics", "Footwear", "Accessories"]
        for category in categories:
            btn = tk.Button(category_frame, text=category,
                          font=SMALL_FONT, bg=CARD_BACKGROUND,
                          fg=TEXT_COLOR, relief="flat",
                          command=lambda c=category: self.select_category(c))
            btn.pack(side="left", padx=5)
            self.category_buttons[category] = btn

        # Products grid
        self.products_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        self.products_frame.grid(row=2, column=0, sticky="nsew")
        self.products_frame.grid_columnconfigure(0, weight=1)
        self.products_frame.grid_rowconfigure(0, weight=1)

        # Create scrollable canvas for products
        self.canvas = tk.Canvas(self.products_frame, bg=BACKGROUND_COLOR,
                              highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.products_frame, orient="vertical",
                                command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas for products
        self.products_container = tk.Frame(self.canvas, bg=BACKGROUND_COLOR)
        self.canvas.create_window((0, 0), window=self.products_container,
                                anchor="nw", width=self.canvas.winfo_width())
        
        # Bind canvas resize
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.bind("<Configure>", self.on_resize)

        # Load products
        self.update_product_grid()

    def select_category(self, category):
        """Handle category selection"""
        for btn in self.category_buttons.values():
            btn['relief'] = 'flat'
        self.category_buttons[category]['relief'] = 'sunken'
        self.filter_products()

    def filter_products(self):
        """Filter products based on search text and selected category"""
        search_text = self.search_var.get().lower()
        selected_category = None
        
        # Find selected category
        for category, btn in self.category_buttons.items():
            if btn['relief'] == 'sunken':
                selected_category = category
                break
        
        # Get products from database
        if search_text:
            products = search_products_by_name(search_text)
        else:
            products = self.get_products_from_db()
        
        # Filter by category if one is selected
        if selected_category and selected_category != "All":
            products = [p for p in products if p['category'] == selected_category]
        
        # Update the product grid
        self.update_product_grid(products)

    def on_canvas_resize(self, event):
        self.canvas.itemconfig("all", width=event.width)
        self.update_product_grid()

    def on_resize(self, event):
        self.canvas.configure(width=event.width)
        self.update_product_grid()

    def update_product_grid(self, products=None):
        """Update the product grid with the given products"""
        if products is None:
            products = self.get_products_from_db()
            
        # Clear existing products
        for widget in self.products_container.winfo_children():
            widget.destroy()
        
        # Recreate the grid with current window size
        self.create_product_grid(self.products_container, products)

    def connect(self):
        """Establish a new database connection"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = get_db_connection()
                if not self.connection:
                    raise Exception("Failed to connect to database")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def __del__(self):
        if self.connection and self.connection.is_connected():
            close_db_connection(self.connection)

    def get_products_from_db(self):
        """Get all products from the database"""
        return get_all_products()

    def load_product_image(self, product_name, image_url=None):
        """Load product image or placeholder if not available"""
        try:
            # If image_url is provided, try to load it
            if image_url:
                image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", image_url)
                if os.path.exists(image_path):
                    try:
                        image = tk.PhotoImage(file=image_path)
                        # Resize the image to fit the card
                        width = image.width()
                        height = image.height()
                        max_size = 200  # Maximum dimension for the image
                        
                        if width > height:
                            subsample = max(1, width // max_size)
                        else:
                            subsample = max(1, height // max_size)
                            
                        image = image.subsample(subsample, subsample)
                        return image
                    except tk.TclError as e:
                        print(f"Error loading image for {product_name}: {e}")
            
            # If no image_url or image not found, use placeholder
            placeholder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Logo.png")
            if os.path.exists(placeholder_path):
                try:
                    image = tk.PhotoImage(file=placeholder_path)
                    image = image.subsample(4, 4)  # Make placeholder smaller
                    return image
                except tk.TclError as e:
                    print(f"Error loading placeholder image: {e}")
                    
            return None
        except Exception as e:
            print(f"Error in load_product_image: {e}")
            return None

    def create_product_grid(self, parent, products):
        # Create a frame for the grid
        grid_frame = tk.Frame(parent, bg=BACKGROUND_COLOR)
        grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Calculate number of columns based on window width
        window_width = self.winfo_width()
        num_columns = max(3, window_width // 300)  # Minimum 3 columns
        
        # Calculate card dimensions
        card_width = (window_width - 100) // num_columns
        card_height = int(card_width * 1.4)

        for i, product in enumerate(products):
            row = i // num_columns
            col = i % num_columns
            
            # Create product card with improved styling
            card_frame = tk.Frame(grid_frame, bg=CARD_BACKGROUND, bd=1, relief="solid",
                                width=card_width, height=card_height)
            card_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            card_frame.grid_propagate(False)
            
            # Configure grid weights
            grid_frame.grid_columnconfigure(col, weight=1)
            grid_frame.grid_rowconfigure(row, weight=1)
            
            # Product image
            image = self.load_product_image(product["name"], product.get("image_path"))
            if image:
                image_label = tk.Label(card_frame, image=image, bg=CARD_BACKGROUND)
                image_label.image = image  # Keep a reference
                image_label.pack(pady=(10, 0))
            
            # Product details
            details_frame = tk.Frame(card_frame, bg=CARD_BACKGROUND)
            details_frame.pack(fill="both", expand=True, padx=20, pady=15)
            
            # Calculate font sizes based on card width
            title_font_size = max(10, min(16, card_width // 20))
            price_font_size = max(12, min(20, card_width // 18))
            info_font_size = max(8, min(14, card_width // 25))
            
            # Product name
            name = tk.Label(details_frame, text=product["name"],
                          font=("Inter", title_font_size, "bold"),
                          bg=CARD_BACKGROUND, fg=TEXT_COLOR,
                          wraplength=card_width-40, justify="left")
            name.pack(anchor="w", pady=(0, 10))
            
            # Price
            price = tk.Label(details_frame, text=f"${product['price']:.2f}",
                           font=("Inter", price_font_size, "bold"),
                           bg=CARD_BACKGROUND, fg=PRIMARY_COLOR)
            price.pack(anchor="w", pady=(0, 10))
            
            # Category
            category_frame = tk.Frame(details_frame, bg=CARD_BACKGROUND)
            category_frame.pack(anchor="w", pady=(0, 10))
            
            category = tk.Label(category_frame, text=product["category"],
                              font=("Inter", info_font_size),
                              bg=CARD_BACKGROUND, fg=TEXT_COLOR)
            category.pack(side="left")
            
            # Stock status with color coding
            stock_frame = tk.Frame(details_frame, bg=CARD_BACKGROUND)
            stock_frame.pack(anchor="w", pady=(0, 10))
            
            stock_color = SUCCESS_COLOR if product["stock"] > 10 else WARNING_COLOR
            stock = tk.Label(stock_frame, text=f"Stock: {product['stock']}",
                           font=("Inter", info_font_size),
                           bg=CARD_BACKGROUND, fg=stock_color)
            stock.pack(side="left")
            
            # Add to Cart button with quantity selector
            add_cart_frame = tk.Frame(card_frame, bg=CARD_BACKGROUND)
            add_cart_frame.pack(fill="x", padx=20, pady=10, side="bottom")

            # Quantity controls
            quantity_frame = tk.Frame(add_cart_frame, bg=CARD_BACKGROUND)
            quantity_frame.pack(side="left", padx=(0, 10))

            # Store quantity variable in dictionary
            self.quantity_vars[product["id"]] = tk.StringVar(value="1")

            # Decrease quantity button
            decrease_btn = tk.Button(quantity_frame, text="-", 
                                   font=("Inter", 12, "bold"),
                                   bg=PRIMARY_COLOR, fg="white",
                                   activebackground=SECONDARY_COLOR, activeforeground="white",
                                   command=lambda p=product: self.update_quantity(p["id"], -1))
            decrease_btn.pack(side="left")

            # Quantity display
            quantity_label = tk.Label(quantity_frame, 
                                    textvariable=self.quantity_vars[product["id"]],
                                    font=("Inter", 12),
                                    bg=CARD_BACKGROUND, fg=TEXT_COLOR,
                                    width=3)
            quantity_label.pack(side="left", padx=5)

            # Increase quantity button
            increase_btn = tk.Button(quantity_frame, text="+", 
                                   font=("Inter", 12, "bold"),
                                   bg=PRIMARY_COLOR, fg="white",
                                   activebackground=SECONDARY_COLOR, activeforeground="white",
                                   command=lambda p=product: self.update_quantity(p["id"], 1))
            increase_btn.pack(side="left")

            # Add to Cart button
            add_btn = tk.Button(add_cart_frame, text="Add to Cart",
                              font=("Inter", info_font_size, "bold"),
                              bg=PRIMARY_COLOR, fg="white",
                              activebackground=SECONDARY_COLOR, activeforeground="white",
                              command=lambda p=product: self.add_to_cart(p, int(self.quantity_vars[p["id"]].get())))
            add_btn.pack(side="right", fill="x", expand=True)

    def update_quantity(self, product_id, change):
        """Update the quantity for a product"""
        if product_id in self.quantity_vars:
            current_quantity = int(self.quantity_vars[product_id].get())
            new_quantity = max(1, current_quantity + change)  # Ensure quantity is at least 1
            self.quantity_vars[product_id].set(str(new_quantity))

    def add_to_cart(self, product, quantity=1):
        """Add product to cart with specified quantity and show success message"""
        try:
            if product["stock"] <= 0:
                messagebox.showwarning("Out of Stock", "This product is currently out of stock.")
                return
                
            if quantity > product["stock"]:
                messagebox.showwarning("Insufficient Stock", 
                                     f"Only {product['stock']} items available in stock.")
                return
                
            # Add the product to cart with the specified quantity
            for _ in range(quantity):
                self.cart_screen.add_to_cart(product)
                
            # Update cart badge
            current_count = int(self.cart_badge["text"])
            self.cart_badge.config(text=str(current_count + quantity))
                
            messagebox.showinfo("Added to Cart", f"{quantity} {product['name']}(s) added to cart!")
            # Reset quantity to 1 after adding to cart
            self.quantity_vars[product["id"]].set("1")
        except Exception as e:
            print(f"Error adding product to cart: {e}")
            messagebox.showerror("Error", "Failed to add product to cart. Please try again.")

    def show_cart(self):
        """Show the cart screen"""
        self.grid_remove()
        self.cart_screen.grid()

    def show_products(self):
        """Show the products screen"""
        self.cart_screen.grid_remove()
        self.grid()
        # Refresh the user name in case it changed
        try:
            self.current_user = self.get_current_user()
            self.user_name_label.config(text=f"Welcome, {self.current_user}")
        except Exception as e:
            print(f"Error updating user name: {e}")

    def get_current_user(self):
        """Get the current user's name from the Auth instance"""
        if self.auth and self.auth.current_username:
            return self.auth.current_username
        return "User"
