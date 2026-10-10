import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 倉庫庫存與出入庫動態作業",
        "caption": "支援手動選擇料號、明確區分「入庫」與「出庫」動作，並即時自動更新庫存與安全水位。",
        "tab_inventory": "📑 倉庫即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材出入庫作業 (支援手動選擇與條碼掃描)",
        "tab_inbound": "📥 新增資材建檔與初始入庫",
        "table_header": "📋 倉庫資材庫存現況清冊",
        "no_records": "目前無倉庫庫存紀錄。",
        "op_header": "🔄 倉庫資材出入庫作業處理",
        "lbl_op_type": "選擇作業動作 (Operation Type) *",
        "op_opts": ["📥 入庫作業 (Stock In - 增加庫存)", "📤 出庫作業 (Stock Out - 扣減庫存)"],
        "lbl_select_item": "選擇或搜尋資材品項 *",
        "lbl_scan_alt": "或者使用條碼槍掃描料號：",
        "lbl_op_qty": "異動數量 (Quantity) *",
        "lbl_memo": "備註說明 / 領料專案編號",
        "memo_placeholder": "例如: 領用於專案工程、或是廠商進貨補給...",
        "btn_execute_op": "💾 確認執行出入庫作業",
        "success_in": "✅ 入庫成功！資材 `{item_name}` 庫存已增加 `{qty}`，現有總庫存：`{total}`",
        "success_out": "📤 出庫成功！資材 `{item_name}` 庫存已扣減 `{qty}`，現有總庫存：`{total}`",
        "warning_out": "⚠️ 庫存不足！現有庫存僅剩 `{total}`，無法完成此出庫數量。",
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
        "title": "📦 Phòng Sản xuất / Kho - Quản lý Xuất Nhập Kho",
        "caption": "Thực hiện nghiệp vụ xuất nhập kho linh hoạt bằng mã vạch hoặc chọn thủ công.",
        "tab_inventory": "📑 Tồn kho",
        "tab_barcode": "🏷️ Xuất Nhập Kho",
        "tab_inbound": "📥 Đăng ký vật tư mới",
        "table_header": "📋 Danh mục tồn kho",
        "no_records": "Không có bản ghi.",
        "op_header": "🔄 Nghiệp vụ Xuất / Nhập kho",
        "lbl_op_type": "Loại nghiệp vụ *",
        "op_opts": ["📥 Nhập kho (Tăng tồn kho)", "📤 Xuất kho (Giảm tồn kho)"],
        "lbl_select_item": "Chọn vật tư *",
        "lbl_scan_alt": "Hoặc quét mã vạch:",
        "lbl_op_qty": "Số lượng *",
        "lbl_memo": "Ghi chú",
        "memo_placeholder": "Ví dụ: Xuất cho dự án...",
        "btn_execute_op": "💾 Xác nhận",
        "success_in": "✅ Nhập kho thành công!",
        "success_out": "📤 Xuất kho thành công!",
        "warning_out": "⚠️ Tồn kho không đủ!",
        "col_index": "STT",
        "col_code": "Mã",
        "col_name": "Tên",
        "col_cat": "Loại",
        "col_site": "Kho",
        "col_qty": "Tồn",
        "col_safety": "An toàn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📦 Production / Warehouse - Stock In / Stock Out Operations",
        "caption": "Handle material inbound and outbound manually or via barcode scanner.",
        "tab_inventory": "📑 Real-time Inventory",
        "tab_barcode": "🏷️ Stock In / Stock Out Operations",
        "tab_inbound": "📥 Register New Material",
        "table_header": "📋 Warehouse Inventory Registry",
        "no_records": "No records found.",
        "op_header": "🔄 Material Inbound / Outbound Processing",
        "lbl_op_type": "Operation Type *",
        "op_opts": ["📥 Stock In (Increase Inventory)", "📤 Stock Out (Decrease Inventory)"],
        "lbl_select_item": "Select Material Item *",
        "lbl_scan_alt": "Or scan barcode/item code:",
        "lbl_op_qty": "Operation Quantity *",
        "lbl_memo": "Remarks / Project Reference",
        "memo_placeholder": "Example: Issued for switchgear assembly...",
        "btn_execute_op": "💾 Confirm Stock Operation",
        "success_in": "✅ Stock In successful! Item `{item_name}` increased by `{qty}`, current stock: `{total}`",
        "success_out": "📤 Stock Out successful! Item `{item_name}` decreased by `{qty}`, current stock: `{total}`",
        "warning_out": "⚠️ Insufficient stock! Current stock is only `{total}`.",
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

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = WAREHOUSE_I18N.get(active_lang, WAREHOUSE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🛡️ 初始化倉庫庫存資料庫
    if "warehouse_db" not in st.session_state or not isinstance(st.session_state.warehouse_db, list):
        st.session_state.warehouse_db = [
            {"code": "GASKET-M10", "name": "不鏽鋼平墊片 M10 (不鏽鋼 304)", "category": "五金配件與墊片", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 2500.0, "safety": 500.0, "status": "庫存充足"},
            {"code": "GASKET-RUB", "name": "配電盤箱體防水橡膠墊片 (捲裝)", "category": "五金配件與墊片", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 120.0, "safety": 30.0, "status": "庫存充足"},
            {"code": "LAMP-LED-4FT", "name": "盤內照明 LED 支架燈管 4尺 (220V)", "category": "燈具與照明配件", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 85.0, "safety": 20.0, "status": "庫存充足"},
            {"code": "PVC-ELB-2IN", "name": "硬質 PVC 90度彎頭 2吋", "category": "PVC管與管件/彎頭", "site": "🇻🇳 越南海防廠倉庫 (Hai Phong WH)", "qty": 350.0, "safety": 80.0, "status": "庫存充足"},
            {"code": "CBL-CV-10MM", "name": "極軟式控制電纜 CV 10mm² (黑色)", "category": "電線與電纜線", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 520.0, "safety": 100.0, "status": "庫存充足"},
            {"code": "SHEET-SPCC-2MM", "name": "SPCC 冷軋鋼板板金料件 (1200x2400x2mm)", "category": "箱體與鈑金零件", "site": "🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "qty": 65.0, "safety": 15.0, "status": "庫存充足"}
        ]

    if "warehouse_categories_list" not in st.session_state:
        st.session_state.warehouse_categories_list = ["五金配件與墊片", "燈具與照明配件", "PVC管與管件/彎頭", "電線與電纜線", "箱體與鈑金零件", "銅排與導電材料", "低壓斷路器 (MCCB/MCB)"]

    # 分頁宣告
    tab_inv, tab_bar, tab_in = st.tabs([
        L["tab_inventory"], L["tab_barcode"], L["tab_inbound"]
    ])

    # 1. 庫存總表
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

    # 2. 出入庫作業處理 (手動選擇 + 條碼槍皆可)
    with tab_bar:
        st.markdown(f"### {L['op_header']}")
        
        with st.form("form_stock_operation"):
            op_type = st.radio(L["lbl_op_type"], L["op_opts"], horizontal=True)
            
            c_sel1, c_sel2 = st.columns(2)
            with c_sel1:
                # 提供下拉選單供手動選擇（無需條碼槍也能直接作業）
                item_options = [f"{i['code']} - {i['name']} (現庫存: {i['qty']})" for i in st.session_state.warehouse_db]
                selected_item_str = st.selectbox(L["lbl_select_item"], item_options)
            with c_sel2:
                scan_code_input = st.text_input(L["lbl_scan_alt"], placeholder="例如: GASKET-M10")

            op_qty = st.number_input(L["lbl_op_qty"], min_value=1.0, value=10.0, step=1.0)
            memo = st.text_input(L["lbl_memo"], placeholder=L["memo_placeholder"])

            if st.form_submit_button(L["btn_execute_op"], type="primary", use_container_width=True):
                # 決定目標料號
                target_code = ""
                if scan_code_input.strip():
                    target_code = scan_code_input.strip().lower()
                elif selected_item_str:
                    target_code = selected_item_str.split(" - ")[0].strip().lower()

                matched_item = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code), None)

                if matched_item:
                    if "入庫" in op_type or "Stock In" in op_type:
                        matched_item["qty"] += op_qty
                        if matched_item["qty"] >= matched_item["safety"]:
                            matched_item["status"] = "庫存充足"
                        st.success(L["success_in"].format(item_name=matched_item["name"], qty=op_qty, total=matched_item["qty"]))
                        st.rerun()
                    else: # 出庫
                        if matched_item["qty"] >= op_qty:
                            matched_item["qty"] -= op_qty
                            if matched_item["qty"] < matched_item["safety"]:
                                matched_item["status"] = "⚠️ 庫存低於安全水位"
                            st.success(L["success_out"].format(item_name=matched_item["name"], qty=op_qty, total=matched_item["qty"]))
                            st.rerun()
                        else:
                            st.warning(L["warning_out"].format(total=matched_item["qty"]))
                else:
                    st.warning("⚠️ 查無此料號，請確認選擇或條碼是否正確！")

    # 3. 新增資材建檔
    with tab_in:
        st.markdown(f"### 📥 新增資材建檔與初始庫存")
        with st.form("form_new_material"):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_code = st.text_input("料號 / 條碼編號 *", value="GASKET-COPPER-8MM")
                new_name = st.text_input("資材品項名稱 *", placeholder="例如: 紅銅墊片 8mm")
                new_category = st.selectbox("資材類別 *", st.session_state.warehouse_categories_list)
            with nc2:
                new_site = st.selectbox("存放廠區倉庫 *", ["🇻🇳 越南西寧廠倉庫 (Tay Ninh WH)", "🇻🇳 越南海防廠倉庫 (Hai Phong WH)"])
                new_qty = st.number_input("初始現有庫存量 *", min_value=0.0, value=500.0, step=10.0)
                new_safety = st.number_input("安全庫存水位 *", min_value=0.0, value=100.0, step=10.0)

            if st.form_submit_button("💾 建立新資材並登錄", type="primary", use_container_width=True):
                if new_code and new_name:
                    st.session_state.warehouse_db.insert(0, {
                        "code": new_code,
                        "name": new_name,
                        "category": new_category,
                        "site": new_site,
                        "qty": new_qty,
                        "safety": new_safety,
                        "status": "庫存充足"
                    })
                    st.success(f"✅ 新資材 `{new_name}` 建檔成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫料號與資材名稱！")

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def render_warehouse_management_page(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
