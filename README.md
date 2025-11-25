# Smart Negotiator 🤖

An AI-powered negotiation chatbot for e-commerce, built with Streamlit, LangGraph, and multiple LLM providers including Google Gemini.

## ✨ Features

- **User Authentication**: Register and login to manage your account
- **Product Management**: View available products with prices and descriptions
- **AI Chatbot (Kiki Bot)**: Interactive negotiation assistant with LLM integration
- **Multi-Language Support**: Handles Telugu and English queries
- **RAG Engine**: Uses LangGraph and Sentence Transformers for intelligent recommendations
- **LLM Enhancement**: Google Gemini, OpenAI, or Anthropic for smart responses
- **Shopping Cart**: Add products to cart and place orders
- **Order History**: View past orders
- **Intelligent Negotiation**: AI-powered pricing strategies and discounts

## 🚀 Quick Start

```bash
# Start with Docker (recommended)
docker-compose up --build

# Or use the quick start script
./run.sh  # Linux/Mac
run.bat   # Windows

# Access at http://localhost:8501
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend Logic**: Python with LangGraph
- **Database**: MySQL
- **AI/ML**:
  - Sentence Transformers (embeddings)
  - LangGraph (workflow orchestration)
  - Google Gemini (currently active)
  - OpenAI GPT (alternative)
  - Anthropic Claude (alternative)
- **Deployment**: Docker + Docker Compose

## 📁 Project Structure

```
smartnegotiator/
├── streamlit_app.py          # Main Streamlit application
├── backend/
│   ├── rag_engine.py         # LangGraph RAG pipeline with LLM integration
│   └── .env                  # Environment variables (moved to root)
├── data/
│   ├── products.csv          # Product data
│   ├── competitors.csv       # Competitor data
│   └── policies.md           # Company policies
├── vectordb/                 # Vector database storage
├── .env                      # API keys and configuration
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Multi-container setup
├── init.sql                  # Database initialization
├── run.sh                    # Quick start script (Linux/Mac)
├── run.bat                   # Quick start script (Windows)
├── API_SETUP.md              # Comprehensive AI integration guide
├── DEPLOYMENT_GUIDE.md       # Sharing/deployment instructions
└── README.md                 # This file
```

## Installation & Setup

### Local Development

1. **Clone the repository** (if applicable) and navigate to the project directory.

2. **Create virtual environment**:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**:
   - Install MySQL on your system
   - Create a database named `smartnegotiator`
   - Run the `init.sql` script to create tables

5. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Access the app** at `http://localhost:8501`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the app** at `http://localhost:8501`

## 🧪 Testing & Verification

```bash
# Test AI integration
docker-compose exec app python -c "
from backend.rag_engine import rag_answer_with_llm
result = rag_answer_with_llm('What products do you have?', use_llm=True)
print('AI Response:', result)
"

# Test basic RAG
docker-compose exec app python -c "
from backend.rag_engine import rag_answer
result = rag_answer('test query')
print('Basic RAG:', result)
"

# Check API key loading
docker-compose exec app python -c "
import os
print('Gemini key loaded:', bool(os.getenv('GEMINI_API_KEY')))
"
```

## 📖 Usage

1. **Register/Login**: Create an account or log in
2. **Browse Products**: View available products with AI-powered descriptions
3. **Chat with Kiki Bot**: Ask questions or negotiate prices with AI assistance
4. **Add to Cart**: Select products to purchase
5. **Place Orders**: Complete your purchases with smart recommendations

### Example Conversations
- "What's the best smartphone for photography?"
- "Can you give me a discount on the iPhone?"
- "Show me products under ₹50,000"
- "What's your return policy?" (in Telugu or English)

## AI Features

### Current Setup (Gemini Active)
- **Google Gemini 2.0 Flash**: Active with free tier (15 RPM)
- **Smart Negotiation**: AI-powered pricing strategies
- **Natural Responses**: Context-aware, human-like replies
- **Multi-Provider Fallback**: Automatic switching between AI services

### Core Capabilities
- **Multi-language Support**: Handles Telugu and English queries
- **Intelligent Negotiation**: Offers discounts based on stock levels and context
- **RAG-powered Responses**: Retrieves relevant product information using vector similarity
- **Contextual Conversations**: Maintains conversation history
- **Dynamic Pricing**: Smart discount suggestions based on inventory and AI analysis

### AI Providers Supported
1. **Google Gemini** ✅ (currently active - free)
2. **OpenAI GPT** (premium option)
3. **Anthropic Claude** (alternative premium)
4. **Basic RAG** (fallback - always works)

## Database Schema

- `users`: User accounts
- `products`: Product catalog with embeddings
- `cart`: Shopping cart items
- `orders`: Order history
- `conversations`: Chat history

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# AI API Keys (add your keys here)
GEMINI_API_KEY=AIzaSyDeL-KWP7xvFz6xl7N9_4UEBa8S6H5TEAY  # Currently active
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database Configuration (Docker default)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=smartnegotiator
```

### Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up --build

# Restart after config changes
docker-compose restart app

# View logs
docker-compose logs app
```

### Local Development
```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up MySQL database
# ... (create database and run init.sql)

# Run application
streamlit run streamlit_app.py
```

## 📦 Sharing with Friends

Want to share your AI chatbot with friends? See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for complete instructions!

**Quick version:**
1. Share the entire `smartnegotiator/` folder
2. Remove your API key from `.env` (they get their own free Gemini key)
3. They run: `./run.sh` (Linux/Mac) or `run.bat` (Windows)

## 📚 Documentation

- **[API_SETUP.md](API_SETUP.md)**: Comprehensive AI integration guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: How to share and deploy
- **Database Schema**: MySQL tables for users, products, cart, orders, conversations
- **LangGraph Pipeline**: State-based RAG workflow with LLM enhancement

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly with the verification scripts above
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Google Gemini](https://ai.google.dev/)
- UI by [Streamlit](https://streamlit.io/)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)

## 🆘 Support

- **Issues**: Open an issue on GitHub
- **AI Setup**: See [API_SETUP.md](API_SETUP.md) for detailed configuration
- **Logs**: Use `docker-compose logs` for debugging
- **Testing**: Run the verification scripts above

---

**🎉 Your Smart Negotiator is now powered by Google Gemini AI!**