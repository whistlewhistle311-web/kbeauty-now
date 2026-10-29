// Render one 1000x1500 Pinterest image per ranking (top 5) from docs data, and an RSS feed for Pinterest auto-publish.
import fs from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const data = JSON.parse(fs.readFileSync('pins.json', 'utf8'));
fs.mkdirSync('docs/pins', { recursive: true });
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1000, height: 1500 } });
for (const pin of data.pins) {
    const rows = pin.items.map((it, i) => `<li><span class="n">${i + 1}</span><div><div class="b">${esc(it.brand)}</div><div class="p">${esc(it.name)}</div><div class="m">★ ${it.rating.toFixed(2)} · ${it.reviews.toLocaleString('en-US')} Korean reviews</div></div></li>`).join('');
    await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;width:1000px;height:1500px;background:#fbf4ee;font-family:"Noto Sans","Noto Sans KR",Arial,sans-serif;color:#2a2420}
.wrap{padding:80px 72px;box-sizing:border-box;height:100%;display:flex;flex-direction:column}
.k{font-size:26px;letter-spacing:4px;color:#b04a5a;font-weight:700;text-transform:uppercase}
h1{font-size:72px;line-height:1.05;margin:18px 0 10px;letter-spacing:-1px}
.s{font-size:30px;color:#6b665f;margin-bottom:40px}
ol{list-style:none;padding:0;margin:0;flex:1}
li{display:flex;gap:28px;background:#fff;border-radius:22px;padding:26px 30px;margin-bottom:22px;align-items:center}
.n{font-size:64px;font-weight:800;color:#b04a5a;width:56px}
.b{font-size:26px;color:#6b665f;text-transform:uppercase;letter-spacing:1px}.p{font-size:34px;font-weight:700;line-height:1.2}.m{font-size:24px;color:#6b665f;margin-top:4px}
.f{font-size:26px;color:#6b665f;display:flex;justify-content:space-between}
</style></head><body><div class="wrap"><div class="k">Ranked by Korean reviewers</div><h1>${esc(pin.title)}</h1><div class="s">Hwahae top 5 · ${esc(pin.date)}</div><ol>${rows}</ol>
<div class="f"><span>K-Beauty Now</span><span>Full top 20 at kbeauty-now</span></div></div></body></html>`);
    await p.screenshot({ path: `docs/pins/${pin.file}`, type: 'png' });
}
await b.close();
console.log('pins', data.pins.length);
// keep the last 14 days of pin images so the repo stays small
const cutoff = Date.now() - 14 * 864e5;
for (const f of fs.readdirSync('docs/pins')) {
    const m = f.match(/(\d{4}-\d{2}-\d{2})\.png$/);
    if (m && Date.parse(m[1]) < cutoff) fs.unlinkSync(`docs/pins/${f}`);
}
