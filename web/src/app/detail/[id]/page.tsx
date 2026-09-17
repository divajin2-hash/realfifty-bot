import {redirect} from 'next/navigation';export default async function LegacyDetail({params}:{params:Promise<{id:string}>}){const {id}=await params;redirect(`/complex?id=${encodeURIComponent(id)}`);}
