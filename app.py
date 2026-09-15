import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 版面拓寬與標題設定
st.set_page_config(page_title="外匯分析與回測系統", layout="wide")

# 2. 強制設定淺色背景與字體顏色
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FAFAFA;
        color: #333333;
    }
    .css-1d391kg {
        background-color: #F0F2F6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("外匯分析與回測系統")
# 修改頁面名稱為外匯交易指南
page = st.sidebar.selectbox("選擇功能", ["外匯交易指南", "一年期波動分析", "五年期策略回測"])

currencies = ['USD', 'JPY', 'EUR', 'GBP', 'AUD', 'CAD', 'CHF']
target = st.sidebar.selectbox("選擇外幣 (兌換台幣)", currencies)
ticker = f"{target}TWD=X"

if page == "外匯交易指南":
    st.header("外匯交易基礎知識")
    
    st.subheader("1. 什麼是貨幣對？")
    st.write(f"外匯交易是成對進行的。以目前選擇的 **{target}/TWD** 為例，{target} 是「基礎貨幣」，TWD 是「計價貨幣」。報價代表需要多少台幣才能換取一單位的 {target}。外匯交易的核心在於判斷兩國貨幣的相對強弱。")
    
    st.subheader("2. 什麼是均線 (SMA)？")
    st.write("均線是將過去一段時間的收盤價平均，用來過濾短期的價格雜訊，觀察長期趨勢。")
    st.markdown("""
    *   **短期均線**：反映近期市場情緒，變動較快。
    *   **長期均線**：反映長線歷史趨勢，變動較慢。
    """)
    
    st.subheader("3. 雙均線交易策略")
    st.markdown("""
    *   **買點 (黃金交叉)**：短期均線向上突破長期均線，暗示上漲動能轉強。
    *   **賣點 (死亡交叉)**：短期均線向下跌破長期均線，暗示下跌風險增加。
    """)
    
    st.subheader("4. 為什麼要看最大虧損幅度？")
    st.write("投資不能只看最終利潤。「最大虧損幅度 (Max Drawdown)」衡量策略在歷史中最差情況下，資金從最高點跌至最低點的比例。這是評估個人風險承受度最重要的指標。")

elif page == "一年期波動分析":
    st.subheader(f"{target}/TWD 過去一年匯率波動")
    try:
        data_1y = yf.Ticker(ticker).history(period="1y")
        if not data_1y.empty:
            current_price = data_1y['Close'].iloc[-1]
            st.metric("當前匯率", f"{current_price:.4f}")
            
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(data_1y.index, data_1y['Close'], color='#1f77b4', linewidth=1.5)
            ax.set_title(f"{target}/TWD 1-Year Trend", color='#333333')
            ax.grid(True, linestyle='--', alpha=0.6)
            fig.patch.set_facecolor('#FAFAFA')
            ax.set_facecolor('#FFFFFF')
            st.pyplot(fig)
            
            high_1y = data_1y['High'].max()
            low_1y = data_1y['Low'].min()
            
            col1, col2 = st.columns(2)
            col1.metric("近一年最高價", f"{high_1y:.4f}")
            col2.metric("近一年最低價", f"{low_1y:.4f}")
    except Exception as e:
        st.error(f"系統發生錯誤，詳細資訊：{e}")

elif page == "五年期策略回測":
    st.subheader("雙均線交叉策略回測")
    initial_capital = 100000.0

    # 運用分欄將控制項與圖表整合至同一視角
    col_settings, col_chart = st.columns([1, 2.5])
    
    with col_settings:
        st.info("調整均線參數以觀察圖表與利潤變化")
        short_window = st.slider("短期均線 (日)", 5, 20, 10)
        long_window = st.slider("長期均線 (日)", 20, 60, 30)

    try:
        data_5y = yf.Ticker(ticker).history(period="5y")
        if not data_5y.empty:
            data_5y['SMA_Short'] = data_5y['Close'].rolling(window=short_window).mean()
            data_5y['SMA_Long'] = data_5y['Close'].rolling(window=long_window).mean()
            
            data_5y['Signal'] = 0
            data_5y.loc[data_5y['SMA_Short'] > data_5y['SMA_Long'], 'Signal'] = 1
            data_5y['Position'] = data_5y['Signal'].diff()
            
            data_5y['Daily_Return'] = data_5y['Close'].pct_change()
            data_5y['Strategy_Return'] = data_5y['Signal'].shift(1) * data_5y['Daily_Return']
            data_5y['Portfolio_Value'] = initial_capital * (1 + data_5y['Strategy_Return'].fillna(0)).cumprod()
            
            data_5y['Peak'] = data_5y['Portfolio_Value'].cummax()
            data_5y['Drawdown'] = (data_5y['Portfolio_Value'] - data_5y['Peak']) / data_5y['Peak']
            max_drawdown = data_5y['Drawdown'].min() * 100
            
            final_value = data_5y['Portfolio_Value'].iloc[-1]
            profit = final_value - initial_capital
            
            # 列出指定之四項核心數據
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("初始投入資金", f"{initial_capital:,.0f}")
            m2.metric("最終總資金", f"{final_value:,.2f}")
            m3.metric("五年期最終總利潤", f"{profit:,.2f}")
            m4.metric("最大虧損幅度", f"{max_drawdown:.2f}%")
            
            with col_chart:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(data_5y.index, data_5y['Close'], label='Price', alpha=0.4, color='gray')
                ax.plot(data_5y.index, data_5y['SMA_Short'], label='Short SMA', alpha=0.8, color='#ff7f0e')
                ax.plot(data_5y.index, data_5y['SMA_Long'], label='Long SMA', alpha=0.8, color='#1f77b4')
                
                buy_signals = data_5y[data_5y['Position'] == 1]
                sell_signals = data_5y[data_5y['Position'] == -1]
                ax.scatter(buy_signals.index, buy_signals['SMA_Short'], marker='^', color='#2ca02c', label='Buy', s=100)
                ax.scatter(sell_signals.index, sell_signals['SMA_Short'], marker='v', color='#d62728', label='Sell', s=100)
                
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.6)
                fig.patch.set_facecolor('#FAFAFA')
                ax.set_facecolor('#FFFFFF')
                ax.tick_params(colors='#333333')
                st.pyplot(fig)
            
            st.write("### 交易紀錄")
            trades = data_5y[data_5y['Position'].isin([1, -1])].copy()
            trades['Action'] = trades['Position'].map({1: '買進', -1: '賣出'})
            trades = trades[['Action', 'Close']]
            trades.columns = ['動作', '執行匯率']
            trades.index = trades.index.strftime('%Y-%m-%d')
            st.dataframe(trades, use_container_width=True)
            
    except Exception as e:
        st.error(f"系統發生錯誤，詳細資訊：{e}")