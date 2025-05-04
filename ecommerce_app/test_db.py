from services.database import get_db_connection, close_db_connection
from mysql.connector import Error

def test_database():
    connection = None
    try:
        # Test connection
        connection = get_db_connection()
        if not connection:
            print("Error: Could not connect to database")
            return False

        cursor = connection.cursor()

        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            print("Error: 'users' table does not exist")
            return False

        # Show actual table structure
        print("\nActual table structure:")
        cursor.execute("DESCRIBE users")
        for column in cursor.fetchall():
            print(f"Column: {column[0]}, Type: {column[1]}")

        return True

    except Error as e:
        print(f"Database Error: {str(e)}")
        return False
    finally:
        if connection and connection.is_connected():
            close_db_connection(connection)

if __name__ == "__main__":
    test_database() 