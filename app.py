"""
AI Legal Aid Multi-Agent System
================================
Powered by IBM Granite via watsonx.ai

Agents
------
1. IntakeAgent          – collects jurisdiction and categorises the question domain
2. PrivacyAgent         – redacts PII before any model call
3. LegalInfoAgent       – calls IBM Granite to produce jurisdiction-aware legal information
4. SourceVerifyAgent    – flags invented-sounding citations or absolute legal claims
5. SafetyEscalationAgent– detects urgent / high-risk situations and surfaces local resources
6. QualityReviewAgent   – enforces disclaimer, tone guard, and no-advice language

Run
---
    pip install -r requirements.txt
    cp .env.example .env   # fill in your IBM watsonx credentials
    python app.py
"""

import os
import re
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# IBM watsonx.ai SDK — import lazily so missing creds don't crash startup
try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    _WATSONX_AVAILABLE = True
except ImportError:
    _WATSONX_AVAILABLE = False

# ── Initialisation ────────────────────────────────────────────────────────────

load_dotenv()

# Use dist/ as static folder only if it exists (requires npm run build)
_dist_path = os.path.join(os.path.dirname(__file__), "dist")
_static_folder = _dist_path if os.path.isdir(_dist_path) else None

app = Flask(__name__, static_folder=_static_folder, static_url_path="/")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# watsonx.ai configuration
WX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
GRANITE_MODEL = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-chat-v2")

# ── Helpers ───────────────────────────────────────────────────────────────────

LEGAL_DOMAINS = {
    "employment":   ["fired", "termination", "wrongful dismissal", "redundancy", "wage", "salary",
                     "discrimination", "harassment", "workplace", "FMLA", "leave"],
    "housing":      ["eviction", "landlord", "tenant", "rent", "lease", "deposit", "notice",
                     "repairs", "habitability", "section 8", "housing"],
    "family":       ["divorce", "custody", "child support", "alimony", "adoption", "guardianship",
                     "domestic", "restraining order", "parental"],
    "immigration":  ["visa", "green card", "deportation", "asylum", "citizenship", "undocumented",
                     "DACA", "naturalization", "immigration"],
    "consumer":     ["debt", "credit", "repossession", "bankruptcy", "collections", "refund",
                     "fraud", "scam", "warranty", "consumer"],
    "criminal":     ["arrest", "charge", "bail", "conviction", "probation", "parole", "police",
                     "crime", "felony", "misdemeanor"],
    "benefits":     ["social security", "disability", "SSI", "SSDI", "medicaid", "medicare",
                     "unemployment", "benefits", "welfare"],
}

URGENCY_KEYWORDS = [
    "immediate", "urgent", "emergency", "tonight", "today", "imminent",
    "domestic violence", "abuse", "threatened", "threatened", "stalking",
    "deportation order", "evicted today", "evicted tonight", "no shelter",
    "harm myself", "harm themselves", "suicide", "in danger",
]

PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]"),                  # US SSN
    (r"\b\d{9}\b", "[ID# REDACTED]"),                               # 9-digit IDs
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", "[EMAIL REDACTED]"),
    (r"\b\d{10,11}\b", "[PHONE REDACTED]"),                         # phone numbers
    (r"\b\d{1,5}\s\w+\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Lane|Ln)\b",
     "[ADDRESS REDACTED]"),
]

LOCAL_LEGAL_HELP = {
    "us": "https://www.lsc.gov/about-lsc/what-legal-aid/find-legal-aid",
    "uk": "https://www.gov.uk/find-legal-advice/find-legal-aid",
    "ca": "https://www.legalaid.on.ca/",
    "au": "https://www.nationallegalaid.org/",
    "za": "https://www.justice.gov.za/legalaid/",
    "default": "https://www.legalaidatwork.org/",
}

DISCLAIMER = (
    "⚠️ **Disclaimer:** This is general legal *information* only — not legal advice. "
    "It does not create an attorney-client relationship. Laws vary by jurisdiction and "
    "change frequently. For advice specific to your situation, please consult a "
    "qualified lawyer or legal aid organisation."
)


def get_watsonx_model():
    """Return an IBM Granite ModelInference instance, or None if not configured."""
    if not _WATSONX_AVAILABLE or not WX_API_KEY or not WX_PROJECT_ID:
        return None
    try:
        creds = Credentials(url=WX_URL, api_key=WX_API_KEY)
        params = {
            GenParams.MAX_NEW_TOKENS: 800,
            GenParams.TEMPERATURE: 0.2,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        return ModelInference(
            model_id=GRANITE_MODEL,
            credentials=creds,
            project_id=WX_PROJECT_ID,
            params=params,
        )
    except Exception as exc:
        app.logger.error("watsonx init error: %s", exc)
        return None


# ── Agent Implementations ─────────────────────────────────────────────────────

class IntakeAgent:
    """Extracts jurisdiction (country + state/province) and legal domain from user message."""

    def run(self, message: str, context: dict) -> dict:
        lower = message.lower()

        # ── Jurisdiction detection ──────────────────────────────────────────
        jurisdiction = context.get("jurisdiction", {})
        if not jurisdiction.get("country"):
            country, region = self._detect_jurisdiction(lower)
            if country:
                jurisdiction = {"country": country, "region": region}
        context["jurisdiction"] = jurisdiction

        # ── Domain detection ────────────────────────────────────────────────
        domain = "general"
        for d, keywords in LEGAL_DOMAINS.items():
            if any(kw in lower for kw in keywords):
                domain = d
                break
        context["domain"] = domain

        # ── Needs jurisdiction prompt? ──────────────────────────────────────
        needs_jurisdiction = not jurisdiction.get("country")
        return {"context": context, "needs_jurisdiction": needs_jurisdiction}

    def _detect_jurisdiction(self, text: str):
        country_map = {
            "united states": "us", "usa": "us", "u.s.": "us", "u.s.a.": "us",
            "united kingdom": "uk", "uk": "uk", "england": "uk", "scotland": "uk",
            "canada": "ca", "australia": "au", "south africa": "za",
        }
        us_states = [
            "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
            "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
            "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
            "maine", "maryland", "massachusetts", "michigan", "minnesota",
            "mississippi", "missouri", "montana", "nebraska", "nevada",
            "new hampshire", "new jersey", "new mexico", "new york",
            "north carolina", "north dakota", "ohio", "oklahoma", "oregon",
            "pennsylvania", "rhode island", "south carolina", "south dakota",
            "tennessee", "texas", "utah", "vermont", "virginia", "washington",
            "west virginia", "wisconsin", "wyoming", "dc", "washington dc",
        ]
        country = ""
        region = ""
        for name, code in country_map.items():
            if name in text:
                country = code
                break
        if country == "us" or not country:
            for state in us_states:
                if state in text:
                    region = state.title()
                    if not country:
                        country = "us"
                    break
        return country, region


class PrivacyAgent:
    """Redacts PII from user input before passing to the language model."""

    def run(self, message: str) -> str:
        cleaned = message
        for pattern, replacement in PII_PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        return cleaned


class LegalInfoAgent:
    """Calls IBM Granite to generate jurisdiction-aware legal information."""

    def __init__(self):
        self._model = None          # lazy — initialised on first call
        self._model_tried = False

    @property
    def model(self):
        if not self._model_tried:
            self._model_tried = True
            self._model = get_watsonx_model()
        return self._model

    def run(self, clean_message: str, context: dict) -> str:
        jurisdiction = context.get("jurisdiction", {})
        country  = jurisdiction.get("country", "unspecified").upper()
        region   = jurisdiction.get("region", "")
        domain   = context.get("domain", "general")
        loc_str  = f"{region}, {country}" if region else country

        system_prompt = (
            "You are a legal information assistant. "
            "You provide clear, accurate, general legal information — NOT legal advice. "
            "You never invent statutes, case names, deadlines, or citations. "
            "If you are unsure, say so explicitly. "
            "You do not tell the user what they should do legally. "
            "You always recommend consulting a qualified lawyer for their specific situation. "
            f"The user is located in: {loc_str}. "
            f"The question relates to: {domain} law."
        )

        full_prompt = (
            f"<|system|>\n{system_prompt}\n"
            f"<|user|>\n{clean_message}\n"
            "<|assistant|>\n"
        )

        if self.model:
            try:
                response = self.model.generate_text(prompt=full_prompt)
                return response.strip() if response else self._fallback(domain, loc_str)
            except Exception as exc:
                app.logger.error("Granite generate error: %s", exc)
                return self._fallback(domain, loc_str)
        else:
            return self._fallback(domain, loc_str)

    def _fallback(self, domain: str, location: str) -> str:
        return (
            f"I'm currently unable to reach the IBM Granite model. "
            f"For {domain} law questions in {location}, please contact a local legal "
            f"aid organisation. They can provide free or low-cost help. "
            f"Use the resource link below to find one near you."
        )


class SourceVerifyAgent:
    """Flags suspicious absolute claims or plausible-sounding invented citations."""

    RISK_PATTERNS = [
        r"\b(you must|you will|you cannot|you are required|you are guaranteed)\b",
        r"\b\d{1,2}\s+U\.S\.C\.\s+§\s*\d+\b",          # US code citations
        r"\bsection\s+\d+[A-Z]?\b",                      # generic section refs
        r"\bact\s+of\s+\d{4}\b",                          # "Act of 19xx / 20xx"
        r"\bcase\s+no\.?\s+\d",                           # case numbers
    ]

    def run(self, text: str) -> dict:
        flags = []
        lower = text.lower()
        for pattern in self.RISK_PATTERNS:
            if re.search(pattern, lower, re.IGNORECASE):
                flags.append(pattern)
        return {
            "verified": len(flags) == 0,
            "flags": flags,
            "warning": (
                "⚠️ This response may contain specific legal references. "
                "Please independently verify any statute, case, or deadline before relying on it."
            ) if flags else "",
        }


class SafetyEscalationAgent:
    """Detects urgent situations and injects emergency resource notice."""

    def run(self, message: str, jurisdiction: dict) -> dict:
        lower = message.lower()
        urgent = any(kw in lower for kw in URGENCY_KEYWORDS)

        country_code = jurisdiction.get("country", "default").lower()
        resource_url = LOCAL_LEGAL_HELP.get(country_code, LOCAL_LEGAL_HELP["default"])

        escalation_notice = ""
        if urgent:
            escalation_notice = (
                "🚨 **Urgent situation detected.** If you or someone else is in immediate danger, "
                "call your local emergency services (911 in the US, 999 in the UK, 000 in Australia). "
                f"For urgent legal help: {resource_url}"
            )
        return {
            "is_urgent": urgent,
            "escalation_notice": escalation_notice,
            "resource_url": resource_url,
        }


class QualityReviewAgent:
    """Ensures disclaimer is present, removes absolute advice, enforces respectful tone."""

    ADVICE_PATTERNS = [
        r"\byou should\b",
        r"\byou must\b",
        r"\bmy advice is\b",
        r"\bI advise you\b",
        r"\bthe law requires you\b",
    ]

    def run(self, text: str) -> dict:
        issues = []
        for pattern in self.ADVICE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Advice-like phrasing detected: '{pattern}'")

        # Soften advice phrasing automatically
        cleaned = text
        replacements = [
            (r"\bYou should\b",       "You may wish to consider"),
            (r"\byou should\b",       "you may wish to consider"),
            (r"\bYou must\b",         "In many jurisdictions, it is required that"),
            (r"\byou must\b",         "in many jurisdictions, it is required that"),
            (r"\bMy advice is\b",     "General information suggests"),
            (r"\bmy advice is\b",     "general information suggests"),
            (r"\bI advise you\b",     "As general information"),
            (r"\bi advise you\b",     "as general information"),
        ]
        for find, replace in replacements:
            cleaned = re.sub(find, replace, cleaned)

        return {"reviewed_text": cleaned, "issues": issues}


# ── Orchestrator ──────────────────────────────────────────────────────────────

class Orchestrator:
    """
    Coordinates all agents in sequence and assembles the final response.
    Pipeline:
      IntakeAgent → PrivacyAgent → SafetyEscalationAgent →
      LegalInfoAgent → SourceVerifyAgent → QualityReviewAgent
    """

    def __init__(self):
        self.intake      = IntakeAgent()
        self.privacy     = PrivacyAgent()
        self.legal_info  = LegalInfoAgent()
        self.source_ver  = SourceVerifyAgent()
        self.safety      = SafetyEscalationAgent()
        self.quality     = QualityReviewAgent()

    def handle(self, message: str, session_context: dict) -> dict:
        # 1. Intake — detect jurisdiction + domain
        intake_result = self.intake.run(message, session_context)
        context = intake_result["context"]
        needs_jurisdiction = intake_result["needs_jurisdiction"]

        # 2. If no jurisdiction yet, ask for it
        if needs_jurisdiction:
            return {
                "reply": (
                    "To give you the most relevant general legal information, "
                    "could you please tell me your **country** and, if in the US or Canada, "
                    "your **state or province**?"
                ),
                "needs_jurisdiction": True,
                "context": context,
                "is_urgent": False,
                "escalation_notice": "",
                "disclaimer": DISCLAIMER,
                "source_warning": "",
                "resource_url": LOCAL_LEGAL_HELP["default"],
                "domain": context.get("domain", "general"),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

        # 3. Privacy — redact PII
        clean_message = self.privacy.run(message)

        # 4. Safety escalation check
        safety_result = self.safety.run(message, context["jurisdiction"])

        # 5. Legal information via IBM Granite
        raw_answer = self.legal_info.run(clean_message, context)

        # 6. Source verification
        verify_result = self.source_ver.run(raw_answer)

        # 7. Quality review — soften advice language
        quality_result = self.quality.run(raw_answer)
        reviewed_answer = quality_result["reviewed_text"]

        # 8. Assemble response
        country_code = context["jurisdiction"].get("country", "default").lower()
        resource_url = LOCAL_LEGAL_HELP.get(country_code, LOCAL_LEGAL_HELP["default"])

        return {
            "reply": reviewed_answer,
            "needs_jurisdiction": False,
            "context": context,
            "is_urgent": safety_result["is_urgent"],
            "escalation_notice": safety_result["escalation_notice"],
            "disclaimer": DISCLAIMER,
            "source_warning": verify_result["warning"],
            "resource_url": resource_url,
            "domain": context.get("domain", "general"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


# ── Flask Routes ──────────────────────────────────────────────────────────────

orchestrator = Orchestrator()

# In-memory session store (keyed by session_id)
# Production: replace with Redis or a database
sessions: dict = {}


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: { "message": str, "session_id": str }
    Returns: structured JSON response from the orchestrator
    """
    data = request.get_json(silent=True) or {}
    message    = (data.get("message") or "").strip()
    session_id = (data.get("session_id") or "default").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Retrieve or create session context
    context = sessions.get(session_id, {})

    # Run orchestrator pipeline
    result = orchestrator.handle(message, context)

    # Persist updated context
    sessions[session_id] = result.get("context", context)

    return jsonify(result), 200


@app.route("/api/reset", methods=["POST"])
def reset():
    """POST /api/reset — clears session context."""
    data       = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "default").strip()
    sessions.pop(session_id, None)
    return jsonify({"status": "reset", "session_id": session_id}), 200


@app.route("/api/health", methods=["GET"])
def health():
    """GET /api/health — liveness check."""
    model_configured = bool(WX_API_KEY and WX_PROJECT_ID)
    return jsonify({
        "status": "ok",
        "model": GRANITE_MODEL,
        "model_configured": model_configured,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }), 200


# Serve React SPA for all non-API routes (production build only)
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    if not app.static_folder:
        return jsonify({
            "message": "API is running. Build the React frontend with: npm run build",
            "health": "/api/health",
            "chat": "POST /api/chat"
        }), 200
    dist = os.path.join(app.static_folder, path)
    if path and os.path.exists(dist):
        return app.send_static_file(path)
    return app.send_static_file("index.html")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    print(f"\n{'='*60}")
    print(f"  AI Legal Aid Multi-Agent System")
    print(f"  IBM Granite model : {GRANITE_MODEL}")
    print(f"  Model configured  : {bool(WX_API_KEY and WX_PROJECT_ID)}")
    print(f"  Listening on      : http://localhost:{port}")
    print(f"  API health check  : http://localhost:{port}/api/health")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
