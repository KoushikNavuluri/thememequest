"""
Main meme generator service
"""
import json
import os
import time
import random
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
import logging
from curl_cffi import requests as cf_requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from .token_manager import TokenManager
from .token_generator import TokenGenerator
from ..schemas.meme_schemas import MemeData, MemeFile, CaptionData

logger = logging.getLogger(__name__)


class SuperMemeGenerator:
    """Main service for generating memes using SuperMeme AI"""
    
    def __init__(self, api_url: str, supabase_url: str, supabase_api_key: str, mail_api_url: str):
        self.api_url = api_url
        self.token_generator = TokenGenerator(supabase_url, supabase_api_key)
        self.token_manager = TokenManager()
        self.mail_api_url = mail_api_url
        self.current_token = None
        self.default_font_size = 18
        self.default_font_color = "white"
        self.stroke_color = "black"
        self.stroke_width = 2
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'token': self.current_token,
            'Origin': 'https://supermeme.ai',
            'Referer': 'https://supermeme.ai/text-to-meme',
        }
    
    def test_token_validity(self, token: str) -> bool:
        """Test if a token is still valid by making a lightweight API call"""
        if not token:
            return False
        
        test_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'token': token,
            'Origin': 'https://supermeme.ai',
            'Referer': 'https://supermeme.ai/text-to-meme',
        }
        
        test_payload = json.dumps({
            "text": "test",
            "maxDimension": 500,
            "inputLanguage": "en",
            "outputLanguage": "en"
        })
        
        try:
            response = cf_requests.post(
                self.api_url, 
                headers=test_headers, 
                data=test_payload, 
                impersonate="chrome110",
                timeout=10
            )
            
            # If we get 401/403, token is invalid
            # If we get 429, token is valid but rate limited
            # If we get 200, token is valid
            return response.status_code not in [401, 403]
        except Exception as e:
            logger.error(f"Error testing token validity: {e}")
            return False
    
    def ensure_valid_token(self) -> bool:
        """Ensure we have a valid authentication token"""
        # First, try to load saved token
        if not self.current_token:
            saved_token = self.token_manager.load_token()
            if saved_token:
                logger.info("Checking saved token...")
                if self.test_token_validity(saved_token):
                    logger.info("Saved token is valid!")
                    self.current_token = saved_token
                    return True
                else:
                    logger.info("Saved token is invalid, clearing...")
                    self.token_manager.clear_token()
        
        # If no valid token, generate new one
        if not self.current_token:
            logger.info("Generating new access token...")
            new_token = self.token_generator.generate_new_token(self.mail_api_url)
            if new_token:
                logger.info("Token generated successfully!")
                self.current_token = new_token
                # Save the new token
                if self.token_manager.save_token(new_token):
                    logger.info("Token saved for future use!")
                return True
            else:
                logger.error("Failed to generate token")
                return False
        return True
    
    def generate_memes_from_text(
        self, 
        text_prompt: str, 
        max_dimension: int = 500,
        input_language: str = "en",
        output_language: str = "en",
        max_retries: int = 2
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """Generate memes from text prompt"""
        for attempt in range(max_retries):
            if not self.ensure_valid_token():
                return None, None
            
            payload = json.dumps({
                "text": text_prompt,
                "maxDimension": max_dimension,
                "inputLanguage": input_language,
                "outputLanguage": output_language
            })
            
            try:
                logger.info(f"Making meme generation request (attempt {attempt + 1})")
                response = cf_requests.post(
                    self.api_url, 
                    headers=self.get_headers(), 
                    data=payload, 
                    impersonate="chrome110",
                    timeout=30
                )
                
                if response.status_code == 429:
                    logger.warning("Credit limit reached, generating new token...")
                    self.token_manager.clear_token()
                    self.current_token = None
                    continue
                
                if response.status_code in [401, 403]:
                    logger.warning("Token expired, generating new token...")
                    self.token_manager.clear_token()
                    self.current_token = None
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('error'):
                    logger.error(f"API Error: {data['error']}")
                    return None, None
                
                results = data.get('response', {}).get('results', [])
                run_id = data.get('response', {}).get('runId')
                logger.info(f"Successfully generated {len(results)} memes")
                return results, run_id
                
            except Exception as e:
                if "429" in str(e) or "401" in str(e) or "403" in str(e):
                    logger.warning("Token issue detected, generating new token...")
                    self.token_manager.clear_token()
                    self.current_token = None
                    continue
                else:
                    logger.error(f"Request failed: {e}")
                    return None, None
        
        logger.error("All retry attempts failed")
        return None, None
    
    def download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        try:
            response = cf_requests.get(url, timeout=10, impersonate="chrome110")
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return self.create_placeholder_image()
    
    def create_placeholder_image(self, width: int = 476, height: int = 500) -> Image.Image:
        """Create placeholder image when base image is not available"""
        img = Image.new('RGB', (width, height), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, width-50, height//2-25], fill='white', outline='black', width=2)
        draw.rectangle([50, height//2+25, width-50, height-50], fill='white', outline='black', width=2)
        
        try:
            font = self.get_font(24)
            text = "MEME TEMPLATE"
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='black', font=font)
        except Exception as e:
            logger.warning(f"Failed to add text to placeholder: {e}")
        
        return img
    
    def get_font(self, size: int = 18) -> ImageFont.ImageFont:
        """Get font for text rendering"""
        try:
            font_paths = [
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "/usr/share/fonts/TTF/arial.ttf",
                "arial.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            
            return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load custom font: {e}")
            return ImageFont.load_default()
    
    def wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_text_with_stroke(
        self, 
        draw: ImageDraw.Draw, 
        position: Tuple[int, int], 
        text: str, 
        font: ImageFont.ImageFont, 
        fill_color: str, 
        stroke_color: str, 
        stroke_width: int
    ) -> None:
        """Draw text with stroke outline"""
        x, y = position
        
        # Draw stroke
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def add_caption_to_image(self, image: Image.Image, caption_data: Dict[str, Any]) -> None:
        """Add caption to image"""
        draw = ImageDraw.Draw(image)
        
        x = caption_data.get('x', 0)
        y = caption_data.get('y', 0)
        text = caption_data.get('text', '')
        width = caption_data.get('width', 200)
        font_size = caption_data.get('fontSize', self.default_font_size)
        
        font = self.get_font(font_size)
        wrapped_lines = self.wrap_text(text, font, width)
        
        bbox = font.getbbox("A")
        line_height = bbox[3] - bbox[1] + 5
        
        current_y = y
        for line in wrapped_lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            centered_x = x + (width - text_width) // 2
            
            self.draw_text_with_stroke(
                draw, 
                (centered_x, current_y), 
                line, 
                font, 
                self.default_font_color, 
                self.stroke_color, 
                self.stroke_width
            )
            
            current_y += line_height
    
    def generate_image_from_meme_data(
        self, 
        meme_data: Dict[str, Any], 
        output_dir: str = "generated_memes"
    ) -> str:
        """Generate final meme image from meme data"""
        os.makedirs(output_dir, exist_ok=True)
        
        meme_id = meme_data.get('id', f'meme_{random.randint(1000, 9999)}')
        width = meme_data.get('width', 476)
        height = meme_data.get('height', 500)
        
        # Download or create base image
        image_url = meme_data.get('image_name')
        if image_url and image_url.startswith('http'):
            base_image = self.download_image(image_url)
            base_image = base_image.resize((width, height), Image.Resampling.LANCZOS)
        else:
            base_image = self.create_placeholder_image(width, height)
        
        # Add captions
        captions = meme_data.get('captions', [])
        for caption in captions:
            self.add_caption_to_image(base_image, caption)
        
        # Add header and footer captions
        if meme_data.get('top_header_caption'):
            header_caption = {
                'x': 0, 'y': 10, 'text': meme_data['top_header_caption'],
                'width': width, 'height': 30, 'fontSize': 20
            }
            self.add_caption_to_image(base_image, header_caption)
        
        if meme_data.get('bottom_header_caption'):
            footer_caption = {
                'x': 0, 'y': height - 40, 'text': meme_data['bottom_header_caption'],
                'width': width, 'height': 30, 'fontSize': 20
            }
            self.add_caption_to_image(base_image, footer_caption)
        
        # Save image
        filename = f"meme_{meme_id}.png"
        output_path = os.path.join(output_dir, filename)
        base_image.save(output_path, 'PNG')
        
        logger.info(f"Generated meme image: {output_path}")
        return output_path 