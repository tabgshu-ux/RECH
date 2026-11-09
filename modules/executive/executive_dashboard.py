import streamlit as st
import datetime
import importlib

# 嘗試導入總經理室底下的 4 個獨立子功能模組（具備防呆機制，若尚未建立也不會崩潰）
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
    st.title("📈 裕豐電機工業 - 總經理室營運與財務戰情室")
    st.caption("即時監控工程專案、原料與外匯市場行情、會計財務報表及越南法規動態。")

    # 頂部全公司公告欄提示
    st.info(f"📢 **營運提示**：當前系統時間為 {datetime.date.today()}，各部門營運與簽核流程正常運作中。")

    # 子功能選擇選單（對應 4 個獨立模組）
    sub_option = st.selectbox(
        "選擇總經理室功能項目",
        [
            "1. 原料市場行情與外匯基準",
            "2. 財務與損益摘要 (AR / AP 與財報)",
            "3. 工程專案進度與現場狀態追蹤",
            "4. 越南政府政策與法規動態速遞"
        ]
    )

    st.markdown("---")

    # 依據選擇動態渲染對應的子模組畫面（加強防呆與例外處理）
    if "1. 原料" in sub_option:
        if commodities_fx and hasattr(commodities_fx, "show"):
            commodities_fx.show(engine=engine, lang=lang, **kwargs)
        else:
            st.info("📊 【原料市場行情與外匯基準】模組準備中...")
            
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

# 確保所有外部呼叫的函數名稱都能順暢對應，絕對不會再發生找不到方法的錯誤！
def render_executive_dashboard_page(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_executive_main(engine=engine, lang=lang, **kwargs)
