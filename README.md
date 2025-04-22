# SWIFT Codes API

A FastAPI-based service for managing and querying SWIFT/BIC codes with PostgreSQL database backend.

## Features

- CRUD operations for SWIFT codes
- Search by SWIFT code or country
- Headquarters-branch relationship handling
- CSV data import functionality
- Comprehensive unit and integration tests
- Dockerized deployment

## Project Structure
swift-codes-api/
├── app/ # Main application code
│ ├── init.py
│ ├── main.py # FastAPI app and routes
│ ├── database.py # Database configuration
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic models
│ ├── services.py # Business logic
│ ├── utils.py # Utility functions
├── tests/ # Test files
│ ├── conftest.py # Test fixtures
│ ├── test_api.py # API endpoint tests
│ ├── test_services.py # Service layer tests
├── data/ # Data files
│ └── Interns_2025_SWIFT_CODES.csv # Sample SWIFT codes
├── docker-compose.yml # Docker compose configuration
├── Dockerfile # Application Dockerfile
├── requirements.txt # Python dependencies
├── env.example # Environment variables example
└── README.md # This file


## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/swift-codes-api.git
   cd swift-codes-api
Copy the example environment file:

bash
cp env.example .env
Edit the .env file with your configuration if needed.

Build and start the services:

bash
docker-compose up --build
The API will be available at http://localhost:8000

Running Tests
To run the test suite:

bash
docker-compose run app pytest -v
The tests include:

Unit tests for service layer

Integration tests for API endpoints

Database operation tests

API Documentation
Once the service is running, you can access:

Interactive API docs: http://localhost:8000/docs

OpenAPI schema: http://localhost:8000/openapi.json

Endpoints
GET /api/v1/swift-codes/{swift_code} - Get SWIFT code details

GET /api/v1/swift-codes/country/{country_code} - Get all codes for a country

POST /api/v1/swift-codes - Create new SWIFT code

DELETE /api/v1/swift-codes/{swift_code} - Delete a SWIFT code

GET /health - Service health check

Development
To run locally without Docker:

Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Start the PostgreSQL database:

bash
docker-compose up db -d
Run the application:

bash
uvicorn app.main:app --reload
Data Import
The application automatically imports SWIFT codes from the CSV file (Interns_2025_SWIFT_CODES.csv) on startup. To manually trigger an import:

python
from app.utils import import_swift_codes_from_csv
from app.database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    await import_swift_codes_from_csv(session)
Deployment
For production deployment:

Set appropriate environment variables in .env

Configure proper database connection pooling

Consider adding:

Rate limiting

Authentication

HTTPS

Monitoring

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT