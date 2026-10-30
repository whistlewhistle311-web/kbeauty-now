// Vertical 1080x1920 slideshow video (Shorts / Reels / TikTok) for one Hwahae ranking: countdown #5 -> #1.
// Usage: node ops/shorts.mjs sunscreen [outdir]. Text only, no music (add trending audio in the app).
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');

const slug = process.argv[2] || 'sunscreen';
const outDir = process.argv[3] || 'shorts';
const data = JSON.parse(fs.readFileSync(new URL('../data/latest.json', import.meta.url)));
const names = JSON.parse(fs.readFileSync(new URL('../data/shorts_names.json', import.meta.url)));
const rk = data.rankings.find((r) => r.type === 'category' && r.slug === slug);
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
slides.push(`<div class="w"><div class="k">Ranked by Korean reviewers</div><h1>Korea's top 5 ${esc(label)}, and what Koreans pay</h1>
<div class="s">From Hwahae, the review app Koreans check before buying. ${esc(day)}</div></div>`);
const KRW_PER_USD = 1337;
const price = (r) => (r.priceKrw ? `<div class="pr">In Korea: $${Math.round(r.priceKrw / KRW_PER_USD)} <small>· ₩${r.priceKrw.toLocaleString('en-US')}${r.size ? ' · ' + esc(String(r.size).split(' /')[0]) : ''}</small></div>` : '');
for (const r of rk.rows.slice(0, 5).reverse()) {
    const n = names.products[String(r.id)] || { brand: r.brandEn || r.brand, name: r.name };
    const tags = (r.topics || []).slice(0, 3).map((t) => `<span>${esc(t)}</span>`).join('');
    slides.push(`<div class="w"><div class="n">#${r.rank}</div><div class="b">${esc(n.brand)}</div><div class="p">${esc(n.name)}</div>
<div class="r">★ ${r.rating.toFixed(2)} <small>· ${r.reviews.toLocaleString('en-US')} Korean reviews</small></div>${price(r)}<div class="t">${tags}</div></div>`);
}
slides.push(`<div class="w"><div class="k">Full top 20, Korean prices, where to buy</div><h1 style="font-size:84px;letter-spacing:-1px">koreanbeautynow.com</h1>
<div class="s">Updated every morning from Hwahae. Not sponsored.</div><div class="u">Link in bio</div></div>`);

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
const dur = slides.map((_, i) => (i === 0 ? 1.8 : i === slides.length - 1 ? 3 : 2.6));  // short title: viewers decide in the first second
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
const out = `${outDir}/${slug}-${day}.mp4`;
args.push('-filter_complex', f.replace(/;$/, ''), '-map', '[v]', '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out);
execFileSync('ffmpeg', args, { stdio: 'ignore' });
fs.rmSync(tmp, { recursive: true });
console.log(out);
