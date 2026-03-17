# 📊 경기 선행 지표 기업 대시보드

경기 사이클을 선행하는 글로벌 핵심 기업 20개의 주가·재무 데이터를 추적하는 대시보드입니다.

## 추적 기업 (섹터별)

| 섹터 | 기업 |
|------|------|
| 운송/물류 | FedEx, UPS, Maersk |
| 반도체 | TSMC, 삼성전자, ASML |
| 산업재/건설 | Caterpillar, United Rentals, 3M |
| 화학/소재 | BASF, DuPont, Linde |
| 금융 | Goldman Sachs, Visa |
| 채용/인력 | Robert Half, ManpowerGroup |
| 소비재 | Home Depot, Ferrari |
| 원자재/에너지 | BHP Group, Freeport-McMoRan |

## 빠른 시작

```bash
pip install -r requirements.txt

# 데이터 수집
python fetch_data.py

# 대시보드 실행
streamlit run dashboard.py
```

## 기능

- **종합 현황**: 전체 기업의 1일/1주/1개월/3개월 변동률 한눈에 확인
- **주가 차트**: 정규화 주가 비교 및 개별 캔들차트
- **섹터 분석**: 섹터별 평균 성과 비교
- **기업 상세**: 개별 기업 정보 및 선행 지표 근거
- **CSV 다운로드**: 요약 데이터, 주가 히스토리, 기업 목록 다운로드

## 자동 업데이트

GitHub Actions를 통해 **매일 평일 한국시간 15:00**에 자동으로 데이터가 업데이트됩니다.
수동 실행도 가능합니다 (Actions > Daily Data Update > Run workflow).
