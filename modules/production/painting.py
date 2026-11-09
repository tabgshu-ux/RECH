import streamlit as st
import pandas as pd
import datetime

def get_supabase_client():
    if "supabase" in st.session_state:
        return st.session_state.supabase
    return None

def render_painting_module(engine=None, t=None, lang="繁體中文", **kwargs):
    st.title("🎨 [塗料] 粉體塗裝烤漆組品管與製程追蹤")
    st.caption("專屬塗裝車間：前處理水池管制、烤箱固化追蹤、視覺化燈號、自動同步 Supabase 資料庫。")

    supabase = get_supabase_client()

    # 預設塗裝工單資料
    default_painting_orders = [
        {
            "order_code": "WO-PT-20261001",
            "project_name": "越南西寧廠低壓控制盤箱體",
            "color_spec": "經典電腦灰 (RAL 7035 / 皺紋漆)",
            "qty": 10.0,
            "status": "🔥 靜電噴塗與固化烤箱烘烤中",
            "manager": "admin"
        },
        {
            "order_code": "WO-PT-20261002",
            "project_name": "海防廠動力配電箱外殼",
            "color_spec": "工業白 (RAL 9002 / 平光)",
            "qty": 5.0,
            "status": "💧 前處理車間 (脫脂/酸洗/皮膜/水洗)",
            "manager": "admin"
        }
    ]

    # 初始化 Session State
    if "painting_db" not in st.session_state or not isinstance(st.session_state.painting_db, list) or not st.session_state.painting_db:
        if supabase:
            try:
                res = supabase.table("painting_orders").select("*").execute()
                if res.data:
                    st.session_state.painting_db = [{
                        "order_code": row["order_code"],
                        "project_name": row["project_name"],
                        "color_spec": row["color_spec"],
                        "qty": float(row["qty"]),
                        "status": row["status"],
                        "manager": row["manager"]
                    } for row in res.data]
                else:
                    st.session_state.painting_db = default_painting_orders
            except Exception:
                st.session_state.painting_db = default_painting_orders
        else:
            st.session_state.painting_db = default_painting_orders

    tab_list, tab_action, tab_new = st.tabs([
        "📋 塗裝工單進度總表", 
        "⚡ 現場快速回報與製程燈號 (水池/烤箱管制)", 
        "➕ 接收板金完工件並開立塗裝單"
    ])

    # 1. 總表檢視
    with tab_list:
        st.markdown("### 📋 現行粉體塗裝加工與烤漆清冊")
        if st.session_state.painting_db:
            df = pd.DataFrame(st.session_state.painting_db)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("目前無塗裝工單紀錄。")

    # 2. 現場快速回報與製程燈號
    with tab_action:
        st.markdown("### ⚡ 塗裝車間主管快速進度回報")
        
        if st.session_state.painting_db:
            order_options = [f"{o['order_code']} - {o['project_name']} (現狀: {o['status']})" for o in st.session_state.painting_db]
            selected_order_str = st.selectbox("🎯 選擇要回報的塗裝工單", order_options, key="select_painting_order")

            if selected_order_str:
                target_code = selected_order_str.split(" - ")[0].strip()
                current_order = next((o for o in st.session_state.painting_db if o["order_code"] == target_code), None)

                if current_order:
                    st.markdown("#### 📊 目前塗裝製程進度燈號：")
                    status_text = current_order["status"]
                    
                    p_val = 0
                    if "待塗裝" in status_text:
                        p_val = 10
                        st.markdown("🔴 **【第 1 階段】📌 待塗裝 / 吊掛準備中** ⏳ (等待從板金車間移入)")
                    elif "前處理" in status_text:
                        p_val = 40
                        st.markdown("🟡 **【第 2 階段】💧 前處理車間（脫脂 ➡️ 酸洗 ➡️ 多槽水洗 ➡️ 皮膜）** 🧪 (化學清洗與防銹處理中)")
                    elif "靜電噴塗" in status_text:
                        p_val = 75
                        st.markdown("🔵 **【第 3 階段】🔥 靜電粉體噴塗與固化烤箱烘烤中** 🌡️ (粉末噴塗完成，正在高溫烤箱固化)")
                    elif "完工" in status_text:
                        p_val = 100
                        st.markdown("🟢 **【第 4 階段】✅ 塗裝品檢合格 (準備轉入配盤組)** 🎉 (QC 通過，準備下件)")

                    st.progress(p_val)
                    st.markdown("---")

                    with st.expander("📌 點此展開【塗裝色卡與規格明細】", expanded=True):
                        st.markdown(f"**工單編號**：`{current_order['order_code']}`")
                        st.markdown(f"**專案名稱**：{current_order['project_name']}")
                        st.markdown(f"**塗裝色卡/規範**：`{current_order['color_spec']}`")
                        st.markdown(f"**生產數量**：`{current_order['qty']} 件`")
                        st.warning("⚠️ 塗裝車間品管提醒：進烤箱前請確認表面無油汙、水漬，並嚴格控管固化烤箱溫度與烘烤時間！")

                    st.markdown("---")
                    st.markdown("#### 🔄 點擊下方大按鈕切換更新塗裝製程：")
                    
                    col1, col2, col3 = st.columns(3)
                    logged_staff = st.session_state.get('user_name', 'admin')

                    with col1:
                        if st.button("💧 1. 前處理水池作業", use_container_width=True, type="secondary"):
                            current_order["status"] = "💧 前處理車間 (脫脂/酸洗/皮膜/水洗)"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("painting_orders").upsert(current_order).execute()
                            st.success(f"✅ 工單 {target_code} 已進入前處理水池作業！")
                            st.rerun()

                    with col2:
                        if st.button("🔥 2. 噴塗與烤箱固化", use_container_width=True, type="secondary"):
                            current_order["status"] = "🔥 靜電噴塗與固化烤箱烘烤中"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("painting_orders").upsert(current_order).execute()
                            st.success(f"✅ 工單 {target_code} 已進入靜電噴塗與烤箱固化階段！")
                            st.rerun()

                    with col3:
                        if st.button("✅ 3. 塗裝品檢完工", use_container_width=True, type="primary"):
                            current_order["status"] = "✅ 塗裝品檢完工 (待轉配盤)"
                            current_order["manager"] = logged_staff
                            if supabase:
                                supabase.table("painting_orders").upsert(current_order).execute()
                            st.success(f"🎉 工單 {target_code} 塗裝完工並 QC 合格！")
                            st.rerun()
        else:
            st.warning("⚠️ 目前無可操作的塗裝工單。")

    # 3. 新增塗裝工單
    with tab_new:
        st.markdown("### ➕ 接收板金完工件並建立塗裝工單")
        with st.form("form_new_painting"):
            c1, c2 = st.columns(2)
            with c1:
                new_code = st.text_input("塗裝工單編號 *", value="WO-PT-20261003")
                new_project = st.text_input("專案名稱 *", placeholder="例如: 某某廠配電盤箱體塗裝")
            with c2:
                new_color = st.text_input("指定色卡與漆種規範 *", value="RAL 7035 經典電腦灰 (平光)")
                new_qty = st.number_input("數量 *", min_value=1.0, value=10.0, step=1.0)

            if st.form_submit_button("💾 建立塗裝工單並同步至 Supabase", type="primary", use_container_width=True):
                if new_code and new_project:
                    new_item = {
                        "order_code": new_code,
                        "project_name": new_project,
                        "color_spec": new_color,
                        "qty": new_qty,
                        "status": "📌 待塗裝 / 吊掛準備中",
                        "manager": st.session_state.get('user_name', 'admin')
                    }
                    st.session_state.painting_db.insert(0, new_item)
                    if supabase:
                        try:
                            supabase.table("painting_orders").upsert(new_item).execute()
                        except Exception as e:
                            st.error(f"Supabase 寫入失敗: {e}")
                    st.success(f"✅ 塗裝工單 `{new_code}` 建立成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫工單編號與專案名稱！")

def show(*args, **kwargs):
    render_painting_module(*args, **kwargs)

def main(*args, **kwargs):
    render_painting_module(*args, **kwargs)

def render_painting_page(*args, **kwargs):
    render_painting_module(*args, **kwargs)
