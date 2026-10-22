import {api} from './client.js';
export const register=b=>api('/accounts/register/',{method:'POST',body:b,auth:false});
export const login=b=>api('/accounts/login/',{method:'POST',body:b,auth:false});
export const profile=()=>api('/accounts/profile/');
