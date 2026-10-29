import streamlit as st

def render_alert_tab(inventory_db, lang):
    st.markdown("##### ⚠️ 安全庫存與缺料警示監控")
    low_items = [i for i in inventory_db if i["qty"] <= i["safety_stock"]] if inventory_db else []
    if low_items:
        st.warning("⚠️ 以下物料庫存已低於安全水位，請通知採購進行補貨！")
        for item in low_items:
            st.error(f"儲位: **{item['location']}** | 料號: `{item['item_code']}` | 品名: {item['item_name']} | 現有庫存: **{item['qty']} {item['unit']}** (安全水位要求: {item['safety_stock']})")
    else:
        st.success("🟢 目前所有倉庫物料之庫存水位皆高於安全警戒線！")
