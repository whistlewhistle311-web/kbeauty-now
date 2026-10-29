// Polite HTTP helper shared by all actors (copied into each actor's src/lib/ so every
// actor folder stays self-contained for `apify push`).
// - global min interval between requests (rate limit)
// - retries with exponential backoff + jitter on network errors, 429 and 5xx
// - honours Retry-After
const log = { info: (...a) => console.log(...a), warning: (...a) => console.warn(...a), debug: () => {} };

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export class PoliteClient {
    /**
     * @param {object} opts
     * @param {number} [opts.minIntervalMs=1000] minimum gap between two requests (all hosts)
     * @param {number} [opts.maxRetries=4]
     * @param {number} [opts.baseBackoffMs=2000]
     * @param {number} [opts.timeoutMs=30000]
     * @param {Record<string,string>} [opts.headers]
     * @param {typeof fetch} [opts.fetchImpl] injectable for tests
     */
    constructor(opts = {}) {
        this.minIntervalMs = opts.minIntervalMs ?? 1000;
        this.maxRetries = opts.maxRetries ?? 4;
        this.baseBackoffMs = opts.baseBackoffMs ?? 2000;
        this.timeoutMs = opts.timeoutMs ?? 30000;
        this.headers = opts.headers ?? {};
        this.fetchImpl = opts.fetchImpl ?? globalThis.fetch;
        this.last = 0;
        this.queue = Promise.resolve();
        this.requestCount = 0;
    }

    async #throttle() {
        // serialize the waiting so concurrent callers still respect the interval
        const p = this.queue.then(async () => {
            const wait = this.last + this.minIntervalMs - Date.now();
            if (wait > 0) await sleep(wait);
            this.last = Date.now();
        });
        this.queue = p.catch(() => {});
        return p;
    }

    /**
     * @param {string} url
     * @param {RequestInit & {json?: unknown, responseType?: 'json'|'text'}} [init]
     */
    async request(url, init = {}) {
        const { json, responseType = 'json', ...rest } = init;
        const headers = { ...this.headers, ...(rest.headers || {}) };
        let body = rest.body;
        if (json !== undefined) {
            body = JSON.stringify(json);
            headers['Content-Type'] = 'application/json';
        }
        let attempt = 0;
        for (;;) {
            await this.#throttle();
            this.requestCount++;
            const ctrl = new AbortController();
            const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
            let res;
            let err;
            try {
                res = await this.fetchImpl(url, { ...rest, headers, body, signal: ctrl.signal });
            } catch (e) {
                err = e;
            } finally {
                clearTimeout(timer);
            }
            const retryable = err || res.status === 429 || res.status >= 500;
            if (!retryable) {
                if (!res.ok) {
                    const text = await res.text().catch(() => '');
                    const e = new Error(`HTTP ${res.status} for ${redact(url)}: ${text.slice(0, 300)}`);
                    e.status = res.status;
                    e.body = text;
                    throw e;
                }
                return responseType === 'text' ? res.text() : res.json();
            }
            if (attempt >= this.maxRetries) {
                if (err) throw err;
                const e = new Error(`HTTP ${res.status} for ${redact(url)} after ${attempt + 1} attempts`);
                e.status = res.status;
                throw e;
            }
            const retryAfter = res && Number(res.headers.get('retry-after'));
            const backoff = Number.isFinite(retryAfter) && retryAfter > 0
                ? retryAfter * 1000
                : this.baseBackoffMs * 2 ** attempt + Math.floor(Math.random() * 500);
            log.warning(`Request failed (${err ? err.message : res.status}), retry ${attempt + 1}/${this.maxRetries} in ${backoff} ms`);
            await sleep(backoff);
            attempt++;
        }
    }
}

/** Remove credentials from URLs before logging. */
export function redact(url) {
    return String(url).replace(/(crtfc_key|serviceKey|key|client_secret)=[^&]+/gi, '$1=***');
}
