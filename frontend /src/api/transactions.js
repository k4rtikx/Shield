import {api} from './client.js';
export const transfer=(b,key)=>api('/transactions/transfer/',{method:'POST',body:b,headers:{'Idempotency-Key':key}});
export const history=()=>api('/transactions/history/');
