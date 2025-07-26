import sqlite3

DATABASE_NAME = "books.db"


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn


def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            publication_year INTEGER
        )
    """
    )
    conn.commit()
    conn.close()
    print("Database initialized or already exists.")


if __name__ == "__main__":
    # This block of code runs only when database.py is executed directly
    init_db()
    # You can add some initial data here for testing
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO books (title, author, genre, publication_year) VALUES (?, ?, ?, ?)",
            ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", 1925),
        )
        cursor.execute(
            "INSERT INTO books (title, author, genre, publication_year) VALUES (?, ?, ?, ?)",
            ("1984", "George Orwell", "Dystopian", 1949),
        )
        conn.commit()
        print("Initial data inserted.")
    except sqlite3.IntegrityError:
        print("Initial data already exists (or a unique constraint failed).")
    conn.close()
