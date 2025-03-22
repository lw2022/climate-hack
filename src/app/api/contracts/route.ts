import { NextResponse } from 'next/server';
import clientPromise from '@/lib/mongodb';
import { Contract } from '@/models/Contract';

export async function GET() {
  try {
    const client = await clientPromise;
    const db = client.db('greenbox');
    const contracts = await db.collection('contracts').find({}).toArray();
    return NextResponse.json(contracts);
  } catch (error) {
    console.error('Error fetching contracts:', error);
    return NextResponse.json({ error: 'Failed to fetch contracts' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const client = await clientPromise;
    const db = client.db('greenbox');
    
    const contract: Omit<Contract, '_id'> = {
      ...body,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    const result = await db.collection('contracts').insertOne(contract);
    return NextResponse.json({ id: result.insertedId });
  } catch (error) {
    console.error('Error creating contract:', error);
    return NextResponse.json({ error: 'Failed to create contract' }, { status: 500 });
  }
} 