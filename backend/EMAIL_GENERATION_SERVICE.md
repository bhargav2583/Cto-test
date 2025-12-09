# Email Generation Service Documentation

## Overview

The Email Generation Service provides AI-powered professional cover letter generation using OpenAI's GPT models. It combines CV text, job descriptions, and job titles to create personalized, professional cover letters with appropriate subject lines.

## Architecture

### Components

1. **LLM Provider Interface** (`llm_provider.py`)
   - Abstract base class for pluggable LLM implementations
   - Allows switching between different AI providers (OpenAI, Anthropic, etc.)

2. **OpenAI Provider** (`openai_provider.py`)
   - Concrete implementation using OpenAI's API
   - Handles async API calls, error handling, and response parsing

3. **Prompt Templates** (`prompts.py`)
   - Configurable prompt templates for different tones
   - Separate prompts for body and subject line generation

4. **Email Service** (`email_service.py`)
   - Main service orchestrating cover letter generation
   - Implements fallback mechanism when LLM fails
   - Combines body and subject generation

5. **API Endpoint** (`api/email.py`)
   - REST API endpoint at `POST /api/email/preview`
   - Request/response validation with Pydantic schemas

## Environment Variables

### Required

- `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-...`)

### Optional

- `OPENAI_MODEL`: Model to use (default: `gpt-3.5-turbo`)
  - Options: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`
  
- `LLM_TEMPERATURE`: Temperature for generation, 0.0-2.0 (default: `0.7`)
  - Lower values (0.0-0.5): More deterministic, focused
  - Medium values (0.5-1.0): Balanced creativity and consistency
  - Higher values (1.0-2.0): More creative and varied
  
- `LLM_MAX_TOKENS`: Maximum tokens for generation (default: `1500`)
  - Typical cover letter uses 300-600 tokens

## API Endpoint

### POST `/api/email/preview`

Generate a professional cover letter preview.

#### Request Body

```json
{
  "cv_text": "Software engineer with 5 years of experience...",
  "job_title": "Senior Software Engineer",
  "job_description": "We are looking for an experienced software engineer...",
  "company_name": "TechCorp Inc.",  // Optional
  "tone": "professional"             // Optional: professional, enthusiastic, formal
}
```

#### Response

```json
{
  "subject": "Application for Senior Software Engineer Position at TechCorp Inc.",
  "body": "Dear Hiring Manager,\n\nI am writing to express my strong interest...",
  "metadata": {
    "model": "gpt-3.5-turbo",
    "tone": "professional",
    "tokens_body": "350",
    "tokens_subject": "20",
    "total_tokens": "370"
  }
}
```

#### Error Responses

**503 Service Unavailable**
```json
{
  "detail": "Email generation service is not configured. Please set OPENAI_API_KEY environment variable."
}
```

**400 Bad Request**
```json
{
  "detail": [
    {
      "loc": ["body", "cv_text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to generate email preview: <error message>"
}
```

## Tone Options

### Professional (default)
- Confident and competent tone
- Balanced between formal and approachable
- Highlights experience and skills objectively

### Enthusiastic
- Shows genuine interest and passion
- More engaging and personable
- Maintains professionalism while expressing excitement

### Formal
- Highly traditional business etiquette
- Emphasizes qualifications formally
- Most conservative option

## Features

### 1. Async/Streaming Support
- All LLM calls are asynchronous using `AsyncOpenAI`
- Non-blocking API requests for better performance

### 2. Fallback Mechanism
- If LLM fails, returns a professional template-based cover letter
- Ensures endpoint always returns usable content
- Fallback indicated in response metadata

### 3. Error Handling

#### LLM Provider Errors
- API key invalid or missing
- Rate limits exceeded
- Network timeouts
- Model unavailable

All LLM errors trigger the fallback mechanism with appropriate logging.

#### Service Errors
- Invalid input parameters (caught by Pydantic validation)
- Service configuration errors (503 status)
- Unexpected errors (500 status with error details)

### 4. Prompt Personalization
- Automatically incorporates company name when provided
- Adjusts tone based on selection
- Aligns CV experience with job requirements
- Generates contextually appropriate subject lines

## Usage Examples

### Python Client

```python
import httpx

async def generate_cover_letter():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/email/preview",
            json={
                "cv_text": "Senior developer with 7 years experience...",
                "job_title": "Lead Backend Engineer",
                "job_description": "Looking for a technical leader...",
                "company_name": "StartupXYZ",
                "tone": "enthusiastic"
            }
        )
        return response.json()
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/email/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Experienced software engineer...",
    "job_title": "Software Engineer",
    "job_description": "Build scalable systems...",
    "tone": "professional"
  }'
```

### JavaScript/TypeScript

```typescript
async function generateCoverLetter(data: EmailPreviewRequest) {
  const response = await fetch('/api/email/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  
  return await response.json();
}
```

## Testing

### Running Tests

```bash
# Install test dependencies
cd backend
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_email_service.py -v
```

### Test Coverage

The test suite includes:

1. **Prompt Assembly Tests**
   - Basic prompt building
   - Company name personalization
   - Different tone variations
   - Subject line generation

2. **Service Logic Tests**
   - Successful generation flow
   - LLM failure fallback
   - Partial failure handling
   - Parameter passing validation

3. **Provider Tests**
   - OpenAI initialization
   - Successful API calls
   - Error handling (API errors, network issues)
   - Edge cases (empty content, missing usage data)

### Mocking Strategy

All tests mock the LLM provider to:
- Avoid API costs during testing
- Ensure deterministic test results
- Test error handling without triggering real errors

## Adding New LLM Providers

To add a new LLM provider (e.g., Anthropic Claude):

1. Create new provider class:

```python
from .llm_provider import LLMProvider, LLMProviderError

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet"):
        # Initialize Anthropic client
        pass
    
    async def generate_completion(self, prompt: str, **kwargs):
        # Implement Anthropic API call
        pass
```

2. Update configuration:

```python
# config.py
anthropic_api_key: str | None = None
anthropic_model: str = Field(default="claude-3-sonnet")
```

3. Update email service factory:

```python
# api/email.py
def get_email_service() -> EmailGenerationService:
    settings = get_settings()
    
    if settings.anthropic_api_key:
        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
    elif settings.openai_api_key:
        provider = OpenAIProvider(api_key=settings.openai_api_key)
    else:
        raise HTTPException(...)
    
    return EmailGenerationService(provider)
```

## Performance Considerations

### Token Usage
- Average cover letter: 300-600 tokens
- Subject line: 15-30 tokens
- Total per request: ~350-650 tokens

### Response Time
- OpenAI API latency: 2-5 seconds
- Total endpoint response: 3-7 seconds
- Async architecture prevents blocking

### Cost Estimation (GPT-3.5-turbo)
- Input: ~$0.0005 per request (500 tokens @ $0.001/1K)
- Output: ~$0.0006 per request (300 tokens @ $0.002/1K)
- Total: ~$0.0011 per cover letter

### Optimization Tips
1. Cache common CV/job combinations (future enhancement)
2. Use streaming for real-time feedback (future enhancement)
3. Batch multiple requests when possible
4. Monitor token usage via metadata

## Security Considerations

1. **API Key Protection**
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **Input Validation**
   - All inputs validated by Pydantic schemas
   - Length limits prevent abuse
   - Sanitization handled by OpenAI API

3. **Rate Limiting** (recommended)
   - Implement rate limiting to prevent abuse
   - Use API gateway or middleware
   - Monitor usage patterns

4. **Error Messages**
   - Don't expose sensitive information in errors
   - Log detailed errors server-side
   - Return generic messages to clients

## Monitoring and Logging

### Key Metrics to Track
- Request volume and frequency
- Token usage and costs
- Error rates by type
- Response times
- Fallback usage frequency

### Log Levels
- `INFO`: Successful generations, token usage
- `WARNING`: Fallback used, rate limits approaching
- `ERROR`: LLM failures, unexpected errors

### Example Log Output
```
INFO: Generating cover letter for position: Senior Developer, tone: professional
INFO: Completion generated successfully. Tokens used: 370, Finish reason: stop
```

## Troubleshooting

### Common Issues

**"Service not configured" error**
- Check `OPENAI_API_KEY` is set in environment
- Verify key format (starts with `sk-`)
- Check `.env` file is loaded

**High latency**
- Check network connectivity to OpenAI
- Consider using GPT-3.5 instead of GPT-4
- Monitor OpenAI status page

**Quality issues**
- Adjust temperature (lower for consistency)
- Try different tone settings
- Ensure CV and job description are detailed

**Token limit exceeded**
- Reduce `LLM_MAX_TOKENS` setting
- Shorten input text (CV/job description)
- Use more concise prompts

## Future Enhancements

1. **Streaming Support**
   - Real-time generation feedback
   - Better UX for long generations

2. **Caching Layer**
   - Redis cache for similar requests
   - Reduce costs and latency

3. **A/B Testing**
   - Compare different prompts
   - Optimize tone effectiveness

4. **Fine-tuning**
   - Custom model for cover letters
   - Improved quality and cost

5. **Multi-language Support**
   - Detect CV language
   - Generate in appropriate language

6. **PDF/DOCX Export**
   - Format cover letters
   - Download ready-to-send files
