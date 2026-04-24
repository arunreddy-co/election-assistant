---
description: Build the FastAPI application with all API endpoints, security middleware, rate limiting, CORS configuration, and centralized error handling. This wires agents to the frontend. Run AFTER workflow 03-agents is complete and verified.
---

# Workflow 04: FastAPI Endpoints and Security Layer

## Important Context
- This is the ONLY file that handles HTTP — agents never touch requests/responses directly
- Every endpoint returns the universal APIResponse schema from src/models/response.py
- Every endpoint validates input using Pydantic models from src/models/request.py
- Every endpoint catches exceptions and returns clean error responses
- Rate limiting, CORS, and CSP are configured here — not in agents or services
- The frontend (index.html) will be served as a static file from this app

## Step 1: Create src/main.py

```python
"""VoteReady API — Personalized Election Readiness Platform.

FastAPI application serving the VoteReady election assistant.
Handles user onboarding, election data, AI chat, simulator,
and voter readiness tracking.

All endpoints return standardized APIResponse format.
Security: rate limiting, CORS, CSP headers, input validation.
"""

import json
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings
from src.models.request import OnboardRequest, ChatRequest, ChecklistUpdateRequest
from src.models.response import success_response, error_response
from src.agents.orchestrator import Orchestrator
from src.agents.process_guide import ProcessGuideAgent
from src.agents.eligibility import EligibilityAgent
from src.agents.timeline import TimelineAgent
from src.agents.simulator import SimulatorAgent
from src.services.firestore_service import get_firestore_service
from src.services.maps_service import get_maps_service
from src.utils.validators import sanitize_string, is_safe_input
from src.utils.logger import get_logger

logger = get_logger(__name__)
```

### Lifespan and App Initialization

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services and agents on startup."""
    # Startup
    logger.info("Starting VoteReady API")
    app.state.orchestrator = Orchestrator()
    app.state.process_guide = ProcessGuideAgent()
    app.state.eligibility = EligibilityAgent()
    app.state.timeline = TimelineAgent()
    app.state.simulator = SimulatorAgent()
    logger.info("All agents initialized")
    yield
    # Shutdown
    logger.info("Shutting down VoteReady API")


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# App
app = FastAPI(
    title="VoteReady API",
    description="Personalized Election Readiness Platform for Indian Voters",
    version="1.0.0",
    lifespan=lifespan,
)

# Register rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Security Middleware

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Add CSP, X-Frame-Options, and other security headers."""
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
            "https://cdn.jsdelivr.net https://maps.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://maps.googleapis.com https://maps.gstatic.com; "
            "connect-src 'self'; "
            "frame-src https://www.google.com https://maps.google.com;"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# Add middleware (order matters — last added = first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)
```

### Request Size Limiter

```python
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than 1KB."""
    
    MAX_BODY_SIZE = 1024  # 1KB
    
    async def dispatch(self, request: Request, call_next):
        """Check request body size before processing."""
        if request.method in ("POST", "PUT"):
            body = await request.body()
            if len(body) > self.MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content=error_response(
                        code="REQUEST_TOO_LARGE",
                        message="Request body exceeds maximum size of 1KB."
                    )
                )
        return await call_next(request)


app.add_middleware(RequestSizeLimitMiddleware)
```

### Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return safe error response.
    
    NEVER expose internal error details to the client.
    Log the full error internally for debugging.
    """
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=error_response(
            code="INTERNAL_ERROR",
            message="Something went wrong. Please try again."
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with standard response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail)
        )
    )
```

### Endpoint: Health Check

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run.
    
    Returns:
        Simple status response confirming API is running.
    """
    return success_response({"status": "healthy", "service": "voteready-api"})
```

### Endpoint: Serve Frontend

```python
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the VoteReady single-page application.
    
    Returns:
        The index.html file as an HTML response.
    """
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if not frontend_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return HTMLResponse(content=frontend_path.read_text(encoding="utf-8"))
```

### Endpoint: User Onboarding

```python
@app.post("/api/onboard")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def onboard_user(request: Request, body: OnboardRequest):
    """Register a new user and return personalized dashboard data.
    
    Validates user input, checks eligibility, determines relevant
    elections, and stores profile in Firestore.
    
    Args:
        body: OnboardRequest with name, age, state, district, 
              voter_id (optional), language.
              
    Returns:
        APIResponse with:
          - user_id: Generated unique ID
          - eligibility: Eligibility check result
          - elections: List of relevant upcoming elections
          - checklist: Voter readiness checklist
          - nearest_election: The closest upcoming election
          - motivation: Personalized motivational message
    """
    try:
        # 1. Additional input safety check
        if not is_safe_input(body.name):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_INPUT", "Name contains invalid characters.", body.language)
            )
        
        # 2. Check eligibility (pure logic, instant)
        eligibility_agent: EligibilityAgent = request.app.state.eligibility
        eligibility = eligibility_agent.check_eligibility(
            age=body.age,
            voter_id=body.voter_id
        )
        
        # 3. Get elections for state
        timeline_agent: TimelineAgent = request.app.state.timeline
        elections = timeline_agent.get_elections_for_state(
            state=body.state,
            language=body.language
        )
        nearest = timeline_agent.get_nearest_election(
            state=body.state,
            language=body.language
        )
        
        # 4. Store user in Firestore
        firestore = get_firestore_service()
        user_data = {
            "name": sanitize_string(body.name),
            "age": body.age,
            "state": body.state,
            "district": body.district,
            "voter_id": body.voter_id,
            "language": body.language,
            "category": eligibility["category"],
        }
        user_id = await firestore.create_user(user_data)
        
        # 5. Get default checklist
        checklist = await firestore.get_checklist(user_id)
        
        # 6. Get personalized guidance (uses Gemini)
        guidance = await eligibility_agent.get_personalized_guidance(
            category=eligibility["category"],
            user_context=user_data,
            language=body.language
        )
        
        # 7. Build response
        return success_response(
            data={
                "user_id": user_id,
                "name": sanitize_string(body.name),
                "eligibility": eligibility,
                "elections": elections,
                "nearest_election": nearest,
                "checklist": checklist,
                "guidance": guidance,
            },
            language=body.language
        )
        
    except Exception as e:
        logger.error(f"Onboard error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("ONBOARD_FAILED", "Failed to process registration.", body.language)
        )
```

### Endpoint: Get Elections

```python
@app.get("/api/elections")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_elections(request: Request, state: str, language: str = "en"):
    """Get all upcoming elections for a state.
    
    Args:
        state: Indian state name (validated against known states).
        language: Response language ("en" or "hi").
        
    Returns:
        APIResponse with list of election dicts sorted by date.
    """
    try:
        # Validate state
        from src.utils.validators import validate_state
        if not validate_state(state):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_STATE", "Unrecognized state name.", language)
            )
        
        timeline_agent: TimelineAgent = request.app.state.timeline
        elections = timeline_agent.get_elections_for_state(state=state, language=language)
        
        return success_response(data={"elections": elections, "state": state}, language=language)
        
    except Exception as e:
        logger.error(f"Elections fetch error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("FETCH_FAILED", "Failed to load election data.", language)
        )
```

### Endpoint: Get Election Detail with Process Steps

```python
@app.get("/api/election/{election_type}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_election_detail(
    request: Request,
    election_type: str,
    state: str,
    user_id: str | None = None,
    language: str = "en"
):
    """Get detailed election info with step-by-step process guide.
    
    Args:
        election_type: "lok_sabha", "vidhan_sabha", "municipal", "panchayat".
        state: User's state.
        user_id: Optional user ID for personalized tips.
        language: Response language.
        
    Returns:
        APIResponse with election detail and process steps.
    """
    try:
        # Validate election_type
        valid_types = ["lok_sabha", "vidhan_sabha", "municipal", "panchayat"]
        if election_type not in valid_types:
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_TYPE", f"Must be one of: {', '.join(valid_types)}", language)
            )
        
        # Get election detail
        timeline_agent: TimelineAgent = request.app.state.timeline
        detail = timeline_agent.get_election_detail(
            state=state, election_type=election_type, language=language
        )
        
        # Get process steps
        process_agent: ProcessGuideAgent = request.app.state.process_guide
        
        # If user_id provided, fetch context for personalization
        user_context = None
        if user_id:
            firestore = get_firestore_service()
            user_context = await firestore.get_user(user_id)
        
        overview = await process_agent.get_overview(
            election_type=election_type, language=language
        )
        
        return success_response(
            data={
                "election": detail,
                "process": overview,
            },
            language=language
        )
        
    except Exception as e:
        logger.error(f"Election detail error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("FETCH_FAILED", "Failed to load election details.", language)
        )
```

### Endpoint: Find Polling Booth

```python
@app.get("/api/polling-booth")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def find_polling_booth(
    request: Request,
    district: str,
    state: str,
    language: str = "en"
):
    """Find nearest polling booths using Google Maps.
    
    Args:
        district: User's district name.
        state: User's state name.
        language: Response language.
        
    Returns:
        APIResponse with list of nearby polling booths with map data.
    """
    try:
        if not is_safe_input(district) or not is_safe_input(state):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_INPUT", "Invalid characters in location.", language)
            )
        
        maps = get_maps_service()
        booths = await maps.find_polling_booths(district=district, state=state)
        
        return success_response(
            data={"booths": booths, "district": district, "state": state},
            language=language
        )
        
    except Exception as e:
        logger.error(f"Polling booth error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("MAPS_FAILED", "Failed to find polling booths.", language)
        )
```

### Endpoint: AI Chat

```python
@app.post("/api/chat")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def chat(request: Request, body: ChatRequest):
    """Contextual AI chat with VoteReady assistant.
    
    Routes messages through the orchestrator which classifies
    intent and delegates to the appropriate specialist agent.
    
    Args:
        body: ChatRequest with message, user_id, language, context_screen.
        
    Returns:
        APIResponse with intent, response text, and follow-up suggestions.
    """
    try:
        # Safety check on message
        if not is_safe_input(body.message):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_INPUT", "Message contains invalid content.", body.language)
            )
        
        # Get user context from Firestore if user_id provided
        user_context = None
        if body.user_id:
            firestore = get_firestore_service()
            user_context = await firestore.get_user(body.user_id)
            if user_context and body.context_screen:
                user_context["current_screen"] = body.context_screen
        
        # Route through orchestrator
        orchestrator: Orchestrator = request.app.state.orchestrator
        result = await orchestrator.route_and_respond(
            message=body.message,
            user_context=user_context,
            language=body.language
        )
        
        return success_response(data=result, language=body.language)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("CHAT_FAILED", "Failed to process your message.", body.language)
        )
```

### Endpoint: Voter Turnout Stats

```python
@app.get("/api/stats")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_stats(request: Request, state: str | None = None, language: str = "en"):
    """Get voter turnout statistics for charts.
    
    Args:
        state: Optional state filter. If None, returns national data.
        language: Response language.
        
    Returns:
        APIResponse with national turnout, state turnout,
        age group data, and closest margin stories.
    """
    try:
        data_path = Path(__file__).parent / "data" / "turnout_stats.json"
        with open(data_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
        
        result = {
            "national_turnout": stats.get("national_turnout", []),
            "age_group_turnout": stats.get("age_group_turnout", []),
            "closest_margins": stats.get("closest_margins", [])[:5],
        }
        
        # Add state-specific data if requested
        if state and state in stats.get("state_turnout", {}):
            result["state_turnout"] = stats["state_turnout"][state]
        
        return success_response(data=result, language=language)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("STATS_FAILED", "Failed to load statistics.", language)
        )
```

### Endpoint: Election Day Simulator

```python
@app.get("/api/simulate")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_simulation(request: Request, language: str = "en"):
    """Get all election day simulation scenarios.
    
    Args:
        language: Response language.
        
    Returns:
        APIResponse with list of scenarios (answers hidden).
    """
    try:
        simulator: SimulatorAgent = request.app.state.simulator
        scenarios = simulator.get_all_scenarios(language=language)
        
        return success_response(
            data={"scenarios": scenarios, "total": len(scenarios)},
            language=language
        )
        
    except Exception as e:
        logger.error(f"Simulator error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("SIMULATOR_FAILED", "Failed to load simulator.", language)
        )


@app.post("/api/simulate/check")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def check_simulation_answer(
    request: Request,
    scenario_id: int,
    selected_option: int,
    language: str = "en"
):
    """Check user's answer for a simulation scenario.
    
    Args:
        scenario_id: Which scenario step.
        selected_option: Which option the user picked.
        language: Response language.
        
    Returns:
        APIResponse with is_correct, feedback, tip, correct answer.
    """
    try:
        simulator: SimulatorAgent = request.app.state.simulator
        result = simulator.check_answer(
            scenario_id=scenario_id,
            selected_option_id=selected_option,
            language=language
        )
        
        return success_response(data=result, language=language)
        
    except Exception as e:
        logger.error(f"Simulator check error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("CHECK_FAILED", "Failed to check answer.", language)
        )
```

### Endpoint: Voter Readiness Checklist

```python
@app.get("/api/checklist")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_checklist(request: Request, user_id: str, language: str = "en"):
    """Get user's voter readiness checklist with progress.
    
    Args:
        user_id: The user's unique identifier.
        language: Response language.
        
    Returns:
        APIResponse with checklist items, completion count, percentage.
    """
    try:
        firestore = get_firestore_service()
        checklist = await firestore.get_checklist(user_id)
        
        # Calculate progress
        items = checklist.get("items", [])
        completed = sum(1 for item in items if item.get("completed", False))
        total = len(items)
        percentage = round((completed / total * 100) if total > 0 else 0)
        
        return success_response(
            data={
                "checklist": checklist,
                "completed": completed,
                "total": total,
                "percentage": percentage,
            },
            language=language
        )
        
    except Exception as e:
        logger.error(f"Checklist fetch error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("CHECKLIST_FAILED", "Failed to load checklist.", language)
        )


@app.put("/api/checklist")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def update_checklist(request: Request, body: ChecklistUpdateRequest):
    """Update a checklist item's completion status.
    
    Args:
        body: ChecklistUpdateRequest with user_id, item_id, completed.
        
    Returns:
        APIResponse confirming the update.
    """
    try:
        firestore = get_firestore_service()
        success = await firestore.update_checklist_item(
            user_id=body.user_id,
            item_id=body.item_id,
            completed=body.completed
        )
        
        if success:
            return success_response(data={"updated": True, "item_id": body.item_id})
        else:
            return JSONResponse(
                status_code=404,
                content=error_response("NOT_FOUND", "User or checklist item not found.")
            )
        
    except Exception as e:
        logger.error(f"Checklist update error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("UPDATE_FAILED", "Failed to update checklist.")
        )
```

## Step 2: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8080

# Run with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Step 3: Git Commit

```
git add src/main.py Dockerfile
git commit -m "feat: implement FastAPI endpoints with security middleware and Dockerfile"
git push origin main
```

## Verification Checklist
Before moving to the next workflow, verify:
- [ ] All 9 endpoints implemented: health, frontend, onboard, elections, election detail, polling-booth, chat, stats, simulate (GET + POST check), checklist (GET + PUT)
- [ ] Every endpoint returns APIResponse format via success_response() or error_response()
- [ ] Every POST/PUT endpoint validates input with Pydantic models
- [ ] Every endpoint has @limiter.limit decorator
- [ ] Every endpoint has try/except with logged error and safe error response
- [ ] SecurityHeadersMiddleware adds CSP, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy
- [ ] RequestSizeLimitMiddleware rejects bodies > 1KB
- [ ] CORS configured with specific origins (not wildcard *)
- [ ] Global exception handler catches unhandled errors safely
- [ ] Agents accessed via request.app.state (initialized in lifespan)
- [ ] Services accessed via singleton getters
- [ ] is_safe_input() called on all user-provided text fields
- [ ] Dockerfile uses python:3.11-slim, exposes 8080, runs uvicorn
- [ ] No hardcoded secrets anywhere
- [ ] All functions have Google-style docstrings and type hints
- [ ] Clean commit pushed to GitHub
