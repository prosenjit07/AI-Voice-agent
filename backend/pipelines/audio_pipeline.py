"""
Low-latency audio pipeline for Gemini Live API streaming
"""
import asyncio
import logging
import time
from typing import Optional, Callable, Dict, Any, List
from services.gemini_live_service import GeminiLiveService
from services.audio_service import AudioService  
from services.rtvi_service import RTVIService
from schemas.rtvi_schemas import RTVIEventType
from config import get_settings

logger = logging.getLogger(__name__)

class LowLatencyAudioPipeline:
    """Low-latency audio pipeline for direct Gemini Live API streaming"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gemini_service = GeminiLiveService()
        self.audio_service = AudioService()
        self.rtvi_service = RTVIService()
        self.is_running = False
        self.websocket = None
        
        # Performance tracking
        self.audio_chunks_received = 0
        self.audio_chunks_sent = 0
        self.last_audio_time = 0
        self.response_times = []
        
        # Audio buffering for low latency
        self.audio_buffer = asyncio.Queue(maxsize=10)  # Small buffer for low latency
        self.response_buffer = asyncio.Queue(maxsize=5)
        
        # Processing tasks
        self.audio_processor_task = None
        self.response_processor_task = None
        
    async def initialize(self, websocket):
        """Initialize the audio pipeline"""
        self.websocket = websocket
        
        # Register RTVI event handlers
        self._register_rtvi_handlers()
        
        # Initialize services
        await self.rtvi_service.initialize_client({})
        
        logger.info("Low-latency audio pipeline initialized")
        
    def _register_rtvi_handlers(self):
        """Register RTVI event handlers"""
        self.rtvi_service.register_event_handler(RTVIEventType.AUDIO_INPUT, self._handle_audio_input)
        self.rtvi_service.register_event_handler(RTVIEventType.AUDIO_OUTPUT, self._handle_audio_output)
        self.rtvi_service.register_event_handler(RTVIEventType.USER_SPEAKING, self._handle_user_speaking)
        self.rtvi_service.register_event_handler(RTVIEventType.BOT_SPEAKING, self._handle_bot_speaking)
        self.rtvi_service.register_event_handler(RTVIEventType.ERROR, self._handle_error)
        
    async def start(self):
        """Start the audio pipeline"""
        if self.is_running:
            logger.warning("Pipeline already running")
            return
            
        try:
            # Connect to Gemini Live API
            if not await self.gemini_service.connect():
                raise Exception("Failed to connect to Gemini Live API")
            
            # Start processing tasks
            self.audio_processor_task = asyncio.create_task(self._process_audio_input())
            self.response_processor_task = asyncio.create_task(self._process_gemini_responses())
            
            self.is_running = True
            
            # Send ready event
            await self.rtvi_service.set_transport_state("ready")
            await self._send_to_websocket({
                "type": "transport-state-changed",
                "state": "ready"
            })
            
            logger.info("Low-latency audio pipeline started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            await self.stop()
            raise
            
    async def stop(self):
        """Stop the audio pipeline"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Cancel processing tasks
        if self.audio_processor_task:
            self.audio_processor_task.cancel()
        if self.response_processor_task:
            self.response_processor_task.cancel()
            
        # Disconnect from Gemini
        await self.gemini_service.disconnect()
        
        # Clear buffers
        while not self.audio_buffer.empty():
            self.audio_buffer.get_nowait()
        while not self.response_buffer.empty():
            self.response_buffer.get_nowait()
            
        logger.info("Audio pipeline stopped")
        
    async def process_audio_input(self, audio_data: bytes):
        """Process incoming audio data"""
        if not self.is_running:
            return
            
        start_time = time.time()
        self.audio_chunks_received += 1
        
        try:
            # Add to buffer for processing (non-blocking)
            if not self.audio_buffer.full():
                await self.audio_buffer.put(audio_data)
            else:
                # Drop oldest audio if buffer is full (maintain low latency)
                try:
                    self.audio_buffer.get_nowait()
                    await self.audio_buffer.put(audio_data)
                except asyncio.QueueEmpty:
                    pass
                    
        except Exception as e:
            logger.error(f"Error processing audio input: {e}")
            
    async def process_text_input(self, text: str):
        """Process incoming text input"""
        if not self.is_running:
            return
            
        try:
            await self.gemini_service.send_text(text)
            logger.info(f"Sent text to Gemini: {text}")
        except Exception as e:
            logger.error(f"Error sending text: {e}")
            
    async def _process_audio_input(self):
        """Process audio from buffer and send to Gemini"""
        while self.is_running:
            try:
                # Get audio from buffer with timeout
                audio_data = await asyncio.wait_for(
                    self.audio_buffer.get(), 
                    timeout=0.1
                )
                
                # Send to Gemini Live API
                await self.gemini_service.send_audio(audio_data)
                self.audio_chunks_sent += 1
                
            except asyncio.TimeoutError:
                # No audio available, continue
                continue
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                await asyncio.sleep(0.01)
                
    async def _process_gemini_responses(self):
        """Process responses from Gemini Live API"""
        try:
            async for response in self.gemini_service.receive_responses():
                if not self.is_running:
                    break
                    
                # Track response time
                response_time = time.time() - self.last_audio_time
                self.response_times.append(response_time)
                
                # Keep only recent response times (last 100)
                if len(self.response_times) > 100:
                    self.response_times = self.response_times[-100:]
                
                # Send response to WebSocket
                await self._send_to_websocket(response)
                
        except Exception as e:
            logger.error(f"Error processing Gemini responses: {e}")
            await self.rtvi_service.handle_error(f"Gemini response error: {e}")
            
    async def _send_to_websocket(self, data: Dict[str, Any]):
        """Send data to WebSocket"""
        if self.websocket and self.websocket.client_state == "connected":
            try:
                await self.websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                
    async def _handle_audio_input(self, data: Dict[str, Any]):
        """Handle audio input RTVI event"""
        if "audio_data" in data:
            await self.process_audio_input(data["audio_data"])
            
    async def _handle_audio_output(self, data: Dict[str, Any]):
        """Handle audio output RTVI event"""
        await self._send_to_websocket({
            "type": "audio-output",
            "data": data
        })
        
    async def _handle_user_speaking(self, data: Dict[str, Any]):
        """Handle user speaking RTVI event"""
        self.last_audio_time = time.time()
        await self._send_to_websocket({
            "type": "user-speaking",
            "data": data
        })
        
    async def _handle_bot_speaking(self, data: Dict[str, Any]):
        """Handle bot speaking RTVI event"""
        await self._send_to_websocket({
            "type": "bot-speaking", 
            "data": data
        })
        
    async def _handle_error(self, data: Dict[str, Any]):
        """Handle error RTVI event"""
        await self._send_to_websocket({
            "type": "error",
            "data": data
        })
        
    async def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        avg_response_time = 0
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            
        return {
            "is_running": self.is_running,
            "gemini_connected": self.gemini_service.is_connected,
            "audio_chunks_received": self.audio_chunks_received,
            "audio_chunks_sent": self.audio_chunks_sent,
            "buffer_size": self.audio_buffer.qsize(),
            "avg_response_time_ms": avg_response_time * 1000,
            "form_status": self.gemini_service.get_form_status()
        }
        
