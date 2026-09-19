const fs = require('fs');

const newsPath = 'src/data/factcheck_history.json';
let allNews = [];
if (fs.existsSync(newsPath)) {
    allNews = JSON.parse(fs.readFileSync(newsPath, 'utf8'));
}
const groupedNews = {};
allNews.forEach(item => {
    let d = item.factcheck_date || item.pub_date;
    if (!d) return;
    try {
        d = new Date(d).toISOString().substring(0, 10);
    } catch(e) {
        d = d.substring(0, 10);
    }
    if (!groupedNews[d]) groupedNews[d] = [];
    groupedNews[d].push(item);
});
console.log("allNews items:", allNews.length);
console.log("sortedDates length:", Object.keys(groupedNews).length);
console.log("first sortedDate:", Object.keys(groupedNews).sort((a,b)=>b.localeCompare(a))[0]);
