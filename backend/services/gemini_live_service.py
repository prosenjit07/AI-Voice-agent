"""
Gemini Live API service with function calling capabilities
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any, List
from google import genai
from google.genai import types
from config import get_settings

logger = logging.getLogger(__name__)

class FormFunctions:
    """Form management functions for Gemini Live API"""
    
    def __init__(self):
        self.current_form = None
        self.form_fields = {}
        self.is_form_open = False
        
    async def open_form(self) -> Dict[str, Any]:
        """Open a new form for data entry"""
        try:
            self.current_form = "data_entry_form"
            self.form_fields = {}
            self.is_form_open = True
            
            logger.info("Form opened successfully")
            return {
                "success": True,
                "message": "Form has been opened and is ready for data entry",
                "form_id": self.current_form
            }
        except Exception as e:
            logger.error(f"Error opening form: {e}")
            return {"success": False, "error": str(e)}
    
    async def fill_field(self, field_name: str, value: str) -> Dict[str, Any]:
        """Fill a specific field in the form"""
        try:
            if not self.is_form_open:
                return {"success": False, "error": "No form is currently open. Please open a form first."}
            
            # Clean and validate field name
            field_name = field_name.lower().strip()
            if not field_name or not value:
                return {"success": False, "error": "Field name and value cannot be empty"}
            
            self.form_fields[field_name] = value
            logger.info(f"Field '{field_name}' filled with value: {value}")
            
            return {
                "success": True,
                "message": f"Field '{field_name}' has been filled with '{value}'",
                "field_name": field_name,
                "value": value,
                "total_fields": len(self.form_fields)
            }
        except Exception as e:
            logger.error(f"Error filling field: {e}")
            return {"success": False, "error": str(e)}
    
    async def submit_form(self) -> Dict[str, Any]:
        """Submit the current form"""
        try:
            if not self.is_form_open:
                return {"success": False, "error": "No form is currently open"}
            
            if not self.form_fields:
                return {"success": False, "error": "Form is empty. Please fill at least one field before submitting."}
            
            # Process form submission
            form_data = {
                "form_id": self.current_form,
                "fields": dict(self.form_fields),
                "submitted_at": asyncio.get_event_loop().time()
            }
            
            logger.info(f"Form submitted with {len(self.form_fields)} fields: {self.form_fields}")
            
            # Reset form state
            self.current_form = None
            self.form_fields = {}
            self.is_form_open = False
            
            return {
                "success": True,
                "message": "Form has been successfully submitted",
                "submitted_data": form_data,
                "field_count": len(form_data["fields"])
            }
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return {"success": False, "error": str(e)}

class GeminiLiveService:
    """Enhanced Gemini Live API service with function calling"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.session = None
        self.is_connected = False
        self.form_functions = FormFunctions()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            api_key = self.settings.gemini_api_key
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
            
            self.client = genai.Client(api_key=api_key)
            logger.info("Gemini Live client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Live client: {e}")
            raise
    
    def _get_function_declarations(self) -> List[Dict[str, Any]]:
        """Get function declarations for Gemini Live API"""
        return [
            {
                "name": "open_form",
                "description": "Opens a new form for data entry. Call this before filling any fields.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "fill_field",
                "description": "Fills a specific field in the currently open form with a value.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "field_name": {
                            "type": "string",
                            "description": "The name of the field to fill (e.g., 'name', 'email', 'phone')"
                        },
                        "value": {
                            "type": "string",
                            "description": "The value to put in the field"
                        }
                    },
                    "required": ["field_name", "value"]
                }
            },
            {
                "name": "submit_form",
                "description": "Submits the current form after all fields have been filled.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def connect(self) -> bool:
        """Connect to Gemini Live API with function calling"""
        try:
            # Simplified configuration using dictionary format
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self.settings.gemini_voice
                        }
                    }
                },
                "system_instruction": {
                    "parts": [{
                        "text": """You are a helpful assistant that can manage forms through voice commands. 
                        You have access to three functions:
                        1. open_form() - Opens a new form for data entry
                        2. fill_field(field_name, value) - Fills a field with a value  
                        3. submit_form() - Submits the completed form
                        
                        When users want to fill out a form or enter data, help them by:
                        - First opening a form
                        - Then filling fields as they provide information
                        - Finally submitting the form when they're ready
                        
                        Be conversational and confirm each action. Respond naturally through voice."""
                    }]
                },
                "tools": {
                    "function_declarations": self._get_function_declarations()
                }
            }
            
            # Use the async context manager correctly
            self._session_context = self.client.aio.live.connect(
                model=self.settings.gemini_model,
                config=config
            )
            
            # Enter the context and store the session
            self.session = await self._session_context.__aenter__()
            
            self.is_connected = True
            logger.info("Connected to Gemini Live API with function calling enabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Gemini Live API"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_connected = False
            logger.info("Disconnected from Gemini Live API")
        except Exception as e:
            logger.error(f"Error disconnecting from Gemini Live API: {e}")
    
    async def send_audio(self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """Send audio data to Gemini Live API"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            await self.session.send_realtime_input(
                audio={"data": audio_data, "mime_type": mime_type}
            )
            
        except Exception as e:
            logger.error(f"Error sending audio to Gemini: {e}")
            raise
    
    async def send_text(self, text: str, turn_complete: bool = True):
        """Send text message to Gemini Live API"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            await self.session.send_client_content(
                turns=[{"role": "user", "parts": [{"text": text}]}],
                turn_complete=turn_complete
            )
            
        except Exception as e:
            logger.error(f"Error sending text to Gemini: {e}")
            raise
    
    async def _execute_function_call(self, function_call) -> Dict[str, Any]:
        """Execute a function call from Gemini"""
        try:
            function_name = function_call.name
            args = function_call.args
            
            logger.info(f"Executing function: {function_name} with args: {args}")
            
            if function_name == "open_form":
                return await self.form_functions.open_form()
            elif function_name == "fill_field":
                field_name = args.get("field_name", "")
                value = args.get("value", "")
                return await self.form_functions.fill_field(field_name, value)
            elif function_name == "submit_form":
                return await self.form_functions.submit_form()
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Error executing function call: {e}")
            return {"success": False, "error": str(e)}
    
    async def receive_responses(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Receive responses from Gemini Live API including function calls"""
        try:
            if not self.is_connected or not self.session:
                raise Exception("Not connected to Gemini Live API")
            
            async for response in self.session.receive():
                try:
                    # Handle server content
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'model_turn') and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                # Handle function calls
                                if hasattr(part, 'function_call') and part.function_call:
                                    function_result = await self._execute_function_call(part.function_call)
                                    
                                    # Send function response back to Gemini
                                    await self.session.send_client_content(
                                        turns=[{
                                            "role": "function",
                                            "parts": [{
                                                "function_response": {
                                                    "name": part.function_call.name,
                                                    "response": function_result
                                                }
                                            }]
                                        }],
                                        turn_complete=True
                                    )
                                    
                                    yield {
                                        "type": "function_call",
                                        "function_name": part.function_call.name,
                                        "arguments": part.function_call.args,
                                        "result": function_result
                                    }
                                
                                # Handle audio response
                                elif hasattr(part, 'inline_data') and part.inline_data:
                                    yield {
                                        "type": "audio",
                                        "data": part.inline_data.data,
                                        "mime_type": part.inline_data.mime_type if hasattr(part.inline_data, 'mime_type') else "audio/pcm"
                                    }
                                
                                # Handle text response
                                elif hasattr(part, 'text') and part.text:
                                    yield {
                                        "type": "text",
                                        "data": part.text
                                    }
                    
                    # Handle turn complete
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            yield {
                                "type": "turn_complete",
                                "data": True
                            }
                            
                except Exception as e:
                    logger.error(f"Error processing Gemini response: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error receiving responses from Gemini: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if the service is healthy"""
        try:
            return self.is_connected and self.session is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
            
    def get_form_status(self) -> Dict[str, Any]:
        """Get current form status"""
        return {
            "is_form_open": self.form_functions.is_form_open,
            "current_form": self.form_functions.current_form,
            "fields_filled": len(self.form_functions.form_fields),
            "form_fields": dict(self.form_functions.form_fields)
        }