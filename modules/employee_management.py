import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 員工與人事管理模組多語系字典 (i18n)
# ----------------------------------------------------
EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司在職員工名冊、離職歷史檔案、回鍋復職、新增員工與權限角色（含廠內與外勤GPS出勤性質分流）。",
        "tab_list": "👥 現職員工名冊",
        "tab_resigned": "📂 離職與歷史名冊 (Archive)",
        "tab_add": "➕ 新增員工與初始帳密設定",
        "tab_edit": "✏️ 修改員工資料與重設密碼",
        "tab_delete": "🗑️ 離職歸檔與帳號刪除",
        "header_list": "📋 全公司現職員工名冊與權限總覽",
        "header_resigned": "📂 離職歷史人員名冊與復職管理",
        "header_add": "➕ 新增員工個人檔案與初始帳密設定",
        "header_edit": "✏️ 修改員工基本資料與權限",
        "header_delete": "🗑️ 辦理離職歸檔或徹底刪除重複帳號",
        "lbl_code": "員工工號 (登入帳號) *",
        "lbl_name": "員工姓名 (Employee Name) *",
        "lbl_factory": "工作廠區 (Factory) *",
        "factory_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
        "lbl_dept": "部門 *",
        "dept_opts": ["總經理室", "管理部", "工程部", "生產部", "資訊部"],
        "lbl_pwd": "初始登入密碼 (預設) *",
        "lbl_title": "職稱 / 職務 *",
        "lbl_attendance": "出勤性質歸屬 (Attendance Type) *",
        "attendance_opts": ["廠內固定員工 (Plant Fixed Attendance)", "外勤GPS工地人員 (Field GPS Site Staff)"],
        "lbl_country": "國籍",
        "country_opts": ["台灣 (Taiwan)", "越南 (Vietnam)", "中國 (China)"],
        "lbl_role": "系統權限角色 *",
        "lbl_addr_perm": "戶籍地址 (Permanent Address)",
        "lbl_addr_temp": "現住地址 (Temporary Address)",
        "btn_add": "🚀 立即新增員工並建立帳號",
        "success_add": "✅ 成功新增員工 `{name}` (工號: `{code}`)！已成功歸納至指定出勤性質。",
        "btn_update": "💾 儲存修改後員工資料",
        "success_update": "✅ 員工 `{code}` 資料已成功更新！",
        "btn_archive": "📂 將此員工辦理離職歸檔",
        "success_archive": "✅ 員工 `{code}` 已移至離職歷史名冊。",
        "btn_reactivate": "🔄 辦理回鍋復職 (Reactivate)",
        "success_reactivate": "🎉 員工 `{code}` 已成功復職並轉為現職員工！",
        "btn_hard_delete": "🔥 徹底刪除帳號 (僅適用於重複建檔錯誤)",
        "success_hard_delete": "🔥 帳號 `{code}` 已自系統中徹底刪除。",
        "search_ph": "🔍 搜尋員工姓名或工號...",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_factory": "廠區",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_attendance": "出勤性質",
        "col_role": "系統角色",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Nhân sự & Hồ sơ Nhân viên",
        "caption": "Quản lý danh sách nhân viên hiện tại, lưu trữ nghỉ việc, tái tuyển dụng và phân quyền.",
        "tab_list": "👥 Nhân viên hiện tại",
        "tab_resigned": "📂 Lịch sử nhân viên nghỉ việc",
        "tab_add": "➕ Thêm Nhân viên mới",
        "tab_edit": "✏️ Chỉnh sửa Thông tin",
        "tab_delete": "🗑️ Lưu trữ & Xóa",
        "header_list": "📋 Danh sách nhân viên đang làm việc",
        "header_resigned": "📂 Hồ sơ nhân viên đã nghỉ việc & Tái tuyển dụng",
        "header_add": "➕ Thêm hồ sơ nhân viên",
        "header_edit": "✏️ Cập nhật thông tin",
        "header_delete": "🗑️ Xử lý nghỉ việc hoặc Xóa vĩnh viễn",
        "lbl_code": "Mã nhân viên *",
        "lbl_name": "Họ tên nhân viên *",
        "lbl_factory": "Nhà máy *",
        "factory_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "lbl_dept": "Phòng ban *",
        "lbl_dept_opts": ["Ban Giám đốc", "Phòng Quản lý", "Phòng Kỹ thuật", "Phòng Sản xuất", "Phòng IT"],
        "lbl_pwd": "Mật khẩu ban đầu *",
        "lbl_title": "Chức vụ *",
        "lbl_attendance": "Tính chất chấm công *",
        "attendance_opts": ["Nhân viên làm việc tại nhà máy", "Nhân viên ngoại tuyến GPS công trường"],
        "lbl_country": "Quốc tịch",
        "country_opts": ["Đài Loan", "Việt Nam", "Trung Quốc"],
        "lbl_role": "Vai trò hệ thống *",
        "lbl_addr_perm": "Hộ khẩu thường trú",
        "lbl_addr_temp": "Chỗ ở hiện tại",
        "btn_add": "🚀 Thêm nhân viên mới",
        "success_add": "✅ Đã thêm nhân viên `{name}` thành công!",
        "btn_update": "💾 Lưu thay đổi",
        "success_update": "✅ Đã cập nhật thành công!",
        "btn_archive": "📂 Lưu trữ nghỉ việc",
        "success_archive": "✅ Đã chuyển sang danh sách nghỉ việc.",
        "btn_reactivate": "🔄 Tái tuyển dụng (Phục hồi)",
        "success_reactivate": "🎉 Nhân viên `{code}` đã đi làm trở lại!",
        "btn_hard_delete": "🔥 Xóa vĩnh viễn",
        "success_hard_delete": "🔥 Đã xóa vĩnh viễn.",
        "search_ph": "🔍 Tìm kiếm...",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_factory": "Nhà máy",
        "col_dept": "Phòng ban",
        "col_title": "Chức vụ",
        "col_attendance": "Chấm công",
        "col_role": "Vai trò",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "👤 Management - Employee Profile & HR Center",
        "caption": "Manage active employees, resigned history archives, rehiring, and roles.",
        "tab_list": "👥 Active Employees",
        "tab_resigned": "📂 Resigned Archives",
        "tab_add": "➕ Add Employee",
        "tab_edit": "✏️ Edit Profile",
        "tab_delete": "🗑️ Archive / Delete",
        "header_list": "📋 Active Employee Directory",
        "header_resigned": "📂 Resigned Employee History & Rehiring",
        "header_add": "➕ Add Employee Profile",
        "header_edit": "✏️ Update Employee Info",
        "header_delete": "🗑️ Archive Resigned or Delete Duplicates",
        "lbl_code": "Employee ID *",
        "lbl_name": "Employee Name *",
        "lbl_factory": "Work Plant *",
        "factory_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "lbl_dept": "Department *",
        "dept_opts": ["Executive Office", "Management Dept", "Engineering Dept", "Production Dept", "IT Dept"],
        "lbl_pwd": "Initial Password *",
        "lbl_title": "Job Title *",
        "lbl_attendance": "Attendance Nature *",
        "attendance_opts": ["Plant Fixed Attendance", "Field GPS Site Staff"],
        "lbl_country": "Nationality",
        "country_opts": ["Taiwan", "Vietnam", "China"],
        "lbl_role": "System Role *",
        "lbl_addr_perm": "Permanent Address",
        "lbl_addr_temp": "Temporary Address",
        "btn_add": "🚀 Create Employee",
        "success_add": "✅ Successfully added employee `{name}`!",
        "btn_update": "💾 Save Changes",
        "success_update": "✅ Updated successfully!",
        "btn_archive": "📂 Archive as Resigned",
        "success_archive": "✅ Archived successfully.",
        "btn_reactivate": "🔄 Rehired (Reactivate)",
        "success_reactivate": "🎉 Employee `{code}` reactivated successfully!",
        "btn_hard_delete": "🔥 Permanently Delete",
        "success_hard_delete": "🔥 Permanently deleted.",
        "search_ph": "🔍 Search...",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_factory": "Plant",
        "col_dept": "Department",
        "col_title": "Title",
        "col_attendance": "Attendance",
        "col_role": "Role",
        "col_status": "Status"
    }
}

ROLE_I18N = {
    "繁體中文": {
        "admin": "系統管理員 (Admin)",
        "chairman": "董事長 (Chairman)",
        "generalmanager": "總經理 (General Manager)",
        "vicemanager": "副總經理 / 協理 (Vice Manager)",
        "manager": "部門經理 / 財務主管 / 廠長 (Manager)",
        "staff": "一般員工 / 作業員 (Staff)",
        "security": "廠區警衛/門禁 (Security)"
    },
    "Tiếng Việt": {
        "admin": "Quản trị hệ thống (Admin)",
        "chairman": "Chủ tịch (Chairman)",
        "generalmanager": "Tổng Giám đốc (General Manager)",
        "vicemanager": "Phó Tổng Giám đốc (Vice Manager)",
        "manager": "Trưởng phòng / Quản lý (Manager)",
        "staff": "Nhân viên (Staff)",
        "security": "Bảo vệ (Security)"
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
                "出勤性質": "廠內固定員工",
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
                "職稱": "財務主管",
                "出勤性質": "廠內固定員工",
                "國籍": "越南 (Vietnam)",
                "角色": "manager",
                "密碼": "123456",
                "must_change_password": True,
                "狀態": "🟢 在職 (Active)"
            },
            {
                "工號": "VN-003",
                "姓名": "Phạm Văn Nam",
                "廠區": "西寧廠 (Tay Ninh)",
                "部門": "工程部",
                "職稱": "外勤工程師",
                "出勤性質": "外勤GPS工地人員",
                "國籍": "越南 (Vietnam)",
                "角色": "staff",
                "密碼": "123456",
                "must_change_password": True,
                "狀態": "🟢 在職 (Active)"
            }
        ]

    # 建立 5 個獨立分頁（現職名冊、離職歷史名冊、新增、修改、刪除管理）
    tab_list, tab_resigned, tab_add, tab_edit, tab_delete = st.tabs([
        L["tab_list"], L["tab_resigned"], L["tab_add"], L["tab_edit"], L["tab_delete"]
    ])

    # 1. 👥 現職員工名冊
    with tab_list:
        st.markdown(f"### {L['header_list']}")
        search_q = st.text_input(L["search_ph"], key="emp_search_box_active")

        active_data = [e for e in st.session_state.employee_db if "在職" in e["狀態"]]
        if search_q:
            active_data = [
                e for e in active_data 
                if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower()
            ]

        if active_data:
            display_list = []
            for idx, emp in enumerate(active_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: emp["工號"],
                    L["col_name"]: emp["姓名"],
                    L["col_factory"]: emp["廠區"],
                    L["col_dept"]: emp["部門"],
                    L["col_title"]: emp["職稱"],
                    L["col_attendance"]: emp.get("出勤性質", "廠內固定員工"),
                    L["col_role"]: role_display,
                    L["col_status"]: emp["狀態"]
                })
            st.dataframe(pd.DataFrame(display_list), use_container_width=True)
        else:
            st.info("目前尚無在職員工記錄。")

    # 2. 📂 離職與歷史名冊 (Archive)
    with tab_resigned:
        st.markdown(f"### {L['header_resigned']}")
        resigned_search = st.text_input("🔍 搜尋離職人員姓名或工號...", key="emp_search_box_resigned")

        resigned_data = [e for e in st.session_state.employee_db if "離職" in e["狀態"]]
        if resigned_search:
            resigned_data = [
                e for e in resigned_data 
                if resigned_search.lower() in e["姓名"].lower() or resigned_search.lower() in e["工號"].lower()
            ]

        if resigned_data:
            res_display_list = []
            for idx, emp in enumerate(resigned_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                res_display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: emp["工號"],
                    L["col_name"]: emp["姓名"],
                    L["col_factory"]: emp["廠區"],
                    L["col_dept"]: emp["部門"],
                    L["col_title"]: emp["職稱"],
                    L["col_attendance"]: emp.get("出勤性質", "廠內固定員工"),
                    L["col_role"]: role_display,
                    L["col_status"]: emp["狀態"]
                })
            st.dataframe(pd.DataFrame(res_display_list), use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🔄 離職人員回鍋復職 (Rehire / Reactivate)")
            rehire_opts = [e["工號"] + " - " + e["姓名"] for e in resigned_data]
            sel_rehire = st.selectbox("選擇要辦理復職的員工", rehire_opts, key="rehire_select")
            
            if st.button(L["btn_reactivate"], type="primary"):
                rehire_code = sel_rehire.split(" - ")[0]
                for e in st.session_state.employee_db:
                    if e["工號"] == rehire_code:
                        e["狀態"] = "🟢 在職 (Active)"
                st.success(L["success_reactivate"].format(code=rehire_code))
                st.rerun()
        else:
            st.info("📂 目前歷史檔案中無離職員工記錄。")

    # 3. ➕ 新增員工 (含職稱與出勤性質分流)
    with tab_add:
        st.markdown(f"### {L['header_add']}")
        auto_emp_id = f"VN-00{len(st.session_state.employee_db) + 1}"

        with st.form("form_add_employee"):
            c1, c2 = st.columns(2)
            with c1:
                e_code = st.text_input(L["lbl_code"], value=auto_emp_id)
                e_name = st.text_input(L["lbl_name"])
                e_pwd = st.text_input(L["lbl_pwd"], value="123456")
                e_country = st.selectbox(L["lbl_country"], L["country_opts"])
                e_attendance = st.selectbox(L["lbl_attendance"], L["attendance_opts"])
            with c2:
                e_factory = st.selectbox(L["lbl_factory"], L["factory_opts"])
                e_dept = st.selectbox(L["lbl_dept"], L["dept_opts"])
                e_title = st.text_input(L["lbl_title"], value="工程師 / 技術員")
                
                role_keys = list(role_dict.keys())
                role_display_names = list(role_dict.values())
                sel_role_display = st.selectbox(L["lbl_role"], role_display_names)
                e_role = role_keys[role_display_names.index(sel_role_display)]

            e_addr_perm = st.text_input(L["lbl_addr_perm"])
            e_addr_temp = st.text_input(L["lbl_addr_temp"])

            submitted = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted:
                if e_code and e_name:
                    existing_codes = [e["工號"] for e in st.session_state.employee_db]
                    if e_code in existing_codes:
                        st.error(f"⚠️ 錯誤：工號 `{e_code}` 已經存在！")
                    else:
                        st.session_state.employee_db.append({
                            "工號": e_code,
                            "姓名": e_name,
                            "廠區": e_factory,
                            "部門": e_dept,
                            "職稱": e_title,
                            "出勤性質": e_attendance,
                            "國籍": e_country,
                            "角色": e_role,
                            "密碼": e_pwd,
                            "must_change_password": True,
                            "狀態": "🟢 在職 (Active)"
                        })
                        st.success(L["success_add"].format(name=e_name, code=e_code))
                        st.rerun()
                else:
                    st.warning("⚠️ 請填寫員工工號與姓名！")

    # 4. ✏️ 修改員工 (含職稱與出勤性質)
    with tab_edit:
        st.markdown(f"### {L['header_edit']}")
        if st.session_state.employee_db:
            emp_codes = [e["工號"] + " - " + e["姓名"] + " (" + e["狀態"] + ")" for e in st.session_state.employee_db]
            sel_target = st.selectbox("選擇要修改的員工 (Select Employee)", emp_codes, key="edit_emp_select")
            target_code = sel_target.split(" - ")[0]
            
            target_emp = next((e for e in st.session_state.employee_db if e["工號"] == target_code), None)
            
            if target_emp:
                with st.form("form_edit_employee"):
                    ed_name = st.text_input(L["lbl_name"], value=target_emp["姓名"])
                    ed_factory = st.selectbox(L["lbl_factory"], L["factory_opts"], index=0 if "西寧" in target_emp["廠區"] else 1)
                    ed_title = st.text_input(L["lbl_title"], value=target_emp.get("職稱", ""))
                    
                    current_att = target_emp.get("出勤性質", L["attendance_opts"][0])
                    att_index = L["attendance_opts"].index(current_att) if current_att in L["attendance_opts"] else 0
                    ed_attendance = st.selectbox(L["lbl_attendance"], L["attendance_opts"], index=att_index)
                    
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
                        target_emp["出勤性質"] = ed_attendance
                        target_emp["角色"] = ed_role
                        target_emp["密碼"] = ed_pwd
                        st.success(L["success_update"].format(code=target_code))
                        st.rerun()
        else:
            st.info("尚無員工可供修改。")

    # 5. 🗑️ 離職歸檔與重複帳號徹底刪除
    with tab_delete:
        st.markdown(f"### {L['header_delete']}")
        
        if st.session_state.employee_db:
            all_emp_codes = [e["工號"] + " - " + e["姓名"] + " (" + e["狀態"] + ")" for e in st.session_state.employee_db]
            sel_target_del = st.selectbox("選擇要處理的員工帳號", all_emp_codes, key="manage_emp_select")
            target_code = sel_target_del.split(" - ")[0]

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button(L["btn_archive"], type="secondary", use_container_width=True):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_code:
                            e["狀態"] = "🔴 離職 (Resigned)"
                    st.success(L["success_archive"].format(code=target_code))
                    st.rerun()

            with col_btn2:
                if st.button(L["btn_hard_delete"], type="primary", use_container_width=True):
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_code]
                    st.success(L["success_hard_delete"].format(code=target_code))
                    st.rerun()
        else:
            st.info("目前系統中無任何員工記錄。")

def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)

def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
