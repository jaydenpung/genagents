#!/usr/bin/env python3
"""
Migration script to move agents from agent_bank/populations/single_agent/ to database
"""

import os
import json
import uuid
import sys
from datetime import datetime

# Add the project root to the path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database, get_db_session, Agent as DBAgent, InterviewSession as DBInterviewSession
from genagents.genagents import GenerativeAgent

# Override DATABASE_URL for local connection
import os
os.environ['DATABASE_URL'] = 'postgresql://genagents_user:genagents_password@localhost:5432/genagents_db'

def migrate_single_agent_to_database():
    """
    Migrate the single agent from agent_bank/populations/single_agent/ to database
    """
    # Initialize database
    init_database()
    db = get_db_session()
    
    try:
        # Path to the single agent
        agent_path = "agent_bank/populations/single_agent/01fd7d2a-0357-4c1b-9f3e-8eade2d537ae"
        
        if not os.path.exists(agent_path):
            print(f"Agent directory not found: {agent_path}")
            return
        
        # Load agent data from files
        print(f"Loading agent from: {agent_path}")
        
        # Load scratch data
        scratch_file = os.path.join(agent_path, "scratch.json")
        with open(scratch_file, 'r') as f:
            scratch_data = json.load(f)
        
        # Load memory stream data
        nodes_file = os.path.join(agent_path, "memory_stream/nodes.json")
        with open(nodes_file, 'r') as f:
            nodes_data = json.load(f)
        
        embeddings_file = os.path.join(agent_path, "memory_stream/embeddings.json")
        with open(embeddings_file, 'r') as f:
            embeddings_data = json.load(f)
        
        # Create memory stream data structure
        memory_stream_data = {
            "nodes": nodes_data,
            "embeddings": embeddings_data
        }
        
        # Generate new agent ID and session ID
        agent_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        # Extract name from scratch data
        first_name = scratch_data.get("first_name", "Unknown")
        last_name = scratch_data.get("last_name", "Unknown")
        agent_name = f"{first_name} {last_name}"
        age = str(scratch_data.get("age", "Unknown"))
        
        # Create a dummy interview session for this agent
        print("Creating interview session...")
        interview_session = DBInterviewSession(
            session_id=session_id,
            participant_data={
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                **scratch_data  # Include all scratch data as participant data
            },
            questions_data=[],  # No questions for migrated agent
            responses_data=[],  # No responses for migrated agent
            current_question_index=0,
            status="agent_created",  # Mark as completed with agent created
            agent_path=agent_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(interview_session)
        db.flush()  # Flush to get the session created
        
        # Create agent record
        print("Creating agent record...")
        db_agent = DBAgent(
            agent_id=agent_id,
            session_id=session_id,
            name=agent_name,
            age=age,
            participant_data=scratch_data,
            memory_stream=memory_stream_data,
            scratch_data=scratch_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_agent)
        db.commit()
        
        print(f"✅ Successfully migrated agent:")
        print(f"   - Name: {agent_name}")
        print(f"   - Agent ID: {agent_id}")
        print(f"   - Session ID: {session_id}")
        print(f"   - Memory nodes: {len(nodes_data)}")
        print(f"   - Embeddings count: {len(embeddings_data) if isinstance(embeddings_data, list) else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error migrating agent: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_migration():
    """
    Verify that the migration was successful by checking the database
    """
    db = get_db_session()
    
    try:
        # Count agents in database
        agent_count = db.query(DBAgent).count()
        session_count = db.query(DBInterviewSession).count()
        
        print(f"\n📊 Migration verification:")
        print(f"   - Agents in database: {agent_count}")
        print(f"   - Sessions in database: {session_count}")
        
        # List all agents
        agents = db.query(DBAgent).all()
        for agent in agents:
            print(f"   - Agent: {agent.name} (ID: {agent.agent_id})")
            print(f"     Session: {agent.session_id}")
            print(f"     Memory nodes: {len(agent.memory_stream.get('nodes', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting agent migration from file system to database...")
    print("=" * 60)
    
    # Perform migration
    success = migrate_single_agent_to_database()
    
    if success:
        print("\n" + "=" * 60)
        verify_migration()
        print("\n✅ Migration completed successfully!")
        print("\nThe agent has been moved from the file system to the database.")
        print("You can now interact with it through the web interface.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)