import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    # 🌐 人事管理模組多語系字典 (i18n)
    EMP_I18N = {
        "繁體中文": {
            "title": "👤 管理部 - 員工個人檔案與人事管理",
            "info": "在此維護全廠區員工個人檔案、保險資料、戶籍/暫住地址、保險醫院與人事資料。",
            "search_label": "🔍 搜尋員工姓名 / 工號 / 職稱",
            "search_ph": "輸入關鍵字搜尋員工...",
            "list_title": "### 📋 現有在職員工名冊",
            "resigned_title": "### 🚪 離職人員歸檔名冊",
            "tabs": ["➕ 新增員工", "✏️ 修改員工資料", "🗑️ 刪除或離職"],
            "add_header": "### ➕ 新增員工個人檔案與保險/地址資料",
            "lbl_id": "員工工號",
            "lbl_name": "員工姓名 (Employee Name)",
            "lbl_nat": "國籍",
            "nat_opts": ["台灣 (Taiwan)", "越南 (Vietnam)", "其他 (Other)"],
            "lbl_perm": "戶籍地址 (Permanent Address / Hộ khẩu thường trú)",
            "lbl_temp": "暫住地址 (Temporary Address / Chỗ ở hiện tại)",
            "lbl_fac": "工作廠區 (Factory)",
            "lbl_dept": "部門",
            "lbl_title": "職稱 / 職務",
            "title_ph": "例如: 董事長 / 總經理 / 經理 / 現場工程師...",
            "lbl_role": "系統權限角色",
            "lbl_phone": "聯絡電話",
            "phone_ph": "0912...",
            "lbl_insurance": "保險資料 / 社會保險編號 (Insurance / BHXH)",
            "lbl_hospital": "保險醫院 / 就醫指定醫院 (Insurance Hospital)",
            "btn_add": "🚀 立即新增員工",
            "success_add": "✅ 員工 {name} 新增成功！",
            "warn_name": "⚠️ 請填寫員工姓名！",
            "edit_header": "### ✏️ 修改員工檔案與保險/地址資料",
            "select_edit": "選擇要修改的員工",
            "btn_save_edit": "💾 儲存修改",
            "success_edit": "✅ 員工 {id} 資料更新成功！",
            "no_emp_edit": "目前無員工資料可供修改。",
            "del_header": "### 🗑️ 刪除重複或辦理離職歸檔",
            "select_del": "選擇要處理的員工",
            "warn_del_title": "您正在處理員工：",
            "btn_del_hard": "🔥 完全刪除 (移除重複建檔)",
            "btn_del_resign": "🚪 辦理離職 (移至離職歸檔表)",
            "success_hard": "✅ 員工 {id} 已自系統完全刪除！",
            "success_resign": "🚪 員工 {id} 已成功移至離職歸檔表！",
            "no_emp_del": "目前無員工資料可供處理。"
        },
        "Tiếng Việt": {
            "title": "👤 Quản lý Nhân sự & Hồ sơ Nhân viên",
            "info": "Nơi quản lý hồ sơ nhân viên, bảo hiểm, địa chỉ và thông tin chi tiết toàn nhà máy.",
            "search_label": "🔍 Tìm kiếm nhân viên theo tên / Mã NV / Chức vụ",
            "search_ph": "Nhập từ khóa tìm kiếm...",
            "list_title": "### 📋 Danh sách Nhân viên hiện tại",
            "resigned_title": "### 🚪 Danh sách Nhân viên đã nghỉ việc",
            "tabs": ["➕ Thêm nhân viên", "✏️ Sửa thông tin", "🗑️ Xóa hoặc Nghỉ việc"],
            "add_header": "### ➕ Thêm hồ sơ nhân sự, bảo hiểm & địa chỉ mới",
            "lbl_id": "Mã nhân viên (Employee ID)",
            "lbl_name": "Họ tên nhân viên (Employee Name)",
            "lbl_nat": "Quốc tịch (Nationality)",
            "nat_opts": ["Việt Nam (Vietnam)", "Đài Loan (Taiwan)", "Khác (Other)"],
            "lbl_perm": "Hộ khẩu thường trú (Permanent Address)",
            "lbl_temp": "Chỗ ở hiện tại / Tạm trú (Temporary Address)",
            "lbl_fac": "Khu vực nhà máy (Factory)",
            "lbl_dept": "Phòng ban (Department)",
            "lbl_title": "Chức vụ / Vị trí (Job Title)",
            "title_ph": "Ví dụ: Chủ tịch / Tổng Giám đốc / Kỹ sư hiện trường...",
            "lbl_role": "Vai trò phân quyền hệ thống (System Role)",
            "lbl_phone": "Số điện thoại liên hệ",
            "phone_ph": "0912...",
            "lbl_insurance": "Số bảo hiểm xã hội (Insurance / BHXH)",
            "lbl_hospital": "Bệnh viện khám chữa bệnh BHYT (Hospital)",
            "btn_add": "🚀 Thêm nhân viên mới",
            "success_add": "✅ Thêm nhân viên {name} thành công!",
            "warn_name": "⚠️ Vui lòng nhập tên nhân viên!",
            "edit_header": "### ✏️ Chỉnh sửa hồ sơ nhân sự & bảo hiểm",
            "select_edit": "Chọn nhân viên cần sửa",
            "btn_save_edit": "💾 Lưu thay đổi",
            "success_edit": "✅ Cập nhật thông tin nhân viên {id} thành công!",
            "no_emp_edit": "Hiện không có nhân viên nào để chỉnh sửa.",
            "del_header": "### 🗑️ Xóa trùng lặp hoặc Thủ tục nghỉ việc",
            "select_del": "Chọn nhân viên cần xử lý",
            "warn_del_title": "Bạn đang xử lý nhân viên:",
            "btn_del_hard": "🔥 Xóa hoàn toàn (Xóa bản ghi trùng)",
            "btn_del_resign": "🚪 Làm thủ tục nghỉ việc (Chuyển sang lưu trữ)",
            "success_hard": "✅ Đã xóa hoàn toàn nhân viên {id} khỏi hệ thống!",
            "success_resign": "🚪 Đã chuyển nhân viên {id} vào danh sách nghỉ việc!",
            "no_emp_del": "Hiện không có nhân viên nào để xử lý."
        },
        "English": {
            "title": "👤 Management Dept - HR & Employee Records",
            "info": "Manage employee profiles, insurance, addresses, and personnel records across all plants.",
            "search_label": "🔍 Search Employee Name / ID / Title",
            "search_ph": "Enter keyword to search...",
            "list_title": "### 📋 Current Employee Directory",
            "resigned_title": "### 🚪 Resigned Employee Archive",
            "tabs": ["➕ Add Employee", "✏️ Edit Employee", "🗑️ Delete or Resign"],
            "add_header": "### ➕ Add New Employee Profile & Insurance/Address",
            "lbl_id": "Employee ID",
            "lbl_name": "Employee Name",
            "lbl_nat": "Nationality",
            "nat_opts": ["Taiwan (Taiwan)", "Vietnam (Vietnam)", "Other (Other)"],
            "lbl_perm": "Permanent Address",
            "lbl_temp": "Temporary Address",
            "lbl_fac": "Factory Location",
            "lbl_dept": "Department",
            "lbl_title": "Job Title / Position",
            "title_ph": "e.g., Chairman / General Manager / Engineer...",
            "lbl_role": "System Permission Role",
            "lbl_phone": "Phone Number",
            "phone_ph": "0912...",
            "lbl_insurance": "Insurance / Social Security No. (BHXH)",
            "lbl_hospital": "Designated Hospital (Bệnh viện KCB)",
            "btn_add": "🚀 Add New Employee",
            "success_add": "✅ Employee {name} added successfully!",
            "warn_name": "⚠️ Please enter employee name!",
            "edit_header": "### ✏️ Edit Employee Profile & Details",
            "select_edit": "Select Employee to Edit",
            "btn_save_edit": "💾 Save Changes",
            "success_edit": "✅ Employee {id} updated successfully!",
            "no_emp_edit": "No employee records available for editing.",
            "del_header": "### 🗑️ Delete Duplicate or Process Resignation",
            "select_del": "Select Employee to Process",
            "warn_del_title": "You are processing employee:",
            "btn_del_hard": "🔥 Completely Delete (Remove Duplicate)",
            "btn_del_resign": "🚪 Process Resignation (Move to Archive)",
            "success_hard": "✅ Employee {id} completely deleted from system!",
            "success_resign": "🚪 Employee {id} successfully moved to resignation archive!",
            "no_emp_del": "No employee records available for processing."
        }
    }

    active_lang = lang if lang in EMP_I18N else "繁體中文"
    L = EMP_I18N[active_lang]

    st.title(L["title"])
    st.info(L["info"])

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "工號": "EMP-001", "姓名": "張董事長", "國籍": "台灣 (Taiwan)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "總經理室", "職稱": "董事長 (Chairman)", "角色": "Chairman", "電話": "0912345678", 
                "戶籍地址": "台北市信義區...", "暫住地址": "西寧省廠區宿舍", "保險資料": "TW-INS-888899", "保險醫院": "台北榮民總醫院", "生物辨識代碼": "FACE-BIO-888899"
            },
            {
                "工號": "EMP-002", "姓名": "Nguyễn Văn A", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "總經理室", "職稱": "總經理 (General Manager)", "角色": "GeneralManager", "電話": "0918999080", 
                "戶籍地址": "Tỉnh Tây Ninh, Huyện Trảng Bàng", "暫住地址": "Khu công nghiệp Thành Thành Công", "保險資料": "VN-BHXH-0192834", "保險醫院": "Bệnh viện Đa khoa Tây Ninh", "生物辨識代碼": "FACE-BIO-100234"
            }
        ]

    if "resigned_employee_db" not in st.session_state:
        st.session_state.resigned_employee_db = []

    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人": "張董事長", "電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)", "負責人": "阮文強", "電話": "0918999080"}
        ]

    search_q = st.text_input(L["search_label"], placeholder=L["search_ph"])
    
    filtered_emp = [
        e for e in st.session_state.employee_db 
        if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower() or search_q.lower() in e["職稱"].lower()
    ] if search_q else st.session_state.employee_db

    st.markdown(L["list_title"])
    st.dataframe(pd.DataFrame(filtered_emp), use_container_width=True)

    if st.session_state.resigned_employee_db:
        st.markdown(L["resigned_title"])
        st.dataframe(pd.DataFrame(st.session_state.resigned_employee_db), use_container_width=True)

    tab_add, tab_edit, tab_del = st.tabs(L["tabs"])

    with tab_add:
        with st.form("add_employee_form"):
            st.markdown(L["add_header"])
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input(L["lbl_id"], value=f"EMP-{len(st.session_state.employee_db)+1:03d}")
                e_name = st.text_input(L["lbl_name"])
                e_nat = st.selectbox(L["lbl_nat"], L["nat_opts"])
                e_perm_addr = st.text_input(L["lbl_perm"])
                e_temp_addr = st.text_input(L["lbl_temp"])
            with c2:
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if not fac_choices:
                    fac_choices = ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"]
                e_fac = st.selectbox(L["lbl_fac"], fac_choices)
                
                # 部門多語系對應
                if active_lang == "Tiếng Việt":
                    dept_display_map = {
                        "總經理室": "Ban Giám đốc (Executive Office)",
                        "管理部": "Phòng Quản lý (Management Dept)",
                        "工程與設計管理中心": "Trung tâm Kỹ thuật & Thiết kế",
                        "生產部": "Phòng Sản xuất (Production Dept)"
                    }
                elif active_lang == "English":
                    dept_display_map = {
                        "總經理室": "Executive Office",
                        "管理部": "Management Dept",
                        "工程與設計管理中心": "Engineering & Design Center",
                        "生產部": "Production Dept"
                    }
                else:
                    dept_display_map = {
                        "總經理室": "總經理室 (Executive Office)",
                        "管理部": "管理部",
                        "工程與設計管理中心": "工程與設計管理中心",
                        "生產部": "生產部"
                    }
                
                dept_keys = list(dept_display_map.keys())
                dept_sel = st.selectbox(L["lbl_dept"], dept_keys, format_func=lambda x: dept_display_map[x])
                e_dept = dept_sel

                e_title = st.text_input(L["lbl_title"], placeholder=L["title_ph"])

                # 角色多語系對應
                if active_lang == "Tiếng Việt":
                    role_display_map = {
                        "Chairman": "Chủ tịch HĐQT (Chairman)",
                        "GeneralManager": "Tổng Giám đốc (General Manager)",
                        "ViceManager": "Phó Tổng Giám đốc (Vice GM)",
                        "AVP": "Phó Giám đốc / Trợ lý cấp cao (AVP)",
                        "DeputyAVP": "Phó Trợ lý cấp cao (Deputy AVP)",
                        "Manager": "Quản lý / Trưởng phòng (Manager)",
                        "AdminManager": "Quản lý Hành chính (Admin Manager)",
                        "FinanceManager": "Quản lý Tài chính (Finance Manager)",
                        "Staff": "Nhân viên chung (Staff)",
                        "admin": "Quản trị hệ thống (Admin)"
                    }
                elif active_lang == "English":
                    role_display_map = {
                        "Chairman": "Chairman",
                        "GeneralManager": "General Manager",
                        "ViceManager": "Vice General Manager",
                        "AVP": "Assistant Vice President (AVP)",
                        "DeputyAVP": "Deputy AVP",
                        "Manager": "Manager",
                        "AdminManager": "Administrative Manager",
                        "FinanceManager": "Finance Manager",
                        "Staff": "General Staff",
                        "admin": "System Administrator (Admin)"
                    }
                else:
                    role_display_map = {
                        "Chairman": "董事長 (Chairman)",
                        "GeneralManager": "總經理 (General Manager)",
                        "ViceManager": "副總經理 (Vice General Manager)",
                        "AVP": "協理 (AVP)",
                        "DeputyAVP": "副協理 (Deputy AVP)",
                        "經理": "經理 (Manager)",
                        "AdminManager": "行政主管 (Admin Manager)",
                        "FinanceManager": "財務主管 (Finance Manager)",
                        "Staff": "一般員工 (Staff)",
                        "admin": "系統管理員 (Admin)"
                    }

                role_keys = list(role_display_map.keys())
                role_sel = st.selectbox(L["lbl_role"], role_keys, format_func=lambda x: role_display_map[x])
                e_role = role_sel

                e_phone = st.text_input(L["lbl_phone"], placeholder=L["phone_ph"])
                e_insurance = st.text_input(L["lbl_insurance"])
                e_hospital = st.text_input(L["lbl_hospital"])

            if st.form_submit_button(L["btn_add"], type="primary"):
                if e_name:
                    st.session_state.employee_db.append({
                        "工號": e_id,
                        "姓名": e_name,
                        "國籍": e_nat,
                        "工作廠區": e_fac,
                        "部門": e_dept,
                        "職稱": e_title,
                        "角色": e_role,
                        "電話": e_phone,
                        "戶籍地址": e_perm_addr,
                        "暫住地址": e_temp_addr,
                        "保險資料": e_insurance,
                        "保險醫院": e_hospital,
                        "生物辨識代碼": f"FACE-BIO-{len(st.session_state.employee_db)+100000}"
                    })
                    st.success(L["success_add"].format(name=e_name))
                    st.rerun()
                else:
                    st.warning(L["warn_name"])

    with tab_edit:
        if st.session_state.employee_db:
            emp_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox(L["select_edit"], list(emp_opts.keys()))
            target_emp = emp_opts[sel_emp_key]

            with st.form("edit_employee_form"):
                st.markdown(L["edit_header"])
                ed_name = st.text_input(L["lbl_name"], value=target_emp["姓名"])
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                if target_emp["工作廠區"] not in fac_choices:
                    fac_choices.append(target_emp["工作廠區"])
                ed_fac = st.selectbox(L["lbl_fac"], fac_choices, index=fac_choices.index(target_emp["工作廠區"]) if target_emp["工作廠區"] in fac_choices else 0)
                ed_title = st.text_input(L["lbl_title"], value=target_emp["職稱"])
                ed_phone = st.text_input(L["lbl_phone"], value=target_emp["電話"])
                ed_perm_addr = st.text_input(L["lbl_perm"], value=target_emp.get("戶籍地址", ""))
                ed_temp_addr = st.text_input(L["lbl_temp"], value=target_emp.get("暫住地址", ""))
                ed_insurance = st.text_input(L["lbl_insurance"], value=target_emp.get("保險資料", ""))
                ed_hospital = st.text_input(L["lbl_hospital"], value=target_emp.get("Bệnh viện khám chữa bệnh BHYT" if active_lang=="Tiếng Việt" else "保險醫院", ""))

                if st.form_submit_button(L["btn_save_edit"], type="primary"):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_emp["工號"]:
                            e["姓名"] = ed_name
                            e["工作廠區"] = ed_fac
                            e["職稱"] = ed_title
                            e["電話"] = ed_phone
                            e["戶籍地址"] = ed_perm_addr
                            e["暫住地址"] = ed_temp_addr
                            e["保險資料"] = ed_insurance
                            e["保險醫院"] = ed_hospital
                    st.success(L["success_edit"].format(id=target_emp["工號"]))
                    st.rerun()
        else:
            st.info(L["no_emp_edit"])

    with tab_del:
        if st.session_state.employee_db:
            del_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_del_key = st.selectbox(L["select_del"], list(del_opts.keys()))
            target_del = del_opts[sel_del_key]

            with st.form("delete_employee_form"):
                st.markdown(L["del_header"])
                st.warning(f"{L['warn_del_title']} **{target_del['工號']} - {target_del['姓名']}**")
                
                col_btn1, col_btn2 = st.columns(2)
                do_delete = col_btn1.form_submit_button(L["btn_del_hard"])
                do_resign = col_btn2.form_submit_button(L["btn_del_resign"])

                if do_delete:
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_del["工號"]]
                    st.success(L["success_hard"].format(id=target_del['工號']))
                    st.rerun()

                if do_resign:
                    resigned_record = target_del.copy()
                    resigned_record["離職時間"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.resigned_employee_db.append(resigned_record)
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_del["工號"]]
                    st.success(L["success_resign"].format(id=target_del['工號']))
                    st.rerun()
        else:
            st.info(L["no_emp_del"])

def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)

def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
