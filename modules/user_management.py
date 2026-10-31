import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; font-weight: 700 !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label, .stMarkdown { font-size: 0.9rem !important; }
    .stDataFrame { overflow-x: auto; width: 100% !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; font-size: 1rem !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

def get_department_module_tree():
    """全域共享的部門與子功能樹狀結構"""
    if "custom_department_module_tree" not in st.session_state:
        st.session_state.custom_department_module_tree = {
            "📈 總經理室 (Executive Office)": [
                "🔴 原料價格與 Gemini 智慧採購顧問",
                "📊 財務類顯示資料 (AR/AP & P&L)",
                "⚡ 工程專案進度與現場異常監控",
                "📰 越南經營政策與法規每日動態"
            ],
            "👔 管理部 (Management Dept)": [
                "--- 👤 【人事行政類】 ---",
                "公司公告",
                "員工檔案",
                "員工打卡紀錄",
                "密碼修改",
                "員工薪資與保險",
                "--- 📦 【總務後勤類】 ---",
                "宿舍與伙食",
                "工作廠區管理",
                "車輛進出口",
                "車輛維修紀錄",
                "固定資產管理",
                "文件管理",
                "--- 💰 【財務會計類】 ---",
                "採購與應付帳款",
                "應收帳款管理",
                "越南稅務報表",
                "電子發票管理"
            ],
            "📍 外勤工程打卡與工作回報 (Field Attendance)": [
                "📍 現場外勤打卡與工作回報"
            ],
            "✍️ 電子簽核中心 (Approval Center)": [
                "✍️ 提交請假/採購與即時進度追蹤 / 審核"
            ],
            "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
                "⚡ 1. 工程主管戰情室與案場管理",
                "⚡ 2. 工程專案報價系統",
                "📋 3. 施工日報表與點工點料登記",
                "🤖 4. AI 施工照片辨識與稽核",
                "⚠️ 5. 工程證照預警與機具檢驗預警",
                "🎨 6. 配電盤電氣與機構設計圖庫",
                "🔌 7. 配電盤 BOM 零件與採購連動",
                "👷 8. 外包商計價與偶鐸管理",
                "🧪 9. FAT/SAT 出廠與現場驗收管理"
            ],
            "🏭 生產部 (Production Dept)": [
                "✂️ [板金] 板金加工組工單與條碼",
                "🎨 [塗料] 粉體塗裝烤漆組品管",
                "⚡ [配盤] 配電盤組裝配線組"
            ],
            "📦 倉庫管理 (Warehouse Management)": [
                "📦 [倉儲] 倉庫庫存與資材條碼管理"
            ],
            "💻 資訊管理部 (IT & System)": [
                "🔒 系統角色權限與模組開關設定",
                "🔌 API 串聯設定中心"
            ]
        }
    return st.session_state.custom_department_module_tree

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🔒 IT 管理中心 - 組織架構與企業部門設置")
    st.info("系統運行正常")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
