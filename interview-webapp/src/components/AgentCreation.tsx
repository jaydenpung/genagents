'use client';

import React from 'react';
import { AgentCreationResponse } from '@/types/interview';

interface AgentCreationProps {
  sessionId: string;
  onCreateAgent: () => void;
  agentResult?: AgentCreationResponse;
  isLoading: boolean;
  error?: string;
}

export default function AgentCreation({ 
  onCreateAgent, 
  agentResult, 
  isLoading, 
  error 
}: AgentCreationProps) {
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Interview Complete!</h2>
      
      {!agentResult && !error && (
        <div className="text-center">
          <p className="text-gray-600 mb-6">
            Your interview has been completed successfully. Now we can create your personalized agent based on your responses.
          </p>
          <button
            onClick={onCreateAgent}
            disabled={isLoading}
            className="bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating Agent...' : 'Create My Agent'}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <h3 className="text-red-800 font-medium mb-2">Error Creating Agent</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={onCreateAgent}
            disabled={isLoading}
            className="mt-3 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
          >
            {isLoading ? 'Retrying...' : 'Try Again'}
          </button>
        </div>
      )}

      {agentResult && (
        <div className="bg-green-50 border border-green-200 rounded-md p-6">
          <h3 className="text-green-800 font-bold text-lg mb-4">✅ Agent Created Successfully!</h3>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Session ID:</span>
              <span className="font-mono text-gray-800">{agentResult.session_id}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Agent Path:</span>
              <span className="font-mono text-gray-800 break-all">{agentResult.agent_path}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Total Responses:</span>
              <span className="text-gray-800">{agentResult.total_responses}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Memory Nodes:</span>
              <span className="text-gray-800">{agentResult.memory_nodes}</span>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-white rounded border">
            <p className="text-gray-700">{agentResult.message}</p>
          </div>

          <div className="mt-6 flex space-x-3">
            <button
              onClick={() => window.location.href = '/agents'}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              View All Agents
            </button>
            <button
              onClick={() => window.location.href = '/interview'}
              className="bg-white text-blue-600 border border-blue-600 py-2 px-4 rounded-md hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Start New Interview
            </button>
          </div>
        </div>
      )}
    </div>
  );
}