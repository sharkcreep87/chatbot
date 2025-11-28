# ChatterMate Pro - Modern AI Chatbot Service

A modern, feature-rich AI chatbot service with beautiful UI/UX and powerful capabilities.

## ✨ Features

### Core Features
- 🤖 **Multi-AI Provider Support** - OpenAI GPT-4, Anthropic Claude, and more
- 💬 **Real-time Chat** - WebSocket-based instant messaging
- 🎨 **Modern UI/UX** - Beautiful, responsive design with dark mode
- 📝 **Rich Text Support** - Markdown, code highlighting, syntax highlighting
- 📚 **Knowledge Base** - Upload PDFs and create searchable knowledge bases
- 💾 **Conversation History** - Persistent chat history with search
- 🔐 **Authentication** - Secure user management and sessions
- 📊 **Analytics Dashboard** - Usage insights and metrics

### Knowledge Base Features
- 📄 **PDF Upload** - Upload and process PDF documents
- 🔍 **Semantic Search** - Vector-based search with embeddings
- 🧠 **Context-Aware AI** - AI uses knowledge base for accurate responses
- 📦 **Multiple Knowledge Bases** - Organize documents by topic
- ⚡ **Automatic Processing** - Text extraction and chunking
- 📈 **Processing Status** - Track document processing in real-time
- 💡 **Smart Retrieval** - Top relevant chunks for each query

### Advanced Features
- 📈 **Usage Analytics** - Track conversations, messages, and tokens
- 📊 **Activity Charts** - Visualize usage over time
- 🎯 **Model Statistics** - See which AI models you use most
- 🎨 **Theme Customization** - Dark mode and theme persistence
- 🔄 **Context Awareness** - Maintains conversation context
- ⚡ **Streaming Responses** - Real-time AI response streaming

### 🏢 Multivendor & Subscription Features
- 💼 **Multi-Tenancy** - Support for multiple vendors/organizations
- 💳 **Subscription Plans** - 4 pricing tiers (Free, Basic, Pro, Enterprise)
- 📊 **Usage Tracking** - Real-time monitoring of all usage metrics
- ⚠️ **Limit Enforcement** - Automatic limits based on subscription tier
- 🎨 **Vendor Branding** - Custom logos and colors per vendor
- 📈 **Usage Dashboard** - Visual usage and limits tracking
- 💰 **Flexible Billing** - Monthly and yearly billing cycles
- 🔒 **Role-Based Access** - User, Vendor Admin, Super Admin roles

## 🏗️ Architecture

```
chatbot/
├── backend/          # FastAPI backend service
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core configuration
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── websocket/# WebSocket handlers
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   └── package.json
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd chatbot
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys
uvicorn app.main:app --reload
```

3. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

4. **Docker Setup (Alternative)**
```bash
docker-compose up -d
```

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database
DATABASE_URL=sqlite:///./chatbot.db

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎯 Usage

1. Open the frontend at `http://localhost:5173`
2. Create an account or sign in
3. Start chatting with the AI
4. Customize your experience in settings
5. View analytics in the dashboard

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **WebSockets** - Real-time communication
- **JWT** - Authentication
- **OpenAI/Anthropic SDKs** - AI integration

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Beautiful components
- **React Query** - Data fetching
- **Zustand** - State management
- **Socket.io Client** - WebSocket client

## 📝 License

MIT License - feel free to use this project for your own purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For support, please open an issue or contact the maintainers.

## 💳 Subscription Plans

ChatterMate Pro offers flexible subscription plans to match your needs:

| Feature | Free | Basic | Pro | Enterprise |
|---------|------|-------|-----|------------|
| **Price** | $0/month | $29/month | $99/month | $499/month |
| **Conversations/month** | 50 | 500 | 5,000 | 100,000 |
| **Messages/month** | 500 | 5,000 | 50,000 | 1,000,000 |
| **Tokens/month** | 25,000 | 250,000 | 1,000,000 | 10,000,000 |
| **Knowledge Bases** | 1 | 5 | 20 | 100 |
| **Documents** | 5 | 50 | 200 | 1,000 |
| **Storage** | 50MB | 500MB | 2GB | 10GB |
| **Team Members** | 1 | 3 | 10 | 100 |
| **AI Models** | GPT-3.5 | GPT-3.5, GPT-4 | All Models | All Models |
| **Analytics** | ❌ | ✅ | ✅ | ✅ |
| **API Access** | ❌ | ❌ | ✅ | ✅ |
| **Custom Branding** | ❌ | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ | ✅ |

### Setting Up Subscription Plans

After deploying the backend, run the seed script to create default plans:

```bash
cd backend
python -m app.scripts.seed_plans
```

This will create the 4 default subscription tiers in your database.

## 🏢 Multivendor Setup

### Creating a Vendor

Users can create a vendor organization through the API or UI:

```bash
POST /api/vendor/vendors
{
  "name": "My Company",
  "email": "admin@mycompany.com",
  "description": "Our AI chatbot service"
}
```

The user who creates the vendor automatically becomes the vendor admin.

### Vendor Features

- **Custom Branding**: Set logo, primary and secondary colors
- **Usage Tracking**: Monitor all resource usage in real-time
- **Subscription Management**: Upgrade/downgrade plans anytime
- **Team Management**: Add multiple users to your organization

