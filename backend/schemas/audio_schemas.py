"""
Audio-related schema definitions
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from enum import Enum

class AudioFormat(str, Enum):
    """Supported audio formats"""
    PCM = "pcm"
    WAV = "wav"
    MP3 = "mp3"

class AudioConfig(BaseModel):
    """Audio configuration schema"""
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    format: AudioFormat = Field(default=AudioFormat.PCM, description="Audio format")
    chunk_size: int = Field(default=512, description="Audio chunk size in bytes")

class AudioData(BaseModel):
    """Audio data schema"""
    data: bytes = Field(..., description="Raw audio data")
    format: AudioFormat = Field(..., description="Audio format")
    sample_rate: int = Field(..., description="Sample rate in Hz")
    channels: int = Field(default=1, description="Number of channels")
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds")

class VoiceActivityDetection(BaseModel):
    """Voice activity detection configuration"""
    enabled: bool = Field(default=True, description="Enable VAD")
    sensitivity: float = Field(default=0.5, description="VAD sensitivity (0.0-1.0)")
    start_threshold: float = Field(default=0.3, description="Start of speech threshold")
    end_threshold: float = Field(default=0.5, description="End of speech threshold")

class AudioStreamConfig(BaseModel):
    """Audio streaming configuration"""
    input_config: AudioConfig = Field(default_factory=AudioConfig)
    output_config: AudioConfig = Field(default_factory=lambda: AudioConfig(sample_rate=24000))
    vad_config: VoiceActivityDetection = Field(default_factory=VoiceActivityDetection)
    buffer_size: int = Field(default=1024, description="Buffer size for audio streaming")
