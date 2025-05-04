import tkinter as tk
from tkinter import messagebox
from services.database import get_db_connection, close_db_connection
from mysql.connector import Error

# Colors
PRIMARY_COLOR = "#007BFF"  # Electric Blue
BACKGROUND_COLOR = "#F4F1EB"  # Light Beige
TEXT_COLOR = "#313715"  # Dark Olive Brown

class SignupScreen(tk.Frame):
    def __init__(self, master, switch_to_login):
        super().__init__(master)
        self.switch_to_login = switch_to_login
        self.configure(bg=BACKGROUND_COLOR)
        self.grid(row=0, column=0, sticky="nsew")

        # Load the background image
        self.bg_image = tk.PhotoImage(file="ecommerce_app/assets/background5.png")
        
        # Create a Canvas to display the background
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Set the background image on the Canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        
        # Keep a reference to the image to prevent it from being garbage collected
        self.canvas.bg_image = self.bg_image

        # Create a frame for content
        center_frame = tk.Frame(self.canvas, bg=BACKGROUND_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header = tk.Label(
            center_frame, text="CartX", font=("Helvetica", 28, "bold"),
            bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR
        )
        header.pack(pady=(40, 10))

        subheader = tk.Label(
            center_frame, text="Create your account", font=("Helvetica", 12),
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        subheader.pack(pady=(0, 30))

        # Username
        username_label = tk.Label(center_frame, text="Username", font=("Helvetica", 10),
                                bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        username_label.pack(fill="x", padx=40)
        self.username_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.username_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Email
        email_label = tk.Label(center_frame, text="Email", font=("Helvetica", 10),
                             bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        email_label.pack(fill="x", padx=40)
        self.email_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.email_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Password
        password_label = tk.Label(center_frame, text="Password", font=("Helvetica", 10),
                                bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        password_label.pack(fill="x", padx=40)
        self.password_entry = tk.Entry(center_frame, show="*", font=("Helvetica", 12), bd=2, relief="groove")
        self.password_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Phone
        phone_label = tk.Label(center_frame, text="Phone Number", font=("Helvetica", 10),
                             bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        phone_label.pack(fill="x", padx=40)
        self.phone_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.phone_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Address
        address_label = tk.Label(center_frame, text="Address", font=("Helvetica", 10),
                               bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        address_label.pack(fill="x", padx=40)
        
        # City
        city_label = tk.Label(center_frame, text="City", font=("Helvetica", 10),
                            bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        city_label.pack(fill="x", padx=40)
        self.city_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.city_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Street
        street_label = tk.Label(center_frame, text="Street", font=("Helvetica", 10),
                              bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        street_label.pack(fill="x", padx=40)
        self.street_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.street_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Building Number
        building_label = tk.Label(center_frame, text="Building Number", font=("Helvetica", 10),
                                bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        building_label.pack(fill="x", padx=40)
        self.building_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.building_entry.pack(padx=40, pady=(0, 10), ipady=6, fill="x")

        # Sign Up button
        signup_button = tk.Button(
            center_frame, text="Sign Up", font=("Helvetica", 12, "bold"),
            bg=PRIMARY_COLOR, fg=BACKGROUND_COLOR,
            activebackground="#0056b3", activeforeground=BACKGROUND_COLOR,
            command=self.signup_action
        )
        signup_button.pack(padx=40, pady=(20, 10), ipadx=10, ipady=6, fill="x")

        # Footer
        footer = tk.Label(
            center_frame, text="Already have an account? Login", font=("Helvetica", 10),
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR, cursor="hand2"
        )
        footer.pack(side="bottom", pady=20)
        footer.bind("<Button-1>", lambda e: self.switch_to_login())

    def signup_action(self):
        # Get all form values
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        phone = self.phone_entry.get()
        city = self.city_entry.get()
        street = self.street_entry.get()
        building = self.building_entry.get()

        print(f"Attempting to sign up user: {username} with email: {email}")

        # Validate required fields
        if not all([username, email, password, phone, city, street, building]):
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        try:
            # Validate phone number
            phone = int(phone)
            building = int(building)
        except ValueError:
            messagebox.showwarning("Invalid Input", "Phone number and building number must be numeric.")
            return

        connection = None
        try:
            connection = get_db_connection()
            if not connection:
                raise Error("Failed to connect to database")
                
            cursor = connection.cursor()

            # Check if username or email already exists
            print("Checking for existing username/email...")
            cursor.execute("""
                SELECT id FROM users 
                WHERE username = %s OR email = %s
            """, (username, email))
            
            if cursor.fetchone():
                messagebox.showerror("Sign Up Failed", "Username or email already exists.")
                return

            # Combine address components
            full_address = f"{building} {street}, {city}"

            # Insert new user
            print("Inserting new user...")
            cursor.execute("""
                INSERT INTO users (username, password, email, name, phone_number, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, password, email, username, phone, full_address))
            
            connection.commit()
            print("User created successfully!")
            messagebox.showinfo("Success", "Account created successfully!")
            self.switch_to_login()

        except Error as e:
            print(f"Database Error during signup: {str(e)}")
            print(f"Error code: {e.errno}")
            print(f"SQL state: {e.sqlstate}")
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except Exception as e:
            print(f"Unexpected Error during signup: {str(e)}")
            print(f"Error type: {type(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            if connection and connection.is_connected():
                close_db_connection(connection) 