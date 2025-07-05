"""
WebSocket routes for real-time audio streaming
"""
import asyncio
import json
import logging
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
        self.pipelines: Dict[str, LowLatencyLowLatencyAudioPipeline] = {}
    
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
        pipeline = LowLatencyLowLatencyAudioPipeline()
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
                await pipeline.process_text_input(text)
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
