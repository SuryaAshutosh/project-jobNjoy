# jobSee Frontend

A modern React frontend for the jobSee platform, built with Vite, TypeScript, and Tailwind CSS.

## Features

- Authentication (Login/Register)
- Job listings with search and filtering
- Job application tracking
- Resume upload and parsing
- Dashboard with analytics
- Responsive design with dark mode support
- Protected routes and user context

## Tech Stack

- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
5. Start the development server:
   ```bash
   npm run dev
   ```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Project Structure

```
src/
├── components/     # Reusable UI components
├── contexts/       # React context providers
├── pages/          # Page components
├── services/       # API services
├── types/          # TypeScript types
└── App.tsx         # Main app component
```

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Development

The frontend is designed to work with the jobSee backend API. Make sure the backend is running and accessible at the configured API URL.

## Deployment

To deploy the frontend:

1. Build the project:
   ```bash
   npm run build
   ```
2. The built files will be in the `dist/` directory, ready for deployment to any static hosting service.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is proprietary and confidential. All rights reserved.