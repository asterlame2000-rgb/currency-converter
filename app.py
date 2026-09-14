import streamlit as st
import yfinance as yf

st.title("即時匯率轉換器")

# 建立幣別選項
currencies = ['TWD', 'USD', 'JPY', 'EUR', 'GBP']
col1, col2 = st.columns(2)

with col1:
    base_currency = st.selectbox("從", currencies, index=1)
    amount = st.number_input("金額", min_value=0.0, value=100.0)

with col2:
    target_currency = st.selectbox("轉換為", currencies, index=0)

if st.button("計算匯率"):
    if base_currency == target_currency:
        st.success(f"{amount} {base_currency} = {amount} {target_currency}")
    else:
        # yfinance 匯率代碼格式，例如 USDTWD=X
        ticker = f"{base_currency}{target_currency}=X"
        try:
            data = yf.Ticker(ticker)
            # 取得最新收盤價
            current_price = data.history(period="1d")['Close'].iloc[-1]
            result = amount * current_price
            st.success(f"{amount} {base_currency} = {result:.4f} {target_currency}")
        except Exception as e:
            st.error("無法取得匯率資料，請稍後再試。")