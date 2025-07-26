from flask import Flask, request, jsonify
from database import get_db_connection, init_db  # Import our database functions
from sqlite3 import Error as sqlite3Error

app = Flask(__name__)

# Call init_db() once when the application starts
# In a larger app, you might do this in a separate setup script or manage migrations
init_db()

# Define a simple API key (for demonstration purposes only, use environment variables or a config file in production)
API_KEY = "secret_simple_api_key_dev"  # Change this to a more secure and random key in production


# Decorator for API key authentication
def api_key_required(func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"message": "API Key is missing"}), 401  # 401 Unauthorized
        if api_key != API_KEY:
            return jsonify({"message": "Invalid API Key"}), 403  # 403 Forbidden
        return func(*args, **kwargs)

    # Flask needs this to correctly identify decorated functions
    wrapper.__name__ = func.__name__
    return wrapper


# --- API Endpoints ---


# 1. GET all books with search and pagination features
@app.route("/books", methods=["GET"])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()

    # -- Search Parameters --
    # Get query parameters from the request for searching
    search_title = request.args.get(
        "title", default="", type=str
    )  # Default to empty string if not provided
    search_author = request.args.get("author", default="", type=str)
    search_genre = request.args.get("genre", default="", type=str)
    search_pub_year = request.args.get(
        "publication_year", default="", type=str
    )  # Will be a string, convert later if needed for exact match

    # Build the WHERE clause dynamically based on provided search parameters
    where_clauses = []
    params = []

    if search_title:
        where_clauses.append("title LIKE ?")
        params.append(f"%{search_title}%")

    if search_author:
        where_clauses.append("author LIKE ?")
        params.append(f"%{search_author}%")

    if search_genre:
        where_clauses.append("genre LIKE ?")
        params.append(f"%{search_genre}%")

    if search_pub_year:
        try:
            # Convert to integer for exact match
            pub_year_int = int(search_pub_year)
            where_clauses.append("publication_year = ?")
            params.append(pub_year_int)
        except ValueError:
            # Handle case where publication_year is not a valid integer
            conn.close()
            return (
                jsonify(
                    {"message": "Invalid publication year format. Must be an integer."}
                ),
                400,
            )

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # -- Pagination Parameters --
    page = request.args.get("page", default=1, type=int)  # Default to page 1
    limit = request.args.get(
        "limit", default=10, type=int
    )  # Default to 10 items per page

    if page < 1 or limit < 1:
        conn.close()
        return jsonify({"message": "Page and limit must be positive integers"}), 400

    offset = (page - 1) * limit

    # -- Construct the SQL query with search and pagination --
    # First, get total count for pagination metadata
    count_sql = f"SELECT COUNT(*) FROM books {where_sql}"
    total_books = conn.execute(count_sql, params).fetchone()[0]

    # Then, get the actual books with limit and offset
    sql_query = f"SELECT * FROM books {where_sql} LIMIT ? OFFSET ?"
    # Append limit and offset to the parameters
    params.extend([limit, offset])

    books = cursor.execute(sql_query, params).fetchall()
    conn.close()
    # Convert sqlite3.Row objects to dictionaries for jsonify
    books_list = [dict(book) for book in books]

    # Prepare pagination metadata
    total_pages = (
        total_books + limit - 1
    ) // limit  # Ceiling division to get total pages
    pagination_metadata = {
        "total_books": total_books,
        "total_pages": total_pages,
        "current_page": page,
        "books_per_page": limit,
        "next_page": page + 1 if page < total_pages else None,
        "previous_page": page - 1 if page > 1 else None,
    }

    return jsonify({"data": books_list, "pagination": pagination_metadata})


# 2. GET a single book by ID
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    if book is None:
        return jsonify({"message": "Book not found"}), 404
    return jsonify(dict(book))


# 3. POST (Create) a new book
@app.route("/books", methods=["POST"])
@api_key_required  # Apply the API key authentication decorator
def create_book():
    new_book_data = request.get_json()

    # Basic input validation
    if not new_book_data or not all(
        key in new_book_data for key in ["title", "author"]
    ):
        return jsonify({"message": "Missing title or author in request body"}), 400

    title = new_book_data["title"]
    author = new_book_data["author"]
    genre = new_book_data.get("genre")  # genre is optional
    publication_year = new_book_data.get(
        "publication_year"
    )  # publication_year is optional

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, genre, publication_year) VALUES (?, ?, ?, ?)",
            (title, author, genre, publication_year),
        )
        conn.commit()
        book_id = cursor.lastrowid  # Get the ID of the newly inserted book
        new_book = conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return jsonify(dict(new_book)), 201  # 201 Created
    except sqlite3Error as e:
        conn.rollback()
        return jsonify({"message": "Database error", "error": str(e)}), 500
    finally:
        conn.close()


# 4. PUT (Update) an existing book
@app.route("/books/<int:book_id>", methods=["PUT"])
@api_key_required  # Apply the API key authentication decorator
def update_book(book_id):
    update_data = request.get_json()

    # Find the existing book first
    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        conn.close()
        return jsonify({"message": "Book not found"}), 404

    # Update fields only if provided in the request body
    title = update_data.get("title", book["title"])
    author = update_data.get("author", book["author"])
    genre = update_data.get("genre", book["genre"])
    publication_year = update_data.get("publication_year", book["publication_year"])

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET title = ?, author = ?, genre = ?, publication_year = ? WHERE id = ?",
            (title, author, genre, publication_year, book_id),
        )
        conn.commit()
        updated_book = conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()
        return jsonify(dict(updated_book))
    except sqlite3Error as e:
        conn.rollback()
        return jsonify({"message": "Database error", "error": str(e)}), 500
    finally:
        conn.close()


# 5. DELETE a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
@api_key_required  # Apply the API key authentication decorator
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    rows_affected = cursor.rowcount  # Check how many rows were deleted
    conn.close()

    if rows_affected == 0:
        return jsonify({"message": "Book not found"}), 404
    return jsonify({"message": "Book deleted successfully"}), 200  # 200 OK


if __name__ == "__main__":
    app.run(
        debug=True
    )  # Run the Flask app in debug mode for development (auto-reload and better error messages)
