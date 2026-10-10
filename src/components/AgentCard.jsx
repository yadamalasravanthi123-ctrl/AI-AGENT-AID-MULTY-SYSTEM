const AgentCard = ({ icon, name, description }) => (
  <div className="agent-card">
    <div className="agent-card__icon">{icon}</div>
    <h3 className="agent-card__name">{name}</h3>
    <p className="agent-card__desc">{description}</p>
  </div>
)

export default AgentCard
