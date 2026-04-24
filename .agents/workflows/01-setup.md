---
description: Scaffold the VoteReady project — directory structure, configuration, environment, data files, and all boilerplate. Run this FIRST before any other workflow.
---

# Workflow 01: Project Setup and Data Foundation

## Step 1: Create All Directories

Create every directory listed in AGENTS.md directory structure:
- src/
- src/models/
- src/agents/
- src/services/
- src/utils/
- src/data/
- frontend/
- tests/

Add empty `__init__.py` files in: src/, src/models/, src/agents/, src/services/, src/utils/, tests/

## Step 2: Create .gitignore

```
# Environment
.env
.venv/
env/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
htmlcov/
.coverage

# Logs
*.log
```

## Step 3: Create .env.example

```
# Google Cloud Project
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=asia-south1

# Gemini API (via Vertex AI)
GEMINI_MODEL=gemini-3.0-flash

# Google Maps
GOOGLE_MAPS_API_KEY=your-maps-api-key

# Google Cloud Translation
GOOGLE_TRANSLATE_PARENT=projects/your-project-id/locations/global

# Firestore
FIRESTORE_COLLECTION_USERS=users
FIRESTORE_COLLECTION_CACHE=response_cache
FIRESTORE_COLLECTION_CHECKLIST=checklists

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# CORS
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:5500

# Environment
ENV=development
```

## Step 4: Create requirements.txt

```
fastapi==0.115.12
uvicorn==0.34.2
google-cloud-aiplatform>=1.90.0
google-cloud-firestore>=2.20.0
google-cloud-translate>=3.18.0
googlemaps>=4.10.0
python-dotenv>=1.1.0
pydantic>=2.11.0
slowapi>=0.1.9
pytest>=8.3.0
httpx>=0.28.0
```

## Step 5: Create src/config.py

Create a Settings class using pydantic-settings or manual os.getenv loading:
- Load all environment variables from .env
- Provide sensible defaults where appropriate
- Include a validate method that checks all required variables are set
- Use type hints on every field
- Add Google-style docstring explaining what this module does
- Export a singleton `settings` instance

Fields to include:
- google_cloud_project: str
- google_cloud_region: str (default: "asia-south1")
- gemini_model: str (default: "gemini-3.0-flash")
- google_maps_api_key: str
- google_translate_parent: str
- firestore_collection_users: str (default: "users")
- firestore_collection_cache: str (default: "response_cache")
- firestore_collection_checklist: str (default: "checklists")
- rate_limit_per_minute: int (default: 10)
- allowed_origins: list[str]
- env: str (default: "development")

## Step 6: Create src/models/response.py

Create the universal API response model using Pydantic BaseModel:

```python
class ErrorDetail(BaseModel):
    code: str
    message: str

class APIResponse(BaseModel):
    status: Literal["success", "error"]
    data: dict | list | None = None
    error: ErrorDetail | None = None
    timestamp: str  # ISO 8601 format
    language: Literal["en", "hi"] = "en"
```

Add a helper function:
```python
def success_response(data: dict | list, language: str = "en") -> dict:
    """Create a standardized success response."""

def error_response(code: str, message: str, language: str = "en") -> dict:
    """Create a standardized error response."""
```

Both functions must auto-generate the timestamp using datetime.utcnow().isoformat().

## Step 7: Create src/models/request.py

Create Pydantic request models with strict validation:

```python
class OnboardRequest(BaseModel):
    name: str  # min 2 chars, max 100 chars, stripped, no HTML tags
    age: int  # min 1, max 150
    state: str  # must be a valid Indian state from states list
    district: str  # non-empty string
    voter_id: str | None = None  # optional, alphanumeric only if provided
    language: Literal["en", "hi"] = "en"

class ChatRequest(BaseModel):
    message: str  # min 1 char, max 500 chars, stripped, no HTML tags
    user_id: str  # non-empty
    language: Literal["en", "hi"] = "en"
    context_screen: str | None = None  # which screen user is on

class ChecklistUpdateRequest(BaseModel):
    user_id: str
    item_id: str  # which checklist item
    completed: bool
```

Add Pydantic field validators that:
- Strip whitespace from all string fields
- Reject strings containing HTML tags (< or >)
- Reject strings containing script injection patterns
- Validate state against a hardcoded list of Indian states
- Validate voter_id format if provided (alphanumeric, 10 chars)

## Step 8: Create src/utils/logger.py

Create a structured logging utility:
- Use Python's built-in logging module
- Format: JSON structured logs with timestamp, level, module, message
- Log levels: DEBUG for dev, INFO for production
- Read log level from config.env
- NEVER log sensitive user data (voter_id, full name)
- Export a `get_logger(module_name: str)` function that returns a configured logger

## Step 9: Create src/utils/validators.py

Create input validation utilities:

```python
def sanitize_string(value: str) -> str:
    """Remove HTML tags, script patterns, and dangerous characters."""

def validate_state(state: str) -> bool:
    """Check if state is a valid Indian state or UT."""

def validate_age(age: int) -> bool:
    """Check if age is within valid range (1-150)."""

def validate_voter_id(voter_id: str) -> bool:
    """Validate voter ID format: 3 letters + 7 digits (e.g., ABC1234567)."""

def is_safe_input(text: str) -> bool:
    """Check input for XSS, SQL injection, and prompt injection patterns."""
```

Include a VALID_STATES list with all 28 states and 8 UTs:
Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chhattisgarh, Goa, Gujarat, Haryana, Himachal Pradesh, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand, West Bengal, Andaman and Nicobar Islands, Chandigarh, Dadra and Nagar Haveli and Daman and Diu, Delhi, Jammu and Kashmir, Ladakh, Lakshadweep, Puducherry

## Step 10: Create src/utils/cache.py

Create a simple in-memory cache with TTL:

```python
class ResponseCache:
    """In-memory cache with TTL for Gemini API responses.
    
    Falls back to Firestore cache for persistence across restarts.
    Memory cache checked first for speed, Firestore second for persistence.
    """
    
    def __init__(self, default_ttl_seconds: int = 86400):
        """Initialize cache with 24-hour default TTL."""
    
    def get(self, key: str) -> dict | None:
        """Retrieve cached response if not expired."""
    
    def set(self, key: str, value: dict, ttl_seconds: int | None = None) -> None:
        """Store response with TTL."""
    
    def generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
    
    def clear_expired(self) -> int:
        """Remove expired entries, return count of removed items."""
```

Use a dictionary with timestamps. Key format: `{prefix}:{hash_of_params}`.
Use hashlib.md5 for generating short keys from parameters.

## Step 11: Create All Data Files

### src/data/states.json
Complete list of Indian states and UTs with their:
- name (English)
- name_hi (Hindi)
- code (2-letter state code)
- capital
- lok_sabha_seats (number)
- vidhan_sabha_seats (number)
- districts (list of district names — include at least 5 major districts per state)

### src/data/elections.json
For each state, list upcoming elections:
- election_type: "lok_sabha" | "vidhan_sabha" | "municipal" | "panchayat"
- title and title_hi
- tentative_year
- tentative_month (if known, else null)
- last_held_year
- total_seats
- description and description_hi

Include Lok Sabha 2029 as a national entry for all states.

### src/data/process_steps.json
For each election type, list the voter's journey steps:
- step_number
- title and title_hi
- description and description_hi (detailed, 2-3 sentences)
- action_items (list of specific things to do)
- action_items_hi
- documents_needed (if any)
- links (relevant URLs like nvsp.in)
- estimated_time (e.g., "5 minutes online" or "Same day at booth")

Steps should cover: Check Registration → Register/Get Voter ID → Find Polling Booth → Know Your Documents → Polling Day Guide → After Voting

### src/data/eligibility.json
Eligibility criteria structured as:
- criteria (list of conditions with field, operator, value)
- required_documents (list with name, name_hi, description, mandatory boolean)
- special_cases:
  - nri (different process)
  - first_time_voter (additional guidance)
  - under_18 (pre-registration info)
  - address_changed (transfer process)

### src/data/turnout_stats.json
Historical voter turnout data:
- national_turnout: list of {year, percentage, total_voters, votes_cast}
- state_turnout: for each state, {year, percentage} for last 3 elections
- age_group_turnout: {age_range, percentage} for 18-25, 25-40, 40-60, 60+
- closest_margins: list of {constituency, state, year, margin_votes, winner_votes, total_votes} — at least 10 entries with margins under 1000 votes

### src/data/faq.json
20+ FAQ entries:
- id
- question and question_hi
- answer and answer_hi (concise, 2-3 sentences)
- category: "registration" | "eligibility" | "process" | "documents" | "technical" | "general"
- related_links (list of URLs)

Use the FAQ questions from the election-domain skill file as the base.

### src/data/simulator.json
Election day simulation scenarios:
- For each step of polling day (arrival, queue, ID check, ink, voting compartment, EVM, VVPAT, exit):
  - scenario_text and scenario_text_hi
  - options: list of {text, text_hi, is_correct, feedback, feedback_hi}
  - tip and tip_hi (helpful information after answering)

Create at least 6 scenarios covering the full polling day experience.

### src/data/motivational.json
- quotes: list of {text, text_hi, author} — 10+ quotes about democracy and voting
- facts: list of {text, text_hi} — 10+ interesting facts about Indian democracy
- youth_messages: list of {text, text_hi} — 5+ messages specifically targeting 18-25 year olds
- impact_template: "In {constituency}, the last election was decided by just {margin} votes. Your vote could change the outcome."
- impact_template_hi: Hindi version of the same

## Step 12: Initial Git Commit

After all files are created:
```
git add .
git commit -m "chore: initial project structure and configuration"
git push origin main
```

Then immediately:
```
git add src/data/
git commit -m "feat: add comprehensive election data files"
git push origin main
```

## Verification Checklist
Before moving to the next workflow, verify:
- [ ] All directories exist with __init__.py files
- [ ] .gitignore excludes .env and __pycache__
- [ ] .env.example has all required variables with comments
- [ ] requirements.txt has pinned versions
- [ ] config.py loads all env vars with defaults
- [ ] response.py has APIResponse model + helper functions
- [ ] request.py has all 3 request models with validators
- [ ] logger.py provides structured JSON logging
- [ ] validators.py has all 5 validation functions + VALID_STATES
- [ ] cache.py has ResponseCache class with TTL
- [ ] All 8 data JSON files are comprehensive and bilingual
- [ ] Two clean commits pushed to GitHub
