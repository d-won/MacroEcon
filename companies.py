"""
경기 선행 지표 기업 목록 및 메타데이터

경기 사이클을 선행하는 대표 기업들을 섹터별로 정리.
이 기업들의 실적/주가는 실물 경기에 3~6개월 선행하는 경향이 있음.
"""

LEADING_COMPANIES = [
    # --- 운송/물류 (경기 선행의 대표 섹터) ---
    {
        "ticker": "FDX",
        "name": "FedEx",
        "sector": "운송/물류",
        "country": "US",
        "reason": "글로벌 물동량의 바로미터. 기업간 화물량이 경기에 3~6개월 선행",
    },
    {
        "ticker": "UPS",
        "name": "UPS",
        "sector": "운송/물류",
        "country": "US",
        "reason": "소비재·산업재 배송량으로 내수 경기 선행 파악",
    },
    {
        "ticker": "MAERSK-B.CO",
        "name": "A.P. Moller-Maersk",
        "sector": "운송/물류",
        "country": "DK",
        "reason": "세계 최대 해운사. 컨테이너 물동량이 글로벌 무역 선행",
    },

    # --- 반도체 (설비투자·기술 사이클 선행) ---
    {
        "ticker": "TSM",
        "name": "TSMC",
        "sector": "반도체",
        "country": "TW",
        "reason": "파운드리 주문량이 IT·산업 전반 설비투자 사이클 선행",
    },
    {
        "ticker": "005930.KS",
        "name": "삼성전자",
        "sector": "반도체",
        "country": "KR",
        "reason": "메모리 반도체 가격·재고가 글로벌 IT 경기 선행",
    },
    {
        "ticker": "ASML",
        "name": "ASML",
        "sector": "반도체",
        "country": "NL",
        "reason": "반도체 장비 주문이 칩 수요 사이클에 12~18개월 선행",
    },

    # --- 산업재/건설 (실물 경기 선행) ---
    {
        "ticker": "CAT",
        "name": "Caterpillar",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "건설·광업 장비 주문이 인프라·원자재 사이클 선행",
    },
    {
        "ticker": "URI",
        "name": "United Rentals",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "장비 임대율이 건설·산업 활동 선행 지표",
    },
    {
        "ticker": "MMM",
        "name": "3M",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "산업용 소재 수요가 제조업 경기 선행",
    },

    # --- 화학/소재 (원자재 사이클 선행) ---
    {
        "ticker": "BASFY",
        "name": "BASF",
        "sector": "화학/소재",
        "country": "DE",
        "reason": "세계 최대 화학 기업. 화학 제품 수요가 제조업 사이클 선행",
    },
    {
        "ticker": "DD",
        "name": "DuPont",
        "sector": "화학/소재",
        "country": "US",
        "reason": "전자·건설·자동차 소재 수요로 다수 산업 경기 선행 파악",
    },
    {
        "ticker": "LIN",
        "name": "Linde",
        "sector": "화학/소재",
        "country": "IE",
        "reason": "산업용 가스 수요가 제조업·에너지 활동 선행",
    },

    # --- 금융 (신용 사이클 선행) ---
    {
        "ticker": "GS",
        "name": "Goldman Sachs",
        "sector": "금융",
        "country": "US",
        "reason": "IB 딜 파이프라인·트레이딩 수익이 자본시장 사이클 선행",
    },
    {
        "ticker": "V",
        "name": "Visa",
        "sector": "금융",
        "country": "US",
        "reason": "카드 결제량이 소비 지출 트렌드 실시간 선행 지표",
    },

    # --- 임시직/채용 (고용 시장 선행) ---
    {
        "ticker": "RHI",
        "name": "Robert Half",
        "sector": "채용/인력",
        "country": "US",
        "reason": "임시직 수요가 정규직 고용·실업률에 3~6개월 선행",
    },
    {
        "ticker": "MAN",
        "name": "ManpowerGroup",
        "sector": "채용/인력",
        "country": "US",
        "reason": "글로벌 인력 수급 지표가 고용 시장 전환점 선행",
    },

    # --- 소비재 (소비 사이클 선행) ---
    {
        "ticker": "HD",
        "name": "Home Depot",
        "sector": "소비재",
        "country": "US",
        "reason": "주택 개보수 지출이 주택 시장·소비 경기 선행",
    },
    {
        "ticker": "RACE",
        "name": "Ferrari",
        "sector": "소비재",
        "country": "IT",
        "reason": "초고가 소비재 수요가 부유층 심리·자산효과 선행 지표",
    },

    # --- 원자재/에너지 ---
    {
        "ticker": "BHP",
        "name": "BHP Group",
        "sector": "원자재/에너지",
        "country": "AU",
        "reason": "철광석·구리 생산량이 중국·글로벌 산업 활동 선행",
    },
    {
        "ticker": "FCX",
        "name": "Freeport-McMoRan",
        "sector": "원자재/에너지",
        "country": "US",
        "reason": "구리 가격·수요가 'Dr. Copper'로서 경기 선행",
    },
]


def get_tickers():
    """티커 심볼 리스트 반환"""
    return [c["ticker"] for c in LEADING_COMPANIES]


def get_company_info():
    """기업 메타데이터를 ticker 기반 딕셔너리로 반환"""
    return {c["ticker"]: c for c in LEADING_COMPANIES}
