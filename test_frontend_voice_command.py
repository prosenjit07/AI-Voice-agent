#!/usr/bin/env python3
"""
Test script to verify frontend voice command functionality
"""
import asyncio
import websockets
import json

async def test_frontend_voice_command():
    """Test that the frontend can send voice commands and receive responses"""
    uri = "ws://localhost:5050/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for connection established message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📨 Received: {data}")
            
            if data.get("type") == "connection_established":
                print("✅ Connection established successfully")
            else:
                print("❌ Unexpected initial message")
                return
            
            # Send a voice command like the frontend would
            command = "open voice form"
            message = {
                "type": "text_input",
                "text": command,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            print(f"🎤 Sending voice command: {command}")
            await websocket.send(json.dumps(message))
            
            # Wait for multiple responses
            responses_received = []
            for i in range(5):  # Wait for up to 5 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    responses_received.append(data)
                    print(f"📨 Response {i+1}: {data}")
                    
                    # Check if we got the voice command response
                    if data.get("type") == "voice_command_response":
                        response_data = data.get("response", {})
                        if response_data.get("action") == "switch_tab" and response_data.get("tab") == "form":
                            print("✅ Voice command processed correctly!")
                            print(f"✅ Form tab should be opened")
                            return True
                            
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout waiting for response {i+1}")
                    break
            
            print("❌ Voice command response not received correctly")
            print(f"📋 All responses received: {responses_received}")
            return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_frontend_voice_command())
    if success:
        print("\n🎉 Frontend voice command test PASSED!")
    else:
        print("\n❌ Frontend voice command test FAILED!") 