import { ObjectId } from 'mongodb';

export interface Contract {
  _id?: ObjectId;
  title: string;
  description: string;
  status: 'draft' | 'negotiating' | 'active' | 'completed' | 'cancelled';
  startDate: Date;
  endDate: Date;
  value: number;
  currency: string;
  buyer: {
    name: string;
    id: string;
  };
  seller: {
    name: string;
    id: string;
  };
  carbonCredits: {
    amount: number;
    type: string;
    verificationMethod: string;
  };
  documents: {
    id: string;
    type: string;
    url: string;
    createdAt: Date;
  }[];
  createdAt: Date;
  updatedAt: Date;
}

export const ContractSchema = {
  title: { type: String, required: true },
  description: { type: String, required: true },
  status: {
    type: String,
    enum: ['draft', 'negotiating', 'active', 'completed', 'cancelled'],
    default: 'draft'
  },
  startDate: { type: Date, required: true },
  endDate: { type: Date, required: true },
  value: { type: Number, required: true },
  currency: { type: String, required: true },
  buyer: {
    name: { type: String, required: true },
    id: { type: String, required: true }
  },
  seller: {
    name: { type: String, required: true },
    id: { type: String, required: true }
  },
  carbonCredits: {
    amount: { type: Number, required: true },
    type: { type: String, required: true },
    verificationMethod: { type: String, required: true }
  },
  documents: [{
    id: { type: String, required: true },
    type: { type: String, required: true },
    url: { type: String, required: true },
    createdAt: { type: Date, default: Date.now }
  }],
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
}; 