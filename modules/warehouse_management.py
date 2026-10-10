import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 多倉別管理系統 (線材倉、零件倉、裝配倉、退料倉)",
        "caption": "精細化管理多重廠區與四大專業倉別（線材、零件、裝配、退料/殘餘料），解決物品繁雜痛點。",
        "tab_inventory": "📑 各倉別即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材出入庫與跨倉調撥作業",
        "tab_inbound": "📥 新增資材建檔與初始入庫",
        "table_header": "📋 跨廠區與多倉別資材庫存現況清冊",
        "no_records": "目前無倉庫庫存紀錄。",
        "op_header": "🔄 倉庫資材出入庫作業處理 (指定倉別)",
        "lbl_op_type": "選擇作業動作 (Operation Type) *",
        "op_opts": ["📥 入庫作業 (Stock In - 增加庫存)", "📤 出庫作業 (Stock Out - 扣減庫存)"],
        "lbl_target_wh": "選擇目標倉庫 (Target Warehouse) *",
        "warehouse_opts": [
            "📦 零件倉 (Parts & Hardware WH)",
            "🔌 線材倉 (Wire & Cable WH)",
            "⚡ 裝配倉 (Assembly Floor WH)",
            "♻️ 退料/殘餘料倉 (Return & Surplus WH)"
        ],
        "lbl_select_item": "選擇或搜尋資材品項 *",
        "lbl_scan_alt": "或者使用條碼槍掃描料號：",
        "lbl_op_qty": "異動數量 (Quantity) *",
        "lbl_memo": "備註說明 / 領料專案編號",
        "memo_placeholder": "例如: 領用於專案工程、或生產線退料入庫...",
        "btn_execute_op": "💾 確認執行倉別出入庫",
        "success_in": "✅ 入庫成功！資材 `{item_name}` 在 `{wh}` 庫存已增加 `{qty}`，現有庫存：`{total}`",
        "success_out": "📤 出庫成功！資材 `{item_name}` 從 `{wh}` 庫存已扣減 `{qty}`，現有庫存：`{total}`",
        "warning_out": "⚠️ 該倉庫庫存不足！現有庫存僅剩 `{total}`，無法完成此出庫數量。",
        "col_index": "STT",
        "col_code": "料號",
        "col_name": "資材品項名稱",
        "col_cat": "類別",
        "col_wh": "存放倉庫別",
        "col_qty": "現有庫存量",
        "col_safety": "安全水位",
        "col_status": "庫存狀態"
    },
    "Tiếng Việt": {
        "title": "📦 Phòng Sản xuất / Kho - Quản lý Đa kho",
        "caption": "Quản lý kho linh kiện, kho cáp, kho lắp ráp và kho phế phẩm/hàng thừa.",
        "tab_inventory": "📑 Tồn kho đa kho",
        "tab_barcode": "🏷️ Xuất Nhập Kho",
        "tab_inbound": "📥 Thêm vật tư mới",
        "table_header": "📋 Danh mục tồn kho",
        "no_records": "Không có bản ghi.",
        "op_header": "🔄 Nghiệp vụ Xuất / Nhập kho theo Kho",
        "lbl_op_type": "Loại nghiệp vụ *",
        "op_opts": ["📥 Nhập kho", "📤 Xuất kho"],
        "lbl_target_wh": "Chọn kho *",
        "warehouse_opts": ["Kho linh kiện", "Kho cáp điện", "Kho lắp ráp", "Kho hàng thừa/trả lại"],
        "lbl_select_item": "Chọn vật tư *",
        "lbl_scan_alt": "Mã vạch:",
        "lbl_op_qty": "Số lượng *",
        "lbl_memo": "Ghi chú",
        "memo_placeholder": "Ghi chú...",
        "btn_execute_op": "💾 Xác nhận",
        "success_in": "✅ Nhập thành công!",
        "success_out": "📤 Xuất thành công!",
        "warning_out": "⚠️ Tồn kho không đủ!",
        "col_index": "STT",
        "col_code": "Mã",
        "col_name": "Tên",
        "col_cat": "Loại",
        "col_wh": "Kho",
        "col_qty": "Tồn",
        "col_safety": "An toàn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📦 Production / Warehouse - Multi-Warehouse Management",
        "caption": "Manage Parts WH, Wire WH, Assembly WH, and Return/Surplus WH efficiently.",
        "tab_inventory": "📑 Multi-Warehouse Inventory",
        "tab_barcode": "🏷️ Stock In / Stock Out by Warehouse",
        "tab_inbound": "📥 Register New Material",
        "table_header": "📋 Multi-Warehouse Inventory Registry",
        "no_records": "No records found.",
        "op_header": "🔄 Warehouse Stock Processing",
        "lbl_op_type": "Operation Type *",
        "op_opts": ["📥 Stock In", "📤 Stock Out"],
        "lbl_target_wh": "Target Warehouse *",
        "warehouse_opts": ["Parts & Hardware WH", "Wire & Cable WH", "Assembly Floor WH", "Return & Surplus WH"],
        "lbl_select_item": "Select Material Item *",
        "lbl_scan_alt": "Or scan barcode/item code:",
        "lbl_op_qty": "Operation Quantity *",
        "lbl_memo": "Remarks / Project Reference",
        "memo_placeholder": "Example: Issued for assembly or return from shopfloor...",
        "btn_execute_op": "💾 Confirm Operation",
        "success_in": "✅ Stock In successful in `{wh}`! Item `{item_name}` increased by `{qty}`, current stock: `{total}`",
        "success_out": "📤 Stock Out successful from `{wh}`! Item `{item_name}` decreased by `{qty}`, current stock: `{total}`",
        "warning_out": "⚠️ Insufficient stock in this warehouse! Current stock is only `{total}`.",
        "col_index": "No.",
        "col_code": "Item Code",
        "col_name": "Material Name",
        "col_cat": "Category",
        "col_wh": "Warehouse",
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

    # 🛡️ 初始化多倉別倉庫庫存資料庫
    if "warehouse_db" not in st.session_state or not isinstance(st.session_state.warehouse_db, list):
        st.session_state.warehouse_db = [
            {"code": "GASKET-M10", "name": "不鏽鋼平墊片 M10 (不鏽鋼 304)", "category": "五金配件與墊片", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 2500.0, "safety": 500.0, "status": "庫存充足"},
            {"code": "GASKET-RUB", "name": "配電盤箱體防水橡膠墊片 (捲裝)", "category": "五金配件與墊片", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 120.0, "safety": 30.0, "status": "庫存充足"},
            {"code": "LAMP-LED-4FT", "name": "盤內照明 LED 支架燈管 4尺 (220V)", "category": "燈具與照明配件", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 85.0, "safety": 20.0, "status": "庫存充足"},
            {"code": "PVC-ELB-2IN", "name": "硬質 PVC 90度彎頭 2吋", "category": "PVC管與管件/彎頭", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 350.0, "safety": 80.0, "status": "庫存充足"},
            {"code": "CBL-CV-10MM", "name": "極軟式控制電纜 CV 10mm² (黑色)", "category": "電線與電纜線", "warehouse": "🔌 線材倉 (Wire & Cable WH)", "qty": 520.0, "safety": 100.0, "status": "庫存充足"},
            {"code": "SHEET-SPCC-2MM", "name": "SPCC 冷軋鋼板板金料件 (1200x2400x2mm)", "category": "箱體與鈑金零件", "warehouse": "⚡ 裝配倉 (Assembly Floor WH)", "qty": 65.0, "safety": 15.0, "status": "庫存充足"},
            {"code": "SURPLUS-NUT", "name": "現場退回雜項螺絲與華司 (待分類/退料)", "category": "退料與殘餘料", "warehouse": "♻️ 退料/殘餘料倉 (Return & Surplus WH)", "qty": 150.0, "safety": 20.0, "status": "庫存充足"}
        ]

    if "warehouse_categories_list" not in st.session_state:
        st.session_state.warehouse_categories_list = ["五金配件與墊片", "燈具與照明配件", "PVC管與管件/彎頭", "電線與電纜線", "箱體與鈑金零件", "退料與殘餘料"]

    # 分頁宣告
    tab_inv, tab_bar, tab_in = st.tabs([
        L["tab_inventory"], L["tab_barcode"], L["tab_inbound"]
    ])

    # 1. 各倉別即時庫存總表
    with tab_inv:
        st.markdown(f"### {L['table_header']}")
        
        # 篩選特定倉庫檢視
        wh_filter_opts = ["全部倉庫"] + L["warehouse_opts"]
        selected_wh_filter = st.selectbox("🔍 篩選檢視特定倉庫", wh_filter_opts)

        filtered_db = st.session_state.warehouse_db
        if selected_wh_filter != "全部倉庫":
            filtered_db = [i for i in st.session_state.warehouse_db if i["warehouse"] == selected_wh_filter]

        if filtered_db:
            display_data = []
            for idx, item in enumerate(filtered_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_cat"]: item["category"],
                    L["col_wh"]: item["warehouse"],
                    L["col_qty"]: f"{item['qty']:,.1f}",
                    L["col_safety"]: f"{item['safety']:,.1f}",
                    L["col_status"]: item["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    # 2. 出入庫與跨倉作業處理
    with tab_bar:
        st.markdown(f"### {L['op_header']}")
        
        with st.form("form_stock_operation"):
            op_type = st.radio(L["lbl_op_type"], L["op_opts"], horizontal=True)
            target_warehouse = st.selectbox(L["lbl_target_wh"], L["warehouse_opts"])
            
            c_sel1, c_sel2 = st.columns(2)
            with c_sel1:
                item_options = [f"{i['code']} - {i['name']} (現庫存: {i['qty']} | 倉別: {i['warehouse']})" for i in st.session_state.warehouse_db]
                selected_item_str = st.selectbox(L["lbl_select_item"], item_options)
            with c_sel2:
                scan_code_input = st.text_input(L["lbl_scan_alt"], placeholder="例如: GASKET-M10")

            op_qty = st.number_input(L["lbl_op_qty"], min_value=1.0, value=10.0, step=1.0)
            memo = st.text_input(L["lbl_memo"], placeholder=L["memo_placeholder"])

            if st.form_submit_button(L["btn_execute_op"], type="primary", use_container_width=True):
                target_code = ""
                if scan_code_input.strip():
                    target_code = scan_code_input.strip().lower()
                elif selected_item_str:
                    target_code = selected_item_str.split(" - ")[0].strip().lower()

                matched_item = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code and i["warehouse"] == target_warehouse), None)

                # 若在該倉庫找不到但總庫存有，允許自動對應或提示
                if not matched_item:
                    matched_item = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code), None)

                if matched_item:
                    if "入庫" in op_type or "Stock In" in op_type:
                        # 如果是入庫到指定倉庫，若倉庫不同則新增或增加數量
                        if matched_item["warehouse"] == target_warehouse:
                            matched_item["qty"] += op_qty
                        else:
                            # 檢查該倉庫是否已有此料號
                            exist_in_wh = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code and i["warehouse"] == target_warehouse), None)
                            if exist_in_wh:
                                exist_in_wh["qty"] += op_qty
                                matched_item = exist_in_wh
                            else:
                                new_entry = matched_item.copy()
                                new_entry["warehouse"] = target_warehouse
                                new_entry["qty"] = op_qty
                                st.session_state.warehouse_db.insert(0, new_entry)
                                matched_item = new_entry

                        if matched_item["qty"] >= matched_item["safety"]:
                            matched_item["status"] = "庫存充足"
                        st.success(L["success_in"].format(item_name=matched_item["name"], wh=target_warehouse, qty=op_qty, total=matched_item["qty"]))
                        st.rerun()
                    else: # 出庫
                        if matched_item["warehouse"] == target_warehouse:
                            if matched_item["qty"] >= op_qty:
                                matched_item["qty"] -= op_qty
                                if matched_item["qty"] < matched_item["safety"]:
                                    matched_item["status"] = "⚠️ 庫存低於安全水位"
                                st.success(L["success_out"].format(item_name=matched_item["name"], wh=target_warehouse, qty=op_qty, total=matched_item["qty"]))
                                st.rerun()
                            else:
                                st.warning(L["warning_out"].format(total=matched_item["qty"]))
                        else:
                            st.warning(f"⚠️ 所選倉庫 [{target_warehouse}] 中找不到此料號，請確認該倉庫是否有存貨！")
                else:
                    st.warning("⚠️ 查無此料號，請確認選擇或條碼是否正確！")

    # 3. 新增資材建檔
    with tab_in:
        st.markdown(f"### 📥 新增資材建檔與指定倉別初始入庫")
        with st.form("form_new_material"):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_code = st.text_input("料號 / 條碼編號 *", value="WIRE-PVC-2.0")
                new_name = st.text_input("資材品項名稱 *", placeholder="例如: 控制軟線 2.0mm²")
                new_category = st.selectbox("資材類別 *", st.session_state.warehouse_categories_list)
            with nc2:
                new_warehouse = st.selectbox("指定初始存放倉庫 *", L["warehouse_opts"])
                new_qty = st.number_input("初始現有庫存量 *", min_value=0.0, value=200.0, step=10.0)
                new_safety = st.number_input("安全庫存水位 *", min_value=0.0, value=50.0, step=10.0)

            if st.form_submit_button("💾 建立新資材並登錄至指定倉庫", type="primary", use_container_width=True):
                if new_code and new_name:
                    st.session_state.warehouse_db.insert(0, {
                        "code": new_code,
                        "name": new_name,
                        "category": new_category,
                        "warehouse": new_warehouse,
                        "qty": new_qty,
                        "safety": new_safety,
                        "status": "庫存充足"
                    })
                    st.success(f"✅ 新資材 `{new_name}` 已成功建檔並存入 `{new_warehouse}`！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫料號與資材名稱！")

def show(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def main(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)

def render_warehouse_management_page(*args, **kwargs):
    render_warehouse_management(*args, **kwargs)
