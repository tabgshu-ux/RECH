import streamlit as st
from modules.warehouse.db_init import init_warehouse_db, load_warehouse_data
from modules.warehouse.tab_inventory import render_inventory_tab
from modules.warehouse.tab_transaction import render_transaction_tab
from modules.warehouse.tab_stocktaking import render_stocktaking_tab
from modules.warehouse.tab_alert import render_alert_tab
from modules.warehouse.tab_management import render_management_tab

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    # 1. 初始化資料庫與自動修復舊表結構
    if engine:
        init_warehouse_db(engine)

    # 2. 取得當前登入帳號
    current_logged_user = "admin"
    if "username" in st.session_state and st.session_state.username:
        current_logged_user = st.session_state.username

    # 3. 多語系 UI 字典
    ui_texts = {
        "繁體中文": {
            "title": "📦 裕豐電機 (REETECH) - 全廠共用倉庫：直覺化管理與智慧盤點系統",
            "info": "💡 內控規範：授權同仁可隨時檢視庫存；領用物料請至【電子簽核中心】申請，由倉管人員於此處執行出庫覆核並留存稽核日誌。",
            "tab1": "📊 即時庫存總表與查詢",
            "tab2": "📥📤 出入庫覆核與簽核追蹤",
            "tab3": "📋 庫存盤點作業 (支援列印與平板線上盤點)",
            "tab4": "⚠️ 安全庫存預警",
            "tab5": "⚙️ 物料建檔與維護"
        },
        "越南文 (Tiếng Việt)": {
            "title": "📦 REETECH - Quản lý Kho chung & Kiểm kê Thông minh",
            "info": "💡 Quy định nội bộ: Tra cứu tồn kho trực tuyến; yêu cầu lĩnh vật tư qua Trung tâm Phê duyệt điện tử.",
            "tab1": "📊 Tổng hợp tồn kho",
            "tab2": "📥📤 Xuất nhập kho & Theo dõi",
            "tab3": "📋 Kiểm kê kho",
            "tab4": "⚠️ Cảnh báo tồn kho",
            "tab5": "⚙️ Quản lý danh mục"
        }
    }
    curr_t = ui_texts.get(lang, ui_texts["繁體中文"])

    st.markdown(f"### {curr_t['title']}")
    st.info(curr_t['info'])

    # 4. 安全載入資料庫數據
    inventory_db, logs_db, stocktake_db = load_warehouse_data(engine)

    # 5. 建立五大核心分頁
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        curr_t["tab1"], curr_t["tab2"], curr_t["tab3"], curr_t["tab4"], curr_t["tab5"]
    ])

    with tab1:
        render_inventory_tab(inventory_db, lang)

    with tab2:
        render_transaction_tab(engine, inventory_db, logs_db, current_logged_user, lang)

    with tab3:
        render_stocktaking_tab(engine, inventory_db, stocktake_db, current_logged_user, lang)

    with tab4:
        render_alert_tab(inventory_db, lang)

    with tab5:
        render_management_tab(engine, inventory_db, lang)

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
