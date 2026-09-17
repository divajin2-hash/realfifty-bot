import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import type { Article, AuditJob, AuditResult } from './factcheck-model';
export const auditRoot = () => path.join(process.cwd(), 'src/data/factcheck');
export async function readArticles(): Promise<Article[]> { try {
    const rows = JSON.parse(await fs.readFile(path.join(process.cwd(), 'src/data/latest_news.json'), 'utf8')) as Omit<Article, 'id'>[];
    return [...new Map(rows.filter(a => /^https?:\/\//.test(a.link)).map(a => [a.link, { ...a, id: createHash('sha256').update(a.link).digest('hex').slice(0, 20) }])).values()];
}
catch {
    return [];
} }
export async function readAudits() { const jobs: AuditJob[] = []; const results: AuditResult[] = []; for (const [dir, list] of [['queue', jobs], ['results', results]] as const) {
    try {
        for (const file of await fs.readdir(path.join(auditRoot(), dir))) {
            if (!/^[a-f0-9]{32}\.json$/.test(file))
                continue;
            try {
                list.push(JSON.parse(await fs.readFile(path.join(auditRoot(), dir, file), 'utf8')));
            }
            catch { }
        }
    }
    catch { }
} return { jobs: jobs.sort((a, b) => b.created_at.localeCompare(a.created_at)), results: results.sort((a, b) => b.collected_at.localeCompare(a.collected_at)) }; }
