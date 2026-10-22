import {useEffect,useMemo,useState,Fragment} from 'react';import {ArrowUpDown} from 'lucide-react';
import Navbar from '../components/Navbar.jsx';import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import RiskGauge from '../components/RiskGauge.jsx';import DecisionBadge from '../components/DecisionBadge.jsx';import {history} from '../api/transactions.js';import {analyze} from '../api/fraud.js';import {errMsg} from '../api/client.js';
import {useToast} from '../components/ToastContext.jsx';import {fmt,short} from './Dashboard.jsx';
const PER=10;
export default function History(){
 const toast=useToast();const [tx,setTx]=useState(null);const [q,setQ]=useState('all');const [sort,setSort]=useState({k:'created_at',d:-1});const [pg,setPg]=useState(0);const [open,setOpen]=useState(null);const [res,setRes]=useState({});
 useEffect(()=>{history().then(setTx).catch(e=>{toast.error(errMsg(e));setTx([]);});},[]);
 const rows=useMemo(()=>(tx||[]).filter(t=>q==='all'||(q==='completed')===(t.status==='completed')).sort((a,b)=>{const x=sort.k==='amount'?+a.amount-+b.amount:new Date(a.created_at)-new Date(b.created_at);return x*sort.d;}),[tx,q,sort]);
 const pages=Math.max(1,Math.ceil(rows.length/PER));const view=rows.slice(pg*PER,pg*PER+PER);
 const run=async id=>{if(open===id){setOpen(null);return;}setOpen(id);if(res[id]?.data)return;setRes(r=>({...r,[id]:{loading:true}}));
  try{const d=await analyze(id);sessionStorage.setItem('shield_last_analysis',JSON.stringify(d));setRes(r=>({...r,[id]:{data:d}}));}catch(e){setRes(r=>({...r,[id]:{error:errMsg(e)}}));}};
 const S=k=><button className="th" onClick={()=>setSort(s=>({k,d:s.k===k?-s.d:-1}))}>{k==='amount'?'Amount':'Date'}<ArrowUpDown size={12}/></button>;
 return <><ThreeBackground scene="grid"/><Navbar/><main className="page container"><div className="row between"><h2>Transaction history</h2>
  <select value={q} onChange={e=>{setQ(e.target.value);setPg(0);}}><option value="all">All statuses</option><option value="completed">Completed</option><option value="other">Not completed</option></select></div>
  {!tx?<div className="center"><LoadingSpinner/></div>:rows.length===0?<GlassCard className="empty"><svg viewBox="0 0 120 90" width="140"><g className="cube"><path d="M60 10l40 20v36L60 86 20 66V30z" fill="none" stroke="var(--accent-cyan)" strokeWidth="2"/><path d="M20 30l40 20 40-20M60 50v36" fill="none" stroke="var(--accent-blue)" strokeWidth="2"/></g></svg><h3>No transactions yet</h3><p className="muted">Your transfers will appear here.</p></GlassCard>:<>
  <div className="trow thead"><span>{S('created_at')}</span><span>{S('amount')}</span><span>Sender</span><span>Receiver</span><span>Status</span><span/></div>
  {view.map(t=><Fragment key={t._id}><GlassCard className="trow"><span>{new Date(t.created_at).toLocaleString()}</span><b className="money">${fmt(t.amount)}</b><code>{short(t.sender_account_id)}</code><code>{short(t.receiver_account_id)}</code>
   <span className={`badge badge-${t.status==='completed'?'allow':t.status==='failed'||t.status==='declined'?'decline':'review'}`}>{t.status}</span><button className="btn btn-sm btn-ghost" onClick={()=>run(t._id)}>{open===t._id?'Hide':'Analyze fraud'}</button></GlassCard>
   <div className={`accordion ${open===t._id?'open':''}`}><div>{res[t._id]?.loading&&<LoadingSpinner small/>}{res[t._id]?.error&&<p className="field-err">{res[t._id].error}</p>}
    {res[t._id]?.data&&<div className="fraud-inline"><RiskGauge mini score={res[t._id].data.risk_score}/><div><DecisionBadge decision={res[t._id].data.decision}/><div className="pills">{res[t._id].data.risk_factors.map(f=><span className="pill" key={f}>{f}</span>)}{!res[t._id].data.risk_factors.length&&<span className="muted">No risk factors</span>}</div><p className="muted small">Analyzed {new Date(res[t._id].data.analyzed_at).toLocaleString()}</p></div></div>}</div></div></Fragment>)}
  <div className="row center"><button className="btn btn-sm btn-ghost" disabled={pg===0} onClick={()=>setPg(pg-1)}>Previous</button><span className="muted">Page {pg+1} of {pages}</span><button className="btn btn-sm btn-ghost" disabled={pg>=pages-1} onClick={()=>setPg(pg+1)}>Next</button></div></>}</main></>;}
