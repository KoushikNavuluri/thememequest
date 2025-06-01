"""
Unit tests for the Meme Generator API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app
from app.schemas.meme_schemas import MemeGenerationRequest


@pytest.fixture
def client():
    """Test client fixture"""
    with TestClient(app) as client:
        yield client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_generate_meme_request_validation(client):
    """Test meme generation request validation"""
    # Test with empty text prompt
    response = client.post("/api/v1/generate-meme", json={
        "text_prompt": "",
        "max_dimension": 500
    })
    assert response.status_code == 422
    
    # Test with invalid max_dimension
    response = client.post("/api/v1/generate-meme", json={
        "text_prompt": "test meme",
        "max_dimension": 50  # Too small
    })
    assert response.status_code == 422
    
    # Test with invalid language code
    response = client.post("/api/v1/generate-meme", json={
        "text_prompt": "test meme",
        "input_language": "invalid"
    })
    assert response.status_code == 422


@patch('app.routers.memes.get_meme_generator')
def test_generate_meme_success(mock_get_generator, client):
    """Test successful meme generation"""
    # Mock the meme generator
    mock_generator = Mock()
    mock_generator.generate_memes_from_text.return_value = (
        [
            {
                "id": "test_meme_1",
                "width": 476,
                "height": 500,
                "image_name": "https://example.com/image.jpg",
                "captions": [],
                "top_header_caption": None,
                "bottom_header_caption": None
            }
        ],
        "run123"
    )
    mock_generator.generate_image_from_meme_data.return_value = "generated_memes/test_meme_1.png"
    mock_get_generator.return_value = mock_generator
    
    response = client.post("/api/v1/generate-meme", json={
        "text_prompt": "test meme",
        "max_dimension": 500
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["meme_count"] == 1
    assert len(data["memes"]) == 1
    assert len(data["generated_files"]) == 1


@patch('app.routers.memes.get_meme_generator')
def test_generate_meme_failure(mock_get_generator, client):
    """Test meme generation failure"""
    # Mock the meme generator to return None
    mock_generator = Mock()
    mock_generator.generate_memes_from_text.return_value = (None, None)
    mock_get_generator.return_value = mock_generator
    
    response = client.post("/api/v1/generate-meme", json={
        "text_prompt": "test meme",
        "max_dimension": 500
    })
    
    assert response.status_code == 503


def test_clear_token(client):
    """Test token clearing endpoint"""
    with patch('app.routers.memes.get_meme_generator') as mock_get_generator:
        mock_generator = Mock()
        mock_generator.token_manager.clear_token.return_value = True
        mock_get_generator.return_value = mock_generator
        
        response = client.post("/api/v1/clear-token")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


def test_pydantic_models():
    """Test Pydantic model validation"""
    # Test valid request
    request = MemeGenerationRequest(
        text_prompt="test meme",
        max_dimension=500,
        input_language="en",
        output_language="en"
    )
    assert request.text_prompt == "test meme"
    assert request.max_dimension == 500
    
    # Test with defaults
    request = MemeGenerationRequest(text_prompt="test")
    assert request.max_dimension == 500
    assert request.input_language == "en"
    assert request.output_language == "en"


if __name__ == "__main__":
    pytest.main([__file__]) 