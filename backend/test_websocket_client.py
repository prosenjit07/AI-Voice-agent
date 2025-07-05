#!/usr/bin/env python3
"""
Simple WebSocket client for testing the real-time audio streaming API
"""
import asyncio
import json
import websockets
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test basic WebSocket connection and functionality"""
    uri = "ws://localhost:5000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Wait for connection message
            response = await websocket.recv()
            connection_data = json.loads(response)
            logger.info(f"Connection established: {connection_data}")
            
            # Send a ping message
            ping_message = {
                "type": "ping",
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send(json.dumps(ping_message))
            logger.info("Sent ping message")
            
            # Wait for pong response
            response = await websocket.recv()
            pong_data = json.loads(response)
            logger.info(f"Received pong: {pong_data}")
            
            # Send a text input message
            text_message = {
                "type": "text_input",
                "text": "Hello, this is a test message from the WebSocket client!"
            }
            await websocket.send(json.dumps(text_message))
            logger.info("Sent text message")
            
            # Wait for text response
            response = await websocket.recv()
            text_data = json.loads(response)
            logger.info(f"Received text response: {text_data}")
            
            # Request status
            status_message = {
                "type": "status_request"
            }
            await websocket.send(json.dumps(status_message))
            logger.info("Requested status")
            
            # Wait for status response
            response = await websocket.recv()
            status_data = json.loads(response)
            logger.info(f"Received status: {status_data}")
            
            # Send RTVI message
            rtvi_message = {
                "type": "rtvi_message",
                "rtvi_data": {
                    "type": "client_ready",
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            await websocket.send(json.dumps(rtvi_message))
            logger.info("Sent RTVI message")
            
            # Wait for RTVI response
            response = await websocket.recv()
            rtvi_data = json.loads(response)
            logger.info(f"Received RTVI response: {rtvi_data}")
            
            # Keep connection open for a few seconds to observe any additional messages
            logger.info("Waiting for additional messages...")
            try:
                await asyncio.wait_for(websocket.recv(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.info("No additional messages received")
            
            logger.info("WebSocket test completed successfully")
            
    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())