# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室營運戰情與決策中心（移除重複標題，極致精簡版面）
# ==========================================

import streamlit as st
import datetime
import importlib

try:
    from modules.executive import commodities_fx
except ImportError:
    commodities_fx = None

try:
    from modules.executive import financials_pl
except ImportError:
    financials_pl = None

try:
    from modules.executive import project_progress
except ImportError:
    project_progress = None

try:
    from modules.executive import vietnam_policy
except ImportError:
    vietnam_policy = None


def render_executive_main(engine=None, lang="繁體中文", **kwargs):
    # 直接以次標題顯示戰情中心名稱，不重複顯示「總經理室」字樣
    st.markdown("#### 📊 營運與決策戰情中心")
    st.caption(f"系統時間: {datetime.date.today()} | 營運與簽核正常運作")

    # =========================================================================
    # 🌟 總經理專屬設定（預設收合，不佔空間）
    # =========================================================================
    with st.expander("⚙️ 【總經理專屬設定】自訂戰情顯示模組與行程筆記", expanded=False):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            show_market = st.checkbox("📈 股市、原料與外匯行情", value=True)
            show_finance = st.checkbox("💰 財務損益與 AR/AP 摘要", value=True)
        with col_s2:
            show_project = st.checkbox("🛠️ 工程專案進度與現場狀態", value=True)
            show_schedule = st.checkbox("📅 秘書/副總行程筆記 (動土/商會)", value=True)

    # =========================================================================
    # 📅 秘書與副總回報之重要行程 / 商會 / 動土典禮專區
    # =========================================================================
    if 'show_schedule' not in locals() or show_schedule:
        with st.expander("📅 秘書室回報：近期重要行程與工地動土、商會集會", expanded=True):
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

    # =========================================================================
    # 📊 核心功能選擇選單
    # =========================================================================
    sub_option = st.selectbox(
        "📌 選擇專業分析模組",
        [
            "1. 原料市場行情、股市與外匯基準",
            "2. 財務與損益摘要 (AR / AP 與財報)",
            "3. 工程專案進度與現場狀態追蹤",
            "4. 越南政府政策與法規動態速遞"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # 依據選擇動態渲染對應子模組
    if "1. 原料" in sub_option:
        if commodities_fx and hasattr(commodities_fx, "show"):
            commodities_fx.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("📊 【原料市場行情與股市外匯基準】模組準備中...")
            
    elif "2. 財務" in sub_option:
        if financials_pl and hasattr(financials_pl, "show"):
            financials_pl.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("💰 【財務與損益摘要】模組準備中...")
            
    elif "3. 工程" in sub_option:
        if project_progress and hasattr(project_progress, "show"):
            project_progress.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("🛠️ 【工程專案進度】模組準備中...")
            
    elif "4. 越南" in sub_option:
        if vietnam_policy and hasattr(vietnam_policy, "show"):
            vietnam_policy.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("📰 【越南政府政策與法規動態】模組準備中...")


def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
