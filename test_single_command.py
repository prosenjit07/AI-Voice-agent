import asyncio
import websockets
import json
import time

async def test_single_email_command():
    """Test just the email command to isolate the issue"""
    uri = "ws://localhost:5050/ws"
    
    print("🧪 Testing Single Email Command")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Wait for connection
            await asyncio.sleep(1)
            
            # Send email command
            command = "my email is john@example.com"
            print(f"📤 Sending command: '{command}'")
            
            message = {
                "type": "text_input",
                "text": command,
                "timestamp": time.time()
            }
            
            print(f"📤 Sending message: {json.dumps(message)}")
            await websocket.send(json.dumps(message))
            
            # Wait for multiple responses
            responses_received = 0
            while responses_received < 3:  # Expect connection, voice command response, and text received
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(response)
                    responses_received += 1
                    
                    print(f"📥 Response {responses_received}: {data}")
                    
                    if data.get("type") == "voice_command_response":
                        response_data = data.get("response", {})
                        action = response_data.get("action")
                        field = response_data.get("field")
                        value = response_data.get("value")
                        
                        print(f"✅ Backend response:")
                        print(f"   Action: {action}")
                        print(f"   Field: {field}")
                        print(f"   Value: {value}")
                        
                        if action == "fill_field" and field == "email":
                            print(f"   ✅ SUCCESS: Email field correctly identified!")
                        else:
                            print(f"   ❌ FAILED: Expected email field, got {field}")
                            
                    elif data.get("type") == "text_received":
                        print("📝 Text received confirmation")
                    elif data.get("type") == "connection_established":
                        print("🔗 Connection established")
                    else:
                        print(f"📨 Other message: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                    break
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_email_command()) 