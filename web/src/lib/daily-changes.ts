import fs from 'node:fs/promises';
import path from 'node:path';
export interface DailyChanges { date:string;previousDate:string;generatedAt:string;unavailable?:boolean;comparable:number;unchanged:number;appeared:number;disappeared:number;missing:number;rises:number;falls:number;rows:{id:string;name:string;area:string;label:string;before:number;after:number;percent:number}[] }
export async function readDailyChanges(stamp:string):Promise<DailyChanges|null>{
 try {const d=JSON.parse(await fs.readFile(path.join(process.cwd(),'src/data/daily_changes.json'),'utf8')) as DailyChanges;
 if(d.unavailable || !Array.isArray(d.rows) || Date.parse(d.generatedAt)!==Date.parse(stamp) || Date.now()-Date.parse(stamp)>3*86400000) return null;
 return d;}catch{return null;}
}
