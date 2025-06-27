# AI Document Q&A System

A modern FastAPI-based backend and responsive frontend for uploading documents, processing them with AI embeddings, and asking questions about their content.
This project is an AI-powered Document Q&A System using FastAPI, SQLAlchemy, HuggingFace embeddings, FAISS, and LangChain with Mistral LLM. It enables users to upload documents and get intelligent, context-aware answers, showcasing advanced backend design and modern NLP integration.
---


https://github.com/user-attachments/assets/4b6ec588-eade-4865-a3f2-bc4c3b698b94


## Features

- **Document Upload & Processing:** Upload `.txt`, `.pdf`, `.docx`, or `.md` files. Documents are split into chunks, embedded with HuggingFace models, and stored for semantic search.
- **AI-Powered Q&A:** Ask questions about your uploaded documents. Answers are generated using Mistral LLM via LangChain, with context and chat history support.
- **User Authentication:** Register, login, and manage users with JWT-based authentication.
- **Modern Frontend:** Responsive, mobile-friendly UI with drag-and-drop upload, real-time feedback, and authentication.
- **RESTful API:** Well-structured endpoints for documents, questions, and users.
- **Extensible Services:** Modular service layer for document processing, Q&A, and user management.

---

## Project Structure

```
.
├── app/
│   ├── api/                # API routers and endpoint definitions
│   │   ├── v1/
│   │   │   ├── endpoints/  # API endpoints: auth, users, documents, questions
│   │   │   └── router.py   # Main API router
│   │   └── deps.py         # Dependency injection for FastAPI
│   ├── core/               # Core config, security, and exception handling
│   ├── db/                 # Database session and base
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic schemas for validation/serialization
│   ├── services/           # Business logic: document processing, Q&A, users
│   ├── main.py             # FastAPI app entrypoint
│   └── main_minimal.py     # (Optional) Minimal FastAPI app
├── frontend/               # Modern HTML/CSS/JS frontend
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── README.md
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── uploads/                # Uploaded documents (gitignored)
```

---

## Backend File Overview

### `app/main.py`
- FastAPI app entrypoint. Sets up CORS, trusted hosts, exception handlers, and includes all API routers.

### `app/api/v1/endpoints/`
- **auth.py:** User registration, login, and token testing endpoints.
- **users.py:** Endpoints for user info and admin user listing.
- **documents.py:** Upload, list, update, delete, process, and summarize documents.
- **questions.py:** Create, list, retrieve, and delete questions about documents.
- **rl.py:** (Empty, RL code removed.)

### `app/services/`
- **document_processor.py:** Handles document splitting, embedding, and storage. Uses HuggingFace and FAISS for local vector search.
- **qa_service.py:** Handles question answering using LangChain, Mistral LLM, and document embeddings. Supports context and chat history.
- **user_service.py:** User CRUD, authentication, and password management.

### `app/models/models.py`
- SQLAlchemy models for User, Document, DocumentEmbedding, and Question.

### `app/schemas/schemas.py`
- Pydantic schemas for all API data validation and serialization.

### `app/core/`
- **config.py:** App settings and environment variable management.
- **security.py:** Password hashing and JWT token creation.
- **exceptions.py:** Custom exception classes for API errors.

### `app/db/`
- **base.py:** SQLAlchemy base and model import.
- **session.py:** Database session creation.

---

## Frontend Overview

See `frontend/README.md` for full details.

- **index.html:** Main UI, includes upload, login, and Q&A forms.
- **styles.css:** Custom styles and responsive design.
- **script.js:** Handles API calls, authentication, file upload, and Q&A logic.

---

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database:**
   ```bash
   # If using Alembic for migrations
   alembic upgrade head
   ```

6. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Run the frontend:**
   ```bash
   cd frontend
   python -m http.server 3000
   # Visit http://localhost:3000
   ```

---

## API Endpoints

- `POST /api/v1/auth/login/access-token` — Login and get JWT token
- `POST /api/v1/auth/register` — Register a new user
- `GET /api/v1/users/me` — Get current user info
- `POST /api/v1/documents/upload` — Upload a document
- `GET /api/v1/documents/` — List user documents
- `POST /api/v1/questions/` — Ask a question about a document
- `GET /api/v1/questions/` — List your questions

See `/docs` for full interactive API documentation.

---

## Database & Data

- **SQLite** is used by default (see `DATABASE_URL` in `.env`).
- **Document embeddings** are stored in the `document_embeddings` table.
- **FAISS index** is built in-memory from these embeddings on each app start.
- **Uploaded files** are stored in the `uploads/` directory (add this to `.gitignore`).

---

## Security

- JWT-based authentication for all protected endpoints.
- Passwords are hashed using best practices.
- CORS enabled for frontend-backend communication.

---

## How to Clear All Document Embeddings

To clear all FAISS data, delete all rows from the `document_embeddings` table:
```python
from app.db.session import SessionLocal
from app.models.models import DocumentEmbedding

db = SessionLocal()
db.query(DocumentEmbedding).delete()
db.commit()
db.close()
```
Or use a DB tool to run: `DELETE FROM document_embeddings;`

---

## .gitignore Recommendations

Add the following to your `.gitignore` to avoid committing sensitive or large files:
```
# SQLite database files
*.db
*.sqlite3
app.db
app/*.db
uploads/
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## License

MIT License. See LICENSE file for details.

---

**For more details on the frontend, see `frontend/README.md`.** 
