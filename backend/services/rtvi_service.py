"""
RTVI protocol service implementation
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from schemas.rtvi_schemas import (
    RTVIMessage, RTVIEventType, RTVITransportState, 
    RTVITransportStateMessage, RTVITranscriptionMessage,
    RTVISpeakingMessage, RTVIErrorMessage, RTVIAudioMessage,
    RTVIClientConfig, RTVIServiceConfig
)
from config import get_settings

logger = logging.getLogger(__name__)

class RTVIService:
    """RTVI protocol service for standardized communication"""
    
    def __init__(self):
        self.settings = get_settings()
        self.transport_state = RTVITransportState.DISCONNECTED
        self.event_handlers: Dict[RTVIEventType, List[Callable]] = {}
        self.client_config: Optional[RTVIClientConfig] = None
        self.session_id: Optional[str] = None
        self.is_user_speaking = False
        self.is_bot_speaking = False
        
    def register_event_handler(self, event_type: RTVIEventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event: {event_type}")
    
    def unregister_event_handler(self, event_type: RTVIEventType, handler: Callable):
        """Unregister an event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered handler for event: {event_type}")
    
    async def emit_event(self, event_type: RTVIEventType, data: Dict[str, Any] = None):
        """Emit an RTVI event"""
        try:
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")
    
    async def set_transport_state(self, state: RTVITransportState):
        """Set transport state and emit event"""
        try:
            if self.transport_state != state:
                old_state = self.transport_state
                self.transport_state = state
                
                logger.info(f"Transport state changed: {old_state} -> {state}")
                
                # Emit transport state change event
                await self.emit_event(
                    RTVIEventType.TRANSPORT_STATE_CHANGED,
                    {"state": state, "previous_state": old_state}
                )
                
        except Exception as e:
            logger.error(f"Error setting transport state: {e}")
    
    async def initialize_client(self, config: Dict[str, Any]) -> RTVIClientConfig:
        """Initialize RTVI client with configuration"""
        try:
            # Parse and validate client configuration
            self.client_config = RTVIClientConfig(**config)
            
            # Set initial transport state
            await self.set_transport_state(RTVITransportState.CONNECTING)
            
            logger.info("RTVI client initialized successfully")
            return self.client_config
            
        except Exception as e:
            logger.error(f"Error initializing RTVI client: {e}")
            await self.set_transport_state(RTVITransportState.ERROR)
            raise
    
    async def handle_client_ready(self):
        """Handle client ready state"""
        try:
            await self.set_transport_state(RTVITransportState.READY)
            await self.emit_event(RTVIEventType.CLIENT_READY)
            logger.info("RTVI client ready")
        except Exception as e:
            logger.error(f"Error handling client ready: {e}")
    
    async def handle_audio_input(self, audio_data: bytes, format: str = "pcm", sample_rate: int = 16000):
        """Handle incoming audio data"""
        try:
            # Create audio message
            audio_message = RTVIAudioMessage(
                type=RTVIEventType.AUDIO_INPUT,
                audio_data=audio_data,
                format=format,
                sample_rate=sample_rate,
                timestamp=datetime.now().timestamp()
            )
            
            # Emit audio input event
            await self.emit_event(
                RTVIEventType.AUDIO_INPUT,
                {
                    "audio_data": audio_data,
                    "format": format,
                    "sample_rate": sample_rate,
                    "size": len(audio_data)
                }
            )
            
            return audio_message
            
        except Exception as e:
            logger.error(f"Error handling audio input: {e}")
            raise
    
    async def handle_audio_output(self, audio_data: bytes, format: str = "pcm", sample_rate: int = 24000):
        """Handle outgoing audio data"""
        try:
            # Create audio message
            audio_message = RTVIAudioMessage(
                type=RTVIEventType.AUDIO_OUTPUT,
                audio_data=audio_data,
                format=format,
                sample_rate=sample_rate,
                timestamp=datetime.now().timestamp()
            )
            
            # Emit audio output event
            await self.emit_event(
                RTVIEventType.AUDIO_OUTPUT,
                {
                    "audio_data": audio_data,
                    "format": format,
                    "sample_rate": sample_rate,
                    "size": len(audio_data)
                }
            )
            
            return audio_message
            
        except Exception as e:
            logger.error(f"Error handling audio output: {e}")
            raise
    
    async def handle_user_transcription(self, text: str, is_final: bool = False, confidence: float = None):
        """Handle user transcription"""
        try:
            transcription_message = RTVITranscriptionMessage(
                type=RTVIEventType.USER_TRANSCRIPTION,
                text=text,
                is_final=is_final,
                confidence=confidence,
                timestamp=datetime.now().timestamp()
            )
            
            await self.emit_event(
                RTVIEventType.USER_TRANSCRIPTION,
                {
                    "text": text,
                    "is_final": is_final,
                    "confidence": confidence
                }
            )
            
            return transcription_message
            
        except Exception as e:
            logger.error(f"Error handling user transcription: {e}")
            raise
    
    async def handle_bot_transcription(self, text: str, is_final: bool = False, confidence: float = None):
        """Handle bot transcription"""
        try:
            transcription_message = RTVITranscriptionMessage(
                type=RTVIEventType.BOT_TRANSCRIPTION,
                text=text,
                is_final=is_final,
                confidence=confidence,
                timestamp=datetime.now().timestamp()
            )
            
            await self.emit_event(
                RTVIEventType.BOT_TRANSCRIPTION,
                {
                    "text": text,
                    "is_final": is_final,
                    "confidence": confidence
                }
            )
            
            return transcription_message
            
        except Exception as e:
            logger.error(f"Error handling bot transcription: {e}")
            raise
    
    async def handle_user_speaking(self, is_speaking: bool):
        """Handle user speaking state"""
        try:
            if self.is_user_speaking != is_speaking:
                self.is_user_speaking = is_speaking
                
                speaking_message = RTVISpeakingMessage(
                    type=RTVIEventType.USER_SPEAKING,
                    is_speaking=is_speaking,
                    speaker="user",
                    timestamp=datetime.now().timestamp()
                )
                
                await self.emit_event(
                    RTVIEventType.USER_SPEAKING,
                    {
                        "is_speaking": is_speaking,
                        "speaker": "user"
                    }
                )
                
                return speaking_message
                
        except Exception as e:
            logger.error(f"Error handling user speaking: {e}")
            raise
    
    async def handle_bot_speaking(self, is_speaking: bool):
        """Handle bot speaking state"""
        try:
            if self.is_bot_speaking != is_speaking:
                self.is_bot_speaking = is_speaking
                
                speaking_message = RTVISpeakingMessage(
                    type=RTVIEventType.BOT_SPEAKING,
                    is_speaking=is_speaking,
                    speaker="bot",
                    timestamp=datetime.now().timestamp()
                )
                
                await self.emit_event(
                    RTVIEventType.BOT_SPEAKING,
                    {
                        "is_speaking": is_speaking,
                        "speaker": "bot"
                    }
                )
                
                return speaking_message
                
        except Exception as e:
            logger.error(f"Error handling bot speaking: {e}")
            raise
    
    async def handle_error(self, error: str, code: int = None):
        """Handle error events"""
        try:
            error_message = RTVIErrorMessage(
                error=error,
                code=code,
                timestamp=datetime.now().timestamp()
            )
            
            await self.emit_event(
                RTVIEventType.ERROR,
                {
                    "error": error,
                    "code": code
                }
            )
            
            logger.error(f"RTVI Error: {error} (Code: {code})")
            return error_message
            
        except Exception as e:
            logger.error(f"Error handling error event: {e}")
            raise
    
    def create_rtvi_message(self, event_type: RTVIEventType, data: Dict[str, Any] = None) -> RTVIMessage:
        """Create a standardized RTVI message"""
        try:
            return RTVIMessage(
                type=event_type,
                timestamp=datetime.now().timestamp(),
                data=data or {}
            )
        except Exception as e:
            logger.error(f"Error creating RTVI message: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect and cleanup"""
        try:
            await self.set_transport_state(RTVITransportState.DISCONNECTED)
            self.event_handlers.clear()
            self.client_config = None
            self.session_id = None
            logger.info("RTVI service disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting RTVI service: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current RTVI service status"""
        return {
            "transport_state": self.transport_state,
            "is_user_speaking": self.is_user_speaking,
            "is_bot_speaking": self.is_bot_speaking,
            "session_id": self.session_id,
            "client_config": self.client_config.dict() if self.client_config else None
        }
