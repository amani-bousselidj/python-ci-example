# Portfolio Admin Dashboard API

A FastAPI-based backend API for managing contact form messages from a personal portfolio website.

## Features

- **Message Management**: Create, read, update, and delete contact messages
- **Admin Dashboard API**: Dedicated admin endpoints for message management
- **Message Statistics**: Get summary statistics (total, read, unread messages)
- **Email Validation**: Built-in email validation for contact submissions
- **SQLite Database**: Lightweight database for message storage
- **CORS Support**: Ready for frontend integration
- **Comprehensive Tests**: Full test coverage with pytest

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **SQLite**: Lightweight database
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Server

### Option 1: Using the startup script (recommended)
```bash
./start_server.sh
```

### Option 2: Using uvicorn directly
```bash
# Start the server with auto-reload
uvicorn app:app --reload

# Or without reload for production
uvicorn app:app --host 0.0.0.0 --port 8000
```

The server will be available at http://localhost:8000

- API Documentation (Swagger): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Public Endpoints

#### Create Message
```bash
POST /api/messages
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Subject line",
  "message": "Message content"
}
```

### Admin Endpoints

#### Get All Messages
```bash
GET /api/admin/messages?skip=0&limit=100
```

#### Get Single Message
```bash
GET /api/admin/messages/{message_id}
```

#### Update Message Status
```bash
PATCH /api/admin/messages/{message_id}
Content-Type: application/json

{
  "read": true
}
```

#### Delete Message
```bash
DELETE /api/admin/messages/{message_id}
```

#### Get Message Statistics
```bash
GET /api/admin/messages/stats/summary
```

Returns:
```json
{
  "total": 10,
  "read": 3,
  "unread": 7
}
```

## Testing

```bash
# Run all tests
python -m pytest test_admin.py -v

# Run original math operation tests
python -m pytest test_app.py -v

# Run all tests
python -m pytest -v
```

## Database

The application uses SQLite by default with the database file stored as `messages.db`. The database schema includes:

- **id**: Primary key
- **name**: Sender's name
- **email**: Sender's email (validated)
- **subject**: Message subject
- **message**: Message content
- **timestamp**: When the message was created
- **read**: Boolean flag for message status

## Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./messages.db`)
- `DB_DIR`: Directory for database file (default: current directory)

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Quick Start with Example Script

The repository includes an example script that demonstrates all API endpoints:

```bash
# Make sure the server is running first
./start_server.sh

# In another terminal, run the example
python example_usage.py
```

### Manual API Usage

```python
import requests

# Submit a contact message
response = requests.post(
    "http://localhost:8000/api/messages",
    json={
        "name": "Jane Smith",
        "email": "jane@example.com",
        "subject": "Portfolio Inquiry",
        "message": "I'd like to discuss a project..."
    }
)
print(response.json())

# Get all messages (admin)
messages = requests.get("http://localhost:8000/api/admin/messages").json()
print(f"Total messages: {len(messages)}")

# Mark message as read
requests.patch(
    f"http://localhost:8000/api/admin/messages/1",
    json={"read": True}
)
```

## Development

The project includes:
- `app.py`: Main FastAPI application
- `test.py`: Original math utility functions
- `test_app.py`: Tests for math utilities
- `test_admin.py`: Comprehensive admin API tests
- `requirements.txt`: Python dependencies

## License

MIT