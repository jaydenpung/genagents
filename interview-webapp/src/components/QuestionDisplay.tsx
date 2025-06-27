'use client';

import { useState, useEffect } from 'react';
import { QuestionResponse } from '@/types/interview';

interface QuestionDisplayProps {
  question: QuestionResponse;
  onSubmitResponse: (response: string) => void;
  isLoading: boolean;
}

export default function QuestionDisplay({ question, onSubmitResponse, isLoading }: QuestionDisplayProps) {
  const [response, setResponse] = useState('');
  const [timeLeft, setTimeLeft] = useState(question.time_limit);

  useEffect(() => {
    setTimeLeft(question.time_limit);
    setResponse('');
  }, [question]);

  useEffect(() => {
    if (question.time_limit === 0) {
      // If time_limit is 0, don't start countdown
      return;
    }
    
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !isLoading) {
      // Auto-submit when time runs out
      onSubmitResponse(response.trim());
    }
  }, [timeLeft, question.time_limit, response, onSubmitResponse, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmitResponse(response.trim());
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-500">
            Question {question.question_number + 1} of {question.total_questions + 2}
          </span>
          {question.time_limit > 0 ? (
            <span className={`text-sm font-medium ${timeLeft <= 30 ? 'text-red-600' : 'text-gray-600'}`}>
              Time: {formatTime(timeLeft)}
            </span>
          ) : (
            <span className="text-sm font-medium text-gray-600">
              No time limit
            </span>
          )}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${((question.question_number + 1) / (question.total_questions + 2)) * 100}%` 
            }}
          ></div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          {question.question}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {!question.is_introduction && !question.is_conclusion && (
          <div>
            <label htmlFor="response" className="block text-sm font-medium text-gray-700 mb-2">
              Your Response
            </label>
            <textarea
              id="response"
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
              placeholder="Type your response here..."
              required={false}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Submitting...' : 
           question.is_introduction ? 'Begin Interview' :
           question.is_conclusion ? 'Complete Interview' : 
           'Next Question'}
        </button>
      </form>
    </div>
  );
}