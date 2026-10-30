// Vertical 1080x1920 slideshow video (Shorts / Reels / TikTok) for one Hwahae ranking: countdown #5 -> #1.
// Usage: node ops/shorts.mjs sunscreen [outdir]. Text only, no music (add trending audio in the app).
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const slug = process.argv[2] || 'sunscreen';
const outDir = process.argv[3] || 'shorts';
// A/B test: 'a' = countdown title, 'b' = price hook ("Korea's #1 toner costs $13"). Default: b for the KST-morning post, a for the night post
const style = process.argv[4] || (new Date(Date.now() + 9 * 3600e3).getUTCHours() < 12 ? 'b' : 'a');
const data = JSON.parse(fs.readFileSync(new URL('../data/latest.json', import.meta.url)));
const names = JSON.parse(fs.readFileSync(new URL('../data/shorts_names.json', import.meta.url)));
// slug 'routine': a full 5-step routine built from each step's #1 (cleanser, toner, serum, moisturizer, sunscreen)
const STEPS = [['cleansing', 'Cleanser'], ['toner', 'Toner'], ['serum', 'Serum'], ['cream', 'Moisturizer'], ['sunscreen', 'Sunscreen']];
// slug 'hype': US favourites vs Korea's #1 today (ops/us_favorites.json), with the US pick's Hwahae rank
const US = slug === 'hype' ? JSON.parse(fs.readFileSync(new URL('./us_favorites.json', import.meta.url))) : [];
const nm = (r) => { const n = names.products[String(r.id)] || { brand: r.brandEn || r.brand, name: r.name }; return `${n.brand} ${n.name}`; };
const hype = US.map((u) => {
    const rows = data.rankings.find((r) => r.type === 'category' && r.slug === u.cat).rows;
    const hit = rows.find((r) => new RegExp(u.rx, 'i').test(nm(r)));
    return { ...u, top: rows[0], usRank: hit ? hit.rank : null };
});
// slug 'concern': skin problem -> the best-ranked product Korean reviewers most praise for it
const CONC = [['Fixes inner dryness', 'Tight, dehydrated skin?'], ['Soothing', 'Redness and irritation?'], ['Clears breakouts', 'Breakouts?'],
    ['Pore care', 'Big pores?'], ['Non-sticky', 'Hate a sticky finish?'], ['Non-irritating', 'Sensitive skin?']];
const conc = [];
if (slug === 'concern') {
    const pool = data.rankings.filter((r) => r.type === 'category' && !['all', 'skincare', 'cushion', 'lip'].includes(r.slug)).flatMap((r) => r.rows.map((x) => ({ ...x, cat: r.slug })));
    const used = new Set();
    for (const [topic, q] of CONC) {
        const c = pool.filter((x) => (x.topics || []).includes(topic) && !used.has(x.id)).sort((a, b) => a.topics.indexOf(topic) - b.topics.indexOf(topic) || a.rank - b.rank)[0];
        if (c) { used.add(c.id); conc.push({ q, topic, r: c }); }
    }
}
const rk = slug === 'concern' ? { rows: conc.map((c) => c.r) } : slug === 'hype' ? { rows: hype.map((h) => h.top) } : slug === 'routine'
    ? { rows: STEPS.map(([s, step], i) => ({ ...data.rankings.find((r) => r.type === 'category' && r.slug === s).rows[0], step, stepNo: i + 1 })) }
    : data.rankings.find((r) => r.type === 'category' && r.slug === slug);
if (!rk) throw new Error('no ranking ' + slug);
const label = names.labels[slug] || slug;
const day = data.updatedAt.slice(0, 10);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const CSS = `body{margin:0;width:1080px;height:1920px;background:#fbf4ee;font-family:"Noto Sans","Noto Sans CJK KR",Arial,sans-serif;color:#2a2420}
.w{box-sizing:border-box;height:100%;padding:170px 90px 260px;display:flex;flex-direction:column;justify-content:center}
.k{font-size:40px;letter-spacing:5px;color:#b04a5a;font-weight:800;text-transform:uppercase}
h1{font-size:120px;line-height:1.02;margin:30px 0;letter-spacing:-2px}
.s{font-size:46px;color:#6b665f;line-height:1.3}
.n{font-size:300px;font-weight:900;color:#b04a5a;line-height:.9}
.b{font-size:50px;color:#6b665f;text-transform:uppercase;letter-spacing:3px;margin-top:40px}
.p{font-size:96px;font-weight:800;line-height:1.05;margin:14px 0 40px;letter-spacing:-1.5px}
.r{font-size:56px;font-weight:700}.r small{color:#6b665f;font-weight:500;font-size:44px}
.t{margin-top:40px;display:flex;flex-wrap:wrap;gap:18px}.t span{background:#f1e4da;border-radius:99px;padding:18px 34px;font-size:44px;font-weight:650}
.pr{margin-top:34px;font-size:58px;font-weight:800;color:#2a2420}.pr small{font-size:42px;color:#6b665f;font-weight:500}
.u{margin-top:60px;background:#b04a5a;color:#fff;border-radius:30px;padding:44px 50px;font-size:60px;font-weight:800}`;
const slides = [];
const KRW_PER_USD = 1337;
const price = (r) => (r.priceKrw ? `<div class="pr">In Korea: $${Math.round(r.priceKrw / KRW_PER_USD)} <small>· ₩${r.priceKrw.toLocaleString('en-US')}${r.size ? ' · ' + esc((String(r.size).match(/\d+(?:\.\d+)?\s*(?:ml|g)\b/i) || [String(r.size).split(' /')[0]])[0]) : ''}</small></div>` : '');
const SING = { toner: 'toner', serum: 'serum', cream: 'moisturizer', cleansing: 'cleanser', masks: 'face mask', sunscreen: 'sunscreen', cushion: 'cushion', lip: 'lip product', all: 'K-beauty product', skincare: 'skincare product' };
const top1 = rk.rows[0];
const total = rk.rows.slice(0, 5).reduce((a, r) => a + (r.priceKrw || 0), 0);
if (slug === 'concern') {
    slides.push(`<div class="w"><div class="k">Ranked by Korean reviewers</div><h1>Your skin problem → what Koreans actually use</h1>
<div class="s">The top-ranked pick Korean reviewers praise most for each, from Hwahae. ${esc(day)}</div></div>`);
    for (const c of conc) {
        const n = names.products[String(c.r.id)] || { brand: c.r.brandEn || c.r.brand, name: c.r.name };
        slides.push(`<div class="w"><h1 style="font-size:110px;margin:0 0 50px">${esc(c.q)}</h1><div class="b">Koreans reach for</div>
<div class="p">${esc(n.brand)} ${esc(n.name.split(' SPF')[0])}</div><div class="r">#${c.r.rank} ${esc(SING[c.r.cat] || c.r.cat)} in Korea · ★ ${c.r.rating.toFixed(2)}</div>
${price(c.r)}<div class="t"><span>Reviewers say: ${esc(c.topic.toLowerCase())}</span></div></div>`);
    }
} else if (slug === 'hype') {
    slides.push(`<div class="w"><div class="k">K-beauty, honestly</div><h1>What America buys vs what's #1 in Korea</h1>
<div class="s">US favorites against today's Hwahae rankings, from Korean reviewers. ${esc(day)}</div></div>`);
    for (const h of hype) {
        const t = h.top, n = names.products[String(t.id)] || { brand: t.brandEn || t.brand, name: t.name };
        slides.push(`<div class="w"><div class="k">${esc(SING[h.cat] || h.cat)}s</div>
<div class="b" style="margin-top:30px">The US favorite</div><div class="p" style="font-size:72px">${esc(h.us)}</div>
<div class="r" style="color:#b04a5a">${h.usRank ? `#${h.usRank} in Korea right now` : "Not in Korea's top 20 right now"}</div>
<div class="b" style="margin-top:70px">Korea's #1 ${esc(SING[h.cat] || h.cat)}</div><div class="p">${esc(n.brand)} ${esc(n.name.split(' SPF')[0])}</div>
<div class="r">★ ${t.rating.toFixed(2)} <small>· ${t.reviews.toLocaleString('en-US')} Korean reviews</small></div>${price(t)}</div>`);
    }
} else if (slug === 'routine') {
    slides.push(`<div class="w"><div class="k">Only Korea's #1s</div><h1>A full Korean skincare routine costs $${Math.round(total / 1337)} in Seoul</h1>
<div class="s">The #1 product for every step, ranked by Korean reviewers on Hwahae. ${esc(day)}</div></div>`);
} else if (style === 'b' && top1.priceKrw) {
    slides.push(`<div class="w"><div class="k">What Koreans actually pay</div><h1>Korea's #1 ${esc(SING[slug] || label)} costs $${Math.round(top1.priceKrw / 1337)} in Seoul</h1>
<div class="s">Top 5 by Korean reviewers on Hwahae, with Seoul prices. ${esc(day)}</div></div>`);
} else {
    slides.push(`<div class="w"><div class="k">Ranked by Korean reviewers</div><h1>Korea's top 5 ${esc(label)}, and what Koreans pay</h1>
<div class="s">From Hwahae, the review app Koreans check before buying. ${esc(day)}</div></div>`);
}
for (const r of (['hype', 'concern'].includes(slug) ? [] : slug === 'routine' ? rk.rows : rk.rows.slice(0, 5).reverse())) {
    const n = names.products[String(r.id)] || { brand: r.brandEn || r.brand, name: r.name };
    const tags = (r.topics || []).slice(0, 3).map((t) => `<span>${esc(t)}</span>`).join('');
    slides.push(`<div class="w">${r.step ? `<div class="k" style="font-size:52px">Step ${r.stepNo} · ${esc(r.step)}</div><div class="n" style="font-size:150px;margin-top:20px">#1</div>` : `<div class="n">#${r.rank}</div>`}<div class="b">${esc(n.brand)}</div><div class="p">${esc(n.name)}</div>
<div class="r">★ ${r.rating.toFixed(2)} <small>· ${r.reviews.toLocaleString('en-US')} Korean reviews</small></div>${price(r)}<div class="t">${tags}</div></div>`);
}
slides.push(`<div class="w"><div class="k">Full top 20, Korean prices, where to buy</div><h1 style="font-size:84px;letter-spacing:-1px">koreanbeautynow.com</h1>
<div class="s">Checked daily against Hwahae. Not sponsored.</div><div class="u">Link in bio</div></div>`);

fs.mkdirSync(outDir, { recursive: true });
const tmp = fs.mkdtempSync(outDir + '/tmp-');
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
for (let i = 0; i < slides.length; i++) {
    await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>${slides[i]}</body></html>`);
    await p.screenshot({ path: `${tmp}/s${i}.png` });
}
await b.close();
// 2.6s per slide (title 1.8s, end 3s), 0.4s slides
const dur = slides.map((_, i) => (i === 0 ? 1.8 : i === slides.length - 1 ? 3 : slug === 'concern' ? 2.0 : 2.6));  // short title: viewers decide in the first second
const args = ['-y'];
slides.forEach((_, i) => args.push('-i', `${tmp}/s${i}.png`));  // one frame each; zoompan makes the motion frames
// slow push-in on every slide (keeps the frame moving, which helps Reels retention)
let f = '';
slides.forEach((_, i) => {
    const n = Math.round(dur[i] * 30);
    f += `[${i}:v]scale=1188:2112,zoompan=z='1+0.05*on/${n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${n}:s=1080x1920:fps=30,setsar=1[z${i}];`;
});
let last = '[z0]', off = 0;
for (let i = 1; i < slides.length; i++) {
    off += dur[i - 1] - 0.4;
    const o = i === slides.length - 1 ? '[v]' : `[x${i}]`;
    f += `${last}[z${i}]xfade=transition=slideleft:duration=0.4:offset=${off.toFixed(2)}${o};`;
    last = o;
}
const out = `${outDir}/${slug}-${day}${style === 'b' && !['routine', 'hype', 'concern'].includes(slug) ? '-b' : ''}.mp4`;
args.push('-filter_complex', f.replace(/;$/, ''), '-map', '[v]', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out);
execFileSync('ffmpeg', args, { stdio: 'ignore' });
fs.rmSync(tmp, { recursive: true });
console.log(out);
