# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部動態主控台（自動讀取後台勾選的掛載模組並生成分頁）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
    st.caption("統籌工程專案損益、施工日報、外勤 GPS 打卡、緊急派工與 FAT/SAT 驗收。")

    # 1. 嘗試從資料庫讀取工程部在後台實際掛載了哪些模組
    assigned_modules = []
    if engine is not None:
        try:
            query = text("""
                SELECT m.module_name 
                FROM sys_department_modules m
                JOIN sys_departments d ON m.dept_code = d.dept_code
                WHERE d.dept_name_zh LIKE '%工程%' OR d.dept_code = 'eng'
            """)
            df_mods = pd.read_sql(query, con=engine)
            if not df_mods.empty:
                assigned_modules = df_mods["module_name"].tolist()
        except Exception:
            pass

    # 如果資料庫尚未建立或查詢不到，預設提供完整的工程部核心模組清單
    if not assigned_modules:
        assigned_modules = [
            "工程部總覽",
            "緊急維修派工與事故公告通知",
            "工程專案損益與預算控管",
            "工程專案報價與管線追蹤",
            "FAT/SAT 廠內與現場測試驗收",
            "施工日報表與點工點料登記",
            "外勤師傅 GPS 圍籬即時打卡",
            "配電盤電氣與機構設計圖庫 (設計人員專用)"
        ]

    # 2. 動態建立分頁 (Tabs)
    tab_labels = []
    for m in assigned_modules:
        # 簡化分頁名稱以便顯示
        if "總覽" in m: tab_labels.append("📊 工程總覽")
        elif "緊急" in m: tab_labels.append("🚨 緊急派工")
        elif "損益" in m: tab_labels.append("📈 專案損益")
        elif "報價" in m: tab_labels.append("📋 專案報價")
        elif "FAT" in m: tab_labels.append("🧪 FAT/SAT驗收")
        elif "日報" in m: tab_labels.append("📝 施工日報")
        elif "GPS" in m: tab_labels.append("📍 外勤打卡")
        elif "設計" in m: tab_labels.append("📐 設計圖庫")
        else: tab_labels.append(m)

    if not tab_labels:
        st.warning("⚠️ 目前工程部尚未掛載任何模組，請至系統設定的後台進行勾選。")
        return

    tabs = st.tabs(tab_labels)

    # 3. 根據分頁依序載入對應的子模組畫面
    for idx, mod_name in enumerate(assigned_modules):
        with tabs[idx]:
            if "總覽" in mod_name:
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("進行中案場", "12 案", "🟢 正常")
                with col2: st.metric("今日出勤人數", "86 人", "包含點工 18 人")
                with col3: st.metric("進度落後警示", "1 案", "需調派支援")
                with col4: st.metric("總合約金額", "325.5億 ₫", "執行率 78%")
                
                project_data = pd.DataFrame({
                    "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
                    "案場名稱": ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"],
                    "負責經理": ["陳志豪", "阮文雄", "林建良"],
                    "目前進度": ["85%", "62%", "40%"],
                    "狀態": ["🟢 正常", "🟡 需留意", "🟢 正常"]
                })
                st.dataframe(project_data, use_container_width=True, hide_index=True)

            elif "損益" in mod_name:
                try:
                    from modules.engineering import project_pnl
                    project_pnl.show(engine=engine, lang=lang, **kwargs)
                except Exception:
                    st.info("📈 【工程專案損益與預算控管】模組載入中...")

            elif "緊急" in mod_name:
                try:
                    from modules.engineering import emergency_dispatch
                    emergency_dispatch.show(engine=engine, lang=lang, **kwargs)
                except Exception:
                    st.markdown("#### 🚨 緊急維修派工與事故公告通知中心")
                    st.info("快速發布緊急事故公告並指派工程師前往外部廠商/案場維修。")

            elif "設計" in mod_name:
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

            elif "FAT" in mod_name:
                st.markdown("#### 🧪 FAT / SAT 測試驗收管理")
                st.info("管理工廠出廠測試 (FAT) 與現場驗收測試 (SAT) 紀錄與客戶簽認單。")

            elif "日報" in mod_name:
                st.markdown("#### 📋 施工日報表與點工點料登記")
                st.info("每日記錄施工現場點工數、耗用材料與施工進度。")

            elif "GPS" in mod_name:
                st.markdown("#### 📍 外勤師傅 GPS 圍籬即時打卡")
                st.info("記錄外勤人員抵達案場與廠商處的 GPS 坐標打卡狀態。")

            else:
                st.markdown(f"#### 📌 {mod_name}")
                st.info(f"【{mod_name}】功能模組建置中...")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
