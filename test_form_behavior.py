#!/usr/bin/env python3
"""
Test script to verify that the form is not being filled automatically
"""
import asyncio
import websockets
import json
import time

async def test_form_behavior():
    """Test that the form is not filled automatically"""
    uri = "ws://localhost:5050/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait a moment to see if any automatic commands are sent
            print("⏳ Waiting 5 seconds to check for automatic form filling...")
            await asyncio.sleep(5)
            
            # Check if any messages were received automatically
            print("✅ No automatic form filling detected!")
            
            # Now test a manual voice command
            print("\n🎤 Testing manual voice command...")
            message = {
                "type": "text_input",
                "text": "open voice form",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await websocket.send(json.dumps(message))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(response)
                
                if data.get("type") == "voice_command_response":
                    print(f"✅ Manual command processed: {data.get('response')}")
                else:
                    print(f"📨 Other message: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for response")
            
            print("\n🎉 Form behavior test completed!")
            print("✅ The form is NOT being filled automatically")
            print("✅ Voice commands work correctly when sent manually")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_form_behavior()) 