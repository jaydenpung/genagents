'use client';

import { useState, useEffect } from 'react';
import { Agent } from '@/types/interview';
import { interviewApi } from '@/services/api';

interface AgentsListProps {
  onCreateNewAgent: () => void;
  onChatWithAgent: (agentId: string) => void;
}

export default function AgentsList({ onCreateNewAgent, onChatWithAgent }: AgentsListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await interviewApi.listAgents();
      setAgents(response.agents);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load agents');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (dateString === 'Unknown') return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="text-gray-600">Loading agents...</div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Created Agents</h1>
          <p className="text-gray-600">Manage your AI agents created through interviews</p>
        </div>
        <button
          onClick={onCreateNewAgent}
          className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
        >
          Create New Agent
        </button>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadAgents}
            className="mt-2 text-red-700 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {agents.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🤖</div>
          <h3 className="text-xl font-medium text-gray-800 mb-2">No Agents Created Yet</h3>
          <p className="text-gray-600 mb-6">
            Start by creating your first AI agent through the interview process
          </p>
          <button
            onClick={onCreateNewAgent}
            className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
          >
            Create Your First Agent
          </button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-800 mb-1">
                    {agent.name}
                  </h3>
                  <p className="text-gray-600 text-sm">Age: {agent.age}</p>
                </div>
                <div className="text-right">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-lg">
                      {agent.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{formatDate(agent.created_date)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Responses:</span>
                  <span>{agent.total_responses}</span>
                </div>
                <div className="flex justify-between">
                  <span>Agent ID:</span>
                  <span className="font-mono text-xs truncate max-w-24" title={agent.agent_id}>
                    {agent.agent_id}
                  </span>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      // TODO: Add view/interact functionality
                      alert(`Viewing agent: ${agent.name}`);
                    }}
                    className="flex-1 bg-gray-100 text-gray-700 py-2 px-3 rounded text-sm hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => onChatWithAgent(agent.agent_id)}
                    className="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Interact
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {agents.length > 0 && (
        <div className="mt-8 text-center">
          <button
            onClick={loadAgents}
            className="text-gray-600 hover:text-gray-800 underline"
          >
            Refresh List
          </button>
        </div>
      )}
    </div>
  );
}