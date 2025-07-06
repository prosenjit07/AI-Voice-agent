"""
FastAPI backend for real-time audio streaming with Pipecat and Gemini Live API
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.websocket import websocket_router
from utils.logger import setup_logger
from config import get_settings

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting FastAPI application")
    yield
    logger.info("Shutting down FastAPI application")

# Create FastAPI application
app = FastAPI(
    title="Real-Time Audio Streaming API",
    description="FastAPI backend for real-time audio streaming using Pipecat and Gemini Live API with RTVI protocol support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(websocket_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with test interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Audio Streaming API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .card { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Real-Time Audio Streaming API</h1>
        <div class="card">
            <h2>API Information</h2>
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Status:</strong> Active</p>
            <p><strong>WebSocket Endpoint:</strong> /ws</p>
        </div>
        
        <div class="card">
            <h2>Test Interface</h2>
            <p>Test the WebSocket connection and RTVI protocol:</p>
            <a href="/static/index.html" class="btn">Open Test Client</a>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <ul>
                <li><strong>GET /health</strong> - Health check</li>
                <li><strong>WS /ws</strong> - WebSocket audio streaming</li>
                <li><strong>GET /ws/connections</strong> - Active connections</li>
                <li><strong>POST /ws/broadcast</strong> - Broadcast message</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Features</h2>
            <ul>
                <li>Real-time audio streaming</li>
                <li>RTVI protocol support</li>
                <li>Gemini Live API integration</li>
                <li>Voice activity detection</li>
                <li>WebSocket connection management</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5050,
        reload=True,
        log_level="info"
    )
