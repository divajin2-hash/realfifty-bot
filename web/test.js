const fs = require('fs');

const allNews = JSON.parse(fs.readFileSync('src/data/factcheck_history.json', 'utf8'));
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
console.log(Object.keys(groupedNews));
