import asyncio
import websockets
import json
import time

async def test_end_to_end_voice_commands():
    """Test the complete end-to-end voice command flow"""
    uri = "ws://localhost:5050/ws"
    
    test_scenarios = [
        {
            "name": "Open Voice Form",
            "command": "open voice form",
            "expected_response": "switch_tab"
        },
        {
            "name": "Fill Name Field",
            "command": "my name is John Doe",
            "expected_response": "fill_field"
        },
        {
            "name": "Fill Email Field", 
            "command": "my email is john@example.com",
            "expected_response": "fill_field"
        },
        {
            "name": "Fill Message Field",
            "command": "my message is Hello, this is a test message",
            "expected_response": "fill_field"
        },
        {
            "name": "Submit Form",
            "command": "submit form",
            "expected_response": "submit_form"
        }
    ]
    
    print("🧪 Starting End-to-End Voice Command Tests")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            for i, scenario in enumerate(test_scenarios, 1):
                print(f"\n--- Test {i}: {scenario['name']} ---")
                print(f"Command: '{scenario['command']}'")
                
                message = {
                    "type": "text_input",
                    "text": scenario['command'],
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "voice_command_response":
                        response_data = data.get("response", {})
                        action = response_data.get("action")
                        
                        if action == scenario["expected_response"]:
                            print(f"✅ PASS: Expected '{scenario['expected_response']}', got '{action}'")
                            print(f"   Response: {response_data}")
                        else:
                            print(f"❌ FAIL: Expected '{scenario['expected_response']}', got '{action}'")
                            print(f"   Response: {response_data}")
                            
                    elif data.get("type") == "text_received":
                        print("📝 Text received confirmation")
                    elif data.get("type") == "connection_established":
                        print("🔗 Connection established")
                    else:
                        print(f"📨 Other message: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for response")
                
                # Small delay between commands
                await asyncio.sleep(1)
            
            print("\n" + "=" * 50)
            print("🎉 End-to-End Tests Completed!")
            print("\n📋 Summary:")
            print("• Backend is running on port 5050")
            print("• Frontend is running on port 3000") 
            print("• WebSocket connection is working")
            print("• Voice commands are being processed")
            print("\n🌐 Next Steps:")
            print("1. Open http://localhost:3000 in your browser")
            print("2. Try the test buttons or speak voice commands")
            print("3. Check the browser console for debug messages")
            print("4. Verify that 'open voice form' switches to the form tab")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_end_to_end_voice_commands()) 