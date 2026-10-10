import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 倉庫庫存與資材條碼管理",
        "caption": "管理跨國廠區（西寧廠/海防廠）配電盤原物料、銅排厚度、PVC管規格、斷路器庫存水位與條碼作業。",
        "tab_inventory": "📑 倉庫即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材條碼掃描與出入庫作業",
        "tab_inbound": "📥 資材入庫登記入帳",
        "table_header": "📋 倉庫資材庫存現況清冊 (含銅排、PVC、指示燈與斷路器多規格)",
        "no_records": "目前無倉庫庫存紀錄。",
        "barcode_header": "🏷️ 倉庫條碼掃描與出入庫作業",
        "barcode_input": "請使用條碼槍掃描或輸入料號 (Barcode / Item Code)：",
        "btn_scan": "🔍 查詢資材與庫存",
        "inbound_header": "📥 新增資材入庫作業",
        "lbl_code": "料號 / 條碼編號 *",
        "lbl_name": "資材品項名稱 *",
        "item_placeholder": "例如: 導電銅排 Busbar 10x100mm",
        "lbl_category": "資材類別 *",
        "cat_opts": ["銅排與導電材料", "低壓斷路器 (MCCB/MCB)", "空氣斷路器 (ACB)", "箱體與鈑金零件", "線材與端子配件", "指示燈與按鈕開關", "PVC管與配線槽"],
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
        "title": "📦 Phòng Sản xuất / Kho - Quản lý Kho & Mã vạch Vật tư",
        "caption": "Quản lý tồn kho nguyên vật liệu tủ điện, đồng thanh cái, ống PVC, đèn báo và mã vạch.",
        "tab_inventory": "📑 Báo cáo Tồn kho & Cảnh báo an toàn",
        "tab_barcode": "🏷️ Quét mã vạch xuất nhập kho",
        "tab_inbound": "📥 Nhập kho Vật tư",
        "table_header": "📋 Sổ chi tiết tồn kho vật tư tủ điện",
        "no_records": "Hiện không có bản ghi tồn kho nào.",
        "barcode_header": "🏷️ Quét mã vạch tra cứu tồn kho",
        "barcode_input": "Quét hoặc nhập mã vạch / mã linh kiện (Barcode):",
        "btn_scan": "🔍 Tra cứu vật tư",
        "inbound_header": "📥 Đăng ký nhập kho vật tư mới",
        "lbl_code": "Mã vật tư / Barcode *",
        "lbl_name": "Tên vật tư *",
        "item_placeholder": "Ví dụ: Đồng thanh cái Busbar 10x100mm",
        "lbl_category": "Phân loại *",
        "cat_opts": ["Đồng & Vật liệu dẫn điện", "Aptomat / MCCB / MCB", "Máy cắt không khí (ACB)", "Vỏ tủ điện & Cơ khí", "Dây điện & Phụ kiện", "Đèn báo & Nút nhấn", "Ống PVC & Máng cáp"],
        "lbl_site": "Kho nhà máy *",
        "site_opts": ["Kho Nhà máy Tây Ninh", "Kho Nhà máy Hải Phòng"],
        "lbl_qty": "Số lượng nhập *",
        "lbl_safety": "Mức tồn kho an toàn *",
        "btn_save_inbound": "💾 Xác nhận nhập kho",
        "success_inbound": "✅ Đã nhập kho thành công vật tư `{item_name}`!",
        "fill_warning": "⚠️ Vui lòng điền Mã vật tư và Tên vật tư!",
        "col_index": "STT",
        "col_code": "Mã linh kiện",
        "col_name": "Tên vật tư",
        "col_cat": "Phân loại",
        "col_site": "Kho",
        "col_qty": "Tồn kho",
        "col_safety": "Mức an toàn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📦 Production / Warehouse - Inventory & Barcode Management",
        "caption": "Manage switchgear raw materials, copper busbars, PVC pipes, indicator lights, and inventory.",
        "tab_inventory": "📑 Real-time Inventory & Safety Levels",
        "tab_barcode": "🏷️ Barcode Scanning & Operations",
        "tab_inbound": "📥 Material Inbound Registration",
        "table_header": "📋 Warehouse Inventory Registry",
        "no_records": "No inventory records found.",
        "barcode_header": "🏷️ Barcode Scan & Lookup",
        "barcode_input": "Scan barcode or enter Item Code:",
        "btn_scan": "🔍 Lookup Item",
        "inbound_header": "📥 Register Material Inbound",
        "lbl_code": "Item Code / Barcode *",
        "lbl_name": "Material Name *",
        "item_placeholder": "Example: Copper Busbar 10x100mm",
        "lbl_category": "Category *",
        "cat_opts": ["Copper & Conductive Materials", "MCCB / MCB Breakers", "Air Circuit Breaker (ACB)", "Enclosure & Sheet Metal", "Wires & Terminals", "Indicator Lights & Pushbuttons", "PVC Pipes & Cable Trays"],
        "lbl_site": "Warehouse Plant *",
        "site_opts": ["Tay Ninh Plant Warehouse", "Hai Phong Plant Warehouse"],
        "lbl_qty": "Inbound Qty *",
        "lbl_safety": "Safety Stock Level *",
        "btn_save_inbound": "💾 Confirm Inbound & Update Stock",
        "success_inbound": "✅ Material `{item_name}` successfully added to warehouse!",
        "fill_warning": "⚠️ Please fill in Item Code and Material Name!",
        "col_index": "No.",
        "col_code": "Item Code",
        "col_name": "Material Name",
        "col_cat": "Category",
        "col_site": "Warehouse",
        "col_qty": "Current Stock",
        "col_safety": "Safety Level",
        "col_status": "Status"
    }
}

def smart_translate_wh(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    return text_val

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = WAREHOUSE_I18N.get(active_lang, WAREHOUSE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🛡️ 初始化倉庫庫存資料庫（包含多規格銅排、PVC管、指示燈、斷路器）
    if "warehouse_db" not in st.session_state or not isinstance(st.session_state.warehouse_db, list):
        st.session_state.warehouse_db = [
            {"code": "CU-BUS-3MM", "name": "導電銅排 Busbar 3x30mm (厚度 3mm)", "category": "銅排與導電材料", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 800.0, "safety": 200.0, "status": "庫存充足"},
            {"code": "CU-BUS-5MM", "name": "導電銅排 Busbar 5x50mm (厚度 5mm)", "category": "銅排與導電材料", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 1000.0, "safety": 250.0, "status": "庫存充足"},
            {"code": "CU-BUS-10100", "name": "導電銅排 Busbar 10x100mm (厚度 10mm)", "category": "銅排與導電材料", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 1250.0, "safety": 300.0, "status": "庫存充足"},
            {"code": "CB-MCCB-250A", "name": "塑殼斷路器 MCCB 250A (Schneider)", "category": "低壓斷路器 (MCCB/MCB)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 45.0, "safety": 10.0, "status": "庫存充足"},
            {"code": "CB-ACB-2000A", "name": "空氣斷路器 ACB 2000A (Schneider)", "category": "空氣斷路器 (ACB)", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 8.0, "safety": 5.0, "status": "庫存充足"},
            {"code": "PVC-PIPE-1IN", "name": "硬質 PVC 配線管 1吋 (4米/支)", "category": "PVC管與配線槽", "site": "🇻🇳 越南海防廠倉庫 (Hai Phong WH)", "qty": 600.0, "safety": 150.0, "status": "庫存充足"},
            {"code": "PVC-PIPE-2IN", "name": "硬質 PVC 配線管 2吋 (4米/支)", "category": "PVC管與配線槽", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 400.0, "safety": 100.0, "status": "庫存充足"},
            {"code": "PVC-PIPE-3IN", "name": "硬質 PVC 配線管 3吋 (4米/支)", "category": "PVC管與配線槽", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 250.0, "safety": 80.0, "status": "庫存充足"},
            {"code": "IND-LED-RED", "name": "LED 盤面指示燈 (紅裝 22mm)", "category": "指示燈與按鈕開關", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 300.0, "safety": 50.0, "status": "庫存充足"},
            {"code": "IND-LED-GRN", "name": "LED 盤面指示燈 (綠裝 22mm)", "category": "指示燈與按鈕開關", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 320.0, "safety": 50.0, "status": "庫存充足"},
            {"code": "IND-LED-YEL", "name": "LED 盤面指示燈 (黃裝 22mm)", "category": "指示燈與按鈕開關", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 150.0, "safety": 40.0, "status": "庫存充足"},
            {"code": "CBL-CTRL-3.5", "name": "控制電纜 3.5mm² (100米/卷)", "category": "線材與端子配件", "site": "🇻🇳 越南海防廠倉庫 (Hai Phong WH)", "qty": 85.0, "safety": 20.0, "status": "庫存充足"}
        ]

    # 🔗 定義各分頁變數，解決未定義錯誤
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
        scan_code = st.text_input(L["barcode_input"], value="CU-BUS-10100")
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
                code = st.text_input(L["lbl_code"], value="CU-BUS-8MM")
                name = st.text_input(L["lbl_name"], placeholder=L["item_placeholder"])
                category = st.selectbox(L["lbl_category"], L["cat_opts"])
            with c2:
                site = st.selectbox(L["lbl_site"], L["site_opts"])
                qty = st.number_input(L["lbl_qty"], min_value=0.0, value=500.0, step=10.0)
                safety = st.number_input(L["lbl_safety"], min_value=0.0, value=100.0, step=10.0)

            if st.form_submit_button(L["btn_save_inbound"], type="primary", use_container_width=True):
                if code and name:
                    st.session_state.warehouse_db.insert(0, {
                        "code": code,
                        "name": name,
                        "category": category,
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
