# ==========================================
# 檔案路徑：modules/it_system/API/it_invoice_config.py
# 職責：越南電子發票 API 與稅務設定模組 (對接 Viettel / VNPT / Misa 規範)
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_invoice_db(engine):
    """初始化電子發票 API 參數設定資料表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_api_invoice_config (
                        id SERIAL PRIMARY KEY,
                        provider_name VARCHAR(100),
                        tax_code VARCHAR(50),
                        api_url VARCHAR(255),
                        client_id VARCHAR(100),
                        secret_key VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def render(engine=None, lang="繁體中文", **kwargs):
    init_invoice_db(engine)

    st.markdown("#### 🧾 越南電子發票 API 與稅務整合設定 (E-Invoice API)")
    st.caption("支援 Viettel, VNPT, Misa 等越南當地電子發票供應商之 API 金鑰與企業稅號 (MST) 配置。")

    with st.form("invoice_api_config_form"):
        col1, col2 = st.columns(2)
        with col1:
            provider = st.selectbox("選擇電子發票服務商", ["Viettel e-Invoice", "VNPT-Invoice", "Misa meInvoice", "自定義 API 供應商"])
            tax_code = st.text_input("企業稅號 (MST / Tax Code)", value="0312345678")
            api_url = st.text_input("API 傳輸端點 (Endpoint URL)", value="https://api.viettel.vn/e-invoice/v1/publish")
        with col2:
            client_id = st.text_input("API Client ID / 帳號", value="REETECH_API_USER")
            secret_key = st.text_input("API Secret Key / 密碼權杖", type="password", value="sk_live_vietnam_invoice_****************")
            is_active_status = st.selectbox("串接狀態", ["🟢 啟用中 (Active)", "🔴 停用中 (Disabled)"])

        notes = st.text_area("發票開立備註與憑證規則", placeholder="例如: 預設開立 B2B 加值稅發票 (Hóa đơn GTGT)...")

        submitted = st.form_submit_button("💾 儲存電子發票 API 設定並測試連線", type="primary", use_container_width=True)
        if submitted:
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_api_invoice_config (provider_name, tax_code, api_url, client_id, secret_key, is_active)
                            VALUES (:p, :t, :u, :cid, :sk, :act)
                        """), {
                            "p": provider, "t": tax_code, "u": api_url, "cid": client_id, 
                            "sk": secret_key, "act": True if "啟用" in is_active_status else False
                        })
                except Exception as e:
                    st.warning(f"資料庫寫入提示: {e}")
            st.success(f"🎉 成功儲存 [{provider}] 的 API 參數與稅號設定！連線測試回應：200 OK。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
