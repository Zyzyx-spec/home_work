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
```
swift-codes-api/
├── app/                       # Main application code
│   ├── __init__.py
│   ├── main.py                # FastAPI app and routes
│   ├── database.py            # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic models
│   ├── services.py            # Business logic
│   ├── utils.py               # Utility functions
├── tests/                    # Test files
│   ├── conftest.py            # Test fixtures
│   ├── test_api.py            # API endpoint tests
│   ├── test_services.py       # Service layer tests
├── data/                     # Data files
│   └── Interns_2025_SWIFT_CODES.csv  # Sample SWIFT codes
├── docker-compose.yml        # Docker compose configuration
├── Dockerfile                # Application Dockerfile
├── requirements.txt          # Python dependencies
├── env.example               # Environment variables example
└── README.md                 # This file
```



## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

## Installation & Setup

1. Clone the repository:
```bash
   git clone https://github.com/your-username/swift-codes-api.git
cd swift-codes-api
```
2. Copy the example environment file:
```bash
cp env.example .env
Edit the .env file with your configuration if needed.
```
3. Build and start the services:
```bash
docker-compose up --build
```
4. The API will be available at http://localhost:8000

## Running Tests
To run the test suite:
```bash
docker-compose run app pytest -v
```
The tests include:

Unit tests for service layer

Integration tests for API endpoints

Database operation tests

##API Documentation
Once the service is running, you can access:

Interactive API docs: http://localhost:8000/docs

OpenAPI schema: http://localhost:8000/openapi.json

## Continuous Integration & Deployment (CI/CD)

This project uses GitHub Actions for automated testing and deployment. The workflow includes:

### CI/CD Pipeline Features:
- ✅ Automated tests on every push/pull request
- ✅ PostgreSQL service for integration testing
- ✅ Docker image build and push on successful tests
- ✅ Multi-stage pipeline (test → deploy)

### Pipeline Structure:
1. **Test Stage**:
   - Sets up Python 3.9
   - Installs dependencies
   - Runs unit and integration tests with PostgreSQL

2. **Deploy Stage** (main branch only):
   - Builds and pushes Docker image to Docker Hub

### Viewing Workflow Results:
- Go to **Actions** tab in your GitHub repository
- Click on the latest workflow run to see details
- View test results and deployment status

### Configuration:
The workflow is defined in [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)

[![CI/CD Status](https://github.com/Zyzyx-spec/home_exercise/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Zyzyx-spec/home_exercise/actions/workflows/ci-cd.yml)

## Endpoints
GET /api/v1/swift-codes/{swift_code} - Get SWIFT code details

GET /api/v1/swift-codes/country/{country_code} - Get all codes for a country

POST /api/v1/swift-codes - Create new SWIFT code

DELETE /api/v1/swift-codes/{swift_code} - Delete a SWIFT code

GET /health - Service health check

## Development
To run locally without Docker:

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. Install dependencies:

```bash
pip install -r requirements.txt
```
3. Start the PostgreSQL database:

```bash
docker-compose up db -d
```
4. Run the application:
```bash
uvicorn app.main:app --reload
```
## Data Import
The application automatically imports SWIFT codes from the CSV file (Interns_2025_SWIFT_CODES.csv) on startup. To manually trigger an import:

```python
from app.utils import import_swift_codes_from_csv
from app.database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    await import_swift_codes_from_csv(session)
```
## Deployment
For production deployment:

1. Set appropriate environment variables in .env

2. Configure proper database connection pooling

3. Consider adding:

Rate limiting

Authentication

HTTPS

Monitoring

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT