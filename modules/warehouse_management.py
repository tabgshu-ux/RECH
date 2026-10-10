import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 倉庫庫存與資材條碼管理 (彈性自訂分類)",
        "caption": "管理跨國廠區配電盤原物料、墊片、燈具燈管、PVC管件、各類電纜線、板金件與動態擴充資材類別。",
        "tab_inventory": "📑 倉庫即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材條碼掃描與出入庫作業",
        "tab_inbound": "📥 資材入庫登記入帳 (含自訂類別)",
        "table_header": "📋 倉庫資材庫存現況清冊 (支援多樣化電機與五金零件)",
        "no_records": "目前無倉庫庫存紀錄。",
        "barcode_header": "🏷️ 倉庫條碼掃描與出入庫作業",
        "barcode_input": "請使用條碼槍掃描或輸入料號 (Barcode / Item Code)：",
        "btn_scan": "🔍 查詢資材與庫存",
        "inbound_header": "📥 新增資材入庫作業 (支援自由新增零件與類別)",
        "lbl_code": "料號 / 條碼編號 *",
        "lbl_name": "資材品項名稱 *",
        "item_placeholder": "例如: 不鏽鋼墊片 M10 / PVC 90度彎頭 2吋 / 橡膠絕緣墊片",
        "lbl_category": "資材類別 (可選或自訂新類別) *",
        "default_categories": [
            "五金配件與墊片 (Gaskets & Washers)",
            "燈具與照明配件 (Lamps & Holders)",
            "PVC管與管件/彎頭 (PVC Pipes & Fittings)",
            "電線與電纜線 (Cables & Wires)",
            "銅排與導電材料 (Copper Busbars)",
            "低壓斷路器 (MCCB/MCB)",
            "空氣斷路器 (ACB)",
            "箱體與鈑金零件 (Enclosures & Sheet Metal)",
            "線材與端子配件 (Terminals & Lugs)",
            "指示燈與按鈕開關 (Indicators & Pushbuttons)",
            "➕ [自訂新資材類別...]"
        ],
        "lbl_site": "存放廠區倉庫 *",
        "site_opts": ["🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "🇻🇳 越南海防廠倉庫 (Hai Phong WH)"],
        "lbl_qty": "入庫數量 *",
        "lbl_safety": "安全庫存水位 *",
        "btn_save_inbound": "💾 確認入庫並更新庫存",
        "success_inbound": "✅ 資材 `{item_name}` 已成功入庫！",
        "fill_warning": "⚠️ 請完整填寫料號與資材名稱！",
        "col_index": "STT",
        "col_code": "料號",
        "col_name": "資材品項名稱",
        "col_cat": "類別",
        "col_site": "存放倉庫",
        "col_qty": "現有庫存量",
        "col_safety": "安全水位",
        "col_status": "庫存狀態"
    },
    "Tiếng Việt": {
        "title": "📦 Phòng Sản xuất / Kho - Quản lý Kho & Phân loại linh hoạt",
        "caption": "Quản lý tồn kho gioăng đệm, đèn, ống PVC, cáp điện, tôn tấm và danh mục tùy chỉnh.",
        "tab_inventory": "📑 Tồn kho & Cảnh báo an toàn",
        "tab_barcode": "🏷️ Quét mã vạch",
        "tab_inbound": "📥 Nhập kho Vật tư",
        "table_header": "📋 Danh mục tồn kho vật tư thiết bị điện",
        "no_records": "Không có bản ghi.",
        "barcode_header": "🏷️ Tra cứu mã vạch",
        "barcode_input": "Nhập mã vạch:",
        "btn_scan": "🔍 Tra cứu",
        "inbound_header": "📥 Nhập kho vật tư mới",
        "lbl_code": "Mã vật tư *",
        "lbl_name": "Tên vật tư *",
        "item_placeholder": "Ví dụ: Gioăng cao su, Ống PVC...",
        "lbl_category": "Phân loại *",
        "default_categories": ["Gioăng đệm", "Đèn & Máng đèn", "Ống & Co PVC", "Cáp điện", "Đồng thanh cái", "Tủ điện & Tôn tấm", "➕ [Tùy chỉnh...]"],
        "lbl_site": "Kho *",
        "site_opts": ["Kho Tây Ninh", "Kho Hải Phòng"],
        "lbl_qty": "Số lượng *",
        "lbl_safety": "Mức an toàn *",
        "btn_save_inbound": "💾 Nhập kho",
        "success_inbound": "✅ Đã nhập thành công `{item_name}`!",
        "fill_warning": "⚠️ Vui lòng điền đủ thông tin!",
        "col_index": "STT",
        "col_code": "Mã",
        "col_name": "Tên vật tư",
        "col_cat": "Phân loại",
        "col_site": "Kho",
        "col_qty": "Tồn kho",
        "col_safety": "An toàn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📦 Production / Warehouse - Inventory & Custom Categories",
        "caption": "Manage gaskets, lamp holders, PVC fittings, cables, sheet metals, and dynamic categories.",
        "tab_inventory": "📑 Inventory & Safety Levels",
        "tab_barcode": "🏷️ Barcode Operations",
        "tab_inbound": "📥 Material Inbound (Custom Categories)",
        "table_header": "📋 Warehouse Inventory Registry",
        "no_records": "No records found.",
        "barcode_header": "🏷️ Barcode Lookup",
        "barcode_input": "Scan or enter Item Code:",
        "btn_scan": "🔍 Lookup",
        "inbound_header": "📥 Register Inbound (Custom Categories)",
        "lbl_code": "Item Code *",
        "lbl_name": "Material Name *",
        "item_placeholder": "Example: Stainless Gasket M10, PVC Elbow 2-inch",
        "lbl_category": "Category *",
        "default_categories": ["Gaskets & Washers", "Lamps & Holders", "PVC Pipes & Fittings", "Cables & Wires", "Copper Busbars", "Enclosures & Sheet Metal", "➕ [Custom Category...]"],
        "lbl_site": "Warehouse *",
        "site_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "lbl_qty": "Qty *",
        "lbl_safety": "Safety Level *",
        "btn_save_inbound": "💾 Confirm Inbound",
        "success_inbound": "✅ Material `{item_name}` added!",
        "fill_warning": "⚠️ Please fill in all required fields!",
        "col_index": "No.",
        "col_code": "Item Code",
        "col_name": "Material Name",
        "col_cat": "Category",
        "col_site": "Warehouse",
        "col_qty": "Stock",
        "col_safety": "Safety",
        "col_status": "Status"
    }
}

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = WAREHOUSE_I18N.get(active_lang, WAREHOUSE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🛡️ 初始化倉庫庫存資料庫（擴充墊片、燈具、PVC管配件、電纜線與板金多樣零件）
    if "warehouse_db" not in st.session_state or not isinstance(st.session_state.warehouse_db, list):
        st.session_state.warehouse_db = [
            {"code": "GASKET-M10", "name": "不鏽鋼平墊片 M10 (不鏽鋼 304)", "category": "五金配件與墊片 (Gaskets & Washers)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 2500.0, "safety": 500.0, "status": "庫存充足"},
            {"code": "GASKET-RUB", "name": "配電盤箱體防水橡膠墊片 (捲裝)", "category": "五金配件與墊片 (Gaskets & Washers)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 120.0, "safety": 30.0, "status": "庫存充足"},
            {"code": "LAMP-LED-4FT", "name": "盤內照明 LED 支架燈管 4尺 (220V)", "category": "燈具與照明配件 (Lamps & Holders)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 85.0, "safety": 20.0, "status": "庫存充足"},
            {"code": "PVC-ELB-2IN", "name": "硬質 PVC 90度彎頭 2吋", "category": "PVC管與管件/彎頭 (PVC Pipes & Fittings)", "site": "🇻🇳 越南海防廠倉庫 (Hai Phong WH)", "qty": 350.0, "safety": 80.0, "status": "庫存充足"},
            {"code": "CBL-CV-10MM", "name": "極軟式控制電纜 CV 10mm² (黑色)", "category": "電線與電纜線 (Cables & Wires)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 520.0, "safety": 100.0, "status": "庫存充足"},
            {"code": "SHEET-SPCC-2MM", "name": "SPCC 冷軋鋼板板金料件 (1200x2400x2mm)", "category": "箱體與鈑金零件 (Enclosures & Sheet Metal)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 65.0, "safety": 15.0, "status": "庫存充足"},
            {"code": "CU-BUS-3MM", "name": "導電銅排 Busbar 3x30mm (厚度 3mm)", "category": "銅排與導電材料", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 800.0, "safety": 200.0, "status": "庫存充足"},
            {"code": "CB-MCCB-250A", "name": "塑殼斷路器 MCCB 250A (Schneider)", "category": "低壓斷路器 (MCCB/MCB)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 45.0, "safety": 10.0, "status": "庫存充足"},
            {"code": "IND-LED-RED", "name": "LED 盤面指示燈 (紅裝 22mm)", "category": "指示燈與按鈕開關", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 300.0, "safety": 50.0, "status": "庫存充足"}
        ]

    # 初始化動態類別清單
    if "warehouse_categories_list" not in st.session_state:
        st.session_state.warehouse_categories_list = L["default_categories"]

    # 🔗 定義各分頁變數
    tab_inv, tab_bar, tab_in = st.tabs([
        L["tab_inventory"], L["tab_barcode"], L["tab_inbound"]
    ])

    with tab_inv:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.warehouse_db:
            display_data = []
            for idx, item in enumerate(st.session_state.warehouse_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_cat"]: item["category"],
                    L["col_site"]: item["site"],
                    L["col_qty"]: f"{item['qty']:,.1f}",
                    L["col_safety"]: f"{item['safety']:,.1f}",
                    L["col_status"]: item["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_bar:
        st.markdown(f"### {L['barcode_header']}")
        scan_code = st.text_input(L["barcode_input"], value="GASKET-M10")
        if st.button(L["btn_scan"], type="primary"):
            matched = next((i for i in st.session_state.warehouse_db if i["code"].lower() == scan_code.strip().lower()), None)
            if matched:
                st.success(f"✅ 成功找到資材：`{matched['code']}` - {matched['name']}")
                st.metric("當前倉庫現有庫存", f"{matched['qty']:,.1f}", f"安全水位: {matched['safety']}")
            else:
                st.warning("⚠️ 查無此料號，請確認條碼是否正確！")

    with tab_in:
        st.markdown(f"### {L['inbound_header']}")
        with st.form("form_inbound"):
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input(L["lbl_code"], value="GASKET-COPPER-8MM")
                name = st.text_input(L["lbl_name"], placeholder=L["item_placeholder"])
                
                selected_cat_opt = st.selectbox(L["lbl_category"], st.session_state.warehouse_categories_list)
            with c2:
                site = st.selectbox(L["lbl_site"], L["site_opts"])
                qty = st.number_input(L["lbl_qty"], min_value=0.0, value=500.0, step=10.0)
                safety = st.number_input(L["lbl_safety"], min_value=0.0, value=100.0, step=10.0)

            # 🛠️ 允許自訂新資材類別
            final_category = selected_cat_opt
            if "➕" in selected_cat_opt:
                custom_cat_input = st.text_input("✨ 請自由輸入新的資材分類名稱 (例如: 絕緣材料類、氣動元件類、五金螺絲類...):")
                if custom_cat_input:
                    final_category = custom_cat_input
                    if custom_cat_input not in st.session_state.warehouse_categories_list:
                        st.session_state.warehouse_categories_list.insert(0, custom_cat_input)

            if st.form_submit_button(L["btn_save_inbound"], type="primary", use_container_width=True):
                if code and name:
                    st.session_state.warehouse_db.insert(0, {
                        "code": code,
                        "name": name,
                        "category": final_category,
                        "site": site,
                        "qty": qty,
                        "safety": safety,
                        "status": "庫存充足"
                    })
                    st.success(L["success_inbound"].format(item_name=name))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def render_warehouse_management_page(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
