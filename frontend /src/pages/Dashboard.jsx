import {useEffect,useMemo,useState} from 'react';import {Link} from 'react-router-dom';
import Navbar from '../components/Navbar.jsx';import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';
import DigitRoll from '../components/DigitRoll.jsx';import RiskGauge from '../components/RiskGauge.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import {useAuth} from '../context/AuthContext.jsx';import {history} from '../api/transactions.js';import {OID} from '../api/client.js';
export const fmt=n=>Number(n).toFixed(2);export const short=id=>id?`${id.slice(0,6)}…${id.slice(-4)}`:'—';
export default function Dashboard(){
 const {user}=useAuth();const [tx,setTx]=useState(null);const [acct,setAcct]=useState(localStorage.getItem('shield_account_id')||'');
 useEffect(()=>{history().then(setTx).catch(()=>setTx([]));},[]);
 const saveAcct=v=>{setAcct(v);if(OID.test(v))localStorage.setItem('shield_account_id',v);};
 const st=useMemo(()=>{const mine=OID.test(acct)?acct:null;let sent=0,recv=0;(tx||[]).forEach(t=>{if(!mine)return;if(t.sender_account_id===mine)sent+=+t.amount;if(t.receiver_account_id===mine)recv+=+t.amount;});return {sent,recv,net:recv-sent};},[tx,acct]);
 const last=(tx||[]).slice(0,3);const la=JSON.parse(sessionStorage.getItem('shield_last_analysis')||'null');
 return <><ThreeBackground scene="hex"/><Navbar/><main className="page container">
  <div className="grid2"><GlassCard tilt><p className="label">Your account</p><p className="muted">{user.username} · {user.email}</p>
    <input className="mono-input" placeholder="Paste your 24-char account ID" value={acct} onChange={e=>saveAcct(e.target.value.trim())}/>
    <p className="label">Net flow</p><div className="big">$<DigitRoll value={fmt(st.net)}/></div><p className="muted small">Masked ID: {acct?short(acct):'not set'}. The API does not expose balances, so net flow is computed from your history.</p></GlassCard>
   <GlassCard tilt><p className="label">Recent activity</p>{!tx?<LoadingSpinner small/>:last.length===0?<p className="muted">No transactions yet. <Link to="/transfer">Make a transfer</Link></p>:
    last.map(t=><div className="mini-row" key={t._id}><span>{new Date(t.created_at).toLocaleDateString()}</span><b className="money">${fmt(t.amount)}</b><span className={`badge badge-${t.status==='completed'?'allow':'review'}`}>{t.status}</span></div>)}</GlassCard></div>
  <div className="grid4">{[['Total sent',`$${fmt(st.sent)}`],['Total received',`$${fmt(st.recv)}`],['Transactions',tx?.length??'—']].map(([l,v])=><GlassCard tilt key={l}><p className="label">{l}</p><div className="big money">{v}</div></GlassCard>)}
   <GlassCard tilt><p className="label">Status</p><div className="big live"><i className="pulse-dot"/>System live</div></GlassCard></div>
  <GlassCard className="gauge-card"><p className="label">Live fraud risk</p><RiskGauge score={la?.risk_score??null}/>
   <div className="pills">{(la?.risk_factors||[]).map(f=><span key={f} className="pill">{f}</span>)}</div></GlassCard></main></>;}
