import asyncio
import websockets
import json
import time

async def test_frontend_websocket_simulation():
    """Simulate frontend WebSocket connection and test voice command responses"""
    uri = "ws://localhost:5050/ws"
    
    print("🧪 Testing Frontend WebSocket Simulation")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Frontend WebSocket connected")
            
            # Simulate frontend connection behavior
            print("\n--- Step 1: Send initial connection message ---")
            init_message = {
                "type": "control",
                "data": {"action": "connect", "protocol": "rtvi"},
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(init_message))
            
            # Wait for connection established
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📥 Connection response: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ No connection response (timeout)")
            
            # Test voice command
            print("\n--- Step 2: Send voice command 'open voice form' ---")
            voice_command = {
                "type": "text_input",
                "text": "open voice form",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(voice_command))
            
            # Collect all responses
            responses = []
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    responses.append(data)
                    print(f"📥 Frontend received: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ No more responses (timeout)")
            
            # Analyze responses
            print(f"\n📊 Analysis:")
            print(f"• Total responses: {len(responses)}")
            
            voice_command_responses = [r for r in responses if r.get("type") == "voice_command_response"]
            print(f"• Voice command responses: {len(voice_command_responses)}")
            
            if voice_command_responses:
                print("✅ Frontend would receive voice command response!")
                for resp in voice_command_responses:
                    action = resp.get("response", {}).get("action")
                    tab = resp.get("response", {}).get("tab")
                    print(f"   Action: {action}, Tab: {tab}")
                    
                    if action == "switch_tab" and tab == "form":
                        print("   ✅ This should switch to the form tab in the frontend!")
            else:
                print("❌ Frontend would NOT receive voice command response")
            
            print("\n" + "=" * 50)
            print("🎯 Conclusion:")
            if voice_command_responses:
                print("✅ The WebSocket communication is working correctly")
                print("❌ The issue is likely in the frontend UI connection status")
                print("🔧 Check the browser console for WebSocket connection errors")
            else:
                print("❌ The WebSocket communication is not working")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_frontend_websocket_simulation()) 