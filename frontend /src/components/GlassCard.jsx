import {useRef} from 'react';
export default function GlassCard({tilt=false,className='',children,...p}){
 const ref=useRef();
 const move=e=>{if(!tilt)return;const b=ref.current.getBoundingClientRect();const x=(e.clientX-b.left)/b.width-.5,y=(e.clientY-b.top)/b.height-.5;
  requestAnimationFrame(()=>{if(ref.current)ref.current.style.transform=`perspective(900px) rotateX(${(-y*24).toFixed(1)}deg) rotateY(${(x*24).toFixed(1)}deg)`;});};
 const leave=()=>{if(ref.current)ref.current.style.transform='';};
 return <div ref={ref} className={`glass ${tilt?'tilt':''} ${className}`} onMouseMove={move} onMouseLeave={leave} {...p}>{children}</div>;}
