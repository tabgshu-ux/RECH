# ==========================================
# 檔案路徑：modules/production/production_overview.py
# 職責：生產部總覽（工單排程、產線稼動率與品質檢驗）
# ==========================================

import streamlit as st
import pandas as pd

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏭 生產部總覽 (Production Department Overview)")
    st.caption("即時監控西寧廠板金、烤漆、配盤組裝產線稼動率、工單進度與物料需求 (MRP)。")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏭 執行中生產工單", "24 張", "🟢 產線運作正常")
    with col2:
        st.metric("⚡ 產線綜合稼動率", "88.5%", "📈 較上月 +4.1%")
    with col3:
        st.metric("🧪 本月良率 (FPY)", "98.2%", "符合品質規範")
    with col4:
        st.metric("📦 待出貨成品", "8 批次", "配合工程部交期")

    st.markdown("---")

    st.markdown("#### 📋 各核心產線即時負載與工單進度")
    prod_data = pd.DataFrame({
        "產線名稱": ["鈑金加工作業區", "粉體烤漆車間", "高低壓配電盤組裝線", "母線排加工區"],
        "負責組長": ["黎文特 (Le Van Thien)", "黃文明", "陳國棟", "吳俊傑"],
        "當前對應工單": ["MO-2026-101", "MO-2026-098", "MO-2026-105", "MO-2026-102"],
        "產線稼動率": ["92%", "85%", "90%", "87%"],
        "狀態": ["🟢 運作中", "🟢 運作中", "🟢 運作中", "🟡 待料中"]
    })
    st.dataframe(prod_data, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📊 生產車間物料與 MRP 協同狀況")
    st.info("💡 **MRP 系統提示**：目前高低壓配電盤組裝線之銅排原料庫存充足，系統已自動依據訂單拋轉採購建議給總務採購課。")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
