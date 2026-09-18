import fs from 'node:fs/promises';
import path from 'node:path';
import { readMarket, type MarketData } from './market-data';
export interface ResearchReport {
    title: string;
    summary: string;
    takeaways: {
        title: string;
        body: string;
        evidence_ids: string[];
    }[];
    analysis: {
        title: string;
        body: string;
        evidence_ids: string[];
    }[];
    scenarios: {
        title: string;
        condition: string;
        implication: string;
    }[];
    limitations: string[];
}
interface Document {
    schema_version: number;
    date: string;
    generated_at: string;
    evidence?: Record<string, {label?:string; date?:string; previous_date?:string; comparable?:number; rises?:number; falls?:number; unchanged?:number}>;
    model: string;
    prompt_version: string;
    snapshot: MarketData;
    report: ResearchReport;
}
export async function readReport(requested?: string) {
    const dir = path.join(process.cwd(), 'src/data/reports');
    let files: string[] = [];
    try {
        files = await fs.readdir(dir);
    }
    catch { }
    const dates: string[] = [];
    for (const file of files.filter(f => /^report_\d{4}-\d{2}-\d{2}\.json$/.test(f))) {
        try {
            const entry = JSON.parse(await fs.readFile(path.join(dir, file), 'utf8'));
            if (entry.accuracy_version === "official-v1" && entry.schema_version === 2 && entry.snapshot && entry.report)
                dates.push(file.slice(7, 17));
        } catch { }
    }
    dates.sort().reverse();
    const date = requested && dates.includes(requested) ? requested : dates[0] || '';
    let document: Document | null = null;
    let legacy = '';
    if (date) {
        try {
            const value = JSON.parse(await fs.readFile(path.join(dir, `report_${date}.json`), 'utf8'));
            if (value.accuracy_version === "official-v1" && value.schema_version === 2 && value.matching_version === "area-v3" && value.snapshot && value.report)
                document = value;
        }
        catch { }
        if (!document)
            try {
                legacy = ''; // Prior matching-based narratives are held for revalidation.
            }
            catch { }
    }
    return { dates, date, document, legacy, market: document?.snapshot || await readMarket() };
}
