"""
Meme generation API routes
"""
import time
import os
from typing import Dict, Any
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from ..schemas.meme_schemas import (
    MemeGenerationRequest, 
    MemeGenerationResponse, 
    ErrorResponse, 
    MemeData, 
    MemeFile
)
from ..services.meme_generator import SuperMemeGenerator
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["memes"])

# Global meme generator instance
meme_generator = None


def get_meme_generator() -> SuperMemeGenerator:
    """Get or create meme generator instance"""
    global meme_generator
    if meme_generator is None:
        meme_generator = SuperMemeGenerator(
            api_url=settings.supermeme_api_url,
            supabase_url=settings.supabase_url,
            supabase_api_key=settings.supabase_api_key,
            mail_api_url=settings.mail_api_url
        )
    return meme_generator


def generate_image_url(request: Request, file_path: str) -> str:
    """Generate HTTP URL for accessing the meme image"""
    # Convert file path to URL path
    relative_path = file_path.replace("\\", "/")  # Handle Windows paths
    if relative_path.startswith("generated_memes/"):
        relative_path = relative_path[len("generated_memes/"):]
    
    # Build full URL
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    image_url = f"{base_url}/static/memes/{relative_path}"
    return image_url


@router.post(
    "/generate-meme",
    response_model=MemeGenerationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service temporarily unavailable"}
    },
    summary="Generate memes from text",
    description="Generate AI-powered memes from a text prompt using SuperMeme AI"
)
async def generate_meme(request_data: MemeGenerationRequest, request: Request) -> MemeGenerationResponse:
    """Generate memes from text prompt"""
    start_time = time.time()
    
    try:
        logger.info(f"Received meme generation request: '{request_data.text_prompt}'")
        
        # Get meme generator
        generator = get_meme_generator()
        
        # Generate memes from text
        meme_results, run_id = generator.generate_memes_from_text(
            text_prompt=request_data.text_prompt,
            max_dimension=request_data.max_dimension,
            input_language=request_data.input_language,
            output_language=request_data.output_language
        )
        
        if not meme_results:
            logger.error("Failed to generate memes from API")
            raise HTTPException(
                status_code=503,
                detail="Failed to generate memes. The service may be temporarily unavailable."
            )
        
        # Create timestamped output directory
        timestamp = int(time.time())
        output_dir = os.path.join(settings.output_directory, f"memes_{timestamp}")
        
        logger.info(f"Generating {len(meme_results)} meme images...")
        generated_files = []
        memes = []
        meme_list = []  # List of image URLs as requested
        
        for i, meme_data in enumerate(meme_results, 1):
            try:
                # Generate image file
                output_path = generator.generate_image_from_meme_data(meme_data, output_dir)
                
                # Create meme file info
                filename = os.path.basename(output_path)
                relative_path = os.path.relpath(output_path)
                
                # Generate HTTP URL for the image
                image_url = generate_image_url(request, relative_path)
                meme_list.append(image_url)  # Add to meme_list as requested
                
                # Pydantic will automatically convert integer meme_id to string
                meme_file = MemeFile(
                    filename=filename,
                    file_path=relative_path,
                    image_url=image_url,
                    meme_id=meme_data.get('id', f'meme_{i}')
                )
                generated_files.append(meme_file)
                
                # Pydantic will automatically convert integer id to string
                meme = MemeData(**meme_data)
                memes.append(meme)
                
                logger.info(f"Generated meme {i}/{len(meme_results)}")
                
            except Exception as e:
                logger.error(f"Error generating meme {i}: {e}")
                continue
        
        if not generated_files:
            logger.error("No memes were generated successfully")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any meme images"
            )
        
        generation_time = time.time() - start_time
        
        response = MemeGenerationResponse(
            success=True,
            message=f"Successfully generated {len(generated_files)} memes",
            count=len(generated_files),  # New field as requested
            meme_list=meme_list,  # New field as requested
            run_id=run_id,
            meme_count=len(generated_files),  # Legacy field
            memes=memes,
            generated_files=generated_files,
            output_directory=os.path.relpath(output_dir),
            generation_time=generation_time
        )
        
        logger.info(f"Meme generation completed in {generation_time:.2f} seconds")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in meme generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/clear-token")
async def clear_token() -> Dict[str, Any]:
    """Clear saved authentication token"""
    try:
        generator = get_meme_generator()
        success = generator.token_manager.clear_token()
        generator.current_token = None
        
        if success:
            return {
                "success": True,
                "message": "Authentication token cleared successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to clear authentication token"
            }
    except Exception as e:
        logger.error(f"Error clearing token: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear token: {str(e)}"
        ) 