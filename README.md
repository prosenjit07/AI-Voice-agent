# Voice AI Assistant

A real-time voice-controlled AI assistant with form filling capabilities, built with FastAPI backend and Next.js frontend.

## 🚀 Features

- **Real-time Voice Interaction**: Speak naturally with the AI assistant
- **Voice-Controlled Form Filling**: Fill forms using voice commands
- **Tab Switching**: Navigate between different sections using voice
- **Speech Recognition**: Built-in browser speech recognition for voice input
- **WebSocket Communication**: Real-time bidirectional communication
- **Modern UI**: Clean, responsive interface with Tailwind CSS
- **Audio Processing**: Real-time audio capture and playback

## 🏗️ Architecture

### Backend (FastAPI)
- **WebSocket Server**: Handles real-time voice communication
- **Voice Command Processing**: Parses and executes voice commands
- **AI Integration**: Gemini AI for natural language processing
- **Audio Pipeline**: Processes audio streams in real-time

### Frontend (Next.js)
- **Voice Interface**: Microphone controls and speech recognition
- **Form Components**: Voice-controlled form filling
- **WebSocket Client**: Real-time communication with backend
- **Audio Processing**: Client-side audio capture and playback

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Microphone access in browser
- Google Gemini API key (for AI features)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd voice-agent
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt
# or if using uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
```

## 🚀 Running the Application

### 1. Start the Backend
```bash
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
# or
yarn dev
```

### 3. Access the Application
Open your browser and navigate to `http://localhost:3000`

## 🎤 Voice Commands

### General Navigation
- "Switch to [tab name]" - Navigate between tabs
- "Go to voice form" - Switch to form tab
- "Go to chat" - Switch to chat tab

### Form Filling Commands
- "My name is [name]" - Fill the name field
- "My email is [email]" - Fill the email field
- "My message is [message]" - Fill the message field
- "Submit" or "Send form" - Submit the form
- "Clear" or "Reset" - Clear all form fields

### General Interaction
- "Hello" - Start a conversation
- "What can you do?" - Get help
- "Stop listening" - Stop voice recognition

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest test_voice_form_commands.py
```

### Manual Testing
1. Open the application in your browser
2. Click the microphone button to start voice input
3. Speak voice commands clearly
4. Verify form fields are filled automatically
5. Test tab switching with voice commands

## 📁 Project Structure

```
voice-agent/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── routes/
│   │   └── websocket.py        # WebSocket route handlers
│   ├── services/
│   │   ├── audio_service.py    # Audio processing service
│   │   ├── gemini_service.py   # AI integration service
│   │   └── rtvi_service.py     # Real-time voice interface
│   ├── schemas/
│   │   ├── audio_schemas.py    # Audio data schemas
│   │   └── rtvi_schemas.py     # Voice command schemas
│   └── utils/
│       └── logger.py           # Logging utilities
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main application page
│   │   └── layout.tsx          # Root layout
│   ├── components/
│   │   ├── mic-stream.tsx      # Microphone stream component
│   │   ├── voice-form.tsx      # Voice-controlled form
│   │   └── ui/                 # Reusable UI components
│   └── utils/
│       ├── audio-processor.ts  # Audio processing utilities
│       └── ws.ts               # WebSocket client service
└── README.md
```

## 🔧 Configuration

### Environment Variables (Backend)
Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

### Frontend Configuration
The frontend automatically connects to `ws://localhost:8000/ws` for WebSocket communication.

## 🐛 Troubleshooting

### Common Issues

1. **Microphone Not Working**
   - Ensure browser has microphone permissions
   - Check if microphone is not being used by other applications
   - Try refreshing the page

2. **WebSocket Connection Failed**
   - Verify backend is running on port 8000
   - Check browser console for connection errors
   - Ensure no firewall blocking WebSocket connections

3. **Voice Commands Not Recognized**
   - Speak clearly and at normal volume
   - Check browser speech recognition support
   - Verify microphone is working in other applications

4. **Form Fields Not Filling**
   - Check browser console for errors
   - Verify WebSocket connection is active
   - Ensure voice commands match expected patterns

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in the backend `.env` file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) for speech recognition

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem

---

**Note**: This application requires a modern browser with Web Speech API support and microphone access permissions. 