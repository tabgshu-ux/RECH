import streamlit as st

def render_inventory_tab(inventory_db, lang):
    st.markdown("##### 📊 管理部倉庫：全廠各品項即時庫存總覽")
    search_wh = st.text_input("🔍 搜尋料號、名稱、條碼或儲位...", key="wh_search_box")
    
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
