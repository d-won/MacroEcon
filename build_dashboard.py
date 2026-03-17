"""
CSV 데이터를 읽어 정적 HTML 대시보드를 생성하는 스크립트.
GitHub Actions에서 데이터 수집 후 실행되며, docs/index.html을 생성.
GitHub Pages로 배포됨.
"""

import os
import json
import datetime
import pandas as pd

from companies import LEADING_COMPANIES

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")


def load_data():
    summary_path = os.path.join(DATA_DIR, "summary_latest.csv")
    prices_path = os.path.join(DATA_DIR, "prices_latest.csv")
    quarterly_path = os.path.join(DATA_DIR, "quarterly_latest.csv")

    summary_df = pd.read_csv(summary_path) if os.path.exists(summary_path) else pd.DataFrame()
    prices_df = pd.read_csv(prices_path) if os.path.exists(prices_path) else pd.DataFrame()
    quarterly_df = pd.read_csv(quarterly_path) if os.path.exists(quarterly_path) else pd.DataFrame()

    return summary_df, prices_df, quarterly_df


def build_summary_json(summary_df):
    if summary_df.empty:
        return "[]"
    records = summary_df.fillna("null").to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if v == "null" or (isinstance(v, float) and pd.isna(v)):
                r[k] = None
    return json.dumps(records, ensure_ascii=False)


def build_prices_json(prices_df):
    if prices_df.empty:
        return "{}"
    result = {}
    for ticker, group in prices_df.groupby("Ticker"):
        group = group.sort_values("Date")
        result[ticker] = {
            "dates": group["Date"].tolist(),
            "close": [round(v, 2) for v in group["Close"].tolist()],
            "name": group["Name"].iloc[0] if "Name" in group.columns else ticker,
        }
    return json.dumps(result, ensure_ascii=False)


def build_quarterly_json(quarterly_df):
    """분기 실적을 티커별 시계열 JSON으로 변환"""
    if quarterly_df.empty:
        return "{}"
    result = {}
    for ticker, group in quarterly_df.groupby("Ticker"):
        group = group.sort_values("Date")
        dates = group["Date"].tolist()
        revenue = []
        op_income = []
        for _, row in group.iterrows():
            revenue.append(round(row["Revenue"], 0) if pd.notna(row.get("Revenue")) else None)
            op_income.append(round(row["Operating_Income"], 0) if pd.notna(row.get("Operating_Income")) else None)
        result[ticker] = {
            "dates": dates,
            "revenue": revenue,
            "operating_income": op_income,
        }
    return json.dumps(result, ensure_ascii=False)


def build_companies_json():
    return json.dumps(LEADING_COMPANIES, ensure_ascii=False)


def generate_html(summary_json, prices_json, quarterly_json, companies_json, updated_at):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>경기 선행 지표 기업 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #0f1117;
  --card: #1a1d29;
  --border: #2a2d3a;
  --text: #e0e0e0;
  --text-dim: #888;
  --accent: #4f8ff7;
  --green: #22c55e;
  --red: #ef4444;
  --yellow: #eab308;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  min-height: 100vh;
}}
.container {{ max-width: 1400px; margin: 0 auto; padding: 16px; }}

header {{
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-bottom: 1px solid var(--border);
  padding: 20px 0;
  margin-bottom: 20px;
}}
header .container {{ display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }}
header h1 {{ font-size: 1.4rem; font-weight: 700; }}
header h1 span {{ font-size: 1.6rem; margin-right: 8px; }}
.updated {{ font-size: 0.8rem; color: var(--text-dim); }}

.tabs {{
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 4px;
}}
.tab {{
  padding: 10px 18px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  font-size: 0.9rem;
  color: var(--text-dim);
  transition: all 0.2s;
}}
.tab:hover {{ border-color: var(--accent); color: var(--text); }}
.tab.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

.kpi-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}}
.kpi {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}}
.kpi-label {{ font-size: 0.75rem; color: var(--text-dim); margin-bottom: 4px; }}
.kpi-value {{ font-size: 1.5rem; font-weight: 700; }}
.kpi-value.positive {{ color: var(--green); }}
.kpi-value.negative {{ color: var(--red); }}

.sector-badge {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
}}

.table-wrap {{
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--card);
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  white-space: nowrap;
}}
th {{
  background: #1e2235;
  position: sticky;
  top: 0;
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-dim);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
}}
th:hover {{ color: var(--accent); }}
td {{
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
}}
tr.clickable {{ cursor: pointer; }}
tr.clickable:hover {{ background: rgba(79,143,247,0.08); }}
tr.selected {{ background: rgba(79,143,247,0.15) !important; }}
.pos {{ color: var(--green); font-weight: 600; }}
.neg {{ color: var(--red); font-weight: 600; }}

tr.sector-header td {{
  font-weight: 700;
  font-size: 0.85rem;
  padding: 10px 14px;
  border-bottom: 2px solid;
  color: #fff;
}}

/* Stock chart panel */
.stock-chart-panel {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  margin-top: 16px;
  display: none;
}}
.stock-chart-panel.visible {{ display: block; }}
.stock-chart-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}}
.stock-chart-header h3 {{ font-size: 1.1rem; }}
.stock-chart-close {{
  background: none;
  border: 1px solid var(--border);
  color: var(--text-dim);
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}}
.stock-chart-close:hover {{ border-color: var(--red); color: var(--red); }}
.stock-chart-info {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}}
.stock-info-item {{
  text-align: center;
  padding: 8px;
  background: var(--bg);
  border-radius: 6px;
}}
.stock-info-item .label {{ font-size: 0.7rem; color: var(--text-dim); }}
.stock-info-item .value {{ font-size: 0.95rem; font-weight: 600; }}
.stock-chart-canvas-wrap {{ position: relative; height: 350px; }}

/* References */
.ref-section {{
  margin-top: 16px;
  padding: 14px;
  background: var(--bg);
  border-radius: 8px;
}}
.ref-section h4 {{
  font-size: 0.8rem;
  color: var(--text-dim);
  margin-bottom: 8px;
  text-transform: uppercase;
}}
.ref-list {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}}
.ref-link {{
  display: inline-block;
  padding: 4px 10px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--accent);
  text-decoration: none;
  font-size: 0.78rem;
  transition: all 0.15s;
}}
.ref-link:hover {{
  background: rgba(79,143,247,0.15);
  border-color: var(--accent);
}}

/* Quarterly chart section */
.quarterly-section {{
  margin-top: 16px;
}}
.quarterly-section h4 {{
  font-size: 0.85rem;
  margin-bottom: 10px;
  color: var(--text);
}}
.quarterly-chart-wrap {{
  position: relative;
  height: 280px;
}}

/* Floating back-to-top button */
.back-to-top {{
  position: fixed;
  bottom: 28px;
  right: 28px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, visibility 0.3s, transform 0.2s;
  z-index: 1000;
}}
.back-to-top.visible {{
  opacity: 1;
  visibility: visible;
}}
.back-to-top:hover {{
  transform: scale(1.1);
}}

.filters {{
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
}}
.filter-group label {{
  display: block;
  font-size: 0.75rem;
  color: var(--text-dim);
  margin-bottom: 4px;
}}
.filter-group select {{
  background: var(--card);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
}}

.chart-box {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}}
.chart-box canvas {{ max-height: 500px; }}

.sector-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 14px;
}}
.sector-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px;
  border-top: 3px solid;
}}
.sector-card-header {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}}
.sector-card-header h3 {{ font-size: 1rem; }}
.sector-avg {{
  font-size: 1.1rem;
  font-weight: 700;
}}
.sector-company {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 0.85rem;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  cursor: pointer;
  transition: background 0.15s;
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 4px;
}}
.sector-company:hover {{ background: rgba(79,143,247,0.08); }}
.sector-company:last-child {{ border-bottom: none; }}
.sector-company .ticker {{ color: var(--accent); font-weight: 600; margin-right: 6px; }}

.download-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}}
.download-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px;
  text-align: center;
}}
.download-card h3 {{ margin-bottom: 8px; }}
.download-card p {{ color: var(--text-dim); font-size: 0.85rem; margin-bottom: 16px; }}
.btn {{
  display: inline-block;
  padding: 10px 24px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.2s;
}}
.btn:hover {{ opacity: 0.85; }}

@media (max-width: 768px) {{
  .container {{ padding: 10px; }}
  header h1 {{ font-size: 1.1rem; }}
  .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
  .kpi-value {{ font-size: 1.2rem; }}
  table {{ font-size: 0.75rem; }}
  th, td {{ padding: 8px 10px; }}
  .tab {{ padding: 8px 14px; font-size: 0.8rem; }}
  .stock-chart-canvas-wrap {{ height: 250px; }}
  .stock-chart-info {{ grid-template-columns: repeat(3, 1fr); }}
  .quarterly-chart-wrap {{ height: 200px; }}
  .back-to-top {{ bottom: 16px; right: 16px; width: 42px; height: 42px; font-size: 1.1rem; }}
}}
</style>
</head>
<body>

<header>
  <div class="container">
    <h1><span>📊</span> 경기 선행 지표 기업 대시보드</h1>
    <div class="updated">마지막 업데이트: {updated_at}</div>
  </div>
</header>

<div class="container">
  <div class="tabs" id="tabs">
    <div class="tab active" data-tab="overview">📈 종합 현황</div>
    <div class="tab" data-tab="chart">📉 주가 비교</div>
    <div class="tab" data-tab="sector">🏭 섹터 분석</div>
    <div class="tab" data-tab="download">💾 CSV 다운로드</div>
  </div>

  <!-- ===== 종합 현황 ===== -->
  <div class="tab-content active" id="tab-overview">
    <div class="kpi-row" id="kpi-row"></div>
    <div class="filters">
      <div class="filter-group">
        <label>섹터</label>
        <select id="filter-sector"><option value="all">전체</option></select>
      </div>
      <div class="filter-group">
        <label>국가</label>
        <select id="filter-country"><option value="all">전체</option></select>
      </div>
    </div>
    <div class="table-wrap">
      <table id="summary-table">
        <thead><tr id="summary-header"></tr></thead>
        <tbody id="summary-body"></tbody>
      </table>
    </div>
    <div class="stock-chart-panel" id="stock-chart-panel">
      <div class="stock-chart-header">
        <h3 id="stock-chart-title"></h3>
        <button class="stock-chart-close" onclick="closeStockChart()">닫기</button>
      </div>
      <div class="stock-chart-info" id="stock-chart-info"></div>
      <div class="stock-chart-canvas-wrap">
        <canvas id="stockChart"></canvas>
      </div>
      <!-- 분기 실적 차트 -->
      <div class="quarterly-section" id="quarterly-section" style="display:none">
        <h4>분기별 매출 / 영업이익 (최근 5개년)</h4>
        <div class="quarterly-chart-wrap">
          <canvas id="quarterlyChart"></canvas>
        </div>
      </div>
      <!-- 근거자료 링크 -->
      <div class="ref-section" id="ref-section" style="display:none">
        <h4>경기 선행 근거자료</h4>
        <div class="ref-list" id="ref-list"></div>
      </div>
    </div>
  </div>

  <!-- ===== 주가 비교 ===== -->
  <div class="tab-content" id="tab-chart">
    <div class="filters">
      <div class="filter-group">
        <label>섹터 필터</label>
        <select id="chart-sector-filter"><option value="all">전체</option></select>
      </div>
      <div class="filter-group">
        <label style="display:flex;align-items:center;gap:6px;">
          <input type="checkbox" id="chart-normalize" checked> 정규화 (시작=100)
        </label>
      </div>
    </div>
    <div class="chart-box">
      <canvas id="priceChart"></canvas>
    </div>
  </div>

  <!-- ===== 섹터 분석 ===== -->
  <div class="tab-content" id="tab-sector">
    <div class="filters">
      <div class="filter-group">
        <label>기간</label>
        <select id="sector-period">
          <option value="Change_1D_pct">1일</option>
          <option value="Change_1W_pct">1주</option>
          <option value="Change_1M_pct" selected>1개월</option>
          <option value="Change_3M_pct">3개월</option>
        </select>
      </div>
    </div>
    <div class="chart-box">
      <canvas id="sectorChart"></canvas>
    </div>
    <div class="sector-grid" id="sector-grid"></div>
  </div>

  <!-- ===== CSV 다운로드 ===== -->
  <div class="tab-content" id="tab-download">
    <div class="download-grid">
      <div class="download-card">
        <h3>📋 기업 요약 데이터</h3>
        <p>현재가, 변동률, 시가총액, PER 등</p>
        <button class="btn" onclick="downloadCSV('summary')">📥 다운로드</button>
      </div>
      <div class="download-card">
        <h3>📈 주가 히스토리</h3>
        <p>일별 시가·고가·저가·종가·거래량</p>
        <button class="btn" onclick="downloadCSV('prices')">📥 다운로드</button>
      </div>
      <div class="download-card">
        <h3>🏢 기업 목록</h3>
        <p>20개 선행 기업 메타데이터 및 선행 근거</p>
        <button class="btn" onclick="downloadCSV('companies')">📥 다운로드</button>
      </div>
    </div>
  </div>
</div>

<!-- Floating back-to-top button -->
<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
// ── 데이터 ──
const summaryData = {summary_json};
const pricesData = {prices_json};
const quarterlyData = {quarterly_json};
const companiesData = {companies_json};
const companyMap = {{}};
companiesData.forEach(c => companyMap[c.ticker] = c);

// ── 상단 복귀 버튼 ──
const backToTopBtn = document.getElementById('backToTop');
window.addEventListener('scroll', () => {{
  backToTopBtn.classList.toggle('visible', window.scrollY > 400);
}});

// ── 섹터 색상 매핑 ──
const SECTOR_COLORS = {{
  '운송/물류': '#3b82f6',
  '반도체': '#8b5cf6',
  '산업재/건설': '#f59e0b',
  '화학/소재': '#10b981',
  '금융': '#06b6d4',
  '채용/인력': '#ec4899',
  '소비재': '#f97316',
  '원자재/에너지': '#ef4444',
}};
function getSectorColor(sector) {{
  return SECTOR_COLORS[sector] || '#64748b';
}}

// ── 탭 전환 ──
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  }});
}});

// ── 유틸 ──
function fmt(v, decimals=2) {{
  if (v == null || isNaN(v)) return '-';
  return Number(v).toFixed(decimals);
}}
function fmtPct(v) {{
  if (v == null || isNaN(v)) return '-';
  const n = Number(v);
  const sign = n > 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}}
function pctClass(v) {{
  if (v == null || isNaN(v)) return '';
  return Number(v) > 0 ? 'pos' : Number(v) < 0 ? 'neg' : '';
}}
function fmtCap(v) {{
  if (!v || isNaN(v)) return '-';
  if (v >= 1e12) return '$' + (v/1e12).toFixed(1) + 'T';
  if (v >= 1e9) return '$' + (v/1e9).toFixed(1) + 'B';
  return '$' + (v/1e6).toFixed(0) + 'M';
}}
function fmtRevenue(v) {{
  if (v == null || isNaN(v)) return '-';
  const abs = Math.abs(v);
  if (abs >= 1e9) return (v/1e9).toFixed(1) + 'B';
  if (abs >= 1e6) return (v/1e6).toFixed(0) + 'M';
  return (v/1e3).toFixed(0) + 'K';
}}

const COLORS = [
  '#4f8ff7','#22c55e','#ef4444','#eab308','#a855f7',
  '#ec4899','#06b6d4','#f97316','#84cc16','#6366f1',
  '#14b8a6','#f43f5e','#8b5cf6','#0ea5e9','#d946ef',
  '#64748b','#fb923c','#34d399','#fbbf24','#f87171'
];

// ── KPI 카드 ──
function renderKPI() {{
  const row = document.getElementById('kpi-row');
  if (!summaryData.length) return;
  const metrics = [
    ['평균 1일 변동률', 'Change_1D_pct'],
    ['평균 1주 변동률', 'Change_1W_pct'],
    ['평균 1개월 변동률', 'Change_1M_pct'],
    ['평균 3개월 변동률', 'Change_3M_pct'],
  ];
  row.innerHTML = metrics.map(([label, key]) => {{
    const vals = summaryData.map(d => d[key]).filter(v => v != null && !isNaN(v));
    const avg = vals.reduce((a,b) => a+b, 0) / vals.length;
    const cls = avg > 0 ? 'positive' : avg < 0 ? 'negative' : '';
    return `<div class="kpi"><div class="kpi-label">${{label}}</div><div class="kpi-value ${{cls}}">${{fmtPct(avg)}}</div></div>`;
  }}).join('');
}}

// ── 필터 초기화 ──
function initFilters() {{
  const sectors = [...new Set(summaryData.map(d => d.Sector))].sort();
  const countries = [...new Set(summaryData.map(d => d.Country))].sort();

  ['filter-sector','chart-sector-filter'].forEach(id => {{
    const sel = document.getElementById(id);
    if(!sel) return;
    sectors.forEach(s => {{
      const opt = document.createElement('option');
      opt.value = s; opt.textContent = s;
      sel.appendChild(opt);
    }});
  }});

  const countrySel = document.getElementById('filter-country');
  countries.forEach(c => {{
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    countrySel.appendChild(opt);
  }});
}}

// ── 요약 테이블 (섹터별 그룹) ──
const TABLE_COLS = [
  {{key:'Ticker', label:'티커', sort:'string'}},
  {{key:'Name', label:'기업명', sort:'string'}},
  {{key:'Sector', label:'섹터', sort:'string', isSector: true}},
  {{key:'Country', label:'국가', sort:'string'}},
  {{key:'Current_Price', label:'현재가', sort:'number', fmt: v => fmt(v)}},
  {{key:'Change_1D_pct', label:'1일 %', sort:'number', fmt: fmtPct, cls: pctClass}},
  {{key:'Change_1W_pct', label:'1주 %', sort:'number', fmt: fmtPct, cls: pctClass}},
  {{key:'Change_1M_pct', label:'1개월 %', sort:'number', fmt: fmtPct, cls: pctClass}},
  {{key:'Change_3M_pct', label:'3개월 %', sort:'number', fmt: fmtPct, cls: pctClass}},
  {{key:'Market_Cap', label:'시가총액', sort:'number', fmt: fmtCap}},
  {{key:'PE_Ratio', label:'PER', sort:'number', fmt: v => fmt(v,1)}},
];

let sortCol = null, sortAsc = true;

function renderTable() {{
  const sector = document.getElementById('filter-sector').value;
  const country = document.getElementById('filter-country').value;

  let data = summaryData.filter(d =>
    (sector === 'all' || d.Sector === sector) &&
    (country === 'all' || d.Country === country)
  );

  if (sortCol !== null) {{
    const col = TABLE_COLS[sortCol];
    data.sort((a, b) => {{
      let va = a[col.key], vb = b[col.key];
      if (col.sort === 'number') {{
        va = va == null ? -Infinity : Number(va);
        vb = vb == null ? -Infinity : Number(vb);
        return sortAsc ? va - vb : vb - va;
      }}
      va = (va || '').toString(); vb = (vb || '').toString();
      return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    }});
  }}

  const header = document.getElementById('summary-header');
  header.innerHTML = TABLE_COLS.map((c, i) =>
    `<th onclick="sortTable(${{i}})">${{c.label}} ${{sortCol === i ? (sortAsc ? '▲' : '▼') : ''}}</th>`
  ).join('');

  const groupBySector = sortCol === null && sector === 'all';
  const body = document.getElementById('summary-body');

  if (groupBySector) {{
    const sectorOrder = [...new Set(data.map(d => d.Sector))];
    let html = '';
    sectorOrder.forEach(s => {{
      const color = getSectorColor(s);
      html += `<tr class="sector-header"><td colspan="${{TABLE_COLS.length}}" style="border-color:${{color}}; background: ${{color}}20;"><span style="color:${{color}}">■</span> ${{s}}</td></tr>`;
      const sectorData = data.filter(d => d.Sector === s);
      sectorData.forEach(d => {{
        html += renderRow(d);
      }});
    }});
    body.innerHTML = html;
  }} else {{
    body.innerHTML = data.map(d => renderRow(d)).join('');
  }}
}}

function renderRow(d) {{
  return `<tr class="clickable" onclick="showStockChart('${{d.Ticker}}')" data-ticker="${{d.Ticker}}">` +
    TABLE_COLS.map(c => {{
      const val = d[c.key];
      if (c.isSector) {{
        const color = getSectorColor(val);
        return `<td><span class="sector-badge" style="background:${{color}}">${{val}}</span></td>`;
      }}
      const display = c.fmt ? c.fmt(val) : (val ?? '-');
      const cls = c.cls ? c.cls(val) : '';
      return `<td class="${{cls}}">${{display}}</td>`;
    }}).join('') + '</tr>';
}}

function sortTable(colIdx) {{
  if (sortCol === colIdx) sortAsc = !sortAsc;
  else {{ sortCol = colIdx; sortAsc = true; }}
  renderTable();
}}

// ── 개별 종목 주가 차트 ──
let stockChart = null;
let quarterlyChart = null;
let selectedTicker = null;

function showStockChart(ticker) {{
  const panel = document.getElementById('stock-chart-panel');
  const d = summaryData.find(r => r.Ticker === ticker);
  const info = companyMap[ticker] || {{}};
  const pData = pricesData[ticker];

  if (!d) return;

  selectedTicker = ticker;
  document.querySelectorAll('#summary-body tr.clickable').forEach(tr => {{
    tr.classList.toggle('selected', tr.dataset.ticker === ticker);
  }});

  const color = getSectorColor(d.Sector);
  const leadMonths = info.lead_months || '3-6';
  document.getElementById('stock-chart-title').innerHTML =
    `${{d.Name}} <span style="color:var(--text-dim);font-weight:400;font-size:0.9rem">(${{d.Ticker}})</span> <span class="sector-badge" style="background:${{color}};font-size:0.7rem;vertical-align:middle">${{d.Sector}}</span> <span style="font-size:0.75rem;color:var(--yellow);font-weight:400;margin-left:6px">⏱ 약 ${{leadMonths}}개월 선행</span>`;

  document.getElementById('stock-chart-info').innerHTML = `
    <div class="stock-info-item"><div class="label">현재가</div><div class="value">${{fmt(d.Current_Price)}}</div></div>
    <div class="stock-info-item"><div class="label">1일</div><div class="value ${{pctClass(d.Change_1D_pct)}}">${{fmtPct(d.Change_1D_pct)}}</div></div>
    <div class="stock-info-item"><div class="label">1주</div><div class="value ${{pctClass(d.Change_1W_pct)}}">${{fmtPct(d.Change_1W_pct)}}</div></div>
    <div class="stock-info-item"><div class="label">1개월</div><div class="value ${{pctClass(d.Change_1M_pct)}}">${{fmtPct(d.Change_1M_pct)}}</div></div>
    <div class="stock-info-item"><div class="label">3개월</div><div class="value ${{pctClass(d.Change_3M_pct)}}">${{fmtPct(d.Change_3M_pct)}}</div></div>
    <div class="stock-info-item"><div class="label">시가총액</div><div class="value">${{fmtCap(d.Market_Cap)}}</div></div>
    <div class="stock-info-item"><div class="label">PER</div><div class="value">${{fmt(d.PE_Ratio, 1)}}</div></div>
    <div class="stock-info-item"><div class="label">52주 고/저</div><div class="value" style="font-size:0.8rem">${{fmt(d['52W_High'])}} / ${{fmt(d['52W_Low'])}}</div></div>
  `;
  if (info.reason) {{
    document.getElementById('stock-chart-info').innerHTML += `
      <div class="stock-info-item" style="grid-column: 1 / -1; text-align:left;">
        <div class="label">선행 근거</div>
        <div style="font-size:0.85rem;font-weight:400;color:var(--text)">${{info.reason}}</div>
      </div>`;
  }}

  // 주가 차트
  if (pData && pData.dates.length > 0) {{
    if (stockChart) stockChart.destroy();

    const prices = pData.close;
    const startPrice = prices[0];
    const endPrice = prices[prices.length - 1];
    const isUp = endPrice >= startPrice;
    const lineColor = isUp ? '#22c55e' : '#ef4444';
    const bgColor = isUp ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)';

    stockChart = new Chart(document.getElementById('stockChart'), {{
      type: 'line',
      data: {{
        labels: pData.dates,
        datasets: [{{
          label: d.Name + ' 종가',
          data: prices,
          borderColor: lineColor,
          backgroundColor: bgColor,
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 4,
          tension: 0.3,
          fill: true,
        }}],
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            backgroundColor: '#1a1d29',
            titleColor: '#e0e0e0',
            bodyColor: '#e0e0e0',
            borderColor: '#2a2d3a',
            borderWidth: 1,
            callbacks: {{
              label: ctx => `${{d.Currency || 'USD'}} ${{ctx.parsed.y.toFixed(2)}}`
            }}
          }},
        }},
        scales: {{
          x: {{ ticks: {{ color: '#666', maxTicksLimit: 8 }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
          y: {{ ticks: {{ color: '#666' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
        }},
      }},
    }});
  }}

  // 분기 실적 차트
  const qSection = document.getElementById('quarterly-section');
  const qData = quarterlyData[ticker];
  if (qData && qData.dates && qData.dates.length > 0) {{
    qSection.style.display = 'block';
    if (quarterlyChart) quarterlyChart.destroy();

    // 분기 라벨 (YYYY-MM → YYYY Q#)
    const qLabels = qData.dates.map(dt => {{
      const parts = dt.split('-');
      const month = parseInt(parts[1]);
      const q = Math.ceil(month / 3);
      return parts[0] + ' Q' + q;
    }});

    quarterlyChart = new Chart(document.getElementById('quarterlyChart'), {{
      type: 'bar',
      data: {{
        labels: qLabels,
        datasets: [
          {{
            label: '매출',
            data: qData.revenue,
            backgroundColor: 'rgba(79,143,247,0.7)',
            borderRadius: 4,
            yAxisID: 'y',
            order: 2,
          }},
          {{
            label: '영업이익',
            data: qData.operating_income,
            type: 'line',
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34,197,94,0.1)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3,
            fill: false,
            yAxisID: 'y',
            order: 1,
          }},
        ],
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ position: 'top', labels: {{ color: '#888', boxWidth: 12, font: {{size: 11}} }} }},
          tooltip: {{
            backgroundColor: '#1a1d29',
            titleColor: '#e0e0e0',
            bodyColor: '#e0e0e0',
            callbacks: {{
              label: ctx => {{
                const v = ctx.parsed.y;
                return ctx.dataset.label + ': $' + fmtRevenue(v);
              }}
            }}
          }},
        }},
        scales: {{
          x: {{ ticks: {{ color: '#666', maxRotation: 45 }}, grid: {{ display: false }} }},
          y: {{
            ticks: {{
              color: '#666',
              callback: v => '$' + fmtRevenue(v),
            }},
            grid: {{ color: 'rgba(255,255,255,0.05)' }},
          }},
        }},
      }},
    }});
  }} else {{
    qSection.style.display = 'none';
  }}

  // 근거자료 링크
  const refSection = document.getElementById('ref-section');
  const refList = document.getElementById('ref-list');
  if (info.references && info.references.length > 0) {{
    refSection.style.display = 'block';
    refList.innerHTML = info.references.map(ref =>
      `<a class="ref-link" href="${{ref.url}}" target="_blank" rel="noopener">${{ref.title}}</a>`
    ).join('');
  }} else {{
    refSection.style.display = 'none';
  }}

  panel.classList.add('visible');
  panel.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}

function closeStockChart() {{
  document.getElementById('stock-chart-panel').classList.remove('visible');
  document.querySelectorAll('#summary-body tr.clickable').forEach(tr => tr.classList.remove('selected'));
  selectedTicker = null;
  if (stockChart) {{ stockChart.destroy(); stockChart = null; }}
  if (quarterlyChart) {{ quarterlyChart.destroy(); quarterlyChart = null; }}
}}

// ── 주가 비교 차트 ──
let priceChart = null;
function renderPriceChart() {{
  const sectorFilter = document.getElementById('chart-sector-filter').value;
  const normalize = document.getElementById('chart-normalize').checked;

  const tickers = Object.keys(pricesData).filter(t => {{
    if (sectorFilter === 'all') return true;
    const info = companyMap[t];
    return info && info.sector === sectorFilter;
  }});

  const datasets = tickers.map((ticker, i) => {{
    const d = pricesData[ticker];
    const info = companyMap[ticker];
    const sectorColor = info ? getSectorColor(info.sector) : COLORS[i % COLORS.length];
    let values = d.close;
    if (normalize && values.length > 0) {{
      const base = values[0];
      values = values.map(v => base > 0 ? (v / base * 100) : v);
    }}
    return {{
      label: d.name || ticker,
      data: values,
      borderColor: sectorFilter === 'all' ? sectorColor : COLORS[i % COLORS.length],
      borderWidth: 1.5,
      pointRadius: 0,
      tension: 0.3,
      fill: false,
    }};
  }});

  const labels = tickers.length > 0 ? pricesData[tickers[0]].dates : [];

  if (priceChart) priceChart.destroy();
  priceChart = new Chart(document.getElementById('priceChart'), {{
    type: 'line',
    data: {{ labels, datasets }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      interaction: {{ mode: 'index', intersect: false }},
      plugins: {{
        legend: {{ position: 'bottom', labels: {{ color: '#888', boxWidth: 12, font: {{size: 11}} }} }},
        tooltip: {{ backgroundColor: '#1a1d29', titleColor: '#e0e0e0', bodyColor: '#e0e0e0', borderColor: '#2a2d3a', borderWidth: 1 }},
      }},
      scales: {{
        x: {{ ticks: {{ color: '#666', maxTicksLimit: 12 }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
        y: {{ ticks: {{ color: '#666' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      }},
    }},
  }});
  document.getElementById('priceChart').parentElement.style.height = '500px';
}}

// ── 섹터 분석 ──
let sectorChart = null;
function renderSectorAnalysis() {{
  const periodKey = document.getElementById('sector-period').value;
  const periodLabel = {{'Change_1D_pct':'1일','Change_1W_pct':'1주','Change_1M_pct':'1개월','Change_3M_pct':'3개월'}}[periodKey];

  const sectorMap = {{}};
  summaryData.forEach(d => {{
    if (!sectorMap[d.Sector]) sectorMap[d.Sector] = [];
    if (d[periodKey] != null) sectorMap[d.Sector].push(d[periodKey]);
  }});

  const sectors = Object.keys(sectorMap).sort((a,b) => {{
    const avgA = sectorMap[a].reduce((s,v) => s+v, 0) / sectorMap[a].length;
    const avgB = sectorMap[b].reduce((s,v) => s+v, 0) / sectorMap[b].length;
    return avgB - avgA;
  }});

  const avgs = sectors.map(s => {{
    const vals = sectorMap[s];
    return +(vals.reduce((a,b) => a+b, 0) / vals.length).toFixed(2);
  }});

  const bgColors = sectors.map(s => getSectorColor(s));

  if (sectorChart) sectorChart.destroy();
  sectorChart = new Chart(document.getElementById('sectorChart'), {{
    type: 'bar',
    data: {{
      labels: sectors,
      datasets: [{{ label: `평균 ${{periodLabel}} 변동률 (%)`, data: avgs, backgroundColor: bgColors, borderRadius: 6 }}],
    }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1d29',
          titleColor: '#e0e0e0',
          bodyColor: '#e0e0e0',
          callbacks: {{
            label: ctx => `${{ctx.parsed.x > 0 ? '+' : ''}}${{ctx.parsed.x.toFixed(2)}}%`
          }}
        }},
      }},
      scales: {{
        x: {{
          ticks: {{ color: '#666', callback: v => v + '%' }},
          grid: {{ color: 'rgba(255,255,255,0.05)' }},
        }},
        y: {{ ticks: {{ color: '#ccc', font: {{ weight: 'bold' }} }}, grid: {{ display: false }} }},
      }},
    }},
  }});

  const grid = document.getElementById('sector-grid');
  grid.innerHTML = sectors.map((s, si) => {{
    const companies = summaryData.filter(d => d.Sector === s);
    const avg = avgs[si];
    const color = getSectorColor(s);
    const compHTML = companies.map(d =>
      `<div class="sector-company" onclick="navigateToStock('${{d.Ticker}}')">
        <span><span class="ticker">${{d.Ticker}}</span> ${{d.Name}}</span>
        <span class="${{pctClass(d[periodKey])}}">${{fmtPct(d[periodKey])}}</span>
      </div>`
    ).join('');
    return `<div class="sector-card" style="border-top-color:${{color}}">
      <div class="sector-card-header">
        <h3 style="color:${{color}}">${{s}}</h3>
        <span class="sector-avg ${{pctClass(avg)}}">${{fmtPct(avg)}}</span>
      </div>
      ${{compHTML}}
    </div>`;
  }}).join('');
}}

function navigateToStock(ticker) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
  document.querySelector('[data-tab="overview"]').classList.add('active');
  document.getElementById('tab-overview').classList.add('active');
  showStockChart(ticker);
}}

// ── CSV 다운로드 ──
function downloadCSV(type) {{
  let csv = '', filename = '';
  const today = new Date().toISOString().slice(0,10);

  if (type === 'summary') {{
    const cols = ['Ticker','Name','Sector','Country','Current_Price','Currency','Change_1D_pct','Change_1W_pct','Change_1M_pct','Change_3M_pct','Market_Cap','PE_Ratio','52W_High','52W_Low','Reason'];
    csv = '\\uFEFF' + cols.join(',') + '\\n';
    summaryData.forEach(d => {{
      csv += cols.map(c => {{
        let v = d[c] ?? '';
        if (typeof v === 'string' && (v.includes(',') || v.includes('"')))
          v = '"' + v.replace(/"/g, '""') + '"';
        return v;
      }}).join(',') + '\\n';
    }});
    filename = `leading_companies_summary_${{today}}.csv`;
  }}
  else if (type === 'prices') {{
    const cols = ['Date','Ticker','Name','Close'];
    csv = '\\uFEFF' + cols.join(',') + '\\n';
    Object.entries(pricesData).forEach(([ticker, d]) => {{
      d.dates.forEach((date, i) => {{
        csv += `${{date}},${{ticker}},"${{d.name}}",${{d.close[i]}}\\n`;
      }});
    }});
    filename = `leading_companies_prices_${{today}}.csv`;
  }}
  else if (type === 'companies') {{
    const cols = ['ticker','name','sector','country','reason'];
    csv = '\\uFEFF' + cols.join(',') + '\\n';
    companiesData.forEach(d => {{
      csv += cols.map(c => {{
        let v = d[c] ?? '';
        if (typeof v === 'string' && (v.includes(',') || v.includes('"')))
          v = '"' + v.replace(/"/g, '""') + '"';
        return v;
      }}).join(',') + '\\n';
    }});
    filename = `leading_companies_list.csv`;
  }}

  const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}}

// ── 이벤트 바인딩 ──
document.getElementById('filter-sector').addEventListener('change', renderTable);
document.getElementById('filter-country').addEventListener('change', renderTable);
document.getElementById('chart-sector-filter').addEventListener('change', renderPriceChart);
document.getElementById('chart-normalize').addEventListener('change', renderPriceChart);
document.getElementById('sector-period').addEventListener('change', renderSectorAnalysis);

// ── 초기 렌더 ──
initFilters();
renderKPI();
renderTable();
renderPriceChart();
renderSectorAnalysis();
</script>
</body>
</html>"""


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    summary_df, prices_df, quarterly_df = load_data()

    summary_json = build_summary_json(summary_df)
    prices_json = build_prices_json(prices_df)
    quarterly_json = build_quarterly_json(quarterly_df)
    companies_json = build_companies_json()

    ts_path = os.path.join(DATA_DIR, "last_updated.txt")
    if os.path.exists(ts_path):
        with open(ts_path) as f:
            updated_at = f.read().strip()[:19].replace("T", " ")
    else:
        updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = generate_html(summary_json, prices_json, quarterly_json, companies_json, updated_at)

    out_path = os.path.join(DOCS_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {out_path}")


if __name__ == "__main__":
    main()
