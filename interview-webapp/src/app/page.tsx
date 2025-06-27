'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleGetStarted = () => {
    router.push('/agents');
  };

  const handleStartInterview = () => {
    router.push('/interview');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-6">
            Create Your
            <span className="text-blue-600"> AI Agent</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Transform your thoughts, experiences, and personality into a personalized AI agent 
            through our comprehensive interview process. Build an AI that thinks and responds like you.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={handleGetStarted}
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50 transition-all"
            >
              View My Agents
            </button>
            <button
              onClick={handleStartInterview}
              className="bg-white text-blue-600 border-2 border-blue-600 px-8 py-4 rounded-lg text-lg font-medium hover:bg-blue-50 focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50 transition-all"
            >
              Start New Interview
            </button>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="text-blue-600 text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Personalized</h3>
              <p className="text-gray-600">
                Every agent is unique, built from your personal experiences, values, and thoughts
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="text-blue-600 text-4xl mb-4">💬</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Interactive</h3>
              <p className="text-gray-600">
                Comprehensive interview process covering life experiences, opinions, and perspectives
              </p>
            </div>
            
            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="text-blue-600 text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Intelligent</h3>
              <p className="text-gray-600">
                Advanced AI technology creates agents that respond authentically based on your input
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">How It Works</h2>
          
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-blue-600 font-bold text-xl">1</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Complete Interview</h3>
                <p className="text-gray-600">
                  Answer questions about your life, experiences, and perspectives in a structured interview
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-blue-600 font-bold text-xl">2</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">AI Processing</h3>
                <p className="text-gray-600">
                  Our AI analyzes your responses and creates a personalized agent based on your unique traits
                </p>
              </div>
              
              <div className="text-center">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-blue-600 font-bold text-xl">3</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Interact & Manage</h3>
                <p className="text-gray-600">
                  View, interact with, and manage your AI agents from your personal dashboard
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
