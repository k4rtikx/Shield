import {createContext,useContext,useReducer,useCallback} from 'react';
const Ctx=createContext();export const useToast=()=>useContext(Ctx);
let n=0;const red=(s,a)=>a.t==='add'?[...s,a.x]:s.filter(x=>x.id!==a.id);
export function ToastProvider({children}){
 const [list,d]=useReducer(red,[]);
 const push=useCallback((type,msg)=>{const id=++n;d({t:'add',x:{id,type,msg}});setTimeout(()=>d({t:'rm',id}),4000);},[]);
 const toast={success:m=>push('success',m),error:m=>push('error',m),info:m=>push('info',m),warning:m=>push('warning',m)};
 return <Ctx.Provider value={toast}>{children}<div className="toast-stack">{list.map(x=><div key={x.id} className={`toast toast-${x.type}`}>{x.msg}</div>)}</div></Ctx.Provider>;}
