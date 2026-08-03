# 🗳️ VoteReady — Personalized Election Readiness Platform

> **Your Vote, Your Voice** | आपका वोट, आपकी आवाज़

VoteReady is an AI-powered election readiness platform designed to help Indian citizens understand the voting process through personalized guidance, interactive simulations, readiness tracking, and multilingual assistance.

The system combines AI agents, structured election workflows, and accessibility-focused design to make election information easier to understand and act upon.

**Built for PromptWars 2026 — Election Process Assistant vertical**

---

## 🎯 Chosen Vertical

**Election Process Assistant** — Create an assistant that helps users 
understand the election process, timelines, and steps in an 
interactive and easy-to-follow way.

---

## 💡 Approach and Logic

### The Problem
Election information is often fragmented across government websites, documents, and multiple platforms.

First-time voters especially struggle with understanding:
- registration processes
- eligibility requirements
- election timelines
- polling procedures

### Our Solution
VoteReady goes beyond a chatbot. It's a **voter activation platform** 
with three key differentiators:

1. **Voter Readiness Tracker** — A gamified progress checklist that 
   tracks what the user has completed. Progress ring on the dashboard 
   creates accountability and motivation.

2. **Election Day Simulator** — An interactive walkthrough where users 
   practice the polling day experience through scenario-based learning. 
   "You arrive at the booth. What do you do first?"

3. **Hyper-Local Impact Data** — Constituency-level statistics showing 
   how close elections can be. "This seat was decided by 847 votes."

### Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (index.html)             │
│   Language Select → Onboarding → Dashboard  │
│   Election Detail → Simulator → Chat Widget │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────┐
│           FastAPI Backend                    │
│                                             │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │
│  │Orchestr-│ │ Process  │ │ Eligibility  │ │
│  │  ator   │ │  Guide   │ │   Agent      │ │
│  └────┬────┘ └────┬─────┘ └──────┬───────┘ │
│       │           │              │          │
│  ┌────┴────┐ ┌────┴─────┐ ┌─────┴───────┐ │
│  │Timeline │ │Simulator │ │  Services   │ │
│  │ Agent   │ │  Agent   │ │ Layer       │ │
│  └─────────┘ └──────────┘ └─────────────┘ │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Google Cloud Services               │
│                                             │
│  Gemini 2.5 │ Maps API │ Translate │Firestore │
│  (Vertex)  │          │    API    │          │
└─────────────────────────────────────────────┘

## Agent Responsibilities

### Orchestrator Agent
Coordinates user requests and routes tasks.

### Eligibility Agent
Determines voter readiness based on profile information.

### Timeline Agent
Generates election-related schedules and reminders.

### Process Guide Agent
Explains voting procedures step-by-step.

### Simulator Agent
Creates interactive election-day scenarios.

```

## Why Agentic AI?

A traditional chatbot can answer election-related questions.

VoteReady requires multiple reasoning workflows:

1. Understand the user's voter profile.
2. Identify relevant election processes.
3. Generate personalized guidance.
4. Simulate real-world voting scenarios.
5. Provide context-aware responses.

The system uses specialized agents instead of a single conversational model to handle these different responsibilities.

### User Paths
The app delivers four distinct experiences based on user profile:

| User Type | Age | Voter ID | Experience |
|-----------|-----|----------|------------|
| Under-18 | <18 | — | Countdown to eligibility, pre-registration education |
| First-Time Voter | 18-21 | No | Guided hand-holding, "Your First Vote" section |
| Registered Voter | Any | Yes | Dashboard with booth finder, timeline, checklist |
| NRI Voter | Any | — | Form 6A process, overseas voting rules |

---

## ⚙️ How the Solution Works

### User Flow
1. **Language Selection** — Choose English or Hindi
2. **Onboarding** — Enter name, age, state, district, voter ID (optional)
3. **Dashboard** — Personalized view with eligibility status, upcoming 
   elections, readiness tracker, turnout charts, and impact data
4. **Election Detail** — Click any election to see interactive timeline, 
   step-by-step process guide, and polling booth finder
5. **Simulator** — Practice election day through 6 interactive scenarios
6. **Chat** — Floating AI assistant for open-ended election questions

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check for Cloud Run |
| GET | / | Serve frontend SPA |
| POST | /api/onboard | User registration + eligibility check |
| GET | /api/elections | Upcoming elections by state |
| GET | /api/election/{type} | Detailed election info + process steps |
| GET | /api/polling-booth | Find nearest booths via Google Maps |
| POST | /api/chat | Context-aware AI assistant |
| GET | /api/stats | Voter turnout data for charts |
| GET | /api/simulate | Election day scenarios |
| POST | /api/simulate/check | Check simulator answers |
| GET | /api/checklist | Get readiness progress |
| PUT | /api/checklist | Update checklist item |

### Google Services Integration
| Service | Purpose | Why Essential |
|---------|---------|---------------|
| Gemini 2.5 (Vertex AI) | Conversational AI, personalized guidance, simulator feedback | Core intelligence — removing it breaks personalization and chat |
| Google Maps API | Polling booth finder with interactive map | Real utility — voters need to find their booth |
| Cloud Translation API | English ↔ Hindi bilingual support | Accessibility — 500M+ Hindi speakers need native language |
| Firestore | User profiles, checklist progress, response cache | Persistence — removing it breaks progress tracking |
| Cloud Run | Serverless deployment | Production hosting with auto-scaling |

---

## 🔒 Security Implementation
- Input sanitization on all user-provided fields (XSS, SQL injection, prompt injection)
- Rate limiting: 10 requests/minute per IP via slowapi
- Request body size limit: 1KB maximum
- CORS restricted to specific origins
- Content-Security-Policy headers on all responses
- X-Frame-Options: DENY
- API keys stored in environment variables, never in code
- Gemini system prompt hardened against prompt injection
- No internal error details exposed to clients

## Responsible AI Considerations

VoteReady is designed as a neutral civic education assistant.

The system:

- Does not recommend political parties or candidates.
- Does not influence voting decisions.
- Separates factual information from generated explanations.
- Communicates assumptions and limitations clearly.
- Uses structured election information rather than generating unsupported claims.

The goal is to improve voter awareness, not influence voter choices.

## ♿ Accessibility Features
- Bilingual: English and Hindi
- Font size toggle (regular/large)
- High contrast mode
- Semantic HTML with proper heading hierarchy
- ARIA labels on all interactive elements
- Keyboard navigation support
- Skip-to-content link
- Screen reader compatible (role="log", aria-live)
- Color contrast: WCAG AA (4.5:1 ratio)
- Loading and error states — no blank screens

## 🧪 Testing
Run tests with:
```bash
pytest tests/ -v
```

Test coverage includes:
- Input validation and sanitization (XSS, SQL injection, prompt injection)
- Eligibility logic for all 5 voter categories
- All API endpoints (valid, invalid, edge cases)
- Orchestrator intent classification
- Data file integrity (all states, bilingual content, no nulls)
- Security header verification
- Response format consistency

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Google Cloud project with enabled APIs
- gcloud CLI authenticated

### Local Development
```bash
# Clone the repository
git clone https://github.com/arunreddy-co/election-assistant.git
cd election-assistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run locally
uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

### Deploy to Cloud Run
```bash
gcloud run deploy voteready \
    --source . \
    --region asia-south1 \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=your-project-id"
```

---

## 📋 Assumptions
- Election dates are tentative estimates based on historical 5-year cycles
- Polling booth data from Google Maps may not match ECI's official assignments
- Hindi translations via Cloud Translation API may not capture regional dialects
- App assumes internet access during use
- Voter eligibility based on age 18+ as of qualifying date per ECI rules
- No political party information or candidate endorsements — strictly neutral
- Turnout statistics sourced from Election Commission of India public data

---

## 🛠️ Tech Stack
| Layer | Technology |
|-|-|
| Backend | FastAPI, Python 3.11, Pydantic |
| Frontend | Vanilla JS, Tailwind CSS, Chart.js |
| AI | Gemini 2.5 via Vertex AI |
| Database | Google Firestore |
| APIs | Google Maps API, Cloud Translation |
| Deployment | Docker, Cloud Run |
| Testing | pytest, httpx |
---

## My Contribution

I designed and implemented the overall system architecture including:

- FastAPI backend structure
- AI agent workflow
- API design
- Security middleware
- Frontend interaction flow
- Accessibility features
- Testing strategy
- Cloud deployment workflow

AI tools were used during development for exploration, debugging, and iteration. All system architecture decisions, integrations, and validations were manually reviewed.

Built with ❤️ for Indian democracy.

