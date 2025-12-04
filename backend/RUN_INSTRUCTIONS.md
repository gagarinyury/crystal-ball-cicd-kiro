# Running Crystal Ball CI/CD Backend

## Prerequisites

- Python 3.11+
- All dependencies installed: `pip install -r requirements.txt`
- Environment variables configured in `.env` file

## Starting the Server

### Option 1: Using uvicorn directly
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8023 --reload
```

### Option 2: Using Python
```bash
cd backend
python main.py
```

## Endpoints

Once running, the following endpoints are available:

- **Health Check**: `GET http://localhost:8023/health`
- **GitHub Webhook**: `POST http://localhost:8023/webhook/github`
- **WebSocket**: `ws://localhost:8023/ws`
- **API Docs**: `http://localhost:8023/docs` (Swagger UI)

## Testing

Run all tests:
```bash
pytest backend/test_*.py -v
```

## Logs

The application logs all events with sensitive data redaction enabled. API keys and tokens are automatically redacted from logs.

## Environment Variables Required

- `GITHUB_TOKEN`: GitHub personal access token
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude
- `GITHUB_WEBHOOK_SECRET`: Secret for webhook signature validation
- `BACKEND_PORT`: Port to run on (default: 8000)
- `FRONTEND_URL`: Frontend URL for CORS (default: http://localhost:5173)
