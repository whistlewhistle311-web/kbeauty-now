// Fetch public Hwahae ranking pages (top 20) and save a compact snapshot for the site.
// Uses the same polite client, robots check and public-page-only guard as the Apify actor.
import fs from 'node:fs';
import path from 'node:path';
import { PoliteClient } from './lib/http.js';
import { parseRobots, isAllowed } from './lib/robots.js';
import { romanize, romanizeSyllables } from './lib/romanize.js';
import { DEFAULT_THEME, findTheme, parseNextData, mapDetail, pageUrl, isPublicRankingUrl } from './lib/hwahae.js';

const CATS = [
    ['001', 'all'], ['001:001', 'skincare'], ['001:001:001', 'toner'], ['001:001:003', 'serum'], ['001:001:005', 'cream'],
    ['001:002', 'cleansing'], ['001:003', 'masks'], ['001:004:001', 'sunscreen'], ['001:005:005', 'cushion'], ['001:007', 'lip'],
];
const SKINS = [['건성', 'dry'], ['지성', 'oily'], ['복합성', 'combination'], ['민감성', 'sensitive'], ['여드름', 'acne-prone']];

const client = new PoliteClient({ minIntervalMs: 3000, maxRetries: 3, headers: { 'Accept-Language': 'ko-KR,ko;q=0.9' } });
const robots = parseRobots(await client.request('https://www.hwahae.co.kr/robots.txt', { responseType: 'text' }).catch(() => ''));
const get = async (url) => {
    if (!isPublicRankingUrl(url) || !isAllowed(robots, url)) throw new Error(`not allowed: ${url}`);
    return parseNextData(await client.request(url, { responseType: 'text' }));
};

const out = { fetchedAt: new Date().toISOString(), rankings: [] };
for (const [type, list] of [['category', CATS.map(([c, s]) => ({ code: c, slug: s, seg: null }))],
    ['skin', SKINS.map(([k, s]) => ({ code: '001:001', slug: s, seg: k }))]]) {
    const root = await get(pageUrl(type, DEFAULT_THEME[type]));
    const tree = root.rankingsCategories;
    out.updatedAt = tree.last_updated_at;
    for (const t of list) {
        const th = findTheme(tree, { categoryCode: t.code, segmentName: t.seg });
        if (!th) { console.warn('missing', type, t.slug); continue; }
        const p = await get(pageUrl(type, th.themeId));
        const rows = (p?.rankingProducts?.data?.details ?? []).slice(0, 20)
            .map((d, i) => mapDetail(d, i, { rankingType: type, ...th, offset: 0 }))
            .map((r) => ({
                rank: r.rank, delta: r.hwahaeRankDelta, isNew: r.isNewOnHwahae, id: r.productId, name: r.productName,
                brand: r.brandName, brandEn: r.brandNameRomanized,
                brandOfficial: Boolean(r.brandName && /[가-힣]/.test(r.brandName) && romanize(r.brandName) !== romanizeSyllables(r.brandName)) || Boolean(r.brandName && !/[가-힣]/.test(r.brandName)), size: r.packageInfo, priceKrw: r.listPriceKrw,
                rating: r.rating, reviews: r.reviewCount, url: r.url,
                topics: r.topReviewTopics.filter((x) => x.isPositive && x.topicEn).slice(0, 3).map((x) => x.topicEn),
            }));
        out.rankings.push({ type, slug: t.slug, categoryKo: th.categoryKo, segmentKo: th.segmentKo, rows });
        console.log(type, t.slug, rows.length);
    }
}
const dir = path.join(path.dirname(new URL(import.meta.url).pathname), 'data');
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, 'latest.json'), JSON.stringify(out, null, 1));
fs.writeFileSync(path.join(dir, `${out.fetchedAt.slice(0, 10)}.json`), JSON.stringify(out));
console.log('saved', out.rankings.length, 'rankings');
