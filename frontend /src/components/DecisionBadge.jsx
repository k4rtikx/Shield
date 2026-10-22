export default function DecisionBadge({decision}){return <span className={`badge badge-${decision}`}>{String(decision).toUpperCase()}</span>;}
