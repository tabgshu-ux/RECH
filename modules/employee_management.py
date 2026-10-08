import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 員工與人事管理模組多語系字典 (i18n)
# ----------------------------------------------------
EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司員工基本資料、分派廠區（西寧廠/海防廠）、初始密碼設定與系統權限角色。",
        "tab_list": "👥 員工名冊與資料檢視",
        "tab_add": "➕ 新增員工與初始帳密設定",
        "tab_edit": "✏️ 修改員工資料與重設密碼",
        "tab_delete": "🗑️ 停用 / 刪除員工帳號",
        "header_list": "📋 全公司在職員工名冊與權限總覽",
        "header_add": "➕ 新增員工個人檔案與初始帳密設定",
        "header_edit": "✏️ 修改員工基本資料與權限",
        "header_delete": "🗑️ 停用或刪除離職員工帳號",
        "lbl_code": "員工工號 (登入帳號) *",
        "lbl_name": "員工姓名 (Employee Name) *",
        "lbl_factory": "工作廠區 (Factory) *",
        "factory_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
        "lbl_dept": "部門 *",
        "dept_opts": ["總經理室", "管理部", "工程部", "生產部", "資訊部"],
        "lbl_pwd": "初始登入密碼 (預設) *",
        "lbl_title": "職稱 / 職務 *",
        "lbl_country": "國籍",
        "country_opts": ["越南 (Vietnam)", "台灣 (Taiwan)", "中國 (China)"],  # 👈 已新增中國並移除其他
        "lbl_role": "系統權限角色 *",
        "lbl_addr_perm": "戶籍地址 (Permanent Address)",
        "lbl_addr_temp": "現住地址 (Temporary Address)",
        "btn_add": "🚀 立即新增員工並建立帳號",
        "success_add": "✅ 成功新增員工 `{name}` (工號: `{code}`)！系統已自動勾選『首次登入強制修改密碼』。",
        "btn_update": "💾 儲存修改後員工資料",
        "success_update": "✅ 員工 `{code}` 資料已成功更新！",
        "btn_delete": "⚠️ 確認停用/刪除此員工帳號",
        "success_delete": "✅ 員工 `{code}` 已自系統中停用。",
        "search_ph": "🔍 搜尋員工姓名或工號...",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_factory": "廠區",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_role": "系統角色",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Nhân sự & Hồ sơ Nhân viên",
        "caption": "Quản lý thông tin nhân viên, phân bổ nhà máy (Tây Ninh/Hải Phòng), mật khẩu ban đầu và phân quyền hệ thống.",
        "tab_list": "👥 Danh sách Nhân viên",
        "tab_add": "➕ Thêm Nhân viên mới",
        "tab_edit": "✏️ Chỉnh sửa Thông tin",
        "tab_delete": "🗑️ Vô hiệu hóa Tài khoản",
        "header_list": "📋 Danh sách nhân viên toàn công ty",
        "header_add": "➕ Thêm hồ sơ nhân viên và mật khẩu ban đầu",
        "header_edit": "✏️ Cập nhật thông tin nhân viên",
        "header_delete": "🗑️ Xóa hoặc vô hiệu hóa tài khoản nhân viên",
        "lbl_code": "Mã nhân viên (Tên đăng nhập) *",
        "lbl_name": "Họ tên nhân viên *",
        "lbl_factory": "Nhà máy làm việc *",
        "factory_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "lbl_dept": "Phòng ban *",
        "dept_opts": ["Ban Giám đốc", "Phòng Quản lý", "Phòng Kỹ thuật", "Phòng Sản xuất", "Phòng IT"],
        "lbl_pwd": "Mật khẩu ban đầu *",
        "lbl_title": "Chức vụ *",
        "lbl_country": "Quốc tịch",
        "country_opts": ["Việt Nam", "Đài Loan", "Trung Quốc"],  # 👈 越南文版國籍
        "lbl_role": "Vai trò Phân quyền hệ thống *",
        "lbl_addr_perm": "Hộ khẩu thường trú",
        "lbl_addr_temp": "Chỗ ở hiện tại",
        "btn_add": "🚀 Thêm nhân viên mới",
        "success_add": "✅ Đã thêm nhân viên `{name}` (Mã: `{code}`) thành công!",
        "btn_update": "💾 Lưu thay đổi",
        "success_update": "✅ Đã cập nhật thông tin nhân viên `{code}`!",
        "btn_delete": "⚠️ Xác nhận vô hiệu hóa tài khoản",
        "success_delete": "✅ Đã vô hiệu hóa nhân viên `{code}`.",
        "search_ph": "🔍 Tìm kiếm theo tên hoặc mã NV...",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_factory": "Nhà máy",
        "col_dept": "Phòng ban",
        "col_title": "Chức vụ",
        "col_role": "Vai trò",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "👤 Management - Employee Profile & HR Center",
        "caption": "Manage employee records, plant allocation (Tay Ninh/Hai Phong), initial passwords, and system roles.",
        "tab_list": "👥 Employee Directory",
        "tab_add": "➕ Add New Employee",
        "tab_edit": "✏️ Edit Employee Profile",
        "tab_delete": "🗑️ Disable / Delete Account",
        "header_list": "📋 Company Employee Directory & Role Overview",
        "header_add": "➕ Add Employee Profile & Initial Credentials",
        "header_edit": "✏️ Update Employee Information",
        "header_delete": "🗑️ Deactivate Employee Account",
        "lbl_code": "Employee ID (Login Username) *",
        "lbl_name": "Employee Name *",
        "lbl_factory": "Work Plant *",
        "factory_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "lbl_dept": "Department *",
        "dept_opts": ["Executive Office", "Management Dept", "Engineering Dept", "Production Dept", "IT Dept"],
        "lbl_pwd": "Initial Password *",
        "lbl_title": "Job Title *",
        "lbl_country": "Nationality",
        "country_opts": ["Vietnam", "Taiwan", "China"],  # 👈 英文版國籍
        "lbl_role": "System Access Role *",
        "lbl_addr_perm": "Permanent Address",
        "lbl_addr_temp": "Temporary Address",
        "btn_add": "🚀 Create Employee Account",
        "success_add": "✅ Successfully added employee `{name}` (ID: `{code}`)!",
        "btn_update": "💾 Save Changes",
        "success_update": "✅ Employee `{code}` updated successfully!",
        "btn_delete": "⚠️ Confirm Deactivation",
        "success_delete": "✅ Employee `{code}` deactivated.",
        "search_ph": "🔍 Search by name or ID...",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_factory": "Plant",
        "col_dept": "Department",
        "col_title": "Title",
        "col_role": "Role",
        "col_status": "Status"
    }
}

# 🌐 系統權限角色多語系對應字典
ROLE_I18N = {
    "繁體中文": {
        "admin": "系統管理員 (Admin)",
        "chairman": "董事長 (Chairman)",
        "generalmanager": "總經理 (General Manager)",
        "vicemanager": "副總經理 (Vice Manager)",
        "manager": "部門經理 / 小主管 (Manager)",
        "staff": "一般員工 (Staff)",
        "security": "廠區警衛/門禁 (Security)"
    },
    "Tiếng Việt": {
        "admin": "Quản trị hệ thống (Admin)",
        "chairman": "Chủ tịch (Chairman)",
        "generalmanager": "Tổng Giám đốc (General Manager)",
        "vicemanager": "Phó Tổng Giám đốc (Vice Manager)",
        "manager": "Trưởng phòng / Quản lý (Manager)",
        "staff": "Nhân viên (Staff)",
        "security": "Bảo vệ / An ninh (Security)"
    },
    "English": {
        "admin": "System Administrator (Admin)",
        "chairman": "Chairman",
        "generalmanager": "General Manager",
        "vicemanager": "Vice Manager",
        "manager": "Department Manager / Supervisor",
        "staff": "Staff",
        "security": "Security Guard"
    }
}

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in EMP_I18N else "繁體中文"
    L = EMP_I18N[active_lang]
    role_dict = ROLE_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "工號": "TW-001",
                "姓名": "李佑銘",
                "廠區": "西寧廠 (Tay Ninh)",
                "部門": "總經理室",
                "職稱": "董事長",
                "國籍": "台灣 (Taiwan)",
                "角色": "admin",
                "密碼": "123456",
                "must_change_password": False,
                "狀態": "🟢 在職 (Active)"
            },
            {
                "工號": "VN-002",
                "姓名": "Nguyễn Văn Quý",
                "廠區": "海防廠 (Hai Phong)",
                "部門": "管理部",
                "職稱": "廠務經理",
                "國籍": "越南 (Vietnam)",
                "角色": "manager",
                "密碼": "123456",
                "must_change_password": True,
                "狀態": "🟢 在職 (Active)"
            }
        ]

    tab_list, tab_add, tab_edit, tab_delete = st.tabs([
        L["tab_list"], L["tab_add"], L["tab_edit"], L["tab_delete"]
    ])

    with tab_list:
        st.markdown(f"### {L['header_list']}")
        search_q = st.text_input(L["search_ph"], key="emp_search_box")

        data = st.session_state.employee_db
        if search_q:
            data = [
                e for e in data 
                if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower()
            ]

        if data:
            display_list = []
            for idx, emp in enumerate(data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: emp["工號"],
                    L["col_name"]: emp["姓名"],
                    L["col_factory"]: emp["廠區"],
                    L["col_dept"]: emp["部門"],
                    L["col_title"]: emp["職稱"],
                    L["col_role"]: role_display,
                    L["col_status"]: emp["狀態"]
                })
            st.dataframe(pd.DataFrame(display_list), use_container_width=True)
        else:
            st.info("目前尚無員工資料。")

    with tab_add:
        st.markdown(f"### {L['header_add']}")
        with st.form("form_add_employee"):
            c1, c2 = st.columns(2)
            with c1:
                e_code = st.text_input(L["lbl_code"], value="VN-003")
                e_name = st.text_input(L["lbl_name"])
                e_pwd = st.text_input(L["lbl_pwd"], value="123456")
                e_country = st.selectbox(L["lbl_country"], L["country_opts"])
            with c2:
                e_factory = st.selectbox(L["lbl_factory"], L["factory_opts"])
                e_dept = st.selectbox(L["lbl_dept"], L["dept_opts"])
                e_title = st.text_input(L["lbl_title"], value="財務主管")
                
                role_keys = list(role_dict.keys())
                role_display_names = list(role_dict.values())
                sel_role_display = st.selectbox(L["lbl_role"], role_display_names)
                e_role = role_keys[role_display_names.index(sel_role_display)]

            e_addr_perm = st.text_input(L["lbl_addr_perm"])
            e_addr_temp = st.text_input(L["lbl_addr_temp"])

            if st.form_submit_button(L["btn_add"], type="primary", use_container_width=True):
                if e_code and e_name:
                    st.session_state.employee_db.append({
                        "工號": e_code,
                        "姓名": e_name,
                        "廠區": e_factory,
                        "部門": e_dept,
                        "職稱": e_title,
                        "國籍": e_country,
                        "角色": e_role,
                        "密碼": e_pwd,
                        "must_change_password": True,
                        "狀態": "🟢 在職 (Active)"
                    })
                    st.success(L["success_add"].format(name=e_name, code=e_code))
                else:
                    st.warning("⚠️ 請填寫員工工號與姓名！")

    with tab_edit:
        st.markdown(f"### {L['header_edit']}")
        if st.session_state.employee_db:
            emp_codes = [e["工號"] + " - " + e["姓名"] for e in st.session_state.employee_db]
            sel_target = st.selectbox("選擇要修改的員工 (Select Employee)", emp_codes, key="edit_emp_select")
            target_code = sel_target.split(" - ")[0]
            
            target_emp = next((e for e in st.session_state.employee_db if e["工號"] == target_code), None)
            
            if target_emp:
                with st.form("form_edit_employee"):
                    ed_name = st.text_input(L["lbl_name"], value=target_emp["姓名"])
                    ed_factory = st.selectbox(L["lbl_factory"], L["factory_opts"], index=0 if "西寧" in target_emp["廠區"] else 1)
                    ed_title = st.text_input(L["lbl_title"], value=target_emp["職稱"])
                    
                    role_keys = list(role_dict.keys())
                    role_display_names = list(role_dict.values())
                    current_role_idx = role_keys.index(target_emp["角色"]) if target_emp["角色"] in role_keys else 0
                    sel_ed_role_display = st.selectbox(L["lbl_role"], role_display_names, index=current_role_idx)
                    ed_role = role_keys[role_display_names.index(sel_ed_role_display)]
                    
                    ed_pwd = st.text_input("重設新密碼 (Reset Password)", value=target_emp.get("密碼", "123456"))

                    if st.form_submit_button(L["btn_update"], type="primary", use_container_width=True):
                        target_emp["姓名"] = ed_name
                        target_emp["廠區"] = ed_factory
                        target_emp["職稱"] = ed_title
                        target_emp["角色"] = ed_role
                        target_emp["密碼"] = ed_pwd
                        st.success(L["success_update"].format(code=target_code))
        else:
            st.info("尚無員工可供修改。")

    with tab_delete:
        st.markdown(f"### {L['header_delete']}")
        if st.session_state.employee_db:
            del_codes = [e["工號"] + " - " + e["姓名"] for e in st.session_state.employee_db]
            sel_del = st.selectbox("選擇要停用的員工", del_codes, key="del_emp_select")
            del_code = sel_del.split(" - ")[0]

            if st.button(L["btn_delete"], type="secondary"):
                st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != del_code]
                st.success(L["success_delete"].format(code=del_code))
                st.rerun()
        else:
            st.info("尚無員工可供停用。")

def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)

def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
