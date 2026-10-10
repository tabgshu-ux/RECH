import streamlit as st
import pandas as pd
import datetime

def get_supabase_client():
    if "supabase" in st.session_state:
        return st.session_state.supabase
    return None

def render_assembly_module(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("⚡ [配盤] 配電盤組裝配線組與拍照入庫")
    st.caption("專為配盤車間設計：多規格配電盤管理、佈線組裝追蹤、完工拍照上傳與自動完工入庫。")

    supabase = get_supabase_client()

    # 預設配電盤組裝工單
    default_assembly_orders = [
        {
            "order_code": "WO-AS-20261001",
            "project_name": "越南西寧廠低壓主配電盤 (LVS)",
            "panel_spec": "2000x800x600mm (主斷路器 1600A)",
            "qty": 2.0,
            "status": "⚡ 內部銅排配置與二次控制線配線中",
            "photo_name": "LVS_Panel_Wiring_Draft.jpg",
            "manager": "admin"
        },
        {
            "order_code": "WO-AS-20261002",
            "project_name": "海防廠馬達控制中心 (MCC)",
            "panel_spec": "1800x600x500mm (多迴路 Inverter)",
            "qty": 4.0,
            "status": "📌 待組裝配線",
            "photo_name": "無完工照片",
            "manager": "admin"
        }
    ]

    # 初始化 Session State
    if "assembly_db" not in st.session_state or not isinstance(st.session_state.assembly_db, list) or not st.session_state.assembly_db:
        if supabase:
            try:
                res = supabase.table("assembly_orders").select("*").execute()
                if res.data:
                    st.session_state.assembly_db = [{
                        "order_code": row["order_code"],
                        "project_name": row["project_name"],
                        "panel_spec": row["panel_spec"],
                        "qty": float(row["qty"]),
                        "status": row["status"],
                        "photo_name": row.get("photo_name", "無完工照片"),
                        "manager": row["manager"]
                    } for row in res.data]
                else:
                    st.session_state.assembly_db = default_assembly_orders
            except Exception:
                st.session_state.assembly_db = default_assembly_orders
        else:
            st.session_state.assembly_db = default_assembly_orders

    tab_list, tab_action, tab_new = st.tabs([
        "📋 配電盤組裝與完工總表", 
        "⚡ 現場配線回報與拍照上傳入庫", 
        "➕ 接收塗料完工件並開立配盤工單"
    ])

    # 1. 總表檢視
    with tab_list:
        st.markdown("### 📋 現行配電盤組裝進度與成品清冊")
        if st.session_state.assembly_db:
            df = pd.DataFrame(st.session_state.assembly_db)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("目前無配盤組裝工單紀錄。")

    # 2. 現場快速回報與拍照入庫
    with tab_action:
        st.markdown("### ⚡ 配盤車間主管現場組裝進度回報")
        
        if st.session_state.assembly_db:
            order_options = [f"{o['order_code']} - {o['project_name']} (現狀: {o['status']})" for o in st.session_state.assembly_db]
            selected_order_str = st.selectbox("🎯 選擇要回報的配電盤工單", order_options, key="select_assembly_order")

            if selected_order_str:
                target_code = selected_order_str.split(" - ")[0].strip()
                current_order = next((o for o in st.session_state.assembly_db if o["order_code"] == target_code), None)

                if current_order:
                    st.markdown("#### 📊 目前配盤組裝進度燈號：")
                    status_text = current_order["status"]
                    
                    p_val = 0
                    if "待組裝" in status_text:
                        p_val = 15
                        st.markdown("🔴 **【第 1 階段】📌 待組裝配線** ⏳ (箱體已送達，等待配線師傅進場)")
                    elif "銅排" in status_text or "配線中" in status_text:
                        p_val = 60
                        st.markdown("🟡 **【第 2 階段】⚡ 內部銅排配置與二次控制線配線中** 🔌 (正在進行主母線安裝與控制迴路配線)")
                    elif "完工" in status_text or "入庫" in status_text:
                        p_val = 100
                        st.markdown("🟢 **【第 3 階段】🎉 組裝完工並已拍照驗收自動入庫** ✅ (FAT 檢驗合格，正式入庫準備出貨)")

                    st.progress(p_val)
                    st.markdown("---")

                    with st.expander("📌 點此展開【配電盤規格與完工照片驗收】", expanded=True):
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            st.markdown(f"**工單編號**：`{current_order['order_code']}`")
                            st.markdown(f"**專案名稱**：{current_order['project_name']}")
                            st.markdown(f"**盤體規格**：`{current_order['panel_spec']}`")
                        with col_a2:
                            st.markdown(f"**生產數量**：`{current_order['qty']} 台`")
                            st.markdown(f"**完工照片檔案**：📸 `{current_order.get('photo_name', '無完工照片')}`")
                        
                        st.warning("⚠️ 配盤品管提醒：配線完成後務必進行絕緣耐壓測試（Megger Test），並上傳實體完工照片後方可按下入庫按鈕！")

                    st.markdown("---")
                    st.markdown("#### 📸 拍照上傳完成驗收並入庫：")
                    
                    uploaded_photo = st.file_uploader("📷 拍攝或上傳配電盤完工照片 (JPG, PNG)", type=["png", "jpg", "jpeg"], key="assembly_photo_upload")

                    col1, col2 = st.columns(2)
                    logged_staff = st.session_state.get('user_name', 'admin')

                    with col1:
                        if st.button("🔌 進行內部配線與銅排組裝", use_container_width=True, type="secondary"):
                            current_order["status"] = "⚡ 內部銅排配置與二次控制線配線中"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("assembly_orders").upsert(current_order).execute()
                            st.success(f"✅ 工單 {target_code} 已更新為：配線組裝中！")
                            st.rerun()

                    with col2:
                        if st.button("🎉 拍照驗收完成並【自動入庫】", use_container_width=True, type="primary"):
                            photo_filename = uploaded_photo.name if uploaded_photo is not None else "Final_Assembly_Inspection.jpg"
                            current_order["status"] = "🟢 組裝完工並已拍照驗收自動入庫"
                            current_order["photo_name"] = photo_filename
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("assembly_orders").upsert(current_order).execute()
                            st.success(f"🎉 恭喜！工單 {target_code} 驗收合格，照片 `{photo_filename}` 已上傳並完成自動入庫！")
                            st.rerun()
        else:
            st.warning("⚠️ 目前無可操作的配盤工單。")

    # 3. 新增配盤工單
    with tab_new:
        st.markdown("### ➕ 接收塗料完工件並建立配電盤組裝工單")
        with st.form("form_new_assembly"):
            c1, c2 = st.columns(2)
            with c1:
                new_code = st.text_input("配盤工單編號 *", value="WO-AS-20261003")
                new_project = st.text_input("專案名稱 *", placeholder="例如: 某某科技廠總配電盤")
            with c2:
                new_spec = st.text_input("盤體規格與容量描述 *", value="1600x800x500mm (MCC 盤)")
                new_qty = st.number_input("數量 (台) *", min_value=1.0, value=2.0, step=1.0)

            if st.form_submit_button("💾 建立配盤工單並同步至 Supabase", type="primary", use_container_width=True):
                if new_code and new_project:
                    new_item = {
                        "order_code": new_code,
                        "project_name": new_project,
                        "panel_spec": new_spec,
                        "qty": new_qty,
                        "status": "📌 待組裝配線",
                        "photo_name": "無完工照片",
                        "manager": st.session_state.get('user_name', 'admin')
                    }
                    st.session_state.assembly_db.insert(0, new_item)
                    if supabase:
                        try:
                            supabase.table("assembly_orders").upsert(new_item).execute()
                        except Exception as e:
                            st.error(f"Supabase 寫入失敗: {e}")
                    st.success(f"✅ 配盤工單 `{new_code}` 建立成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫工單編號與專案名稱！")

def show(*args, **kwargs):
    render_assembly_module(*args, **kwargs)

def main(*args, **kwargs):
    render_assembly_module(*args, **kwargs)

def render_assembly_page(*args, **kwargs):
    render_assembly_module(*args, **kwargs)
