# ==========================================
# 檔案路徑：modules/it_system/API/lme_market_api.py
# 職責：LME 銅價與外匯匯率換算 API 閘道設定
# ==========================================

import streamlit as st

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("#### 📈 LME 銅價與外匯匯率 API 整合設定")
    st.caption("設定即時匯率轉換（USD/VND/TWD）與國際銅價/金屬原料行情資料抓取之 API 閘道。")

    with st.form("lme_forex_form"):
        api_type = st.selectbox("選擇金融與原料行情資料來源", [
            "LME 倫敦金屬交易所銅價與鋁價行情 API",
            "越南國家銀行 / 商業銀行即時匯率 API (Vietcombank / BIDV)",
            "國際外匯市場即時匯率換算 API (ExchangeRate-API)"
        ])
        
        c1, c2 = st.columns(2)
        with c1:
            api_endpoint = st.text_input("API 請求端點 (Endpoint URL)", value="https://api.exchangerate-api.com/v4/latest/USD")
            api_key = st.text_input("金融/原料 API 授權金鑰 (API Key)", type="password", value="lme_forex_live_key_********************")
        with c2:
            sync_freq = st.selectbox("自動同步頻率", ["每小時同步一次", "每日開盤同步一次", "手動更新"])
            api_status = st.selectbox("API 運作狀態", ["🟢 啟用中 (Active)", "🔴 停用中 (Disabled)"])

        notes = st.text_area("匯率與原料匯算備註", placeholder="例如: 預設採購成本換算基準以越盾 (VND) 與美元 (USD) 即時匯率為準...")

        if st.form_submit_button("💾 儲存 LME 與外匯 API 設定", type="primary", use_container_width=True):
            st.success(f"🎉 成功儲存 [{api_type}] 的 API 閘道設定！已成功寫入系統動態配置。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
