'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ChatInterface from '@/components/ChatInterface';
import { AgentDetails } from '@/types/interview';
import { interviewApi } from '@/services/api';

export default function ChatPage() {
  const router = useRouter();
  const params = useParams();
  const agentId = params.agentId as string;
  
  const [agent, setAgent] = useState<AgentDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadAgent();
  }, [agentId]);

  const loadAgent = async () => {
    if (!agentId) return;

    setIsLoading(true);
    setError('');

    try {
      const agentData = await interviewApi.getAgentDetails(agentId);
      setAgent(agentData);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load agent');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    router.push('/agents');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-600 text-lg">Loading agent...</div>
        </div>
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-600 text-lg mb-4">
            {error || 'Agent not found'}
          </div>
          <button
            onClick={handleBack}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Back to Agents
          </button>
        </div>
      </div>
    );
  }

  return <ChatInterface agent={agent} onBack={handleBack} />;
}