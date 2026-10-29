import streamlit as st
import datetime
from sqlalchemy import text

def render_management_tab(engine, inventory_db, lang):
    st.markdown("##### ⚙️ 倉庫資材主檔與安全水位設定")
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
                            st.success(f"✅ 成功將料號 `{n_code}` 寫入資料庫！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"寫入資料庫失敗: {e}")
                else:
                    st.warning("請填寫必填欄位！")

    elif action_mode == "✏️ 修改物料與安全水位":
        if not inventory_db:
            st.info("目前無物料可修改")
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
                        st.success(f"已成功從資料庫刪除料號 {del_str}！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
