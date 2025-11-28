# Setup Guide

## Quick Start with Docker

The easiest way to get started is using Docker:

```bash
# 1. Clone the repository
git clone <repository-url>
cd chatbot

# 2. Copy environment file and configure
cp .env.example .env
# Edit .env and add your API keys

# 3. Start with Docker Compose
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Manual Setup

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run the backend
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Configuration

### API Keys

You'll need API keys from:

1. **OpenAI** (optional): Get from https://platform.openai.com/api-keys
2. **Anthropic** (optional): Get from https://console.anthropic.com/

Add them to your `.env` file:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Security

Change the default secret key in production:

```env
SECRET_KEY=your-secure-random-key-here
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database

By default, the application uses SQLite. For production, consider PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/chatbot
```

## Production Deployment

### Using Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

For production, use a production ASGI server and configure:

1. Set `DEBUG=False` in backend
2. Configure proper CORS origins
3. Use a production database (PostgreSQL)
4. Set up HTTPS/SSL
5. Configure reverse proxy (nginx)
6. Set up monitoring and logging

## Troubleshooting

### Backend won't start
- Check Python version (3.9+)
- Verify virtual environment is activated
- Check API keys in `.env`
- Review logs for errors

### Frontend build fails
- Check Node.js version (18+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check for syntax errors in code

### Database errors
- Delete database file to reset: `rm chatbot.db`
- Check DATABASE_URL configuration
- Verify database permissions

## Support

For issues and questions:
- Check the README.md
- Review API documentation at `/docs`
- Open an issue on GitHub
