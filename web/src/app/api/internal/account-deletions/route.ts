import {drainDeletions,matchesSecret} from '@/lib/account-lifecycle';
export const runtime='nodejs';
export const maxDuration=60;
export async function GET(req:Request){
 const key=process.env.CRON_SECRET;
 if(!matchesSecret(req.headers.get('authorization'),key?`Bearer ${key}`:undefined))return Response.json({error:'Unauthorized'},{status:401});
 try{const result=await drainDeletions();return Response.json(result,{status:result.failed?503:200});}
 catch{return Response.json({error:'Deletion queue unavailable'},{status:503});}
}
