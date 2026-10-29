import streamlit as st
import pandas as pd
import datetime

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    st.markdown("### 📦 裕豐電機 (REETECH) - 倉庫庫存與物料條碼照片識別中心")
    st.info("💡 管理廠內原物料、零組件、配電盤成品，支援照片預覽、條碼/QR Code 掃描識別、出入庫作業與安全庫存預警，幫助新進員工一眼識別正確物料。")

    if "warehouse_inventory_db" not in st.session_state:
        st.session_state.warehouse_inventory_db = [
            {"item_code": "MCCB-400L", "item_name": "MCCB 3P 400AF 315AT 50KA", "category": "配電元件", "spec": "TBX-400L", "barcode": "893500123401", "qty": 45, "unit": "只", "safety_stock": 10, "location": "A區-01櫃", "updated": "2026-10-20", "photo": None},
            {"item_code": "CU-BAR-02", "item_name": "銅牌導體 (CU BAR BUS)", "category": "導電銅材", "spec": "標準規格 4m/支", "barcode": "893500123402", "qty": 120, "unit": "支", "safety_stock": 30, "location": "B區-03架", "updated": "2026-10-21", "photo": None},
            {"item_code": "CT-300-5A", "item_name": "比流器 CT300/5A", "category": "儀表元件", "spec": "CT300/5A 高精度", "barcode": "893500123403", "qty": 18, "unit": "只", "safety_stock": 15, "location": "A區-05櫃", "updated": "2026-10-22", "photo": None},
            {"item_code": "SPCC-2.0", "item_name": "SPCC 鋼板 (烤漆用)", "category": "鈑金原料", "spec": "厚度 T=2.0 靜電粉體", "barcode": "893500123404", "qty": 8, "unit": "噸", "safety_stock": 5, "location": "C區-露天棚", "updated": "2026-10-23", "photo": None}
        ]

    if "warehouse_logs_db" not in st.session_state:
        st.session_state.warehouse_logs_db = [
            {"log_id": "LOG-2026-001", "type": "📥 入庫 (In)", "item_code": "MCCB-400L", "item_name": "MCCB 3P 400AF 315AT 50KA", "qty": 20, "operator": "倉庫管理員", "date": "2026-10-20", "note": "採購部到貨驗收上架"},
            {"log_id": "LOG-2026-002", "type": "📤 出庫 (Out)", "item_code": "CT-300-5A", "item_name": "比流器 CT300/5A", "qty": 3, "operator": "配盤組裝員", "date": "2026-10-22", "note": "領料投入西寧廠高壓配盤專案"}
        ]

    tab_inv, tab_in_out, tab_alert, tab_manage = st.tabs([
        "📊 即時庫存總表與照片/條碼預覽 | Tồn kho",
        "📥📤 入庫與出庫領料作業 | Nhập/Xuất kho",
        "⚠️ 安全庫存預警 | Cảnh báo tồn kho",
        "⚙️ 物料建檔、照片與條碼維護"
    ])

    # ----------------------------------------------------
    # Tab 1: 即時庫存總表與照片/條碼預覽
    # ----------------------------------------------------
    with tab_inv:
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            search_wh = st.text_input("🔍 搜尋料號、名稱、條碼 (Barcode) 或儲位...", key="wh_search_box")
        with col_w2:
            cat_options = ["全部類別"] + list(set([i["category"] for i in st.session_state.warehouse_inventory_db]))
            cat_filter = st.selectbox("依類別篩選", cat_options, key="wh_cat_filter")

        filtered_items = st.session_state.warehouse_inventory_db
        if cat_filter != "全部類別":
            filtered_items = [i for i in filtered_items if i["category"] == cat_filter]
        if search_wh:
            s_low = search_wh.lower()
            filtered_items = [i for i in filtered_items if s_low in i["item_code"].lower() or s_low in i["item_name"].lower() or s_low in i["location"].lower() or s_low in str(i.get("barcode", "")).lower()]

        if filtered_items:
            for item in filtered_items:
                with st.container():
                    c_photo, c_info, c_status = st.columns([1.5, 3.5, 1.5])
                    with c_photo:
                        if item.get("photo"):
                            st.image(item["photo"], caption=f"料號: {item['item_code']}", width=110)
                        else:
                            st.markdown("📷 `無照片`")
                            st.caption("建議補拍外觀以供新進同仁辨識")
                    with c_info:
                        st.markdown(f"**📦 [{item['item_code']}] {item['item_name']}**")
                        st.caption(f"🏷️ 條碼/QR Code: `{item.get('barcode', '無條碼')}`")
                        st.write(f"📁 類別: `{item['category']}` | 規格: `{item['spec']}`")
                        st.write(f"📍 儲位: **{item['location']}** | 現有庫存: **{item['qty']} {item['unit']}** (安全水位: {item['safety_stock']})")
                    with c_status:
                        is_normal = item["qty"] > item["safety_stock"]
                        color_str = "green" if is_normal else "red"
                        text_str = "🟢 庫存正常" if is_normal else "🔴 低於安全水位"
                        st.markdown(f"狀態: :{color_str}[{text_str}]")
                        st.caption(f"更新: {item['updated']}")
                st.markdown("---")
        else:
            st.info("目前尚無符合條件的庫存資材紀錄。")

    # ----------------------------------------------------
    # Tab 2: 入庫與出庫領料作業
    # ----------------------------------------------------
    with tab_in_out:
        st.markdown("##### 📥📤 快速登錄物料入庫或出庫領料")
        with st.form("form_warehouse_transaction"):
            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                t_type = st.selectbox("交易類型 / Loại giao dịch", ["📥 物料入庫 (Stock In)", "📤 出庫領料 (Stock Out)"])
            with tc2:
                item_options = [f"{i['item_code']} - {i['item_name']} (條碼:{i.get('barcode','N/A')})" for i in st.session_state.warehouse_inventory_db]
                t_code = st.selectbox("選擇料號與條碼 / Mã vật tư", item_options) if item_options else ""
            with tc3:
                t_qty = st.number_input("異動數量 / Số lượng", min_value=1.0, value=1.0)

            t_note = st.text_input("備註說明 / Ghi chú", placeholder="例如: 專案領料、廠商送貨入庫")
            t_operator = st.text_input("經辦人員 / Người thao tác", value="倉庫管理員")

            if st.form_submit_button("💾 確認送出並更新庫存", type="primary", use_container_width=True):
                if not t_code:
                    st.error("❌ 目前無可用料號可供異動！")
                else:
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
                                st.stop()

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

    # ----------------------------------------------------
    # Tab 3: 安全庫存預警
    # ----------------------------------------------------
    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示監控")
        low_stock_items = [i for i in st.session_state.warehouse_inventory_db if i["qty"] <= i["safety_stock"]]
        if low_stock_items:
            st.warning("⚠️ 以下物料庫存已低於安全水位，請盡速聯繫採購部進行補貨！")
            for item in low_stock_items:
                st.error(f"料號: `{item['item_code']}` | 條碼: {item.get('barcode','N/A')} | 品名: {item['item_name']} | 現有庫存: {item['qty']} {item['unit']} (安全水位: {item['safety_stock']})")
        else:
            st.success("🟢 目前所有倉庫物料庫存皆高於安全水位，供應鏈狀態正常！")

    # ----------------------------------------------------
    # Tab 4: 物料建檔、照片與條碼維護
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("##### ⚙️ 倉庫資材主檔、照片與條碼/QR Code 維護")
        
        action_mode = st.radio("選擇維護動作", ["➕ 新增資材與照片/條碼", "✏️ 修改現有資材、照片與條碼", "🗑️ 移除資材品項"], horizontal=True)
        st.markdown("---")

        if action_mode == "➕ 新增資材與照片/條碼":
            with st.form("form_add_item"):
                c1, c2 = st.columns(2)
                with c1:
                    new_code = st.text_input("料號 (Item Code) *", placeholder="例如: MCCB-600L")
                    new_name = st.text_input("品名規格名稱 (Item Name) *", placeholder="例如: 600A 無熔絲開關")
                    new_cat = st.text_input("資材類別 (Category) *", placeholder="例如: 配電元件")
                    new_spec = st.text_input("詳細規格 (Specification)", placeholder="例如: TBX-600L")
                with c2:
                    new_barcode = st.text_input("條碼 / QR Code 編號 *", placeholder="例如: 893500123405")
                    new_qty = st.number_input("初始庫存數量 (Initial Qty)", min_value=0.0, value=10.0)
                    new_unit = st.text_input("計量單位 (Unit) *", value="只")
                    new_safety = st.number_input("安全庫存水位 (Safety Stock)", min_value=0.0, value=5.0)
                    new_loc = st.text_input("倉庫儲位 (Location)", value="A區-02櫃")

                uploaded_file = st.file_uploader("📷 上傳物品外觀照片 (供新進員工識別)", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("💾 確認新增資材", type="primary", use_container_width=True):
                    if new_code and new_name and new_cat and new_unit:
                        if any(i["item_code"] == new_code.strip() for i in st.session_state.warehouse_inventory_db):
                            st.error(f"❌ 錯誤：料號 `{new_code}` 已存在！")
                        else:
                            st.session_state.warehouse_inventory_db.append({
                                "item_code": new_code.strip(),
                                "item_name": new_name.strip(),
                                "category": new_cat.strip(),
                                "spec": new_spec.strip(),
                                "barcode": new_barcode.strip() if new_barcode else f"893{datetime.datetime.now().strftime('%m%d%H%M')}",
                                "qty": new_qty,
                                "unit": new_unit.strip(),
                                "safety_stock": new_safety,
                                "location": new_loc.strip(),
                                "updated": str(datetime.date.today()),
                                "photo": uploaded_file if uploaded_file else None
                            })
                            st.success(f"✅ 成功新增資材：`{new_code} - {new_name}`！")
                            st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫所有必填欄位！")

        elif action_mode == "✏️ 修改現有資材、照片與條碼":
            if not st.session_state.warehouse_inventory_db:
                st.info("目前無任何資材可供修改。")
            else:
                edit_target_str = st.selectbox("選擇要修改的資材料號", [i["item_code"] + " - " + i["item_name"] for i in st.session_state.warehouse_inventory_db])
                target_code = edit_target_str.split(" - ")[0]
                target_item = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == target_code), None)

                if target_item:
                    with st.form("form_edit_item"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            edit_name = st.text_input("品名規格名稱", value=target_item["item_name"])
                            edit_cat = st.text_input("資材類別", value=target_item["category"])
                            edit_spec = st.text_input("詳細規格", value=target_item["spec"])
                            edit_barcode = st.text_input("條碼 / QR Code 編號", value=target_item.get("barcode", ""))
                        with ec2:
                            edit_qty = st.number_input("現有庫存數量", min_value=0.0, value=float(target_item["qty"]))
                            edit_unit = st.text_input("計量單位", value=target_item["unit"])
                            edit_safety = st.number_input("安全庫存水位", min_value=0.0, value=float(target_item["safety_stock"]))
                            edit_loc = st.text_input("倉庫儲位", value=target_item["location"])

                        edit_photo = st.file_uploader("📷 更新物品照片", type=["jpg", "png", "jpeg"], key="edit_photo_upload")

                        if st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True):
                            target_item["item_name"] = edit_name.strip()
                            target_item["category"] = edit_cat.strip()
                            target_item["spec"] = edit_spec.strip()
                            target_item["barcode"] = edit_barcode.strip()
                            target_item["qty"] = edit_qty
                            target_item["unit"] = edit_unit.strip()
                            target_item["safety_stock"] = edit_safety
                            target_item["location"] = edit_loc.strip()
                            target_item["updated"] = str(datetime.date.today())
                            if edit_photo:
                                target_item["photo"] = edit_photo

                            st.success(f"✅ 料號 `{target_code}` 資料與照片條碼已成功更新！")
                            st.rerun()

        elif action_mode == "🗑️ 移除資材品項":
            if not st.session_state.warehouse_inventory_db:
                st.info("目前無任何資材可供移除。")
            else:
                del_target_str = st.selectbox("選擇要移除的資材料號", [i["item_code"] + " - " + i["item_name"] for i in st.session_state.warehouse_inventory_db], key="del_select")
                del_code = del_target_str.split(" - ")[0]

                st.warning(f"⚠️ 您即將從庫存系統中徹底移除料號：`{del_code}`。此動作無法復原，請確認！")
                if st.button("🗑️ 確認永久刪除此資材品項", type="primary"):
                    st.session_state.warehouse_inventory_db = [i for i in st.session_state.warehouse_inventory_db if i["item_code"] != del_code]
                    st.success(f"✅ 已成功將料號 `{del_code}` 自庫存系統中移除！")
                    st.rerun()

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
