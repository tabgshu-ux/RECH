import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    EMP_I18N = {
        "繁體中文": {
            "title": "👤 管理部 - 員工個人檔案與人事管理",
            "info": "在此維護全廠區員工個人檔案、保險資料、戶籍/暫住地址、保險醫院與初始登入密碼設定。",
            "search_label": "🔍 搜尋員工姓名 / 工號 / 職稱",
            "search_ph": "輸入關鍵字搜尋員工...",
            "list_title": "### 📋 現有在職員工名冊",
            "resigned_title": "### 🚪 離職人員歸檔名冊",
            "tabs": ["➕ 新增員工", "✏️ 修改員工資料", "🗑️ 刪除或離職"],
            "add_header": "### ➕ 新增員工個人檔案與初始帳密設定",
            "lbl_id": "員工工號 (登入帳號)",
            "lbl_name": "員工姓名 (Employee Name)",
            "lbl_pwd": "初始登入密碼 (預設)",
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
            "btn_add": "🚀 立即新增員工並建立帳號",
            "success_add": "✅ 員工 {name} 新增成功！初始密碼已設定，首次登入將強制要求修改。",
            "warn_name": "⚠️ 請填寫員工姓名與工號！",
            "edit_header": "### ✏️ 修改員工檔案與重設密碼",
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
            "info": "Quản lý hồ sơ nhân viên, bảo hiểm, địa chỉ và mật khẩu đăng nhập ban đầu.",
            "search_label": "🔍 Tìm kiếm nhân viên theo tên / Mã NV / Chức vụ",
            "search_ph": "Nhập từ khóa tìm kiếm...",
            "list_title": "### 📋 Danh sách Nhân viên hiện tại",
            "resigned_title": "### 🚪 Danh sách Nhân viên đã nghỉ việc",
            "tabs": ["➕ Thêm nhân viên", "✏️ Sửa thông tin", "🗑️ Xóa hoặc Nghỉ việc"],
            "add_header": "### ➕ Thêm nhân sự & Cấp mật khẩu ban đầu",
            "lbl_id": "Mã nhân viên (Tài khoản đăng nhập)",
            "lbl_name": "Họ tên nhân viên (Employee Name)",
            "lbl_pwd": "Mật khẩu ban đầu",
            "lbl_nat": "Quốc tịch (Nationality)",
            "nat_opts": ["Việt Nam (Vietnam)", "Đài Loan (Taiwan)", "Khác (Other)"],
            "lbl_perm": "Hộ khẩu thường trú (Permanent Address)",
            "lbl_temp": "Chỗ ở hiện tại / Tạm trú (Temporary Address)",
            "lbl_fac": "Khu vực nhà máy (Factory)",
            "lbl_dept": "Phòng ban (Department)",
            "lbl_title": "Chức vụ / Vị trí (Job Title)",
            "title_ph": "Ví dụ: Chủ tịch / Tổng Giám đốc / Kỹ sư...",
            "lbl_role": "Vai trò phân quyền hệ thống (System Role)",
            "lbl_phone": "Số điện thoại liên hệ",
            "phone_ph": "0912...",
            "lbl_insurance": "Số bảo hiểm xã hội (Insurance / BHXH)",
            "lbl_hospital": "Bệnh viện khám chữa bệnh BHYT (Hospital)",
            "btn_add": "🚀 Thêm nhân viên và tạo tài khoản",
            "success_add": "✅ Thêm nhân viên {name} thành công! Mật khẩu ban đầu đã được cấp.",
            "warn_name": "⚠️ Vui lòng nhập tên và mã nhân viên!",
            "edit_header": "### ✏️ Chỉnh sửa hồ sơ & Đặt lại mật khẩu",
            "select_edit": "Chọn nhân viên cần sửa",
            "btn_save_edit": "💾 Lưu thay đổi",
            "success_edit": "✅ Cập nhật thông tin nhân viên {id} thành công!",
            "no_emp_edit": "Hiện không có nhân viên nào để chỉnh sửa.",
            "del_header": "### 🗑️ Xóa trùng lặp hoặc Thủ tục nghỉ việc",
            "select_del": "Chọn nhân viên cần xử lý",
            "warn_del_title": "Bạn đang xử lý nhân viên:",
            "btn_del_hard": "🔥 Xóa hoàn toàn",
            "btn_del_resign": "🚪 Làm thủ tục nghỉ việc",
            "success_hard": "✅ Đã xóa hoàn toàn nhân viên {id}!",
            "success_resign": "🚪 Đã chuyển nhân viên {id} vào danh sách nghỉ việc!",
            "no_emp_del": "Hiện không có nhân viên nào để xử lý."
        },
        "English": {
            "title": "👤 Management Dept - HR & Employee Records",
            "info": "Manage employee profiles, initial passwords, insurance, and addresses.",
            "search_label": "🔍 Search Employee Name / ID / Title",
            "search_ph": "Enter keyword to search...",
            "list_title": "### 📋 Current Employee Directory",
            "resigned_title": "### 🚪 Resigned Employee Archive",
            "tabs": ["➕ Add Employee", "✏️ Edit Employee", "🗑️ Delete or Resign"],
            "add_header": "### ➕ Add New Employee & Initial Password",
            "lbl_id": "Employee ID (Username)",
            "lbl_name": "Employee Name",
            "lbl_pwd": "Initial Password",
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
            "success_add": "✅ Employee {name} added successfully! Must change password on first login.",
            "warn_name": "⚠️ Please enter employee name and ID!",
            "edit_header": "### ✏️ Edit Employee Profile & Password Reset",
            "select_edit": "Select Employee to Edit",
            "btn_save_edit": "💾 Save Changes",
            "success_edit": "✅ Employee {id} updated successfully!",
            "no_emp_edit": "No employee records available for editing.",
            "del_header": "### 🗑️ Delete Duplicate or Process Resignation",
            "select_del": "Select Employee to Process",
            "warn_del_title": "You are processing employee:",
            "btn_del_hard": "🔥 Completely Delete",
            "btn_del_resign": "🚪 Process Resignation",
            "success_hard": "✅ Employee {id} completely deleted!",
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
                "工號": "admin", "姓名": "系統管理員", "國籍": "台灣 (Taiwan)", "工作廠區": "台灣總部", "部門": "資訊管理部", "職稱": "Admin", "角色": "admin", "電話": "0912345678", 
                "密碼": "123", "must_change_password": False,
                "戶籍地址": "台北市...", "暫住地址": "台北市...", "保險資料": "TW-INS-01", "保險醫院": "台大醫院"
            },
            {
                "工號": "EMP-002", "姓名": "Nguyễn Văn A", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "總經理室", "職稱": "總經理 (General Manager)", "角色": "GeneralManager", "電話": "0918999080", 
                "密碼": "123456", "must_change_password": True,  # 👈 標記首次登入必須修改密碼
                "戶籍地址": "Tỉnh Tây Ninh", "暫住地址": "Khu công nghiệp", "保險資料": "VN-BHXH-01", "保險醫院": "Bệnh viện Tây Ninh"
            }
        ]

    if "resigned_employee_db" not in st.session_state:
        st.session_state.resigned_employee_db = []

    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)", "負責人與職位": "張董事長", "聯絡電話": "0912345678"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)", "負責人與職位": "阮文強", "聯絡電話": "0918999080"}
        ]

    search_q = st.text_input(L["search_label"], placeholder=L["search_ph"], key="emp_search_u")
    
    filtered_emp = [
        e for e in st.session_state.employee_db 
        if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower() or search_q.lower() in e["職稱"].lower()
    ] if search_q else st.session_state.employee_db

    st.markdown(L["list_title"])
    st.dataframe(pd.DataFrame([{k: v for k, v in e.items() if k != "密碼"} for e in filtered_emp]), use_container_width=True)

    tab_add, tab_edit, tab_del = st.tabs(L["tabs"])

    with tab_add:
        with st.form("add_employee_form_u"):
            st.markdown(L["add_header"])
            c1, c2 = st.columns(2)
            with c1:
                e_id = st.text_input(L["lbl_id"], value=f"EMP-{len(st.session_state.employee_db)+1:03d}")
                e_name = st.text_input(L["lbl_name"])
                e_pwd = st.text_input(L["lbl_pwd"], value="123456", type="password") # 預設初始密碼
                e_nat = st.selectbox(L["lbl_nat"], L["nat_opts"])
                e_perm_addr = st.text_input(L["lbl_perm"])
                e_temp_addr = st.text_input(L["lbl_temp"])
            with c2:
                fac_choices = [f"{fac['廠區名稱']}" for fac in st.session_state.factory_list]
                e_fac = st.selectbox(L["lbl_fac"], fac_choices)
                
                e_dept = st.selectbox(L["lbl_dept"], ["總經理室", "管理部", "工程與設計管理中心", "生產部"])
                e_title = st.text_input(L["lbl_title"], placeholder=L["title_ph"])
                e_role = st.selectbox(L["lbl_role"], ["admin", "Chairman", "GeneralManager", "ViceManager", "Manager", "Staff", "security"])

                e_phone = st.text_input(L["lbl_phone"], placeholder=L["phone_ph"])
                e_insurance = st.text_input(L["lbl_insurance"])
                e_hospital = st.text_input(L["lbl_hospital"])

            if st.form_submit_button(L["btn_add"], type="primary"):
                if e_name and e_id:
                    st.session_state.employee_db.append({
                        "工號": e_id,
                        "姓名": e_name,
                        "國籍": e_nat,
                        "工作廠區": e_fac,
                        "部門": e_dept,
                        "職稱": e_title,
                        "角色": e_role,
                        "電話": e_phone,
                        "密碼": e_pwd,
                        "must_change_password": True,  # 👈 關鍵：設定為首次登入必須改密碼
                        "戶籍地址": e_perm_addr,
                        "暫住地址": e_temp_addr,
                        "保險資料": e_insurance,
                        "保險醫院": e_hospital
                    })
                    st.success(L["success_add"].format(name=e_name))
                    st.rerun()
                else:
                    st.warning(L["warn_name"])

    with tab_edit:
        if st.session_state.employee_db:
            emp_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_emp_key = st.selectbox(L["select_edit"], list(emp_opts.keys()), key="edit_emp_sel_u")
            target_emp = emp_opts[sel_emp_key]

            with st.form("edit_employee_form_u"):
                st.markdown(L["edit_header"])
                ed_name = st.text_input(L["lbl_name"], value=target_emp["姓名"])
                ed_pwd = st.text_input("重設新密碼 (Reset Password)", value="", type="password", placeholder="若不修改請留空")
                ed_phone = st.text_input(L["lbl_phone"], value=target_emp["電話"])

                if st.form_submit_button(L["btn_save_edit"], type="primary"):
                    for e in st.session_state.employee_db:
                        if e["工號"] == target_emp["工號"]:
                            e["姓名"] = ed_name
                            e["電話"] = ed_phone
                            if ed_pwd:
                                e["密碼"] = ed_pwd
                                e["must_change_password"] = True  # 管理員重設後也須重新修改
                    st.success(L["success_edit"].format(id=target_emp["工號"]))
                    st.rerun()
        else:
            st.info(L["no_emp_edit"])

    with tab_del:
        if st.session_state.employee_db:
            del_opts = {f"{e['工號']} - {e['姓名']}": e for e in st.session_state.employee_db}
            sel_del_key = st.selectbox(L["select_del"], list(del_opts.keys()), key="del_emp_sel_u")
            target_del = del_opts[sel_del_key]

            with st.form("delete_employee_form_u"):
                st.markdown(L["del_header"])
                st.warning(f"{L['warn_del_title']} **{target_del['工號']} - {target_del['姓名']}**")
                
                c_d1, c_d2 = st.columns(2)
                if c_d1.form_submit_button(L["btn_del_hard"]):
                    st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_del["工號"]]
                    st.success(L["success_hard"].format(id=target_del['工號']))
                    st.rerun()
                if c_d2.form_submit_button(L["btn_del_resign"]):
                    resigned_record = target_del.copy()
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
