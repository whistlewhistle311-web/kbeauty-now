// Minimal robots.txt evaluator for "User-agent: *" (merges all * groups; longest match wins; Allow wins ties).
// Used by actors that do plain HTTP requests (Crawlee crawlers use their own respectRobotsTxtFile).

export function parseRobots(txt) {
    const rules = [];
    let applies = false;
    let lastWasUa = false;
    for (const raw of String(txt || '').split(/\r?\n/)) {
        const line = raw.replace(/#.*/, '').trim();
        if (!line) continue;
        const idx = line.indexOf(':');
        if (idx < 0) continue;
        const field = line.slice(0, idx).trim().toLowerCase();
        const value = line.slice(idx + 1).trim();
        if (field === 'user-agent') {
            if (!lastWasUa) applies = false;
            if (value === '*') applies = true;
            lastWasUa = true;
            continue;
        }
        lastWasUa = false;
        if (!applies) continue;
        if (field === 'allow' || field === 'disallow') rules.push({ allow: field === 'allow', path: value });
    }
    return rules;
}

function toRegex(path) {
    const anchored = path.endsWith('$');
    const body = (anchored ? path.slice(0, -1) : path).replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*');
    return new RegExp(`^${body}${anchored ? '$' : ''}`);
}

/** @returns {boolean} */
export function isAllowed(rules, urlOrPath) {
    let path;
    try {
        const u = new URL(urlOrPath);
        path = u.pathname + u.search;
    } catch {
        path = urlOrPath;
    }
    let best = null;
    for (const r of rules) {
        if (r.path === '') continue; // "Disallow:" (empty) allows everything
        if (toRegex(r.path).test(path)) {
            if (!best || r.path.length > best.path.length || (r.path.length === best.path.length && r.allow)) best = r;
        }
    }
    return best ? best.allow : true;
}
