"""
RTVI protocol schema definitions
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any
from enum import Enum

class RTVIEventType(str, Enum):
    """RTVI event types"""
    TRANSPORT_STATE_CHANGED = "transport-state-changed"
    CLIENT_READY = "client-ready"
    USER_TRANSCRIPTION = "user-transcription"
    BOT_TRANSCRIPTION = "bot-transcription"
    USER_SPEAKING = "user-speaking"
    BOT_SPEAKING = "bot-speaking"
    ERROR = "error"
    AUDIO_INPUT = "audio-input"
    AUDIO_OUTPUT = "audio-output"

class RTVITransportState(str, Enum):
    """RTVI transport states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    READY = "ready"
    ERROR = "error"

class RTVIServiceType(str, Enum):
    """RTVI service types"""
    STT = "stt"
    LLM = "llm"
    TTS = "tts"
    VAD = "vad"

class RTVIServiceConfig(BaseModel):
    """RTVI service configuration"""
    service: RTVIServiceType = Field(..., description="Service type")
    options: List[Dict[str, Any]] = Field(default_factory=list, description="Service options")

class RTVIMessage(BaseModel):
    """Base RTVI message schema"""
    type: RTVIEventType = Field(..., description="Message type")
    id: Optional[str] = Field(None, description="Message ID")
    timestamp: Optional[float] = Field(None, description="Message timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Message data")

class RTVIClientConfig(BaseModel):
    """RTVI client configuration"""
    services: Dict[str, str] = Field(default_factory=dict, description="Service mappings")
    config: List[RTVIServiceConfig] = Field(default_factory=list, description="Service configurations")
    enableMic: bool = Field(default=True, description="Enable microphone")
    enableCam: bool = Field(default=False, description="Enable camera")
    baseUrl: Optional[str] = Field(None, description="Base URL for services")

class RTVITransportStateMessage(RTVIMessage):
    """Transport state change message"""
    type: RTVIEventType = RTVIEventType.TRANSPORT_STATE_CHANGED
    state: RTVITransportState = Field(..., description="Transport state")

class RTVITranscriptionMessage(RTVIMessage):
    """Transcription message"""
    text: str = Field(..., description="Transcribed text")
    is_final: bool = Field(default=False, description="Is final transcription")
    confidence: Optional[float] = Field(None, description="Confidence score")

class RTVISpeakingMessage(RTVIMessage):
    """Speaking state message"""
    is_speaking: bool = Field(..., description="Speaking state")
    speaker: str = Field(..., description="Speaker (user/bot)")

class RTVIErrorMessage(RTVIMessage):
    """Error message"""
    type: RTVIEventType = RTVIEventType.ERROR
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(None, description="Error code")

class RTVIAudioMessage(RTVIMessage):
    """Audio data message"""
    audio_data: bytes = Field(..., description="Audio data")
    format: str = Field(..., description="Audio format")
    sample_rate: int = Field(..., description="Sample rate")
    channels: int = Field(default=1, description="Number of channels")
