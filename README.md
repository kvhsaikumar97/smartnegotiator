# 🤖 Smart Negotiator - AI-Powered Shopping Assistant

An intelligent e-commerce chatbot that uses advanced AI to help customers negotiate prices and discover products through natural conversation.

![Smart Negotiator](https://img.shields.io/badge/AI-Powered-🤖-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11+-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## ✨ Features

### 🚀 **Core Features**
- **AI-Powered Negotiation**: Intelligent price negotiation using Google Gemini, OpenAI GPT, or Anthropic Claude
- **Semantic Product Search**: Find products using natural language queries with sentence embeddings
- **Real-time Chat Interface**: Modern Streamlit UI with persistent chat history
- **User Authentication**: Secure user registration and login with PBKDF2 password hashing
- **Shopping Cart**: Full e-commerce cart functionality
- **Order Management**: Complete order tracking system

### 🔒 **Security & Performance**
- **Enhanced Security**: PBKDF2 password hashing with salt, input validation, SQL injection prevention
- **Connection Pooling**: Efficient database connection management
- **Lazy Loading**: AI models load only when needed
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Logging**: Structured logging for debugging and monitoring

### 🛠 **Technical Architecture**
- **Service-Oriented Architecture**: Clean separation of concerns with dedicated service classes
- **Database Optimization**: Indexed queries, connection pooling, and efficient data retrieval
- **Modular Design**: Easy to extend and maintain
- **Docker Support**: Containerized deployment for easy sharing

## 🏗️ Architecture Overview

```
├── frontend/          # React-based frontend (optional)
├── backend/           # Python backend services
│   ├── config.py      # Configuration and database management
│   ├── user_service.py    # User authentication & management
│   ├── product_service.py # Product and cart operations
│   ├── conversation_service.py # Chat and negotiation logic
│   └── rag_engine.py  # AI-powered search and responses
├── data/             # Product data and policies
├── streamlit_app.py  # Main Streamlit application
├── docker-compose.yml # Container orchestration
└── requirements.txt  # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Python 3.11+ (if running locally)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd smartnegotiator
```

### 2. Environment Configuration
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Launch with Docker (Recommended)
```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the Application
- **Main App**: http://localhost:8501
- **Database**: localhost:3306 (MySQL)

### 5. Initial Setup
1. Load products: Click "📥 Load Products" in the sidebar
2. Rebuild embeddings: Click "🔄 Rebuild Embeddings" for AI search
3. Register/Login and start chatting!

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=smartnegotiator

# AI API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-anthropic-key

# App Settings
MAX_LOGIN_ATTEMPTS=5
SESSION_TIMEOUT=3600
ITEMS_PER_PAGE=10
```

### API Keys Setup
1. **Google Gemini**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **OpenAI**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Anthropic**: Get from [Anthropic Console](https://console.anthropic.com/)

## 📊 Database Schema

### Core Tables
- **users**: User accounts with secure password storage
- **products**: Product catalog with embeddings for AI search
- **cart**: Shopping cart items
- **orders**: Order history and tracking
- **conversations**: Chat message history
- **order_items**: Detailed order line items

### Indexes & Performance
- Full-text search on product descriptions
- Optimized indexes on frequently queried columns
- Foreign key constraints for data integrity

## 🤖 AI Features

### Negotiation Intelligence
The chatbot provides context-aware negotiation responses based on:
- **Stock Levels**: Higher discounts for lower stock items
- **Product Context**: Relevant product information in responses
- **User History**: Personalized recommendations

### Supported LLMs
1. **Google Gemini 2.0 Flash** (Recommended - Fast & Cost-effective)
2. **OpenAI GPT-3.5 Turbo** (Balanced performance)
3. **Anthropic Claude Haiku** (High-quality responses)

## 🔍 Key Improvements Made

### Security Enhancements
- ✅ **PBKDF2 Password Hashing**: Replaced SHA256 with salted PBKDF2
- ✅ **Input Validation**: Email, phone, and general input sanitization
- ✅ **SQL Injection Prevention**: Parameterized queries throughout
- ✅ **Connection Pooling**: Efficient database connection management

### Performance Optimizations
- ✅ **Lazy Model Loading**: AI models load only when needed
- ✅ **Database Indexing**: Optimized queries with proper indexes
- ✅ **Connection Pooling**: Reduced connection overhead
- ✅ **Caching Strategy**: Smart caching for embeddings and results

### Code Quality Improvements
- ✅ **Service Architecture**: Clean separation of business logic
- ✅ **Error Handling**: Comprehensive exception handling
- ✅ **Logging**: Structured logging throughout the application
- ✅ **Type Hints**: Added type annotations for better code clarity
- ✅ **Modular Design**: Easy to extend and maintain

### User Experience Enhancements
- ✅ **Modern UI**: Improved Streamlit interface with better navigation
- ✅ **Loading States**: Visual feedback for long operations
- ✅ **Error Messages**: User-friendly error handling
- ✅ **Responsive Design**: Better mobile and desktop experience

## 🧪 Testing

### Automated Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Product loading from CSV
- [ ] Embedding rebuild process
- [ ] AI chat responses
- [ ] Cart functionality
- [ ] Order placement
- [ ] Negotiation logic

## 🚀 Deployment

### Production Deployment
```bash
# Build for production
docker-compose -f docker-compose.prod.yml up --build

# Or use the deployment scripts
./run.sh  # Linux/Mac
run.bat   # Windows
```

### Environment-Specific Configs
- **Development**: `docker-compose.yml`
- **Production**: `docker-compose.prod.yml`
- **Testing**: `docker-compose.test.yml`

## 📈 Monitoring & Analytics

### Built-in Analytics
- User session tracking
- Product view analytics
- Conversation analytics
- Order tracking and reporting

### Logs
```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run tests: `pytest`
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Create a Pull Request

### Code Standards
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit hooks**: Automated quality checks

## 📝 API Documentation

### Service Classes
- **UserService**: User management operations
- **ProductService**: Product and cart operations
- **ConversationService**: Chat and negotiation logic
- **RAGEngine**: AI-powered search and responses

### Key Methods
```python
# User operations
UserService.authenticate_user(email, password)
UserService.register_user(user_data)

# Product operations
ProductService.get_all_products()
ProductService.add_to_cart(user_email, product_id)

# AI operations
rag_answer(query, k=3)
rag_answer_with_llm(query, use_llm=True)
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart db
```

**AI Model Loading Issues**
```bash
# Clear cache and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

**Port Already in Use**
```bash
# Change ports in docker-compose.yml
ports:
  - "8502:8501"  # Change host port
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web app framework
- **Sentence Transformers**: For semantic search capabilities
- **LangGraph**: For workflow orchestration
- **Google, OpenAI, Anthropic**: For powerful LLM APIs

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)

---

**Built with ❤️ using AI and modern web technologies**
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