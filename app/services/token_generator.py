"""
Token generator service for creating authentication tokens
"""
import requests
import time
import re
from typing import Optional
import logging
from .temp_mail import TempMailGenerator

logger = logging.getLogger(__name__)


class TokenGenerator:
    """Generates authentication tokens using temporary email and OTP verification"""
    
    def __init__(self, supabase_url: str, api_key: str):
        self.supabase_url = supabase_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'apikey': self.api_key,
            'X-Client-Info': 'supabase-ssr/0.1.0',
            'X-Supabase-Api-Version': '2024-01-01',
            'Origin': 'https://supermeme.ai',
            'Referer': 'https://supermeme.ai/',
        }
    
    def request_otp(self, email: str) -> bool:
        """Request OTP for email verification"""
        payload = {
            "email": email,
            "data": {},
            "create_user": True,
            "gotrue_meta_security": {}
        }
        
        try:
            response = requests.post(f"{self.supabase_url}/otp", headers=self.headers, json=payload, timeout=10)
            success = response.status_code in [200, 201]
            if success:
                logger.info(f"OTP requested successfully for {email}")
            else:
                logger.error(f"Failed to request OTP: {response.status_code}")
            return success
        except Exception as e:
            logger.error(f"Error requesting OTP: {e}")
            return False
    
    def verify_otp(self, email: str, otp: str) -> Optional[str]:
        """Verify OTP and get access token"""
        payload = {
            "email": email,
            "token": otp,
            "type": "email",
            "gotrue_meta_security": {}
        }
        
        try:
            response = requests.post(f"{self.supabase_url}/verify", headers=self.headers, json=payload, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                access_token = response_data.get('access_token')
                if access_token:
                    logger.info("OTP verified successfully, access token obtained")
                return access_token
            logger.error(f"Failed to verify OTP: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return None
    
    def extract_otp_from_text(self, text: str) -> Optional[str]:
        """Extract OTP code from email text"""
        otp_patterns = [
            r'\b(\d{6})\b',
            r'OTP[:\s]*(\d{6})',
            r'code[:\s]*(\d{6})',
            r'verification[:\s]*(\d{6})',
            r'token[:\s]*(\d{6})',
        ]
        
        for pattern in otp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                logger.info("OTP extracted from email text")
                return matches[0]
        logger.warning("No OTP found in email text")
        return None
    
    def generate_new_token(self, mail_api_url: str = "https://api.mail.tm") -> Optional[str]:
        """Generate new authentication token using temporary email"""
        logger.info("Starting token generation process")
        temp_mail = TempMailGenerator(mail_api_url)
        
        # Create temporary email account
        if not temp_mail.create_account():
            logger.error("Failed to create temporary email account")
            return None
        
        # Request OTP
        if not self.request_otp(temp_mail.email_address):
            logger.error("Failed to request OTP")
            return None
        
        # Wait for email and extract OTP
        logger.info("Waiting for OTP email...")
        for attempt in range(15):
            time.sleep(2)
            messages = temp_mail.get_messages()
            
            if messages:
                for message in messages:
                    full_message = temp_mail.get_message_content(message['id'])
                    if full_message and 'text' in full_message:
                        otp = self.extract_otp_from_text(full_message['text'])
                        if otp:
                            # Verify OTP and get access token
                            access_token = self.verify_otp(temp_mail.email_address, otp)
                            if access_token:
                                logger.info("Token generation completed successfully")
                                return access_token
                break
        
        logger.error("Token generation failed - no valid OTP received")
        return None 