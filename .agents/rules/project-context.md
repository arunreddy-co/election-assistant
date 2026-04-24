---
description: Deep project context for the Election Assistant — purpose, evaluation criteria, design decisions, and differentiation strategy
globs: ["**/*.py", "**/*.html", "**/*.json"]
---

# Project Context: VoteReady — Personalized Election Readiness Platform

## Why This Exists
India has 960M+ eligible voters but voter turnout among 18-25 year olds is consistently below 50%. The core problem is not lack of information — it's fragmentation and apathy. Election data exists across dozens of government sites, PDFs, and news articles. No single interactive tool connects it all AND motivates action. VoteReady solves both: it personalizes the election journey AND activates the user to actually vote.

## Competition Context
This is a PromptWars 2026 / Solution Challenge submission. An AI evaluator judges submissions on 6 strict criteria. Every line of code must be written with these criteria in mind:

### Evaluation Criteria (Memorize This)
1. **Code Quality** — structure, readability, maintainability. Clean modules, docstrings, type hints, consistent patterns, Pydantic models, centralized error handling, structured logging.
2. **Security** — safe and responsible implementation. Input sanitization with regex, rate limiting (slowapi), prompt injection protection in Gemini system prompt, CORS lockdown, CSP headers, env vars for secrets, request size limits, no internal details in error responses.
3. **Efficiency** — optimal use of resources. Static content from JSON (never call Gemini for predictable answers), response caching in Firestore with 24h TTL, lazy loading Maps and Chart.js, minimal Gemini token usage with concise prompts.
4. **Testing** — validation of functionality. 20+ pytest cases covering eligibility logic, input validators, API endpoints, prompt injection, language toggle, data integrity. Fixtures in conftest.py.
5. **Accessibility** — inclusive and usable design. Bilingual (English + Hindi), mobile responsive, semantic HTML, keyboard navigation, ARIA labels, 4.5:1 contrast ratio, font size toggle, high contrast mode, screen reader support, loading/error states.
6. **Google Services** — meaningful integration. Gemini 3 (conversational AI + personalization), Google Maps (polling booth finder), Cloud Translation (bilingual support), Firestore (session + cache), Cloud Run (deployment). Each service solves a real user problem — none are bolted on.

## Differentiation Strategy
Most submissions will build a generic election chatbot. VoteReady is different because:

1. **Voter Readiness Tracker** — gamified progress checklist that tracks what the user has completed (checked electoral roll, found booth, gathered documents). Progress ring on dashboard. Stored in Firestore.
2. **Election Day Simulator** — interactive 2-minute walkthrough of polling day. "You arrive at the booth. What do you do first?" User picks options, gets feedback. Gemini generates scenarios dynamically based on user's state and election type.
3. **Hyper-Local Impact Data** — "In your constituency, the last election was decided by just 847 votes. Your vote matters." One powerful data point per constituency that emotionally convinces the user.
4. **Context-Aware Assistant** — the chat widget knows where the user is in the app. If they're on eligibility screen, it says "I see you're 19 and from Telangana. You're eligible! Want help registering?" Not a generic "how can I help?"
5. **Four Distinct User Paths** — under-18, first-time voter (18-21), registered voter, NRI. Each gets a fundamentally different experience, not just different text.

## Assistant Persona: VoteReady
- Tone: Friendly, encouraging, simple language, never condescending
- Always uses the user's name after onboarding
- Celebrates progress: "Great job, you've completed 4 of 6 steps!"
- Strictly non-partisan: NEVER mentions parties, candidates, or political opinions
- Redirects off-topic questions politely: "I'm here to help you with election-related questions. What would you like to know about voting?"
- Speaks in the user's selected language (English or Hindi)
- Uses motivational framing: "Your vote is your voice" not "You should vote"

## Key Design Decisions

### Why Single HTML File (Not React Build)
- Repo must be under 1MB — React build with dependencies would exceed this
- No build step needed — evaluator can open index.html directly
- Tailwind CSS via CDN, Chart.js via CDN, Google Maps via script tag
- Vanilla JS with clean component-like functions — still modular and readable
- Faster load, zero tooling dependencies

### Why Firestore (Not BigQuery/AlloyDB)
- Election data is ~500 entries max — warehouse-scale tools would be inefficient
- Firestore is serverless, zero-provisioning, auto-scales
- Perfect for: user profiles, session data, checklist progress, response cache
- Free tier covers this project entirely
- Evaluator sees appropriate tool selection = higher efficiency score

### Why Static JSON (Not Database for Election Data)
- Election processes, eligibility rules, timelines are static reference data
- Loading from JSON is faster than any database query
- Keeps the app simple, reduces failure points
- Gemini is called ONLY when personalization is needed
- Evaluator sees minimal API waste = higher efficiency score

### Why Gemini 3 (Not Raw API)
- Used via Vertex AI for enterprise-grade reliability
- System prompt enforces persona, topic boundaries, and injection protection
- Called only for: personalized guidance, chat Q&A, simulator scenarios, impact stats
- All predictable content pre-written in JSON files

## Assumptions (Must Be Documented in README)
- Election dates are tentative estimates based on historical 5-year cycles
- Polling booth data from Google Maps may not match ECI's official assignments
- Hindi translations via Cloud Translation API — may not capture regional dialects
- App assumes internet access during use
- Voter eligibility based on age 18+ as of qualifying date per ECI rules
- No political party information or candidate endorsements — strictly neutral
- Turnout statistics sourced from Election Commission of India public data

## What Success Looks Like
A submission where the AI evaluator scores 9+ on all 6 criteria because:
- Every file is clean, documented, and follows consistent patterns
- Security is proactive, not reactive
- No unnecessary API calls or resource waste
- Tests actually verify functionality, not just exist
- Accessibility is built-in, not bolted on
- Every Google service removal would visibly degrade the experience
