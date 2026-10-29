// Static Korean -> English glossary for category names, regions and common shopping terms.
// No paid translation APIs. Unknown terms return null (the Korean original is always kept).

export const GLOSSARY = {
    // ---------- generic shopping ----------
    '전체': 'All', '기타': 'Other', '카테고리 전체': 'All categories', '가격비교': 'Price comparison', '일반구매': 'Regular purchase',
    '무료배송': 'Free shipping', '해외직구': 'Overseas direct purchase', '중고': 'Used', '새상품': 'New', '렌탈': 'Rental', '단종': 'Discontinued',
    '판매중': 'On sale', '예약중': 'Reserved', '판매완료': 'Sold', '거래완료': 'Sold',
    // ---------- top-level shopping categories (Naver / Coupang / Danawa) ----------
    '패션의류': 'Fashion apparel', '패션잡화': 'Fashion accessories', '화장품/미용': 'Cosmetics & beauty', '디지털/가전': 'Digital & appliances',
    '가구/인테리어': 'Furniture & interior', '출산/육아': 'Maternity & baby', '식품': 'Food', '스포츠/레저': 'Sports & leisure',
    '생활/건강': 'Living & health', '여가/생활편의': 'Leisure & convenience', '면세점': 'Duty free', '도서': 'Books',
    '여성패션': 'Women\'s fashion', '남성패션': 'Men\'s fashion', '뷰티': 'Beauty', '출산/유아동': 'Maternity & kids', '주방용품': 'Kitchenware',
    '생활용품': 'Household goods', '홈인테리어': 'Home interior', '가전디지털': 'Appliances & digital',
    '자동차용품': 'Car accessories', '도서/음반/DVD': 'Books, music & DVD', '완구/취미': 'Toys & hobbies', '문구/오피스': 'Stationery & office',
    '반려동물용품': 'Pet supplies', '헬스/건강식품': 'Health & supplements', '계절가전': 'Seasonal appliances', '생활가전': 'Home appliances',
    '주방가전': 'Kitchen appliances', '가습기/공기청정기': 'Humidifiers & air purifiers', '가습기': 'Humidifier', '공기청정기': 'Air purifier',
    '에어워셔': 'Air washer', '가습기/에어워셔': 'Humidifiers & air washers', '공기청정기/계절가전': 'Air purifiers & seasonal appliances',
    '제습기': 'Dehumidifier', '전기히터': 'Electric heater', '난방기': 'Heater', '전기요/매트': 'Electric blanket & mat', '선풍기': 'Electric fan',
    '에어컨': 'Air conditioner', '청소기': 'Vacuum cleaner', '로봇청소기': 'Robot vacuum', '무선청소기': 'Cordless vacuum', '세탁기': 'Washing machine',
    '건조기': 'Dryer', '냉장고': 'Refrigerator', '김치냉장고': 'Kimchi refrigerator', '전자레인지': 'Microwave', '에어프라이어': 'Air fryer',
    '전기밥솥': 'Rice cooker', '커피머신': 'Coffee machine', '정수기': 'Water purifier', '식기세척기': 'Dishwasher', 'TV': 'TV',
    '노트북': 'Laptop', '데스크탑': 'Desktop PC', '모니터': 'Monitor', '태블릿': 'Tablet', '스마트폰': 'Smartphone', '휴대폰': 'Mobile phone',
    '이어폰': 'Earphones', '헤드폰': 'Headphones', '스피커': 'Speaker', '카메라': 'Camera', '게임기': 'Game console', '스마트워치': 'Smartwatch',
    '키보드': 'Keyboard', '마우스': 'Mouse', 'CPU': 'CPU', '그래픽카드': 'Graphics card', 'SSD': 'SSD', '메모리': 'Memory (RAM)',
    // ---------- second-hand (Daangn) ----------
    '디지털기기': 'Digital devices', '유아동': 'Kids', '유아동패션': 'Kids\' fashion', '여성의류': 'Women\'s clothing', '여성잡화': 'Women\'s accessories',
    '남성패션/잡화': 'Men\'s fashion & accessories', '뷰티/미용': 'Beauty', '취미/게임/음반': 'Hobbies, games & music',
    '티켓/교환권': 'Tickets & vouchers', '가공식품': 'Processed food', '식물': 'Plants',
    '기타 중고물품': 'Other used goods', '삽니다': 'Wanted to buy', '생활/주방': 'Living & kitchen',
    // ---------- beauty (Hwahae) ----------
    '스킨케어': 'Skincare', '스킨/토너': 'Toner', '로션/에멀젼': 'Lotion & emulsion', '에센스/앰플/세럼': 'Essence, ampoule & serum',
    '페이스오일': 'Face oil', '크림': 'Cream', '아이케어': 'Eye care', '미스트': 'Mist', '젤': 'Gel', '스킨/토너 패드': 'Toner pads',
    '밤/멀티밤': 'Balm & multi-balm', '클렌징/필링': 'Cleansing & peeling', '클렌징 폼': 'Cleansing foam', '클렌징 워터': 'Cleansing water',
    '클렌징 젤': 'Cleansing gel', '클렌징 오일': 'Cleansing oil', '클렌징 로션/크림': 'Cleansing lotion & cream', '클렌징 비누': 'Cleansing soap',
    '클렌징 티슈/패드': 'Cleansing tissues & pads', '립/아이 리무버': 'Lip & eye remover', '스크럽/필링': 'Scrub & peeling',
    '스크럽/필링 패드': 'Scrub & peeling pads', '클렌징 파우더': 'Cleansing powder', '클렌징 밤': 'Cleansing balm', '마스크/팩': 'Masks & packs',
    '시트마스크': 'Sheet mask', '부분마스크/팩': 'Spot mask & pack', '워시오프 팩': 'Wash-off pack', '필오프 팩': 'Peel-off pack',
    '슬리핑팩': 'Sleeping pack', '패치': 'Patch', '코팩': 'Nose pack', '부분마스크 패드': 'Spot mask pads', '선케어': 'Sun care',
    '선크림/로션': 'Sunscreen & sun lotion', '선스프레이': 'Sun spray', '선케어 기타': 'Sun care (other)', '선스틱': 'Sun stick',
    '선쿠션/팩트': 'Sun cushion & pact', '베이스메이크업': 'Base makeup', '메이크업베이스': 'Makeup base', '프라이머': 'Primer',
    'BB/CC크림': 'BB & CC cream', '파운데이션': 'Foundation', '쿠션': 'Cushion', '파우더/팩트': 'Powder & pact', '컨실러': 'Concealer',
    '블러셔': 'Blusher', '하이라이터': 'Highlighter', '메이크업픽서': 'Makeup fixer', '셰이딩': 'Shading', '톤업크림': 'Tone-up cream',
    '아이메이크업': 'Eye makeup', '아이섀도': 'Eyeshadow', '아이라이너': 'Eyeliner', '아이브로우': 'Eyebrow', '마스카라/픽서': 'Mascara & fixer',
    '속눈썹영양제': 'Lash serum', '립메이크업': 'Lip makeup', '립스틱': 'Lipstick', '립틴트': 'Lip tint', '립글로스': 'Lip gloss',
    '립케어/립밤': 'Lip care & balm', '컬러 립케어/립밤': 'Tinted lip balm', '바디': 'Body', '바디워시': 'Body wash', '바디로션': 'Body lotion',
    '바디크림/젤': 'Body cream & gel', '바디오일/에센스': 'Body oil & essence', '바디스크럽': 'Body scrub', '바디미스트/샤워코롱': 'Body mist & cologne',
    '핸드크림/밤': 'Hand cream & balm', '풋케어': 'Foot care', '입욕제': 'Bath products', '여성청결제': 'Feminine wash', '데오드란트': 'Deodorant',
    '바디기타': 'Body (other)', '바디케어 패드': 'Body care pads', '핸드워시': 'Hand wash', '핸드케어 기타': 'Hand care (other)', '헤어': 'Hair',
    '샴푸': 'Shampoo', '린스/컨디셔너': 'Rinse & conditioner', '헤어에센스/오일': 'Hair essence & oil', '헤어미스트': 'Hair mist',
    '스타일링': 'Styling', '헤어컬러링': 'Hair coloring', '트리트먼트/팩': 'Treatment & hair pack', '두피 스케일러': 'Scalp scaler',
    '네일': 'Nail', '네일컬러': 'Nail color', '네일케어': 'Nail care', '네일리무버': 'Nail remover', '향수': 'Perfume', '여성향수': 'Women\'s perfume',
    '남성향수': 'Men\'s perfume', '물티슈': 'Wet wipes', '이너뷰티': 'Inner beauty (supplements)', '피부 건강': 'Skin health',
    '모발/손톱 건강': 'Hair & nail health', '소화/위장 건강': 'Digestive health', '체지방 관리': 'Body fat management', '근육량 증가': 'Muscle gain',
    '항산화 관리': 'Antioxidant', '면역/피로 관리': 'Immunity & fatigue', '종합 건강': 'General health', '눈 건강': 'Eye health',
    '뼈/관절/치아 건강': 'Bone, joint & dental health', '혈행 개선': 'Blood circulation', '기타 식품': 'Other foods', '베이비&맘': 'Baby & mom',
    '임산부케어': 'Maternity care', '남성': 'Men', '메이크업': 'Makeup', '뷰티디바이스': 'Beauty devices', '스킨케어 디바이스': 'Skincare device',
    '클렌징 디바이스': 'Cleansing device', '뷰티소품': 'Beauty tools', '스킨케어 소품': 'Skincare tools', '메이크업 소품': 'Makeup tools',
    '헤어 소품': 'Hair tools', '바디 소품': 'Body tools', '기타 소품': 'Other tools',
    '건성': 'Dry skin', '지성': 'Oily skin', '중성': 'Normal skin', '복합성': 'Combination skin', '민감성': 'Sensitive skin', '여드름': 'Acne-prone skin', '아토피': 'Atopic skin',
    '10대': 'Teens', '20대': '20s', '30대': '30s', '40대 이상': '40s and over', '급상승': 'Trending',
    // ---------- places (Kakao) ----------
    '음식점': 'Restaurant', '카페': 'Cafe', '한식': 'Korean food', '중식': 'Chinese food', '일식': 'Japanese food', '양식': 'Western food',
    '분식': 'Korean snack food (bunsik)', '치킨': 'Fried chicken', '피자': 'Pizza', '패스트푸드': 'Fast food', '술집': 'Bar', '호프,요리주점': 'Pub',
    '고기,구이': 'Korean BBQ / grilled meat', '육류,고기': 'Meat', '해물,생선': 'Seafood', '국수': 'Noodles', '냉면': 'Naengmyeon (cold noodles)',
    '국밥': 'Gukbap (rice soup)', '찌개,전골': 'Stew & hot pot', '돈까스,우동': 'Tonkatsu & udon', '초밥,롤': 'Sushi & rolls', '베이커리': 'Bakery',
    '디저트카페': 'Dessert cafe', '커피전문점': 'Coffee shop', '제과,베이커리': 'Bakery', '아시아음식': 'Asian food', '뷔페': 'Buffet',
    '편의점': 'Convenience store', '대형마트': 'Supermarket', '마트': 'Mart', '약국': 'Pharmacy', '병원': 'Hospital', '은행': 'Bank',
    '관광명소': 'Tourist attraction', '문화시설': 'Cultural facility', '숙박': 'Accommodation', '주차장': 'Parking', '주유소,충전소': 'Gas & charging station',
    '지하철역': 'Subway station', '학교': 'School', '학원': 'Academy (hagwon)', '공공기관': 'Public institution', '여행': 'Travel', '쇼핑': 'Shopping',
    '가정,생활': 'Home & living', '서비스,산업': 'Services & industry', '스포츠,레저': 'Sports & leisure', '문화,예술': 'Culture & arts',
    '박물관': 'Museum', '미술관': 'Art gallery', '공원': 'Park', '궁궐': 'Palace', '시장': 'Market', '전통시장': 'Traditional market',
    '화장품': 'Cosmetics', '올리브영': 'Olive Young', '다이소': 'Daiso', '서점': 'Bookstore', '노래방': 'Karaoke (noraebang)', 'PC방': 'PC bang (internet cafe)',
    // ---------- regions ----------
    '서울': 'Seoul', '서울특별시': 'Seoul', '부산': 'Busan', '부산광역시': 'Busan', '대구': 'Daegu', '대구광역시': 'Daegu', '인천': 'Incheon',
    '인천광역시': 'Incheon', '광주': 'Gwangju', '광주광역시': 'Gwangju', '대전': 'Daejeon', '대전광역시': 'Daejeon', '울산': 'Ulsan',
    '울산광역시': 'Ulsan', '세종': 'Sejong', '세종특별자치시': 'Sejong', '경기': 'Gyeonggi', '경기도': 'Gyeonggi-do', '강원': 'Gangwon',
    '강원특별자치도': 'Gangwon', '충북': 'Chungbuk', '충청북도': 'Chungcheongbuk-do', '충남': 'Chungnam', '충청남도': 'Chungcheongnam-do',
    '전북': 'Jeonbuk', '전북특별자치도': 'Jeonbuk', '전남': 'Jeonnam', '전라남도': 'Jeollanam-do', '경북': 'Gyeongbuk', '경상북도': 'Gyeongsangbuk-do',
    '경남': 'Gyeongnam', '경상남도': 'Gyeongsangnam-do', '제주': 'Jeju', '제주특별자치도': 'Jeju',
    '강남구': 'Gangnam-gu', '강동구': 'Gangdong-gu', '강북구': 'Gangbuk-gu', '강서구': 'Gangseo-gu', '관악구': 'Gwanak-gu', '광진구': 'Gwangjin-gu',
    '구로구': 'Guro-gu', '금천구': 'Geumcheon-gu', '노원구': 'Nowon-gu', '도봉구': 'Dobong-gu', '동대문구': 'Dongdaemun-gu', '동작구': 'Dongjak-gu',
    '마포구': 'Mapo-gu', '서대문구': 'Seodaemun-gu', '서초구': 'Seocho-gu', '성동구': 'Seongdong-gu', '성북구': 'Seongbuk-gu', '송파구': 'Songpa-gu',
    '양천구': 'Yangcheon-gu', '영등포구': 'Yeongdeungpo-gu', '용산구': 'Yongsan-gu', '은평구': 'Eunpyeong-gu', '종로구': 'Jongno-gu', '중구': 'Jung-gu',
    '중랑구': 'Jungnang-gu',
};

/**
 * Translate a Korean label. Tries exact match, then splits on " > ", "/", "," and spaces.
 * Returns null when no part is known (caller keeps the Korean original).
 */
export function translate(ko) {
    if (ko === null || ko === undefined) return null;
    const s = String(ko).trim();
    if (!s) return null;
    if (GLOSSARY[s]) return GLOSSARY[s];
    for (const sep of [' > ', '>', '/', ',', ' ']) {
        if (s.includes(sep)) {
            const parts = s.split(sep).map((p) => p.trim()).filter(Boolean);
            const tr = parts.map((p) => GLOSSARY[p] ?? translate(p));
            if (tr.every((t) => t)) return tr.join(sep === ' > ' || sep === '>' ? ' > ' : sep === ' ' ? ' ' : sep === ',' ? ', ' : ' / ');
        }
    }
    return null;
}

/** Translate an address prefix: "서울 노원구 ..." -> "Seoul Nowon-gu ..." for known tokens only. */
export function translateRegionTokens(address) {
    if (!address) return null;
    const tokens = String(address).split(/\s+/);
    const tr = tokens.slice(0, 2).map((t) => GLOSSARY[t]);
    if (!tr[0]) return null;
    return tr.filter(Boolean).join(' ');
}
