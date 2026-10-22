export const BASE='http://127.0.0.1:8000/api';
export const OID=/^[a-fA-F0-9]{24}$/;
export const AMT=/^\d+(\.\d{1,2})?$/;
export const tok=()=>localStorage.getItem('shield_access_token');
export const setTokens=(a,r)=>{localStorage.setItem('shield_access_token',a);if(r)localStorage.setItem('shield_refresh_token',r);};
export const clearTokens=()=>{localStorage.removeItem('shield_access_token');localStorage.removeItem('shield_refresh_token');};
async function refresh(){const r=localStorage.getItem('shield_refresh_token');if(!r)return false;
 try{const res=await fetch(BASE+'/accounts/token/refresh/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh:r})});
 if(!res.ok)return false;const d=await res.json();setTokens(d.access,d.refresh);return true;}catch{return false;}}
export async function api(path,{method='GET',body,headers={},auth=true}={},retried=false){
 const h={'Content-Type':'application/json',...headers};if(auth&&tok())h.Authorization='Bearer '+tok();
 let res;try{res=await fetch(BASE+path,{method,headers:h,body:body?JSON.stringify(body):undefined});}
 catch{throw {status:0,data:{error:'Cannot reach server at 127.0.0.1:8000'}};}
 if(res.status===401&&auth){
  if(!retried&&await refresh())return api(path,{method,body,headers,auth},true);
  clearTokens();window.location.href='/login';throw {status:401,data:{error:'Session expired'}};}
 let data=null;try{data=await res.json();}catch{}
 if(!res.ok)throw {status:res.status,data:data||{error:'Request failed'}};
 return data;}
export const errMsg=e=>{const d=e?.data||{};if(d.error)return d.error;const k=Object.keys(d)[0];return k?`${k}: ${[].concat(d[k]).join(' ')}`:'Something went wrong';};
