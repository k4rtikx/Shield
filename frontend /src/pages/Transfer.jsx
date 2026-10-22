import {useState} from 'react';import {RefreshCw,AlertTriangle,XCircle,Zap} from 'lucide-react';
import Navbar from '../components/Navbar.jsx';import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import {transfer} from '../api/transactions.js';import {OID,AMT,errMsg} from '../api/client.js';
function Confetti(){const c=['#3D7FFF','#00E5FF','#00FF94','#FFB800','#FF3D6B'];
 return <div className="confetti">{Array.from({length:30},(_,i)=><i key={i} style={{background:c[i%5],'--dx':`${(Math.random()-.5)*360}px`,'--dy':`${(Math.random()-.8)*280}px`}}/>)}</div>;}
export default function Transfer(){
 const [f,setF]=useState({s:localStorage.getItem('shield_account_id')||'',r:'',a:''});const [key,setKey]=useState(crypto.randomUUID());const [busy,setBusy]=useState(false);const [out,setOut]=useState(null);const [e,setE]=useState({});const [boom,setBoom]=useState(false);
 const amt=v=>{if(v===''||/^\d*\.?\d{0,2}$/.test(v))setF({...f,a:v});};
 const submit=async ev=>{ev.preventDefault();const x={};if(!OID.test(f.s))x.s='Enter a 24-character hex account ID.';if(!OID.test(f.r))x.r='Enter a 24-character hex account ID.';
  if(!AMT.test(f.a)||+f.a<=0)x.a='Enter an amount greater than 0.';setE(x);if(Object.keys(x).length)return;
  setBusy(true);setOut(null);
  try{const t=await transfer({sender_account_id:f.s,receiver_account_id:f.r,amount:(+f.a).toFixed(2)},key);setOut({k:'ok',t});setBoom(true);setTimeout(()=>setBoom(false),1100);localStorage.setItem('shield_account_id',f.s);setKey(crypto.randomUUID());setF({...f,a:''});}
  catch(er){const m=errMsg(er);const l=m.toLowerCase();setOut({k:l.includes('insufficient')?'bal':l.includes('review')?'review':'decline',m});if(!l.includes('reused'))setKey(crypto.randomUUID());}
  setBusy(false);};
 return <><ThreeBackground scene="particles"/><Navbar/><main className="page container narrow"><GlassCard className="form-card"><h2>Send money</h2>
  <form onSubmit={submit} noValidate>
   <label>Sender account ID<input className={`mono-input ${e.s?'invalid':''}`} value={f.s} onChange={ev=>setF({...f,s:ev.target.value.trim()})}/>{e.s&&<span className="field-err">{e.s}</span>}</label>
   <label>Receiver account ID<input className={`mono-input ${e.r?'invalid':''}`} value={f.r} onChange={ev=>setF({...f,r:ev.target.value.trim()})}/>{e.r&&<span className="field-err">{e.r}</span>}</label>
   <label>Amount<span className="input-wrap"><b className="prefix">$</b><input className={`money pad-l ${e.a?'invalid':''}`} inputMode="decimal" value={f.a} onChange={ev=>amt(ev.target.value)} placeholder="0.00"/></span>{e.a&&<span className="field-err">{e.a}</span>}</label>
   <div className="idem">Idempotency key: <code>{key}</code><button type="button" className="icon-btn" onClick={()=>setKey(crypto.randomUUID())} aria-label="New key"><RefreshCw size={14}/></button></div>
   <button className="btn shine" disabled={busy}>{busy?<LoadingSpinner small/>:'Send transfer'}</button></form></GlassCard>
  {out?.k==='ok'&&<div className="outcome ok slide-up">{boom&&<Confetti/>}<svg className="check" viewBox="0 0 52 52"><circle cx="26" cy="26" r="24"/><path d="M14 27l8 8 16-17"/></svg><div><b>Transfer complete</b><p className="money">${out.t.amount}</p><code>{out.t._id}</code></div></div>}
  {out?.k==='review'&&<div className="outcome warn slide-up"><AlertTriangle/><div><b>Transfer flagged for manual review</b><p>{out.m}</p></div></div>}
  {out?.k==='decline'&&<div className="outcome bad slide-up"><XCircle/><div><b>Transfer not completed</b><p>{out.m}</p></div></div>}
  {out?.k==='bal'&&<div className="outcome warn slide-up"><Zap/><div><b>Insufficient balance</b><p>{out.m}</p></div></div>}</main></>;}
