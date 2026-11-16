# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部純路由分發中心（精準串接您專案內原本就有的獨立子模組檔案）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_announcement_banner(engine):
    """渲染全域企業公告橫幅"""
    announcement_text = "📢 【全廠公告】裕豐電機工業 SaaS ERP 系統運行中。請各工程師與外勤人員確實完成案場 GPS 打卡與每日施工日報填寫。"
    if engine is not None:
        try:
            df_ann = pd.read_sql("SELECT content FROM sys_announcements WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 1", con=engine)
            if not df_ann.empty:
                announcement_text = f"📢 {df_ann.iloc[0]['content']}"
        except Exception:
            pass
    st.info(announcement_text)

def show(engine=None, lang="繁體中文", **kwargs):
    # 渲染頂部公告橫幅
    render_announcement_banner(engine)

    # 初始化工程部內部子路由狀態
    if 'eng_sub_view' not in st.session_state:
        st.session_state['eng_sub_view'] = 'overview'

    # 如果點擊進入了某個專區，上方提供返回總覽按鈕
    if st.session_state.get('eng_sub_view') != 'overview':
        if st.button("⬅️ 返回工程部總覽戰情", key="back_to_eng_overview"):
            st.session_state['eng_sub_view'] = 'overview'
            st.rerun()
        st.markdown("---")

    current_sub = st.session_state['eng_sub_view']

    # 1. 👑 工程部總覽（戰情儀表板與四大直覺分類大卡片）
    if current_sub == 'overview':
        st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
        st.caption("全廠工程案場執行戰情室與直覺化功能導覽。")

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("進行中案場", "12 案", "🟢 正常")
        with col2: st.metric("今日現場出勤", "86 人", "包含點工 18 人")
        with col3: st.metric("進度落後警示", "1 案", "需主管介入")
        with col4: st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

        st.markdown("---")
        st.markdown("##### 📌 工程部近期異常警示與進度追蹤")
        warning_df = pd.DataFrame({
            "日期": ["2026-11-16", "2026-11-15", "2026-11-14"],
            "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
            "案場名稱": ["西寧廠二期配電盤擴建", "平陽工業區廠房機電統包", "隆安省光電園區變壓器"],
            "事件類型": ["材料超支警示", "進度落後 5%", "設備驗收待簽認"],
            "處理狀態": ["🔴 待主管審核", "🟡 趕工中", "✅ 已改善"]
        })
        st.dataframe(warning_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 📂 工程部四大核心分類專區")
        
        cols = st.columns(4)
        eng_sections = [
            {"id": "field", "name": "🛠️ 現場工程", "desc": "每日施工日報表、點工點料登記與突發緊急派工。"},
            {"id": "design", "name": "📐 設計圖庫", "desc": "配電盤電氣與機構設計圖面版本控制與審查。"},
            {"id": "attendance", "name": "⏱️ 考勤打卡", "desc": "外勤師傅 GPS 圍籬即時打卡與出勤足跡紀錄。"},
            {"id": "fatsat", "name": "🧪 驗收報告", "desc": "FAT 廠內出廠測試與 SAT 現場驗收簽認報告。"}
        ]
        
        for idx, sec in enumerate(eng_sections):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"#### {sec['name']}")
                    st.caption(sec['desc'])
                    if st.button("進入專區 ➡️", key=f"btn_eng_sec_{sec['id']}", use_container_width=True, type="primary"):
                        st.session_state['eng_sub_view'] = sec['id']
                        st.rerun()

        st.markdown("")
        c_pnl1, c_pnl2 = st.columns(2)
        with c_pnl1:
            with st.container(border=True):
                st.markdown("#### 📈 專案損益與預算控管")
                st.caption("工程專案成本歸屬、外包工資與毛利分析。")
                if st.button("進入損益專區 ➡️", key="btn_pnl_sec", use_container_width=True):
                    st.session_state['eng_sub_view'] = 'pnl'
                    st.rerun()
        with c_pnl2:
            with st.container(border=True):
                st.markdown("#### 📋 專案報價追蹤")
                st.caption("投標報價、BOM 成本估算與管線進度。")
                if st.button("進入報價專區 ➡️", key="btn_quote_sec", use_container_width=True):
                    st.session_state['eng_sub_view'] = 'quote'
                    st.rerun()

    # 2. 進入各專區後的頂部按鈕導覽列與子模組轉發（直接對接您專案內的既有檔案）
    else:
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            if st.button("🛠️ 現場工程", use_container_width=True, type="primary" if current_sub == 'field' else "secondary"):
                st.session_state['eng_sub_view'] = 'field'; st.rerun()
        with b2:
            if st.button("📐 設計圖庫", use_container_width=True, type="primary" if current_sub == 'design' else "secondary"):
                st.session_state['eng_sub_view'] = 'design'; st.rerun()
        with b3:
            if st.button("⏱️ 考勤打卡", use_container_width=True, type="primary" if current_sub == 'attendance' else "secondary"):
                st.session_state['eng_sub_view'] = 'attendance'; st.rerun()
        with b4:
            if st.button("🧪 驗收報告", use_container_width=True, type="primary" if current_sub == 'fatsat' else "secondary"):
                st.session_state['eng_sub_view'] = 'fatsat'; st.rerun()
        with b5:
            if st.button("📈 專案損益", use_container_width=True, type="primary" if current_sub == 'pnl' else "secondary"):
                st.session_state['eng_sub_view'] = 'pnl'; st.rerun()
        with b6:
            if st.button("📋 專案報價", use_container_width=True, type="primary" if current_sub == 'quote' else "secondary"):
                st.session_state['eng_sub_view'] = 'quote'; st.rerun()

        st.markdown("---")

        # 🌟 直接調用您原本就已經建好的獨立檔案
        if current_sub == 'field':
            st.markdown("#### 🛠️ 現場工程日常作業管理中心")
            # 呼叫現有的施工日報與緊急派工檔案
            try:
                from modules.engineering import field_daily_report
                if hasattr(field_daily_report, "show"):
                    field_daily_report.show(engine=engine, lang=lang, **kwargs)
                elif hasattr(field_daily_report, "render"):
                    field_daily_report.render(engine, lang=lang)
            except Exception as e:
                st.info(f"正在載入施工日報模組: {e}")

            st.markdown("---")
            with st.expander("🚨 突發事故與緊急維修派工中心 (非日常狀況專用)", expanded=False):
                try:
                    from modules.engineering import emergency_dispatch
                    if hasattr(emergency_dispatch, "show"):
                        emergency_dispatch.show(engine=engine, lang=lang, **kwargs)
                    elif hasattr(emergency_dispatch, "render"):
                        emergency_dispatch.render(engine, lang=lang)
                except Exception as e:
                    st.info(f"正在載入緊急派工模組: {e}")

        elif current_sub == 'design':
            st.markdown("#### 📐 配電盤電氣與機構設計圖庫")
            st.info("💡 專為廠內設計人員打造：上傳與檢閱 AutoCAD / 3D 機構圖面、審查電氣迴路圖與版本控制。")
            # 如果有專屬的設計圖庫檔案可在此呼叫

        elif current_sub == 'attendance':
            try:
                from modules.engineering import field_gps_attendance
                if hasattr(field_gps_attendance, "show"):
                    field_gps_attendance.show(engine=engine, lang=lang, **kwargs)
                elif hasattr(field_gps_attendance, "render"):
                    field_gps_attendance.render(engine, lang=lang)
                else:
                    st.info("⏱️ 正在載入 GPS 外勤打卡模組...")
            except Exception as e:
                st.markdown("#### ⏱️ 外勤師傅考勤與 GPS 圍籬打卡")
                st.info(f"載入提示: {e}")

        elif current_sub == 'fatsat':
            try:
                from modules.engineering import fat_sat_testing
                if hasattr(fat_sat_testing, "show"):
                    fat_sat_testing.show(engine=engine, lang=lang, **kwargs)
                elif hasattr(fat_sat_testing, "render"):
                    fat_sat_testing.render(engine, lang=lang)
                else:
                    st.info("🧪 正在載入 FAT/SAT 驗收模組...")
            except Exception as e:
                st.markdown("#### 🧪 FAT / SAT 驗收報告")
                st.info(f"載入提示: {e}")

        elif current_sub == 'pnl':
            try:
                from modules.engineering import project_pnl
                if hasattr(project_pnl, "show"):
                    project_pnl.show(engine=engine, lang=lang, **kwargs)
                elif hasattr(project_pnl, "render"):
                    project_pnl.render(engine, lang=lang)
            except Exception as e:
                st.info(f"載入專案損益模組提示: {e}")

        elif current_sub == 'quote':
            try:
                from modules.engineering import gineering_pipeline
                if hasattr(gineering_pipeline, "show"):
                    gineering_pipeline.show(engine=engine, lang=lang, **kwargs)
                elif hasattr(gineering_pipeline, "render"):
                    gineering_pipeline.render(engine, lang=lang)
            except Exception as e:
                st.info(f"載入專案報價模組提示: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
