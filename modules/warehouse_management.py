import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 嘗試連線 Supabase 資料庫
# ----------------------------------------------------
def get_supabase_client():
    if "supabase" in st.session_state:
        return st.session_state.supabase
    return None

# ----------------------------------------------------
# 🌐 倉庫與資材管理模組多語系字典 (i18n)
# ----------------------------------------------------
WAREHOUSE_I18N = {
    "繁體中文": {
        "title": "📦 生產部/倉儲 - 多倉別與出入庫追蹤 (Supabase 永久同步)",
        "caption": "支援依特定倉別篩選歷史稽核日誌，進出庫時間與領料人完美記錄，重啟絕不遺失。",
        "tab_inventory": "📑 各倉別即時庫存與安全水位總表",
        "tab_barcode": "🏷️ 資材出入庫與領料作業 (倉別動態聯動)",
        "tab_history": "📊 倉庫出入庫異動歷史日誌 (含倉別篩選)",
        "tab_inbound": "📥 新增資材建檔與初始入庫",
        "table_header": "📋 跨廠區與多倉別資材庫存現況清冊 (Supabase)",
        "no_records": "目前無倉庫庫存紀錄。",
        "op_header": "🔄 倉庫資材出入庫作業處理 (同步寫入資料庫)",
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
        "btn_execute_op": "💾 確認執行出入庫並同步寫入資料庫",
        "success_in": "✅ 入庫成功並已同步 Supabase！時間: {time} | 增加數量: {qty}",
        "success_out": "📤 領料出庫成功並已同步 Supabase！時間: {time} | 領取人: {receiver} | 扣減數量: {qty}",
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
        "title": "📦 Phòng Sản xuất / Kho - Quản lý Đa kho (Đồng bộ Supabase)",
        "caption": "Lịch sử kho phân theo từng kho.",
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
        "receiver_placeholder": "Nhập tên...",
        "lbl_memo": "Ghi chú",
        "memo_placeholder": "Ghi chú...",
        "btn_execute_op": "💾 Xác nhận & Lưu Database",
        "success_in": "✅ Thành công!",
        "success_out": "📤 Thành công!",
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
        "title": "📦 Production / Warehouse - Multi-WH with Filterable Logs",
        "caption": "Filter audit logs by specific warehouse for streamlined tracking.",
        "tab_inventory": "📑 Multi-Warehouse Inventory",
        "tab_barcode": "🏷️ Stock In / Stock Out Operations",
        "tab_history": "📊 Warehouse Operation History (Filtered)",
        "tab_inbound": "📥 Register New Material",
        "table_header": "📋 Inventory Registry (Supabase)",
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
        "btn_execute_op": "💾 Confirm & Sync to Database",
        "success_in": "✅ Stock In recorded & synced at {time}!",
        "success_out": "📤 Stock Out recorded & synced at {time}!",
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

    supabase = get_supabase_client()

    # 🛡️ 初始化倉庫庫存資料庫（優先從 Supabase 讀取）
    if "warehouse_db" not in st.session_state or not isinstance(st.session_state.warehouse_db, list):
        default_warehouse = [
            {"code": "GASKET-M10", "name": "不鏽鋼平墊片 M10 (不鏽鋼 304)", "category": "五金配件與墊片", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 2500.0, "safety": 500.0, "status": "庫存充足"},
            {"code": "GASKET-RUB", "name": "配電盤箱體防水橡膠墊片 (捲裝)", "category": "五金配件與墊片", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 120.0, "safety": 30.0, "status": "庫存充足"},
            {"code": "LAMP-LED-4FT", "name": "盤內照明 LED 支架燈管 4尺 (220V)", "category": "燈具與照明配件", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 85.0, "safety": 20.0, "status": "庫存充足"},
            {"code": "PVC-ELB-2IN", "name": "硬質 PVC 90度彎頭 2吋", "category": "PVC管與管件/彎頭", "warehouse": "📦 零件倉 (Parts & Hardware WH)", "qty": 350.0, "safety": 80.0, "status": "庫存充足"},
            {"code": "CBL-CV-10MM", "name": "極軟式控制電纜 CV 10mm² (黑色)", "category": "電線與電纜線", "warehouse": "🔌 線材倉 (Wire & Cable WH)", "qty": 520.0, "safety": 100.0, "status": "庫存充足"},
            {"code": "SHEET-SPCC-2MM", "name": "SPCC 冷軋鋼板板金料件 (1200x2400x2mm)", "category": "箱體與鈑金零件", "warehouse": "⚡ 裝配倉 (Assembly Floor WH)", "qty": 65.0, "safety": 15.0, "status": "庫存充足"},
            {"code": "SURPLUS-NUT", "name": "現場退回雜項螺絲與華司 (待分類/退料)", "category": "退料與殘餘料", "warehouse": "♻️ 退料/殘餘料倉 (Return & Surplus WH)", "qty": 150.0, "safety": 20.0, "status": "庫存充足"}
        ]
        
        if supabase:
            try:
                res = supabase.table("warehouse_inventory").select("*").execute()
                if res.data:
                    st.session_state.warehouse_db = [{
                        "code": row["code"],
                        "name": row["name"],
                        "category": row["category"],
                        "warehouse": row["warehouse"],
                        "qty": float(row["qty"]),
                        "safety": float(row["safety"]),
                        "status": row["status"]
                    } for row in res.data]
                else:
                    st.session_state.warehouse_db = default_warehouse
                    for item in default_warehouse:
                        supabase.table("warehouse_inventory").upsert(item).execute()
            except Exception:
                st.session_state.warehouse_db = default_warehouse
        else:
            st.session_state.warehouse_db = default_warehouse

    # 初始化歷史日誌（從 Supabase 讀取）
    if "warehouse_logs_db" not in st.session_state:
        default_logs = [
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
        if supabase:
            try:
                res_logs = supabase.table("warehouse_logs").select("*").order("id", desc=True).limit(50).execute()
                if res_logs.data:
                    st.session_state.warehouse_logs_db = [{
                        "time": row["op_time"],
                        "op_type": row["op_type"],
                        "code": row["code"],
                        "name": row["name"],
                        "warehouse": row["warehouse"],
                        "qty": float(row["qty"]),
                        "receiver_or_supplier": row["receiver_or_supplier"],
                        "staff": row["staff"],
                        "memo": row["memo"]
                    } for row in res_logs.data]
                else:
                    st.session_state.warehouse_logs_db = default_logs
            except Exception:
                st.session_state.warehouse_logs_db = default_logs
        else:
            st.session_state.warehouse_logs_db = default_logs

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
        selected_wh_filter = st.selectbox("🔍 篩選檢視特定倉庫庫存", wh_filter_opts)

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

    # 2. 出入庫與領料作業處理
    with tab_bar:
        st.markdown(f"### {L['op_header']}")
        
        target_warehouse = st.selectbox(L["lbl_target_wh"], L["warehouse_opts"], key="target_wh_select")
        
        with st.form("form_stock_operation"):
            op_type = st.radio(L["lbl_op_type"], L["op_opts"], horizontal=True)
            
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

                matched_item = next((i for i in st.session_state.warehouse_db if i["code"].strip().lower() == target_code and i["warehouse"] == target_warehouse), None)

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
                        
                        log_entry = {
                            "op_time": current_time_str,
                            "op_type": "📥 入庫 (Stock In)",
                            "code": matched_item["code"],
                            "name": matched_item["name"],
                            "warehouse": target_warehouse,
                            "qty": op_qty,
                            "receiver_or_supplier": f"
