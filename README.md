# 📊 경기 선행 지표 기업 대시보드

경기 사이클을 선행하는 글로벌 핵심 기업 20개의 주가·재무 데이터를 추적하는 대시보드입니다.

## 🌐 웹 대시보드

**GitHub Pages에서 바로 확인 (PC / 스마트폰 모두 지원):**

> Settings > Pages > Source를 `docs` 폴더로 설정하면 활성화됩니다.

### 대시보드 기능

- **📈 종합 현황** - KPI 카드 + 정렬 가능한 기업 테이블
- **📉 주가 차트** - 전체 기업 주가 정규화 비교
- **🏭 섹터 분석** - 섹터별 평균 성과 비교 차트
- **🔍 기업 상세** - 개별 기업 정보, 선행 근거, 주가 차트
- **💾 CSV 다운로드** - 요약/주가/기업목록 3종 다운로드

## 추적 기업 (8개 섹터, 20개 기업)

| 섹터 | 기업 | 선행 근거 |
|------|------|-----------|
| 운송/물류 | FedEx, UPS, Maersk | 물동량 → 경기 3~6개월 선행 |
| 반도체 | TSMC, 삼성전자, ASML | 설비투자·IT 사이클 선행 |
| 산업재/건설 | Caterpillar, United Rentals, 3M | 인프라·제조업 활동 선행 |
| 화학/소재 | BASF, DuPont, Linde | 원자재·제조업 사이클 선행 |
| 금융 | Goldman Sachs, Visa | 자본시장·소비 지출 선행 |
| 채용/인력 | Robert Half, ManpowerGroup | 고용 시장 3~6개월 선행 |
| 소비재 | Home Depot, Ferrari | 주택·고급 소비 심리 선행 |
| 원자재/에너지 | BHP Group, Freeport-McMoRan | Dr. Copper, 산업 활동 선행 |

## 빠른 시작

```bash
pip install -r requirements.txt

# 1. 데이터 수집
python fetch_data.py

# 2-A. 웹 대시보드 생성 (GitHub Pages용)
python build_dashboard.py
# → docs/index.html 생성, 브라우저에서 직접 열기 가능

# 2-B. 로컬 Streamlit 대시보드 (선택)
streamlit run dashboard.py
```

## 자동 업데이트

GitHub Actions가 **매 평일 한국시간 15:00** (미국 장 마감 후)에:
1. 최신 주가·재무 데이터 수집
2. 정적 HTML 대시보드 재생성
3. GitHub Pages 자동 배포

수동 실행: Actions > Daily Data Update & Deploy Dashboard > Run workflow
