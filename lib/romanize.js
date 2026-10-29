// Revised Romanization of Korean (simplified, syllable-by-syllable, with the most common
// sound-change rule: final consonant + following ㅇ is linked). Static algorithm, no API calls.
// It is an approximation meant for search/display, not an official transliteration.

const INITIAL = ['g', 'kk', 'n', 'd', 'tt', 'r', 'm', 'b', 'pp', 's', 'ss', '', 'j', 'jj', 'ch', 'k', 't', 'p', 'h'];
const MEDIAL = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i'];
const FINAL = ['', 'k', 'k', 'k', 'n', 'n', 'n', 't', 'l', 'k', 'm', 'l', 'l', 'l', 'p', 'l', 'm', 'p', 'p', 't', 't', 'ng', 't', 't', 'k', 't', 'p', 't'];
// final consonant when the next syllable starts with ㅇ (linking): use the initial-form sound
const FINAL_LINKED = ['', 'g', 'kk', 'ks', 'n', 'nj', 'nh', 'd', 'r', 'lg', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh', 'm', 'b', 'bs', 's', 'ss', 'ng', 'j', 'ch', 'k', 't', 'p', 'h'];

function romanizeSyllables(text) {
    if (!text) return text ?? null;
    const chars = [...String(text)];
    let out = '';
    for (let i = 0; i < chars.length; i++) {
        const code = chars[i].codePointAt(0) - 0xac00;
        if (code < 0 || code > 11171) {
            out += chars[i];
            continue;
        }
        const ini = Math.floor(code / 588);
        const med = Math.floor((code % 588) / 28);
        const fin = code % 28;
        const next = chars[i + 1] ? chars[i + 1].codePointAt(0) - 0xac00 : -1;
        const nextStartsWithSilent = next >= 0 && next <= 11171 && Math.floor(next / 588) === 11;
        let syl = INITIAL[ini] + MEDIAL[med];
        if (fin) syl += nextStartsWithSilent && fin !== 21 ? FINAL_LINKED[fin] : FINAL[fin];
        // syllable-initial ㄹ at word start is "r" in RR only between vowels; at word start use "r" too (RR rule)
        out += syl;
    }
    // capitalise first letter of each word for display
    return out.replace(/(^|[\s(])([a-z])/g, (_, p, c) => p + c.toUpperCase());
}

// Loanwords, common place words and big chains. A syllable-by-syllable transliteration turns
// "카페" into "Kape" and "탐앤탐스" into "Tamaentamseu", which a foreign reader cannot use.
// Only entries of 2+ syllables, matched longest-first inside each word.
const LOAN = {
    '게스트하우스': 'Guesthouse', '투썸플레이스': 'A Twosome Place', '파리바게뜨': 'Paris Baguette', '뚜레쥬르': 'Tous les Jours',
    '세븐일레븐': '7-Eleven', '스타벅스': 'Starbucks', '탐앤탐스': 'Tom N Toms', '맥도날드': "McDonald's", '올리브영': 'Olive Young',
    '롯데리아': 'Lotteria', '롯데마트': 'Lotte Mart', '홈플러스': 'Homeplus', '빽다방': "Paik's Coffee", '폴바셋': 'Paul Bassett',
    '버거킹': 'Burger King', '이디야': 'Ediya', '할리스': 'Hollys', '컴포즈': 'Compose', '다이소': 'Daiso', '이마트': 'Emart', '무신사': 'Musinsa',
    '베이크샵': 'Bakeshop', '베이커리': 'Bakery', '레스토랑': 'Restaurant', '프로젝트': 'Project', '스튜디오': 'Studio', '비스트로': 'Bistro',
    '디저트': 'Dessert', '케이크': 'Cake', '브런치': 'Brunch', '라운지': 'Lounge', '하우스': 'House', '토스트': 'Toast', '갤러리': 'Gallery',
    '스토어': 'Store', '스퀘어': 'Square', '플라자': 'Plaza', '클리닉': 'Clinic', '호스텔': 'Hostel', '플라워': 'Flower', '파스타': 'Pasta',
    '카페': 'Cafe', '커피': 'Coffee', '키친': 'Kitchen', '호텔': 'Hotel', '모텔': 'Motel', '마트': 'Mart', '뮤직': 'Music', '와인': 'Wine',
    '피자': 'Pizza', '버거': 'Burger', '치킨': 'Chicken', '그릴': 'Grill', '마켓': 'Market', '헤어': 'Hair', '네일': 'Nail', '뷰티': 'Beauty',
    '센터': 'Center', '타워': 'Tower', '빌딩': 'Building', '파크': 'Park', '스테이': 'Stay', '메가': 'Mega', '밸리': 'Valley', '시그마': 'Sigma',
    '한라': 'Halla', '신라': 'Silla',
    // K-beauty brands (Hwahae / Olive Young)
    '조선미녀': 'Beauty of Joseon', '라로슈포제': 'La Roche-Posay', '메이크프렘': 'make p:rem', '투쿨포스쿨': 'too cool for school',
    '셀퓨전씨': 'Cell Fusion C', '더페이스샵': 'The Face Shop', '라운드랩': 'Round Lab', '이니스프리': 'Innisfree', '코스알엑스': 'COSRX',
    '마녀공장': 'Manyo Factory', '스킨1004': 'SKIN1004', '바이오더마': 'Bioderma', '에스네이처': 'S.NATURE', '웨이크메이크': 'Wakemake',
    '닥터자르트': 'Dr.Jart+', '정샘물': 'Jung Saem Mool', '하다라보': 'Hada Labo', '브링그린': 'Bring Green', '바닐라코': 'Banila Co',
    '듀이트리': 'Dewytree', '넘버즈인': 'numbuzin', '아이오페': 'IOPE', '페리페라': 'Peripera', '설화수': 'Sulwhasoo', '메디힐': 'Mediheal',
    '더랩바이블랑두': 'THE LAB by blanc doux', '라곰': 'Lagom', '루나': 'LUNA', '린제이': 'Lindsay', '시드물': 'Sidmool', '쏘내추럴': 'So Natural', '아비브': 'Abib', '아토팜': 'Atopalm', '이즈앤트리': 'Isntree', '터치인솔': 'Touch in Sol', '토니모리': 'TONYMOLY',
    '토리든': 'Torriden', '닥터지': 'Dr.G', '에뛰드': 'Etude', '에스트라': 'Aestura', '일리윤': 'Illiyoon', '비플레인': 'beplain', '웰라쥬': 'Wellage',
    '세타필': 'Cetaphil', '데이지크': 'Dasique', '에스쁘아': 'espoir', '라네즈': 'Laneige', '아이소이': 'isoi', '어뮤즈': 'AMUSE', '파티온': 'Fation',
    '아누아': 'Anua', '달바': "d'Alba", '롬앤': 'rom&nd', '클리오': 'CLIO', '헤라': 'Hera', '구달': 'Goodal', '미샤': 'Missha', '키엘': "Kiehl's",
    // appliance / PC makers (Danawa / Coupang)
    '일렉트로룩스': 'Electrolux', '한성컴퓨터': 'Hansung Computer', '대유위니아': 'Daeyu Winia', '삼성전자': 'Samsung Electronics',
    '엘지전자': 'LG Electronics', '에코백스': 'Ecovacs', '로보락': 'Roborock', '드롱기': "De'Longhi", '레노버': 'Lenovo', '에이수스': 'ASUS',
    '위니아': 'Winia', '캐리어': 'Carrier', '필립스': 'Philips', '다이슨': 'Dyson', '샤오미': 'Xiaomi', '코웨이': 'Coway',
    '위닉스': 'Winix', '쿠첸': 'Cuchen', '쿠쿠': 'Cuckoo', '신일': 'Shinil', '한일': 'Hanil', '보국': 'Bokuk', '테팔': 'Tefal', '드리미': 'Dreame',
    '애플': 'Apple', '삼성': 'Samsung', '전자': 'Electronics', '컴퓨터': 'Computer',
};
const LOAN_KEYS = Object.keys(LOAN).sort((a, b) => b.length - a.length);

function romanizeWord(word, { branch }) {
    let stem = word;
    let suffix = '';
    if (branch) {
        const m = word.match(/^(.*[가-힣A-Za-z])(\d+)호점$/);
        if (m) { stem = m[1]; suffix = ` No.${m[2]} Branch`; } else if (/[가-힣]{2,}점$/.test(word)) { stem = word.slice(0, -1); suffix = ' Branch'; }
    }
    const parts = [];
    let buf = '';
    const flush = () => { if (buf) { parts.push({ t: romanizeSyllables(buf).replace(/^[a-z]/, (c) => c.toUpperCase()), loan: false }); buf = ''; } };
    for (let i = 0; i < stem.length;) {
        const key = /[가-힣]/.test(stem[i]) ? LOAN_KEYS.find((k) => stem.startsWith(k, i)) : null;
        if (key) { flush(); parts.push({ t: LOAN[key], loan: true }); i += key.length; } else { buf += stem[i]; i += 1; }
    }
    flush();
    let out = '';
    parts.forEach((p, i) => { out += (i && (p.loan || parts[i - 1].loan) ? ' ' : '') + p.t; });
    return out + suffix;
}

/** Readable romanization for names: loanwords/chains in English, "...점" as "Branch", rest Revised Romanization. */
export function romanize(text) {
    if (!text) return text ?? null;
    const words = String(text).trim().split(/\s+/);
    return words.map((w, i) => (/[가-힣]/.test(w) ? romanizeWord(w, { branch: i > 0 }) : w)).join(' ');
}

export { romanizeSyllables };
