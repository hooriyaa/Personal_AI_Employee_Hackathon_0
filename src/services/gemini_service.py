"""
Gemini Service - Handles interactions with Google's Gemini API.

This service provides methods to generate AI-powered content for
email replies and LinkedIn posts using the Gemini API.
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any


class GeminiService:
    """Service class for interacting with Google's Gemini API."""

    def __init__(self):
        """Initialize the Gemini API client."""
        # Load the API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure the API key
        genai.configure(api_key=api_key)

        # Find an available model that supports generateContent
        available_model = self._find_available_model()
        
        if available_model:
            self.model = genai.GenerativeModel(available_model)
            print(f"Using Gemini model: {available_model}")
        else:
            # Fallback to static templates if no model is found
            self.model = None
            print("No available Gemini model found. Will use static templates as fallback.")

    def _find_available_model(self):
        """Find the first available model that supports generateContent and has 'gemini' in the name."""
        try:
            # List all available models
            models = genai.list_models()
            
            # Look for models that support generateContent and have 'gemini' in the name
            for model in models:
                if 'generateContent' in model.supported_generation_methods and 'gemini' in model.name.lower():
                    return model.name.split('/')[-1]  # Return just the model name without the path
            
            # If no gemini model is found, try to find any model that supports generateContent
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    return model.name.split('/')[-1]  # Return just the model name without the path
                    
        except Exception as e:
            print(f"Error listing models: {e}")
            return None
            
        return None
    
    def generate_email_reply(self, email_body: str, sender_name: str, intent: str) -> Dict[str, Any]:
        """
        Generate an AI-powered email reply based on the provided parameters.

        Args:
            email_body (str): The content of the original email
            sender_name (str): The name of the sender
            intent (str): The intended purpose or tone of the reply

        Returns:
            Dict[str, Any]: A dictionary containing the generated content and metadata
        """
        # If no model is available, use static templates as fallback
        if self.model is None:
            return {
                "success": False,
                "error": "No Gemini model available",
                "fallback_message": f"Thank you for your message. I have received your request about '{intent}' and will get back to you soon."
            }
        
        try:
            # Construct the prompt for the Gemini API with specific quality instructions
            prompt = f"""
            You are Hooriya, a professional AI Employee. Act as a helpful and efficient assistant.

            CONSTRAINTS:
            - Be concise and direct. Do NOT repeat the same thought in different words. Avoid redundancy.
            - Start with a professional greeting, address the specific intent clearly in 1-2 sentences, and end with a polite closing.
            - Always sign off exactly as:
              Best regards,
              Hooriya M. Fareed
              AI Agent Specialist
              (Sent via AI Employee)

            Original email from {sender_name}:
            {email_body}

            The intent of the reply is: {intent}

            Please generate a professional, contextually appropriate reply following the above constraints.
            """

            # Generate content using the Gemini API
            response = self.model.generate_content(prompt)

            # Return the generated content with metadata
            return {
                "success": True,
                "content": response.text,
                "confidence": 0.9,  # Placeholder confidence value
                "tokens_used": len(response.text.split())  # Approximate token count
            }
        except Exception as e:
            # Return a safe fallback message if the API call fails
            return {
                "success": False,
                "error": str(e),
                "fallback_message": f"Thank you for your message. I have received your request about '{intent}' and will get back to you soon."
            }
    
    def generate_linkedin_post(self, topic: str) -> Dict[str, Any]:
        """
        Generate an AI-powered LinkedIn post based on the provided topic.

        Args:
            topic (str): The subject or theme for the LinkedIn post

        Returns:
            Dict[str, Any]: A dictionary containing the generated content and metadata
        """
        # If no model is available, use static templates as fallback
        if self.model is None:
            return {
                "success": False,
                "error": "No Gemini model available",
                "fallback_message": f"Just exploring {topic} today. The potential for innovation is incredible!"
            }
        
        try:
            # Construct the prompt for the Gemini API
            prompt = f"""
            Create an engaging, professional LinkedIn post about: {topic}

            The post should be insightful, valuable to professionals, and include relevant hashtags.
            """

            # Generate content using the Gemini API
            response = self.model.generate_content(prompt)

            # Return the generated content with metadata
            return {
                "success": True,
                "content": response.text,
                "hashtags": self._extract_hashtags(response.text),
                "confidence": 0.9  # Placeholder confidence value
            }
        except Exception as e:
            # Return a safe fallback message if the API call fails
            return {
                "success": False,
                "error": str(e),
                "fallback_message": f"Just exploring {topic} today. The potential for innovation is incredible!"
            }
    
    def _extract_hashtags(self, content: str) -> list:
        """
        Extract hashtags from the generated content.
        
        Args:
            content (str): The generated content
            
        Returns:
            list: A list of hashtags found in the content
        """
        # Simple hashtag extraction (in a real implementation, this could be more sophisticated)
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags