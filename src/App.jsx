import { useState, useRef, useEffect, useCallback } from 'react'
import axios from 'axios'

// ── Unique session ID per browser tab ──────────────────────────────────────
const SESSION_ID = `session_${Math.random().toString(36).slice(2, 10)}`

// ── Colour palette constants ───────────────────────────────────────────────
const C = {
  bg:        '#0f1117',
  surface:   '#161b27',
  border:    '#1e2d45',
  borderSub: '#1a2438',
  text:      '#e2e8f0',
  muted:     '#64748b',
  blue:      '#3b82f6',
  blueDim:   'rgba(59,130,246,0.12)',
  blueBorder:'rgba(59,130,246,0.3)',
  green:     '#22c55e',
  orange:    '#f97316',
  red:       '#ef4444',
  violet:    '#7c3aed',
}

// ── Inline styles (no CSS-in-JS library needed) ────────────────────────────
const S = {
  layout: {
    display: 'flex', flexDirection: 'column', height: '100vh',
    background: C.bg, color: C.text,
  },
  // Header
  header: {
    background: C.surface, borderBottom: `1px solid ${C.border}`,
    padding: '14px 24px', display: 'flex', alignItems: 'center',
    justifyContent: 'space-between', flexShrink: 0,
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 12 },
  headerIcon: { fontSize: 22 },
  headerTitle: { fontSize: '1rem', fontWeight: 700, color: C.text },
  headerSub: { fontSize: '0.72rem', color: C.muted, marginTop: 2 },
  badgeGreen: {
    background: 'rgba(34,197,94,0.1)', border: '1px solid rgba(34,197,94,0.3)',
    color: C.green, fontSize: '0.68rem', fontWeight: 700,
    padding: '2px 9px', borderRadius: 20, letterSpacing: '0.8px',
    textTransform: 'uppercase',
  },
  resetBtn: {
    background: 'transparent', border: `1px solid ${C.border}`,
    color: C.muted, fontSize: '0.75rem', padding: '5px 12px',
    borderRadius: 6, cursor: 'pointer',
  },
  // Banner
  banner: {
    background: 'rgba(59,130,246,0.06)', borderBottom: `1px solid ${C.blueBorder}`,
    padding: '8px 24px', fontSize: '0.75rem', color: '#93c5fd',
    textAlign: 'center', flexShrink: 0,
  },
  // Messages
  messages: {
    flex: 1, overflowY: 'auto', padding: '24px',
    display: 'flex', flexDirection: 'column', gap: 16,
  },
  // Bubble wrappers
  rowUser: { display: 'flex', justifyContent: 'flex-end' },
  rowBot:  { display: 'flex', justifyContent: 'flex-start' },
  bubbleUser: {
    background: C.blue, color: '#fff', padding: '12px 16px',
    borderRadius: '16px 16px 4px 16px', maxWidth: '72%',
    fontSize: '0.9rem', lineHeight: 1.6,
  },
  bubbleBot: {
    background: C.surface, border: `1px solid ${C.border}`,
    padding: '14px 18px', borderRadius: '4px 16px 16px 16px',
    maxWidth: '82%', fontSize: '0.9rem', lineHeight: 1.6,
  },
  // Alert blocks inside bot bubble
  alertUrgent: {
    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 8, padding: '10px 14px', marginTop: 10,
    fontSize: '0.82rem', color: '#fca5a5', lineHeight: 1.6,
  },
  alertSource: {
    background: 'rgba(249,115,22,0.08)', border: '1px solid rgba(249,115,22,0.25)',
    borderRadius: 8, padding: '10px 14px', marginTop: 10,
    fontSize: '0.78rem', color: '#fdba74', lineHeight: 1.6,
  },
  alertDisclaimer: {
    background: 'rgba(59,130,246,0.06)', border: `1px solid ${C.blueBorder}`,
    borderRadius: 8, padding: '10px 14px', marginTop: 10,
    fontSize: '0.78rem', color: '#93c5fd', lineHeight: 1.6,
  },
  resourceLink: {
    display: 'inline-block', marginTop: 8,
    color: C.blue, fontSize: '0.78rem', textDecoration: 'none',
    borderBottom: `1px dashed ${C.blue}`,
  },
  domainPill: {
    display: 'inline-block',
    background: C.blueDim, border: `1px solid ${C.blueBorder}`,
    color: '#93c5fd', fontSize: '0.68rem', fontWeight: 600,
    padding: '2px 9px', borderRadius: 20, marginTop: 8,
    textTransform: 'uppercase', letterSpacing: '0.7px',
  },
  timestamp: { fontSize: '0.66rem', color: C.muted, marginTop: 6 },
  // Typing indicator
  typingDot: {
    display: 'inline-block', width: 7, height: 7,
    background: C.muted, borderRadius: '50', margin: '0 2px',
  },
  // Input area
  inputArea: {
    background: C.surface, borderTop: `1px solid ${C.border}`,
    padding: '16px 24px', flexShrink: 0,
  },
  inputRow: { display: 'flex', gap: 10 },
  textarea: {
    flex: 1, background: '#0f1117', border: `1px solid ${C.border}`,
    color: C.text, borderRadius: 10, padding: '11px 14px',
    fontSize: '0.9rem', resize: 'none', outline: 'none',
    fontFamily: 'inherit', lineHeight: 1.5,
  },
  sendBtn: {
    background: C.blue, color: '#fff', border: 'none',
    borderRadius: 10, padding: '0 20px', cursor: 'pointer',
    fontSize: '1.1rem', fontWeight: 700, flexShrink: 0,
    opacity: 1,
  },
  sendBtnDisabled: { opacity: 0.45, cursor: 'not-allowed' },
  inputHint: { fontSize: '0.68rem', color: C.muted, marginTop: 6, textAlign: 'center' },
  // Welcome card
  welcome: {
    background: C.surface, border: `1px solid ${C.border}`,
    borderRadius: 14, padding: 28, maxWidth: 540, margin: '0 auto',
    textAlign: 'center',
  },
  welcomeIcon: { fontSize: 36, marginBottom: 12 },
  welcomeTitle: { fontSize: '1.1rem', fontWeight: 700, color: C.text, marginBottom: 8 },
  welcomeSub: { fontSize: '0.85rem', color: C.muted, lineHeight: 1.7 },
  welcomeGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 18,
  },
  welcomeChip: {
    background: '#0f1117', border: `1px solid ${C.borderSub}`,
    borderRadius: 8, padding: '8px 10px', fontSize: '0.76rem',
    color: '#94a3b8', textAlign: 'left', cursor: 'pointer',
  },
}

// ── Helpers ────────────────────────────────────────────────────────────────
const fmtTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const EXAMPLE_QUESTIONS = [
  '🏠 Can my landlord evict me without notice?',
  '👔 What are my rights if I was wrongfully fired?',
  '🧾 How do I dispute a debt collector?',
  '👨‍👩‍👧 How does child custody work after divorce?',
]

// ── Typing indicator component ─────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div style={S.rowBot}>
      <div style={{ ...S.bubbleBot, padding: '14px 20px' }}>
        <span style={{ fontSize: '0.78rem', color: C.muted }}>AI Legal Aid is thinking</span>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            style={{
              ...S.typingDot,
              animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
        <style>{`
          @keyframes bounce {
            0%,80%,100% { transform:translateY(0) }
            40%          { transform:translateY(-5px) }
          }
        `}</style>
      </div>
    </div>
  )
}

// ── Bot message bubble ─────────────────────────────────────────────────────
function BotBubble({ msg }) {
  const {
    reply, disclaimer, escalation_notice, source_warning,
    resource_url, domain, timestamp,
  } = msg

  return (
    <div style={S.rowBot}>
      <div style={S.bubbleBot}>
        {/* Main reply */}
        <div style={{ whiteSpace: 'pre-wrap' }}>{reply}</div>

        {/* Domain pill */}
        {domain && domain !== 'general' && (
          <span style={S.domainPill}>{domain}</span>
        )}

        {/* Urgency escalation */}
        {escalation_notice && (
          <div style={S.alertUrgent}>{escalation_notice}</div>
        )}

        {/* Source warning */}
        {source_warning && (
          <div style={S.alertSource}>{source_warning}</div>
        )}

        {/* Disclaimer */}
        {disclaimer && (
          <div style={S.alertDisclaimer}>{disclaimer}</div>
        )}

        {/* Resource link */}
        {resource_url && (
          <div style={{ marginTop: 10 }}>
            <a
              href={resource_url}
              target="_blank"
              rel="noopener noreferrer"
              style={S.resourceLink}
            >
              🔗 Find local legal help →
            </a>
          </div>
        )}

        {/* Timestamp */}
        <div style={S.timestamp}>{fmtTime(timestamp)}</div>
      </div>
    </div>
  )
}

// ── Welcome card ───────────────────────────────────────────────────────────
function WelcomeCard({ onExample }) {
  return (
    <div style={S.welcome}>
      <div style={S.welcomeIcon}>⚖️</div>
      <div style={S.welcomeTitle}>AI Legal Aid Multi-Agent System</div>
      <div style={S.welcomeSub}>
        Ask any general legal question. I'll ask for your location when
        needed and direct urgent cases to qualified local help.
        <br /><br />
        <em style={{ color: '#60a5fa', fontSize: '0.78rem' }}>
          This provides general information only — not legal advice.
        </em>
      </div>
      <div style={S.welcomeGrid}>
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            style={S.welcomeChip}
            onClick={() => onExample(q.slice(2).trim())}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Main App ───────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = useCallback(async (text) => {
    const trimmed = (text || input).trim()
    if (!trimmed || loading) return

    // Append user bubble
    setMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/chat', {
        message: trimmed,
        session_id: SESSION_ID,
      })
      setMessages((prev) => [...prev, { role: 'bot', ...data }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          reply: 'Sorry, I could not reach the server. Please check that the Flask backend is running on port 5000.',
          disclaimer: '',
          escalation_notice: '',
          source_warning: '',
          resource_url: 'https://www.legalaidatwork.org/',
          domain: '',
          timestamp: new Date().toISOString(),
        },
      ])
    } finally {
      setLoading(false)
      setTimeout(() => textareaRef.current?.focus(), 50)
    }
  }, [input, loading])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleReset = async () => {
    try {
      await axios.post('/api/reset', { session_id: SESSION_ID })
    } catch (_) { /* ignore */ }
    setMessages([])
    setInput('')
  }

  return (
    <div style={S.layout}>
      {/* ── Header ── */}
      <header style={S.header}>
        <div style={S.headerLeft}>
          <span style={S.headerIcon}>⚖️</span>
          <div>
            <div style={S.headerTitle}>AI Legal Aid</div>
            <div style={S.headerSub}>Multi-Agent System · IBM Granite</div>
          </div>
          <span style={S.badgeGreen}>Live</span>
        </div>
        <button style={S.resetBtn} onClick={handleReset}>
          ↺ New Conversation
        </button>
      </header>

      {/* ── Disclaimer banner ── */}
      <div style={S.banner}>
        General legal <strong>information</strong> only — not legal advice.
        No attorney-client relationship is created.
      </div>

      {/* ── Messages ── */}
      <div style={S.messages}>
        {messages.length === 0 && (
          <WelcomeCard onExample={(q) => sendMessage(q)} />
        )}

        {messages.map((msg, i) =>
          msg.role === 'user' ? (
            <div key={i} style={S.rowUser}>
              <div style={S.bubbleUser}>{msg.text}</div>
            </div>
          ) : (
            <BotBubble key={i} msg={msg} />
          )
        )}

        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* ── Input ── */}
      <div style={S.inputArea}>
        <div style={S.inputRow}>
          <textarea
            ref={textareaRef}
            rows={2}
            style={S.textarea}
            placeholder="Type your legal question… (Shift+Enter for new line)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            style={{
              ...S.sendBtn,
              ...(loading || !input.trim() ? S.sendBtnDisabled : {}),
            }}
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            aria-label="Send"
          >
            ➤
          </button>
        </div>
        <div style={S.inputHint}>
          Powered by IBM Granite (watsonx.ai) · Your data is not stored beyond this session
        </div>
      </div>
    </div>
  )
}
