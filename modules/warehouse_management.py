import streamlit as st
import pandas as pd
import datetime

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    ui_texts = {
        "繁體中文": {
            "title": "📦 裕豐電機 (REETECH) - 倉庫直覺化管理與快速出入庫",
            "info": "💡 專為現場同仁設計：點選分區與物品，系統即時顯示照片與正確儲位，滑鼠點兩下輕鬆完成領料與入庫。",
            "tab1": "📊 即時庫存總表與照片預覽",
            "tab2": "📥📤 快速出入庫領料作業 (極簡直覺)",
            "tab3": "⚠️ 安全庫存預警",
            "tab4": "⚙️ 物料建檔與照片條碼維護",
            "search_box": "🔍 搜尋料號、名稱或儲位...",
            "zone_label": "1️⃣ 選擇倉庫分區 (Zone)",
            "all_zone": "全部倉庫分區",
            "item_label": "2️⃣ 選擇物品 (看照片與儲位確認)",
            "trans_type": "3️⃣ 選擇作業類型",
            "trans_in": "📥 物料入庫 (Stock In)",
            "trans_out": "📤 出庫領料 (Stock Out)",
            "qty_label": "4️⃣ 輸入異動數量",
            "note_label": "5️⃣ 備註說明 (選填)",
            "operator_label": "經辦人員",
            "submit_btn": "🚀 確認執行出入庫",
            "log_title": "📋 近期庫存異動日誌"
        },
        "越南文 (Tiếng Việt)": {
            "title": "📦 REETECH - Quản lý Kho Trực quan & Nhập Xuất Nhanh",
            "info": "💡 Dành cho nhân viên: Chọn khu vực và vật tư, hệ thống hiện ngay ảnh và vị trí kệ kho.",
            "tab1": "📊 Tổng hợp tồn kho & Xem ảnh",
            "tab2": "📥📤 Nhập/Xuất kho nhanh (Đơn giản)",
            "tab3": "⚠️ Cảnh báo tồn kho",
            "tab4": "⚙️ Quản lý danh mục & Mã vạch",
            "search_box": "🔍 Tìm kiếm mã, tên hoặc vị trí...",
            "zone_label": "1️⃣ Chọn khu vực kho (Zone)",
            "all_zone": "Tất cả khu vực",
            "item_label": "2️⃣ Chọn vật tư (Xem ảnh & vị trí)",
            "trans_type": "3️⃣ Loại giao dịch",
            "trans_in": "📥 Nhập kho (Stock In)",
            "trans_out": "📤 Xuất kho (Stock Out)",
            "qty_label": "4️⃣ Số lượng",
            "note_label": "5️⃣ Ghi chú",
            "operator_label": "Người thao tác",
            "submit_btn": "🚀 Xác nhận thực hiện",
            "log_title": "📋 Lịch sử giao dịch kho"
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
        search_wh = st.text_input(curr_t["search_box"], key="wh_search_box")
        filtered_items = st.session_state.warehouse_inventory_db
        if search_wh:
            s_low = search_wh.lower()
            filtered_items = [i for i in filtered_items if s_low in i["item_code"].lower() or s_low in i["item_name"].lower() or s_low in i["location"].lower()]

        if filtered_items:
            for item in filtered_items:
                with st.container():
                    c_photo, c_info, c_status = st.columns([1.5, 3.5, 1.5])
                    with c_photo:
                        if item.get("photo"):
                            st.image(item["photo"], caption=item['item_code'], width=100)
                        else:
                            st.markdown("📷 `無照片`")
                    with c_info:
                        st.markdown(f"**📦 [{item['item_code']}] {item['item_name']}**")
                        st.write(f"📁 類別: `{item['category']}` | 📍 儲位: **{item['location']}**")
                        st.write(f"📊 現有庫存: **{item['qty']} {item['unit']}** (安全水位: {item['safety_stock']})")
                    with c_status:
                        is_normal = item["qty"] > item["safety_stock"]
                        color_str = "green" if is_normal else "red"
                        text_str = "🟢 正常" if is_normal else "🔴 偏低"
                        st.markdown(f":{color_str}[{text_str}]")
                st.markdown("---")
        else:
            st.info("目前無符合條件的庫存紀錄。")

    # ----------------------------------------------------
    # Tab 2: 快速出入庫領料作業（左右直覺對照設計）
    # ----------------------------------------------------
    with tab_in_out:
        st.markdown(f"##### {curr_t['tab2']}")

        # 步驟 1 & 2：分區篩選與物品選擇
        all_zones = sorted(list(set([i["location"].split("-")[0] if "-" in i["location"] else i["location"] for i in st.session_state.warehouse_inventory_db])))
        zone_choices = [curr_t["all_zone"]] + all_zones
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            chosen_zone = st.selectbox(curr_t["zone_label"], zone_choices, key="simple_zone_box")
        
        pool = st.session_state.warehouse_inventory_db
        if chosen_zone != curr_t["all_zone"]:
            pool = [i for i in pool if chosen_zone in i["location"]]

        item_labels = [f"{i['item_code']} ➔ {i['item_name']} (儲位: {i['location']})" for i in pool] if pool else []

        with col_sel2:
            chosen_item_str = st.selectbox(curr_t["item_label"], item_labels, key="simple_item_box") if item_labels else ""

        st.markdown("---")

        # 核心亮點：選定物品後，立刻以「左右大圖對照」顯示物品長相與正確儲位，絕不弄錯！
        selected_item_obj = None
        if chosen_item_str:
            target_code = chosen_item_str.split(" ➔ ")[0]
            selected_item_obj = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == target_code), None)

        if selected_item_obj:
            col_preview_img, col_preview_info = st.columns([1, 2])
            with col_preview_img:
                st.markdown("##### 📷 實物照片辨識")
                if selected_item_obj.get("photo"):
                    st.image(selected_item_obj["photo"], width=180)
                else:
                    st.warning("⚠️ 尚未上傳照片，建議至分頁4補拍上傳")
            with col_preview_info:
                st.markdown("##### 📍 正確出入倉位置確認")
                st.success(f"""
                - **料號代碼**：`{selected_item_obj['item_code']}`
                - **物品名稱**：{selected_item_obj['item_name']}
                - **資材分類**：{selected_item_obj['category']}
                - **🎯 正確儲位/分區**：**{selected_item_obj['location']}**
                - **🏷️ 條碼編號**：`{selected_item_obj.get('barcode', 'N/A')}`
                - **📊 目前即時庫存**：**{selected_item_obj['qty']} {selected_item_obj['unit']}**
                """)

        st.markdown("---")

        # 步驟 3, 4, 5：交易執行
        with st.form("simple_transaction_form"):
            tc1, tc2 = st.columns(2)
            with tc1:
                t_type = st.selectbox(curr_t["trans_type"], [curr_t["trans_in"], curr_t["trans_out"]])
            with tc2:
                t_qty = st.number_input(curr_t["qty_label"], min_value=1.0, value=1.0)

            t_note = st.text_input(curr_t["note_label"], placeholder="例如: 專案領料、廠商送貨...")
            t_operator = st.text_input(curr_t["operator_label"], value="倉庫管理員")

            if st.form_submit_button(curr_t["submit_btn"], type="primary", use_container_width=True):
                if not chosen_item_str or not selected_item_obj:
                    st.error("❌ 請先選擇正確的物品！")
                else:
                    qty_val = float(t_qty)
                    if "入庫" in t_type or "Nhập" in t_type:
                        selected_item_obj["qty"] += qty_val
                        log_type = "📥 入庫 (In)"
                    else:
                        if selected_item_obj["qty"] >= qty_val:
                            selected_item_obj["qty"] -= qty_val
                            log_type = "📤 出庫 (Out)"
                        else:
                            st.error("❌ 庫存數量不足，無法出庫！")
                            st.stop()

                    selected_item_obj["updated"] = str(datetime.date.today())
                    st.session_state.warehouse_logs_db.insert(0, {
                        "log_id": f"LOG-2026-{len(st.session_state.warehouse_logs_db)+1:03d}",
                        "type": log_type,
                        "item_code": selected_item_obj["item_code"],
                        "item_name": selected_item_obj["item_name"],
                        "qty": qty_val,
                        "operator": t_operator,
                        "date": str(datetime.date.today()),
                        "note": f"{t_note} [儲位:{selected_item_obj['location']}]"
                    })
                    st.success(f"🎉 執行成功！儲位 [{selected_item_obj['location']}] 最新庫存：{selected_item_obj['qty']} {selected_item_obj['unit']}")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"##### {curr_t['log_title']}")
        if st.session_state.warehouse_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.warehouse_logs_db), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # Tab 3: 安全庫存預警
    # ----------------------------------------------------
    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示")
        low_items = [i for i in st.session_state.warehouse_inventory_db if i["qty"] <= i["safety_stock"]]
        if low_items:
            for item in low_items:
                st.error(f"儲位: **{item['location']}** | 料號: `{item['item_code']}` | 品名: {item['item_name']} | 現有: {item['qty']} {item['unit']}")
        else:
            st.success("🟢 所有庫存水位正常！")

    # ----------------------------------------------------
    # Tab 4: 物料建檔與照片維護
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("##### ⚙️ 物料建檔、照片與儲位維護")
        action_mode = st.radio("選擇操作", ["➕ 新增物料與上傳照片", "✏️ 修改物料資訊與照片", "🗑️ 刪除物料"], horizontal=True)
        st.markdown("---")

        if action_mode == "➕ 新增物料與上傳照片":
            with st.form("add_item_simple"):
                c1, c2 = st.columns(2)
                with c1:
                    n_code = st.text_input("料號 (Item Code) *")
                    n_name = st.text_input("品名規格 *")
                    n_cat = st.text_input("類別 *", value="配電元件")
                    n_spec = st.text_input("詳細規格")
                with c2:
                    n_barcode = st.text_input("條碼 / QR Code *", value="893500123499")
                    n_loc = st.text_input("倉庫儲位/分區 *", value="A區-02櫃")
                    n_qty = st.number_input("初始庫存", value=10.0)
                    n_unit = st.text_input("單位", value="只")
                    n_safe = st.number_input("安全水位", value=5.0)

                up_file = st.file_uploader("📷 上傳物品照片 (讓新進員工一眼看懂)", type=["jpg", "png", "jpeg"])

                if st.form_submit_button("💾 儲存新物料", type="primary", use_container_width=True):
                    if n_code and n_name and n_loc:
                        st.session_state.warehouse_inventory_db.append({
                            "item_code": n_code.strip(),
                            "item_name": n_name.strip(),
                            "category": n_cat.strip(),
                            "spec": n_spec.strip(),
                            "barcode": n_barcode.strip(),
                            "qty": n_qty,
                            "unit": n_unit.strip(),
                            "safety_stock": n_safe,
                            "location": n_loc.strip(),
                            "updated": str(datetime.date.today()),
                            "photo": up_file
                        })
                        st.success(f"✅ 成功新增：{n_code}")
                        st.rerun()
                    else:
                        st.warning("請填寫必填欄位！")

        elif action_mode == "✏️ 修改物料資訊與照片":
            if not st.session_state.warehouse_inventory_db:
                st.info("無物料可修改")
            else:
                edit_str = st.selectbox("選擇物料", [f"{i['item_code']} - {i['item_name']} (儲位:{i['location']})" for i in st.session_state.warehouse_inventory_db])
                t_code = edit_str.split(" - ")[0]
                t_obj = next((i for i in st.session_state.warehouse_inventory_db if i["item_code"] == t_code), None)
                if t_obj:
                    with st.form("edit_item_simple"):
                        e_name = st.text_input("品名", value=t_obj["item_name"])
                        e_loc = st.text_input("儲位", value=t_obj["location"])
                        e_qty = st.number_input("庫存量", value=float(t_obj["qty"]))
                        e_photo = st.file_uploader("更新照片", type=["jpg", "png", "jpeg"])
                        if st.form_submit_button("💾 更新"):
                            t_obj["item_name"] = e_name
                            t_obj["location"] = e_loc
                            t_obj["qty"] = e_qty
                            if e_photo:
                                t_obj["photo"] = e_photo
                            st.success("更新成功！")
                            st.rerun()

        elif action_mode == "🗑️ 刪除物料":
            if st.session_state.warehouse_inventory_db:
                del_str = st.selectbox("選擇要刪除的物料", [i["item_code"] for i in st.session_state.warehouse_inventory_db])
                if st.button("🗑️ 確認刪除", type="primary"):
                    st.session_state.warehouse_inventory_db = [i for i in st.session_state.warehouse_inventory_db if i["item_code"] != del_str]
                    st.success("已刪除！")
                    st.rerun()

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
