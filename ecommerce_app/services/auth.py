from .database import get_db_connection, close_db_connection
from mysql.connector import Error

class Auth:
    def __init__(self):
        self.current_user_id = None
        self.current_username = None

    def login(self, username, password):
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Query to check user credentials using the new users table
            cursor.execute("""
                SELECT id, username, password
                FROM users 
                WHERE username = %s AND password = %s
            """, (username, password))
            
            user = cursor.fetchone()
            
            if user:
                # Store the logged-in user's information
                self.current_user_id = user['id']
                self.current_username = user['username']
                return True, f"Welcome back, {user['username']}!"
            else:
                return False, "Invalid username or password"
                
        except Error as e:
            print(f"Error during login: {e}")
            return False, "An error occurred during login"
        finally:
            if connection and connection.is_connected():
                close_db_connection(connection) 