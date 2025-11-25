# 🚀 Smart Negotiator - Deployment Guide for Friends

## 🎁 What to Share

Send your friend the **entire project folder** (`smartnegotiator/`) with these modifications:

### 1. Remove Your API Key (Important!)
**Before sharing, edit `.env`:**
```bash
# Remove your real key and add placeholder
GEMINI_API_KEY=your-friend-should-get-their-own-key-here
```

### 2. Include These Files:
- ✅ All Python files (`*.py`)
- ✅ `requirements.txt`
- ✅ `docker-compose.yml`
- ✅ `Dockerfile`
- ✅ `init.sql`
- ✅ `data/` folder (products, competitors)
- ✅ `.env` (with placeholder API key)
- ✅ `API_SETUP.md` (instructions)
- ✅ `README.md` (overview)

## 🐳 Option 1: Docker (Easiest - Recommended)

### Prerequisites:
- Docker Desktop installed
- 4GB+ RAM available
- Internet connection

### Steps for Your Friend:

1. **Extract the project folder**

2. **Get a Gemini API key** (free):
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create API key
   - Edit `.env` file and replace:
     ```
     GEMINI_API_KEY=your-actual-key-here
     ```

3. **Open terminal in project folder**:
   ```bash
   cd smartnegotiator
   ```

4. **Start the app**:
   ```bash
   docker-compose up --build
   ```

5. **Wait for startup** (first time takes 2-3 minutes)

6. **Open browser**: http://localhost:8501

## 🐍 Option 2: Local Python (Alternative)

### Prerequisites:
- Python 3.11+ installed
- MySQL installed and running
- Git (optional)

### Steps:

1. **Extract project and navigate**:
   ```bash
   cd smartnegotiator
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL database**:
   - Install MySQL if not installed
   - Create database: `smartnegotiator`
   - Run the SQL script: `mysql -u root -p smartnegotiator < init.sql`

5. **Get API key** (same as Docker option)

6. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔧 Troubleshooting

### Docker Issues:
```bash
# If port 8501 is busy
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs app

# Clean rebuild
docker-compose down -v
docker-compose up --build
```

### Python Issues:
```bash
# Update pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### API Key Issues:
- Make sure `.env` file exists in project root
- Verify API key starts with `AIza`
- Check internet connection for API calls

## 📱 What Your Friend Gets:

- **Complete AI Chatbot**: Negotiates prices intelligently
- **Product Catalog**: Browse and search products
- **Shopping Features**: Cart, orders, user accounts
- **Multi-language**: English and Telugu support
- **Smart AI**: Uses Google Gemini for responses

## 🎯 Quick Test:

After setup, test with:
- Register a new account
- Chat: "What products do you have?"
- Chat: "Can you give me a discount?"

## 📞 Support:

If your friend has issues:
1. Check the logs: `docker-compose logs app`
2. Verify API key in `.env`
3. Ensure Docker has enough resources
4. Try the troubleshooting steps above

## 🔐 Security Notes:

- The app runs locally (no data sent to you)
- API calls go directly to Google (your friend pays for usage)
- Database is local (SQLite/MySQL on their machine)
- No personal data is shared

---

**🎉 Your friend will have their own AI-powered negotiation chatbot!** 🤖✨</content>
<parameter name="filePath">/Users/saikumarkaparaju/Downloads/smartnegotiator/DEPLOYMENT_GUIDE.md