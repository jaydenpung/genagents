#!/usr/bin/env python3

import os
import sys
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("interview_api:app", host="0.0.0.0", port=port, reload=False)