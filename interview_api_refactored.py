"""
Refactored Web API for conducting interviews to create generative agents
This is the new entry point using the modular API structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)