export interface StartInterviewRequest {
  first_name: string;
  last_name: string;
  age: string;
  additional_info?: Record<string, string>;
}

export interface SubmitResponseRequest {
  session_id: string;
  response: string;
}

export interface QuestionResponse {
  session_id: string;
  question_number: number;
  total_questions: number;
  question: string;
  time_limit: number;
  is_introduction?: boolean;
  is_conclusion?: boolean;
}

export interface AgentCreationResponse {
  session_id: string;
  agent_path: string;
  total_responses: number;
  memory_nodes: number;
  message: string;
}

export interface InterviewSession {
  session_id: string;
  participant: Record<string, string>;
  current_question_index: number;
  total_questions: number;
  responses: Array<{
    question_number: number;
    question: string;
    response: string;
    timestamp: number;
  }>;
  created_at: string;
  status: string;
}

export interface Agent {
  agent_id: string;
  name: string;
  age: string;
  created_date: string;
  total_responses: number;
  agent_path: string;
  session_id: string;
}

export interface AgentDetails extends Agent {
  participant: Record<string, string>;
  status: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent';
  message: string;
  timestamp: string;
  agent_name?: string;
}

export interface ChatRequest {
  agent_id: string;
  message: string;
}

export interface ChatResponse {
  agent_id: string;
  agent_name: string;
  response: string;
  timestamp: string;
}