import streamlit as st
import pandas as pd

def render_factory_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🏭 廠區與工作廠區管理 (Factory Management)")
    st.info("在此您可以搜尋、新增、修改與刪除公司廠區資料（完整 CRUD 功能）。")
    
    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人": "張董事長", "電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "平陽廠 (Binh Duong)", "負責人": "阮文強", "電話": "0918999080"}
        ]
    
    # 搜尋功能
    search_q = st.text_input("🔍 搜尋廠區 / Search Factory", placeholder="輸入廠區名稱或編號搜尋...")
    filtered_fac = [f for f in st.session_state.factory_list if search_q.lower() in f["廠區名稱"].lower() or search_q.lower() in f["廠區編號"].lower()] if search_q else st.session_state.factory_list
    
    st.dataframe(pd.DataFrame(filtered_fac), use_container_width=True)
    
    tab_add, tab_edit, tab_del = st.tabs(["➕ 新增廠區", "✏️ 修改廠區資料", "🗑️ 刪除廠區"])
    
    with tab_add:
        with st.form("add_factory_form"):
            st.markdown("### ➕ 新增廠區")
            fn_id = st.text_input("廠區編號", value=f"FAC-{len(st.session_state.factory_list)+1:02d}")
            fn_name = st.text_input("廠區名稱 (Factory Name)")
            fn_mgr = st.text_input("負責人 (Manager)")
            fn_tel = st.text_input("聯絡電話 (Phone)")
            if st.form_submit_button("🚀 確認新增廠區", type="primary"):
                if fn_name:
                    st.session_state.factory_list.append({"廠區編號": fn_id, "廠區名稱": fn_name, "負責人": fn_mgr, "電話": fn_tel})
                    st.success(f"✅ 廠區 {fn_name} 新增成功！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫廠區名稱！")

    with tab_edit:
        if st.session_state.factory_list:
            fac_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in st.session_state.factory_list}
            selected_fac_key = st.selectbox("選擇要修改的廠區", list(fac_options.keys()))
            target_fac = fac_options[selected_fac_key]
            
            with st.form("edit_factory_form"):
                st.markdown("### ✏️ 修改廠區資料")
                e_name = st.text_input("廠區名稱", value=target_fac["廠區名稱"])
                e_mgr = st.text_input("負責人", value=target_fac["負責人"])
                e_tel = st.text_input("聯絡電話", value=target_fac["電話"])
                
                if st.form_submit_button("💾 儲存修改", type="primary"):
                    for f in st.session_state.factory_list:
                        if f["廠區編號"] == target_fac["廠區編號"]:
                            f["廠區名稱"] = e_name
                            f["負責人"] = e_mgr
                            f["電話"] = e_tel
                    st.success(f"✅ 廠區 {target_fac['廠區編號']} 修改成功！")
                    st.rerun()
        else:
            st.info("目前無廠區資料可供修改。")

    with tab_del:
        if st.session_state.factory_list:
            del_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in st.session_state.factory_list}
            selected_del_key = st.selectbox("選擇要刪除的廠區", list(del_options.keys()))
            target_del = del_options[selected_del_key]
            
            with st.form("delete_factory_form"):
                st.markdown(f"### 🗑️ 刪除廠區確認")
                st.warning(f"確定要刪除廠區 **{target_del['廠區編號']} - {target_del['廠區名稱']}** 嗎？此動作無法復原。")
                if st.form_submit_button("🔥 確認刪除", type="primary"):
                    st.session_state.factory_list = [f for f in st.session_state.factory_list if f["廠區編號"] != target_del["廠區編號"]]
                    st.success(f"✅ 廠區 {target_del['廠區編號']} 已成功刪除！")
                    st.rerun()
        else:
            st.info("目前無廠區資料可供刪除。")

def show(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)
