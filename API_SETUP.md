# Smart Negotiator - API Key Setup Guide

## Recent Updates

✅ **LangGraph State Schema Fixed**: Updated to use proper TypedDict state schema for compatibility with LangGraph >=0.1.0
✅ **LangGraph Entry Point Fixed**: Added `set_entry_point("embed_query")` for proper graph initialization
✅ **Gemini API Fully Integrated**: Complete compatibility with Google Gemini 2.0 Flash model
✅ **Multi-Provider LLM Support**: Automatic fallback between OpenAI, Gemini, and Anthropic

## Important Note: GitHub Copilot vs API Services

**GitHub Copilot** is an AI coding assistant that helps with writing code in your IDE (like VS Code). It does NOT provide API keys or services for external applications. Your Smart Negotiator app needs separate AI API services.

## AI Service Integration

This application supports optional AI enhancements using various providers. To enable advanced features, you'll need to obtain API keys from the respective services.

### Supported AI Services

#### 1. Google Gemini (Currently Active - Free Tier)
- **Purpose**: Google's AI model for natural language responses
- **Current Status**: ✅ **ACTIVE** with your API key
- **Model Used**: `gemini-2.0-flash` (fast, reliable, 15 RPM free)
- **Setup**:
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Sign in with your Google account
  3. Click "Create API key"
  4. Copy the API key (starts with `AIza`)

#### 2. OpenAI (Alternative - Paid)
- **Purpose**: Provides intelligent, natural language responses for better customer negotiation
- **Setup**:
  1. Go to [OpenAI Platform](https://platform.openai.com/)
  2. Create an account or sign in
  3. Navigate to API Keys section
  4. Create a new API key
  5. Copy the key (starts with `sk-`)

#### 3. Anthropic Claude (Alternative - Paid)
- **Purpose**: Alternative AI for responses
- **Setup**:
  1. Go to [Anthropic Console](https://console.anthropic.com/)
  2. Create an account
  3. Get your API key

#### 4. Hugging Face (For Embeddings)
- **Purpose**: Alternative embedding models
- **Setup**:
  1. Go to [Hugging Face](https://huggingface.co/)
  2. Create an account
  3. Go to Settings → Access Tokens
  4. Create a new token
  5. Copy the token

### Configuration

1. **Edit the `.env` file** in the root directory:
   ```bash
   # Replace with your actual API keys
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   GEMINI_API_KEY=AIzaSyDeL-KWP7xvFz6xl7N9_4UEBa8S6H5TEAY  # Currently active
   ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
   HUGGINGFACE_API_KEY=hf-your-actual-huggingface-key-here

   # Database Configuration (already configured)
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=password
   DB_NAME=smartnegotiator
   ```

2. **Restart your application** (no rebuild needed for key changes):
   ```bash
   docker-compose restart app
   ```

3. **Verify integration**:
   ```bash
   docker-compose exec app python -c "from backend.rag_engine import rag_answer_with_llm; print(rag_answer_with_llm('test', use_llm=True))"
   ```

### Features Enabled by API Keys

#### Current Setup (Gemini Active)
- **Gemini API**: ✅ **ACTIVE** - Using Google Gemini 2.0 Flash
- **Smart Responses**: Natural, persuasive negotiation replies
- **Free Tier**: 15 requests per minute included
- **Fallback System**: Automatic provider switching

#### Multi-Provider Intelligence
The app automatically selects the best available AI in this order:
1. **Google Gemini** (currently active - free)
2. **OpenAI GPT** (premium option)
3. **Anthropic Claude** (alternative premium)
4. **Basic RAG** (fallback - always works)

#### Without API Keys
- Basic RAG using sentence transformers
- Simple product matching and responses
- No AI-enhanced negotiation

#### With API Keys
- **Enhanced Responses**: Context-aware, natural language replies
- **Negotiation Intelligence**: Persuasive pricing strategies
- **Customer Engagement**: Professional, helpful communication
- **Dynamic Pricing**: Smart discount suggestions based on inventory

### Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Rotate keys regularly
- Monitor API usage to avoid unexpected charges

### Cost Considerations

#### Current Setup (Gemini)
- **Google Gemini**: Free tier (15 RPM), paid plans available
- **No credit card required** for basic usage
- **Rate Limits**: 15 requests per minute free tier

#### Other Providers
- **OpenAI**: ~$0.002 per 1K tokens (GPT-3.5-Turbo)
- **Anthropic Claude**: Usage-based pricing
- **Hugging Face**: Free tiers with rate limits

### Troubleshooting

#### API Key Issues
```bash
# Check if key is loaded
docker-compose exec app python -c "import os; print('Gemini key:', bool(os.getenv('GEMINI_API_KEY')))"

# Test API connectivity
docker-compose exec app python -c "from backend.rag_engine import rag_answer_with_llm; print(rag_answer_with_llm('test', use_llm=True))"
```

#### Common Issues
- **"No API key found"**: Check `.env` file and restart containers
- **Rate limit exceeded**: Wait or upgrade to paid plan
- **Model not found**: API may have updated - check available models
- **Import errors**: Ensure all packages are installed in container

#### Logs and Debugging
```bash
# View app logs
docker-compose logs app

# View database logs
docker-compose logs db

# Restart services
docker-compose restart
```

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│   RAG Engine     │───▶│  AI Providers   │
│                 │    │  (LangGraph)     │    │  Gemini/OpenAI  │
│ - Chat Interface│    │                  │    │  Claude/etc.    │
│ - Product Mgmt  │    │ - Embeddings     │    │                 │
│ - Cart/Orders   │    │ - Retrieval      │    │ - API Calls     │
└─────────────────┘    │ - Generation     │    └─────────────────┘
                       └──────────────────┘             │
┌─────────────────┐                           ┌─────────────────┐
│   MySQL DB      │◀──────────────────────────┤  Fallback RAG   │
│                 │                           │  (No API key)   │
│ - Users         │                           └─────────────────┘
│ - Products      │
│ - Conversations │
└─────────────────┘
```

### Development Notes

- **LangGraph Version**: >=0.1.0 (with state schema support)
- **Python Version**: 3.11+ (optimized for AI libraries)
- **Containerized**: Full Docker deployment with hot reload
- **Environment**: Production-ready with proper error handling