'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import InterviewForm from '@/components/InterviewForm';
import QuestionDisplay from '@/components/QuestionDisplay';
import AgentCreation from '@/components/AgentCreation';
import { interviewApi } from '@/services/api';
import { StartInterviewRequest, QuestionResponse, AgentCreationResponse } from '@/types/interview';

type InterviewState = 'form' | 'interview' | 'completed' | 'agent-creation';

export default function InterviewPage() {
  const router = useRouter();
  const [state, setState] = useState<InterviewState>('form');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<QuestionResponse | null>(null);
  const [agentResult, setAgentResult] = useState<AgentCreationResponse | null>(null);

  const handleStartInterview = async (data: StartInterviewRequest) => {
    setIsLoading(true);
    setError('');

    try {
      const question = await interviewApi.startInterview(data);
      setCurrentQuestion(question);
      setState('interview');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to start interview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitResponse = async (response: string) => {
    if (!currentQuestion) return;

    setIsLoading(true);
    setError('');

    try {
      const result = await interviewApi.submitResponse({
        session_id: currentQuestion.session_id,
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
    if (!currentQuestion) return;

    setIsLoading(true);
    setError('');

    try {
      const result = await interviewApi.finalizeAgent(currentQuestion.session_id);
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <div className="text-center flex-1">
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              Generative Agent Interview
            </h1>
            <p className="text-gray-600">
              Complete the interview to create your personalized AI agent
            </p>
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

        {state === 'form' && (
          <InterviewForm 
            onStartInterview={handleStartInterview}
            isLoading={isLoading}
          />
        )}

        {state === 'interview' && currentQuestion && (
          <QuestionDisplay
            question={currentQuestion}
            onSubmitResponse={handleSubmitResponse}
            isLoading={isLoading}
          />
        )}

        {(state === 'completed' || state === 'agent-creation') && currentQuestion && (
          <AgentCreation
            sessionId={currentQuestion.session_id}
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