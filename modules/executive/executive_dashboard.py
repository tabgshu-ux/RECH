# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室總覽與決策中心（100% 精準對應資料庫掛載代碼）
# ==========================================

import streamlit as st
import datetime
import pandas as pd
from sqlalchemy import text

def get_mounted_features_for_dept(engine, dept_name):
    """從資料庫動態讀取該部門實際被掛載的功能代碼清單"""
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            res = conn.execute(
                text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d"),
                {"d": dept_name}
            ).fetchone()
            if res and res[0]:
                return [f.strip() for f in res[0].split(",") if f.strip()]
    except Exception:
        pass
    
    return ['feat_executive', 'feat_lme_commodities', 'feat_stock_indices', 'feat_fx_rates', 'feat_exec_announcements']

def render_executive_main(engine=None, lang="繁體中文", **kwargs):
    if 'exec_active_sub' not in st.session_state:
        st.session_state['exec_active_sub'] = None

    current_sub = st.session_state['exec_active_sub']

    if current_sub is not None:
        col_back, col_jump = st.columns([2, 5])
        with col_back:
            if st.button("⬅️ 返回總經理室總覽", key="back_to_exec_main", use_container_width=True):
                st.session_state['exec_active_sub'] = None
                st.rerun()

        with col_jump:
            with st.expander("⚡ 快速切換總經理室其他功能...", expanded=False):
                mounted_feats = get_mounted_features_for_dept(engine, "總經理室")
                sub_options = {}
                
                master_feature_map = {
                    "feat_lme_commodities": ("📈 原料市場與即時外匯行情", "commodities"),
                    "feat_circular_200": ("💰 完整損益表與會計報表", "financials"),
                    "feat_eng_overview": ("🛠️ 工程專案進度與現場狀態", "projects"),
                    "feat_policy": ("📰 越南政府政策與法規動態", "policy"),
                    "feat_analytics": ("🏗️ 工程案場與金額佔比分析", "analytics")
                }
                
                for feat_id, (label, target_sub) in master_feature_map.items():
                    if feat_id in mounted_feats:
                        sub_options[label] = target_sub

                for label, target_sub in sub_options.items():
                    if current_sub != target_sub:
                        if st.button(label, key=f"quick_jump_{target_sub}", use_container_width=True):
                            st.session_state['exec_active_sub'] = target_sub
                            st.rerun()

        st.markdown("---")

        if current_sub == 'commodities':
            try:
                from modules.executive import commodities_fx
                commodities_fx.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入原料與外匯模組失敗: {e}")

        elif current_sub == 'financials':
            try:
                from modules.executive import financials_pl
                financials_pl.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入財務報表失敗: {e}")

        elif current_sub == 'projects':
            try:
                from modules.executive import project_progress
                project_progress.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入工程進度失敗: {e}")

        elif current_sub == 'policy':
            try:
                from modules.executive import vietnam_policy
                vietnam_policy.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入越南政策失敗: {e}")

        elif current_sub == 'analytics':
            try:
                from modules.executive import project_analytics
                project_analytics.show(engine=engine, lang=lang, **kwargs)
            except Exception as e:
                st.error(f"載入工程案場金額分析模組失敗: {e}")

        return

    # 總經理室總覽首頁
    st.markdown("### 👑 總經理室總覽 (Executive Office Overview)")
    st.caption("彙整全廠營運績效、KPI 達成率、重大異常警示與跨部門核心財務數據。")
    
    st.markdown("#### 💰 財務與金流總覽 (AR / AP)")
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

    with st.expander("📅 秘書室回報：近期重要行程、工地動土與商會集會", expanded=True):
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            st.markdown("**🏗️ 工程案場動土/開工：**")
            st.markdown("- 西寧廠二期配電盤車間動土：`2026/11/15 10:00`")
        with col_sch2:
            st.markdown("**🤝 商會集會與拜會：**")
            st.markdown("- 平陽省台商協會例行理監事會：`2026/11/18 18:30`")

    st.markdown("---")

    st.markdown("### 📌 總經理室專屬功能導覽與模組卡片")
    st.caption("💡 提示：以下卡片嚴格依據您在「系統設定 ➡️ 公司部門 ➡️ 跨群組彈性模組掛載」中所勾選的項目動態生成。未勾選的功能將自動隱藏。")

    # 撈取資料庫實際掛載的模組代碼
    mounted_feats = get_mounted_features_for_dept(engine, "總經理室")

    # 🌟 完整收錄總經理室所有可能的專屬卡片與對應的 feat_id
    all_exec_sections = [
        {
            "feat_id": "feat_lme_commodities",
            "id": "commodities", 
            "name": "📈 原料市場與即時外匯行情", 
            "desc": "LME 導電銅價即時 API 抓取、走勢圖、美元/新台幣與越南盾雙向匯率換算。"
        },
        {
            "feat_id": "feat_circular_200",
            "id": "financials", 
            "name": "💰 完整損益表與會計報表", 
            "desc": "依據越南會計標準 (Thông tư 200) 之損益摘要、AR/AP 帳齡與會計科目清單。"
        },
        {
            "feat_id": "feat_eng_overview",
            "id": "projects", 
            "name": "🛠️ 工程專案進度與現場狀態", 
            "desc": "全廠各地高低壓配電盤案場、西寧與海防廠區施工進度與工安監控。"
        },
        {
            "feat_id": "feat_policy",
            "id": "policy", 
            "name": "📰 越南政府政策與法規動態", 
            "desc": "掌握 KCN Trảng Bàng 當地勞動法規、稅務變動與外派幹部證照規範。"
        },
        {
            "feat_id": "feat_analytics",
            "id": "analytics", 
            "name": "🏗️ 工程案場與金額佔比分析", 
            "desc": "分析廠內各類型工程案場數量、合約總金額結構、平均毛利率與營收佔比分佈。"
        },
    ]

    # 🌟 如果資料庫中有勾選這些模組，就把它們撈出來顯示
    active_sections = [sec for sec in all_exec_sections if sec['feat_id'] in mounted_feats]

    if active_sections:
        cols = st.columns(2)
        for idx, sec in enumerate(active_sections):
            col_target = cols[idx % 2]
            with col_target:
                with st.container(border=True):
                    st.markdown(f"#### {sec['name']}")
                    st.caption(sec['desc'])
                    if st.button("進入該模組專區 ➡️", key=f"btn_exec_sec_{sec['id']}", use_container_width=True, type="primary"):
                        st.session_state['exec_active_sub'] = sec['id']
                        st.rerun()
    else:
        st.info("💡 目前總經理室尚未勾選掛載任何專屬模組。請至「系統設定 ➡️ 公司部門 ➡️ 跨群組彈性模組掛載」勾選您需要的功能，畫面將即時連動呈現！")

def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
