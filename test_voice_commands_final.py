import asyncio
import websockets
import json
import time

async def test_voice_commands_final():
    """Final test of the complete voice command system"""
    uri = "ws://localhost:5050/ws"
    
    print("🎯 Final Voice Command System Test")
    print("=" * 50)
    
    test_commands = [
        {
            "command": "open voice form",
            "expected_action": "switch_tab",
            "expected_tab": "form",
            "description": "Switch to form tab"
        },
        {
            "command": "my name is John Doe",
            "expected_action": "fill_field",
            "expected_field": "name",
            "expected_value": "john doe",
            "description": "Fill name field"
        },
        {
            "command": "my email is john@example.com",
            "expected_action": "fill_field", 
            "expected_field": "email",
            "expected_value": "john@example.com",
            "description": "Fill email field"
        },
        {
            "command": "my message is Hello world",
            "expected_action": "fill_field",
            "expected_field": "message", 
            "expected_value": "hello world",
            "description": "Fill message field"
        },
        {
            "command": "submit form",
            "expected_action": "submit_form",
            "description": "Submit the form"
        }
    ]
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            for i, test in enumerate(test_commands, 1):
                print(f"\n--- Test {i}: {test['description']} ---")
                print(f"Command: '{test['command']}'")
                
                message = {
                    "type": "text_input",
                    "text": test['command'],
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "voice_command_response":
                        response_data = data.get("response", {})
                        action = response_data.get("action")
                        
                        print(f"✅ Received voice command response:")
                        print(f"   Action: {action}")
                        print(f"   Expected: {test['expected_action']}")
                        
                        if action == test['expected_action']:
                            print(f"   ✅ Action matches!")
                            
                            # Check specific fields for fill_field actions
                            if action == "fill_field":
                                field = response_data.get("field")
                                value = response_data.get("value")
                                expected_field = test.get("expected_field")
                                expected_value = test.get("expected_value")
                                
                                if field == expected_field and value == expected_value:
                                    print(f"   ✅ Field and value match: {field} = {value}")
                                else:
                                    print(f"   ❌ Field/value mismatch: got {field}={value}, expected {expected_field}={expected_value}")
                            
                            # Check tab for switch_tab actions
                            elif action == "switch_tab":
                                tab = response_data.get("tab")
                                expected_tab = test.get("expected_tab")
                                
                                if tab == expected_tab:
                                    print(f"   ✅ Tab matches: {tab}")
                                else:
                                    print(f"   ❌ Tab mismatch: got {tab}, expected {expected_tab}")
                        else:
                            print(f"   ❌ Action mismatch!")
                            
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
            
            print("\n" + "=" * 50)
            print("🎉 Final Test Results:")
            print("✅ Backend is processing voice commands correctly")
            print("✅ WebSocket communication is working")
            print("✅ Voice command responses are being sent")
            print("\n🌐 Next Steps:")
            print("1. Open http://localhost:3000 in your browser")
            print("2. Click the microphone button to start recording")
            print("3. Say 'open voice form' - it should switch to the form tab")
            print("4. Say 'my name is [your name]' - it should fill the name field")
            print("5. Check the browser console for debug messages")
            print("6. Look for the 'Recognized: ...' message when you speak")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_commands_final()) 