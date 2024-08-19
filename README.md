# PDF Chat Service

This project is a FastAPI-based web service that allows users to upload PDF documents, extract text, and interact with the content using natural language queries. The service integrates with the Gemini API for generating answers based on the extracted PDF content. It uses Redis for storing PDF data and caching query results, with a fallback to the filesystem when Redis is unavailable.

## Features

- **PDF Upload**: Upload and process PDF files.
- **Text Extraction** Extract text from uploaded PDFs.
- **Natural Language Queries**: Ask questions about the content of uploaded PDFs using Gemini API.
- **Caching**: Cache responses to questions for faster subsequent queries using Redis.
- **Fallback Storage**: Store PDF data on the filesystem when Redis is unavailable.

## Table of Contents

1. [Installation](#installation)
2. [Environment Setup](#environment-setup)
3. [API Endpoints](#api-endpoints)
4. [Usage Example](#usage-example)
5. [Configuring Constants for Gemini API Responses](#configuring-constants-for-gemini-api-responses)
6. [Testing](#testing)

## Installation

### Pre-requisites:
    - Python 3.9+
    - Redis (for caching; optional)
    - Virtualenv (recommended)
    - API Key for Gemini API

### Clone the repository:
```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

### Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate # For Linux/Mac
venv\Scripts\activate # For Windows
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup:
Create a `.env` file in the root directory with the following variables:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Redis setup(Optional):
If redis is not installed, you can install it via:
- MacOS: `brew install redis`
- Linux: `sudo apt-get install redis`
- Windows: [please check here](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/)

## API Endpoints
1. **Upload PDF**:
- **Endpoint**: `/v1/pdf`
- **Method**: `POST`
- **Description**: Upload a PDF file for processing.
- **Request**:
    - Content-Type: `multipart/form-data`
    - Parameter: `file` (PDF file)
- **Response**:
    - Status: `200 OK`
    - Content: `{"pdf_id": "unique_pdf_identifier"}`

Example cURL request:
```bash
curl -X POST "http://localhost:8000/v1/pdf" -F "file=@/path/to/your/file.pdf"
```

2. **Ask Question**:
- **Endpoint**: `/v1/pdf/{pdf_id}`
- **Method**: `POST`
- **Description**: Ask a question about the content of the uploaded PDF.
- **Request**:
    - Content-Type: `application/json`
    - Body: `{"message": "What is the main topic of this PDF?"}`
- **Response**:
    - Status: `200 OK`
    - Content: `{"answer": "Answer from Gemini API..."}`

Example cURL request:
```bash
curl -X POST "http://localhost:8000/v1/pdf/unique_pdf_identifier" -H "Content-Type: application/json" -d '{"message": "What is the main topic of this PDF?"}'
```

## Usage Example
1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
or basically run the `main.py` file in root directory.

2. **Upload a PDF**: Use the `/v1/pdf` endpoint to upload a PDF file and receive a `pdf_id`.
3. **Query the PDF**: Use the `/v1/pdf/{pdf_id}` endpoint to ask a question about the content of the uploaded PDF. The response will be generated using the Gemini API. Answers are cached for faster subsequent queries for 24 hours. If same query is asked within 24 hours, the response will be fetched from cache.

## Configuration for Gemini API Responses
In the `/core/config.py` file, you can modify the parameters to adjust the behavior of the Gemini API and the chatbot’s responses. Here’s how each section works:
- `TEXT_SIZE_LIMIT_MB`: The maximum size of the PDF file that can be uploaded. By default, it's set to 5MB. If you want to increase or decrease the limit, simply change the value(plaase note that gemini-flash model has 1 million token limit. So input size may be exceeded for very large files, and as the size increases, the time it takes to receive a response will take longer ):
```
TEXT_SIZE_LIMIT_MB = 10 # For 10MB limit
```

- `generation_config_`:
This configures how the responses are generated. The parameters here control the quality, randomness, and length of the response:
- `max_output_tokens`: The maximum number of tokens (words or word parts) in the output. Increase this for longer responses.
- `top_p`: Controls the diversity of the response by sampling from the top tokens whose probability mass adds up to p. Increase for more varied answers, lower for more focused responses.
- `temperature`: Controls randomness in generation. Higher values (closer to 1) produce more random results, while lower values (closer to 0) make the responses more deterministic.
```
generation_config_={
        "max_output_tokens": 800,
        "top_p": 0.9,
        "temperature": 0.6
    }
```
- `request_options_`:
- `timeout`: The maximum time in seconds to wait for a response from the Gemini API. Increase this if the API is slow to respond.
```
request_options_={
    "timeout": 10
}
```
- `safety_settings_`: This section filters out harmful content like hate speech or harassment. You can adjust the thresholds to change what types of content are blocked. By default, low and above levels of harm are blocked.
```
safety_settings_={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}
```
- `prompt_`: This string forms the base of the prompt sent to the Gemini API. You can modify it to change the tone or specificity of the bot’s instructions.


## Testing
Unit tests ensure that all components of the project function correctly, including PDF uploads, Redis caching, and interaction with the Gemini API.
To run the tests, basically run the `test_main.py` file in tests directory.
```bash
python tests/test_main.py
```
Please be ensure redis server is running before running the tests. Otherwise, if redis is unavailable, the tests will default to filesystem storage.


