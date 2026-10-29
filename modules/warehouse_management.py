import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_warehouse_db(engine):
    """初始化倉庫管理相關資料表，並自動檢查補齊缺少的欄位（確保平滑升級）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # 1. 建立 warehouse_inventory 主檔表
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

            # 2. 建立 warehouse_logs 日誌表
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

            # 3. 建立 warehouse_stocktaking 盤點表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_stocktaking (
                    check_id VARCHAR(50) PRIMARY KEY,
                    item_code VARCHAR(50),
                    item_name VARCHAR(200),
                    location VARCHAR(100),
                    book_qty FLOAT,
                    actual_qty FLOAT,
                    diff_qty FLOAT,
                    operator VARCHAR(100),
                    check_date VARCHAR(50),
                    status VARCHAR(50)
                );
            """))

            # 自動檢查並補齊可能缺少的欄位（針對既有舊資料表）
            for col_sql in [
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS safety_stock FLOAT DEFAULT 5;",
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS barcode VARCHAR(100);",
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS photo_path TEXT;",
                "ALTER TABLE warehouse_logs ADD COLUMN IF NOT EXISTS date VARCHAR(50);",
                "ALTER TABLE warehouse_logs ADD COLUMN IF NOT EXISTS note TEXT;"
            ]:
                try:
                    conn.execute(text(col_sql))
                except Exception:
                    pass

    except Exception as e:
        st.error(f"資料庫初始化失敗: {e}")

def render_warehouse_management(engine=None, t=None, lang="繁體中文", **kwargs):
    if engine:
        init_warehouse_db(engine)

    current_logged_user = "admin"
    if "username" in st.session_state and st.session_state.username:
        current_logged_user = st.session_state.username

    ui_texts = {
        "繁體中文": {
            "title": "📦 裕豐電機 (REETECH) - 管理部轄下：倉庫直覺化管理與智慧盤點系統",
            "info": "💡 歸屬管理部管轄。支援即時庫存查詢、快速出入庫、安全水位警示、物料維護，以及【列印紙本盤點表】與【平板線上盤點】雙模式！",
            "tab1": "📊 即時庫存總表與查詢",
            "tab2": "📥📤 快速出入庫領料",
            "tab3": "📋 庫存盤點作業 (支援列印與平板線上盤點)",
            "tab4": "⚠️ 安全庫存預警",
            "tab5": "⚙️ 物料建檔與維護",
            "search_box": "🔍 搜尋料號、名稱、條碼或儲位..."
        },
        "越南文 (Tiếng Việt)": {
            "title": "📦 REETECH - Quản lý Kho & Kiểm kê Thông minh",
            "info": "💡 Trực thuộc Bộ phận Quản lý. Hỗ trợ kiểm kê trực tuyến qua máy tính bảng và in phiếu kiểm kê.",
            "tab1": "📊 Tổng hợp tồn kho",
            "tab2": "📥📤 Nhập/Xuất kho",
            "tab3": "📋 Kiểm kê kho (In ấn & Trực tuyến)",
            "tab4": "⚠️ Cảnh báo tồn kho",
            "tab5": "⚙️ Quản lý danh mục",
            "search_box": "🔍 Tìm kiếm mã, tên, mã vạch..."
        }
    }

    curr_t = ui_texts.get(lang, ui_texts["繁體中文"])

    st.markdown(f"### {curr_t['title']}")
    st.info(curr_t['info'])

    inventory_db = []
    logs_db = []
    stocktake_db = []
    if engine:
        try:
            with engine.connect() as conn:
                res_inv = conn.execute(text("SELECT * FROM warehouse_inventory")).fetchall()
                for r in res_inv:
                    inventory_db.append({
                        "item_code": r[0], "item_name": r[1], "category": r[2], "spec": r[3],
                        "barcode": r[4] if len(r) > 4 else "", 
                        "qty": r[5] if len(r) > 5 else 0, 
                        "unit": r[6] if len(r) > 6 else "只", 
                        "safety_stock": r[7] if len(r) > 7 else 5,
                        "location": r[8] if len(r) > 8 else "A區", 
                        "updated": r[9] if len(r) > 9 else "", 
                        "photo": r[10] if len(r) > 10 else None
                    })
                
                res_logs = conn.execute(text("SELECT * FROM warehouse_logs ORDER BY date DESC, log_id DESC")).fetchall()
                for r in res_logs:
                    logs_db.append({
                        "log_id": r[0], "type": r[1], "item_code": r[2], "item_name": r[3],
                        "qty": r[4], "operator": r[5], "date": r[6] if len(r) > 6 else "", "note": r[7] if len(r) > 7 else ""
                    })

                res_st = conn.execute(text("SELECT * FROM warehouse_stocktaking ORDER BY check_date DESC")).fetchall()
                for r in res_st:
                    stocktake_db.append({
                        "check_id": r[0], "item_code": r[1], "item_name": r[2], "location": r[3],
                        "book_qty": r[4], "actual_qty": r[5], "diff_qty": r[6], "operator": r[7],
                        "check_date": r[8], "status": r[9]
                    })
        except Exception as e:
            st.error(f"讀取資料庫失敗: {e}")

    tab_inv, tab_in_out, tab_stock, tab_alert, tab_manage = st.tabs([
        curr_t["tab1"], curr_t["tab2"], curr_t["tab3"], curr_t["tab4"], curr_t["tab5"]
    ])

    # ----------------------------------------------------
    # Tab 1: 即時庫存總表
    # ----------------------------------------------------
    with tab_inv:
        st.markdown("##### 📊 管理部倉庫：全廠各品項即時庫存總覽")
        search_wh = st.text_input(curr_t["search_box"], key="wh_search_box")
        
        filtered_items = inventory_db
        if search_wh:
            s_low = search_wh.lower()
            filtered_items = [i for i in filtered_items if s_low in str(i["item_code"]).lower() or s_low in str(i["item_name"]).lower() or s_low in str(i["location"]).lower() or s_low in str(i.get("barcode", "")).lower()]

        if filtered_items:
            for item in filtered_items:
                with st.container():
                    c_photo, c_info, c_status = st.columns([1.5, 3.5, 1.5])
                    with c_photo:
                        if item.get("photo") and str(item["photo"]).startswith("http"):
                            st.image(item["photo"], caption=item['item_code'], width=100)
                        else:
                            st.markdown("📷 `無圖檔`")
                    with c_info:
                        st.markdown(f"**📦 [{item['item_code']}] {item['item_name']}**")
                        st.write(f"📁 類別: `{item['category']}` | 📍 儲位: **{item['location']}** | 🏷️ 條碼: `{item.get('barcode', 'N/A')}`")
                        st.markdown(f"📊 **剩餘庫存：`{item['qty']} {item['unit']}`** (安全水位: {item['safety_stock']})")
                    with c_status:
                        is_normal = item["qty"] > item["safety_stock"]
                        color_str = "green" if is_normal else "red"
                        text_str = "🟢 庫存充足" if is_normal else "🔴 低於安全水位"
                        st.markdown(f":{color_str}[{text_str}]")
                st.markdown("---")
        else:
            st.info("目前無符合搜尋條件的庫存紀錄。請至分頁5新增物料。")

    # ----------------------------------------------------
    # Tab 2: 快速出入庫
    # ----------------------------------------------------
    with tab_in_out:
        st.markdown("##### 📥📤 快速出入庫領料作業")
        all_zones = sorted(list(set([i["location"].split("-")[0] if "-" in str(i["location"]) else str(i["location"]) for i in inventory_db])))
        zone_choices = ["全部倉庫分區"] + all_zones
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            chosen_zone = st.selectbox("1️⃣ 選擇倉庫分區 (Zone)", zone_choices, key="simple_zone_box")
        
        pool = inventory_db
        if chosen_zone != "全部倉庫分區":
            pool = [i for i in pool if chosen_zone in str(i["location"])]

        item_labels = [f"{i['item_code']} ➔ {i['item_name']} (庫存: {i['qty']} {i['unit']} | 儲位: {i['location']})" for i in pool] if pool else []

        with col_sel2:
            chosen_item_str = st.selectbox("2️⃣ 選擇物品", item_labels, key="simple_item_box") if item_labels else ""

        st.markdown("---")
        selected_item_obj = None
        if chosen_item_str:
            target_code = chosen_item_str.split(" ➔ ")[0]
            selected_item_obj = next((i for i in inventory_db if i["item_code"] == target_code), None)

        if selected_item_obj:
            col_img, col_info = st.columns([1, 2])
            with col_img:
                if selected_item_obj.get("photo") and str(selected_item_obj["photo"]).startswith("http"):
                    st.image(selected_item_obj["photo"], width=160)
                else:
                    st.markdown("📷 `無照片`")
            with col_info:
                st.success(f"""
                - **料號**：`{selected_item_obj['item_code']}`
                - **品名**：{selected_item_obj['item_name']}
                - **🎯 正確儲位**：**{selected_item_obj['location']}**
                - **📊 現有庫存**：**{selected_item_obj['qty']} {selected_item_obj['unit']}**
                """)

        st.markdown("---")
        with st.form("simple_transaction_form"):
            tc1, tc2 = st.columns(2)
            with tc1:
                t_type = st.selectbox("3️⃣ 作業類型", ["📥 物料入庫 (Stock In)", "📤 出庫領料 (Stock Out)"])
            with tc2:
                t_qty = st.number_input("4️⃣ 數量", min_value=1.0, value=1.0)
            t_note = st.text_input("5️⃣ 備註說明", placeholder="例如: 專案領料...")
            st.text_input("經辦人員 (自動綁定)", value=str(current_logged_user), disabled=True)

            if st.form_submit_button("🚀 確認執行出入庫", type="primary", use_container_width=True):
                if not chosen_item_str or not selected_item_obj:
                    st.error("❌ 請先選擇物品！")
                else:
                    qty_val = float(t_qty)
                    new_qty = selected_item_obj["qty"]
                    if "入庫" in t_type:
                        new_qty += qty_val
                        log_type = "📥 入庫 (In)"
                    else:
                        if new_qty >= qty_val:
                            new_qty -= qty_val
                            log_type = "📤 出庫 (Out)"
                        else:
                            st.error("❌ 庫存不足！")
                            st.stop()

                    today_str = str(datetime.date.today())
                    new_log_id = f"LOG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE warehouse_inventory SET qty = :q, updated = :u WHERE item_code = :c"), {"q": new_qty, "u": today_str, "c": selected_item_obj["item_code"]})
                                conn.execute(text("""INSERT INTO warehouse_logs (log_id, type, item_code, item_name, qty, operator, date, note)
                                                   VALUES (:id, :t, :c, :n, :q, :op, :d, :note)"""), {
                                    "id": new_log_id, "t": log_type, "c": selected_item_obj["item_code"],
                                    "n": selected_item_obj["item_name"], "q": qty_val, "op": str(current_logged_user),
                                    "d": today_str, "note": f"{t_note} [儲位:{selected_item_obj['location']}]"
                                })
                            st.success(f"🎉 執行成功！最新庫存：{new_qty} {selected_item_obj['unit']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"錯誤: {e}")

        st.markdown("---")
        st.markdown("##### 📋 近期庫存異動日誌")
        if logs_db:
            st.dataframe(pd.DataFrame(logs_db), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # Tab 3: 庫存盤點作業
    # ----------------------------------------------------
    with tab_stock:
        st.markdown("##### 📋 倉庫即時盤點作業中心")
        st.info("💡 說明：支援【列印紙本盤點表】與【平板線上盤點模式】雙模式！")

        stock_mode = st.radio("選擇盤點模式", ["🖨️ 列印紙本盤點表 (供現場逐一清點)", "📱 平板線上盤點與差異結算 (Online Stocktaking)"], horizontal=True)
        st.markdown("---")

        if stock_mode == "🖨️ 列印紙本盤點表 (供現場逐一清點)":
            st.markdown("#### 裕豐電機工業 (REETECH) - 倉儲定期實地盤點表")
            st.write(f"**盤點日期**：{datetime.date.today()} | **管轄部門**：管理部倉庫 | **列印人員**：{current_logged_user}")
            
            if inventory_db:
                print_df = pd.DataFrame(inventory_db)[["location", "item_code", "item_name", "qty", "unit", "barcode"]]
                print_df.columns = ["倉庫儲位", "料號代碼", "品名規格", "帳面數量", "單位", "條碼編號"]
                print_df["實點數量 (Actual)"] = ""
                print_df["盤差 (Diff)"] = ""
                print_df["盤點簽名"] = ""

                st.dataframe(print_df, use_container_width=True, hide_index=True)
                st.markdown("📌 *提示：請按 Ctrl+P 即可直接將此頁面列印成紙本盤點表！*")
            else:
                st.warning("目前無庫存資料可列印。")

        else:
            st.markdown("#### 📱 平板線上盤點與差異結算模式")
            if not inventory_db:
                st.warning("目前無庫存可盤點。")
            else:
                with st.form("tablet_stocktake_form"):
                    st_results = []
                    for idx, item in enumerate(inventory_db):
                        cols = st.columns([2, 1, 1, 1])
                        with cols[0]:
                            st.markdown(f"**[{item['item_code']}]** {item['item_name']}<br><small>📍 儲位: {item['location']}</small>", unsafe_allow_html=True)
                        with cols[1]:
                            st.markdown(f"帳面: **{item['qty']} {item['unit']}**")
                        with cols[2]:
                            act_val = st.number_input(f"實點數_{item['item_code']}", min_value=0.0, value=float(item['qty']), key=f"st_act_{idx}")
                        with cols[3]:
                            diff = act_val - item['qty']
                            if diff == 0:
                                st.markdown(":green[🟢 正常]")
                            elif diff > 0:
                                st.markdown(f":blue[📈 盤盈 +{diff}]")
                            else:
                                st.markdown(f":red[📉 盤虧 {diff}]")
                        
                        st_results.append({
                            "item_code": item['item_code'],
                            "item_name": item['item_name'],
                            "location": item['location'],
                            "book_qty": item['qty'],
                            "actual_qty": act_val,
                            "diff_qty": diff
                        })
                        st.markdown("---")

                    st_note = st.text_input("盤點備註說明")
                    
                    if st.form_submit_button("🚀 確認送出線上盤點並更新帳面庫存", type="primary", use_container_width=True):
                        today_str = str(datetime.date.today())
                        check_batch_id = f"ST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        
                        if engine:
                            try:
                                with engine.begin() as conn:
                                    for res in st_results:
                                        conn.execute(text("UPDATE warehouse_inventory SET qty = :q, updated = :u WHERE item_code = :c"), {"q": res["actual_qty"], "u": today_str, "c": res["item_code"]})
                                        conn.execute(text("""
                                            INSERT INTO warehouse_stocktaking (check_id, item_code, item_name, location, book_qty, actual_qty, diff_qty, operator, check_date, status)
                                            VALUES (:cid, :code, :name, :loc, :bq, :aq, :dq, :op, :dt, :st)
                                        """), {
                                            "cid": f"{check_batch_id}-{res['item_code']}",
                                            "code": res["item_code"], "name": res["item_name"], "loc": res["location"],
                                            "bq": res["book_qty"], "aq": res["actual_qty"], "dq": res["diff_qty"],
                                            "op": str(current_logged_user), "dt": today_str, "st": "已結算覆核"
                                        })

                                        if res["diff_qty"] != 0:
                                            log_type = "📈 盤盈調整" if res["diff_qty"] > 0 else "📉 盤虧調整"
                                            conn.execute(text("""
                                                INSERT INTO warehouse_logs (log_id, type, item_code, item_name, qty, operator, date, note)
                                                VALUES (:id, :t, :c, :n, :q, :op, :d, :note)
                                            """), {
                                                "id": f"LOG-ST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{res['item_code']}",
                                                "t": log_type, "c": res["item_code"], "n": res["item_name"],
                                                "q": abs(res["diff_qty"]), "op": str(current_logged_user),
                                                "d": today_str, "note": f"盤點調整 [{st_note}] 帳面:{res['book_qty']} 實點:{res['actual_qty']}"
                                            })

                                st.success("🎉 線上盤點完成！庫存已自動結算更新。")
                                st.rerun()
                            except Exception as e:
                                st.error(f"寫入資料庫失敗: {e}")

        if stocktake_db:
            st.markdown("---")
            st.markdown("##### 📜 歷史盤點紀錄與差異追溯")
            st.dataframe(pd.DataFrame(stocktake_db), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # Tab 4: 安全庫存預警
    # ----------------------------------------------------
    with tab_alert:
        st.markdown("##### ⚠️ 安全庫存與缺料警示監控")
        low_items = [i for i in inventory_db if i["qty"] <= i["safety_stock"]]
        if low_items:
            st.warning("⚠️ 以下物料庫存已低於安全水位！")
            for item in low_items:
                st.error(f"儲位: **{item['location']}** | 料號: `{item['item_code']}` | 品名: {item['item_name']} | 現有庫存: **{item['qty']} {item['unit']}** (安全水位: {item['safety_stock']})")
        else:
            st.success("🟢 目前所有管理部倉庫物料之庫存水位皆正常！")

    # ----------------------------------------------------
    # Tab 5: 物料建檔與維護
    # ----------------------------------------------------
    with tab_manage:
        st.markdown("##### ⚙️ 管理部倉庫：物料建檔、照片與安全水位設定")
        action_mode = st.radio("選擇操作", ["➕ 新增物料", "✏️ 修改物料與安全水位", "🗑️ 刪除物料"], horizontal=True)
        st.markdown("---")

        if action_mode == "➕ 新增物料":
            with st.form("add_item_db"):
                c1, c2 = st.columns(2)
                with c1:
                    n_code = st.text_input("料號 (Item Code) *")
                    n_name = st.text_input("品名規格 *")
                    n_cat = st.text_input("類別 *", value="配電元件")
                    n_spec = st.text_input("詳細規格")
                with c2:
                    n_barcode = st.text_input("條碼 / QR Code *", value="893500123499")
                    n_loc = st.text_input("倉庫儲位/分區 *", value="A區-02櫃")
                    n_qty = st.number_input("初始庫存數量", value=10.0)
                    n_unit = st.text_input("單位", value="只")
                    n_safe = st.number_input("安全水位警戒值", value=5.0)

                up_file = st.text_input("📷 圖片網址 (URL)", placeholder="https://...")

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
                                st.success(f"✅ 成功新增料號 `{n_code}`！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"寫入失敗: {e}")
                    else:
                        st.warning("請填寫必填欄位！")

        elif action_mode == "✏️ 修改物料與安全水位":
            if not inventory_db:
                st.info("無物料可修改")
            else:
                edit_str = st.selectbox("選擇物料", [f"{i['item_code']} - {i['item_name']} (庫存: {i['qty']} {i['unit']})" for i in inventory_db])
                t_code = edit_str.split(" - ")[0]
                t_obj = next((i for i in inventory_db if i["item_code"] == t_code), None)
                if t_obj:
                    with st.form("edit_item_db"):
                        e_name = st.text_input("品名", value=t_obj["item_name"])
                        e_loc = st.text_input("儲位", value=t_obj["location"])
                        e_qty = st.number_input("現有庫存", value=float(t_obj["qty"]))
                        e_safe = st.number_input("安全水位", value=float(t_obj.get("safety_stock", 5.0)))
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
                                    st.success("更新成功！")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失敗: {e}")

        elif action_mode == "🗑️ 刪除物料":
            if inventory_db:
                del_str = st.selectbox("選擇要刪除的料號", [i["item_code"] for i in inventory_db])
                if st.button("🗑️ 確認刪除", type="primary"):
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("DELETE FROM warehouse_inventory WHERE item_code = :c"), {"c": del_str})
                            st.success("已刪除！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"刪除失敗: {e}")

def show(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)

def main(engine=None, t=None, lang="繁體中文", **kwargs):
    render_warehouse_management(engine=engine, t=t, lang=lang, **kwargs)
