'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import QuestionDisplay from '@/components/QuestionDisplay';
import AgentCreation from '@/components/AgentCreation';
import { interviewApi } from '@/services/api';
import { QuestionResponse, AgentCreationResponse, InterviewSession } from '@/types/interview';

type ResumeState = 'loading' | 'interview' | 'completed' | 'agent-creation' | 'error';

export default function ResumeInterviewPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;

  const [state, setState] = useState<ResumeState>('loading');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<QuestionResponse | null>(null);
  const [agentResult, setAgentResult] = useState<AgentCreationResponse | null>(null);
  const [sessionInfo, setSessionInfo] = useState<InterviewSession | null>(null);

  // Load the session and current question on mount
  useEffect(() => {
    const loadSession = async () => {
      try {
        setState('loading');
        
        // Get session info
        const session = await interviewApi.getSession(sessionId);
        setSessionInfo(session);

        // Check session status
        if (session.status === 'completed') {
          setState('completed');
        } else if (session.status === 'agent_created') {
          setState('agent-creation');
        } else if (session.status === 'active') {
          // Get current question
          const question = await interviewApi.getCurrentQuestion(sessionId);
          setCurrentQuestion(question);
          setState('interview');
        } else {
          setError(`Interview session has status: ${session.status}`);
          setState('error');
        }
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Failed to load interview session');
        setState('error');
      }
    };

    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  const handleSubmitResponse = async (response: string) => {
    if (!currentQuestion) return;

    setIsLoading(true);
    setError('');

    try {
      const result = await interviewApi.submitResponse({
        session_id: sessionId,
        response
      });

      // Check if interview is completed
      if ('ready_for_agent_creation' in result && result.ready_for_agent_creation) {
        setState('completed');
      } else {
        // It's the next question
        setCurrentQuestion(result as QuestionResponse);
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to submit response');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    setIsLoading(true);
    setError('');

    try {
      const result = await interviewApi.finalizeAgent(sessionId);
      setAgentResult(result);
      setState('agent-creation');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to create agent');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToAgents = () => {
    router.push('/agents');
  };

  const handleNewInterview = () => {
    router.push('/interview');
  };

  if (state === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading interview session...</p>
          </div>
        </div>
      </div>
    );
  }

  if (state === 'error') {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-md p-6 text-center">
              <h2 className="text-xl font-semibold text-red-800 mb-2">
                Unable to Load Interview
              </h2>
              <p className="text-red-600 mb-4">{error}</p>
              <div className="space-x-4">
                <button
                  onClick={handleNewInterview}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Start New Interview
                </button>
                <button
                  onClick={handleBackToAgents}
                  className="text-gray-600 hover:text-gray-800 underline"
                >
                  Back to Agents
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <div className="text-center flex-1">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Resume Interview
            </h1>
            {sessionInfo && (
              <p className="text-gray-600">
                Continuing interview for {sessionInfo.participant.first_name} {sessionInfo.participant.last_name}
                <br />
                <span className="text-sm text-gray-500">
                  Progress: {sessionInfo.responses.length}/{sessionInfo.total_questions} questions completed
                </span>
              </p>
            )}
          </div>
          <button
            onClick={handleBackToAgents}
            className="text-gray-600 hover:text-gray-800 underline"
          >
            ← Back to Agents
          </button>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {state === 'interview' && currentQuestion && (
          <QuestionDisplay
            question={currentQuestion}
            onSubmitResponse={handleSubmitResponse}
            isLoading={isLoading}
          />
        )}

        {(state === 'completed' || state === 'agent-creation') && (
          <AgentCreation
            sessionId={sessionId}
            onCreateAgent={handleCreateAgent}
            agentResult={agentResult || undefined}
            isLoading={isLoading}
            error={error}
          />
        )}
      </div>
    </div>
  );
}