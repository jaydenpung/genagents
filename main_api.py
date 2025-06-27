"""
Main entry point for the modular API
"""

from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 