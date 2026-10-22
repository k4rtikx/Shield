import {useState} from 'react';import {Link} from 'react-router-dom';
import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import LoadingSpinner from '../components/LoadingSpinner.jsx';
import {register} from '../api/accounts.js';import {useToast} from '../components/ToastContext.jsx';import {useVTNavigate} from '../components/Navbar.jsx';
const strength=p=>[p.length>=8,/[A-Z]/.test(p),/[0-9]/.test(p),/[^A-Za-z0-9]/.test(p),p.length>=12].filter(Boolean).length;
export default function Register(){
 const toast=useToast();const go=useVTNavigate();const [f,setF]=useState({username:'',email:'',password:'',password_confirm:''});const [errs,setErrs]=useState({});const [busy,setBusy]=useState(false);
 const set=k=>e=>setF({...f,[k]:e.target.value});const sc=strength(f.password);
 const validate=()=>{const e={};if(f.username.trim().length<3)e.username='Use at least 3 characters.';if(!/^\S+@\S+\.\S+$/.test(f.email))e.email='Enter a valid email address.';
  if(f.password.length<8)e.password='Use at least 8 characters.';if(f.password!==f.password_confirm)e.password_confirm='Passwords do not match.';return e;};
 const submit=async ev=>{ev.preventDefault();const e=validate();setErrs(e);if(Object.keys(e).length)return;setBusy(true);
  try{await register({...f,username:f.username.trim()});toast.success('Account created. Log in to continue.');go('/login');}
  catch(x){const d=x.data||{};const m={};Object.keys(d).forEach(k=>m[k]=[].concat(d[k]).join(' '));if(!Object.keys(m).length)m.form='Registration failed';setErrs(m);toast.error(m.error||m.form||'Please fix the highlighted fields.');}setBusy(false);};
 const F=(k,l,t='text')=><label>{l}<input type={t} value={f[k]} onChange={set(k)} className={errs[k]?'invalid':''} required/>{errs[k]&&<span className="field-err">{errs[k]}</span>}</label>;
 return <main className="page center-screen"><ThreeBackground scene="grid"/><GlassCard tilt className="auth-card"><h2>Create your account</h2>
  <form onSubmit={submit} noValidate>{F('username','Username')}{F('email','Email','email')}{F('password','Password','password')}
   <div className="meter"><i className={`s${sc}`} style={{width:`${sc*20}%`}}/></div>{F('password_confirm','Confirm password','password')}
   {(errs.error||errs.form)&&<div className="field-err">{errs.error||errs.form}</div>}<button className="btn shine" disabled={busy}>{busy?<LoadingSpinner small/>:'Create account'}</button></form>
  <p className="muted">Already registered? <Link to="/login">Log in</Link></p></GlassCard></main>;}
