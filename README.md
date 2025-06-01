# 🎭 Meme Generator API

A production-ready REST API for generating AI-powered memes using SuperMeme AI. Transform text prompts into hilarious memes with automatic token management and direct HTTP image access.

## ✨ Features

- 🤖 **AI-Powered Meme Generation**: Uses AI for high-quality meme creation
- 🔗 **Direct Image URLs**: Get HTTP URLs for immediate image access
- 🎨 **Advanced Image Processing**: Text rendering with stroke effects and PIL
- 🚀 **FastAPI Backend**: Modern, fast, and well-documented API
- 🔄 **Automatic Retries**: Robust error handling and recovery
- 📊 **OpenAPI Documentation**: Auto-generated API docs with Swagger UI
- 🌐 **CORS Support**: Ready for web applications
- 🐳 **Docker Ready**: Easy deployment with containerization
- 📁 **Static File Serving**: Automatic HTTP serving of generated memes
- ⚡ **High Performance**: Generates 16 memes per request in ~24 seconds

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/koushiknavuluri/thememequest.git
cd thememequest
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the API**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build the image
docker build -t meme-generator-api .

# Run the container
docker run -p 8000:8000 meme-generator-api
```

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 🛠 API Endpoints

### 1. Generate Memes

**POST** `/api/v1/generate-meme`

Generate AI-powered memes from a text prompt with direct HTTP image URLs.

**Request Body:**
```json
{
  "text_prompt": "cats being dramatic",
  "max_dimension": 500,
  "input_language": "en",
  "output_language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully generated 16 memes",
  "count": 16,
  "meme_list": [
    "http://localhost:8000/static/memes/memes_1748748652/meme_45675894.png",
    "http://localhost:8000/static/memes/memes_1748748652/meme_45675895.png"
  ],
  "run_id": "3410823",
  "meme_count": 16,
  "memes": [
    {
      "id": "45675894",
      "width": 300,
      "height": 315,
      "image_name": "https://supermeme-space-prd.ams3.cdn.digitaloceanspaces.com/templates/Angry baby.jpg",
      "captions": [
        {
          "x": 15,
          "y": 15,
          "width": 270,
          "height": 100,
          "text": "testing API fix with image URLs",
          "fontSize": 18
        }
      ],
      "top_header_caption": null,
      "bottom_header_caption": null
    }
  ],
  "generated_files": [
    {
      "filename": "meme_45675894.png",
      "file_path": "generated_memes\\memes_1748748652\\meme_45675894.png",
      "image_url": "http://localhost:8000/static/memes/memes_1748748652/meme_45675894.png",
      "meme_id": "45675894"
    }
  ],
  "output_directory": "generated_memes\\memes_1748748652",
  "generation_time": 23.31,
  "timestamp": "2025-06-01T09:00:58.743826"
}
```

### 2. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-06-01T09:00:58.743826"
}
```

### 3. Clear Token

**POST** `/api/v1/clear-token`

Clear saved authentication token for fresh authentication.

**Response:**
```json
{
  "success": true,
  "message": "Authentication token cleared successfully"
}
```

### 4. Root Information

**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "name": "Meme Generator API",
  "version": "1.0.0",
  "description": "AI-powered meme generation API using SuperMeme AI",
  "docs": "/docs",
  "health": "/health",
  "static_memes": "/static/memes",
  "timestamp": "2025-06-01T09:00:58.743826"
}
```

## 💡 Usage Examples

### cURL

```bash
# Generate memes
curl -X POST "http://localhost:8000/api/v1/generate-meme" \
  -H "Content-Type: application/json" \
  -d '{
    "text_prompt": "when you find a bug in production",
    "max_dimension": 500
  }'

# Health check
curl http://localhost:8000/health

# Clear token
curl -X POST http://localhost:8000/api/v1/clear-token

# Download a generated meme
curl -o my_meme.png "http://localhost:8000/static/memes/memes_1748748652/meme_45675894.png"
```

### Python

```python
import requests

# Generate memes
response = requests.post(
    "http://localhost:8000/api/v1/generate-meme",
    json={
        "text_prompt": "Monday morning mood",
        "max_dimension": 500,
        "input_language": "en",
        "output_language": "en"
    }
)

data = response.json()
print(f"Generated {data['count']} memes!")
print(f"Files saved in: {data['output_directory']}")

# Access the meme images directly
for i, meme_url in enumerate(data['meme_list'][:3], 1):
    print(f"Meme {i}: {meme_url}")
    
    # Download the image
    img_response = requests.get(meme_url)
    with open(f"downloaded_meme_{i}.png", "wb") as f:
        f.write(img_response.content)
```

### JavaScript

```javascript
// Generate memes
fetch('http://localhost:8000/api/v1/generate-meme', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text_prompt: 'debugging at 3am',
    max_dimension: 500
  })
})
.then(response => response.json())
.then(data => {
  console.log(`Generated ${data.count} memes!`);
  console.log(`Files saved in: ${data.output_directory}`);
  
  // Display memes in HTML
  data.meme_list.forEach((url, index) => {
    const img = document.createElement('img');
    img.src = url;
    img.alt = `Generated Meme ${index + 1}`;
    document.body.appendChild(img);
  });
});
```

### React Native

```javascript
// React Native usage
const MemeGenerator = () => {
  const [memes, setMemes] = useState([]);
  
  const generateMemes = async () => {
    const response = await fetch('http://localhost:8000/api/v1/generate-meme', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text_prompt: 'mobile app memes',
        max_dimension: 400
      })
    });
    
    const data = await response.json();
    setMemes(data.meme_list);
  };
  
  return (
    <View>
      {memes.map((url, index) => (
        <Image key={index} source={{uri: url}} style={{width: 300, height: 300}} />
      ))}
    </View>
  );
};
```

## ⚙️ Configuration

Environment variables can be set in a `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS Settings
ALLOWED_ORIGINS=["*"]
ALLOWED_METHODS=["*"]
ALLOWED_HEADERS=["*"]

# File Storage
OUTPUT_DIRECTORY=generated_memes
MAX_FILE_SIZE_MB=10

# SuperMeme AI Configuration (automatically managed)
SUPERMEME_API_URL=https://api.supermeme.ai
SUPABASE_URL=https://lyosvnajqhpnctlqsaoa.supabase.co
SUPABASE_API_KEY=<auto-generated>
MAIL_API_URL=https://api.mail.tm

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

## 🏗 Project Structure

```
thememequest/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── Dockerfile             # Docker configuration
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
├── API_RESPONSE_EXAMPLE.md # Detailed API response examples
├── test_api.py            # Manual API testing script
├── run.py                 # Alternative startup script
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Pydantic settings configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   └── memes.py       # Meme generation endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── token_manager.py     # JWT token storage and management
│   │   ├── temp_mail.py         # Mail.tm temporary email service
│   │   ├── token_generator.py   # OTP token generation and verification
│   │   └── meme_generator.py    # SuperMeme AI integration & image processing
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── meme_schemas.py      # Pydantic models and validation
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_memes.py        # Pytest unit tests
└── generated_memes/         # Output directory for generated memes (auto-created)
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Test the API manually
python test_api.py
```

## 🔧 Key Features & Implementation

### Image Processing Pipeline
- Downloads base images from SuperMeme CDN
- Applies text captions with PIL (Python Imaging Library)
- Adds stroke effects for better text readability
- Saves high-quality PNG files locally
- Serves images via FastAPI static file mounting

### API Response Format
- **`count`**: Number of memes generated
- **`meme_list`**: Array of direct HTTP URLs for immediate access
- **`generated_files`**: Detailed file information with paths and URLs
- **`memes`**: Raw meme data from AI with caption coordinates

### Error Handling & Validation
- Pydantic v2 field validators for robust data validation
- Automatic integer-to-string conversion for API compatibility
- Comprehensive HTTP status codes (400, 500, 503)
- Structured error responses with timestamps

## 🚦 Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input parameters or validation errors
- **500 Internal Server Error**: Unexpected server errors or processing failures
- **503 Service Unavailable**:  AI service issues or token problems

All errors return a consistent format:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-06-01T09:00:58.743826"
}
```

## 🔒 Security

- **Input Validation**: Comprehensive Pydantic validation with length limits
- **Rate Limiting**: Configurable request limits per minute
- **CORS Protection**: Configurable allowed origins and methods
- **Token Security**: Base64 encoding and secure file storage
- **File System Isolation**: Organized output directories with timestamps
- **Error Sanitization**: No sensitive data in error responses

## 🚀 Deployment

### Production Deployment

1. **Set environment variables**
```bash
export DEBUG=false
export API_HOST=0.0.0.0
export API_PORT=8000
export ALLOWED_ORIGINS='["https://yourdomain.com"]'
```

2. **Run with Gunicorn**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Use systemd service**
```bash
# Create /etc/systemd/system/meme-api.service
sudo systemctl enable meme-api
sudo systemctl start meme-api
```

### Docker Deployment

```bash
# Build and run
docker build -t meme-generator-api .
docker run -d -p 8000:8000 --name meme-api \
  -e DEBUG=false \
  -e ALLOWED_ORIGINS='["https://yourdomain.com"]' \
  meme-generator-api

# Docker Compose
version: '3.8'
services:
  meme-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - API_HOST=0.0.0.0
    volumes:
      - ./generated_memes:/app/generated_memes
```

### Cloud Deployment (AWS/GCP/Azure)

- Use container services (ECS, Cloud Run, Container Instances)
- Mount persistent volumes for generated memes
- Configure load balancers for scalability
- Set up monitoring and logging

## 📊 Monitoring & Logging

The API includes comprehensive observability:

- **Structured Logging**: Timestamped logs with log levels
- **Health Checks**: `/health` endpoint for monitoring systems
- **Request Tracking**: Automatic request/response logging
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Metrics**: Generation time tracking
- **File System Monitoring**: Directory creation and file count tracking

```python
# Example log output
2025-06-01 09:00:37,473 - app.routers.memes - INFO - Received meme generation request: 'testing API'
2025-06-01 09:00:44,502 - app.services.meme_generator - INFO - Saved token is valid!
2025-06-01 09:00:52,416 - app.services.meme_generator - INFO - Successfully generated 16 memes
2025-06-01 09:01:00,785 - app.routers.memes - INFO - Meme generation completed in 23.31 seconds
```

## 🌐 Integration Examples

### Web Application
```html
<!DOCTYPE html>
<html>
<head>
    <title>Meme Generator</title>
</head>
<body>
    <input type="text" id="prompt" placeholder="Enter meme text...">
    <button onclick="generateMemes()">Generate Memes</button>
    <div id="memes"></div>
    
    <script>
        async function generateMemes() {
            const prompt = document.getElementById('prompt').value;
            const response = await fetch('http://localhost:8000/api/v1/generate-meme', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text_prompt: prompt})
            });
            
            const data = await response.json();
            const memesDiv = document.getElementById('memes');
            memesDiv.innerHTML = '';
            
            data.meme_list.forEach(url => {
                const img = document.createElement('img');
                img.src = url;
                img.style.width = '300px';
                img.style.margin = '10px';
                memesDiv.appendChild(img);
            });
        }
    </script>
</body>
</html>
```

### Mobile App (Flutter)
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class MemeService {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  static Future<List<String>> generateMemes(String prompt) async {
    final response = await http.post(
      Uri.parse('$baseUrl/generate-meme'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text_prompt': prompt}),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['meme_list']);
    }
    throw Exception('Failed to generate memes');
  }
}
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the existing code style and patterns
4. **Add tests**: Ensure your changes are tested
5. **Update documentation**: Update README and API docs as needed
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**: Describe your changes and their benefits

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for new modules and classes
- Test your changes with `pytest`
- Update API documentation for new endpoints

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Mail.tm](https://mail.tm) for temporary email services
- [Pydantic](https://pydantic.dev/) for data validation
- [PIL/Pillow](https://pillow.readthedocs.io/) for image processing

## 📞 Support

If you encounter any issues or have questions:

1. **Check the API documentation**: http://localhost:8000/docs
2. **Review the logs**: Look for error details in the console output
3. **Test endpoints**: Use the provided test scripts (`test_api.py`)
4. **Check examples**: Review `API_RESPONSE_EXAMPLE.md` for expected formats
5. **Open an issue**: Create a GitHub issue with detailed information

## 📈 Performance

- **Generation Speed**: ~10 seconds for 16 high-quality memes
- **Concurrent Requests**: Supports multiple simultaneous requests
- **Memory Usage**: Efficient image processing with PIL
- **Storage**: Organized file system with timestamped directories
- **Scalability**: Stateless design for horizontal scaling

---

**Crafted with ❤️, Koushik Navuluri** | Made for the meme community 🎭✨

*Transform your ideas into memes with the power of AI!* 
