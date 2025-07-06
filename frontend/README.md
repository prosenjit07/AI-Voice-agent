# Voice AI Frontend

A Next.js 14+ frontend application for real-time voice interaction with Gemini Live AI through a FastAPI backend.

## Features

- **Real-time Audio Streaming**: Captures microphone audio and streams to backend via WebSocket
- **Bidirectional Communication**: Plays AI responses in real-time
- **Natural Turn-taking**: Automatically interrupts AI when user starts speaking
- **Voice-controlled Forms**: Fill out forms using voice commands
- **RTVI Protocol**: Compatible with Real-Time Voice Interface protocol
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running FastAPI backend on `localhost:8000`

### Installation

1. Navigate to the frontend directory:
\`\`\`bash
cd frontend
\`\`\`

2. Install dependencies:
\`\`\`bash
npm install
\`\`\`

3. Start the development server:
\`\`\`bash
npm run dev
\`\`\`

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Usage

1. **Voice Stream Tab**: 
   - Click the microphone button to start recording
   - Speak naturally - the AI will respond
   - Start speaking to interrupt AI responses

2. **Voice Form Tab**:
   - Use voice commands to fill form fields:
     - "My name is John Doe"
     - "My email is john@example.com" 
     - "My message is I would like more information"
   - Say "Submit" to submit the form

### Voice Commands

- **Name**: "My name is [name]" or "I am [name]"
- **Email**: "My email is [email]" or "Email is [email]"
- **Message**: "My message is [message]" or "I want to say [message]"
- **Submit**: "Submit" or "Send form" or "Send it"
- **Clear**: "Clear" or "Reset"

## Architecture

- **Next.js 14**: App Router with TypeScript
- **WebSocket Service**: Real-time communication with backend
- **Audio Processor**: Web Audio API for microphone capture and playback
- **RTVI Protocol**: Structured messaging for voice interactions
- **Tailwind CSS**: Responsive styling
- **shadcn/ui**: UI component library

## Configuration

The WebSocket connection defaults to `ws://localhost:8000/ws`. To change this, modify the URL in `utils/ws.ts`:

\`\`\`typescript
constructor(private url = "ws://your-backend-url/ws") {}
\`\`\`

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support  
- Safari: Full support (iOS 14.5+)

Requires HTTPS in production for microphone access.
