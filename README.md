# Simple RESTful Book Management API

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgray.svg?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-brightgreen?style=flat&logo=github)](https://github.com/m-arifin-ilham/simple_book_api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project implements a simple RESTful API for managing a collection of books. It allows users to perform standard CRUD (Create, Read, Update, Delete) operations on book entries stored in a SQLite database. This API serves as a foundational backend for a data-driven application, demonstrating robust data handling and clear endpoint design.

## Features

* **Retrieve All Books:** Fetch a list of all available books with search and pagination capabilities.
* **Retrieve Single Book:** Get details for a specific book by its unique ID.
* **Add New Book:** Create a new book entry in the database.
* **Update Existing Book:** Modify the details of an existing book.
* **Delete Book:** Remove a book entry from the database.
* Basic input validation and error handling.
* **Basic API Key authentication** for write/delete operations (POST, PUT, DELETE).

## Technologies Used

* **Backend Framework:** Python (Flask)
* **Database:** SQLite3
* **HTTP Client (for testing):** Python Requests library

## Project Structure

```
simple_book_api/
├── venv/               # Python Virtual Environment
├── app.py              # Flask API application
├── database.py         # Database initialization and connection logic
├── test_api.py         # Script for testing API endpoints
├── requirements.txt    # Project dependencies
├── .gitignore          # Specifies files/folders to ignore in Git
└── LICENSE             # Project license file
```

## Getting Started

Follow these steps to set up and run the API locally on your machine.

### Prerequisites

* Python 3.8+ installed on your system.

### Installation

1.  **Clone the repository (or download the ZIP):**
    ```bash
    git clone https://github.com/m-arifin-ilham/simple_book_api
    cd simple_book_api
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scipts\activate
    # On macOS/Linux:
    source venv/bin/activate 
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Database Initialization

Initialize the SQLite database and populate it with some sample data (a 'books.db' file will be created):

```bash
python database.py
```

### Running the API

Ensure your virtual environment is active, then run the Flask application:

```bash
# Set the FLASK_APP environment variable (once per session/terminal)
# On Windows:
set FLASK_APP=app.py
# On macOS/Linux:
export FLASK_APP=app.py

# Start the Flask development server
flask run
```

The API will be running at http://127.0.0.1:5000.

## API Endpoints

All API requests should be sent to http://127.0.0.1:5000.

1.  ```GET /books```
    * **Description:** Retrieve a list of all books. Supports search/filtering and pagination.
    * **Method:** ```GET```
    * **Query Parameters (Optional):**
        * ```title``` (string): Search for books with titles containing this substring (case-insensitive partial match).
        * ```author``` (string): Search for books with authors containing this substring (case-insensitive partial match).
        * ```genre``` (string): Search for books with genres containing this substring (case-insensitive partial match).
        * ```publication_year``` (integer): Search for books published in this specific year.
        * ```page``` (integer): The page number to retrieve (default: 1).
        * ```limit``` (integer): The number of items per page (default: 10).
    * **Example Requests:**
        * ```GET /books```
        * ```GET /books?title=dune```
        * ```GET /books?author=george&genre=dystopian```
        * ```GET /books?page=2&limit=5```
        * ```GET /books?title=the&limit=3```
    * **Response (Success - 200 OK):**
    ```JSON
    {
        "data": [
            {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "genre": "Classic",
                "publication_year": 1925
            },
            {
                "id": 2,
                "title": "1984",
                "author": "George Orwell",
                "genre": "Dystopian",
                "publication_year": 1949
            }
        ],
        "pagination": {
            "total_items": 2,
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 10,
            "next_page": null,
            "prev_page": null
        }
    }
    ```
    * **Response (Bad Request - 400 Bad Request for invalid params):**
    ```JSON
    {"message": "Invalid publication_year. Must be an integer."}
    ```

2.  ```GET /books/{book_id}```
    * **Description:** Retrieve a single book by its ID.
    * **Method:** ```GET```
    * **URL Parameter:** ```book_id``` (integer) - The ID of the book to retrieve.
    * **Response (Success - 200 OK):** The following is the response if the ```book_id``` is ```1```.
    ```JSON
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic",
        "publication_year": 1925
    }
    ```
    * **Response (Not Found - 404 Not Found):**
    ```JSON
    {"message": "Book not found"}
    ```

3.  ```POST /books```
    * **Description:** Add a new book to the collection.
    * **Method:** ```POST```
    * **Headers:**
        * ```x-api-key: secret_simple_api_key_dev```
    * **Request Body:** The following is an example of the request body required. The fields ```genre``` and ```publication_year``` are optional.
    ```JSON
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "publication_year": 1965
    }
    ```
    * **Response (Success - 201 Created):** Returns the newly created book object with its assigned ID. The following is an example of the response.
    ```JSON
    {
        "id": 3,
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "publication_year": 1965
    }
    ```
    * **Response (Bad Request - 400 Bad Request):**
    ```JSON
    {"message": "Database error"}
    ```
    Probably caused by missing title or author in request body.
    * **Response (Unauthorized - 401 Unauthorized):**
    ```JSON
    {"description": "API Key is missing", "code": 401}
    ```
    * **Response (Forbidden - 403 Forbidden):**
    ```JSON
    {"description": "Invalid API Key", "code": 403}
    ```

4.  ```PUT /books/{book_id}```
    * **Description:** Update an existing book's details.
    * **Method:** ```PUT```
    * **URL Parameter:** ```book_id``` (integer) - The ID of the book to update.
    * **Headers:**
        * ```x-api-key: secret_simple_api_key_dev```
    * **Request Body (JSON):** Provide only the field you want to update. The following is an example of request body.
    ```JSON
    {
        "title": "Dune (Revised Edition)",
        "publication_year": 2001
    }
    ```
    * **Response (Success - 200 OK):** Returns the updated book object. The following is an example of the response.
    ```JSON
    {
        "id": 3,
        "title": "Dune (Revised Edition)",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "publication_year": 2001
    }
    ```
    * **Response (Not Found - 404 Not Found):**
    ```JSON
    {"message": "Book not found"}
    ```
    * **Response (Unauthorized - 401 Unauthorized):**
    ```JSON
    {"description": "API Key is missing", "code": 401}
    ```
    * **Response (Forbidden - 403 Forbidden):**
    ```JSON
    {"description": "Invalid API Key", "code": 403}
    ```

5.  ```DELETE /books/{book_id}```
    * **Description:** Delete a book from the collection.
    * **Method:** ```DELETE```
    * **URL Parameter:** ```book_id``` (integer) - The ID of the book to delete.
    * **Headers:**
        * ```x-api-key: secret_simple_api_key_dev```
    * **Response (Success - 200 OK):**
    ```JSON
    {"message": "Book deleted successfully"}
    ```
    * **Response (Not Found - 404 Not Found):**
    ```JSON
    {"message": "Book not found"}
    ```
    * **Response (Unauthorized - 401 Unauthorized):**
    ```JSON
    {"description": "API Key is missing", "code": 401}
    ```
    * **Response (Forbidden - 403 Forbidden):**
    ```JSON
    {"description": "Invalid API Key", "code": 403}
    ```

## How to Test

You can test the API using the provided 'test_api.py' script:

1.  Ensure the Flask API is running (as shown in "Running the API" section).
2. Open a **separate** terminal window and activate the virtual environment.
3. Run the script:
```bash
python test_api.py
```
4. Observe the output for API responses and status codes.

Alternatively, you can use tools like Postman or curl to send requests directly to the API endpoints. Remember to include the ```x-api-key header``` for protected endpoints.

## Future Enhancements

* Implement more robust user authentication and authorization (e.g., using JWT and user roles).
* Integrate with a more robust, external database like PostgreSQL or MySQL.
* Containerize the application using Docker for easier deployment.
* Add automated unit and integration tests (e.g., using pytest).
* Implement advanced filtering options (e.g., range queries for ```publication_year```).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Developed by [Muhammad Arifin Ilham](https://github.com/m-arifin-ilham)*

* [Github](https://github.com/m-arifin-ilham/simple_book_api)
* [Linkedin](https://www.linkedin.com/in/arifin-ilham-at-ska/)
