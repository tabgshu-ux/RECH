# ==========================================
# 檔案路徑：modules/executive/executive_dashboard.py
# 職責：總經理室營運戰情與個人化動態儀表板（支援股市行情、財務摘要、工程進度與秘書/商會行程筆記）
# ==========================================

import streamlit as st
import datetime
import importlib

# 嘗試導入總經理室底下的獨立子功能模組（具備防呆機制）
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
    st.title("📈 裕豐電機工業 - 總經理室營運與決策戰情室")
    st.caption("即時監控工程專案、原料與股市外匯市場行情、會計財務摘要及秘書/商會行程動態。")

    # 頂部全公司公告欄提示
    st.info(f"📢 **總經理室即時提示**：當前系統時間為 {datetime.date.today()}，各部門營運與簽核流程正常運作中。")

    # =========================================================================
    # 🌟 總經理個人化戰情面板配置（動態勾選想顯示的模組與行程特快車）
    # =========================================================================
    with st.expander("⚙️ 【總經理專屬設定】自訂此戰情頁面要顯示的模組與行程筆記", expanded=False):
        st.markdown("每個總經理關注的重點不同，您可以勾選希望在戰情室優先展開的區塊：")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            show_market = st.checkbox("📈 顯示股市指數、LME 原料與外匯行情", value=True)
            show_finance = st.checkbox("💰 顯示財務損益與 AR/AP 未收未付摘要", value=True)
        with col_s2:
            show_project = st.checkbox("🛠️ 顯示工程專案進度與現場狀態", value=True)
            show_schedule = st.checkbox("📅 顯示秘書/副總行程筆記 (開工典禮、商會集會)", value=True)

    st.markdown("---")

    # =========================================================================
    # 📅 秘書與副總回報之重要行程 / 商會 / 動土典禮專區（可選顯示）
    # =========================================================================
    if 'show_schedule' in locals() and show_schedule:
        st.markdown("### 📅 秘書室回報：近期重要行程、工地動土與商會集會")
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            with st.container(border=True):
                st.markdown("#### 🏗️ 工程案場重大剪綵與動土典禮")
                st.markdown("- **西寧廠二期高低壓配電盤車間動土典禮**：預定於 `2026/11/15 (五) 上午 10:00` 舉行。")
                st.markdown("- **胡志明市商辦機電案開工典禮**：預定於 `2026/11/20 (三) 吉時` 進行。")
        with col_sch2:
            with st.container(border=True):
                st.markdown("#### 🤝 商會集會與外部重要拜會")
                st.markdown("- **平陽省台商協會例行理監事聯席會**：`2026/11/18 (一) 晚上 18:30`（地點：平陽新城大飯店）。")
                st.markdown("- **越南機電公會年度產業趨勢論壇**：`2026/11/25 (二) 全天`（總經理已列為受邀貴賓）。")
        st.markdown("---")

    # =========================================================================
    # 📊 標準 4 大模組分流與動態渲染
    # =========================================================================
    sub_option = st.selectbox(
        "📌 選擇總經理室核心功能與專業分析模組",
        [
            "1. 原料市場行情、股市與外匯基準",
            "2. 財務與損益摘要 (AR / AP 與財報)",
            "3. 工程專案進度與現場狀態追蹤",
            "4. 越南政府政策與法規動態速遞"
        ]
    )

    st.markdown("---")

    # 依據選擇動態渲染對應的子模組畫面（加強防呆與例外處理）
    if "1. 原料" in sub_option:
        if show_market:
            if commodities_fx and hasattr(commodities_fx, "show"):
                commodities_fx.show(engine=engine, lang=lang, **kwargs)
            else:
                st.info("📊 【原料市場行情與股市外匯基準】模組準備中...")
                # 預留擴充：在此處可直接整合台股/越股與 LME 銅價走勢
        else:
            st.warning("⚠️ 您目前已在上方設定中關閉了市場行情模組的顯示。")
            
    elif "2. 財務" in sub_option:
        if show_finance:
            if financials_pl and hasattr(financials_pl, "show"):
                financials_pl.show(engine=engine, lang=lang, **kwargs)
            else:
                st.info("💰 【財務與損益摘要】模組準備中...")
        else:
            st.warning("⚠️ 您目前已在上方設定中關閉了財務損益模組的顯示。")
            
    elif "3. 工程" in sub_option:
        if show_project:
            if project_progress and hasattr(project_progress, "show"):
                project_progress.show(engine=engine, lang=lang, **kwargs)
            else:
                st.info("🛠️ 【工程專案進度】模組準備中...")
        else:
            st.warning("⚠️ 您目前已在上方設定中關閉了工程專案模組的顯示。")
            
    elif "4. 越南" in sub_option:
        if vietnam_policy and hasattr(vietnam_policy, "show"):
            vietnam_policy.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("📰 【越南政府政策與法規動態】模組準備中...")


# 確保所有外部呼叫的函數名稱都能順暢對應
def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
