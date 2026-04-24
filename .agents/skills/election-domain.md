---
description: Comprehensive Indian election domain knowledge for building the election assistant. Load this skill when working on agents, data files, Gemini prompts, or any election-related logic.
---

# Indian Election Domain Knowledge

## Types of Elections in India

### 1. General Elections (Lok Sabha)
- Elects Members of Parliament (MPs) to the Lower House
- 543 constituencies across India
- Held every 5 years (last: 2024, next tentative: 2029)
- Conducted in multiple phases (typically 5-7 phases over 6 weeks)
- All Indian citizens 18+ registered in electoral roll can vote
- Governed by Election Commission of India (ECI)

### 2. State Assembly Elections (Vidhan Sabha)
- Elects Members of Legislative Assembly (MLAs)
- Number of constituencies varies by state (e.g., Telangana: 119, UP: 403)
- Held every 5 years per state (dates vary by state)
- Can coincide with Lok Sabha elections
- Same eligibility as general elections

### 3. Local Body Elections
- **Municipal Corporation** — for cities with 1M+ population
- **Municipal Council/Nagar Palika** — for smaller towns
- **Panchayat Elections** — three tiers:
  - Gram Panchayat (village level)
  - Mandal/Block Panchayat (block level)
  - Zilla Parishad (district level)
- Conducted by State Election Commissions (not ECI)
- Frequency varies by state (typically every 5 years)
- Some states have age requirement of 21+ for contesting

### 4. By-Elections
- Held when a seat becomes vacant mid-term
- Reasons: death, resignation, disqualification of sitting member
- Only affects the specific constituency
- ECI announces dates as needed

## Voter Eligibility Rules

### Basic Eligibility
- Must be an Indian citizen
- Must be 18 years or older on the qualifying date (January 1 of the year of electoral roll revision)
- Must be a resident of the constituency where they wish to vote
- Must not be declared mentally unsound by a competent court
- Must not be disqualified under any law (e.g., convicted of certain offenses)

### Required Documents (Any ONE of these)
- Voter ID Card (EPIC — Electors Photo Identity Card)
- Aadhaar Card
- Passport
- Driving License
- PAN Card
- MNREGA Job Card
- Bank/Post Office Passbook with photo
- Smart Card issued by RGI under NPR

### NRI Voters
- Indian citizens living abroad CAN vote
- Must register using Form 6A
- Must vote in person at assigned polling station in India
- No postal ballot facility for NRIs (as of current rules)
- Passport is the primary ID document

## Voter Registration Process

### New Registration (Form 6)
1. Visit National Voter Service Portal (nvsp.in) OR Voter Helpline App
2. Fill Form 6 with personal details
3. Upload passport-size photo and age proof document
4. Submit online — receive reference number
5. BLO (Booth Level Officer) may visit for verification
6. Name appears in electoral roll after verification
7. Receive EPIC (Voter ID Card) — can also download e-EPIC

### NRI Registration (Form 6A)
1. Visit NVSP portal
2. Fill Form 6A with passport details
3. Upload passport copy
4. Submit — linked to last known Indian address constituency
5. Verification by concerned ERO
6. Name added to electoral roll with NRI tag

### Corrections (Form 8)
- For correcting name, age, gender, address, photo in existing record
- Submit online via NVSP or at ERO office
- Verification and update within 15-30 days

### Transfer (Form 6 again)
- When moving to a new constituency
- File new Form 6 in new constituency
- Old registration deleted after new one is confirmed

### Deletion/Objection (Form 7)
- To report a deceased voter or fraudulent entry
- Any citizen can file Form 7

## Election Day Process (What Happens at the Polling Booth)

### Before Polling Day
1. Check your name on electoral roll at electoralsearch.in
2. Find your assigned polling booth (available on Voter Helpline App)
3. Prepare valid ID document
4. Check voting hours (typically 7 AM to 6 PM, varies by state)

### At the Polling Booth
1. Join the queue at your assigned booth
2. Show your ID to the polling officer at the first table
3. Your name is verified against the electoral roll
4. Indelible ink is applied to your left index finger
5. You receive a slip with your serial number
6. Proceed to the voting compartment
7. Press the button next to your chosen candidate on the EVM (Electronic Voting Machine)
8. A VVPAT (Voter Verified Paper Audit Trail) slip is generated — verify your vote on the paper slip visible for 7 seconds
9. Exit the booth

### After Voting
- Counting happens on a designated date (usually a few days after last phase)
- Results announced constituency by constituency
- Winning candidate: highest votes (First Past The Post system)
- Results available on results.eci.gov.in

## Key Institutions

### Election Commission of India (ECI)
- Constitutional body under Article 324
- Headed by Chief Election Commissioner (CEC) + 2 Election Commissioners
- Responsible for: Lok Sabha, Rajya Sabha, State Assembly elections
- Powers: announce dates, enforce Model Code of Conduct, order re-polls
- Website: eci.gov.in

### State Election Commissions
- Separate body for local body elections (Panchayat, Municipal)
- Each state has its own SEC
- Not under ECI's jurisdiction

### Key Officials
- Chief Electoral Officer (CEO) — state level
- District Election Officer (DEO) — district level
- Returning Officer (RO) — constituency level
- Booth Level Officer (BLO) — polling booth level

## Important Portals and Apps
- **NVSP** (nvsp.in) — National Voter Service Portal for registration
- **Voter Helpline App** — mobile app for registration, booth finding, complaints
- **Electoral Search** (electoralsearch.in) — check if your name is on the roll
- **ECI** (eci.gov.in) — official Election Commission website
- **Results** (results.eci.gov.in) — live election results

## State-wise Election Tentative Schedule
Note: These are estimates based on 5-year cycles. Actual dates announced by ECI/SEC.

### States with Assembly Elections Due (2026-2029)
- Bihar: 2025 (may extend to early 2026)
- Assam: 2026
- West Bengal: 2026
- Tamil Nadu: 2026
- Kerala: 2026
- Puducherry: 2026
- Uttar Pradesh: 2027
- Punjab: 2027
- Uttarakhand: 2027
- Manipur: 2027
- Goa: 2027
- Gujarat: 2027
- Himachal Pradesh: 2027
- Karnataka: 2028
- Madhya Pradesh: 2028
- Rajasthan: 2028
- Chhattisgarh: 2028
- Telangana: 2028
- Mizoram: 2028
- Next Lok Sabha: 2029

## Voter Turnout Statistics (Use for Motivational Data)

### National Turnout Trends (Lok Sabha)
- 2024: 65.8%
- 2019: 67.4%
- 2014: 66.4%
- 2009: 58.2%
- 2004: 57.0%

### Youth Voting Gap
- 18-25 age group turnout: approximately 45-50%
- 25-40 age group turnout: approximately 60-65%
- 40+ age group turnout: approximately 70-75%
- Key insight: youngest voters have the lowest turnout — this is VoteReady's primary target

### Closest Election Margins (Motivational)
- 2024: Several constituencies decided by fewer than 1000 votes
- Historical: Some seats won by margins of 1-5 votes
- Use these to generate "Your vote could decide the result" messaging

## EVM and VVPAT

### Electronic Voting Machine (EVM)
- Used in all Indian elections since 2004
- Two units: Control Unit (with presiding officer) + Ballot Unit (in voting compartment)
- Maximum 16 candidates per ballot unit (additional units linked for more)
- Standalone device — not connected to internet

### VVPAT (Voter Verified Paper Audit Trail)
- Attached to EVM since 2019 (all booths)
- After pressing EVM button, a paper slip shows candidate name + symbol
- Slip visible for 7 seconds through a glass window
- Slips collected in sealed box for audit if needed
- Adds transparency and verifiability to the process

## Model Code of Conduct
- Enforced from date of election announcement until results
- No party can use government resources for campaigning
- No appeals on basis of religion, caste, community
- No announcements of new schemes/projects during this period
- Violation can lead to EC action against candidates/parties

## Common Voter Questions (Use for FAQ Data)
1. "How do I check if I'm registered?" → electoralsearch.in or Voter Helpline App
2. "I lost my Voter ID, can I still vote?" → Yes, with any approved alternate ID
3. "I moved cities, can I vote?" → Need to transfer registration to new constituency
4. "Can I vote if I'm abroad?" → NRIs must vote in person in India
5. "What if my name is not on the list?" → File Form 6 for new registration, or Form 8 for correction
6. "Is voting compulsory?" → No, but it's a civic duty. Some states have proposed compulsory voting.
7. "What is NOTA?" → None Of The Above — option to reject all candidates
8. "Can I change my vote after pressing the button?" → No, EVM records the first press
9. "What if the EVM malfunctions?" → Presiding officer replaces the unit, voting continues
10. "How are results counted?" → EVMs opened at counting centers, votes tallied electronically
11. "What is a re-poll?" → If irregularities found, ECI can order fresh voting at specific booths
12. "Can I take my phone inside?" → No, phones not allowed inside polling booth
13. "What is the ink on my finger?" → Indelible ink to prevent double voting, lasts ~48 hours
14. "Who decides election dates?" → ECI for Lok Sabha/State Assembly, SEC for local body
15. "What documents do I need to carry?" → Any ONE approved photo ID (EPIC, Aadhaar, Passport, DL, PAN, etc.)
16. "What are election phases?" → Large states vote in multiple phases on different dates to allow security forces deployment
17. "Can I vote by mail?" → Only for service voters (military, diplomatic), election duty staff, and senior citizens 85+ / PwD (postal ballot)
18. "What time do polls open?" → Typically 7 AM to 6 PM, varies by state and constituency
19. "What is a constituency?" → A geographical area that elects one representative
20. "How do I find my constituency?" → Based on residential address, searchable on electoralsearch.in
