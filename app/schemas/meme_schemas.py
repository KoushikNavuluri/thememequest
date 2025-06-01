"""
Pydantic models for meme generation API
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class MemeGenerationRequest(BaseModel):
    """Request model for meme generation"""
    text_prompt: str = Field(
        ..., 
        description="Text prompt for meme generation",
        min_length=1,
        max_length=500
    )
    max_dimension: int = Field(
        default=500,
        description="Maximum dimension for generated images",
        ge=100,
        le=1000
    )
    input_language: str = Field(
        default="en",
        description="Input language code",
        pattern="^[a-z]{2}$"
    )
    output_language: str = Field(
        default="en", 
        description="Output language code",
        pattern="^[a-z]{2}$"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text_prompt": "cats being dramatic",
                    "max_dimension": 500,
                    "input_language": "en",
                    "output_language": "en"
                }
            ]
        }
    }


class CaptionData(BaseModel):
    """Model for meme caption data"""
    x: int = Field(description="X coordinate of caption")
    y: int = Field(description="Y coordinate of caption")
    width: int = Field(description="Width of caption area")
    height: Optional[int] = Field(default=None, description="Height of caption area")
    text: str = Field(description="Caption text")
    fontSize: int = Field(description="Font size")
    
    model_config = {"populate_by_name": True}


class MemeData(BaseModel):
    """Model for individual meme data"""
    id: str = Field(description="Unique meme identifier")
    width: int = Field(description="Meme width in pixels")
    height: int = Field(description="Meme height in pixels")
    image_name: Optional[str] = Field(default=None, description="Base image URL")
    captions: List[CaptionData] = Field(default=[], description="List of captions")
    top_header_caption: Optional[str] = Field(default=None, description="Top header text")
    bottom_header_caption: Optional[str] = Field(default=None, description="Bottom header text")
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        """Convert integer IDs to strings"""
        return str(v)


class MemeFile(BaseModel):
    """Model for generated meme file"""
    filename: str = Field(description="Generated file name")
    file_path: str = Field(description="Relative path to generated file")
    image_url: str = Field(description="HTTP URL to access the generated meme image")
    meme_id: str = Field(description="Meme identifier")
    
    @field_validator('meme_id', mode='before')
    @classmethod
    def convert_meme_id_to_string(cls, v):
        """Convert integer meme IDs to strings"""
        return str(v)
    
    
class MemeGenerationResponse(BaseModel):
    """Response model for meme generation"""
    success: bool = Field(description="Whether generation was successful")
    message: str = Field(description="Response message")
    count: int = Field(description="Number of memes generated")
    meme_list: List[str] = Field(description="List of HTTP URLs to generated meme images")
    run_id: Optional[str] = Field(default=None, description="Generation run identifier")
    meme_count: int = Field(description="Number of memes generated (legacy field)")
    memes: List[MemeData] = Field(default=[], description="Generated meme data")
    generated_files: List[MemeFile] = Field(default=[], description="Generated file information")
    output_directory: str = Field(description="Directory containing generated files")
    generation_time: float = Field(description="Time taken for generation in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    @field_validator('run_id', mode='before')
    @classmethod
    def convert_run_id_to_string(cls, v):
        """Convert integer run_id to string"""
        if v is not None:
            return str(v)
        return v


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(description="API status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Success status")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp") 