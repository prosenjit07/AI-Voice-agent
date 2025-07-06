#!/usr/bin/env python3
"""
Test script to verify voice command processing without Gemini errors
"""
import asyncio
import websockets
import json

async def test_voice_command():
    """Test sending a voice command to the backend"""
    uri = "ws://localhost:5050/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Send a test voice command
            test_command = "open voice form"
            message = {
                "type": "text_input",
                "text": test_command,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            print(f"Sending command: {test_command}")
            await websocket.send(json.dumps(message))
            
            # Wait for multiple responses
            for i in range(5):  # Wait for up to 5 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"Received response {i+1}: {response}")
                    
                    # Parse response
                    data = json.loads(response)
                    if data.get("type") == "voice_command_response":
                        print("✅ Voice command processed successfully!")
                        print(f"Response: {data.get('response')}")
                        return
                    elif data.get("type") == "text_received":
                        print("📝 Text received confirmation")
                    elif data.get("type") == "connection_established":
                        print("🔗 Connection established")
                    else:
                        print(f"📨 Other message type: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout waiting for response {i+1}")
                    break
            
            print("❌ No voice command response received")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_command()) 