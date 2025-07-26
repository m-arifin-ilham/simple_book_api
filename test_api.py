import requests
import json

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "secret_simple_api_key_dev"  # Ensure this matches the key in app.py

# Header for API key authentication
AUTH_HEADERS = {"X-API-Key": API_KEY}
# Headers for non-authenticated requests
NO_AUTH_HEADERS = {}


def test_get_all_books(params=None):
    print("\n--- GET All Books (with optional search/pagination) ---")
    response = requests.get(f"{BASE_URL}/books", params=params, headers=NO_AUTH_HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_get_single_book(book_id):
    print(f"\n--- GET Book by ID {book_id} ---")
    response = requests.get(f"{BASE_URL}/books/{book_id}", headers=NO_AUTH_HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_create_book():
    print("\n--- POST Create New Book ---")
    new_book = {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "publication_year": 1965,
    }
    response = requests.post(f"{BASE_URL}/books", json=new_book, headers=AUTH_HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("id")  # Return the ID of the newly created book


def test_update_book(book_id):
    print(f"\n--- PUT Update Book ID {book_id} ---")
    update_data = {"title": "Dune (Revised Edition)", "publication_year": 2001}
    response = requests.put(
        f"{BASE_URL}/books/{book_id}", json=update_data, headers=AUTH_HEADERS
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_delete_book(book_id):
    print(f"\n--- DELETE Book ID {book_id} ---")
    response = requests.delete(f"{BASE_URL}/books/{book_id}", headers=AUTH_HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


# --- Test Authentication Failures ---
def test_create_book_unauthenticated():
    print("\n--- POST Create New Book (Unauthenticated) ---")
    new_book = {"title": "1984", "author": "George Orwell"}
    response = requests.post(
        f"{BASE_URL}/books", json=new_book, headers=NO_AUTH_HEADERS
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    # Ensure your Flask app is running in another terminal before running this script!

    # Test unauthenticated POST
    test_create_book_unauthenticated()

    # Initial GET all books (no search/pagination)
    test_get_all_books()

    # Create a few books for testing search and pagination
    book_ids = []
    book_ids.append(test_create_book())  # Create first book
    book_ids.append(
        requests.post(
            f"{BASE_URL}/books",
            json={
                "title": "Foundation",
                "author": "Isaac Asimov",
                "genre": "Science Fiction",
            },
            headers=AUTH_HEADERS,
        )
        .json()
        .get("id")
    )
    book_ids.append(
        requests.post(
            f"{BASE_URL}/books",
            json={
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "genre": "Romance",
            },
            headers=AUTH_HEADERS,
        )
        .json()
        .get("id")
    )
    book_ids.append(
        requests.post(
            f"{BASE_URL}/books",
            json={
                "title": "The Lord of the Rings",
                "author": "J.R.R. Tolkien",
                "genre": "Fantasy",
                "publication_year": 1954,
            },
            headers=AUTH_HEADERS,
        )
        .json()
        .get("id")
    )
    book_ids.append(
        requests.post(
            f"{BASE_URL}/books",
            json={
                "title": "The Catcher in the Rye",
                "author": "J.D. Salinger",
                "genre": "Fiction",
            },
            headers=AUTH_HEADERS,
        )
        .json()
        .get("id")
    )

    # Test search by title
    test_get_all_books(params={"title": "dune"})
    test_get_all_books(params={"title": "the"})  # Should get multiple results
    test_get_all_books(params={"author": "george"})

    # Test search by genre and publication year
    test_get_all_books(
        params={"genre": "science", "publication_year": 1965}
    )  # Should match Dune

    # Test pagination
    test_get_all_books(params={"page": 1, "limit": 2})  # First page with 2 results
    test_get_all_books(
        params={"page": 2, "limit": 2}
    )  # Second page with next 2 results
    test_get_all_books(
        params={"page": 3, "limit": 2}
    )  # Should show no results if only 5 books exist
    test_get_all_books(params={"page": 99, "limit": 2})  # Out of range page

    # Test combined search and pagination
    test_get_all_books(
        params={"genre": "the", "page": 1, "limit": 1}
    )  # Search with pagination

    # Perform updates and deletes on the newly created book
    if book_ids:
        # Pick one of the created book IDs for testing
        book_test_id = book_ids[0]
        if book_test_id:
            test_get_single_book(book_test_id)
            test_update_book(book_test_id)
            test_get_single_book(book_test_id)  # See updated data
            test_delete_book(book_test_id)
            test_get_single_book(book_test_id)  # Should now be "Book not found"

    test_delete_book(999)  # Attempt to delete a non-existent book
    test_get_all_books()  # See remaining books after operations
