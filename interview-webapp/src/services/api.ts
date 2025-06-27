import axios from 'axios';
import {
  StartInterviewRequest,
  SubmitResponseRequest,
  QuestionResponse,
  AgentCreationResponse,
  InterviewSession,
  Agent,
  AgentDetails,
  ChatRequest,
  ChatResponse
} from '@/types/interview';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const interviewApi = {
  startInterview: async (data: StartInterviewRequest): Promise<QuestionResponse> => {
    const response = await api.post('/interview/start', data);
    return response.data;
  },

  getCurrentQuestion: async (sessionId: string): Promise<QuestionResponse> => {
    const response = await api.get(`/interview/${sessionId}/question`);
    return response.data;
  },

  submitResponse: async (data: SubmitResponseRequest): Promise<QuestionResponse | { ready_for_agent_creation: boolean; message: string; session_id: string; total_responses: number }> => {
    const response = await api.post('/interview/response', data);
    return response.data;
  },

  finalizeAgent: async (sessionId: string): Promise<AgentCreationResponse> => {
    const response = await api.post(`/interview/${sessionId}/finalize`);
    return response.data;
  },

  getSession: async (sessionId: string): Promise<InterviewSession> => {
    const response = await api.get(`/interview/${sessionId}`);
    return response.data;
  },

  listSessions: async (): Promise<{ sessions: Array<{ session_id: string; participant_name: string; created_at: string; status: string; progress: string }> }> => {
    const response = await api.get('/interview/sessions');
    return response.data;
  },

  listAgents: async (): Promise<{ agents: Agent[] }> => {
    const response = await api.get('/agents');
    return response.data;
  },

  getAgentDetails: async (agentId: string): Promise<AgentDetails> => {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  },

  chatWithAgent: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post(`/agents/${data.agent_id}/chat`, data);
    return response.data;
  }
};