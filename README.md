# AI-Powered Document Processing and Q&A System

A sophisticated FastAPI-based application that combines document processing, question answering, and reinforcement learning to provide intelligent responses. This project demonstrates modern Python development practices and integration of cutting-edge AI technologies.

## Features

- **Smart Document Processing**: Upload and process documents using LangChain and OpenAI
- **Intelligent Q&A System**: Ask questions about your documents and get AI-powered responses
- **Reinforcement Learning**: Optimize response quality using RL algorithms
- **Modern API Design**: RESTful API with FastAPI and Pydantic
- **Authentication & Authorization**: JWT-based security
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Asynchronous Processing**: Celery for background tasks
- **Caching**: Redis for performance optimization
- **Containerization**: Docker support
- **Testing**: Comprehensive test suite with pytest
- **CI/CD**: GitHub Actions workflow

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings management
- **LangChain**: Framework for LLM applications
- **OpenAI**: GPT models for natural language processing
- **PyTorch**: Deep learning framework for RL
- **PostgreSQL**: Primary database
- **Redis**: Caching and message broker
- **Celery**: Distributed task queue
- **Docker**: Containerization
- **Alembic**: Database migrations

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── router.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── qa_service.py
│   │   └── rl_service.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_api/
├── alembic/
│   └── versions/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 