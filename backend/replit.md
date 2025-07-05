# Real-Time Audio Streaming with Gemini Live API

## Overview

This is a FastAPI-based real-time audio streaming application that integrates with Google's Gemini Live API for conversational AI. The system processes audio streams in real-time, transcribes speech, generates AI responses, and synthesizes speech back to users through WebSocket connections. It implements the RTVI (Real-Time Voice Interface) protocol for standardized communication and uses the Pipecat framework for audio pipeline orchestration.

## System Architecture

### Backend Architecture
- **FastAPI**: Modern Python web framework serving as the main application server
- **WebSocket-based Communication**: Real-time bidirectional communication between clients and server
- **Service-Oriented Architecture**: Modular design with separate services for different functionalities
- **Pipecat Framework**: Audio pipeline orchestration for processing streams
- **RTVI Protocol**: Standardized protocol for real-time voice interface communication

### Audio Processing Pipeline
The system uses a sophisticated audio processing pipeline that handles:
- Real-time audio streaming via WebSockets
- Voice Activity Detection (VAD) using Silero VAD
- Audio format conversion and sample rate adjustments
- Buffering and chunking for optimal performance

### AI Integration
- **Gemini Live API**: Google's conversational AI service for real-time audio processing
- **Speech-to-Text**: Real-time transcription of user speech
- **Text-to-Speech**: AI-generated speech synthesis
- **Voice Configuration**: Customizable voice settings (default: "Aoede")

## Key Components

### Core Services
1. **GeminiLiveService** (`services/gemini_service.py`): Handles communication with Google's Gemini Live API
2. **AudioService** (`services/audio_service.py`): Manages audio processing, format conversion, and streaming
3. **RTVIService** (`services/rtvi_service.py`): Implements RTVI protocol for standardized communication
4. **AudioPipeline** (`pipelines/audio_pipeline.py`): Orchestrates the complete audio processing pipeline

### API Layer
- **WebSocket Router** (`routes/websocket.py`): Handles real-time WebSocket connections
- **Connection Manager**: Manages multiple concurrent WebSocket connections
- **CORS Configuration**: Cross-origin resource sharing for web clients

### Data Models
- **Audio Schemas** (`schemas/audio_schemas.py`): Defines audio-related data structures
- **RTVI Schemas** (`schemas/rtvi_schemas.py`): Implements RTVI protocol message formats

### Configuration Management
- **Settings System** (`config.py`): Centralized configuration using Pydantic
- **Environment Variables**: Secure API key management
- **Caching**: LRU cache for settings optimization

## Data Flow

1. **Client Connection**: Client establishes WebSocket connection
2. **Audio Input**: Real-time audio data streaming from client
3. **Voice Activity Detection**: VAD analyzer detects speech segments
4. **Audio Processing**: Format conversion and buffering
5. **AI Processing**: Gemini Live API processes audio and generates responses
6. **Speech Synthesis**: AI responses converted to audio
7. **Audio Output**: Processed audio streamed back to client
8. **RTVI Events**: Standardized events for state management and communication

## External Dependencies

### Required APIs
- **Google Gemini Live API**: Requires `GEMINI_API_KEY` environment variable
- **Audio Processing Libraries**: audioop for format conversion
- **WebSocket Support**: Built-in FastAPI WebSocket support

### Python Packages
- **FastAPI**: Web framework and WebSocket support
- **Pipecat**: Audio pipeline framework
- **Google GenAI**: Official Google AI client library
- **Pydantic**: Data validation and settings management
- **Silero VAD**: Voice activity detection

### Optional Integrations
- **ElevenLabs TTS**: Alternative text-to-speech service
- **Deepgram STT**: Alternative speech-to-text service

## Deployment Strategy

### Configuration
- Environment-based configuration with `.env` file support
- Configurable audio parameters (sample rates, formats, buffer sizes)
- Scalable WebSocket connection management (max 100 concurrent connections)
- Session timeout management (10-minute default)

### Performance Considerations
- Async/await pattern for non-blocking operations
- Connection pooling for WebSocket management
- Audio buffering for smooth streaming
- Efficient memory management with queues

### Production Readiness
- Comprehensive logging system
- Error handling and graceful degradation
- CORS configuration for web deployment
- Configurable timeout and connection limits

## Changelog

```
Changelog:
- July 05, 2025. Initial setup - Complete FastAPI backend with real-time audio streaming
- July 05, 2025. Project structure created with organized folders (routes, services, pipelines, schemas)
- July 05, 2025. WebSocket /ws endpoint implemented with RTVI protocol support
- July 05, 2025. Gemini Live API integration configured and ready
- July 05, 2025. Audio processing pipeline with voice activity detection
- July 05, 2025. Server running successfully on port 5000
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```