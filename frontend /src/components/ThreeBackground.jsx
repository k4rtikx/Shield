import {useEffect,useRef} from 'react';import * as THREE from 'three';
export default function ThreeBackground({scene='particles'}){
 const ref=useRef();
 useEffect(()=>{
  const cv=ref.current;const r=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true});r.setPixelRatio(Math.min(devicePixelRatio,2));
  const s=new THREE.Scene(),cam=new THREE.PerspectiveCamera(60,1,.1,300);cam.position.set(0,0,30);
  const col=scene==='wisps'?0xff3d6b:0x00e5ff;const g=new THREE.Group();s.add(g);let mover=null;
  const cloud=(n,spread,size)=>{const p=new Float32Array(n*3);for(let i=0;i<p.length;i++)p[i]=(Math.random()-.5)*spread;
   const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(p,3));
   const pts=new THREE.Points(geo,new THREE.PointsMaterial({color:col,size,transparent:true,opacity:.8}));g.add(pts);return {p,pts};};
  if(scene==='shield'){
   const sh=new THREE.Shape();sh.moveTo(0,7);sh.bezierCurveTo(4,6,6,5.5,7,5);sh.bezierCurveTo(7,-2,5,-6,0,-9);sh.bezierCurveTo(-5,-6,-7,-2,-7,5);sh.bezierCurveTo(-6,5.5,-4,6,0,7);
   const m=new THREE.Mesh(new THREE.ExtrudeGeometry(sh,{depth:1.6,bevelEnabled:true,bevelSize:.5,bevelThickness:.5}),new THREE.MeshStandardMaterial({color:0x3d7fff,metalness:.95,roughness:.22}));
   m.position.z=-4;s.add(m);const w=new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),new THREE.LineBasicMaterial({color:0x00e5ff}));m.add(w);
   s.add(new THREE.AmbientLight(0x4466aa,.8));const l=new THREE.PointLight(0x00e5ff,900,100);l.position.set(10,10,15);s.add(l);
   const {p}=cloud(90,60,.35);const lp=[];for(let i=0;i<90;i++)for(let j=i+1;j<90;j++){const dx=p[i*3]-p[j*3],dy=p[i*3+1]-p[j*3+1],dz=p[i*3+2]-p[j*3+2];
    if(dx*dx+dy*dy+dz*dz<110)lp.push(p[i*3],p[i*3+1],p[i*3+2],p[j*3],p[j*3+1],p[j*3+2]);}
   const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));
   g.add(new THREE.LineSegments(lg,new THREE.LineBasicMaterial({color:0x3d7fff,transparent:true,opacity:.18})));
   mover=(dt,t)=>{m.rotation.y+=dt*.5;m.position.y=Math.sin(t)*.8;g.rotation.y+=dt*.03;};
  }else if(scene==='grid'){
   const gr=new THREE.GridHelper(120,60,0x00e5ff,0x1a3a6a);gr.position.y=-8;s.add(gr);cam.position.set(0,4,25);cloud(80,60,.2);
   mover=(dt,t)=>{gr.position.z=(t*2)%2;g.rotation.y+=dt*.02;};
  }else if(scene==='hex'){
   const geo=new THREE.CylinderGeometry(1.5,1.5,.3,6);const hs=[];
   for(let i=0;i<70;i++){const h=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:i%5?0x3d7fff:0x00e5ff,wireframe:true,transparent:true,opacity:.35}));
    h.position.set((Math.random()-.5)*70,(Math.random()-.5)*40,(Math.random()-.5)*30-10);h.rotation.x=Math.PI/2+Math.random();h.userData.o=Math.random()*6;g.add(h);hs.push(h);}
   mover=(dt,t)=>hs.forEach(h=>{h.rotation.z+=dt*.2;h.position.y+=Math.sin(t+h.userData.o)*dt*.8;});
  }else{
   const {pts}=cloud(scene==='wisps'?260:200,70,scene==='wisps'?.5:.3);
   mover=(dt,t)=>{g.rotation.y+=dt*.04;g.rotation.x=Math.sin(t*.2)*.1;if(scene==='wisps'){const a=pts.geometry.attributes.position;for(let i=0;i<a.count;i++)a.array[i*3+1]+=Math.sin(t+i)*dt*.6;a.needsUpdate=true;}};
  }
  const mouse={x:0};const mm=e=>{mouse.x=e.clientX/innerWidth-.5;};addEventListener('mousemove',mm);
  const rs=()=>{r.setSize(innerWidth,innerHeight,false);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();};rs();addEventListener('resize',rs);
  const clock=new THREE.Clock();let raf,t=0;
  const loop=()=>{raf=requestAnimationFrame(loop);const dt=Math.min(clock.getDelta(),.05);t+=dt;mover&&mover(dt,t);
   cam.position.x+=(mouse.x*6-cam.position.x)*dt*2;cam.lookAt(0,0,0);r.render(s,cam);};loop();
  return()=>{cancelAnimationFrame(raf);removeEventListener('resize',rs);removeEventListener('mousemove',mm);
   s.traverse(o=>{o.geometry?.dispose();o.material?.dispose?.();});r.dispose();};
 },[scene]);
 return <canvas ref={ref} className="three-bg" aria-hidden="true"/>;}
