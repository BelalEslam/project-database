import tkinter as tk
from tkinter import ttk, messagebox
from services.database import get_db_connection, close_db_connection
from mysql.connector import Error

# Colors
PRIMARY_COLOR = "#007BFF"  # Electric Blue
BACKGROUND_COLOR = "#F4F1EB"  # Light Beige
TEXT_COLOR = "#313715"  # Dark Olive Brown
CARD_BACKGROUND = "#FFFFFF"  # White
CARD_BORDER = "#E0E0E0"  # Light Gray
ACCENT_COLOR = "#28A745"  # Green for stock status

class CartScreen(tk.Frame):
    def __init__(self, master, switch_to_products):
        super().__init__(master)
        self.switch_to_products = switch_to_products
        self.configure(bg=BACKGROUND_COLOR)
        
        # Configure the main frame to expand
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main container with padding
        main_container = tk.Frame(self, bg=BACKGROUND_COLOR, padx=20, pady=20)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Header section
        header_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # CartX Logo and Back button
        left_header = tk.Frame(header_frame, bg=BACKGROUND_COLOR)
        left_header.grid(row=0, column=0, sticky="w")
        
        back_button = tk.Button(left_header, text="← Back to Products", 
                              font=("Helvetica", 12),
                              bg=PRIMARY_COLOR, fg="white",
                              activebackground="#0056b3", activeforeground="white",
                              command=self.switch_to_products)
        back_button.pack(side="left", padx=(0, 20))

        # Cart title
        title_frame = tk.Frame(header_frame, bg=BACKGROUND_COLOR)
        title_frame.grid(row=0, column=1, sticky="e")
        
        title = tk.Label(title_frame, text="Your Cart", font=("Helvetica", 28, "bold"),
                        bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR)
        title.pack(side="right")

        # Content area with scrollbar
        content_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(content_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BACKGROUND_COLOR)

        # Configure scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Footer section with total and checkout button
        footer_frame = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        footer_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        footer_frame.grid_columnconfigure(1, weight=1)

        # Total amount
        self.total_label = tk.Label(footer_frame, text="Total: $0.00", 
                                  font=("Helvetica", 16, "bold"),
                                  bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.total_label.grid(row=0, column=0, sticky="w")

        # Checkout button
        checkout_button = tk.Button(footer_frame, text="Proceed to Checkout",
                                  font=("Helvetica", 14, "bold"),
                                  bg=ACCENT_COLOR, fg="white",
                                  activebackground="#1e7e34", activeforeground="white",
                                  command=self.proceed_to_checkout)
        checkout_button.grid(row=0, column=1, sticky="e", padx=(20, 0))

        # Initialize cart items
        self.cart_items = []
        self.update_cart_display()

    def add_to_cart(self, product):
        """Add a product to the cart"""
        # Check if product is already in cart
        for item in self.cart_items:
            if item["product_id"] == product["product_id"]:
                item["quantity"] += 1
                self.update_cart_display()
                return

        # Add new item to cart
        self.cart_items.append({
            "product_id": product["product_id"],
            "name": product["product_name"],
            "price": product["product_price"],
            "quantity": 1
        })
        self.update_cart_display()

    def remove_from_cart(self, product_id):
        """Remove a product from the cart"""
        self.cart_items = [item for item in self.cart_items if item["product_id"] != product_id]
        self.update_cart_display()

    def update_quantity(self, product_id, new_quantity):
        """Update the quantity of a product in the cart"""
        for item in self.cart_items:
            if item["product_id"] == product_id:
                if new_quantity <= 0:
                    self.remove_from_cart(product_id)
                else:
                    item["quantity"] = new_quantity
                break
        self.update_cart_display()

    def update_cart_display(self):
        """Update the cart display with current items"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.cart_items:
            # Show empty cart message
            empty_label = tk.Label(self.scrollable_frame, 
                                 text="Your cart is empty",
                                 font=("Helvetica", 16),
                                 bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
            empty_label.pack(pady=50)
            self.total_label.config(text="Total: $0.00")
            return

        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in self.cart_items)
        self.total_label.config(text=f"Total: ${total:.2f}")

        # Display cart items
        for item in self.cart_items:
            item_frame = tk.Frame(self.scrollable_frame, bg=CARD_BACKGROUND, bd=1, relief="solid")
            item_frame.pack(fill="x", padx=10, pady=5)

            # Product name and price
            info_frame = tk.Frame(item_frame, bg=CARD_BACKGROUND)
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

            name_label = tk.Label(info_frame, text=item["name"],
                              font=("Helvetica", 12, "bold"),
                              bg=CARD_BACKGROUND, fg=TEXT_COLOR)
            name_label.pack(anchor="w")

            price_label = tk.Label(info_frame, text=f"${item['price']:.2f}",
                               font=("Helvetica", 12),
                               bg=CARD_BACKGROUND, fg=PRIMARY_COLOR)
            price_label.pack(anchor="w")

            # Quantity controls
            quantity_frame = tk.Frame(item_frame, bg=CARD_BACKGROUND)
            quantity_frame.pack(side="right", padx=10, pady=10)

            quantity_var = tk.StringVar(value=str(item["quantity"]))
            quantity_var.trace("w", lambda name, index, mode, p_id=item["product_id"], var=quantity_var: 
                            self.update_quantity(p_id, int(var.get() or 0)))

            quantity_entry = tk.Entry(quantity_frame, textvariable=quantity_var,
                                    width=3, font=("Helvetica", 12),
                                    justify="center")
            quantity_entry.pack(side="left", padx=5)

            # Remove button
            remove_button = tk.Button(item_frame, text="×",
                                    font=("Helvetica", 14, "bold"),
                                    bg="red", fg="white",
                                    activebackground="#dc3545", activeforeground="white",
                                    command=lambda p_id=item["product_id"]: self.remove_from_cart(p_id))
            remove_button.pack(side="right", padx=10)

    def proceed_to_checkout(self):
        """Handle the checkout process"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Your cart is empty. Add some products first!")
            return

        # TODO: Implement payment processing
        messagebox.showinfo("Checkout", "Payment processing will be implemented here!")
