# main.py

import tkinter as tk
from ui.login_screen import LoginScreen
from ui.signup_screen import SignupScreen
from ui.product_list import ProductListScreen
from services.auth import Auth

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("CartX")
        self.resizable(True, True)

        # Create a single Auth instance
        self.auth = Auth()

        # Configure full window grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize screens
        self.login_screen = LoginScreen(self, self.show_product_list, self.show_signup, self.auth)
        self.signup_screen = SignupScreen(self, self.show_login)
        self.product_list_screen = None

        # Show login screen initially
        self.show_login()

    def show_login(self):
        if self.product_list_screen:
            self.product_list_screen.grid_forget()
        if self.signup_screen:
            self.signup_screen.grid_forget()
        self.login_screen.grid(row=0, column=0, sticky="nsew")

    def show_signup(self):
        if self.product_list_screen:
            self.product_list_screen.grid_forget()
        if self.login_screen:
            self.login_screen.grid_forget()
        self.signup_screen.grid(row=0, column=0, sticky="nsew")

    def show_product_list(self):
        self.login_screen.grid_forget()
        if self.signup_screen:
            self.signup_screen.grid_forget()
        if not self.product_list_screen:
            self.product_list_screen = ProductListScreen(self, self.auth)
        self.product_list_screen.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
