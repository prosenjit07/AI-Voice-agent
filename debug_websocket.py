import asyncio
import websockets
import json
import time

async def debug_websocket_connection():
    """Debug WebSocket connection and message flow"""
    uri = "ws://localhost:5050/ws"
    
    print("🔍 Starting WebSocket Debug Test")
    print("=" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Test 1: Send "open voice form" command
            print("\n--- Test 1: Sending 'open voice form' ---")
            message = {
                "type": "text_input",
                "text": "open voice form",
                "timestamp": time.time()
            }
            
            print(f"📤 Sending: {json.dumps(message, indent=2)}")
            await websocket.send(json.dumps(message))
            
            # Wait for all responses
            responses = []
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    responses.append(data)
                    print(f"📥 Received: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ No more responses (timeout)")
            
            print(f"\n📊 Total responses received: {len(responses)}")
            
            # Check if we got a voice_command_response
            voice_command_responses = [r for r in responses if r.get("type") == "voice_command_response"]
            if voice_command_responses:
                print("✅ Voice command response found!")
                for resp in voice_command_responses:
                    print(f"   Action: {resp.get('response', {}).get('action')}")
                    print(f"   Tab: {resp.get('response', {}).get('tab')}")
            else:
                print("❌ No voice command response found")
            
            # Test 2: Check connection status
            print("\n--- Test 2: Checking connection status ---")
            status_message = {
                "type": "status_request",
                "timestamp": time.time()
            }
            
            print(f"📤 Sending status request: {json.dumps(status_message, indent=2)}")
            await websocket.send(json.dumps(status_message))
            
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📥 Status response: {json.dumps(data, indent=2)}")
            except asyncio.TimeoutError:
                print("⏰ No status response (timeout)")
            
            print("\n" + "=" * 50)
            print("🎯 Debug Summary:")
            print(f"• WebSocket connection: ✅ Working")
            print(f"• Voice command processing: {'✅ Working' if voice_command_responses else '❌ Not working'}")
            print(f"• Total messages received: {len(responses)}")
            
            if not voice_command_responses:
                print("\n🔧 Troubleshooting:")
                print("1. Check if backend is processing voice commands")
                print("2. Check if frontend WebSocket connection is established")
                print("3. Check browser console for WebSocket errors")
                print("4. Verify the frontend is listening for 'voice_command_response' messages")
                
    except Exception as e:
        print(f"❌ Error during debug: {e}")

if __name__ == "__main__":
    asyncio.run(debug_websocket_connection()) 