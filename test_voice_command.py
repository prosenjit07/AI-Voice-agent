import asyncio
import websockets
import json

async def test_voice_commands():
    """Test sending multiple voice commands to the backend"""
    uri = "ws://localhost:5050/ws"
    
    test_commands = [
        "open voice form",
        "my name is John Doe",
        "my email is john@example.com", 
        "my message is Hello, this is a test message",
        "submit form"
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            for i, command in enumerate(test_commands, 1):
                print(f"\n--- Test {i}: {command} ---")
                
                message = {
                    "type": "text_input",
                    "text": command,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "voice_command_response":
                        print(f"✅ Command processed: {data.get('response')}")
                    elif data.get("type") == "text_received":
                        print("📝 Text received confirmation")
                    elif data.get("type") == "connection_established":
                        print("🔗 Connection established")
                    else:
                        print(f"📨 Other message: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                
                # Small delay between commands
                await asyncio.sleep(0.5)
            
            print("\n🎉 All voice command tests completed!")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_commands()) 