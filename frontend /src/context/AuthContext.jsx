import {createContext,useContext,useReducer,useEffect,useCallback} from 'react';
import * as A from '../api/accounts.js';import {setTokens,clearTokens,tok} from '../api/client.js';
const Ctx=createContext();export const useAuth=()=>useContext(Ctx);
const red=(s,a)=>{switch(a.t){case 'user':return {...s,user:a.u,ready:true};case 'out':return {user:null,ready:true};case 'ready':return {...s,ready:true};default:return s;}};
export function AuthProvider({children}){
 const [s,d]=useReducer(red,{user:null,ready:false});
 useEffect(()=>{if(!tok()){d({t:'ready'});return;}A.profile().then(u=>d({t:'user',u})).catch(()=>d({t:'ready'}));},[]);
 const login=useCallback(async(username,password)=>{const r=await A.login({username,password});setTokens(r.access,r.refresh);d({t:'user',u:await A.profile()});},[]);
 const logout=useCallback(()=>{clearTokens();d({t:'out'});},[]);
 return <Ctx.Provider value={{...s,login,logout}}>{children}</Ctx.Provider>;}
