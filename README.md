# 🔮 Crystal Ball CI/CD

> **Kiroween 2025 Submission - Costume Contest Category**

An AI-powered code review system that predicts code quality issues **before deployment**. Built with Claude 3.5 AI and featuring a mystical, Halloween-themed interface that makes code review magical! ✨

![Crystal Ball Demo](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge&logo=anthropic)
![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
![Kiro](https://img.shields.io/badge/Built_with-Kiro-orange?style=for-the-badge)

---

## 🎃 What is Crystal Ball CI/CD?

Crystal Ball is an automated code quality prediction system that analyzes Pull Requests in real-time using Claude 3.5 AI. It catches security vulnerabilities, bugs, and code smells that manual reviews often miss - all wrapped in a stunning mystical interface.

### The Problem
- Manual code reviews miss critical security issues
- Problems discovered only after deployment
- No real-time feedback during development
- Security vulnerabilities slip through unnoticed

### The Solution
Crystal Ball uses AI to automatically analyze every Pull Request:
- 🤖 **Automatic Analysis** - Triggered via GitHub webhook on PR create/update
- 🔮 **AI Prediction** - Claude 3.5 analyzes code diff and assigns quality score (0-100)
- 🔍 **Issue Detection** - Finds bugs, security vulnerabilities, code smells
- ⚡ **Real-time Dashboard** - WebSocket broadcasts results to live frontend
- 🎨 **Color-coded Scores** - 🟢 ≥80 (safe), 🟡 60-79 (caution), 🔴 <60 (danger)

---

## 🎭 Kiroween Submission - How We Used Kiro

This project was **entirely built using Kiro** AI IDE for the Kiroween 2025 hackathon. Here's how Kiro's features powered our development:

### 📋 Spec-Driven Development
We used Kiro's `.kiro/specs/` directory to design the entire system architecture before writing code:
- **Design Spec** (`crystal-ball-cicd/design.md`) - System architecture, component interactions
- **Requirements Spec** (`crystal-ball-cicd/requirements.md`) - Detailed functional requirements
- **Tasks Spec** (`crystal-ball-cicd/tasks.md`) - Implementation roadmap
- **Production Hardening** (`production-hardening/requirements.md`) - Security and deployment specs

Kiro analyzed these specs and helped generate production-ready code that followed our exact requirements.

### 🤖 Agent Hooks & Vibe Coding
- Used Kiro's **agent hooks** to maintain consistent code patterns across backend modules
- **Vibe coding** helped rapidly prototype the mystical UI with Halloween theme
- Kiro's AI understood our "crystal ball fortune-teller" aesthetic and generated matching CSS animations

### 🔧 Multi-Technology Integration
Kiro seamlessly coordinated development across:
- **Backend**: Python, FastAPI, WebSockets, Anthropic Claude API
- **Frontend**: React, Vite, real-time WebSocket updates
- **DevOps**: GitHub webhooks, production deployment, environment management

### 🎨 UI/UX Excellence (Costume Contest Category)
Our mystical, Halloween-themed interface was refined with Kiro:
- **Crystal Ball Animation** - Floating orb with mist, lightning effects
- **Flying Ghosts** - Animated emoji sprites when predictions arrive
- **Creepster Font** - Custom Halloween typography
- **Mystical Glow Effects** - Pulsing gradients and shadow effects
- **Color-Coded Predictions** - Green (safe), Yellow (warning), Red (danger)

---

## ✨ Features

### For Developers
- **🔒 Security-First Analysis** - Detects SQL injection, XSS, hardcoded secrets, command injection
- **📊 Quality Metrics** - Code complexity, maintainability scores
- **💡 Actionable Recommendations** - Specific fixes for detected issues
- **📜 Historical Tracking** - View past predictions and trends
- **⚡ Real-time Updates** - Instant WebSocket notifications

### Mystical UI
- **🔮 Crystal Ball Visualization** - Animated orb showing prediction scores
- **👻 Ghost Mode** - Floating ghosts appear on new predictions
- **🎃 Halloween Theme** - Creepster font, mystical gradients, eerie animations
- **✨ Emoji Explosions** - Celebratory effects for good scores
- **🌙 Dark Mode** - Perfect for late-night coding sessions

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))
- **GitHub Personal Access Token**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/crystal-ball-cicd.git
cd crystal-ball-cicd
```

2. **Set up environment variables**
```bash
# Create .env file in project root
cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key

# Backend Configuration
BACKEND_PORT=8023

# Frontend Configuration
FRONTEND_PORT=5175
FRONTEND_URL=http://localhost:5175
EOF
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
python3 main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5175 to see the Crystal Ball dashboard! 🔮

---

## 🧪 Testing Without GitHub

Test the system locally using curl:

```bash
curl -X POST http://localhost:8023/test/send-prediction \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_score": 85,
    "mystical_message": "The spirits are pleased with your code!",
    "omens": [
      {
        "severity": "warning",
        "title": "Potential SQL Injection",
        "score": 7,
        "description": "String concatenation in query",
        "file": "backend/database.py"
      }
    ],
    "recommendations": [
      "Use parameterized queries",
      "Add input validation"
    ]
  }'
```

You should see the prediction appear on the dashboard in real-time! ✨

---

## 🌐 GitHub Webhook Setup

To analyze real Pull Requests, set up a GitHub webhook:

### Why Production Server?
GitHub webhooks require a **public URL** to send events. You have two options:

**Option 1: ngrok (for testing)**
```bash
ngrok http 8023
# Use the ngrok URL for webhook: https://abc123.ngrok.io/webhook/github
```

**Option 2: Production Server (recommended)**
Deploy to a server with a public IP or domain.

### Configure GitHub Webhook

1. Go to your repo → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `https://your-server.com/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: Use the value from `GITHUB_WEBHOOK_SECRET` in .env
5. **Events**: Select "Pull requests"
6. Click **Add webhook**

Now every PR will be automatically analyzed! 🎉

---

## 📁 Project Structure

```
crystal-ball-cicd/
├── .kiro/                      # Kiro specs directory (required for Kiroween)
│   └── specs/
│       ├── crystal-ball-cicd/
│       │   ├── design.md       # System architecture
│       │   ├── requirements.md # Functional requirements
│       │   └── tasks.md        # Implementation tasks
│       └── production-hardening/
│           └── requirements.md # Security & deployment
│
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Main server entry point
│   ├── ai_analyzer.py         # Claude AI integration
│   ├── github_handler.py      # GitHub webhook processor
│   ├── prediction_engine.py   # Score calculation logic
│   ├── websocket_manager.py   # WebSocket connection manager
│   ├── models.py              # Pydantic data models
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CrystalBall.jsx      # Main crystal ball animation
│   │   │   ├── OmensFeed.jsx        # Issues display
│   │   │   ├── Recommendations.jsx  # Fix suggestions
│   │   │   ├── History.jsx          # Past predictions
│   │   │   └── EmojiExplosion.jsx   # Celebration effects
│   │   ├── hooks/
│   │   │   └── useWebSocket.js      # WebSocket hook
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   └── package.json           # Node dependencies
│
├── .env                       # Environment variables
└── README.md                  # This file
```

---

## 🎯 API Endpoints

### Health Check
```bash
GET /health
```
Returns server status.

### GitHub Webhook
```bash
POST /webhook/github
```
Receives GitHub PR events (requires valid signature).

### WebSocket
```
ws://localhost:8023/ws
```
Real-time prediction updates.

### Test Endpoint
```bash
POST /test/send-prediction
```
Send test predictions for development.

---

## 🔮 How It Works

1. **Developer creates/updates PR** on GitHub
2. **GitHub webhook fires** → sends PR data to backend
3. **Backend fetches code diff** from GitHub API
4. **Claude AI analyzes** the code changes
5. **Prediction engine** calculates score (0-100)
6. **WebSocket broadcasts** result to all connected clients
7. **Frontend displays** mystical prediction with animations

---

## 🎨 UI Features Showcase

- **Mystical Crystal Ball** - Animated glass orb with mist and lightning
- **Flying Ghosts** - Ethereal sprites that emerge on new predictions
- **Color-Coded Scores** - Instant visual feedback
- **Omen Cards** - Beautiful cards showing detected issues with severity icons
- **Mystical Messages** - AI-generated fortune-teller style feedback
- **Creepster Font** - Custom Halloween typography
- **Smooth Animations** - CSS animations for ball floating, ghost flying, text glow

---

## 🛡️ Security Features

- **Input Validation** - All user inputs sanitized
- **Webhook Signature Verification** - HMAC validation
- **Environment Variables** - Secrets never in code
- **CORS Protection** - Restricted origins
- **Sensitive Data Redaction** - API keys filtered from logs

---

## 🏆 Built for Kiroween 2025

**Category**: Costume Contest - Haunting User Interface

This project showcases:
- ✅ Polished, Halloween-themed mystical UI
- ✅ Real-time WebSocket interactions
- ✅ AI-powered functionality
- ✅ Production-ready architecture
- ✅ Comprehensive use of Kiro's spec-driven development

---

## 📜 License

MIT License - Feel free to use this project as inspiration for your own AI-powered tools!

---

## 🙏 Acknowledgments

- **Kiro AI IDE** - For making this rapid development possible
- **Anthropic Claude** - For powerful code analysis capabilities
- **GitHub** - For webhook infrastructure
- **The Spirits** - For guiding our code to quality 👻

---

<div align="center">

### 🔮 May the Crystal Ball reveal only good omens in your code! 🔮

Built with 💜 for **Kiroween 2025**

</div>
