"""
Temporary email service for creating disposable email addresses
"""
import requests
import random
import string
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TempMailGenerator:
    """Generates temporary email addresses using mail.tm service"""
    
    def __init__(self, base_url: str = "https://api.mail.tm"):
        self.base_url = base_url
        self.token = None
        self.account_id = None
        self.email_address = None
    
    def get_domains(self) -> List[Dict[str, Any]]:
        """Get available email domains"""
        try:
            response = requests.get(f"{self.base_url}/domains", timeout=10)
            if response.status_code == 200:
                domains_data = response.json()
                active_domains = [domain for domain in domains_data['hydra:member'] if domain['isActive']]
                logger.info(f"Found {len(active_domains)} active domains")
                return active_domains
            return []
        except Exception as e:
            logger.error(f"Failed to get domains: {e}")
            return []
    
    def generate_username(self, length: int = 10) -> str:
        """Generate random username"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def create_account(self) -> bool:
        """Create temporary email account"""
        domains = self.get_domains()
        if not domains:
            logger.error("No domains available")
            return False
        
        domain = domains[0]['domain']
        username = self.generate_username()
        self.email_address = f"{username}@{domain}"
        password = self.generate_username(12)
        
        payload = {"address": self.email_address, "password": password}
        
        try:
            response = requests.post(f"{self.base_url}/accounts", json=payload, timeout=10)
            if response.status_code == 201:
                account_data = response.json()
                self.account_id = account_data['id']
                logger.info(f"Created account: {self.email_address}")
                return self._get_token(self.email_address, password)
            logger.error(f"Failed to create account: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error creating account: {e}")
            return False
    
    def _get_token(self, address: str, password: str) -> bool:
        """Get authentication token for the account"""
        payload = {"address": address, "password": password}
        try:
            response = requests.post(f"{self.base_url}/token", json=payload, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data['token']
                logger.info("Authentication token obtained")
                return True
            logger.error(f"Failed to get token: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error getting token: {e}")
            return False
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get messages from the temporary email account"""
        if not self.token:
            logger.error("No authentication token available")
            return []
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"{self.base_url}/messages", headers=headers, timeout=10)
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data['hydra:member']
                logger.info(f"Retrieved {len(messages)} messages")
                return messages
            logger.error(f"Failed to get messages: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    def get_message_content(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get content of a specific message"""
        if not self.token:
            logger.error("No authentication token available")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"{self.base_url}/messages/{message_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"Retrieved message content for ID: {message_id}")
                return response.json()
            logger.error(f"Failed to get message content: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error getting message content: {e}")
            return None 