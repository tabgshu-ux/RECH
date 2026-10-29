import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def render_stocktaking_tab(engine, inventory_db, stocktake_db, current_logged_user, lang):
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
