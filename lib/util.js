// Pure helpers (no Apify imports) so they are unit-testable.

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', middot: '·', hellip: '…', lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”' };

/** Strip HTML tags (e.g. Naver's <b> highlight) and decode entities. */
export function cleanText(s) {
    if (s === null || s === undefined) return null;
    return String(s)
        .replace(/<[^>]*>/g, '')
        .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
        .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
        .replace(/&([a-z]+);/gi, (m, n) => ENTITIES[n.toLowerCase()] ?? m)
        .replace(/\s+/g, ' ')
        .trim();
}

/** Number or null. Accepts "12,300" / "12300" / 12300. */
export function toNumber(v) {
    if (v === null || v === undefined || v === '') return null;
    const n = typeof v === 'number' ? v : Number(String(v).replace(/[^0-9.-]/g, ''));
    return Number.isFinite(n) ? n : null;
}

/** "20261028" -> "2026-10-28" */
export function yyyymmddToIso(s) {
    if (!/^\d{8}$/.test(String(s || ''))) return null;
    const t = String(s);
    return `${t.slice(0, 4)}-${t.slice(4, 6)}-${t.slice(6, 8)}`;
}

/** RFC 822 date (Naver news pubDate) -> ISO 8601 UTC, or null. */
export function rfc822ToIso(s) {
    if (!s) return null;
    const d = new Date(s);
    return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

/** Today's date in Korea (UTC+9) as YYYY-MM-DD. */
export function kstDate(offsetDays = 0, now = new Date()) {
    const d = new Date(now.getTime() + 9 * 3600 * 1000 + offsetDays * 86400 * 1000);
    return d.toISOString().slice(0, 10);
}

export function chunk(arr, size) {
    const out = [];
    for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
    return out;
}

export function uniq(arr) {
    return [...new Set(arr)];
}

/** Linear-interpolated percentile of a sorted numeric array. */
export function percentile(sorted, p) {
    if (!sorted.length) return null;
    const idx = (sorted.length - 1) * p;
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    return Math.round(sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo));
}

/** Descriptive stats with IQR outlier removal (for price indexes). */
export function priceStats(values) {
    const v = values.filter((x) => Number.isFinite(x) && x > 0).sort((a, b) => a - b);
    if (!v.length) {
        return { count: 0, min: null, p10: null, p25: null, median: null, p75: null, p90: null, max: null, mean: null, trimmedMean: null, outliersRemoved: 0 };
    }
    const q1 = percentile(v, 0.25);
    const q3 = percentile(v, 0.75);
    const iqr = q3 - q1;
    const kept = v.filter((x) => x >= q1 - 1.5 * iqr && x <= q3 + 1.5 * iqr);
    const mean = (a) => Math.round(a.reduce((s, x) => s + x, 0) / a.length);
    return {
        count: v.length,
        min: v[0],
        p10: percentile(v, 0.1),
        p25: q1,
        median: percentile(v, 0.5),
        p75: q3,
        p90: percentile(v, 0.9),
        max: v[v.length - 1],
        mean: mean(v),
        trimmedMean: kept.length ? mean(kept) : null,
        outliersRemoved: v.length - kept.length,
    };
}

/**
 * Korean mobile numbers (010, 011, 016-019) may belong to individuals (personal data under PIPA).
 * Business landlines / 15xx / 070 are kept. Returns {phone, phoneMasked}.
 */
export function safeBusinessPhone(phone) {
    if (!phone) return { phone: null, phoneMasked: false };
    const digits = String(phone).replace(/\D/g, '');
    if (/^01[016789]/.test(digits)) return { phone: null, phoneMasked: true };
    return { phone: String(phone).trim(), phoneMasked: false };
}

/**
 * Find the JSON value (array or object) that follows `"key":` in a big string and parse it.
 * String-aware bracket matching, so brackets inside strings are ignored.
 */
export function extractJsonAfterKey(text, key, from = 0) {
    const marker = `"${key}":`;
    const at = text.indexOf(marker, from);
    if (at < 0) return undefined;
    let i = at + marker.length;
    while (i < text.length && /\s/.test(text[i])) i++;
    const open = text[i];
    const close = open === '[' ? ']' : open === '{' ? '}' : null;
    if (!close) return undefined;
    let depth = 0;
    let inStr = false;
    for (let j = i; j < text.length; j++) {
        const ch = text[j];
        if (inStr) {
            if (ch === '\\') j++;
            else if (ch === '"') inStr = false;
            continue;
        }
        if (ch === '"') inStr = true;
        else if (ch === '[' || ch === '{') depth++;
        else if (ch === ']' || ch === '}') {
            depth--;
            if (depth === 0) return JSON.parse(text.slice(i, j + 1));
        }
    }
    return undefined;
}
