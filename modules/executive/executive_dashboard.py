# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室營運與決策戰情室（頂部直接呈現應收應付、原料行情與行程筆記）
# ==========================================

import streamlit as st
import datetime
import pandas as pd

def render_executive_main(engine=None, lang="繁體中文", **kwargs):
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

    # 2. 原物料與金屬即時價格走勢（直接置頂，免點選單）
    st.markdown("### 📈 LME 原料與金屬即時價格行情")
    col_mat1, col_mat2 = st.columns([2, 1])
    with col_mat1:
        raw_material_data = pd.DataFrame({
            "原物料項目 (Material)": ["LME 銅價 (Copper)", "鋁錠 (Aluminum)", "冷軋鋼板 (SPCC)", "絕緣材料 (Insulation)"],
            "即時價格行情": ["$9,240 / 噸", "$2,450 / 噸", "$32.5 / kg", "$14.2 / kg"],
            "週漲跌幅": ["+1.8% 📈", "-0.4% 📉", "+0.5% 📈", "持平"],
            "AI 採購建議": ["分批建倉", "觀望", "維持安全庫存", "正常採購"]
        })
        st.dataframe(raw_material_data, use_container_width=True, hide_index=True)
    with col_mat2:
        with st.container(border=True):
            st.markdown("#### 💡 AI 採購快訊")
            st.info("近期銅價高檔震盪，建議西寧廠高低壓配電盤母線排需求採分批鎖價。")

    st.markdown("---")

    # 3. 秘書與副總回報之重要行程 / 商會 / 動土典禮
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

    # 4. 底部保留專業子模組切換（供需要看細節時使用）
    st.markdown("### 🔍 深度營運與政策分析模組")
    sub_option = st.selectbox(
        "📌 選擇專業分析模組",
        [
            "1. 原料市場行情與外匯基準明細",
            "2. 完整損益表與會計報表 (Thông tư 200)",
            "3. 工程專案進度與現場狀態追蹤",
            "4. 越南政府政策與法規動態速遞"
        ],
        label_visibility="collapsed"
    )

    if "1. 原料" in sub_option:
        try:
            from modules.executive import commodities_fx
            if hasattr(commodities_fx, "show"):
                commodities_fx.show(engine=engine, lang=lang, **kwargs)
        except Exception:
            pass
    elif "2. 財務" in sub_option:
        try:
            from modules.executive import financials_pl
            if hasattr(financials_pl, "show"):
                financials_pl.show(engine=engine, lang=lang, **kwargs)
        except Exception:
            pass
    elif "3. 工程" in sub_option:
        try:
            from modules.executive import project_progress
            if hasattr(project_progress, "show"):
                project_progress.show(engine=engine, lang=lang, **kwargs)
        except Exception:
            pass
    elif "4. 越南" in sub_option:
        try:
            from modules.executive import vietnam_policy
            if hasattr(vietnam_policy, "show"):
                vietnam_policy.show(engine=engine, lang=lang, **kwargs)
        except Exception:
            pass


def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
