# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室營運與決策戰情中心（採用與管理部一致的卡片式二級導覽設計）
# ==========================================

import streamlit as st
import datetime
import pandas as pd

def render_executive_main(engine=None, lang="繁體中文", **kwargs):
    # 檢查當前總經理室內部的子模組狀態
    if 'exec_active_sub' not in st.session_state:
        st.session_state['exec_active_sub'] = None

    current_sub = st.session_state['exec_active_sub']

    # =========================================================================
    # 模式 A：若已進入特定子模組（顯示返回按鈕與對應模組內容）
    # =========================================================================
    if current_sub is not None:
        if st.button("⬅️ 返回總經理室戰情總覽", key="back_to_exec_main"):
            st.session_state['exec_active_sub'] = None
            st.rerun()

        st.markdown("---")

        # 依據選擇載入對應模組
        if current_sub == 'commodities':
            try:
                from modules.executive import commodities_fx
                if hasattr(commodities_fx, "show"):
                    commodities_fx.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入原料與外匯模組失敗: {e}")

        elif current_sub == 'financials':
            try:
                from modules.executive import financials_pl
                if hasattr(financials_pl, "show"):
                    financials_pl.show(engine=engine, lang=lang, **kwargs)
                else:
                    st.info("💰 【完整損益表與會計報表 (Thông tư 200)】模組載入中...")
            except Exception as e:
                st.error(f"載入財務報表模組失敗: {e}")

        elif current_sub == 'projects':
            try:
                from modules.executive import project_progress
                if hasattr(project_progress, "show"):
                    project_progress.show(engine=engine, lang=lang, **kwargs)
                else:
                    st.info("🛠️ 【工程專案進度與現場狀態】模組載入中...")
            except Exception as e:
                st.error(f"載入工程進度模組失敗: {e}")

        elif current_sub == 'policy':
            try:
                from modules.executive import vietnam_policy
                if hasattr(vietnam_policy, "show"):
                    vietnam_policy.show(engine=engine, lang=lang, **kwargs)
                else:
                    st.info("📰 【越南政府政策與法規動態】模組載入中...")
            except Exception as e:
                st.error(f"載入越南政策模組失敗: {e}")

        return

    # =========================================================================
    # 模式 B：總經理室首頁（頂部戰情摘要 + 秘書行程 + 卡片式二級導覽入口）
    # =========================================================================

    # 1. 頂部關鍵財務指標（AR 應收 / AP 應付未收未付金額）直接置頂
    st.markdown("#### 💰 財務與金流戰情摘要 (AR / AP)")
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(label="📊 本月營收達成率", value="94.5%", delta="+2.2%")
    with col_kpi2:
        st.metric(label="📋 應收帳款 (AR 未收)", value="18,455,000 ₫", delta="-1.5%")
    with col_kpi3:
        st.metric(label="🛒 應付帳款 (AP 未付)", value="14,200,000 ₫", delta="+5.2%")
    with col_kpi4:
        st.metric(label="⚠️ 現場安控異常", value="0 案", delta="全安規合規")

    st.markdown("---")

    # 2. 秘書與副總回報之重要行程 / 商會 / 動土典禮（卡片式資訊展示）
    with st.expander("📅 秘書室回報：近期重要行程、工地動土與商會集會", expanded=True):
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            st.markdown("**🏗️ 工程案場動土/開工：**")
            st.markdown("- 西寧廠二期配電盤車間動土：`2026/11/15 10:00`")
            st.markdown("- 胡志明市商辦機電案開工：`2026/11/20 吉時`")
        with col_sch2:
            st.markdown("**🤝 商會集會與拜會：**")
            st.markdown("- 平陽省台商協會例行理監事會：`2026/11/18 18:30`")
            st.markdown("- 越南機電公會產業趨勢論壇：`2026/11/25 全天`")

    st.markdown("---")

    # 3. 高階經營分析模組：卡片式二級導覽入口（完全對齊管理部風格）
    st.markdown("### 📌 總經理室專屬功能導覽與模組卡片")
    cols = st.columns(2)
    
    exec_sections = [
        {
            "id": "commodities", 
            "name": "📈 原料市場與即時外匯行情", 
            "desc": "LME 導電銅價即時 API 抓取、走勢圖、美元/新台幣與越南盾雙向匯率換算。"
        },
        {
            "id": "financials", 
            "name": "💰 完整損益表與會計報表", 
            "desc": "依據越南會計標準 (Thông tư 200) 之損益摘要、AR/AP 帳齡與會計科目清單。"
        },
        {
            "id": "projects", 
            "name": "🛠️ 工程專案進度與現場狀態", 
            "desc": "全廠各地高低壓配電盤案場、西寧與海防廠區施工進度與工安監控。"
        },
        {
            "id": "policy", 
            "name": "📰 越南政府政策與法規動態", 
            "desc": "掌握 KCN Trảng Bàng 當地勞動法規、稅務變動與外派幹部證照規範。"
        },
        {
            "id": "analytics", 
            "name": "🏗️ 工程案場與金額佔比分析", 
            "desc": "分析廠內各類型工程案場數量、合約總金額結構、平均毛利率與營收佔比分佈。"
        },
    ]

    for idx, sec in enumerate(exec_sections):
        col_target = cols[idx % 2]
        with col_target:
            with st.container(border=True):
                st.markdown(f"#### {sec['name']}")
                st.caption(sec['desc'])
                if st.button("進入該模組專區 ➡️", key=f"btn_exec_sec_{sec['id']}", use_container_width=True, type="primary"):
                    st.session_state['exec_active_sub'] = sec['id']
                    st.rerun()


def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
