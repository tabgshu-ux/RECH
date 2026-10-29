import streamlit as st
import pandas as pd
import datetime

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    ui_texts = {
        "繁體中文": {
            "title": "📦 裕豐電機 (REETECH) - 倉庫庫存與物料條碼照片識別中心",
            "info": "💡 管理廠內原物料、零組件、配電盤成品，支援照片預覽、條碼掃描、分區儲位確認與安全庫存預警。",
            "tab1": "📊 即時庫存總表與照片預覽",
            "tab2": "📥📤 入庫與出庫領料作業",
            "tab3": "⚠️ 安全庫存預警",
            "tab4": "⚙️ 物料建檔與照片條碼維護",
            "search_box": "🔍 搜尋料號、名稱、條碼或儲位...",
            "cat_filter": "依類別篩選",
            "zone_filter": "📍 倉庫分區快速篩選 (Zone Filter)",
            "all_zone": "全部倉庫分區",
            "all_cat": "全部類別",
            "trans_title": "📥📤 快速登錄物料入庫或出庫領料（即時儲位連動確認）",
            "trans_type": "交易類型 / Loại giao dịch",
            "trans_in": "📥 物料入庫 (Stock In)",
            "trans_out": "📤 出庫領料 (Stock Out)",
            "select_item": "選擇料號與品名",
            "qty_label": "異動數量",
            "note_label": "備註說明",
            "operator_label": "經辦人員",
            "submit_btn": "💾 確認送出並更新庫存",
            "location_card": "📍 【即時出入倉位置與儲位確認 (Vị trí kho)】",
            "log_title": "📋 近期庫存異動日誌 (Stock Movement History)"
        },
        "越南文 (Tiếng Việt)": {
            "title": "📦 REETECH - Trung tâm Quản lý Kho & Mã vạch Vật tư",
            "info": "💡 Quản lý nguyên vật liệu, linh kiện, tủ điện. Hỗ trợ xem ảnh, quét mã vạch, xác nhận vị trí kho và cảnh báo tồn kho.",
            "tab1": "📊 Tổng hợp tồn kho & Xem trước ảnh",
            "tab2": "📥📤 Nghiệp vụ Nhập / Xuất kho",
            "tab3": "⚠️ Cảnh báo tồn kho an toàn",
            "tab4": "⚙️ Quản lý danh mục & Mã vạch",
            "search_box": "🔍 Tìm kiếm mã, tên, mã vạch hoặc vị trí...",
            "cat_filter": "Lọc theo danh mục",
            "zone_filter": "📍 Lọc khu vực kho nhanh (Zone Filter)",
            "all_zone": "Tất cả khu vực kho",
            "all_cat": "Tất cả danh mục",
            "trans_title": "📥📤 Đăng ký Nhập kho hoặc Xuất kho nhanh",
            "trans_type": "Loại giao dịch",
            "trans_in": "📥 Nhập kho (Stock In)",
            "trans_out": "📤 Xuất kho (Stock Out)",
            "select_item": "Chọn mã và tên vật tư",
            "qty_label": "Số lượng thay đổi",
            "note_label": "Ghi chú",
            "operator_label": "Người thao tác",
            "submit_btn": "💾 Xác nhận & Cập nhật kho",
            "location_card": "📍 【Xác nhận vị trí kho & Phân loại (Vị trí kho)】",
            "log_title": "📋 Lịch sử biến động kho gần đây"
        }
    }

    curr_t = ui_texts.get(lang, ui_texts["繁體中文"])

    st.markdown(f"### {curr_t['title']}")
    st.info(curr_t['info'])

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
        curr_t["tab1"],
        curr_t["tab2"],
        curr_t["tab3"],
        curr_t["tab4"]
    ])

    # ----------------------------------------------------
    # Tab 1: 即時庫存總表與照片預覽
    # ----------------------------------------------------
    with tab_inv:
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            search_wh = st.text_input(curr_t["search_box"], key="wh_search_box")
        with col_w2:
            cat_options = [curr_t["all_cat"]] + list(set([i["category"] for i in st.session_state.warehouse_inventory_db]))
            cat_filter = st.selectbox(curr_t["cat_filter"], cat_options, key="wh_cat_filter")

        filtered_items = st.session_state.warehouse_inventory_db
        if cat_filter != curr_t["all_cat"]:
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
                            st.markdown("📷 `無照片 / Không có ảnh`")
                    with c_info:
                        st.markdown(f"**📦 [{item['item_code']}] {item['item_name']}**")
                        st.caption(f"🏷️ Barcode: `{item.get('barcode', 'N/A')}`")
                        st.write(f"📁 類別 (Danh mục): `{item['category']}` | 規格: `{item['spec']}`")
                        st.write(f"📍 儲位/分區 (Vị trí kho): **{item['location']}** | 庫存: **{item['qty']} {item['unit']}** (安全水位: {item['safety_stock']})")
                    with c_status:
                        is_normal = item["qty"] > item["safety_stock"]
                        color_str = "green" if is_normal else "red"
                        text_str = "🟢 庫存正常" if is_normal else "🔴 低於安全水位"
                        st.markdown(f":{color_str}[{text_str}]")
                        st.caption(f"更新: {item['updated']}")
                st.markdown("---")
        else:
            st.info("目前尚無符合條件的庫存資材紀錄。")

    # ----------------------------------------------------
    # Tab 2: 入庫與出庫領料作業（分區選項 + 即時連動確認卡片）
    # ----------------------------------------------------
    with tab_in_out:
        st.markdown(f"##### {curr_t['trans_title']}")
        
        # 1. 倉庫分區快速篩選器 (讓同仁先選分區，如 A區、B區)
        all_locations = list(set([i["location"].split("-")[0] if "-" in i["location"] else i["location"] for i in st.session_state.warehouse_inventory_db]))
        zone_options = [curr_t["all_zone"]] + all_locations
        selected_zone = st.selectbox(curr_t["zone_filter"], zone_options, key="trans_zone_filter")

        # 根據分區篩選可用物料
        pool_items = st.session_state.warehouse_inventory_db
        if selected_zone != curr_t["all_zone"]:
            pool_items = [i for i in pool_items if selected_zone in i["location"]]

        item_options = [f"{i['item_code']} - {i['item_name']} (儲位: {i['location']})" for i in pool_items] if pool_items else []
        
        # 2. 交易選項與物料選擇（移出 form 外，確保即時連動！）
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            t_type = st.selectbox(curr_t["trans_type"], [curr_t["trans_in"], curr_t["trans_out"]], key="trans_type_box")
        with tc2:
            t_code = st.selectbox(curr_t["select_item"], item_options, key="trans_item_select") if item_options else ""
        with tc3:
            t_qty = st.number_input(curr_t["qty_label"], min_value=1.0, value=1.0, key="trans_qty_box")

        # 3. 立即即時顯示所選物料的分類、儲位與庫存卡片（換物品時會立刻跟著變動！）
        selected_obj = None
        if t_code:
            extracted_code = t_code.split(" - ")[0]
            selected_obj = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == extracted_code), None)
            if selected_obj:
                st.success(f"""
                {curr_t['location_card']}  
                - 📁 **資材分類 (Danh mục)**：`{selected_obj['category']}`  
                - 📍 **正確儲位與分區 (Vị trí kệ kho)**：**{selected_obj['location']}**  
                - 🏷️ **條碼編號 (Barcode)**：`{selected_obj.get('barcode', 'N/A')}`  
                - 📊 **目前庫存 (Tồn kho hiện tại)**：`{selected_obj['qty']} {selected_obj['unit']}` (安全水位: {selected_obj['safety_stock']})
                """)

        # 4. 提交表單（處理實際庫存扣減與異動紀錄）
        with st.form("form_warehouse_transaction_action"):
            t_note = st.text_input(curr_t["note_label"], placeholder="例如: 專案領料、廠商送貨入庫 / Ghi chú...")
            t_operator = st.text_input(curr_t["operator_label"], value="倉庫管理員")

            submitted = st.form_submit_button(curr_t["submit_btn"], type="primary", use_container_width=True)
            if submitted:
                if not t_code or not selected_obj:
                    st.error("❌ 錯誤：請選擇有效的物料！")
                else:
                    qty_val = float(t_qty)
                    if "入庫" in t_type or "Nhập" in t_type:
                        selected_obj["qty"] += qty_val
                        log_type_str = "📥 入庫 (In)"
                    else:
                        if selected_obj["qty"] >= qty_val:
                            selected_obj["qty"] -= qty_val
                            log_type_str = "📤 出庫 (Out)"
                        else:
                            st.error("❌ 庫存不足，無法出庫！")
                            st.stop()

                    selected_obj["updated"] = str(datetime.date.today())
                    
                    st.session_state.warehouse_logs_db.insert(0, {
                        "log_id": f"LOG-2026-{len(st.session_state.warehouse_logs_db)+1:03d}",
                        "type": log_type_str,
                        "item_code": selected_obj["item_code"],
                        "item_name": selected_obj["item_name"],
                        "qty": qty_val,
                        "operator": t_operator,
                        "date": str(datetime.date.today()),
                        "note": f"{t_note} [儲位:{selected_obj['location']}]"
                    })
                    st.success(f"🎉 庫存異動成功！儲位：**{selected_obj['location']}**，最新庫存：{selected_obj['qty']} {selected_obj['unit']}")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"##### {curr_t['log_title']}")
        if st.session_state.warehouse_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.warehouse_logs_db), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # Tab 3: 安全庫存預警
    # ----------------------------------------------------
    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示監控 (Cảnh báo tồn kho)")
        low_stock_items = [i for i in st.session_state.warehouse_inventory_db if i["qty"] <= i["safety_stock"]]
        if low_stock_items:
            st.warning("⚠️ 以下物料庫存已低於安全水位，請盡速補貨！")
            for item in low_stock_items:
                st.error(f"儲位: **{item['location']}** | 料號: `{item['item_code']}` | 品名: {item['item_name']} | 現有庫存: {item['qty']} {item['unit']}")
        else:
            st.success("🟢 目前所有倉庫物料庫存皆高於安全水位，供應鏈狀態正常！")

    # ----------------------------------------------------
    # Tab 4: 物料建檔、照片與條碼維護
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("##### ⚙️ 倉庫資材主檔、照片與條碼/儲位維護")
        action_mode = st.radio("選擇維護動作 / Chọn thao tác", ["➕ 新增資材與照片/條碼/儲位", "✏️ 修改現有資材、照片與儲位", "🗑️ 移除資材品項"], horizontal=True)
        st.markdown("---")

        if action_mode == "➕ 新增資材與照片/條碼/儲位":
            with st.form("form_add_item"):
                c1, c2 = st.columns(2)
                with c1:
                    new_code = st.text_input("料號 (Item Code) *", placeholder="例如: MCCB-600L")
                    new_name = st.text_input("品名規格名稱 (Item Name) *", placeholder="例如: 600A 無熔絲開關")
                    new_cat = st.text_input("資材類別 / 分類 *", placeholder="例如: 配電元件")
                    new_spec = st.text_input("詳細規格 (Specification)", placeholder="例如: TBX-600L")
                with c2:
                    new_barcode = st.text_input("條碼 / QR Code 編號 *", placeholder="例如: 893500123405")
                    new_loc = st.text_input("倉庫儲位 / 分區位置 *", placeholder="例如: A區-02櫃 或 B區-05架")
                    new_qty = st.number_input("初始庫存數量 (Initial Qty)", min_value=0.0, value=10.0)
                    new_unit = st.text_input("計量單位 (Unit) *", value="只")
                    new_safety = st.number_input("安全庫存水位 (Safety Stock)", min_value=0.0, value=5.0)

                uploaded_file = st.file_uploader("📷 上傳物品外觀照片 (供新進員工識別)", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("💾 確認新增資材", type="primary", use_container_width=True):
                    if new_code and new_name and new_cat and new_unit and new_loc:
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
                            st.success(f"✅ 成功新增資材與儲位 [{new_loc}]：`{new_code} - {new_name}`！")
                            st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫所有必填欄位！")

        elif action_mode == "✏️ 修改現有資材、照片與儲位":
            if not st.session_state.warehouse_inventory_db:
                st.info("目前無任何資材可供修改。")
            else:
                edit_target_str = st.selectbox("選擇要修改的資材料號", [f"{i['item_code']} - {i['item_name']} (儲位:{i['location']})" for i in st.session_state.warehouse_inventory_db])
                target_code = edit_target_str.split(" - ")[0]
                target_item = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == target_code), None)

                if target_item:
                    with st.form("form_edit_item"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            edit_name = st.text_input("品名規格名稱", value=target_item["item_name"])
                            edit_cat = st.text_input("資材類別 / 分類", value=target_item["category"])
                            edit_spec = st.text_input("詳細規格", value=target_item["spec"])
                            edit_barcode = st.text_input("條碼 / QR Code 編號", value=target_item.get("barcode", ""))
                        with ec2:
                            edit_loc = st.text_input("倉庫儲位 / 分區位置", value=target_item["location"])
                            edit_qty = st.number_input("現有庫存數量", min_value=0.0, value=float(target_item["qty"]))
                            edit_unit = st.text_input("計量單位", value=target_item["unit"])
                            edit_safety = st.number_input("安全庫存水位", min_value=0.0, value=float(target_item["safety_stock"]))

                        edit_photo = st.file_uploader("📷 更新物品照片", type=["jpg", "png", "jpeg"], key="edit_photo_upload")

                        if st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True):
                            target_item["item_name"] = edit_name.strip()
                            target_item["category"] = edit_cat.strip()
                            target_item["spec"] = edit_spec.strip()
                            target_item["barcode"] = edit_barcode.strip()
                            target_item["location"] = edit_loc.strip()
                            target_item["qty"] = edit_qty
                            target_item["unit"] = edit_unit.strip()
                            target_item["safety_stock"] = edit_safety
                            target_item["updated"] = str(datetime.date.today())
                            if edit_photo:
                                target_item["photo"] = edit_photo

                            st.success(f"✅ 料號 `{target_code}` 的儲位 **{edit_loc}** 與資料已成功更新！")
                            st.rerun()

        elif action_mode == "🗑️ 移除資材品項":
            if not st.session_state.warehouse_inventory_db:
                st.info("目前無任何資材可供移除。")
            else:
                del_target_str = st.selectbox("選擇要移除的資材料號", [f"{i['item_code']} - {i['item_name']} (儲位:{i['location']})" for i in st.session_state.warehouse_inventory_db], key="del_select")
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
