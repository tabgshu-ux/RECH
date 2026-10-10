import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 多倉別聯動與出入庫追蹤系統",
        "caption": "選擇目標倉庫後，下方資材選單將自動精準過濾該倉庫內的專屬零件與資材。",
        "tab_inventory": "📑 各倉別即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材出入庫與領料作業 (倉別動態聯動)",
        "tab_history": "📊 倉庫出入庫異動歷史日誌 (Audit Trail)",
        "tab_inbound": "📥 新增資材建檔與初始入庫",
        "table_header": "📋 跨廠區與多倉別資材庫存現況清冊",
        "no_records": "目前無倉庫庫存紀錄。",
        "op_header": "🔄 倉庫資材出入庫作業處理 (依倉別動態聯動)",
        "lbl_op_type": "選擇作業動作 (Operation Type) *",
        "op_opts": ["📥 入庫作業 (Stock In - 增加庫存)", "📤 出庫作業 (Stock Out - 領料扣減庫存)"],
        "lbl_target_wh": "選擇目標倉庫 (Target Warehouse) *",
        "warehouse_opts": [
            "📦 零件倉 (Parts & Hardware WH)",
            "🔌 線材倉 (Wire & Cable WH)",
            "⚡ 裝配倉 (Assembly Floor WH)",
            "♻️ 退料/殘餘料倉 (Return & Surplus WH)"
        ],
        "lbl_select_item": "選擇該倉庫內的資材品項 *",
        "lbl_scan_alt": "或者使用條碼槍掃描料號：",
        "lbl_op_qty": "異動數量 (Quantity) *",
        "lbl_receiver": "領料人 / 申請部門人員姓名 (Receiver) *",
        "receiver_placeholder": "例如: 王大明 (工程部) 或 現場班長",
        "lbl_memo": "備註說明 / 領料專案編號",
        "memo_placeholder": "例如: 領用於專案工程、或生產線退料入庫...",
        "btn_execute_op": "💾 確認執行出入庫並記錄時間",
        "success_in": "✅ 入庫成功！時間: {time} | 經辦倉管: {staff} | 增加數量: {qty}",
        "success_out": "📤 領料出庫成功！時間: {time} | 領取人: {receiver} | 經辦倉管: {staff} | 扣減數量: {qty}",
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
        "caption": "Lọc vật tư theo kho được chọn.",
        "tab_inventory": "📑 Tồn kho",
        "tab_barcode": "🏷️ Xuất Nhập Kho",
        "tab_history": "📊 Lịch sử kho",
        "tab_inbound": "📥 Thêm vật tư mới",
        "table_header": "📋 Danh mục tồn kho",
        "no_records": "Không có bản ghi.",
        "op_header": "🔄 Xử lý xuất nhập kho",
        "lbl_op_type": "Loại nghiệp vụ *",
        "op_opts": ["📥 Nhập kho", "📤 Xuất kho"],
        "lbl_target_wh": "Chọn kho *",
        "warehouse_opts": ["Kho linh kiện", "Kho cáp điện", "Kho lắp ráp", "Kho hàng thừa/trả lại"],
        "lbl_select_item": "Chọn vật tư trong kho *",
        "lbl_scan_alt": "Mã vạch:",
        "lbl_op_qty": "Số lượng *",
        "lbl_receiver": "Người nhận vật tư *",
        "receiver_placeholder": "Nhập tên người nhận...",
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
        "title": "📦 Production / Warehouse - Warehouse-Linked Operations",
        "caption": "Materials list dynamically updates based on the selected target warehouse.",
        "tab_inventory": "📑 Multi-Warehouse Inventory",
        "tab_barcode": "🏷️ Stock In / Stock Out Operations",
        "tab_history": "📊 Warehouse Operation History",
        "tab_inbound": "📥 Register New Material",
        "table_header": "📋 Inventory Registry",
        "no_records": "No records found.",
        "op_header": "🔄 Warehouse Stock Processing",
        "lbl_op_type": "Operation Type *",
        "op_opts": ["📥 Stock In", "📤 Stock Out (Material Issue)"],
        "lbl_target_wh": "Target Warehouse *",
        "warehouse_opts": ["Parts & Hardware WH", "Wire & Cable WH", "Assembly Floor WH", "Return & Surplus WH"],
        "lbl_select_item": "Select Material in Warehouse *",
        "lbl_scan_alt": "Or scan barcode:",
        "lbl_op_qty": "Operation Quantity *",
        "lbl_receiver": "Material Receiver / Requester *",
        "receiver_placeholder": "Example: John Doe or Assembly Lead",
        "lbl_memo": "Remarks / Project Reference",
        "memo_placeholder": "Example: Project installation...",
        "btn_execute_op": "💾 Confirm Operation & Log Timestamp",
        "success_in": "✅ Stock In recorded at {time} by staff {staff}!",
        "success_out": "📤 Stock Out recorded at {time} issued to {receiver} (Staff: {staff})!",
        "warning_out": "⚠️ Insufficient stock in this warehouse!",
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

    if "warehouse_logs_db" not in st.session_state:
        st.session_state.warehouse_logs_db = [
            {
                "time": "2026-10-06 08:30:12",
                "op_type": "📥 入庫 (Stock In)",
                "code": "GASKET-M10",
                "name": "不鏽鋼平墊片 M10",
                "warehouse": "📦 零件倉 (Parts & Hardware WH)",
                "qty": 500.0,
                "receiver_or_supplier": "廠商送貨 (Supplier)",
                "staff": "admin (倉管經辦)",
                "memo": "採購定期補給"
            }
        ]

    if "warehouse_categories_list" not in st.session_state:
        st.session_state.warehouse_categories_list = ["五金配件與墊片", "燈具與照明配件", "PVC管與管件/彎頭", "電線與電纜線", "箱體與鈑金零件", "退料與殘餘料"]

    # 分頁宣告
    tab_inv, tab_bar, tab_hist, tab_in = st.tabs([
        L["tab_inventory"], L["tab_barcode"], L["tab_history"], L["tab_inbound"]
    ])

    # 1. 各倉別即時庫存總表
    with tab_inv:
        st.markdown(f"### {L['table_header']}")
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

    # 2. 出入庫與領料作業處理 (倉別即時動態聯動)
    with tab_bar:
        st.markdown(f"### {L['op_header']}")
        
        # 🎯 將目標倉庫移到表單外面，實現即時重新載入與過濾
        target_warehouse = st.selectbox(L["lbl_target_wh"], L["warehouse_opts"])
        
        with st.form("form_stock_operation"):
            op_type = st.radio(L["lbl_op_type"], L["op_opts"], horizontal=True)
            
            # 🔗 嚴格根據上方所選的倉庫過濾資材清單
            warehouse_items = [i for i in st.session_state.warehouse_db if i["warehouse"] == target_warehouse]
            
            c_sel1, c_sel2 = st.columns(2)
            with c_sel1:
                if warehouse_items:
                    item_options = [f"{i['code']} - {i['name']} (現庫存: {i['qty']})" for i in warehouse_items]
                    selected_item_str = st.selectbox(L["lbl_select_item"], item_options)
                else:
                    st.warning(f"⚠️ 此倉庫目前無任何資材，請先至「新增資材建檔」建立。")
                    selected_item_str = None
            with c_sel2:
                scan_code_input = st.text_input(L["lbl_scan_alt"], placeholder="例如: GASKET-M10")

            op_qty = st.number_input(L["lbl_op_qty"], min_value=1.0, value=10.0, step=1.0)
            receiver_person = st.text_input(L["lbl_receiver"], placeholder=L["receiver_placeholder"])
            memo = st.text_input(L["lbl_memo"], placeholder=L["memo_placeholder"])

            logged_staff = f"{st.session_state.get('user_name', 'admin')} ({st.session_state.get('user_role', 'Warehouse_Keeper')})"
            st.text_input("倉庫管理員 / 經辦人員 (系統自動綁定)", value=logged_staff, disabled=True)

            if st.form_submit_button(L["btn_execute_op"], type="primary", use_container_width=True):
                target_code = ""
                if scan_code_input.strip():
                    target_code = scan_code_input.strip().lower()
                elif selected_item_str:
                    target_code = selected_item_str.split(" - ")[0].strip().lower()

                # 在目標倉庫中尋找對應料號
                matched_item = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code and i["warehouse"] == target_warehouse), None)

                # 若是入庫作業且該倉庫沒有此料號，自動建立或轉移
                if not matched_item and ("入庫" in op_type or "Stock In" in op_type):
                    any_matched = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code), None)
                    if any_matched:
                        new_entry = any_matched.copy()
                        new_entry["warehouse"] = target_warehouse
                        new_entry["qty"] = 0.0
                        st.session_state.warehouse_db.insert(0, new_entry)
                        matched_item = new_entry

                if matched_item and receiver_person.strip():
                    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if "入庫" in op_type or "Stock In" in op_type:
                        matched_item["qty"] += op_qty
                        if matched_item["qty"] >= matched_item["safety"]:
                            matched_item["status"] = "庫存充足"
                        
                        st.session_state.warehouse_logs_db.insert(0, {
                            "time": current_time_str,
                            "op_type": "📥 入庫 (Stock In)",
                            "code": matched_item["code"],
                            "name": matched_item["name"],
                            "warehouse": target_warehouse,
                            "qty": op_qty,
                            "receiver_or_supplier": f"送貨商/交貨人: {receiver_person}",
                            "staff": logged_staff,
                            "memo": memo or "正常入庫補給"
                        })

                        st.success(L["success_in"].format(time=current_time_str, staff=logged_staff, qty=op_qty))
                        st.rerun()
                    else: # 出庫 / 領料
                        if matched_item["qty"] >= op_qty:
                            matched_item["qty"] -= op_qty
                            if matched_item["qty"] < matched_item["safety"]:
                                matched_item["status"] = "⚠️ 庫存低於安全水位"
                            
                            st.session_state.warehouse_logs_db.insert(0, {
                                "time": current_time_str,
                                "op_type": "📤 出庫 (Stock Out)",
                                "code": matched_item["code"],
                                "name": matched_item["name"],
                                "warehouse": target_warehouse,
                                "qty": op_qty,
                                "receiver_or_supplier": receiver_person,
                                "staff": logged_staff,
                                "memo": memo or "專案領料"
                            })

                            st.success(L["success_out"].format(time=current_time_str, receiver=receiver_person, staff=logged_staff, qty=op_qty))
                            st.rerun()
                        else:
                            st.warning(L["warning_out"].format(total=matched_item["qty"]))
                else:
                    st.warning("⚠️ 請確認所選資材品項，並完整輸入「領取人 / 申請部門人員姓名」！")

    # 3. 倉庫出入庫歷史日誌稽核表
    with tab_hist:
        st.markdown("### 📊 倉庫進出庫與領料稽核歷史日誌 (Audit Trail)")
        st.caption("詳細記錄每一次進倉時間、出倉時間、領取人、倉管經辦與數量異動。")
        if st.session_state.warehouse_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.warehouse_logs_db), use_container_width=True)
        else:
            st.info("目前尚無出入庫歷史日誌紀錄。")

    # 4. 新資材建檔
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
