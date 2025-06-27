# API Structure

This directory contains the modular API endpoints for the Generative Agent Interview System.

## File Organization

### Core Files

- `__init__.py` - Package initialization
- `main.py` - Main FastAPI application setup and router inclusion
- `models.py` - Pydantic models for request/response validation
- `utils.py` - Utility functions and helpers

### Endpoint Modules

- `interview.py` - Interview-related endpoints (session management, questions, responses)
- `agents.py` - Agent-related endpoints (listing, details, chat functionality)

## API Endpoints

### Interview Endpoints (`/interview`)

- `POST /start` - Start a new interview session
- `GET /{session_id}/question` - Get current question for a session
- `POST /response` - Submit a response and advance to next question
- `POST /{session_id}/finalize` - Finalize agent creation from interview
- `GET /{session_id}` - Get interview session details
- `GET /sessions` - List all interview sessions
- `DELETE /{session_id}` - Delete an interview session

### Agent Endpoints (`/agents`)

- `GET /` - List all created agents
- `GET /{agent_id}` - Get agent details
- `POST /{agent_id}/chat` - Chat with an agent
- `DELETE /{agent_id}/chat` - Clear conversation history

## Usage

To run the API:

```bash
# Using the new modular structure
python main_api.py

# Or directly
python -m api.main
```

## Benefits of Modular Structure

1. **Separation of Concerns** - Each module handles specific functionality
2. **Maintainability** - Easier to find and modify specific endpoints
3. **Scalability** - Easy to add new endpoint modules
4. **Testing** - Can test individual modules in isolation
5. **Code Reuse** - Shared models and utilities across modules
