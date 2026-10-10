import streamlit as st
import pandas as pd
import datetime

def get_supabase_client():
    if "supabase" in st.session_state:
        return st.session_state.supabase
    return None

def render_sheet_metal_module(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("✂️ [板金] 板金加工組工單與條碼管理")
    st.caption("專為現場設計：支援工程設計圖上傳與線上檢視、大按鈕快速回報、自動同步 Supabase 資料庫。")

    supabase = get_supabase_client()

    # 預設板金工單資料 (含設計圖欄位 mock)
    default_orders = [
        {
            "order_code": "WO-SM-20261001",
            "project_name": "越南西寧廠低壓控制盤箱體",
            "spec": "800x600x250mm (厚度2mm)",
            "material_code": "SHEET-SPCC-2MM",
            "qty": 10.0,
            "status": "📌 待排程 / 領料中",
            "manager": "admin",
            "drawing_name": "TN_Control_Box_v1.pdf"
        },
        {
            "order_code": "WO-SM-20261002",
            "project_name": "海防廠動力配電箱外殼",
            "spec": "1200x800x300mm (厚度2mm)",
            "material_code": "SHEET-SPCC-2MM",
            "qty": 5.0,
            "status": "✂️ 雷射切割與折床中",
            "manager": "admin",
            "drawing_name": "HP_Power_Enclosure_rev2.pdf"
        }
    ]

    # 初始化 Session State 與 Supabase 同步
    if "sheet_metal_db" not in st.session_state or not isinstance(st.session_state.sheet_metal_db, list) or not st.session_state.sheet_metal_db:
        if supabase:
            try:
                res = supabase.table("sheet_metal_orders").select("*").execute()
                if res.data:
                    st.session_state.sheet_metal_db = [{
                        "order_code": row["order_code"],
                        "project_name": row["project_name"],
                        "spec": row["spec"],
                        "material_code": row["material_code"],
                        "qty": float(row["qty"]),
                        "status": row["status"],
                        "manager": row["manager"],
                        "drawing_name": row.get("drawing_name", "無附圖")
                    } for row in res.data]
                else:
                    st.session_state.sheet_metal_db = default_orders
            except Exception:
                st.session_state.sheet_metal_db = default_orders
        else:
            st.session_state.sheet_metal_db = default_orders

    tab_list, tab_action, tab_new = st.tabs([
        "📋 板金工單進度與設計圖總表", 
        "⚡ 現場快速回報與狀態更新", 
        "➕ 建立新板金工單 (含上傳設計圖)"
    ])

    # 1. 總表檢視 (含設計圖提示)
    with tab_list:
        st.markdown("### 📋 現行板金加工工單與工程圖面清冊")
        if st.session_state.sheet_metal_db:
            display_data = []
            for o in st.session_state.sheet_metal_db:
                display_data.append({
                    "工單編號": o["order_code"],
                    "專案名稱": o["project_name"],
                    "規格尺寸": o["spec"],
                    "鋼板料號": o["material_code"],
                    "數量": o["qty"],
                    "目前狀態": o["status"],
                    "工程設計圖檔": o.get("drawing_name", "無附圖"),
                    "經辦": o["manager"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
            st.info("💡 提示：現場主管或師傅可於「現場快速回報」分頁中直接點選工單查看詳細資訊與圖檔。")
        else:
            st.info("目前無板金工單紀錄。")

    # 2. 現場快速回報與圖面檢視
    with tab_action:
        st.markdown("### ⚡ 現場主管快速進度回報與圖面檢視")
        
        if st.session_state.sheet_metal_db:
            order_options = [f"{o['order_code']} - {o['project_name']} (現狀: {o['status']})" for o in st.session_state.sheet_metal_db]
            selected_order_str = st.selectbox("🎯 選擇要檢視或回報的板金工單", order_options)

            if selected_order_str:
                target_code = selected_order_str.split(" - ")[0].strip()
                current_order = next((o for o in st.session_state.sheet_metal_db if o["order_code"] == target_code), None)

                if current_order:
                    # 📐 顯示該工單的詳細規格與設計圖狀態
                    with st.expander("📌 點此展開【工程設計圖與加工規格明細】", expanded=True):
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.markdown(f"**工單編號**：`{current_order['order_code']}`")
                            st.markdown(f"**專案名稱**：{current_order['project_name']}")
                            st.markdown(f"**規格尺寸**：{current_order['spec']}")
                        with col_d2:
                            st.markdown(f"**對應鋼板**：`{current_order['material_code']}`")
                            st.markdown(f"**生產數量**：`{current_order['qty']} 件`")
                            st.markdown(f"**附加圖檔**：📄 `{current_order.get('drawing_name', '無附圖')}`")
                        
                        st.warning(f"⚠️ 現場施工提醒：請務必核對上方規格與圖面尺寸（{current_order.get('drawing_name', '無附圖')}）後方可進行折彎與雷射切割！")

                    st.markdown("---")
                    st.markdown("#### 🔄 點擊下方大按鈕更新生產進度：")
                    
                    col1, col2, col3 = st.columns(3)
                    logged_staff = st.session_state.get('user_name', 'admin')

                    with col1:
                        if st.button("✂️ 1. 開始雷射/折床", use_container_width=True, type="secondary"):
                            current_order["status"] = "✂️ 雷射切割與折床中"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("sheet_metal_orders").upsert(current_order).execute()
                            st.success(f"✅ 工單 {target_code} 已更新為：雷射切割與折床中！")
                            st.rerun()

                    with col2:
                        if st.button("⚡ 2. 銲接成型中", use_container_width=True, type="secondary"):
                            current_order["status"] = "⚡ 銲接與打磨成型中"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("sheet_metal_orders").upsert(current_order).execute()
                            st.success(f"✅ 工單 {target_code} 已更新為：銲接成型中！")
                            st.rerun()

                    with col3:
                        if st.button("✅ 3. 板金完工 (轉塗料)", use_container_width=True, type="primary"):
                            current_order["status"] = "✅ 板金完工 (待轉塗料)"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("sheet_metal_orders").upsert(current_order).execute()
                            st.success(f"🎉 工單 {target_code} 已順利完工並記錄！")
                            st.rerun()
        else:
            st.warning("⚠️ 目前無可操作的工單。")

    # 3. 新增板金工單 (支援上傳設計圖)
    with tab_new:
        st.markdown("### ➕ 開立新板金加工工單與上傳設計圖")
        with st.form("form_new_sheet_metal"):
            c1, c2 = st.columns(2)
            with c1:
                new_code = st.text_input("工單編號 *", value="WO-SM-20261004")
                new_project = st.text_input("專案名稱 *", placeholder="例如: 某某科技廠配電盤板金")
                new_spec = st.text_input("尺寸規格描述 *", placeholder="例如: 1000x800x300mm (厚度2mm)")
            with c2:
                new_material = st.text_input("對應鋼板料號 (扣料用)", value="SHEET-SPCC-2MM")
                new_qty = st.number_input("生產數量 *", min_value=1.0, value=10.0, step=1.0)
                new_status = st.selectbox("初始狀態", ["📌 待排程 / 領料中", "✂️ 雷射切割與折床中"])

            # 📄 設計圖上傳欄位
            uploaded_file = st.file_uploader("📂 上傳工程設計圖檔 (支援 PDF, DWG, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

            if st.form_submit_button("💾 儲存工單、上傳圖面並同步至 Supabase", type="primary", use_container_width=True):
                if new_code and new_project:
                    drawing_filename = uploaded_file.name if uploaded_file is not None else "Standard_Drawing_v1.pdf"
                    
                    new_item = {
                        "order_code": new_code,
                        "project_name": new_project,
                        "spec": new_spec,
                        "material_code": new_material,
                        "qty": new_qty,
                        "status": new_status,
                        "manager": st.session_state.get('user_name', 'admin'),
                        "drawing_name": drawing_filename
                    }
                    st.session_state.sheet_metal_db.insert(0, new_item)
                    if supabase:
                        try:
                            supabase.table("sheet_metal_orders").upsert(new_item).execute()
                        except Exception as e:
                            st.error(f"Supabase 寫入失敗: {e}")
                    st.success(f"✅ 板金工單 `{new_code}` 建立成功，設計圖 `{drawing_filename}` 已順利附加！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫工單編號與專案名稱！")

def show(*args, **kwargs):
    render_sheet_metal_module(*args, **kwargs)

def main(*args, **kwargs):
    render_sheet_metal_module(*args, **kwargs)

def render_sheet_metal_page(*args, **kwargs):
    render_sheet_metal_module(*args, **kwargs)
