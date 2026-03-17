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
        "lead_months": "3-6",
        "references": [
            {"title": "FedEx as Economic Bellwether (Investopedia)", "url": "https://www.investopedia.com/articles/markets/121515/why-fedex-considered-economic-bellwether.asp"},
            {"title": "The Conference Board Leading Economic Index", "url": "https://www.conference-board.org/topics/us-leading-indicators"},
        ],
    },
    {
        "ticker": "UPS",
        "name": "UPS",
        "sector": "운송/물류",
        "country": "US",
        "reason": "소비재·산업재 배송량으로 내수 경기 선행 파악",
        "lead_months": "3-6",
        "references": [
            {"title": "UPS Freight Index as Leading Indicator (Seeking Alpha)", "url": "https://seekingalpha.com/article/4520000-ups-economic-indicator"},
            {"title": "Cass Freight Index Report", "url": "https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes/cass-freight-index-report"},
        ],
    },
    {
        "ticker": "MAERSK-B.CO",
        "name": "A.P. Moller-Maersk",
        "sector": "운송/물류",
        "country": "DK",
        "reason": "세계 최대 해운사. 컨테이너 물동량이 글로벌 무역 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Baltic Dry Index as Leading Indicator (IMF)", "url": "https://www.imf.org/en/Publications/WP/Issues/2016/12/31/The-Baltic-Dry-Index-as-a-Predictor-of-Global-Stock-Returns-25822"},
            {"title": "Global Container Shipping & Trade (Drewry)", "url": "https://www.drewry.co.uk/container-forecaster"},
        ],
    },

    # --- 반도체 (설비투자·기술 사이클 선행) ---
    {
        "ticker": "TSM",
        "name": "TSMC",
        "sector": "반도체",
        "country": "TW",
        "reason": "파운드리 주문량이 IT·산업 전반 설비투자 사이클 선행",
        "lead_months": "6-9",
        "references": [
            {"title": "Semiconductor Cycle as Economic Indicator (Philadelphia Fed)", "url": "https://www.philadelphiafed.org/surveys-and-data/real-time-data-research"},
            {"title": "TSMC Revenue as Tech Bellwether (Bloomberg)", "url": "https://www.bloomberg.com/quote/2330:TT"},
        ],
    },
    {
        "ticker": "005930.KS",
        "name": "삼성전자",
        "sector": "반도체",
        "country": "KR",
        "reason": "메모리 반도체 가격·재고가 글로벌 IT 경기 선행",
        "lead_months": "6-9",
        "references": [
            {"title": "DRAM Price as Leading Indicator (TrendForce)", "url": "https://www.trendforce.com/presscenter/news/20230102-11484.html"},
            {"title": "한국은행 - 반도체 경기와 수출 선행성 분석", "url": "https://www.bok.or.kr/portal/bbs/P0002353/view.do?nttId=10074269&menuNo=200433"},
        ],
    },
    {
        "ticker": "ASML",
        "name": "ASML",
        "sector": "반도체",
        "country": "NL",
        "reason": "반도체 장비 주문이 칩 수요 사이클에 12~18개월 선행",
        "lead_months": "12-18",
        "references": [
            {"title": "SEMI Book-to-Bill Ratio (SEMI.org)", "url": "https://www.semi.org/en/products-services/market-data"},
            {"title": "Semiconductor Equipment Orders as CapEx Indicator (McKinsey)", "url": "https://www.mckinsey.com/industries/semiconductors/our-insights"},
        ],
    },

    # --- 산업재/건설 (실물 경기 선행) ---
    {
        "ticker": "CAT",
        "name": "Caterpillar",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "건설·광업 장비 주문이 인프라·원자재 사이클 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Caterpillar Dealer Statistics as Economic Barometer (WSJ)", "url": "https://www.wsj.com/market-data/quotes/CAT"},
            {"title": "ISM Manufacturing PMI (Institute for Supply Management)", "url": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/"},
        ],
    },
    {
        "ticker": "URI",
        "name": "United Rentals",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "장비 임대율이 건설·산업 활동 선행 지표",
        "lead_months": "3-6",
        "references": [
            {"title": "Equipment Rental as Construction Indicator (ARA)", "url": "https://www.ararentall.org/"},
            {"title": "Architecture Billings Index (AIA)", "url": "https://www.aia.org/resources/10046-the-architecture-billings-index"},
        ],
    },
    {
        "ticker": "MMM",
        "name": "3M",
        "sector": "산업재/건설",
        "country": "US",
        "reason": "산업용 소재 수요가 제조업 경기 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "3M as Industrial Bellwether (Morningstar)", "url": "https://www.morningstar.com/stocks/xnys/mmm/quote"},
            {"title": "Industrial Production Index (Federal Reserve)", "url": "https://www.federalreserve.gov/releases/g17/current/"},
        ],
    },

    # --- 화학/소재 (원자재 사이클 선행) ---
    {
        "ticker": "BASFY",
        "name": "BASF",
        "sector": "화학/소재",
        "country": "DE",
        "reason": "세계 최대 화학 기업. 화학 제품 수요가 제조업 사이클 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Chemical Activity Barometer (American Chemistry Council)", "url": "https://www.americanchemistry.com/chemistry-in-america/data-industry-statistics/resources/chemical-activity-barometer"},
            {"title": "BASF as Global Chemical Bellwether (FT)", "url": "https://www.ft.com/content/basf-chemical-bellwether"},
        ],
    },
    {
        "ticker": "DD",
        "name": "DuPont",
        "sector": "화학/소재",
        "country": "US",
        "reason": "전자·건설·자동차 소재 수요로 다수 산업 경기 선행 파악",
        "lead_months": "3-6",
        "references": [
            {"title": "Chemical Activity Barometer (ACC)", "url": "https://www.americanchemistry.com/chemistry-in-america/data-industry-statistics/resources/chemical-activity-barometer"},
            {"title": "DuPont Multi-Industry Exposure Analysis (S&P Global)", "url": "https://www.spglobal.com/marketintelligence/en/"},
        ],
    },
    {
        "ticker": "LIN",
        "name": "Linde",
        "sector": "화학/소재",
        "country": "IE",
        "reason": "산업용 가스 수요가 제조업·에너지 활동 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Industrial Gas Demand as Manufacturing Proxy (Linde IR)", "url": "https://www.linde.com/investors"},
            {"title": "Purchasing Managers' Index (IHS Markit)", "url": "https://www.pmi.spglobal.com/"},
        ],
    },

    # --- 금융 (신용 사이클 선행) ---
    {
        "ticker": "GS",
        "name": "Goldman Sachs",
        "sector": "금융",
        "country": "US",
        "reason": "IB 딜 파이프라인·트레이딩 수익이 자본시장 사이클 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Financial Conditions Index (Goldman Sachs)", "url": "https://www.goldmansachs.com/insights/pages/gs-research/global-financial-conditions-index.html"},
            {"title": "Senior Loan Officer Survey (Federal Reserve)", "url": "https://www.federalreserve.gov/data/sloos.htm"},
        ],
    },
    {
        "ticker": "V",
        "name": "Visa",
        "sector": "금융",
        "country": "US",
        "reason": "카드 결제량이 소비 지출 트렌드 실시간 선행 지표",
        "lead_months": "1-3",
        "references": [
            {"title": "Visa Spending Momentum Index", "url": "https://usa.visa.com/partner-with-us/visa-performance-solutions/spending-momentum-index.html"},
            {"title": "Consumer Spending & Credit Card Data (BEA)", "url": "https://www.bea.gov/data/consumer-spending/main"},
        ],
    },

    # --- 임시직/채용 (고용 시장 선행) ---
    {
        "ticker": "RHI",
        "name": "Robert Half",
        "sector": "채용/인력",
        "country": "US",
        "reason": "임시직 수요가 정규직 고용·실업률에 3~6개월 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Temporary Employment as Leading Indicator (BLS)", "url": "https://www.bls.gov/opub/mlr/2014/article/the-relationship-between-temporary-staffing-and-employment.htm"},
            {"title": "NBER - Temp Help as Business Cycle Indicator", "url": "https://www.nber.org/papers/w24310"},
        ],
    },
    {
        "ticker": "MAN",
        "name": "ManpowerGroup",
        "sector": "채용/인력",
        "country": "US",
        "reason": "글로벌 인력 수급 지표가 고용 시장 전환점 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "ManpowerGroup Employment Outlook Survey", "url": "https://go.manpowergroup.com/meos"},
            {"title": "OECD Composite Leading Indicators", "url": "https://www.oecd.org/en/data/indicators/composite-leading-indicator.html"},
        ],
    },

    # --- 소비재 (소비 사이클 선행) ---
    {
        "ticker": "HD",
        "name": "Home Depot",
        "sector": "소비재",
        "country": "US",
        "reason": "주택 개보수 지출이 주택 시장·소비 경기 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "NAHB Housing Market Index", "url": "https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index"},
            {"title": "Home Improvement Spending Indicator (Harvard JCHS)", "url": "https://www.jchs.harvard.edu/research-areas/remodeling/lira"},
        ],
    },
    {
        "ticker": "RACE",
        "name": "Ferrari",
        "sector": "소비재",
        "country": "IT",
        "reason": "초고가 소비재 수요가 부유층 심리·자산효과 선행 지표",
        "lead_months": "3-6",
        "references": [
            {"title": "Luxury Goods as Wealth Effect Indicator (Bain & Company)", "url": "https://www.bain.com/insights/topics/luxury/"},
            {"title": "Consumer Confidence Index (Conference Board)", "url": "https://www.conference-board.org/topics/consumer-confidence"},
        ],
    },

    # --- 원자재/에너지 ---
    {
        "ticker": "BHP",
        "name": "BHP Group",
        "sector": "원자재/에너지",
        "country": "AU",
        "reason": "철광석·구리 생산량이 중국·글로벌 산업 활동 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Commodity Prices as Leading Indicators (World Bank)", "url": "https://www.worldbank.org/en/research/commodity-markets"},
            {"title": "China PMI & Iron Ore Demand (Caixin)", "url": "https://www.pmi.spglobal.com/Public/Home/PressRelease/caixin"},
        ],
    },
    {
        "ticker": "FCX",
        "name": "Freeport-McMoRan",
        "sector": "원자재/에너지",
        "country": "US",
        "reason": "구리 가격·수요가 'Dr. Copper'로서 경기 선행",
        "lead_months": "3-6",
        "references": [
            {"title": "Dr. Copper: Copper Prices as Economic Predictor (Investopedia)", "url": "https://www.investopedia.com/terms/d/doctor-copper.asp"},
            {"title": "LME Copper Forward Curve (London Metal Exchange)", "url": "https://www.lme.com/Metals/Non-ferrous/LME-Copper"},
        ],
    },
]


def get_tickers():
    """티커 심볼 리스트 반환"""
    return [c["ticker"] for c in LEADING_COMPANIES]


def get_company_info():
    """기업 메타데이터를 ticker 기반 딕셔너리로 반환"""
    return {c["ticker"]: c for c in LEADING_COMPANIES}
