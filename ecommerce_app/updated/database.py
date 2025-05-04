import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

# Database connection helper functions

def get_db_connection():
    """
    Create and return a new MySQL database connection using DB_CONFIG.
    Returns:
        connection (mysql.connector.connection.MySQLConnection): The database connection object, or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def close_db_connection(connection):
    """
    Close the given MySQL database connection if it is open.
    Args:
        connection (mysql.connector.connection.MySQLConnection): The connection to close.
    """
    if connection and connection.is_connected():
        connection.close()
        print("Database connection closed") 