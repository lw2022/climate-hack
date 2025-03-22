'use client';

import { useState } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize the Google AI model
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_AI_KEY || '');
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string, id: string }>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      role: 'user' as const,
      content: input,
      id: Date.now().toString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Get response from Google AI
      const result = await model.generateContent(input);
      const response = await result.response;
      const text = response.text();

      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: text,
        id: (Date.now() + 1).toString()
      }]);
    } catch (error) {
      console.error('Error:', error);
      // Handle error appropriately
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-900 shadow'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex space-x-4">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about contracts, negotiations, or carbon credits..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <button
            type="submit"
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
} 