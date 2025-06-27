"""
Shared state for API modules
"""

from typing import Dict, List

# In-memory storage for loaded agents and conversation histories
loaded_agents: Dict[str, any] = {}
conversation_histories: Dict[str, List[List[str]]] = {}