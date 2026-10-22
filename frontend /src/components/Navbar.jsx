import {useState} from 'react';import {NavLink,useNavigate} from 'react-router-dom';import {LogOut,Menu,X} from 'lucide-react';import {useAuth} from '../context/AuthContext.jsx';
export const useVTNavigate=()=>{const n=useNavigate();return to=>document.startViewTransition?document.startViewTransition(()=>n(to)):n(to);};
export function Logo({size=28}){return <svg width={size} height={size} viewBox="0 0 24 24" className="logo-svg"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#00E5FF"><animate attributeName="stop-color" values="#00E5FF;#3D7FFF;#00FF94;#00E5FF" dur="6s" repeatCount="indefinite"/></stop><stop offset="1" stopColor="#3D7FFF"/></linearGradient></defs><path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z" fill="url(#lg)"/></svg>;}
const links=[['/dashboard','Dashboard'],['/transfer','Transfer'],['/history','History'],['/fraud','Fraud Analyzer']];
export default function Navbar(){
 const {user,logout}=useAuth();const go=useVTNavigate();const [open,setOpen]=useState(false);
 const click=to=>e=>{e.preventDefault();setOpen(false);go(to);};
 return <header className="navbar"><a href="/dashboard" className="brand" onClick={click('/dashboard')}><Logo/><span>Shield</span></a>
  <button className="icon-btn burger" onClick={()=>setOpen(!open)} aria-label="Menu">{open?<X/>:<Menu/>}</button>
  <nav className={`nav-links ${open?'open':''}`}>{links.map(([to,l])=><NavLink key={to} to={to} onClick={click(to)}>{l}</NavLink>)}
   <div className="user-chip"><span className="avatar">{user?.username?.[0]?.toUpperCase()}</span>{user?.username}
    <button className="icon-btn" aria-label="Log out" onClick={()=>{logout();go('/login');}}><LogOut size={18}/></button></div></nav></header>;}
