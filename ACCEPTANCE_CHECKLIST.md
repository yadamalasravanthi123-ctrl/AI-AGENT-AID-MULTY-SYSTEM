# Acceptance Checklist — AI Legal Aid Multi-Agent System

All items must be checked before each release.

---

## 1. Legal & Ethical Compliance

- [ ] Every response includes the full disclaimer text
- [ ] No response uses "I advise you", "you must", or "you are legally required" without softening
- [ ] The system never states it provides legal advice
- [ ] The system explicitly states it does not create an attorney-client relationship
- [ ] Urgent/high-risk keywords trigger an emergency resource notice in 100% of test cases

---

## 2. Agent Pipeline Verification

- [ ] IntakeAgent correctly identifies jurisdiction from US state names (10 spot checks)
- [ ] IntakeAgent correctly identifies UK, Canada, Australia, South Africa
- [ ] IntakeAgent asks for jurisdiction when none is provided
- [ ] PrivacyAgent redacts SSN pattern `XXX-XX-XXXX` before model call
- [ ] PrivacyAgent redacts email addresses before model call
- [ ] PrivacyAgent redacts phone numbers before model call
- [ ] PrivacyAgent redacts street addresses before model call
- [ ] LegalInfoAgent returns a coherent answer for: employment, housing, family, immigration, consumer, criminal, benefits domains
- [ ] LegalInfoAgent fallback response is returned when model is unconfigured
- [ ] SourceVerifyAgent flags responses containing US code citation patterns
- [ ] SourceVerifyAgent flags responses containing "you must" absolute statements
- [ ] SafetyEscalationAgent triggers on keyword "domestic violence"
- [ ] SafetyEscalationAgent triggers on keyword "evicted tonight"
- [ ] SafetyEscalationAgent triggers on keyword "harm myself"
- [ ] SafetyEscalationAgent returns correct resource URL per jurisdiction (US, UK, CA, AU, ZA)
- [ ] QualityReviewAgent replaces "You should" with softened language
- [ ] QualityReviewAgent replaces "My advice is" with softened language

---

## 3. API Endpoints

- [ ] `GET /api/health` returns HTTP 200 with `status: ok`
- [ ] `POST /api/chat` with valid message returns HTTP 200
- [ ] `POST /api/chat` with empty message returns HTTP 400
- [ ] `POST /api/reset` clears session context
- [ ] Session context persists jurisdiction across multiple `/api/chat` calls in the same session
- [ ] Different `session_id` values maintain independent contexts

---

## 4. Frontend (React)

- [ ] Chat interface renders correctly in Chrome, Firefox, Edge
- [ ] Disclaimer is displayed beneath every AI response
- [ ] Escalation notice is visually distinct (red/orange alert styling)
- [ ] Source warning is displayed when flagged
- [ ] "Find local legal help" link opens in a new tab
- [ ] "New conversation" / reset button clears chat history
- [ ] Input field is disabled while a response is loading
- [ ] Character limit or loading indicator prevents double-submission

---

## 5. Privacy & Security

- [ ] `.env` file is not committed to version control
- [ ] `WATSONX_API_KEY` is never logged or returned in any API response
- [ ] No user message content is written to a persistent log file
- [ ] Session data is lost on server restart (no silent persistence)

---

## 6. Agentic AI SDLC Phases

- [ ] Discovery: problem statement documented in `PROJECT_PLAN.md`
- [ ] Requirements: FR and NFR tables documented in `PROJECT_PLAN.md`
- [ ] Design: architecture diagram documented in `PROJECT_PLAN.md` and `README.md`
- [ ] Development: all six agents implemented in `app.py`
- [ ] Verification: this checklist completed
- [ ] Release: `README.md`, `.env.example`, `requirements.txt`, `setup_and_run.bat` present
- [ ] Ongoing Review: quarterly review schedule noted in `PROJECT_PLAN.md §5`

---

## 7. Setup & Installation

- [ ] `setup_and_run.bat` runs to completion on a clean Windows 10/11 machine
- [ ] `pip install -r requirements.txt` completes without errors (Python 3.10+)
- [ ] `npm install && npm run build` completes without errors (Node 18+)
- [ ] `python app.py` starts the server on port 5000
- [ ] `http://localhost:5000/api/health` returns `{ "status": "ok" }`
- [ ] Frontend is served at `http://localhost:5000`

---

_Checked by:_ ___________________  _Date:_ ___________________
