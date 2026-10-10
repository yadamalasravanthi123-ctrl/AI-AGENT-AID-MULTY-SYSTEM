# AI Legal Aid Multi-Agent System — Project Plan

## 1. Discovery

### Problem Statement
Citizens with limited means cannot access affordable legal guidance for everyday issues
(landlord disputes, employment rights, family law, immigration, consumer rights).
This system provides **general legal information** — not legal advice — powered by IBM Granite,
coordinated through a multi-agent pipeline.

### Key Constraints
- **No legal advice**: output is general information only; no attorney-client relationship.
- **No hallucination**: agents must refuse to invent statutes, deadlines, or citations.
- **Jurisdiction-awareness**: jurisdiction must be collected before substantive answers.
- **Privacy**: no PII stored beyond the session; no logging of sensitive details.
- **Safety escalation**: urgent/high-risk queries (domestic violence, imminent deadlines) surface local help.
- **Accessibility**: plain English, respectful tone, WCAG AA contrast targets.

---

## 2. Requirements

### Functional
| ID | Requirement |
|----|-------------|
| FR-01 | Collect user's legal question via chat interface |
| FR-02 | Collect jurisdiction (country + state/province) before answering |
| FR-03 | Route question to the correct specialist agent |
| FR-04 | Verify that cited sources are plausible; flag unverifiable claims |
| FR-05 | Detect urgent/risk keywords and surface escalation notice |
| FR-06 | Strip PII from stored context; redact before sending to model |
| FR-07 | Display disclaimer on every response |
| FR-08 | Provide "Find local legal help" links by jurisdiction |

### Non-Functional
| ID | Requirement |
|----|-------------|
| NFR-01 | Response latency < 8 s for standard questions |
| NFR-02 | All secrets via environment variables, never hard-coded |
| NFR-03 | Works on Node 18+ / npm 9+ |
| NFR-04 | Single-command setup on Windows via `.bat` file |

---

## 3. Agent Roles

| Agent | Responsibility |
|-------|----------------|
| **Intake Agent** | Greets user, extracts jurisdiction, categorises question domain |
| **Legal Information Agent** | Uses IBM Granite to answer within the detected domain and jurisdiction |
| **Source Verification Agent** | Post-processes model output; flags invented citations or suspicious claims |
| **Safety Escalation Agent** | Scans for high-risk keywords; injects emergency resources |
| **Privacy Agent** | Redacts PII (names, addresses, dates-of-birth) before model calls |
| **Quality Review Agent** | Ensures disclaimer is present; checks for absolute legal advice phrasing |

---

## 4. Architecture

```
Browser (React + Vite)
        │  POST /api/chat
        ▼
Express API Server
        │
        ▼
  Orchestrator (Node.js)
   ├─ IntakeAgent          ← jurisdiction + domain
   ├─ PrivacyAgent         ← PII redaction
   ├─ LegalInfoAgent       ← IBM Granite (watsonx.ai)
   ├─ SourceVerifyAgent    ← citation sanity check
   ├─ SafetyEscalationAgent← urgency detection
   └─ QualityReviewAgent   ← disclaimer + tone guard
        │
        ▼
  Structured response → Browser
```

---

## 5. SDLC Phases

| Phase | Activities | Exit Criteria |
|-------|-----------|---------------|
| Discovery | Stakeholder interviews, problem definition | Approved problem statement |
| Requirements | FR/NFR table, agent role matrix | Signed-off requirements |
| Design | Architecture diagram, API contracts, UI wireframes | Design review passed |
| Development | Scaffold, implement agents, UI, tests | All acceptance tests green |
| Verification | Manual QA, edge-case testing, disclaimer audit | Checklist 100% checked |
| Release | README, setup scripts, deployment notes | Runnable on clean machine |
| Ongoing Review | Quarterly bias/accuracy review, IBM Granite model updates | Review log maintained |

---

## 6. Acceptance Checklist
See `ACCEPTANCE_CHECKLIST.md`.

---

## 7. Revision History
| Date | Author | Notes |
|------|--------|-------|
| 2025 | AI Agent Aid Team | Initial version |
