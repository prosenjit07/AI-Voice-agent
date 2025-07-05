"""
Gemini Live API service for real-time audio streaming
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from google import genai
from google.genai import types
import os
from config import get_settings
from schemas.audio_schemas import AudioData, AudioFormat

logger = logging.getLogger(__name__)

class GeminiLiveService:
    """Service for interacting with Gemini Live API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.session = None
        self.is_connected = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            api_key = self.settings.gemini_api_key
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
            
            self.client = genai.Client(api_key=api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    async def connect(self) -> bool:
        """Connect to Gemini Live API"""
        try:
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self.settings.gemini_voice
                        }
                    }
                },
                "realtime_input_config": {
                    "automatic_activity_detection": {
                        "end_of_speech_sensitivity": 0.5,
                        "start_of_speech_sensitivity": 0.3
                    }
                }
            }
            
            self.session = await self.client.aio.live.connect(
                model=self.settings.gemini_model,
                config=config
            )
            
            self.is_connected = True
            logger.info("Connected to Gemini Live API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Gemini Live API"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_connected = False
            logger.info("Disconnected from Gemini Live API")
        except Exception as e:
            logger.error(f"Error disconnecting from Gemini Live API: {e}")
    
    async def send_audio(self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """Send audio data to Gemini Live API"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            await self.session.send_realtime_input(
                audio={"data": audio_data, "mime_type": mime_type}
            )
            
        except Exception as e:
            logger.error(f"Error sending audio to Gemini: {e}")
            raise
    
    async def send_text(self, text: str, turn_complete: bool = True):
        """Send text message to Gemini Live API"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            await self.session.send_client_content(
                turns=[{"role": "user", "parts": [{"text": text}]}],
                turn_complete=turn_complete
            )
            
        except Exception as e:
            logger.error(f"Error sending text to Gemini: {e}")
            raise
    
    async def receive_responses(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Receive responses from Gemini Live API"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            async for response in self.session.receive():
                try:
                    # Handle server content
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'model_turn') and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    # Audio response
                                    yield {
                                        "type": "audio",
                                        "data": part.inline_data.data,
                                        "mime_type": part.inline_data.mime_type if hasattr(part.inline_data, 'mime_type') else "audio/pcm"
                                    }
                                elif hasattr(part, 'text') and part.text:
                                    # Text response
                                    yield {
                                        "type": "text",
                                        "data": part.text
                                    }
                    
                    # Handle turn complete
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            yield {
                                "type": "turn_complete",
                                "data": True
                            }
                            
                except Exception as e:
                    logger.error(f"Error processing Gemini response: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error receiving responses from Gemini: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the service is healthy"""
        try:
            return self.is_connected and self.session is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
