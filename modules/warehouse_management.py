import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_warehouse_db(engine):
    """初始化倉庫管理相關資料表（如果不存在則自動建立）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_inventory (
                    item_code VARCHAR(50) PRIMARY KEY,
                    item_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    spec VARCHAR(200),
                    barcode VARCHAR(100),
                    qty FLOAT DEFAULT 0,
                    unit VARCHAR(20) DEFAULT '只',
                    safety_stock FLOAT DEFAULT 5,
                    location VARCHAR(100),
                    updated VARCHAR(50),
                    photo_path TEXT
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_logs (
                    log_id VARCHAR(50) PRIMARY KEY,
                    type VARCHAR(50),
                    item_code VARCHAR(50),
                    item_name VARCHAR(200),
                    qty FLOAT,
                    operator VARCHAR(100),
                    date VARCHAR(50),
                    note TEXT
                );
            """))
    except Exception as e:
        st.error(f"資料庫初始化失敗: {e}")

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    # 確保資料庫與資料表存在
    if engine:
        init_warehouse_db(engine)

    current_logged_user = "admin"
    if "username" in st.session_state and st.session_state.username:
        current_logged_user = st.session_state.username

    ui_texts = {
        "繁體中文": {
            "title": "📦 裕豐電機 (REETECH) - 倉庫直覺化資料庫管理與快速出入庫",
            "info": "💡 資料已全面對接企業資料庫 (PostgreSQL)，重新整理絕不遺失，支援即時庫存查詢、分區確認與出入庫追溯。",
            "tab1": "📊 即時庫存總表與剩餘數量查詢",
            "tab2": "📥📤 快速出入庫領料作業 (極簡直覺)",
            "tab3": "⚠️ 安全庫存預警 (自訂安全水位)",
            "tab4": "⚙️ 物料建檔、照片與條碼維護",
            "search_box": "🔍 搜尋料號、名稱、條碼或儲位...",
            "zone_label": "1️⃣ 選擇倉庫分區 (Zone)",
            "all_zone": "全部倉庫分區",
            "item_label": "2️⃣ 選擇物品 (看儲位與庫存確認)",
            "trans_type": "3️⃣ 選擇作業類型",
            "trans_in": "📥 物料入庫 (Stock In)",
            "trans_out": "📤 出庫領料 (Stock Out)",
            "qty_label": "4️⃣ 輸入異動數量",
            "note_label": "5️⃣ 備註說明 (選填)",
            "operator_label": "經辦人員 (系統自動綁定登入帳號)",
            "submit_btn": "🚀 確認執行出入庫",
            "log_title": "📋 近期庫存異動日誌 (真實資料庫記錄)"
        },
        "越南文 (Tiếng Việt)": {
            "title": "📦 REETECH - Quản lý Kho Cơ sở dữ liệu & Nhập Xuất Nhanh",
            "info": "💡 Dữ liệu được kết nối trực tiếp với CSDL PostgreSQL, không bị mất khi F5, hỗ trợ tra cứu tồn kho.",
            "tab1": "📊 Tổng hợp tồn kho & Tra cứu số lượng",
            "tab2": "📥📤 Nhập/Xuất kho nhanh",
            "tab3": "⚠️ Cảnh báo tồn kho an toàn",
            "tab4": "⚙️ Quản lý danh mục & Mã vạch",
            "search_box": "🔍 Tìm kiếm mã, tên, mã vạch hoặc vị trí...",
            "zone_label": "1️⃣ Chọn khu vực kho (Zone)",
            "all_zone": "Tất cả khu vực",
            "item_label": "2️⃣ Chọn vật tư",
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

    # 從資料庫載入庫存與日誌
    inventory_db = []
    logs_db = []
    if engine:
        try:
            with engine.connect() as conn:
                res_inv = conn.execute(text("SELECT * FROM warehouse_inventory")).fetchall()
                for r in res_inv:
                    inventory_db.append({
                        "item_code": r[0], "item_name": r[1], "category": r[2], "spec": r[3],
                        "barcode": r[4], "qty": r[5], "unit": r[6], "safety_stock": r[7],
                        "location": r[8], "updated": r[9], "photo": r[10]
                    })
                res_logs = conn.execute(text("SELECT * FROM warehouse_logs ORDER BY date DESC, log_id DESC")).fetchall()
                for r in res_logs:
                    logs_db.append({
                        "log_id": r[0], "type": r[1], "item_code": r[2], "item_name": r[3],
                        "qty": r[4], "operator": r[5], "date": r[6], "note": r[7]
                    })
        except Exception as e:
            st.error(f"讀取資料庫失敗: {e}")

    tab_inv, tab_in_out, tab_alert, tab_manage = st.tabs([
        curr_t["tab1"], curr_t["tab2"], curr_t["tab3"], curr_t["tab4"]
    ])

    # ----------------------------------------------------
    # Tab 1: 即時庫存總表與剩餘數量查詢
    # ----------------------------------------------------
    with tab_inv:
        st.markdown("##### 📊 全廠各品項即時庫存與剩餘數量總覽 (資料庫連線中)")
        search_wh = st.text_input(curr_t["search_box"], key="wh_search_box")
        
        filtered_items = inventory_db
        if search_wh:
            s_low = search_wh.lower()
            filtered_items = [i for i in filtered_items if s_low in i["item_code"].lower() or s_low in i["item_name"].lower() or s_low in i["location"].lower() or s_low in str(i.get("barcode", "")).lower()]

        if filtered_items:
            for item in filtered_items:
                with st.container():
                    c_photo, c_info, c_status = st.columns([1.5, 3.5, 1.5])
                    with c_photo:
                        if item.get("photo") and str(item["photo"]).startswith("http"):
                            st.image(item["photo"], caption=item['item_code'], width=100)
                        else:
                            st.markdown("📷 `資料庫無圖檔`")
                    with c_info:
                        st.markdown(f"**📦 [{item['item_code']}] {item['item_name']}**")
                        st.write(f"📁 類別: `{item['category']}` | 📍 儲位: **{item['location']}** | 🏷️ 條碼: `{item.get('barcode', 'N/A')}`")
                        st.markdown(f"📊 **剩餘庫存數量：`{item['qty']} {item['unit']}`** (安全水位警戒線：{item['safety_stock']})")
                    with c_status:
                        is_normal = item["qty"] > item["safety_stock"]
                        color_str = "green" if is_normal else "red"
                        text_str = "🟢 庫存充足" if is_normal else "🔴 低於安全水位"
                        st.markdown(f":{color_str}[{text_str}]")
                        st.caption(f"最後更新: {item['updated']}")
                st.markdown("---")
        else:
            st.info("資料庫目前無符合搜尋條件的庫存紀錄，請至分頁4新增物料。")

    # ----------------------------------------------------
    # Tab 2: 快速出入庫領料作業
    # ----------------------------------------------------
    with tab_in_out:
        st.markdown(f"##### {curr_t['tab2']}")

        all_zones = sorted(list(set([i["location"].split("-")[0] if "-" in i["location"] else i["location"] for i in inventory_db])))
        zone_choices = [curr_t["all_zone"]] + all_zones
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            chosen_zone = st.selectbox(curr_t["zone_label"], zone_choices, key="simple_zone_box")
        
        pool = inventory_db
        if chosen_zone != curr_t["all_zone"]:
            pool = [i for i in pool if chosen_zone in i["location"]]

        item_labels = [f"{i['item_code']} ➔ {i['item_name']} (庫存: {i['qty']} {i['unit']} | 儲位: {i['location']})" for i in pool] if pool else []

        with col_sel2:
            chosen_item_str = st.selectbox(curr_t["item_label"], item_labels, key="simple_item_box") if item_labels else ""

        st.markdown("---")

        selected_item_obj = None
        if chosen_item_str:
            target_code = chosen_item_str.split(" ➔ ")[0]
            selected_item_obj = next((i for i in inventory_db if i["item_code"] == target_code), None)

        if selected_item_obj:
            col_preview_img, col_preview_info = st.columns([1, 2])
            with col_preview_img:
                st.markdown("##### 📷 實物照片辨識")
                if selected_item_obj.get("photo") and str(selected_item_obj["photo"]).startswith("http"):
                    st.image(selected_item_obj["photo"], width=180)
                else:
                    st.warning("⚠️ 尚未上傳照片")
            with col_preview_info:
                st.markdown("##### 📍 正確出入倉位置確認")
                st.success(f"""
                - **料號代碼**：`{selected_item_obj['item_code']}`
                - **物品名稱**：{selected_item_obj['item_name']}
                - **資材分類**：{selected_item_obj['category']}
                - **🎯 正確儲位/分區**：**{selected_item_obj['location']}**
                - **🏷️ 條碼編號**：`{selected_item_obj.get('barcode', 'N/A')}`
                - **📊 目前即時庫存**：**{selected_item_obj['qty']} {selected_item_obj['unit']}** (安全水位: {selected_item_obj['safety_stock']})
                """)

        st.markdown("---")

        with st.form("simple_transaction_form"):
            tc1, tc2 = st.columns(2)
            with tc1:
                t_type = st.selectbox(curr_t["trans_type"], [curr_t["trans_in"], curr_t["trans_out"]])
            with tc2:
                t_qty = st.number_input(curr_t["qty_label"], min_value=1.0, value=1.0)

            t_note = st.text_input(curr_t["note_label"], placeholder="例如: 專案領料、廠商送貨...")
            st.text_input(curr_t["operator_label"], value=str(current_logged_user), disabled=True)

            if st.form_submit_button(curr_t["submit_btn"], type="primary", use_container_width=True):
                if not chosen_item_str or not selected_item_obj:
                    st.error("❌ 請先選擇正確的物品！")
                else:
                    qty_val = float(t_qty)
                    new_qty = selected_item_obj["qty"]
                    if "入庫" in t_type or "Nhập" in t_type:
                        new_qty += qty_val
                        log_type = "📥 入庫 (In)"
                    else:
                        if new_qty >= qty_val:
                            new_qty -= qty_val
                            log_type = "📤 出庫 (Out)"
                        else:
                            st.error("❌ 資料庫庫存數量不足，無法出庫！")
                            st.stop()

                    today_str = str(datetime.date.today())
                    new_log_id = f"LOG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

                    if engine:
                        try:
                            with engine.begin() as conn:
                                # 更新庫存
                                conn.execute(text(
                                    "UPDATE warehouse_inventory SET qty = :q, updated = :u WHERE item_code = :c"
                                ), {"q": new_qty, "u": today_str, "c": selected_item_obj["item_code"]})
                                
                                # 寫入異動日誌
                                conn.execute(text(
                                    """INSERT INTO warehouse_logs (log_id, type, item_code, item_name, qty, operator, date, note)
                                       VALUES (:id, :t, :c, :n, :q, :op, :d, :note)"""
                                ), {
                                    "id": new_log_id, "t": log_type, "c": selected_item_obj["item_code"],
                                    "n": selected_item_obj["item_name"], "q": qty_val, "op": str(current_logged_user),
                                    "d": today_str, "note": f"{t_note} [儲位:{selected_item_obj['location']}]"
                                })
                            st.success(f"🎉 資料庫更新成功！經辦：[{current_logged_user}]，最新庫存：{new_qty} {selected_item_obj['unit']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"寫入資料庫發生錯誤: {e}")

        st.markdown("---")
        st.markdown(f"##### {curr_t['log_title']}")
        if logs_db:
            st.dataframe(pd.DataFrame(logs_db), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # Tab 3: 安全庫存預警
    # ----------------------------------------------------
    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示監控 (資料庫即時比對)")
        low_items = [i for i in inventory_db if i["qty"] <= i["safety_stock"]]
        if low_items:
            st.warning("⚠️ 以下資料庫物料庫存已低於安全水位，請盡速補貨！")
            for item in low_items:
                st.error(f"儲位: **{item['location']}** | 料號: `{item['item_code']}` | 品名: {item['item_name']} | 現有庫存: **{item['qty']} {item['unit']}** (安全水位要求: {item['safety_stock']})")
        else:
            st.success("🟢 目前資料庫中所有倉庫物料的剩餘庫存皆高於安全水位！")

    # ----------------------------------------------------
    # Tab 4: 物料建檔、照片與安全水位設定 (全面寫入資料庫)
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("##### ⚙️ 物料建檔、照片與安全水位設定 (直接寫入資料庫)")
        action_mode = st.radio("選擇操作", ["➕ 新增物料與設定安全水位", "✏️ 修改物料、庫存與安全水位", "🗑️ 刪除物料"], horizontal=True)
        st.markdown("---")

        if action_mode == "➕ 新增物料與設定安全水位":
            with st.form("add_item_db"):
                c1, c2 = st.columns(2)
                with c1:
                    n_code = st.text_input("料號 (Item Code) *", placeholder="例如: MCCB-600L")
                    n_name = st.text_input("品名規格 *", placeholder="例如: 600A 無熔絲開關")
                    n_cat = st.text_input("類別 *", value="配電元件")
                    n_spec = st.text_input("詳細規格")
                with c2:
                    n_barcode = st.text_input("條碼 / QR Code *", value="893500123499")
                    n_loc = st.text_input("倉庫儲位/分區 *", value="A區-02櫃")
                    n_qty = st.number_input("初始庫存數量", value=10.0)
                    n_unit = st.text_input("單位", value="只")
                    n_safe = st.number_input("安全水位警戒值", value=5.0)

                up_file = st.text_input("📷 圖片網址 (URL) 或留空", placeholder="https://...")

                if st.form_submit_button("💾 儲存新物料至資料庫", type="primary", use_container_width=True):
                    if n_code and n_name and n_loc:
                        if engine:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        INSERT INTO warehouse_inventory (item_code, item_name, category, spec, barcode, qty, unit, safety_stock, location, updated, photo_path)
                                        VALUES (:c, :n, :cat, :s, :b, :q, :u, :safe, :loc, :up, :p)
                                        ON CONFLICT (item_code) DO UPDATE SET
                                        item_name = EXCLUDED.item_name, category = EXCLUDED.category, qty = EXCLUDED.qty
                                    """), {
                                        "c": n_code.strip(), "n": n_name.strip(), "cat": n_cat.strip(), "s": n_spec.strip(),
                                        "b": n_barcode.strip(), "q": n_qty, "u": n_unit.strip(), "safe": n_safe,
                                        "loc": n_loc.strip(), "up": str(datetime.date.today()), "p": up_file if up_file else None
                                    })
                                st.success(f"✅ 成功將料號 `{n_code}` 寫入資料庫！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"寫入資料庫失敗: {e}")
                    else:
                        st.warning("請填寫必填欄位！")

        elif action_mode == "✏️ 修改物料、庫存與安全水位":
            if not inventory_db:
                st.info("資料庫中無物料可修改")
            else:
                edit_str = st.selectbox("選擇物料", [f"{i['item_code']} - {i['item_name']} (現有庫存: {i['qty']} {i['unit']})" for i in inventory_db])
                t_code = edit_str.split(" - ")[0]
                t_obj = next((i for i in inventory_db if i["item_code"] == t_code), None)
                if t_obj:
                    with st.form("edit_item_db"):
                        e_name = st.text_input("品名", value=t_obj["item_name"])
                        e_loc = st.text_input("儲位", value=t_obj["location"])
                        e_qty = st.number_input("現有庫存數量", value=float(t_obj["qty"]))
                        e_safe = st.number_input("安全水位警戒值", value=float(t_obj.get("safety_stock", 5.0)))
                        e_photo = st.text_input("圖片網址 (URL)", value=t_obj.get("photo", "") or "")
                        if st.form_submit_button("💾 更新資料庫"):
                            if engine:
                                try:
                                    with engine.begin() as conn:
                                        conn.execute(text("""
                                            UPDATE warehouse_inventory 
                                            SET item_name = :n, location = :l, qty = :q, safety_stock = :s, updated = :u, photo_path = :p
                                            WHERE item_code = :c
                                        """), {
                                            "n": e_name, "l": e_loc, "q": e_qty, "s": e_safe,
                                            "u": str(datetime.date.today()), "p": e_photo if e_photo else None, "c": t_code
                                        })
                                    st.success("資料庫更新成功！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失敗: {e}")

        elif action_mode == "🗑️ 刪除物料":
            if inventory_db:
                del_str = st.selectbox("選擇要刪除的料號", [i["item_code"] for i in inventory_db])
                if st.button("🗑️ 確認從資料庫永久刪除", type="primary"):
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("DELETE FROM warehouse_inventory WHERE item_code = :c"), {"c": del_str})
                            st.success(f"已從資料庫刪除料號 {del_str}！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"刪除失敗: {e}")

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
