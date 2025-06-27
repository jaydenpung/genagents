'use client';

import { useRouter } from 'next/navigation';
import AgentsList from '@/components/AgentsList';

export default function AgentsPage() {
  const router = useRouter();

  const handleCreateNewAgent = () => {
    router.push('/interview');
  };

  const handleChatWithAgent = (agentId: string) => {
    router.push(`/chat/${agentId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <AgentsList 
          onCreateNewAgent={handleCreateNewAgent}
          onChatWithAgent={handleChatWithAgent}
        />
      </div>
    </div>
  );
}