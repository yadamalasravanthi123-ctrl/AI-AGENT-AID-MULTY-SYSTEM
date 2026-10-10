# AI Legal Aid Multi-Agent System
## Powered by IBM Granite (watsonx.ai)

> **Legal Notice:** This application provides **general legal information only** — not legal advice.  
> It does not create an attorney-client relationship. Always consult a qualified lawyer.

---

## Overview

A web-based multi-agent system that coordinates six specialist AI agents to answer common
legal questions in clear, accessible language. Built with:

- **Backend:** Python / Flask
- **AI Model:** IBM Granite (via [watsonx.ai](https://www.ibm.com/watsonx))
- **Frontend:** React + Vite
- **Agents:** Intake, Privacy, Legal Information, Source Verification, Safety Escalation, Quality Review

---

## Architecture

```
Browser (React + Vite)
        │  POST /api/chat
        ▼
Flask API Server  (app.py)
        │
        ▼
  Orchestrator
   ├─ IntakeAgent            ← jurisdiction + domain detection
   ├─ PrivacyAgent           ← PII redaction before model call
   ├─ SafetyEscalationAgent  ← urgency / high-risk detection
   ├─ LegalInfoAgent         ← IBM Granite (watsonx.ai) call
   ├─ SourceVerifyAgent      ← citation sanity check
   └─ QualityReviewAgent     ← disclaimer + tone enforcement
```

---

## Agent Roles

| Agent | Responsibility |
|-------|---------------|
| **IntakeAgent** | Greets user, detects jurisdiction (country + state/province), categorises legal domain |
| **PrivacyAgent** | Redacts SSNs, emails, phone numbers, and addresses before any model call |
| **LegalInfoAgent** | Calls IBM Granite with a system prompt enforcing no-invented-citations policy |
| **SourceVerifyAgent** | Flags absolute legal claims or suspicious citation patterns in model output |
| **SafetyEscalationAgent** | Detects urgency keywords and injects emergency resource links |
| **QualityReviewAgent** | Softens advice-like phrasing; ensures disclaimer is always attached |

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 + |
| pip | 23 + |
| Node.js | 18 + |
| npm | 9 + |
| IBM Cloud account | — |
| watsonx.ai project | — |

---

## Quick Start (Windows)

```bat
setup_and_run.bat
```

This script will:
1. Create a Python virtual environment
2. Install Python dependencies from `requirements.txt`
3. Copy `.env.example` → `.env` (edit with your credentials)
4. Install Node dependencies
5. Build the React frontend
6. Start the Flask server on `http://localhost:5000`

---

## Manual Setup

### 1. Clone / open the project folder

```bash
cd "ai agent aid multi system"
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env    # Windows
cp .env.example .env      # macOS / Linux
```

Edit `.env` and fill in:

```
WATSONX_API_KEY=<your IBM Cloud API key>
WATSONX_PROJECT_ID=<your watsonx.ai project ID>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
```

### 5. Install Node dependencies and build frontend

```bash
npm install
npm run build
```

### 6. Run the server

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Send a message; returns orchestrated agent response |
| `POST` | `/api/reset` | Clear session context |
| `GET` | `/api/health` | Liveness check; returns model configuration status |

### `POST /api/chat` — Request

```json
{
  "message": "Can my landlord evict me without notice in Texas?",
  "session_id": "abc123"
}
```

### `POST /api/chat` — Response

```json
{
  "reply": "In Texas, landlords are generally required to provide written notice...",
  "disclaimer": "⚠️ This is general legal information only — not legal advice...",
  "is_urgent": false,
  "escalation_notice": "",
  "source_warning": "",
  "resource_url": "https://www.lsc.gov/about-lsc/what-legal-aid/find-legal-aid",
  "domain": "housing",
  "needs_jurisdiction": false,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## IBM watsonx.ai Setup

1. Sign in to [IBM Cloud](https://cloud.ibm.com)
2. Create or open a **watsonx.ai** project
3. Under **Manage → Access (IAM)** create an **API key**
4. Copy the **Project ID** from the project's **Settings → General** tab
5. Add both values to your `.env` file

> **Free tier:** IBM provides a free watsonx.ai Lite plan with monthly token allowances.

---

## Running Without IBM Credentials

The app runs in **fallback mode** if `WATSONX_API_KEY` or `WATSONX_PROJECT_ID` are not set.
The Legal Information Agent returns a helpful message directing users to local legal aid
organisations. All other agents (Intake, Privacy, Safety, Quality, Source) function normally.

---

## Privacy & Safety

- **No PII stored:** SSNs, email addresses, phone numbers, and street addresses are redacted
  before any model call and are never persisted.
- **Session memory:** held in-process only; cleared on server restart or via `/api/reset`.
- **Urgency detection:** domestic violence, imminent eviction, self-harm, and similar keywords
  trigger an emergency resource notice immediately.

---

## Disclaimer

This system provides **general legal information only**. It does not constitute legal advice,
does not create an attorney-client relationship, and should not be relied upon as a substitute
for advice from a licensed attorney. Laws vary by jurisdiction and change frequently.

---

## Licence

MIT
