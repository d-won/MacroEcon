"""
경기 선행 지표 기업 대시보드

Streamlit 기반 인터랙티브 대시보드.
실행: streamlit run dashboard.py
"""

import os
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from companies import LEADING_COMPANIES, get_company_info

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── 페이지 설정 ──
st.set_page_config(
    page_title="경기 선행 지표 기업 대시보드",
    page_icon="📊",
    layout="wide",
)

st.title("📊 경기 선행 지표 기업 대시보드")
st.markdown("경기 사이클을 선행하는 글로벌 핵심 기업들의 주가·재무 데이터를 한눈에 확인하세요.")


# ── 데이터 로드 ──
@st.cache_data(ttl=3600)
def load_summary():
    path = os.path.join(DATA_DIR, "summary_latest.csv")
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_prices():
    path = os.path.join(DATA_DIR, "prices_latest.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


def load_last_updated():
    path = os.path.join(DATA_DIR, "last_updated.txt")
    if os.path.exists(path):
        with open(path) as f:
            return f.read().strip()
    return None


# ── 사이드바 ──
st.sidebar.header("필터")

sectors = sorted(set(c["sector"] for c in LEADING_COMPANIES))
selected_sectors = st.sidebar.multiselect(
    "섹터 선택", sectors, default=sectors,
    help="보고 싶은 섹터를 선택하세요"
)

countries = sorted(set(c["country"] for c in LEADING_COMPANIES))
selected_countries = st.sidebar.multiselect(
    "국가 선택", countries, default=countries,
)

last_updated = load_last_updated()
if last_updated:
    st.sidebar.markdown("---")
    st.sidebar.caption(f"마지막 업데이트: {last_updated[:19]}")

# ── 메인 콘텐츠 ──
summary_df = load_summary()
prices_df = load_prices()

if summary_df is None:
    st.warning(
        "데이터가 아직 없습니다. 먼저 `python fetch_data.py`를 실행하여 데이터를 수집하세요."
    )
    st.code("pip install -r requirements.txt\npython fetch_data.py", language="bash")

    # 기업 목록은 항상 표시
    st.subheader("📋 추적 대상 기업 목록")
    info_df = pd.DataFrame(LEADING_COMPANIES)
    st.dataframe(info_df, use_container_width=True)
    st.stop()

# 필터 적용
mask = summary_df["Sector"].isin(selected_sectors) & summary_df["Country"].isin(selected_countries)
filtered_summary = summary_df[mask].copy()

# ── 탭 구성 ──
tab_overview, tab_chart, tab_sector, tab_detail, tab_download = st.tabs(
    ["📈 종합 현황", "📉 주가 차트", "🏭 섹터 분석", "🔍 기업 상세", "💾 CSV 다운로드"]
)

# ━━━ 탭 1: 종합 현황 ━━━
with tab_overview:
    st.subheader("종합 현황")

    # KPI 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_1d = filtered_summary["Change_1D_pct"].mean()
        st.metric("평균 1일 변동률", f"{avg_1d:+.2f}%")
    with col2:
        avg_1w = filtered_summary["Change_1W_pct"].mean()
        st.metric("평균 1주 변동률", f"{avg_1w:+.2f}%")
    with col3:
        avg_1m = filtered_summary["Change_1M_pct"].mean()
        st.metric("평균 1개월 변동률", f"{avg_1m:+.2f}%")
    with col4:
        avg_3m = filtered_summary["Change_3M_pct"].mean()
        st.metric("평균 3개월 변동률", f"{avg_3m:+.2f}%")

    st.markdown("---")

    # 전체 기업 테이블
    st.subheader("기업별 현황")
    display_cols = ["Ticker", "Name", "Sector", "Country", "Current_Price",
                    "Currency", "Change_1D_pct", "Change_1W_pct",
                    "Change_1M_pct", "Change_3M_pct", "PE_Ratio"]
    available = [c for c in display_cols if c in filtered_summary.columns]

    st.dataframe(
        filtered_summary[available].style.format({
            "Current_Price": "{:.2f}",
            "Change_1D_pct": "{:+.2f}%",
            "Change_1W_pct": "{:+.2f}%",
            "Change_1M_pct": "{:+.2f}%",
            "Change_3M_pct": "{:+.2f}%",
            "PE_Ratio": "{:.1f}",
        }).applymap(
            lambda v: "color: green" if isinstance(v, (int, float)) and v > 0
            else ("color: red" if isinstance(v, (int, float)) and v < 0 else ""),
            subset=[c for c in ["Change_1D_pct", "Change_1W_pct",
                                "Change_1M_pct", "Change_3M_pct"] if c in available],
        ),
        use_container_width=True,
        height=600,
    )

# ━━━ 탭 2: 주가 차트 ━━━
with tab_chart:
    st.subheader("주가 추이")

    if prices_df is not None:
        chart_tickers = filtered_summary["Ticker"].tolist()
        chart_prices = prices_df[prices_df["Ticker"].isin(chart_tickers)].copy()

        # 정규화 옵션
        normalize = st.checkbox("주가 정규화 (시작일 = 100)", value=True)

        if normalize:
            normalized = []
            for ticker, group in chart_prices.groupby("Ticker"):
                group = group.sort_values("Date")
                base = group["Close"].iloc[0]
                if base > 0:
                    group["Close_Norm"] = group["Close"] / base * 100
                    normalized.append(group)
            if normalized:
                chart_prices = pd.concat(normalized)
                y_col = "Close_Norm"
                y_label = "정규화 주가 (시작=100)"
            else:
                y_col = "Close"
                y_label = "주가"
        else:
            y_col = "Close"
            y_label = "주가"

        fig = px.line(
            chart_prices, x="Date", y=y_col, color="Name",
            title="선행 지표 기업 주가 추이",
            labels={"Date": "날짜", y_col: y_label, "Name": "기업"},
        )
        fig.update_layout(height=600, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("주가 데이터가 없습니다.")

# ━━━ 탭 3: 섹터 분석 ━━━
with tab_sector:
    st.subheader("섹터별 분석")

    period_col = st.selectbox(
        "기간 선택",
        ["Change_1D_pct", "Change_1W_pct", "Change_1M_pct", "Change_3M_pct"],
        format_func=lambda x: {"Change_1D_pct": "1일", "Change_1W_pct": "1주",
                                "Change_1M_pct": "1개월", "Change_3M_pct": "3개월"}[x],
    )

    # 섹터별 평균 변동률
    sector_avg = filtered_summary.groupby("Sector")[period_col].mean().reset_index()
    sector_avg.columns = ["Sector", "Avg_Change"]
    sector_avg = sector_avg.sort_values("Avg_Change", ascending=True)

    fig_sector = px.bar(
        sector_avg, x="Avg_Change", y="Sector", orientation="h",
        title=f"섹터별 평균 변동률",
        labels={"Avg_Change": "평균 변동률 (%)", "Sector": "섹터"},
        color="Avg_Change",
        color_continuous_scale=["red", "gray", "green"],
        color_continuous_midpoint=0,
    )
    fig_sector.update_layout(height=400)
    st.plotly_chart(fig_sector, use_container_width=True)

    # 섹터별 기업 비교
    fig_comp = px.bar(
        filtered_summary, x="Name", y=period_col, color="Sector",
        title="기업별 변동률 비교",
        labels={"Name": "기업", period_col: "변동률 (%)"},
    )
    fig_comp.update_layout(height=500, xaxis_tickangle=-45)
    st.plotly_chart(fig_comp, use_container_width=True)

# ━━━ 탭 4: 기업 상세 ━━━
with tab_detail:
    st.subheader("기업 상세 정보")

    company_info = get_company_info()
    selected_ticker = st.selectbox(
        "기업 선택",
        filtered_summary["Ticker"].tolist(),
        format_func=lambda t: f"{t} - {company_info[t]['name']}" if t in company_info else t,
    )

    if selected_ticker:
        info = company_info.get(selected_ticker, {})
        row = filtered_summary[filtered_summary["Ticker"] == selected_ticker].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {info.get('name', selected_ticker)}")
            st.markdown(f"**티커:** {selected_ticker}")
            st.markdown(f"**섹터:** {info.get('sector', '-')}")
            st.markdown(f"**국가:** {info.get('country', '-')}")
            st.markdown(f"**선행 근거:** {info.get('reason', '-')}")

        with col2:
            st.metric("현재가", f"{row['Current_Price']:.2f} {row.get('Currency', '')}")
            mcap = row.get("Market_Cap")
            if pd.notna(mcap) and mcap:
                if mcap >= 1e12:
                    st.metric("시가총액", f"${mcap/1e12:.1f}T")
                elif mcap >= 1e9:
                    st.metric("시가총액", f"${mcap/1e9:.1f}B")
                else:
                    st.metric("시가총액", f"${mcap/1e6:.0f}M")

            pe = row.get("PE_Ratio")
            if pd.notna(pe):
                st.metric("PER", f"{pe:.1f}")

        # 개별 주가 차트
        if prices_df is not None:
            ticker_prices = prices_df[prices_df["Ticker"] == selected_ticker].sort_values("Date")
            if not ticker_prices.empty:
                fig_single = go.Figure()
                fig_single.add_trace(go.Candlestick(
                    x=ticker_prices["Date"],
                    open=ticker_prices["Open"],
                    high=ticker_prices["High"],
                    low=ticker_prices["Low"],
                    close=ticker_prices["Close"],
                    name=selected_ticker,
                ))
                fig_single.update_layout(
                    title=f"{info.get('name', selected_ticker)} 주가 차트",
                    height=400, xaxis_rangeslider_visible=False,
                )
                st.plotly_chart(fig_single, use_container_width=True)

# ━━━ 탭 5: CSV 다운로드 ━━━
with tab_download:
    st.subheader("💾 데이터 다운로드")
    st.markdown("원하는 데이터를 CSV 파일로 다운로드하세요.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 기업 요약 데이터")
        st.markdown("현재가, 변동률, 시가총액, PER 등")
        csv_summary = filtered_summary.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 요약 데이터 다운로드 (CSV)",
            data=csv_summary,
            file_name=f"leading_companies_summary_{datetime.date.today()}.csv",
            mime="text/csv",
        )

    with col2:
        if prices_df is not None:
            st.markdown("#### 주가 히스토리 데이터")
            st.markdown("일별 시가, 고가, 저가, 종가, 거래량")
            chart_tickers = filtered_summary["Ticker"].tolist()
            filtered_prices = prices_df[prices_df["Ticker"].isin(chart_tickers)]
            csv_prices = filtered_prices.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 주가 데이터 다운로드 (CSV)",
                data=csv_prices,
                file_name=f"leading_companies_prices_{datetime.date.today()}.csv",
                mime="text/csv",
            )

    st.markdown("---")

    st.markdown("#### 전체 기업 목록 (메타데이터)")
    meta_df = pd.DataFrame(LEADING_COMPANIES)
    csv_meta = meta_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 기업 목록 다운로드 (CSV)",
        data=csv_meta,
        file_name="leading_companies_list.csv",
        mime="text/csv",
    )
