import fs from 'node:fs/promises';
import path from 'node:path';
import {readUniverse} from './complex-data';
import {areaKey,change,daysSince} from './complex-model';
import type {MacroPoint} from './market-data';
export interface AskPoint {date:string;market_recovery_index:number;sample_count:number}
export async function readMarketExtras(){const d=await readUniverse();let asks:AskPoint[]=[],history:MacroPoint[]=[];
 try{asks=JSON.parse(await fs.readFile(path.join(process.cwd(),'src/data/macro_index.json'),'utf8'));}catch{}
 try{history=JSON.parse(await fs.readFile(path.join(process.cwd(),'src/data/macro_tx_index.json'),'utf8'));}catch{}
 const rows=d.groups.flatMap(g=>g.stats.map(s=>({id:g.complex.id,name:g.complex.name,address:g.complex.address,area:areaKey(s),areaLabel:`${s.pyeong_name||''} · 전용 ${s.exclusive_area||s.match_key_area}㎡`,trade:s.recent_deal_absolute?.price||null,tradeDate:s.recent_deal_absolute?.date||null,ask:s.current_lowest_ask||null,peak:s.highest_deal_price||null,age:daysSince(s.recent_deal_absolute?.date,d.updatedAt),gap:change(s.current_lowest_ask,s.recent_deal_absolute?.price),drop:change(s.recent_deal_absolute?.price,s.highest_deal_price),askDrop:change(s.current_lowest_ask,s.highest_deal_price)})));
 return {rows,asks:asks.filter(p=>Number.isFinite(p.market_recovery_index)).sort((a,b)=>a.date.localeCompare(b.date)),history:history.sort((a,b)=>a.month.localeCompare(b.month))};}
