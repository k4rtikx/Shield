import ThreeBackground from '../components/ThreeBackground.jsx';import GlassCard from '../components/GlassCard.jsx';import {Logo,useVTNavigate} from '../components/Navbar.jsx';
export default function Landing(){const go=useVTNavigate();return <main className="page hero">
 <ThreeBackground scene="shield"/><span className="float-badge fb1">10M+ Transactions Protected</span><span className="float-badge fb2">&lt; 8ms Fraud Decision</span><span className="float-badge fb3">99.99% Uptime</span>
 <GlassCard tilt className="hero-card"><Logo size={56}/><h1>Shield</h1><p>Real-time fraud-aware transfers</p>
  <div className="row center"><button className="btn" onClick={()=>go('/login')}>Login</button><button className="btn btn-ghost" onClick={()=>go('/register')}>Register</button></div></GlassCard></main>;}
