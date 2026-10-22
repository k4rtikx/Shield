import {useEffect,useState} from 'react';
export const riskColor=s=>s>=70?'var(--accent-red)':s>=30?'var(--accent-amber)':'var(--accent-green)';
export default function RiskGauge({score=null,size=220,mini=false}){
 const R=54,C=2*Math.PI*R*.75;const [v,setV]=useState(0);
 useEffect(()=>{setV(0);if(score==null)return;const id=requestAnimationFrame(()=>requestAnimationFrame(()=>setV(score)));return()=>cancelAnimationFrame(id);},[score]);
 const col=score==null?'var(--text-muted)':riskColor(score);
 return <div className="gauge" style={{width:mini?110:size,height:mini?110:size}}>
  <svg viewBox="0 0 140 140"><g transform="rotate(135 70 70)">
   <circle cx="70" cy="70" r={R} className="gauge-track" strokeDasharray={`${C} 999`}/>
   <circle cx="70" cy="70" r={R} className="gauge-fill" stroke={col} strokeDasharray={`${C} 999`} strokeDashoffset={C-(C*v)/100} style={{filter:`drop-shadow(0 0 6px ${col})`}}/></g></svg>
  <div className="gauge-label">{score==null?<small>No analysis<br/>run yet</small>:<><b className="money" style={{color:col}}>{Math.round(score)}</b><small>risk score</small></>}</div></div>;}
