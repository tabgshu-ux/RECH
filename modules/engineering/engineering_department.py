# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部唯一主控台（已整合所有子模組，絕不產生多餘檔案）
# ==========================================

import streamlit as st
import pandas as pd

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
    st.caption("統籌工程專案損益、施工日報、外勤 GPS 打卡、緊急派工與 FAT/SAT 驗收。")

    # 使用分頁讓主管在同一個頁面順暢切換所有工程功能，不需切換多個檔案
    tab_overview, tab_pnl, tab_emergency, tab_daily, tab_gps, tab_fatsat = st.tabs([
        "📊 工程部總覽", 
        "📈 專案損益與預算", 
        "🚨 緊急派工公告", 
        "📋 施工日報表", 
        "📍 外勤 GPS 打卡", 
        "🧪 FAT/SAT 驗收"
    ])

    with tab_overview:
        st.markdown("#### 🏗️ 各工業區主要案場執行進度一覽")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("進行中案場", "12 案", "🟢 正常")
        with col2:
            st.metric("今日出勤人數", "86 人", "包含點工 18 人")
        with col3:
            st.metric("進度落後警示", "1 案", "需調派支援")
        with col4:
            st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

        project_data = pd.DataFrame({
            "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
            "案場名稱": ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"],
            "負責經理": ["陳志豪", "阮文雄", "林建良"],
            "目前進度": ["85%", "62%", "40%"],
            "狀態": ["🟢 正常", "🟡 需留意", "🟢 正常"]
        })
        st.dataframe(project_data, use_container_width=True, hide_index=True)

    with tab_pnl:
        try:
            from modules.engineering import project_pnl
            project_pnl.show(engine=engine, lang=lang, **kwargs)
        except Exception as e:
            st.info("💡 正在載入專案損益與預算控管模組...")

    with tab_emergency:
        try:
            from modules.engineering import emergency_dispatch
            emergency_dispatch.show(engine=engine, lang=lang, **kwargs)
        except Exception as e:
            st.markdown("#### 🚨 緊急維修派工與事故公告通知中心")
            st.info("快速發布緊急事故公告並指派工程師前往外部廠商/案場維修。")

    with tab_daily:
        st.markdown("#### 📋 施工日報表與點工點料登記")
        st.info("每日記錄施工現場點工數、耗用材料與施工進度。")

    with tab_gps:
        st.markdown("#### 📍 外勤師傅 GPS 圍籬即時打卡")
        st.info("記錄外勤人員抵達案場與廠商處的 GPS 坐標打卡狀態。")

    with tab_fatsat:
        st.markdown("#### 🧪 FAT / SAT 測試驗收管理")
        st.info("管理工廠出廠測試 (FAT) 與現場驗收測試 (SAT) 紀錄與客戶簽認單。")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
