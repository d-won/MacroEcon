"""
경기 선행 기업 데이터 수집 스크립트

yfinance를 사용하여 주가·재무 데이터를 가져와 CSV로 저장.
GitHub Actions에서 매일 실행됨.
"""

import os
import datetime
import pandas as pd
import yfinance as yf

from companies import LEADING_COMPANIES, get_tickers

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def fetch_price_data(period="1y"):
    """주가 데이터 수집 (1년치 기본)"""
    tickers = get_tickers()
    print(f"Fetching price data for {len(tickers)} tickers...")

    all_data = []
    for company in LEADING_COMPANIES:
        ticker = company["ticker"]
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                print(f"  [WARN] No data for {ticker}")
                continue

            hist = hist.reset_index()
            hist["Ticker"] = ticker
            hist["Name"] = company["name"]
            hist["Sector"] = company["sector"]
            hist["Country"] = company["country"]
            all_data.append(hist)
            print(f"  [OK] {ticker} ({company['name']}): {len(hist)} rows")
        except Exception as e:
            print(f"  [ERR] {ticker}: {e}")

    if not all_data:
        print("No data fetched!")
        return pd.DataFrame()

    df = pd.concat(all_data, ignore_index=True)

    # 컬럼 정리
    cols = ["Date", "Ticker", "Name", "Sector", "Country",
            "Open", "High", "Low", "Close", "Volume"]
    available_cols = [c for c in cols if c in df.columns]
    df = df[available_cols]

    # Date를 날짜만 (시간 제거)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    return df


def fetch_summary_data():
    """기업별 요약 데이터 (현재가, 변동률, 시가총액 등)"""
    print("Fetching summary data...")
    rows = []

    for company in LEADING_COMPANIES:
        ticker = company["ticker"]
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # 최근 주가 히스토리에서 변동률 계산
            hist = stock.history(period="6mo")
            if hist.empty:
                print(f"  [WARN] No history for {ticker}")
                continue

            current_price = hist["Close"].iloc[-1]
            price_1d_ago = hist["Close"].iloc[-2] if len(hist) >= 2 else current_price
            price_1w_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else current_price
            price_1m_ago = hist["Close"].iloc[-22] if len(hist) >= 22 else current_price
            price_3m_ago = hist["Close"].iloc[-66] if len(hist) >= 66 else current_price

            row = {
                "Ticker": ticker,
                "Name": company["name"],
                "Sector": company["sector"],
                "Country": company["country"],
                "Reason": company["reason"],
                "Current_Price": round(current_price, 2),
                "Change_1D_pct": round((current_price / price_1d_ago - 1) * 100, 2),
                "Change_1W_pct": round((current_price / price_1w_ago - 1) * 100, 2),
                "Change_1M_pct": round((current_price / price_1m_ago - 1) * 100, 2),
                "Change_3M_pct": round((current_price / price_3m_ago - 1) * 100, 2),
                "Market_Cap": info.get("marketCap", None),
                "PE_Ratio": info.get("trailingPE", None),
                "52W_High": info.get("fiftyTwoWeekHigh", None),
                "52W_Low": info.get("fiftyTwoWeekLow", None),
                "Currency": info.get("currency", "USD"),
            }
            rows.append(row)
            print(f"  [OK] {ticker} ({company['name']}): ${current_price:.2f}")
        except Exception as e:
            print(f"  [ERR] {ticker}: {e}")

    return pd.DataFrame(rows)


def save_data():
    """데이터를 CSV로 저장"""
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.date.today().isoformat()

    # 1) 요약 데이터
    summary_df = fetch_summary_data()
    if not summary_df.empty:
        summary_path = os.path.join(DATA_DIR, "summary_latest.csv")
        summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
        print(f"\nSaved summary: {summary_path} ({len(summary_df)} companies)")

        # 날짜별 아카이브
        archive_path = os.path.join(DATA_DIR, f"summary_{today}.csv")
        summary_df.to_csv(archive_path, index=False, encoding="utf-8-sig")

    # 2) 주가 히스토리
    price_df = fetch_price_data()
    if not price_df.empty:
        price_path = os.path.join(DATA_DIR, "prices_latest.csv")
        price_df.to_csv(price_path, index=False, encoding="utf-8-sig")
        print(f"Saved prices: {price_path} ({len(price_df)} rows)")

    # 3) 업데이트 타임스탬프
    ts_path = os.path.join(DATA_DIR, "last_updated.txt")
    with open(ts_path, "w") as f:
        f.write(datetime.datetime.now().isoformat())

    print(f"\nData update completed: {today}")


if __name__ == "__main__":
    save_data()
