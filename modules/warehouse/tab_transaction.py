import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_transaction_tab(engine, inventory_db, logs_db, current_logged_user, lang):
    st.markdown("##### 📥📤 快速出入庫領料作業")
    all_zones = sorted(list(set([str(i["location"]).split("-")[0] if "-" in str(i["location"]) else str(i["location"]) for i in inventory_db]))) if inventory_db else []
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
