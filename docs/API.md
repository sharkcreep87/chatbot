# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "secure_password"
}
```

Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=secure_password
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Conversations

#### Create Conversation
```http
POST /api/chat/conversations
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Chat",
  "ai_provider": "openai",
  "model": "gpt-4-turbo-preview",
  "system_prompt": "You are a helpful assistant."
}
```

#### Get All Conversations
```http
GET /api/chat/conversations?skip=0&limit=50
Authorization: Bearer <token>
```

#### Get Conversation
```http
GET /api/chat/conversations/{id}
Authorization: Bearer <token>
```

#### Update Conversation
```http
PATCH /api/chat/conversations/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "system_prompt": "New system prompt"
}
```

#### Delete Conversation
```http
DELETE /api/chat/conversations/{id}
Authorization: Bearer <token>
```

### Messages

#### Get Messages
```http
GET /api/chat/conversations/{conversation_id}/messages?skip=0&limit=100
Authorization: Bearer <token>
```

#### Send Message
```http
POST /api/chat/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "conversation_id": 1,
  "ai_provider": "openai",
  "model": "gpt-4-turbo-preview",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

Response:
```json
{
  "conversation_id": 1,
  "message": {
    "id": 2,
    "conversation_id": 1,
    "user_id": 1,
    "role": "assistant",
    "content": "Hello! I'm doing well, thank you for asking...",
    "metadata": {},
    "tokens_used": 50,
    "is_edited": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "tokens_used": 50
}
```

#### Send Message (Streaming)
```http
POST /api/chat/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Tell me a story",
  "conversation_id": 1,
  "ai_provider": "openai",
  "model": "gpt-4-turbo-preview"
}
```

Response: Server-Sent Events (SSE)
```
data: {"content": "Once"}
data: {"content": " upon"}
data: {"content": " a"}
data: {"content": " time"}
data: {"done": true, "conversation_id": 1}
```

## AI Providers

### OpenAI
- Models: `gpt-4-turbo-preview`, `gpt-4`, `gpt-3.5-turbo`
- Requires: `OPENAI_API_KEY`

### Anthropic Claude
- Models: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Requires: `ANTHROPIC_API_KEY`

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

No rate limiting is currently implemented. For production, consider adding rate limiting middleware.

## Interactive Documentation

Visit these URLs when the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
