import streamlit as st
import pandas as pd

def render_factory_management_page(engine=None, lang="繁體中文", **kwargs):
    # 🌐 廠區管理模組多語系字典 (i18n)
    FAC_I18N = {
        "繁體中文": {
            "title": "🏭 廠區與工作廠區管理 (Factory Management)",
            "info": "在此您可以搜尋、新增、修改與刪除公司廠區資料（負責人與職位已與人事員工名冊自動連動同步）。",
            "search_label": "🔍 搜尋廠區名稱或編號",
            "search_ph": "輸入廠區名稱或編號搜尋...",
            "table_header": "📋 廠區與負責人名冊總覽",
            "tabs": ["➕ 新增廠區", "✏️ 修改廠區資料", "🗑️ 刪除廠區"],
            "add_header": "### ➕ 新增廠區與負責人",
            "lbl_id": "廠區編號",
            "lbl_name": "廠區名稱 (Factory Name)",
            "lbl_mgr": "選擇負責人與自動帶入職稱",
            "lbl_tel": "聯絡電話 (Phone)",
            "btn_add": "🚀 確認新增廠區",
            "success_add": "✅ 廠區 {name} 新增成功！",
            "warn_name": "⚠️ 請填寫廠區名稱！",
            "edit_header": "### ✏️ 修改廠區資料與負責人",
            "select_edit": "選擇要修改的廠區",
            "btn_save_edit": "💾 儲存修改",
            "success_edit": "✅ 廠區 {id} 修改成功！",
            "no_fac_edit": "目前無廠區資料可供修改。",
            "del_header": "### 🗑️ 刪除廠區確認",
            "select_del": "選擇要刪除的廠區",
            "del_warn": "確定要刪除廠區 **{id} - {name}** 嗎？此動作無法復原。",
            "btn_del": "🔥 確認刪除",
            "success_del": "✅ 廠區 {id} 已成功刪除！",
            "no_fac_del": "目前無廠區資料可供刪除。"
        },
        "Tiếng Việt": {
            "title": "🏭 Quản lý Nhà máy & Khu vực sản xuất",
            "info": "Nơi quản lý thông tin nhà máy, người đại diện (đồng bộ tự động từ danh sách nhân sự).",
            "search_label": "🔍 Tìm kiếm tên nhà máy hoặc mã số",
            "search_ph": "Nhập tên hoặc mã nhà máy...",
            "table_header": "📋 Danh sách Nhà máy & Người quản lý",
            "tabs": ["➕ Thêm Nhà máy", "✏️ Sửa Nhà máy", "🗑️ Xóa Nhà máy"],
            "add_header": "### ➕ Thêm Nhà máy & Người quản lý",
            "lbl_id": "Mã nhà máy",
            "lbl_name": "Tên nhà máy (Factory Name)",
            "lbl_mgr": "Chọn người quản lý",
            "lbl_tel": "Số điện thoại liên hệ (Phone)",
            "btn_add": "🚀 Xác nhận thêm nhà máy",
            "success_add": "✅ Đã thêm nhà máy {name} thành công!",
            "warn_name": "⚠️ Vui lòng điền tên nhà máy!",
            "edit_header": "### ✏️ Chỉnh sửa thông tin nhà máy",
            "select_edit": "Chọn nhà máy cần sửa",
            "btn_save_edit": "💾 Lưu thay đổi",
            "success_save_edit": "✅ Đã cập nhật thành công!",
            "success_edit": "✅ Đã cập nhật nhà máy {id} thành công!",
            "no_fac_edit": "Hiện không có nhà máy nào để chỉnh sửa.",
            "del_header": "### 🗑️ Xác nhận xóa nhà máy",
            "select_del": "Chọn nhà máy cần xóa",
            "del_warn": "Bạn có chắc chắn muốn xóa nhà máy **{id} - {name}** không?",
            "btn_del": "🔥 Xác nhận xóa",
            "success_del": "✅ Đã xóa thành công!",
            "no_fac_del": "Hiện không có nhà máy nào."
        },
        "English": {
            "title": "🏭 Factory & Plant Management",
            "info": "Manage plant profiles and responsible persons (synced with employee directory).",
            "search_label": "🔍 Search Factory Name or Code",
            "search_ph": "Enter factory name or code...",
            "table_header": "📋 Factory & Manager Directory",
            "tabs": ["➕ Add Factory", "✏️ Edit Factory", "🗑️ Delete Factory"],
            "add_header": "### ➕ Add New Factory & Manager",
            "lbl_id": "Factory Code",
            "lbl_name": "Factory Name",
            "lbl_mgr": "Select Manager & Title",
            "lbl_tel": "Contact Phone",
            "btn_add": "🚀 Confirm Add Factory",
            "success_add": "✅ Factory {name} added successfully!",
            "warn_name": "⚠️ Please enter factory name!",
            "edit_header": "### ✏️ Edit Factory Details",
            "select_edit": "Select Factory to Edit",
            "btn_save_edit": "💾 Save Changes",
            "success_edit": "✅ Factory {id} updated successfully!",
            "no_fac_edit": "No factory records available.",
            "del_header": "### 🗑️ Confirm Factory Deletion",
            "select_del": "Select Factory to Delete",
            "del_warn": "Are you sure you want to delete **{id} - {name}**?",
            "btn_del": "🔥 Confirm Delete",
            "success_del": "✅ Factory successfully deleted!",
            "no_fac_del": "No factory records available."
        }
    }

    active_lang = lang if lang in FAC_I18N else "繁體中文"
    L = FAC_I18N[active_lang]

    st.title(L["title"])
    st.info(L["info"])
    
    # 初始化廠區資料
    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人與職位": "李佑銘 (董事長)", "聯絡電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)", "負責人與職位": "Nguyễn Văn Quý (財務主管)", "聯絡電話": "0918999080"}
        ]

    # 取得人事系統員工清單（若無則給預設對應）
    employee_options = []
    if "employee_db" in st.session_state and st.session_state.employee_db:
        employee_options = [f"{e['姓名']} ({e['職稱']})" for e in st.session_state.employee_db if "在職" in e.get("狀態", "在職")]
    if not employee_options:
        employee_options = ["李佑銘 (董事長)", "Nguyễn Văn Quý (財務主管)"]

    search_q = st.text_input(L["search_label"], placeholder=L["search_ph"], key="fac_search_input_unique")
    filtered_fac = [
        f for f in st.session_state.factory_list 
        if search_q.lower() in f["廠區名稱"].lower() or search_q.lower() in f["廠區編號"].lower() or search_q.lower() in f["負責人與職位"].lower()
    ] if search_q else st.session_state.factory_list
    
    st.markdown(L["table_header"])
    st.dataframe(pd.DataFrame(filtered_fac), use_container_width=True)
    
    tab_add, tab_edit, tab_del = st.tabs(L["tabs"])
    
    with tab_add:
        with st.form("add_factory_form_unique"):
            st.markdown(L["add_header"])
            fn_id = st.text_input(L["lbl_id"], value=f"FAC-{len(st.session_state.factory_list)+1:02d}", key="add_fn_id_u")
            fn_name = st.text_input(L["lbl_name"], key="add_fn_name_u")
            
            # 從員工名冊動態選取負責人與職位
            fn_mgr = st.selectbox(L["lbl_mgr"], employee_options, key="add_fn_mgr_select_u")
            
            fn_tel = st.text_input(L["lbl_tel"], key="add_fn_tel_u")
            if st.form_submit_button(L["btn_add"], type="primary"):
                if fn_name:
                    st.session_state.factory_list.append({
                        "廠區編號": fn_id,
                        "廠區名稱": fn_name,
                        "負責人與職位": fn_mgr,
                        "聯絡電話": fn_tel if fn_tel else "-"
                    })
                    st.success(L["success_add"].format(name=fn_name))
                    st.rerun()
                else:
                    st.warning(L["warn_name"])

    with tab_edit:
        if st.session_state.factory_list:
            fac_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in st.session_state.factory_list}
            selected_fac_key = st.selectbox(L["select_edit"], list(fac_options.keys()), key="edit_fac_select_u")
            target_fac = fac_options[selected_fac_key]
            
            with st.form("edit_factory_form_unique"):
                st.markdown(L["edit_header"])
                e_name = st.text_input(L["lbl_name"], value=target_fac["廠區名稱"], key="edit_e_name_u")
                
                # 下拉選單自動帶入當前負責人
                current_mgr = target_fac["負責人與職位"]
                mgr_index = employee_options.index(current_mgr) if current_mgr in employee_options else 0
                e_mgr = st.selectbox(L["lbl_mgr"], employee_options, index=mgr_index, key="edit_e_mgr_select_u")
                
                e_tel = st.text_input(L["lbl_tel"], value=target_fac["聯絡電話"], key="edit_e_tel_u")
                
                if st.form_submit_button(L["btn_save_edit"], type="primary"):
                    for f in st.session_state.factory_list:
                        if f["廠區編號"] == target_fac["廠區編號"]:
                            f["廠區名稱"] = e_name
                            f["負責人與職位"] = e_mgr
                            f["聯絡電話"] = e_tel
                    st.success(L["success_edit"].format(id=target_fac['廠區編號']))
                    st.rerun()
        else:
            st.info(L["no_fac_edit"])

    with tab_del:
        if st.session_state.factory_list:
            del_options = {f"{f['廠區編號']} - {f['廠區名稱']}": f for f in st.session_state.factory_list}
            selected_del_key = st.selectbox(L["select_del"], list(del_options.keys()), key="del_fac_select_u")
            target_del = del_options[selected_del_key]
            
            with st.form("delete_factory_form_unique"):
                st.markdown(L["del_header"])
                st.warning(L["del_warn"].format(id=target_del['廠區編號'], name=target_del['廠區名稱']))
                if st.form_submit_button(L["btn_del"], type="primary"):
                    st.session_state.factory_list = [f for f in st.session_state.factory_list if f["廠區編號"] != target_del["廠區編號"]]
                    st.success(L["success_del"].format(id=target_del['廠區編號']))
                    st.rerun()
        else:
            st.info(L["no_fac_del"])

def show(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_factory_management_page(*args, **kwargs)
