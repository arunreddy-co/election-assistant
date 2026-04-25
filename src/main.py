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
from src.utils.validators import sanitize_string, is_safe_input, validate_state
from src.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services and agents on startup."""
    logger.info("Starting VoteReady API")
    app.state.orchestrator = Orchestrator()
    app.state.process_guide = ProcessGuideAgent()
    app.state.eligibility = EligibilityAgent()
    app.state.timeline = TimelineAgent()
    app.state.simulator = SimulatorAgent()
    logger.info("All agents initialized")
    yield
    logger.info("Shutting down VoteReady API")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="VoteReady API",
    description="Personalized Election Readiness Platform for Indian Voters",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
            "https://cdn.jsdelivr.net https://maps.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://maps.googleapis.com https://maps.gstatic.com; "
            "connect-src 'self' https://cdn.jsdelivr.net; "
            "frame-src https://www.google.com https://maps.google.com;"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if settings.allowed_origins else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than 1KB."""
    
    MAX_BODY_SIZE = 1024  # 1KB
    
    async def dispatch(self, request: Request, call_next):
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return safe error response."""
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

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return success_response({"status": "healthy", "service": "voteready-api"})

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the VoteReady single-page application."""
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if not frontend_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return HTMLResponse(content=frontend_path.read_text(encoding="utf-8"))

@app.get("/api/states")
async def get_states():
    """Get all Indian states and UTs."""
    data_path = Path(__file__).parent / "data" / "states.json"
    with open(data_path, "r", encoding="utf-8") as f:
        states = json.load(f)
    return success_response(data=states)

@app.post("/api/onboard")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def onboard_user(request: Request, body: OnboardRequest):
    """Register a new user and return personalized dashboard data."""
    try:
        if not is_safe_input(body.name):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_INPUT", "Name contains invalid characters.", body.language)
            )
        
        eligibility_agent: EligibilityAgent = request.app.state.eligibility
        eligibility = eligibility_agent.check_eligibility(
            age=body.age,
            voter_id=body.voter_id
        )
        
        timeline_agent: TimelineAgent = request.app.state.timeline
        elections = timeline_agent.get_elections_for_state(
            state=body.state,
            language=body.language
        )
        nearest = timeline_agent.get_nearest_election(
            state=body.state,
            language=body.language
        )
        
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
        
        checklist = await firestore.get_checklist(user_id)
        
        guidance = await eligibility_agent.get_personalized_guidance(
            category=eligibility["category"],
            user_context=user_data,
            language=body.language
        )
        
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

@app.get("/api/elections")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_elections(request: Request, state: str, language: str = "en"):
    """Get all upcoming elections for a state."""
    try:
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

@app.get("/api/election/{election_type}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_election_detail(
    request: Request,
    election_type: str,
    state: str,
    user_id: str | None = None,
    language: str = "en"
):
    """Get detailed election info with step-by-step process guide."""
    try:
        valid_types = ["lok_sabha", "vidhan_sabha", "municipal", "panchayat"]
        if election_type not in valid_types:
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_TYPE", f"Must be one of: {', '.join(valid_types)}", language)
            )
        
        timeline_agent: TimelineAgent = request.app.state.timeline
        detail = timeline_agent.get_election_detail(
            state=state, election_type=election_type, language=language
        )
        
        process_agent: ProcessGuideAgent = request.app.state.process_guide
        
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

@app.get("/api/polling-booth")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def find_polling_booth(
    request: Request,
    district: str,
    state: str,
    language: str = "en"
):
    """Find nearest polling booths using Google Maps."""
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

@app.post("/api/chat")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def chat(request: Request, body: ChatRequest):
    """Contextual AI chat with VoteReady assistant."""
    try:
        if not is_safe_input(body.message):
            return JSONResponse(
                status_code=400,
                content=error_response("INVALID_INPUT", "Message contains invalid content.", body.language)
            )
        
        user_context = None
        if body.user_id:
            firestore = get_firestore_service()
            user_context = await firestore.get_user(body.user_id)
            if user_context and body.context_screen:
                user_context["current_screen"] = body.context_screen
        
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

@app.get("/api/stats")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_stats(request: Request, state: str | None = None, language: str = "en"):
    """Get voter turnout statistics for charts."""
    try:
        data_path = Path(__file__).parent / "data" / "turnout_stats.json"
        with open(data_path, "r", encoding="utf-8") as f:
            stats = json.load(f)
        
        result = {
            "national_turnout": stats.get("national_turnout", []),
            "age_group_turnout": stats.get("age_group_turnout", []),
            "closest_margins": stats.get("closest_margins", [])[:5],
        }
        
        if state and state in stats.get("state_turnout", {}):
            result["state_turnout"] = stats["state_turnout"][state]
        
        return success_response(data=result, language=language)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return JSONResponse(
            status_code=500,
            content=error_response("STATS_FAILED", "Failed to load statistics.", language)
        )

@app.get("/api/simulate")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_simulation(request: Request, language: str = "en"):
    """Get all election day simulation scenarios."""
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
    """Check user's answer for a simulation scenario."""
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

@app.get("/api/checklist")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_checklist(request: Request, user_id: str, language: str = "en"):
    """Get user's voter readiness checklist with progress."""
    try:
        firestore = get_firestore_service()
        checklist = await firestore.get_checklist(user_id)
        
        items = checklist.get("items", {})
        completed = sum(1 for item in items.values() if item.get("completed", False))
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
    """Update a checklist item's completion status."""
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
