export type Outlook='bull'|'bear'|'neutral';
export interface Opinion {id:string;complex_id:string;complex_name:string;author_name:string;content:string;vote:Outlook;created_at:string;kind:'user'|'ai'|'unknown'|'local';area?:string;areaLabel?:string;generation?:string}
export const outlookLabel={bull:'↑ 상승 전망',bear:'↓ 하락 전망',neutral:'→ 관망'};
export function parseLocal(raw:string):Opinion[]{try{const v=JSON.parse(raw);return Array.isArray(v)?v.filter((x):x is Opinion=>!!x&&typeof x.id==='string'&&typeof x.complex_id==='string'&&typeof x.content==='string'&&x.kind==='local'&&['bull','bear','neutral'].includes(x.vote)&&Number.isFinite(Date.parse(x.created_at))):[];}catch{return [];}}
export function classifyAuthor(isBot:unknown):Opinion['kind']{return isBot===true?'ai':isBot===false?'user':'unknown';}
export function opinionDistribution(comments:Opinion[]){const n={bull:0,bear:0,neutral:0};for(const c of comments)if(c.kind==='user')n[c.vote]++;return n;}
