# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部主控台（主管總覽與現場作業分流架構）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
    st.caption("主管決策戰情總覽與各專業作業模組分流管理。")

    # 頂部切換：讓「工程部總覽（主管用）」與「各項現場/專屬作業功能」明確分開
    main_tab = st.radio(
        "選擇檢視模式 / Select View Mode:",
        ["👑 工程部總覽（主管決策戰情）", "📋 現場作業與各專屬功能模組"],
        horizontal=True
    )

    if "👑 工程部總覽" in main_tab:
        st.markdown("---")
        st.markdown("#### 📊 領導決策：全廠工程案場執行與損益戰情")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("進行中案場", "12 案", "🟢 正常")
        with col2:
            st.metric("今日現場出勤", "86 人", "包含點工 18 人")
        with col3:
            st.metric("進度落後警示", "1 案", "需主管介入")
        with col4:
            st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

        st.markdown("##### 🏗️ 各工業區主要案場與毛利進度總表")
        project_data = pd.DataFrame({
            "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
            "案場名稱": ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"],
            "負責經理": ["陳志豪", "阮文雄", "林建良"],
            "合約金額 (VND)": ["12,500,000,000", "15,200,000,000", "8,400,000,000"],
            "預估毛利率": ["24.4%", "21.0%", "19.5%"],
            "狀態": ["🟢 正常獲利", "🟡 需留意", "🟢 正常獲利"]
        })
        st.dataframe(project_data, use_container_width=True, hide_index=True)

        # 主管專用快捷進入區
        st.markdown("---")
        st.markdown("##### 🔍 主管快速稽核與損益追蹤")
        if st.button("📈 深入檢視《工程專案損益與預算控管》詳情 ➡️", type="primary"):
            try:
                from modules.engineering import project_pnl
                project_pnl.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入損益模組失敗: {e}")

    else:
        st.markdown("---")
        st.markdown("#### 🧩 現場作業與各專屬職位功能分流")
        st.info("💡 依據不同職務（設計人員、外勤師傅、現場工程師）指派對應作業畫面，落實權責劃分。")

        sub_func = st.selectbox(
            "選擇要操作的作業功能：",
            [
                "🚨 緊急維修派工與事故公告",
                "📈 工程專案損益與預算控管",
                "📋 專案報價與管線追蹤",
                "🧪 FAT/SAT 廠內與現場測試驗收",
                "📝 施工日報表與點工點料登記",
                "📍 外勤師傅 GPS 圍籬即時打卡",
                "📐 配電盤電氣與機構設計圖庫 (設計人員專用)"
            ]
        )

        st.markdown("---")

        if "緊急維修" in sub_func:
            try:
                from modules.engineering import emergency_dispatch
                emergency_dispatch.show(engine=engine, lang=lang, **kwargs)
            except Exception:
                st.markdown("#### 🚨 緊急維修派工與事故公告通知中心")
                st.info("快速發布緊急事故公告並指派工程師前往外部廠商/案場維修。")

        elif "專案損益" in sub_func:
            try:
                from modules.engineering import project_pnl
                project_pnl.show(engine=engine, lang=lang, **kwargs)
            except Exception:
                st.info("📈 【工程專案損益與預算控管】載入中...")

        elif "設計圖庫" in sub_func:
            st.markdown("#### 📐 配電盤電氣與機構設計圖庫 (設計人員專用)")
            st.info("💡 專為廠內設計人員打造：上傳與檢閱 AutoCAD / 3D 機構圖面、審查電氣迴路圖與版本控制。")
            
            design_df = pd.DataFrame({
                "圖面編號": ["DWG-2026-501", "DWG-2026-502", "DWG-2026-503"],
                "專案名稱": ["西寧廠二期總配電盤 (MSB)", "平陽廠自動控制盤 (PLC)", "隆安廠變壓器二次側箱"],
                "設計版本": ["Rev.02", "Rev.01", "Rev.03"],
                "負責設計師": ["張工程師", "李工程師", "王工程師"],
                "審查狀態": ["✅ 主管已核准", "⏳ 審查中", "✅ 客戶已簽認"]
            })
            st.dataframe(design_df, use_container_width=True, hide_index=True)

        elif "FAT/SAT" in sub_func:
            st.markdown("#### 🧪 FAT / SAT 測試驗收管理")
            st.info("管理工廠出廠測試 (FAT) 與現場驗收測試 (SAT) 紀錄與客戶簽認單。")

        elif "施工日報" in sub_func:
            st.markdown("#### 📋 施工日報表與點工點料登記")
            st.info("每日記錄施工現場點工數、耗用材料與施工進度。")

        elif "GPS" in sub_func:
            st.markdown("#### 📍 外勤師傅 GPS 圍籬即時打卡")
            st.info("記錄外勤人員抵達案場與廠商處的 GPS 坐標打卡狀態。")

        else:
            st.markdown(f"#### 📌 {sub_func}")
            st.info(f"【{sub_func}】功能模組建置中...")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
