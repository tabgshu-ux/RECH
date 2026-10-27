import streamlit as st
import pandas as pd
import datetime

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.markdown("### 📦 裕豐電機 (REETECH) - 倉庫庫存與資材條碼管理中心")
    st.info("💡 管理廠內原物料、零組件、配電盤成品庫存，支援條碼掃描入庫、出庫領料與安全庫存預警。")

    if "warehouse_inventory_db" not in st.session_state:
        st.session_state.warehouse_inventory_db = [
            {"item_code": "MCCB-400L", "item_name": "MCCB 3P 400AF 315AT 50KA", "category": "配電元件", "spec": "TBX-400L", "qty": 45, "unit": "只", "safety_stock": 10, "location": "A區-01櫃", "updated": "2026-10-20"},
            {"item_code": "CU-BAR-02", "item_name": "銅牌導體 (CU BAR BUS)", "category": "導電銅材", "spec": "標準規格 4m/支", "qty": 120, "unit": "支", "safety_stock": 30, "location": "B區-03架", "updated": "2026-10-21"},
            {"item_code": "CT-300-5A", "item_name": "比流器 CT300/5A", "category": "儀表元件", "spec": "CT300/5A 高精度", "qty": 18, "unit": "只", "safety_stock": 15, "location": "A區-05櫃", "updated": "2026-10-22"},
            {"item_code": "SPCC-2.0", "item_name": "SPCC 鋼板 (烤漆用)", "category": "鈑金原料", "spec": "厚度 T=2.0 靜電粉體", "qty": 8, "unit": "噸", "safety_stock": 5, "location": "C區-露天棚", "updated": "2026-10-23"}
        ]

    if "warehouse_logs_db" not in st.session_state:
        st.session_state.warehouse_logs_db = [
            {"log_id": "LOG-2026-001", "type": "📥 入庫 (In)", "item_code": "MCCB-400L", "item_name": "MCCB 3P 400AF 315AT 50KA", "qty": 20, "operator": "倉庫管理員", "date": "2026-10-20", "note": "採購部到貨驗收上架"},
            {"log_id": "LOG-2026-002", "type": "📤 出庫 (Out)", "item_code": "CT-300-5A", "item_name": "比流器 CT300/5A", "qty": 3, "operator": "配盤組裝員", "date": "2026-10-22", "note": "領料投入西寧廠高壓配盤專案"}
        ]

    tab_inv, tab_in_out, tab_alert = st.tabs([
        "📊 即時庫存總表與條碼查詢 | Tồn kho",
        "📥📤 入庫與出庫領料作業 | Nhập/Xuất kho",
        "⚠️ 安全庫存預警 | Cảnh báo tồn kho"
    ])

    with tab_inv:
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            search_wh = st.text_input("🔍 搜尋料號、名稱或儲位 / Tìm kiếm...", key="wh_search_box")
        with col_w2:
            cat_filter = st.selectbox("依類別篩選", ["全部類別"] + list(set([i["category"] for i in st.session_state.warehouse_inventory_db])))

        filtered_items = st.session_state.warehouse_inventory_db
        if cat_filter != "全部類別":
            filtered_items = [i for i in filtered_items if i["category"] == cat_filter]
        if search_wh:
            filtered_items = [i for i in filtered_items if search_wh.lower() in i["item_code"].lower() or search_wh.lower() in i["item_name"].lower() or search_wh.lower() in i["location"].lower()]

        if filtered_items:
            st.dataframe(pd.DataFrame(filtered_items), use_container_width=True, hide_index=True)
        else:
            st.info("目前尚無符合條件的庫存資材紀錄。")

    with tab_in_out:
        st.markdown("##### 📥📤 快速登錄物料入庫或出庫領料")
        with st.form("form_warehouse_transaction"):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                t_type = st.selectbox("交易類型 / Loại giao dịch", ["📥 物料入庫 (Stock In)", "📤 出庫領料 (Stock Out)"])
            with tc2:
                t_code = st.selectbox("選擇料號 / Mã vật tư", [i["item_code"] + " - " + i["item_name"] for i in st.session_state.warehouse_inventory_db])
            with tc3:
                t_qty = st.number_input("異動數量 / Số lượng", min_value=1.0, value=1.0)

            t_note = st.text_input("備註說明 / Ghi chú", placeholder="例如: 專案領料、廠商送貨入庫")
            t_operator = st.text_input("經辦人員 / Người thao tác", value="倉庫管理員")

            if st.form_submit_button("💾 確認送出並更新庫存", type="primary", use_container_width=True):
                code_extracted = t_code.split(" - ")[0]
                item_obj = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == code_extracted), None)
                
                if item_obj:
                    qty_val = float(t_qty)
                    if "入庫" in t_type:
                        item_obj["qty"] += qty_val
                        log_type_str = "📥 入庫 (In)"
                    else:
                        if item_obj["qty"] >= qty_val:
                            item_obj["qty"] -= qty_val
                            log_type_str = "📤 出庫 (Out)"
                        else:
                            st.error("❌ 庫存不足，無法出庫！")
                            return

                    item_obj["updated"] = str(datetime.date.today())
                    
                    st.session_state.warehouse_logs_db.insert(0, {
                        "log_id": f"LOG-2026-{len(st.session_state.warehouse_logs_db)+1:03d}",
                        "type": log_type_str,
                        "item_code": item_obj["item_code"],
                        "item_name": item_obj["item_name"],
                        "qty": qty_val,
                        "operator": t_operator,
                        "date": str(datetime.date.today()),
                        "note": t_note
                    })
                    st.success(f"🎉 庫存異動成功！[{item_obj['item_name']}] 目前最新庫存：{item_obj['qty']} {item_obj['unit']}")
                    st.rerun()

        st.markdown("---")
        st.markdown("##### 📋 近期庫存異動日誌 (Stock Movement History)")
        if st.session_state.warehouse_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.warehouse_logs_db), use_container_width=True, hide_index=True)

    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示監控")
        low_stock_items = [i for i in st.session_state.warehouse_inventory_db if i["qty"] <= i["safety_stock"]]
        if low_stock_items:
            st.warning("⚠️ 以下物料庫存已低於安全水位，請盡速聯繫採購部進行補貨！")
            st.dataframe(pd.DataFrame(low_stock_items), use_container_width=True, hide_index=True)
        else:
            st.success("🟢 目前所有倉庫物料庫存皆高於安全水位，供應鏈狀態正常！")

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
