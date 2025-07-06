"""
Gemini Live API service with function calling capabilities
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any, List
import google.generativeai as genai
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
            
            # Configure the API key
            genai.configure(api_key=api_key)
            self.client = genai
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
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
        """Connect to Gemini API with function calling"""
        try:
            # For now, we'll use a simplified approach without Live API
            # The standard Gemini API will be used for text processing
            self.is_connected = True
            logger.info("Connected to Gemini API (standard mode)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini API: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Gemini API"""
        try:
            self.session = None
            self.is_connected = False
            logger.info("Disconnected from Gemini API")
        except Exception as e:
            logger.error(f"Error disconnecting from Gemini API: {e}")
    
    async def send_audio(self, audio_data: bytes, mime_type: str = "audio/pcm;rate=16000"):
        """Send audio data to Gemini API (placeholder for now)"""
        try:
            if not self.is_connected:
                raise Exception("Not connected to Gemini API")
            
            # For now, we'll just log that audio was received
            # In a real implementation, you'd convert audio to text and send to Gemini
            logger.info(f"Received audio data ({len(audio_data)} bytes)")
            
        except Exception as e:
            logger.error(f"Error sending audio to Gemini: {e}")
            raise
    
    async def send_text(self, text: str, turn_complete: bool = True):
        """Send text message to Gemini API"""
        try:
            if not self.is_connected:
                raise Exception("Not connected to Gemini API")
            
            # Use the standard Gemini API to generate a response
            model = genai.GenerativeModel(self.settings.gemini_model)
            response = await model.generate_content_async(text)
            
            logger.info(f"Sent text to Gemini: {text}")
            logger.info(f"Received response: {response.text}")
            
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
        """Receive responses from Gemini API (simplified for now)"""
        try:
            if not self.is_connected:
                raise Exception("Not connected to Gemini API")
            
            # For now, this is a placeholder
            # In a real implementation, you'd handle streaming responses
            yield {
                "type": "text",
                "data": "Gemini API is ready for text processing"
            }
                    
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