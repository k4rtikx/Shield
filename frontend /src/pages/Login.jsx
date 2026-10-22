import {useState} from 'react';import {Link} from 'react-router-dom';import {Eye,EyeOff} from 'lucide-react';
import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import {useAuth} from '../context/AuthContext.jsx';import {useVTNavigate} from '../components/Navbar.jsx';import {errMsg} from '../api/client.js';
export default function Login(){
 const {login}=useAuth();const go=useVTNavigate();const [f,setF]=useState({username:'',password:''});const [show,setShow]=useState(false);const [err,setErr]=useState('');const [busy,setBusy]=useState(false);const [shake,setShake]=useState(0);
 const submit=async e=>{e.preventDefault();setBusy(true);setErr('');try{await login(f.username.trim(),f.password);go('/dashboard');}catch(x){setErr(errMsg(x));setShake(s=>s+1);}setBusy(false);};
 return <main className="page center-screen"><ThreeBackground scene="grid"/>
  <GlassCard tilt className={`auth-card ${err?'has-error':''}`} key={shake}><h2>Welcome back</h2><p className="muted">Log in to your Shield account.</p>
   <form onSubmit={submit}><label>Username<input value={f.username} onChange={e=>setF({...f,username:e.target.value})} required autoComplete="username"/></label>
    <label>Password<span className="input-wrap"><input type={show?'text':'password'} value={f.password} onChange={e=>setF({...f,password:e.target.value})} required autoComplete="current-password"/>
     <button type="button" className="icon-btn" onClick={()=>setShow(!show)} aria-label="Toggle password">{show?<EyeOff size={18}/>:<Eye size={18}/>}</button></span></label>
    {err&&<div className="field-err">{err}</div>}<button className="btn shine" disabled={busy}>{busy?<LoadingSpinner small/>:'Log in'}</button></form>
   <p className="muted">Don't have an account? <Link to="/register">Register</Link></p></GlassCard></main>;}
