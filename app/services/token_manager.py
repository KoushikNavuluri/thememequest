"""
Token management service for handling authentication tokens
"""
import base64
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages authentication tokens with secure storage"""
    
    def __init__(self):
        self.token_file = ".meme_token"
        self.token_dir = Path.home() / ".meme_generator"
        self.token_path = self.token_dir / self.token_file
        
        # Create hidden directory if it doesn't exist
        self.token_dir.mkdir(exist_ok=True)
    
    def save_token(self, token: str) -> bool:
        """Save token with basic encoding (not encryption, just obfuscation)"""
        try:
            # Simple base64 encoding for obfuscation
            encoded_token = base64.b64encode(token.encode()).decode()
            
            with open(self.token_path, 'w') as f:
                f.write(encoded_token)
            
            # Make file readable only by owner (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(self.token_path, 0o600)
            
            logger.info("Token saved successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not save token: {e}")
            return False
    
    def load_token(self) -> Optional[str]:
        """Load and decode saved token"""
        try:
            if not self.token_path.exists():
                return None
            
            with open(self.token_path, 'r') as f:
                encoded_token = f.read().strip()
            
            if not encoded_token:
                return None
            
            # Decode the token
            decoded_token = base64.b64decode(encoded_token.encode()).decode()
            logger.info("Token loaded successfully")
            return decoded_token
        except Exception as e:
            logger.warning(f"Could not load saved token: {e}")
            return None
    
    def clear_token(self) -> bool:
        """Remove saved token"""
        try:
            if self.token_path.exists():
                self.token_path.unlink()
            logger.info("Token cleared successfully")
            return True
        except Exception as e:
            logger.warning(f"Could not clear token: {e}")
            return False 