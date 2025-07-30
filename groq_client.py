"""
Groq API client for chat completions with language support.
"""
import requests
from typing import Optional
from config import config
from utils import get_system_prompts, ErrorHandler


class GroqClient:
    """Simple Groq API client with language support."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key (Optional[str]): Groq API key, defaults to config
            model (Optional[str]): Model name, defaults to config
        """
        self.api_key = api_key or config.api.groq_api_key
        self.model = model or config.api.groq_model
        self.base_url = config.api.groq_base_url
        self.timeout = config.api.groq_timeout
        self.temperature = config.api.groq_temperature
        self.max_tokens = config.api.groq_max_tokens
        self.system_prompts = get_system_prompts()
        
        if not self.api_key:
            raise ValueError("Groq API key is required")
    
    def _create_headers(self) -> dict:
        """
        Create request headers.
        
        Returns:
            dict: Request headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _create_prompt(self, question: str, context: str = "", language: str = "english") -> str:
        """
        Create language-specific prompt.
        
        Args:
            question (str): User question
            context (str): Context from documents
            language (str): Target language
            
        Returns:
            str: Formatted prompt
        """
        system_instruction = self.system_prompts.get(language, self.system_prompts['english'])
        
        if language == "hindi":
            if context:
                return f"{system_instruction}\n\nसंदर्भ (Context): {context}\n\nप्रश्न: {question}\n\nउत्तर (केवल हिंदी में):"
            else:
                return f"{system_instruction}\n\nप्रश्न: {question}\n\nउत्तर (केवल हिंदी में):"
        else:
            if context:
                return f"{system_instruction}\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer (in English only):"
            else:
                return f"{system_instruction}\n\nQuestion: {question}\n\nAnswer (in English only):"
    
    def _create_request_data(self, prompt: str) -> dict:
        """
        Create request data for API call.
        
        Args:
            prompt (str): Formatted prompt
            
        Returns:
            dict: Request data
        """
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
    
    def chat(self, prompt: str, context: str = "", language: str = "english") -> str:
        """
        Chat completion with language-aware prompting.
        
        Args:
            prompt (str): User prompt/question
            context (str): Context from documents
            language (str): Target language ('hindi' or 'english')
            
        Returns:
            str: AI response or error message
        """
        try:
            # Create language-specific prompt
            full_prompt = self._create_prompt(prompt, context, language)
            
            # Prepare request
            headers = self._create_headers()
            data = self._create_request_data(full_prompt)
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                return ErrorHandler.handle_api_error(Exception(error_msg), language)
                
        except requests.exceptions.Timeout:
            error = Exception("Request timed out")
            return ErrorHandler.handle_connection_error(error, language)
            
        except requests.exceptions.ConnectionError:
            error = Exception("Failed to connect to Groq API")
            return ErrorHandler.handle_connection_error(error, language)
            
        except Exception as e:
            return ErrorHandler.handle_api_error(e, language)
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test connection to Groq API.
        
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            test_response = self.chat("Hello", language="english")
            
            if "Error" in test_response:
                return False, test_response
            else:
                return True, "Groq API connection successful"
                
        except Exception as e:
            return False, f"Groq API connection failed: {str(e)}"
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model.
        
        Returns:
            dict: Model information
        """
        return {
            'model': self.model,
            'base_url': self.base_url,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }