# Web Frameworks Tutorial Platform

A comprehensive tutorial platform for learning Flask, FastAPI, and PostgreSQL through interactive lessons and hands-on exercises.

## Project Structure

```
web-frameworks-tutorial/
├── backend/                 # FastAPI backend application
│   ├── app/                # Application code
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile.dev     # Development Docker configuration
├── frontend/               # React frontend application
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile.dev     # Development Docker configuration
├── database/              # Database configuration
│   └── init/             # Database initialization scripts
├── docker-compose.yml     # Docker Compose configuration
└── setup_dev.py          # Development environment setup script
```

## Quick Start

### Option 1: Automated Setup (Recommended)

1. Run the setup script:
   ```bash
   python setup_dev.py
   ```

2. Activate the Python virtual environment:
   ```bash
   # On Unix/Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Option 2: Manual Setup

1. **Set up Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Set up frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

## Services

- **Backend API**: http://localhost:8000
  - API documentation: http://localhost:8000/docs
  - Health check: http://localhost:8000/health

- **Frontend**: http://localhost:3000

- **PostgreSQL Database**: localhost:5432
  - Database: `tutorial_db`
  - Username: `tutorial_user`
  - Password: `tutorial_password`

## Development Commands

### Backend
```bash
# Run backend locally (without Docker)
cd backend
uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Frontend
```bash
# Run frontend locally (without Docker)
cd frontend
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild services
docker-compose up --build
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic
- **Frontend**: React, TypeScript, Tailwind CSS, Monaco Editor
- **Database**: PostgreSQL 15
- **Development**: Docker, Docker Compose

## Next Steps

After setting up the development environment, you can proceed with implementing the remaining tasks from the project specification:

1. Database models and migrations
2. Authentication system
3. Content management API
4. User progress tracking
5. Code execution system
6. Frontend components

See the full implementation plan in `.kiro/specs/web-frameworks-tutorial/tasks.md`.