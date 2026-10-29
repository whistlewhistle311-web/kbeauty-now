// Render one 1000x1500 Pinterest image per ranking (top 5) from docs data, and an RSS feed for Pinterest auto-publish.
import fs from 'node:fs';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
const data = JSON.parse(fs.readFileSync('pins.json', 'utf8'));
fs.mkdirSync('docs/pins', { recursive: true });
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1000, height: 1500 } });
const GUIDE_CSS = `body{margin:0;width:1000px;height:1500px;background:#fbf4ee;font-family:"Noto Sans","Noto Sans KR",Arial,sans-serif;color:#2a2420}
.wrap{padding:80px 72px;box-sizing:border-box;height:100%;display:flex;flex-direction:column}
.k{font-size:26px;letter-spacing:4px;color:#b04a5a;font-weight:700;text-transform:uppercase}
h1{font-size:84px;line-height:1.03;margin:18px 0 44px;letter-spacing:-1.5px}
ul{list-style:none;padding:0;margin:0;flex:1}li{background:#fff;border-radius:22px;padding:30px 34px;margin-bottom:22px;font-size:38px;font-weight:650;line-height:1.25;word-break:keep-all}
.pick{background:#b04a5a;color:#fff;border-radius:22px;padding:28px 34px;font-size:30px;margin-bottom:40px}.pick b{display:block;font-size:38px;margin-top:6px}
.f{font-size:26px;color:#6b665f;display:flex;justify-content:space-between}`;
const PROD_CSS = `body{margin:0;width:1000px;height:1500px;background:#fbf4ee;font-family:"Noto Sans","Noto Sans KR",Arial,sans-serif;color:#2a2420}
.wrap{padding:90px 72px;box-sizing:border-box;height:100%;display:flex;flex-direction:column}
.k{display:inline-block;align-self:flex-start;background:#b04a5a;color:#fff;font-size:30px;font-weight:800;letter-spacing:2px;text-transform:uppercase;border-radius:14px;padding:14px 24px}
.b{font-size:34px;color:#6b665f;text-transform:uppercase;letter-spacing:2px;margin-top:70px}
h1{font-size:86px;line-height:1.04;margin:14px 0 22px;letter-spacing:-1.5px}
.ko{font-size:30px;color:#8a837b;word-break:keep-all}
.score{margin-top:60px;background:#fff;border-radius:26px;padding:40px 44px}
.score .r{font-size:96px;font-weight:800;color:#b04a5a;line-height:1}.score .r small{font-size:40px;color:#6b665f;font-weight:600}
.score .v{font-size:32px;color:#6b665f;margin-top:10px}
.tags{margin-top:36px;display:flex;flex-wrap:wrap;gap:14px}.tags span{background:#f1e4da;border-radius:99px;padding:14px 26px;font-size:32px;font-weight:650}
.also{margin-top:56px;font-size:28px;color:#6b665f;text-transform:uppercase;letter-spacing:2px;font-weight:700}
.o{display:flex;gap:20px;align-items:center;border-bottom:2px solid #eadfd5;padding:20px 0;font-size:34px;font-weight:650}.o b{color:#b04a5a;width:56px}
.sp{flex:1}.f{font-size:26px;color:#6b665f;display:flex;justify-content:space-between}`;
for (const pin of data.pins) {
  if (pin.product) {
    const q = pin.product;
    const tags = q.tags.map((t) => `<span>${esc(t)}</span>`).join('');
    await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${PROD_CSS}</style></head><body><div class="wrap"><div class="k">${esc(q.kicker)}</div>
<div class="b">${esc(q.brand)}</div><h1 style="font-size:${q.name.length > 34 ? 68 : 86}px">${esc(q.name)}</h1><div class="ko">${esc(q.ko)}</div>
<div class="score"><div class="r">★ ${q.rating.toFixed(2)} <small>/ 5</small></div><div class="v">${q.reviews.toLocaleString('en-US')} Korean reviews on Hwahae${q.price ? ' · ' + esc(q.price) + ' in Korea' : ''}</div></div>
<div class="tags">${tags}</div>
<div class="also">Also top ${esc(q.noun)}s in Korea</div>${q.others.slice(0, 3).map((o) => `<div class="o"><b>#${o.rank}</b><span>${esc(o.name)}</span></div>`).join('')}<div class="sp"></div><div class="f"><span>K-Beauty Now</span><span><b>koreanbeautynow.com</b></span></div></div></body></html>`);
    await p.screenshot({ path: `docs/pins/${pin.file}`, type: 'jpeg', quality: 82 });
    continue;
  }
  if (pin.tips) {
    const li = pin.tips.map((t) => `<li>${esc(t)}</li>`).join('');
    await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${GUIDE_CSS}</style></head><body><div class="wrap"><div class="k">K-beauty guide</div><h1>${esc(pin.title)}</h1><ul>${li}</ul>
<div class="pick">${esc(pin.pickLabel)}<b>${esc(pin.pick)}</b></div><div class="f"><span>K-Beauty Now</span><span><b>koreanbeautynow.com</b></span></div></div></body></html>`);
    await p.screenshot({ path: `docs/pins/${pin.file}`, type: 'jpeg', quality: 82 });
    continue;
  }
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
.cta{background:#b04a5a;color:#fff;border-radius:22px;padding:28px 34px;font-size:32px;font-weight:700;margin:8px 0 34px}
</style></head><body><div class="wrap"><div class="k">Ranked by Korean reviewers</div><h1 style="font-size:${pin.title.length > 40 ? 60 : 72}px">${esc(pin.title)}</h1><div class="s">${esc(pin.sub || "Hwahae top 5")} · ${esc(pin.date)}</div><ol>${rows}</ol>
<div class="cta">Full top 20, Korean prices and where to buy →</div><div class="f"><span>K-Beauty Now</span><span><b>koreanbeautynow.com</b></span></div></div></body></html>`);
    await p.screenshot({ path: `docs/pins/${pin.file}`, type: 'jpeg', quality: 82 });
}
await b.close();
console.log('pins', data.pins.length);
// keep the last 14 days of pin images so the repo stays small
const cutoff = Date.now() - 14 * 864e5;
for (const f of fs.readdirSync('docs/pins')) {
    const m = f.match(/(\d{4}-\d{2}-\d{2})\.(png|jpg)$/); // guide pins (YYYY-MM) are kept
    const w = f.match(/-(\d{4})-W(\d{2})\.jpg$/); if (w && Date.now() - Date.parse(`${w[1]}-01-01`) - (+w[2]) * 7 * 864e5 > 28 * 864e5) fs.unlinkSync(`docs/pins/${f}`);
    if (m && Date.parse(m[1]) < cutoff) fs.unlinkSync(`docs/pins/${f}`);
}
