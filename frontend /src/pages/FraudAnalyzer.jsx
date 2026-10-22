import {useState} from 'react';
import Navbar from '../components/Navbar.jsx';import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import RiskGauge from '../components/RiskGauge.jsx';import DecisionBadge from '../components/DecisionBadge.jsx';import {analyze} from '../api/fraud.js';import {OID,errMsg} from '../api/client.js';
export default function FraudAnalyzer(){
 const [id,setId]=useState('');const [r,setR]=useState(null);const [err,setErr]=useState('');const [busy,setBusy]=useState(false);
 const go=async e=>{e.preventDefault();setErr('');setR(null);if(!OID.test(id.trim())){setErr('Enter a 24-character hex transaction ID.');return;}setBusy(true);
  try{const d=await analyze(id.trim());sessionStorage.setItem('shield_last_analysis',JSON.stringify(d));setR(d);}catch(x){setErr(errMsg(x));}setBusy(false);};
 return <><ThreeBackground scene="wisps"/><Navbar/><main className="page container narrow"><GlassCard className="form-card"><h2>Fraud analyzer</h2>
  <form onSubmit={go} noValidate><label>Transaction ID<input className={`mono-input ${err?'invalid':''}`} value={id} onChange={e=>setId(e.target.value)}/></label>{err&&<span className="field-err">{err}</span>}
   <button className="btn shine" disabled={busy}>{busy?<LoadingSpinner small/>:'Analyze'}</button></form>
  {r&&<div className="result scale-in"><RiskGauge score={r.risk_score} size={260}/><DecisionBadge decision={r.decision}/>
   <div className="row center"><span className="chip">Risk level: {r.risk_level}</span><span className="chip">Policy v{r.policy_version}</span></div>
   <div className="pills">{r.risk_factors.length?r.risk_factors.map(f=><span className="pill" key={f}>{f}</span>):<span className="muted">No risk factors detected</span>}</div>
   <p className="muted small">Analyzed {new Date(r.analyzed_at).toLocaleString()}</p></div>}</GlassCard></main></>;}
