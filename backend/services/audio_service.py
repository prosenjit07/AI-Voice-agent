"""
Audio processing service
"""
import asyncio
import logging
from typing import Optional, AsyncGenerator, Callable
import audioop
from schemas.audio_schemas import AudioData, AudioFormat, AudioStreamConfig
from config import get_settings

logger = logging.getLogger(__name__)

class AudioService:
    """Service for audio processing and streaming"""
    
    def __init__(self):
        self.settings = get_settings()
        self.is_recording = False
        self.is_playing = False
        self.audio_buffer = asyncio.Queue()
        self.output_buffer = asyncio.Queue()
        
    async def convert_audio_format(
        self, 
        audio_data: bytes, 
        from_rate: int, 
        to_rate: int,
        from_channels: int = 1,
        to_channels: int = 1
    ) -> bytes:
        """Convert audio format and sample rate"""
        try:
            # Convert sample rate if needed
            if from_rate != to_rate:
                audio_data = audioop.ratecv(
                    audio_data, 2, from_channels, from_rate, to_rate, None
                )[0]
            
            # Convert channels if needed
            if from_channels != to_channels:
                if from_channels == 1 and to_channels == 2:
                    audio_data = audioop.tostereo(audio_data, 2, 1, 1)
                elif from_channels == 2 and to_channels == 1:
                    audio_data = audioop.tomono(audio_data, 2, 1, 1)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            raise
    
    async def process_input_audio(self, audio_data: bytes) -> AudioData:
        """Process incoming audio data"""
        try:
            # Convert to required input format (16kHz PCM)
            processed_data = await self.convert_audio_format(
                audio_data,
                from_rate=self.settings.input_sample_rate,
                to_rate=self.settings.input_sample_rate
            )
            
            return AudioData(
                data=processed_data,
                format=AudioFormat.PCM,
                sample_rate=self.settings.input_sample_rate,
                channels=self.settings.channels
            )
            
        except Exception as e:
            logger.error(f"Error processing input audio: {e}")
            raise
    
    async def process_output_audio(self, audio_data: bytes) -> AudioData:
        """Process outgoing audio data"""
        try:
            # Convert to required output format (24kHz PCM)
            processed_data = await self.convert_audio_format(
                audio_data,
                from_rate=self.settings.output_sample_rate,
                to_rate=self.settings.output_sample_rate
            )
            
            return AudioData(
                data=processed_data,
                format=AudioFormat.PCM,
                sample_rate=self.settings.output_sample_rate,
                channels=self.settings.channels
            )
            
        except Exception as e:
            logger.error(f"Error processing output audio: {e}")
            raise
    
    async def detect_voice_activity(self, audio_data: bytes) -> bool:
        """Simple voice activity detection"""
        try:
            # Calculate RMS (Root Mean Square) for volume detection
            rms = audioop.rms(audio_data, 2)
            
            # Simple threshold-based VAD
            # This is a basic implementation - in production, use more sophisticated VAD
            threshold = 1000  # Adjust based on your needs
            
            return rms > threshold
            
        except Exception as e:
            logger.error(f"Error in voice activity detection: {e}")
            return False
    
    async def buffer_audio(self, audio_data: bytes):
        """Buffer audio data for streaming"""
        try:
            await self.audio_buffer.put(audio_data)
        except Exception as e:
            logger.error(f"Error buffering audio: {e}")
            raise
    
    async def get_buffered_audio(self) -> Optional[bytes]:
        """Get buffered audio data"""
        try:
            if not self.audio_buffer.empty():
                return await self.audio_buffer.get()
            return None
        except Exception as e:
            logger.error(f"Error getting buffered audio: {e}")
            return None
    
    async def stream_audio_chunks(
        self, 
        audio_data: bytes, 
        chunk_size: int = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio data in chunks"""
        try:
            if chunk_size is None:
                chunk_size = self.settings.chunk_size
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                yield chunk
                
        except Exception as e:
            logger.error(f"Error streaming audio chunks: {e}")
            raise
    
    async def apply_audio_effects(self, audio_data: bytes, effects: dict = None) -> bytes:
        """Apply audio effects (volume, filters, etc.)"""
        try:
            if not effects:
                return audio_data
            
            processed_data = audio_data
            
            # Apply volume adjustment
            if 'volume' in effects:
                volume_factor = effects['volume']
                processed_data = audioop.mul(processed_data, 2, volume_factor)
            
            # Apply other effects as needed
            # This is a basic implementation - extend as needed
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error applying audio effects: {e}")
            return audio_data
    
    async def validate_audio_format(self, audio_data: bytes, expected_format: AudioFormat) -> bool:
        """Validate audio data format"""
        try:
            # Basic validation - check if data is not empty
            if not audio_data:
                return False
            
            # Add more sophisticated validation as needed
            # This could include header validation, format detection, etc.
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating audio format: {e}")
            return False
    
    async def get_audio_info(self, audio_data: bytes) -> dict:
        """Get information about audio data"""
        try:
            return {
                "size": len(audio_data),
                "duration_ms": len(audio_data) / (self.settings.input_sample_rate * 2) * 1000,
                "format": "PCM",
                "sample_rate": self.settings.input_sample_rate,
                "channels": self.settings.channels
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {}
