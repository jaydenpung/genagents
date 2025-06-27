'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AgentsList from '@/components/AgentsList';
import { interviewApi } from '@/services/api';

interface InterviewSession {
  session_id: string;
  participant_name: string;
  created_at: string;
  status: string;
  progress: string;
}

export default function AgentsPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [showSessions, setShowSessions] = useState(false);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await interviewApi.listSessions();
      setSessions(response.sessions);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const handleCreateNewAgent = () => {
    router.push('/interview');
  };

  const handleChatWithAgent = (agentId: string) => {
    router.push(`/chat/${agentId}`);
  };

  const handleResumeInterview = (sessionId: string) => {
    router.push(`/interview/${sessionId}`);
  };

  const formatDate = (dateString: string) => {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'agent_created': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Filter active sessions
  const activeSessions = sessions.filter(s => s.status === 'active');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Active Interviews Section */}
        {activeSessions.length > 0 && (
          <div className="max-w-6xl mx-auto mb-8">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-yellow-800 mb-4">
                🔄 Resume Active Interviews
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {activeSessions.map((session) => (
                  <div key={session.session_id} className="bg-white rounded-md p-4 border border-yellow-200">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-gray-800">{session.participant_name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(session.status)}`}>
                        {session.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">Progress: {session.progress}</p>
                    <p className="text-xs text-gray-500 mb-3">Started: {formatDate(session.created_at)}</p>
                    <button
                      onClick={() => handleResumeInterview(session.session_id)}
                      className="w-full bg-yellow-600 text-white py-2 px-3 rounded text-sm hover:bg-yellow-700 transition-colors"
                    >
                      Resume Interview
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Interview Sessions Section */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Interview Sessions</h2>
            <button
              onClick={() => setShowSessions(!showSessions)}
              className="text-blue-600 hover:text-blue-700 underline text-sm"
            >
              {showSessions ? 'Hide' : 'Show'} All Sessions ({sessions.length})
            </button>
          </div>

          {showSessions && (
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
              {isLoadingSessions ? (
                <div className="text-center py-4">
                  <div className="text-gray-600">Loading sessions...</div>
                </div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-4 text-gray-600">
                  No interview sessions found
                </div>
              ) : (
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-md hover:bg-gray-50">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-gray-800">{session.participant_name}</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(session.status)}`}>
                            {session.status}
                          </span>
                          <span className="text-sm text-gray-600">{session.progress}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {formatDate(session.created_at)} • ID: {session.session_id.substring(0, 8)}...
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        {session.status === 'active' && (
                          <button
                            onClick={() => handleResumeInterview(session.session_id)}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                          >
                            Resume
                          </button>
                        )}
                        <button
                          onClick={() => handleResumeInterview(session.session_id)}
                          className="bg-gray-100 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-200 transition-colors"
                        >
                          View
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Agents Section */}
        <AgentsList 
          onCreateNewAgent={handleCreateNewAgent}
          onChatWithAgent={handleChatWithAgent}
        />
      </div>
    </div>
  );
}