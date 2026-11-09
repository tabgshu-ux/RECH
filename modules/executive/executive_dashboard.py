# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室營運與決策戰情室（直接整合即時 API 原料、匯率與秘書行程）
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

    # =========================================================================
    # 2. 直接載入並呼叫您寫好的 commodities_fx 模組（內含 API 即時銅價與美金/新台幣/越盾匯率換算）
    # =========================================================================
    try:
        from modules.executive import commodities_fx
        if hasattr(commodities_fx, "show"):
            commodities_fx.show(engine=engine, lang=lang, **kwargs)
        else:
            st.warning("⚠️ 原料與匯率模組載入異常 (找不到 show 函式)")
    except Exception as e:
        st.error(f"⚠️ 載入原料與匯率模組發生錯誤: {e}")

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

    # 4. 底部保留其他專業分析模組切換
    st.markdown("### 🔍 其他高階經營分析模組")
    sub_option = st.selectbox(
        "📌 選擇專業分析模組",
        [
            "2. 完整損益表與會計報表 (Thông tư 200)",
            "3. 工程專案進度與現場狀態追蹤",
            "4. 越南政府政策與法規動態速遞"
        ],
        label_visibility="collapsed"
    )

    if "2. 財務" in sub_option:
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
