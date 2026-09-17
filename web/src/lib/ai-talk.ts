import 'server-only';
import fs from 'node:fs/promises';import path from 'node:path';
import type {AreaStat} from './complex-model';
export type Talk={date:string;complex:{id:string;name:string};data_updated_at:string;selection_reason:string;snapshot:AreaStat;gap:number;personas:{id:string;name:string;perspective:string}[];opinions:{persona_id:string;judgment:string;evidence:string;change_condition:string;outlook:'bull'|'bear'|'neutral'}[]};
export async function readTalks(){const root=path.join(process.cwd(),'src/data/ai-talk');let names:string[]=[];try{names=await fs.readdir(root);}catch{return [];}const rows:Talk[]=[];for(const n of names.filter(n=>/^\d{4}-\d{2}-\d{2}\.json$/.test(n)).sort().reverse()){try{const t=JSON.parse(await fs.readFile(path.join(root,n),'utf8'));if(t.matching_version==="area-v3"&&t.opinions?.length===6&&t.personas?.length===6)rows.push(t);}catch{}}return rows;}
