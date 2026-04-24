---
description: Build the complete VoteReady frontend as a single index.html file. Includes all screens (language select, onboarding, dashboard, election detail, simulator), chat widget, charts, accessibility features, and responsive design. Run AFTER workflow 04-endpoints is complete and verified.
---

# Workflow 05: Frontend — Single Page Application

## Important Context
- EVERYTHING goes in ONE file: frontend/index.html
- No build step, no npm, no React — vanilla JS with Tailwind CSS via CDN
- Chart.js via CDN for turnout visualizations
- Google Maps JavaScript API via script tag
- Must be under 200KB to keep repo under 1MB total
- Mobile-first responsive design — judges may test on mobile viewport
- Accessibility is a scored criterion — WCAG AA compliance required
- The frontend is served by FastAPI at the root "/" endpoint
- All API calls go to relative paths: /api/onboard, /api/chat, etc.

## Design System

### Color Palette (CSS Variables)
```css
:root {
    /* Primary — Saffron (Indian flag inspired, civic pride) */
    --primary: #FF6B35;
    --primary-dark: #E55A2B;
    --primary-light: #FF8F65;
    
    /* Secondary — Deep Blue (trust, authority) */
    --secondary: #1B3A5C;
    --secondary-dark: #0F2A45;
    --secondary-light: #2D5F8A;
    
    /* Accent — Green (Indian flag, growth, success) */
    --accent: #2E8B57;
    --accent-light: #4CAF7D;
    
    /* Neutrals */
    --bg-primary: #FAFBFC;
    --bg-card: #FFFFFF;
    --bg-dark: #1A1A2E;
    --text-primary: #1A1A2E;
    --text-secondary: #5A6178;
    --text-muted: #8B92A5;
    --border: #E2E8F0;
    --border-light: #F1F5F9;
    
    /* Status */
    --success: #10B981;
    --warning: #F59E0B;
    --error: #EF4444;
    --info: #3B82F6;
    
    /* High Contrast Mode (toggled via JS) */
    --hc-bg: #000000;
    --hc-text: #FFFFFF;
    --hc-border: #FFFFFF;
    --hc-accent: #FFFF00;
    
    /* Font Sizes (toggled via JS) */
    --font-base: 16px;
    --font-lg: 18px;
    --font-xl: 22px;
    --font-2xl: 28px;
    --font-3xl: 36px;
}
```

### Typography
- Font: System font stack — `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Hindi font: Add `'Noto Sans Devanagari'` from Google Fonts for Hindi text
- Headings: Bold, --secondary color
- Body: Regular, --text-primary
- Muted: --text-secondary

### Component Patterns
- Cards: white bg, 1px border, 12px border-radius, subtle shadow
- Buttons: rounded-lg, padding 12px 24px, hover state with slight darken
- Primary buttons: --primary bg, white text
- Secondary buttons: white bg, --primary border and text
- Inputs: full width, 1px border, rounded-lg, focus ring with --primary
- Progress rings: SVG circle with stroke-dasharray animation

## HTML Structure

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="VoteReady — Your personalized election readiness guide for Indian elections">
    <meta name="theme-color" content="#FF6B35">
    <title>VoteReady — Your Vote, Your Voice</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Chart.js (lazy loaded later, but declare script tag) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" defer></script>
    
    <!-- Google Fonts for Hindi -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
    
    <!-- Google Maps (loaded dynamically when needed) -->
    <!-- Script tag added by JS when user opens booth finder -->
    
    <style>
        /* CSS variables defined above */
        /* Custom animations */
        /* Screen transitions */
        /* Accessibility styles */
        /* High contrast mode overrides */
        /* Font size toggle overrides */
        /* Print styles for PDF download */
    </style>
</head>
<body>
    <!-- Skip to main content link (accessibility) -->
    <a href="#main-content" class="sr-only focus:not-sr-only ...">
        Skip to main content
    </a>
    
    <!-- Accessibility Toolbar (top-right corner, always visible) -->
    <div id="a11y-toolbar" role="toolbar" aria-label="Accessibility options">
        <!-- Font size toggle: A → A+ -->
        <!-- High contrast toggle: 🌓 -->
        <!-- Language toggle: EN / हिं -->
    </div>
    
    <!-- Main Content Container -->
    <main id="main-content" role="main">
        <!-- Screen 1: Language Selection -->
        <section id="screen-language" aria-label="Language selection">
        </section>
        
        <!-- Screen 2: Onboarding Form -->
        <section id="screen-onboarding" aria-label="User registration" hidden>
        </section>
        
        <!-- Screen 3: Dashboard -->
        <section id="screen-dashboard" aria-label="Election dashboard" hidden>
        </section>
        
        <!-- Screen 4: Election Detail -->
        <section id="screen-election-detail" aria-label="Election details" hidden>
        </section>
        
        <!-- Screen 5: Simulator -->
        <section id="screen-simulator" aria-label="Election day simulator" hidden>
        </section>
    </main>
    
    <!-- Chat Widget (floating, visible on dashboard and detail screens) -->
    <div id="chat-widget" hidden>
    </div>
    
    <!-- Loading Overlay -->
    <div id="loading-overlay" hidden>
    </div>
    
    <!-- Toast Notification Container -->
    <div id="toast-container" aria-live="polite">
    </div>
    
    <script>
        /* All JavaScript here */
    </script>
</body>
</html>
```

## Screen 1: Language Selection

### Layout
- Full viewport height, centered content
- Indian flag-inspired gradient background (saffron → white → green subtle)
- Large VoteReady logo/title at top
- Motivational tagline: "Your Vote, Your Voice" / "आपका वोट, आपकी आवाज़"
- Two large language buttons side by side
- Small India map silhouette or ballot box illustration (SVG inline, not image file)

### Elements
```html
<section id="screen-language">
    <div class="min-h-screen flex flex-col items-center justify-center p-6">
        
        <!-- Logo / Brand -->
        <div class="mb-8 text-center">
            <!-- Inline SVG: Ballot box or vote icon -->
            <h1 class="text-4xl font-bold text-secondary">VoteReady</h1>
            <p class="text-lg text-text-secondary mt-2">
                Your Vote, Your Voice
            </p>
            <p class="text-md text-text-muted">
                आपका वोट, आपकी आवाज़
            </p>
        </div>
        
        <!-- Language Selection -->
        <div class="flex gap-4">
            <button onclick="selectLanguage('en')" 
                    class="language-btn"
                    aria-label="Continue in English">
                <span class="text-2xl">🇬🇧</span>
                <span>English</span>
            </button>
            <button onclick="selectLanguage('hi')"
                    class="language-btn"
                    aria-label="हिंदी में जारी रखें">
                <span class="text-2xl">🇮🇳</span>
                <span>हिंदी</span>
            </button>
        </div>
        
        <!-- Footer tagline -->
        <p class="mt-12 text-sm text-text-muted">
            Empowering every Indian voter
        </p>
    </div>
</section>
```

### Behavior
- `selectLanguage(lang)` stores language in app state
- Transitions to Screen 2 with slide animation
- Sets `<html lang="en">` or `<html lang="hi">`
- Updates all subsequent UI text based on language

## Screen 2: Onboarding Form

### Layout
- Clean form card centered on screen
- Progress indicator at top (Step 1 of 1)
- VoteReady header with back button to language screen
- Form fields stacked vertically
- Submit button at bottom

### Elements
```html
<section id="screen-onboarding">
    <div class="min-h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-card rounded-2xl shadow-lg p-8">
            
            <!-- Header -->
            <button onclick="goToScreen('language')" aria-label="Go back">←</button>
            <h2 class="text-2xl font-bold">Tell us about yourself</h2>
            <p class="text-text-secondary">
                We'll personalize your election journey
            </p>
            
            <!-- Form (NO <form> tag — use div + JS) -->
            <div class="space-y-4 mt-6">
                
                <!-- Name -->
                <div>
                    <label for="input-name" class="block text-sm font-medium">
                        Your Name *
                    </label>
                    <input id="input-name" type="text" 
                           maxlength="100" required
                           placeholder="Enter your name"
                           aria-required="true"
                           class="w-full border rounded-lg p-3 mt-1">
                    <span id="error-name" class="text-error text-sm hidden"
                          role="alert"></span>
                </div>
                
                <!-- Age -->
                <div>
                    <label for="input-age" class="block text-sm font-medium">
                        Your Age *
                    </label>
                    <input id="input-age" type="number" 
                           min="1" max="150" required
                           placeholder="Enter your age"
                           aria-required="true"
                           class="w-full border rounded-lg p-3 mt-1">
                    <span id="error-age" class="text-error text-sm hidden"
                          role="alert"></span>
                </div>
                
                <!-- State (Dropdown) -->
                <div>
                    <label for="input-state" class="block text-sm font-medium">
                        Your State *
                    </label>
                    <select id="input-state" required
                            aria-required="true"
                            class="w-full border rounded-lg p-3 mt-1">
                        <option value="">Select your state</option>
                        <!-- Populated from states.json via JS -->
                    </select>
                    <span id="error-state" class="text-error text-sm hidden"
                          role="alert"></span>
                </div>
                
                <!-- District (Dropdown, populated after state selection) -->
                <div>
                    <label for="input-district" class="block text-sm font-medium">
                        Your District *
                    </label>
                    <select id="input-district" required
                            aria-required="true"
                            class="w-full border rounded-lg p-3 mt-1">
                        <option value="">Select state first</option>
                    </select>
                    <span id="error-district" class="text-error text-sm hidden"
                          role="alert"></span>
                </div>
                
                <!-- Voter ID (Optional) -->
                <div>
                    <label for="input-voterid" class="block text-sm font-medium">
                        Voter ID (Optional)
                    </label>
                    <input id="input-voterid" type="text"
                           maxlength="10"
                           placeholder="e.g., ABC1234567"
                           class="w-full border rounded-lg p-3 mt-1">
                    <p class="text-xs text-text-muted mt-1">
                        3 letters + 7 digits. Leave blank if you don't have one.
                    </p>
                </div>
                
                <!-- Submit Button -->
                <button onclick="submitOnboarding()"
                        id="btn-submit"
                        class="w-full bg-primary text-white font-semibold 
                               py-3 rounded-lg hover:bg-primary-dark
                               transition-colors"
                        aria-label="Show my elections">
                    Show My Elections →
                </button>
            </div>
        </div>
    </div>
</section>
```

### Behavior
- State dropdown populated from states.json (fetched once, cached in JS)
- District dropdown populated dynamically when state is selected
- Client-side validation before API call:
  - Name: 2-100 chars, no HTML tags
  - Age: 1-150 integer
  - State: must be selected
  - District: must be selected
  - Voter ID: if provided, must match /^[A-Z]{3}[0-9]{7}$/ pattern
- Show inline error messages per field using role="alert"
- On submit: show loading state on button, call POST /api/onboard
- On success: store user_id and response data in app state, transition to Dashboard
- On error: show toast notification with error message

## Screen 3: Dashboard

### Layout
- Top navigation bar with VoteReady logo, user name, language/accessibility toggles
- Welcome banner with motivational message
- Eligibility status card (prominent, color-coded)
- Voter readiness progress ring (circular SVG progress)
- Checklist section (expandable items with checkboxes)
- Elections list (cards, clickable)
- Voter turnout chart (Chart.js bar chart)
- Quick action buttons row
- Floating chat widget button (bottom-right)

### Sections in Order

#### 3a. Welcome Banner
```
"Welcome, {name}! 🗳️"
"{personalized guidance message from API}"
```
- If under 18: show yellow banner "You'll be eligible in {years} years! Start learning now."
- If first-time voter: show green banner "First-time voter? We'll guide you every step of the way!"
- If registered: show green banner "You're registered! Let's make sure you're ready."

#### 3b. Eligibility Card
- Large card at top
- Green check / Red X icon based on eligibility
- Category label: "First-Time Voter", "Registered Voter", etc.
- If not registered: prominent "Register Now →" CTA button linking to NVSP
- Next steps list from eligibility API response

#### 3c. Voter Readiness Progress
- Circular SVG progress ring showing completion percentage
- "4 of 6 steps completed" text
- Animated fill on load
- Clicking opens the checklist section

#### 3d. Readiness Checklist
- 6 items from API with checkbox toggle
- Each item: checkbox + title + brief description
- Checking/unchecking calls PUT /api/checklist
- Progress ring updates in real-time
- Items:
  1. ☐ Check if you're on the electoral roll
  2. ☐ Get your Voter ID (EPIC)
  3. ☐ Find your polling booth
  4. ☐ Prepare your ID documents
  5. ☐ Know your candidates
  6. ☐ Know polling day procedures

#### 3e. Your Elections
- Card for each election from API
- Each card shows: icon (🏛/🏢/🏘), title, tentative date, countdown
- Cards sorted by nearest first
- Clicking a card navigates to Screen 4 (Election Detail)
- If nearest election is within 1 year, show a pulsing "Coming Soon" badge

#### 3f. Impact Statement
- Single powerful stat card with large typography
- "In {constituency}, the last election was decided by just {margin} votes."
- "Your vote could change the result."
- Saffron/orange accent background

#### 3g. Voter Turnout Chart
- Chart.js bar chart showing national turnout over last 5 elections
- Annotated with year labels
- User's age group highlighted with different color
- Chart title: "India's Voter Turnout Over the Years"
- Lazy loaded — Chart.js initialized only when this section scrolls into view

#### 3h. Quick Actions Row
- Horizontal scrollable row of action buttons:
  - "🗳 Practice Voting" → opens Simulator (Screen 5)
  - "📍 Find My Booth" → opens booth finder modal with Google Maps
  - "📋 Registration Guide" → scrolls to checklist
  - "📤 Share with Friends" → opens WhatsApp share
- Each button: icon + label, rounded pill style

#### 3i. WhatsApp Share
- Pre-formatted WhatsApp message:
  "Hey! I'm getting ready to vote using VoteReady. Check your election readiness too! 🗳️ {app_url}"
- Opens: `https://wa.me/?text={encoded_message}`

### Behavior
- All data populated from /api/onboard response (already fetched)
- Checklist interactions call PUT /api/checklist and update progress ring
- Election cards navigate to Screen 4 with election_type and state params
- Chart initialized with IntersectionObserver (lazy load)
- Chat widget becomes visible on this screen

## Screen 4: Election Detail

### Layout
- Back button to dashboard
- Election title and countdown
- Interactive timeline (horizontal stepper)
- Step-by-step guide (expandable accordion)
- Polling booth finder (Google Maps)
- "Practice Voting" CTA button

### Sections

#### 4a. Election Header
- Election type icon and title
- Tentative date with countdown badge
- Total seats info
- Brief description

#### 4b. Interactive Timeline
- Horizontal stepper with 6 steps
- Each step: circle with number + label below
- Active step highlighted with --primary color
- Completed steps filled with --accent
- Connected by a line (progress bar style)
- Clicking a step scrolls to that step's detail below

#### 4c. Step-by-Step Accordion
- Each of the 6 process steps as an expandable section
- Default: first step expanded, rest collapsed
- Each step shows:
  - Step number and title
  - Detailed description (2-3 sentences)
  - Action items as a mini-checklist
  - Required documents (if any)
  - Helpful links (nvsp.in, electoralsearch.in)
  - Personalized tip from Gemini (if user context available)
  - Estimated time

#### 4d. Polling Booth Finder
- "Find Your Nearest Polling Booth" section
- Button triggers Google Maps API load (lazy)
- Shows map with markers for nearby booths
- Each marker has: name, address, directions link
- Uses user's district and state from profile
- If Maps API fails: show fallback text with link to electoralsearch.in

#### 4e. Bottom CTA
- Large button: "🗳 Practice Election Day" → opens Simulator
- Secondary button: "← Back to Dashboard"

### Behavior
- Data fetched from GET /api/election/{type}?state={state}
- Timeline steps are clickable and scroll to accordion
- Accordion sections toggle independently
- Google Maps script loaded dynamically only when booth finder is opened:
  ```javascript
  function loadGoogleMaps() {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${MAPS_KEY}&callback=initMap`;
      script.async = true;
      document.head.appendChild(script);
  }
  ```
- Booth data fetched from GET /api/polling-booth?district={d}&state={s}

## Screen 5: Election Day Simulator

### Layout
- Full-screen immersive experience
- Progress bar at top (Step X of 6)
- Scenario text in large card
- Option buttons (2-4 options per scenario)
- Feedback card (shown after answering)
- Score card (shown after completing all scenarios)

### Flow
```
Start Screen
    "Ready to practice election day?"
    [Start Simulation →]
        ↓
Scenario 1 (Arriving at booth)
    "You've arrived at the polling station. 
     What's the first thing you should do?"
    [ ] Find the queue for your booth
    [ ] Show your voter ID to the guard
    [ ] Go directly to the voting machine
    [ ] Take a selfie outside
        ↓ (user selects)
Feedback Card
    ✅ "Correct! First, find the queue..."
    or
    ❌ "Not quite. You should first..."
    [Next →]
        ↓
Scenario 2... → Scenario 6
        ↓
Score Card
    "🎉 You scored 5/6!"
    "Great job! You're well prepared."
    Progress ring animation
    [Try Again]  [Back to Dashboard]
```

### Elements

#### Scenario Card
```html
<div class="scenario-card">
    <div class="progress-bar">
        <!-- Step X of 6, colored segments -->
    </div>
    <h3 class="scenario-title">At the Polling Booth</h3>
    <p class="scenario-text" id="scenario-text">
        <!-- Dynamic scenario text -->
    </p>
    <div class="options-grid" id="scenario-options">
        <!-- Dynamic option buttons -->
        <button class="option-btn" onclick="selectOption(0)">
            <!-- Option text -->
        </button>
    </div>
</div>
```

#### Feedback Card (appears after selection)
```html
<div class="feedback-card" id="feedback-card" hidden>
    <div class="feedback-icon">✅ or ❌</div>
    <p class="feedback-text" id="feedback-text"></p>
    <p class="feedback-tip" id="feedback-tip"></p>
    <button onclick="nextScenario()" class="next-btn">
        Next →
    </button>
</div>
```

#### Score Card (appears after all scenarios)
```html
<div class="score-card" id="score-card" hidden>
    <!-- Animated progress ring with score -->
    <h2>Your Score: <span id="score-value">5</span>/6</h2>
    <p id="score-rating">Great job!</p>
    <p id="score-message">You're well prepared for election day.</p>
    <div class="score-actions">
        <button onclick="restartSimulator()">Try Again</button>
        <button onclick="goToScreen('dashboard')">Back to Dashboard</button>
    </div>
</div>
```

### Behavior
- Scenarios fetched from GET /api/simulate on simulator open
- All scenarios loaded at once (6 items, small payload)
- User selects an option → call POST /api/simulate/check
- Show feedback with correct/incorrect state
- Highlight correct option in green, wrong in red
- Track answers in JS array
- After scenario 6: calculate score locally, show score card
- Score card has animated progress ring filling up
- "Try Again" resets to scenario 1

## Chat Widget

### Layout
- Floating button: bottom-right corner, circular, --primary color, chat icon
- Opens a slide-up chat panel (max 400px wide, 500px tall)
- Chat panel has: header with title + close button, message area, input field + send button

### Elements
```html
<div id="chat-widget">
    <!-- Toggle Button -->
    <button id="chat-toggle" onclick="toggleChat()"
            aria-label="Open VoteReady assistant"
            class="fixed bottom-6 right-6 w-14 h-14 bg-primary 
                   rounded-full shadow-lg flex items-center justify-center
                   text-white text-2xl hover:bg-primary-dark z-50">
        💬
    </button>
    
    <!-- Chat Panel -->
    <div id="chat-panel" hidden
         class="fixed bottom-24 right-6 w-96 max-h-[500px] bg-white 
                rounded-2xl shadow-2xl flex flex-col z-50"
         role="dialog" aria-label="VoteReady Chat Assistant">
        
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b">
            <div>
                <h3 class="font-semibold">VoteReady Assistant</h3>
                <p class="text-xs text-text-muted">Ask me anything about voting</p>
            </div>
            <button onclick="toggleChat()" aria-label="Close chat">✕</button>
        </div>
        
        <!-- Messages Area -->
        <div id="chat-messages" class="flex-1 overflow-y-auto p-4 space-y-3"
             role="log" aria-live="polite">
            <!-- Initial greeting message from VoteReady -->
            <div class="chat-msg assistant">
                Hi {name}! I'm VoteReady. Ask me anything about elections and voting! 🗳️
            </div>
        </div>
        
        <!-- Input Area -->
        <div class="p-4 border-t flex gap-2">
            <input id="chat-input" type="text" 
                   maxlength="500"
                   placeholder="Type your question..."
                   aria-label="Type your question"
                   class="flex-1 border rounded-lg px-3 py-2"
                   onkeypress="if(event.key==='Enter') sendChat()">
            <button onclick="sendChat()" 
                    aria-label="Send message"
                    class="bg-primary text-white px-4 py-2 rounded-lg">
                →
            </button>
        </div>
    </div>
</div>
```

### Behavior
- Chat toggle shows/hides the panel with slide animation
- Initial greeting personalized with user's name
- User types message → POST /api/chat with message, user_id, language, current screen context
- Show typing indicator ("VoteReady is thinking...") while waiting
- Display response in chat bubble
- Follow-up suggestions shown as clickable chips below the response
- Chat input maxlength 500, validated with is_safe_input logic (client-side)
- Context-aware: sends current screen name so VoteReady knows where the user is
- Chat history maintained in JS array (session only, not persisted)
- Scrolls to bottom on new message

## Loading & Error States

### Loading Overlay
```html
<div id="loading-overlay" hidden
     class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
     role="status" aria-label="Loading">
    <div class="bg-white rounded-2xl p-8 text-center">
        <!-- Animated ballot box SVG or spinner -->
        <p id="loading-text" class="mt-4 text-text-secondary">
            Preparing your election journey...
        </p>
    </div>
</div>
```

### Toast Notifications
```javascript
function showToast(message, type = 'info') {
    // Create toast element
    // Types: success (green), error (red), info (blue), warning (yellow)
    // Auto-dismiss after 4 seconds
    // Accessible: role="status" for info, role="alert" for errors
    // Animate in from top-right
}
```

### Error States per Screen
- API call fails: show toast with user-friendly message
- Network error: show inline "Unable to connect. Check your internet." with retry button
- Empty data: show friendly illustration with message (e.g., "No elections found for your state")
- Never show blank screens — always show loading OR content OR error state

## JavaScript Architecture

```javascript
// ============================================
// APP STATE (single source of truth)
// ============================================
const AppState = {
    language: 'en',
    currentScreen: 'language',
    user: null,         // { id, name, age, state, district, voter_id }
    eligibility: null,
    elections: [],
    checklist: null,
    guidance: null,
    nearestElection: null,
    simulatorScenarios: [],
    simulatorAnswers: [],
    simulatorCurrentStep: 0,
    chatHistory: [],
    mapsLoaded: false,
    chartLoaded: false,
    highContrast: false,
    largeFontSize: false,
};

// ============================================
// UI TEXT (bilingual)
// ============================================
const UI_TEXT = {
    en: {
        welcome: "Welcome",
        show_elections: "Show My Elections",
        eligible: "You are eligible to vote!",
        not_eligible: "You're not yet eligible",
        // ... all UI strings
    },
    hi: {
        welcome: "स्वागत है",
        show_elections: "मेरे चुनाव दिखाएं",
        eligible: "आप मतदान के पात्र हैं!",
        not_eligible: "आप अभी पात्र नहीं हैं",
        // ... all Hindi UI strings
    }
};

// Helper to get text in current language
function t(key) {
    return UI_TEXT[AppState.language]?.[key] || UI_TEXT.en[key] || key;
}

// ============================================
// SCREEN NAVIGATION
// ============================================
function goToScreen(screenName) {
    // Hide all screens
    // Show target screen
    // Update AppState.currentScreen
    // Update browser title
    // Focus management: move focus to screen heading (accessibility)
    // Announce screen change to screen readers via aria-live region
}

// ============================================
// API HELPER
// ============================================
async function api(method, path, body = null) {
    // Centralized API call function
    // Adds Content-Type header
    // Handles loading state
    // Parses JSON response
    // Checks response.status === "success"
    // On error: shows toast, returns null
    // On network error: shows connection error toast
}

// ============================================
// ACCESSIBILITY
// ============================================
function toggleFontSize() {
    // Toggle AppState.largeFontSize
    // Update document.documentElement.style.fontSize
    // Regular: 16px, Large: 20px
    // Store preference in localStorage
}

function toggleHighContrast() {
    // Toggle AppState.highContrast
    // Add/remove 'high-contrast' class on body
    // CSS handles color overrides via .high-contrast selectors
    // Store preference in localStorage
}

function toggleLanguage() {
    // Switch between 'en' and 'hi'
    // Update AppState.language
    // Re-render current screen with new language
    // Update <html lang=""> attribute
}

// ============================================
// SCREEN RENDERERS
// ============================================
// Each screen has a render function that reads from AppState
// and updates the DOM. This keeps rendering declarative.

function renderDashboard() { /* ... */ }
function renderElectionDetail(electionType) { /* ... */ }
function renderSimulator() { /* ... */ }
function renderChecklist() { /* ... */ }

// ============================================
// CHART (lazy loaded)
// ============================================
function initTurnoutChart(data) {
    // Only called when chart section is visible (IntersectionObserver)
    // Creates Chart.js bar chart with national turnout data
    // Highlights user's age group
    // Responsive, accessible (aria-label on canvas)
}

// ============================================
// GOOGLE MAPS (lazy loaded)
// ============================================
function loadGoogleMaps() {
    // Dynamically inject Google Maps script tag
    // Only called when user clicks "Find My Booth"
    // Sets AppState.mapsLoaded = true after load
}

function initBoothMap(booths) {
    // Called after Maps JS is loaded
    // Creates map centered on user's district
    // Adds markers for each booth
    // Each marker has info window with name, address, directions link
}

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Check localStorage for saved preferences (font size, contrast)
    // Apply saved preferences
    // Show language selection screen
    // Fetch states.json for onboarding dropdown
});
```

## Accessibility Verification (Must Pass All)
- [ ] Skip-to-content link at top of page
- [ ] All images/icons have alt text or aria-label
- [ ] All form inputs have associated labels
- [ ] All error messages use role="alert"
- [ ] All interactive elements reachable via Tab key
- [ ] Focus visible on all interactive elements (outline ring)
- [ ] Screen transitions announce via aria-live region
- [ ] Chat messages area has role="log" and aria-live="polite"
- [ ] Color contrast meets 4.5:1 AA ratio for all text
- [ ] Font size toggle works and persists
- [ ] High contrast mode works and persists
- [ ] Language toggle updates all visible text
- [ ] No information conveyed by color alone (icons + text for status)
- [ ] Semantic heading hierarchy: one h1, h2s for sections, h3s for subsections
- [ ] Canvas chart has aria-label describing the data

## Responsive Breakpoints
- Mobile (< 640px): single column, full-width cards, chat panel full-width
- Tablet (640px - 1024px): two-column grid for election cards
- Desktop (> 1024px): max-width 1200px container, three-column for cards

## Step 2: Git Commit

```
git add frontend/
git commit -m "feat: build complete frontend dashboard with accessibility and responsive design"
git push origin main
```

## Verification Checklist
Before moving to the next workflow, verify:
- [ ] All 5 screens render correctly: language, onboarding, dashboard, election detail, simulator
- [ ] Language toggle switches all text between English and Hindi
- [ ] Onboarding form validates all fields client-side before API call
- [ ] Dashboard shows eligibility card, progress ring, elections, chart, checklist
- [ ] Election detail shows interactive timeline, accordion steps, booth finder
- [ ] Simulator flows through all scenarios with feedback and scoring
- [ ] Chat widget opens/closes, sends messages, shows responses
- [ ] Loading overlay appears during API calls
- [ ] Error toasts appear on failures
- [ ] No blank screens — always loading, content, or error state
- [ ] Font size toggle works
- [ ] High contrast toggle works
- [ ] Skip-to-content link works
- [ ] All form inputs have labels
- [ ] Tab navigation reaches every interactive element
- [ ] Mobile layout works at 375px width
- [ ] Google Maps loads only when booth finder is opened
- [ ] Chart.js initializes only when chart scrolls into view
- [ ] File size is under 200KB
- [ ] Clean commit pushed to GitHub
