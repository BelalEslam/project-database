import tkinter as tk
from tkinter import messagebox
from services.auth import Auth

# Colors
PRIMARY_COLOR = "#007BFF"  # Electric Blue
BACKGROUND_COLOR = "#F4F1EB"  # White (will not be used for background)
TEXT_COLOR = "#313715"  # Dark Olive Brown

class LoginScreen(tk.Frame):
    def __init__(self, master, switch_to_products, switch_to_signup, auth):
        super().__init__(master)
        self.switch_to_products = switch_to_products
        self.switch_to_signup = switch_to_signup
        self.auth = auth
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
            center_frame, text="Welcome back! Login to continue", font=("Helvetica", 12),
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR
        )
        subheader.pack(pady=(0, 30))

        # Username label and entry
        username_label = tk.Label(center_frame, text="Username or Email", font=("Helvetica", 10),
                                bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        username_label.pack(fill="x", padx=40)
        self.username_entry = tk.Entry(center_frame, font=("Helvetica", 12), bd=2, relief="groove")
        self.username_entry.pack(padx=40, pady=(0, 20), ipady=6, fill="x")

        # Password label and entry
        password_label = tk.Label(center_frame, text="Password", font=("Helvetica", 10),
                                bg=BACKGROUND_COLOR, fg=TEXT_COLOR, anchor="w")
        password_label.pack(fill="x", padx=40)
        self.password_entry = tk.Entry(center_frame, show="*", font=("Helvetica", 12), bd=2, relief="groove")
        self.password_entry.pack(padx=40, pady=(0, 20), ipady=6, fill="x")

        # Login button
        login_button = tk.Button(
            center_frame, text="Login", font=("Helvetica", 12, "bold"),
            bg=PRIMARY_COLOR, fg=BACKGROUND_COLOR,
            activebackground="#0056b3", activeforeground=BACKGROUND_COLOR,
            command=self.login_action
        )
        login_button.pack(padx=40, pady=(10, 20), ipadx=10, ipady=6, fill="x")

        # Forgot Password
        forgot_label = tk.Label(
            center_frame, text="Forgot Password?", font=("Helvetica", 10, "underline"),
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR, cursor="hand2"
        )
        forgot_label.pack()

        # Footer
        footer = tk.Label(
            center_frame, text="Don't have an account? Sign up", font=("Helvetica", 10),
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR, cursor="hand2"
        )
        footer.pack(side="bottom", pady=20)
        footer.bind("<Button-1>", lambda e: self.switch_to_signup())

    def login_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == "" or password == "":
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        success, message = self.auth.login(username, password)
        
        if success:
            messagebox.showinfo("Login Success", message)
            self.switch_to_products()
        else:
            messagebox.showerror("Login Failed", message)
