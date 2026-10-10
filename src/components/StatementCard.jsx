const PILLS_BLUE = [
  'Goal-Driven Reasoning',
  'Multi-Step Planning',
  'Agent Orchestration',
]

const PILLS_GREY = [
  'Autonomous Execution',
  'Memory & Context',
  'Tool Use',
  'Feedback Loops',
  'Scalable Pipelines',
]

const StatementCard = () => (
  <div className="stmt-card">
    <div className="stmt-card__title">
      <span className="stmt-card__dot" />
      What is Agentic AI?
    </div>

    <div className="stmt-card__body">
      <p>
        <strong>Agentic AI</strong> describes artificial intelligence systems
        that operate with a high degree of <strong>autonomy</strong> — perceiving
        their environment, forming <strong>multi-step plans</strong>, executing
        actions through tools, and <strong>self-correcting</strong> based on
        real-time feedback, all with minimal human intervention.
      </p>
      <p>
        Unlike single-turn AI that responds to one prompt and stops, an{' '}
        <strong>agentic system</strong> pursues goals across extended reasoning
        cycles. The <strong>AI Agent Aid Multi-Agent System</strong> orchestrates
        a network of specialised agents — each expert in a distinct domain such
        as <strong>legal research</strong>, <strong>document analysis</strong>,{' '}
        <strong>case strategy</strong>, and{' '}
        <strong>client communication</strong> — forming a unified, intelligent
        pipeline that delivers accurate, context-aware outcomes at scale.
      </p>
    </div>

    <div className="pillbox">
      {PILLS_BLUE.map((label) => (
        <span key={label} className="pill pill--blue">{label}</span>
      ))}
      {PILLS_GREY.map((label) => (
        <span key={label} className="pill">{label}</span>
      ))}
    </div>
  </div>
)

export default StatementCard
