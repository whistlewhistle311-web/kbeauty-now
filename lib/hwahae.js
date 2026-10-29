// Hwahae rankings, public pages only.
// https://www.hwahae.co.kr/rankings?english_name=<type>&theme_id=<id> -> __NEXT_DATA__ holds ranks 1-20 (robots: /rankings allowed).
// Deeper ranks are loaded by the site from an internal app API; this actor deliberately does NOT call it
// (audit 2026-10-29: public pages only, until Hwahae documents that use as allowed).
// Output contains only product-level aggregates. No individual reviews or reviewer data.
import { toNumber } from './util.js';
import { translate } from './dictionary.js';
import { romanize } from './romanize.js';

/** Ranks available on the public ranking page. */
export const PUBLIC_MAX_RANK = 20;

export const DEFAULT_THEME = { category: 2, trending: null, skin: 687, age: 1714 };

export const TOPICS = {
    수분있는: 'Hydrating', 진정되는: 'Soothing', 자극없는: 'Non-irritating', 흡수잘되는: 'Absorbs well', 끈적하지않은: 'Non-sticky',
    산뜻한: 'Fresh / light', 가벼운: 'Lightweight', 촉촉한: 'Moist', 보습잘되는: 'Moisturizing', 순한: 'Gentle', 트러블안생기는: 'No breakouts',
    트러블없어지는: 'Clears breakouts', 피부결좋아지는: 'Improves texture', 속건조에효과있는: 'Fixes inner dryness', 답답하지않은: 'Breathable',
    쫀득한: 'Bouncy / chewy texture', 잘발리는: 'Spreads well', 윤기나는: 'Glowy', 유분없는: 'Oil-free feel', 밀림없는: 'No pilling',
    겉돌지않는: 'Blends in', 편안해지는: 'Comforting', 따갑지않은: 'No stinging', 뒤집어지지않는: 'No flare-ups', 모공관리되는: 'Pore care',
    피부강화되는: 'Strengthens skin barrier', 노폐물제거되는: 'Removes impurities', '2차세안에적합한': 'Good for double cleansing',
    각질제거잘되는: 'Exfoliates well', 미끌거리지않는: 'Not slippery', 미끌거리는: 'Slippery', 알갱이있는: 'Has granules', 에센스양많은: 'Lots of essence',
    백탁없는: 'No white cast', 눈시림없는: 'No eye sting', 지속력좋은: 'Long-lasting', 발색좋은: 'Good color payoff', 커버력좋은: 'Good coverage',
    향좋은: 'Nice scent', 무향인: 'Fragrance-free', 세정력좋은: 'Cleanses well', 거품풍성한: 'Rich lather', 당김없는: 'No tightness',
    밀착력좋은: 'Adheres well', 다크닝없는: 'No darkening', 뭉침없는: 'No clumping', 번짐없는: 'No smudging', 컬링되는: 'Curls lashes',
};

export function findTheme(tree, { categoryCode, segmentName }) {
    let root = tree;
    let segment = null;
    if (segmentName) {
        segment = (tree.children ?? []).find((c) => c.name === segmentName);
        if (!segment) return null;
        root = segment;
    }
    let found = null;
    const walk = (n) => {
        for (const c of n.children ?? []) {
            if (found) return;
            if (c.category_code === categoryCode && c.name !== '전체') {
                found = c;
                return;
            }
            walk(c);
        }
    };
    walk(root);
    if (!found && categoryCode === '001') found = (root.children ?? []).find((c) => c.category_code === '001');
    if (!found) return null;
    // nodes with children are not rankable themselves; use their "전체" (All) child
    const leaf = found.children?.length ? found.children.find((c) => c.name === '전체') ?? found : found;
    return { themeId: leaf.id, categoryCode, categoryKo: found.name, segmentKo: segment?.name ?? null, maxRank: tree.max_rank ?? 100 };
}

export function parseNextData(html) {
    const m = html.match(/<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/);
    if (!m) return null;
    return JSON.parse(m[1]).props?.pageProps ?? null;
}

export function mapDetail(d, i, ctx) {
    const p = d.product ?? {};
    const g = d.goods ?? null;
    const brand = d.brand?.name ?? null;
    return {
        rankingType: ctx.rankingType,
        themeId: ctx.themeId,
        categoryCode: ctx.categoryCode,
        categoryKo: ctx.categoryKo,
        categoryEn: translate(ctx.categoryKo),
        segmentKo: ctx.segmentKo,
        segmentEn: translate(ctx.segmentKo),
        rank: ctx.offset + i + 1,
        hwahaeRankDelta: d.is_rank_new ? null : toNumber(d.rank_delta),
        isNewOnHwahae: Boolean(d.is_rank_new),
        productId: p.id,
        productName: p.name ?? g?.name,
        shopOfferName: g?.name ?? null,
        brandName: brand,
        brandNameRomanized: brand && /[가-힣]/.test(brand) ? romanize(brand) : null,
        packageInfo: p.package_info ?? g?.capacity ?? null,
        listPriceKrw: toNumber(p.price),
        shopOfferPriceKrw: g ? toNumber(g.discount_price ?? g.price) : null,
        discountRatePct: toNumber(g?.discount_rate),
        reviewCount: toNumber(p.review_count),
        rating: toNumber(p.review_rating),
        topReviewTopics: (p.product_topics ?? []).map((t) => ({
            topicKo: t.review_topic?.name,
            topicEn: TOPICS[t.review_topic?.name] ?? null,
            sentenceKo: t.review_topic?.sentence,
            isPositive: t.is_positive,
            mentions: toNumber(t.review_count),
        })),
        url: g?.id ? `https://www.hwahae.co.kr/goods/${g.id}` : `https://www.hwahae.co.kr/products/${p.id}`,
        imageUrl: g?.image_url ?? p.image_url ?? null,
    };
}

/** Only www.hwahae.co.kr/rankings pages may be fetched. */
export function isPublicRankingUrl(url) {
    try {
        const u = new URL(url);
        return u.protocol === 'https:' && u.hostname === 'www.hwahae.co.kr' && (u.pathname === '/rankings' || u.pathname === '/robots.txt');
    } catch {
        return false;
    }
}

export function pageUrl(type, themeId) {
    const u = new URL('https://www.hwahae.co.kr/rankings');
    u.searchParams.set('english_name', type);
    if (themeId) u.searchParams.set('theme_id', String(themeId));
    return u.toString();
}
