# Greenbox - Carbon Marketplace Platform

Greenbox is an end-to-end carbon marketplace negotiation, audit, and pricing information platform. It helps green energy companies manage complex workflows for partnering with industrials that incorporate green technologies into their operations to generate and sell green contracts to climate-aware Fortune 500s.

## Features

- AI-powered chatbot interface for contract management and negotiation
- Contract portfolio management dashboard
- High-level analytics dashboard
- Document management system for PPA agreements
- NoSQL database for flexible data storage

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: Next.js API Routes
- **Database**: MongoDB
- **UI Framework**: Tailwind CSS
- **State Management**: React Query
- **Document Management**: MongoDB GridFS

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

Create a `.env.local` file with the following variables:

```
MONGODB_URI=your_mongodb_uri
```

## Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── chat/              # AI chatbot interface
│   ├── portfolio/         # Contract portfolio view
│   └── dashboard/         # Analytics dashboard
├── components/            # Reusable components
├── lib/                   # Utility functions and configurations
├── models/               # Database models
└── types/                # TypeScript type definitions
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

MIT