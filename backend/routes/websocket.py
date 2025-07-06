"""
WebSocket routes for real-time audio streaming
"""
import asyncio
import json
import logging
import re
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
from pipelines.audio_pipeline import LowLatencyAudioPipeline
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pipelines: Dict[str, LowLatencyAudioPipeline] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connection established for client: {client_id}")
    
    async def disconnect(self, client_id: str):
        """Disconnect WebSocket connection"""
        if client_id in self.active_connections:
            # Stop pipeline if exists
            if client_id in self.pipelines:
                await self.pipelines[client_id].stop()
                del self.pipelines[client_id]
            
            # Remove connection
            del self.active_connections[client_id]
            logger.info(f"WebSocket connection closed for client: {client_id}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

# Global connection manager
manager = ConnectionManager()

async def process_voice_command(text: str) -> Dict[str, Any]:
    """Process voice commands locally without requiring Gemini API"""
    try:
        lower_text = text.lower().strip()
        logger.info(f"Processing voice command: {text}")
        
        # Tab switching commands
        if any(phrase in lower_text for phrase in ["open voice form", "switch to form", "go to form", "show form"]):
            return {
                "action": "switch_tab",
                "tab": "form",
                "message": "Switching to Voice Form tab"
            }
        
        if any(phrase in lower_text for phrase in ["open voice stream", "switch to stream", "go to stream", "show stream"]):
            return {
                "action": "switch_tab", 
                "tab": "stream",
                "message": "Switching to Voice Stream tab"
            }
        
        # Form filling commands
        name_patterns = [
            r"(?:my name is|i am|i'm|name is|call me)\s+([a-zA-Z\s]+)",
            r"(?:set name to|put name as)\s+([a-zA-Z\s]+)",
            r"(?:name)\s+([a-zA-Z\s]+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, lower_text)
            if match:
                name = match.group(1).strip()
                return {
                    "action": "fill_field",
                    "field": "name",
                    "value": name,
                    "message": f"Setting name to {name}"
                }
        
        email_patterns = [
            r"(?:my email is|email is|my email address is|email address)\s+([^\s]+@[^\s]+\.[^\s]+)",
            r"(?:set email to|put email as)\s+([^\s]+@[^\s]+\.[^\s]+)",
            r"(?:email)\s+([^\s]+@[^\s]+\.[^\s]+)"
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, lower_text)
            if match:
                email = match.group(1).strip()
                return {
                    "action": "fill_field",
                    "field": "email", 
                    "value": email,
                    "message": f"Setting email to {email}"
                }
        
        message_patterns = [
            r"(?:my message is|message is|i want to say|tell them)\s+(.+)",
            r"(?:set message to|put message as)\s+(.+)",
            r"(?:message)\s+(.+)"
        ]
        
        for pattern in message_patterns:
            match = re.search(pattern, lower_text)
            if match:
                message = match.group(1).strip()
                return {
                    "action": "fill_field",
                    "field": "message",
                    "value": message,
                    "message": f"Setting message to {message}"
                }
        
        # Submit commands
        submit_patterns = ["submit", "send form", "send it", "submit form", "send the form", "i'm done", "finished", "complete", "done"]
        if any(pattern in lower_text for pattern in submit_patterns):
            return {
                "action": "submit_form",
                "message": "Submit the form"
            }
        
        # Clear commands
        clear_patterns = ["clear", "reset", "clear form", "reset form", "start over", "clear all", "reset all", "clear everything"]
        if any(pattern in lower_text for pattern in clear_patterns):
            return {
                "action": "clear_form",
                "message": "Clear the form"
            }
        
        # No matching command found
        return {
            "action": "unknown",
            "message": f"No matching command found for: {text}"
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return {
            "action": "error",
            "message": f"Error processing command: {str(e)}"
        }

@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming with RTVI protocol support
    """
    client_id = None
    pipeline = None
    
    try:
        # Accept connection
        await websocket.accept()
        
        # Generate client ID
        client_id = f"client_{id(websocket)}"
        
        # Add to connection manager
        manager.active_connections[client_id] = websocket
        
        # Create and initialize audio pipeline
        pipeline = LowLatencyAudioPipeline()
        await pipeline.initialize(websocket)
        manager.pipelines[client_id] = pipeline
        
        # Send initial connection message
        await websocket.send_json({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to real-time audio streaming service"
        })
        
        # Start the pipeline
        await pipeline.start()
        
        # Start message handling loop
        await handle_websocket_messages(websocket, client_id, pipeline)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for client: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e),
                "message": "An error occurred in the WebSocket connection"
            })
        except:
            pass
    finally:
        # Cleanup
        if client_id:
            await manager.disconnect(client_id)
        if pipeline:
            await pipeline.stop()

async def handle_websocket_messages(websocket: WebSocket, client_id: str, pipeline: LowLatencyAudioPipeline):
    """Handle incoming WebSocket messages"""
    try:
        while True:
            # Receive message
            message = await websocket.receive()
            
            # Handle different message types
            if message["type"] == "websocket.receive":
                if "bytes" in message:
                    # Handle binary audio data
                    audio_data = message["bytes"]
                    await handle_audio_data(audio_data, pipeline, websocket)
                
                elif "text" in message:
                    # Handle text messages
                    try:
                        data = json.loads(message["text"])
                        await handle_text_message(data, pipeline, websocket)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON message: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "error": "Invalid JSON format",
                            "message": "Message must be valid JSON"
                        })
            
            elif message["type"] == "websocket.disconnect":
                break
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error handling WebSocket messages for client {client_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "Error processing message"
        })

async def handle_audio_data(audio_data: bytes, pipeline: LowLatencyAudioPipeline, websocket: WebSocket):
    """Handle incoming audio data"""
    try:
        # Process audio through pipeline
        await pipeline.process_audio_input(audio_data)
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "audio_received",
            "size": len(audio_data),
            "timestamp": asyncio.get_event_loop().time()
        })
        
    except Exception as e:
        logger.error(f"Error handling audio data: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "Error processing audio data"
        })

async def handle_text_message(data: Dict[str, Any], pipeline: LowLatencyAudioPipeline, websocket: WebSocket):
    """Handle incoming text messages"""
    try:
        message_type = data.get("type")
        
        if message_type == "text_input":
            # Handle text input
            text = data.get("text", "")
            if text:
                # Process voice commands locally
                response = await process_voice_command(text)
                logger.info(f"Sending voice command response: {response}")
                await websocket.send_json({
                    "type": "voice_command_response",
                    "command": text,
                    "response": response,
                    "timestamp": asyncio.get_event_loop().time()
                })
                logger.info("Voice command response sent successfully")
                
                # Only send to Gemini if the local command wasn't recognized
                if not response or response.get("action") == "unknown":
                    logger.info("Local command not recognized, sending to Gemini")
                    await pipeline.process_text_input(text)
                else:
                    logger.info("Local command recognized, skipping Gemini")
                
                await websocket.send_json({
                    "type": "text_received",
                    "text": text,
                    "timestamp": asyncio.get_event_loop().time()
                })
        
        elif message_type == "config":
            # Handle configuration update
            config = data.get("config", {})
            await handle_config_update(config, pipeline, websocket)
        
        elif message_type == "status_request":
            # Handle status request
            status = await pipeline.get_status()
            await websocket.send_json({
                "type": "status_response",
                "status": status,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        elif message_type == "ping":
            # Handle ping
            await websocket.send_json({
                "type": "pong",
                "timestamp": asyncio.get_event_loop().time()
            })
        
        elif message_type == "rtvi_message":
            # Handle RTVI protocol messages
            await handle_rtvi_message(data, pipeline, websocket)
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket.send_json({
                "type": "error",
                "error": "Unknown message type",
                "message": f"Message type '{message_type}' is not supported"
            })
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "Error processing text message"
        })

async def handle_config_update(config: Dict[str, Any], pipeline: LowLatencyAudioPipeline, websocket: WebSocket):
    """Handle configuration updates"""
    try:
        # Update pipeline configuration
        # This is a simplified implementation - extend as needed
        logger.info(f"Configuration update requested: {config}")
        
        await websocket.send_json({
            "type": "config_updated",
            "config": config,
            "message": "Configuration updated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "Error updating configuration"
        })

async def handle_rtvi_message(data: Dict[str, Any], pipeline: LowLatencyAudioPipeline, websocket: WebSocket):
    """Handle RTVI protocol messages"""
    try:
        rtvi_data = data.get("rtvi_data", {})
        event_type = rtvi_data.get("type")
        
        if event_type == "client_ready":
            await pipeline.rtvi_service.handle_client_ready()
        
        elif event_type == "audio_input":
            # Handle RTVI audio input
            audio_data = bytes.fromhex(rtvi_data.get("audio_data", ""))
            if audio_data:
                await pipeline.process_audio_input(audio_data)
        
        elif event_type == "transport_state":
            # Handle transport state messages
            state = rtvi_data.get("state")
            logger.info(f"RTVI transport state: {state}")
        
        await websocket.send_json({
            "type": "rtvi_message_received",
            "event_type": event_type,
            "timestamp": asyncio.get_event_loop().time()
        })
        
    except Exception as e:
        logger.error(f"Error handling RTVI message: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "Error processing RTVI message"
        })

# Additional REST endpoints for WebSocket management
@websocket_router.get("/ws/connections")
async def get_active_connections():
    """Get information about active WebSocket connections"""
    try:
        connections_info = []
        for client_id, websocket in manager.active_connections.items():
            pipeline_status = {}
            if client_id in manager.pipelines:
                pipeline_status = await manager.pipelines[client_id].get_status()
            
            connections_info.append({
                "client_id": client_id,
                "state": websocket.client_state.name,
                "pipeline_status": pipeline_status
            })
        
        return {
            "active_connections": len(manager.active_connections),
            "connections": connections_info
        }
    except Exception as e:
        logger.error(f"Error getting connections info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@websocket_router.post("/ws/broadcast")
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast message to all connected clients"""
    try:
        await manager.broadcast(message)
        return {
            "message": "Message broadcasted successfully",
            "recipients": len(manager.active_connections)
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
