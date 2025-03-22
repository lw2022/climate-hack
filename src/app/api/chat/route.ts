import { NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';

export async function POST(request: Request) {
  try {
    const { messages } = await request.json();
    const client = await clientPromise;
    const db = client.db('greenbox');

    // Get the last user message
    const lastUserMessage = messages[messages.length - 1];
    
    // Here you would typically:
    // 1. Process the message with your AI model
    // 2. Query the database for relevant information
    // 3. Generate a response based on the context
    
    // For now, we'll return a simple response
    const response = {
      role: 'assistant',
      content: 'I understand you\'re asking about ' + lastUserMessage.content + '. I can help you with that. What specific information would you like to know?'
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error processing chat message:', error);
    return NextResponse.json(
      { error: 'Failed to process chat message' },
      { status: 500 }
    );
  }
} 