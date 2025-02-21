# Flask Movie Upload and Retrieval Application

This is a Flask application that allows users to upload movie data in CSV format, store it in a MongoDB database, and retrieve the stored data with various filters.

## Prerequisites

- Python 3.11
- MongoDB

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Ensure MongoDB is running:**

    Make sure your MongoDB server is running and accessible at `mongodb://localhost:27017/`.

## Configuration

The MongoDB connection URI is set in the `app.py` file:

```python
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client.flaskproject
collection = db.moviesData
```

5. **Running the Application**

    1. **Start the Flask application:**

        ```bash
        python app.py
        ```

    2. **Access the application:**

        Open your web browser and go to `http://localhost:5000`.

## API Endpoints

### Upload Movie Data

- **Endpoint:** `/upload`
- **Method:** `POST`
- **Description:** Uploads a CSV file containing movie data.
- **Request Body:**
    ```json
    {
        "filename": "movies.csv",
        "content": "<base64_encoded_csv_content>"
    }
    ```
- **Response:**
    ```json
    {
        "message": "File uploaded successfully",
        "records_inserted": 10
    }
    ```

### Retrieve Movies

- **Endpoint:** `/movies`
- **Method:** `GET`
- **Description:** Retrieves movies from the database with optional filters.
- **Query Parameters:**
    - `page` (int): Page number (default: 1)
    - `limit` (int): Number of records per page (default: 10)
    - `year` (str): Filter by release year (e.g., `1995`)
    - `language` (str): Filter by language (case-insensitive)
    - `sort_by` (str): Sort by field (`release_date` or `vote_average`, default: `release_date`)
    - `order` (str): Sort order (`asc` or `desc`, default: `desc`)
- **Response:**
    ```json
    {
        "total_records": 100,
        "current_page": 1,
        "total_pages": 10,
        "movies": [
            {
                "title": "Movie Title",
                "release_date": "1995-12-15",
                "languages": ["English", "French"],
                "vote_average": 7.5,
                "revenue": 1000000
            },
            ...
        ]
    }
    ```

## Application Structure

- `app.py`: Main application file containing routes and logic.
- `templates/`: Directory containing HTML templates.
    - `index.html`: Home page with file upload form.
    - `moviesCRM.html`: Page to view and filter movies.

## Notes

- Ensure that the `languages` field in the CSV file is formatted as a list of strings (e.g., `["English", "French"]`).
- The application uses the `pandas` library to process CSV files and the `pymongo` library to interact with MongoDB.
