import {api} from './client.js';
export const analyze=id=>api('/fraud/analyze/',{method:'POST',body:{transaction_id:id}});
