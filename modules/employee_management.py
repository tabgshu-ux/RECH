import streamlit as st
import pandas as pd

def render_employee_management(engine=None, t=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "👤 管理部 - 員工個人檔案與人事管理",
            "info": "在此維護全廠區員工個人檔案、合約記錄、工作廠區與人事資料（支援多國籍、雙地址與保險/薪資設定）。",
            "search": "🔍 搜尋員工姓名 / 工號 / 職稱",
            "search_ph": "輸入關鍵字搜尋員工...",
            "list_title": "### 📋 現有在職員工名冊",
            "tab_add": "➕ 新增員工",
            "tab_edit": "✏️ 修改員工資料",
            "tab_del": "🗑️ 刪除員工",
            "step1": "📌 步驟 1: 選擇員工國籍/廠區 (選擇後即時切換下方欄位)",
            "nat_label": "員工國籍 / 所屬廠區 *",
            "id_label": "員工工號 (Emp ID) *",
            "dept_label": "所屬部門",
            "phone_label": "聯絡電話 (Phone) *",
            "name_label": "員工全名 (Full Name) *",
            "title_label": "職位名稱",
            "role_label": "系統權限角色 (Role)",
            "perm_addr": "戶籍地址 (Permanent Address / Hộ khẩu) *",
            "temp_addr": "現居/暫住地址 (Current Address / Tạm trú) *",
            "step2": "📌 步驟 2: 輸入【VN 越南 (Vietnam)】專屬身分、起薪與法定保險資訊",
            "cccd_label": "身份證字號 (Số CCCD)",
            "salary_label": "約定起薪 / 保險起薪 (VND)",
            "hire_label": "入職/到職日期",
            "ins_label": "每月社醫保個人扣繳 (10.5% VND)",
            "hosp_label": "醫保指定醫院 (Bệnh viện)",
            "allow_label": "各類津貼總計 (VND)",
            "contract_label": "合約原署日期",
            "add_btn": "🚀 立即新增員工",
            # 修改與刪除專用多語言
            "select_edit_emp": "選擇要修改的員工",
            "edit_tab_title": "### ✏️ 修改員工檔案",
            "edit_id": "工號 (Emp ID)",
            "edit_name": "員工姓名 (Name)",
            "edit_title_label": "職稱 (Title)",
            "edit_phone": "電話 (Phone)",
            "edit_perm": "戶籍地址 (Permanent Address)",
            "edit_temp": "現居地址 (Current Address)",
            "save_btn": "💾 儲存修改",
            "del_tab_title": "### 🗑️ 刪除員工確認",
            "select_del_emp": "選擇要刪除的員工",
            "del_warn": "確定要將員工 **{id} - {name}** 自系統中刪除嗎？",
            "del_btn": "🔥 確認刪除"
        },
        "Tiếng Việt": {
            "title": "👤 Phòng Quản lý - Quản lý Nhân sự & Hồ sơ Nhân viên",
            "info": "Nơi quản lý hồ sơ nhân viên, hợp đồng, khu vực làm việc và dữ liệu nhân sự toàn nhà máy (Hỗ trợ đa quốc tịch, đa địa chỉ và bảo hiểm/lương).",
            "search": "🔍 Tìm kiếm nhân viên (Tên / Mã NV / Chức vụ)",
            "search_ph": "Nhập từ khóa tìm kiếm...",
            "list_title": "### 📋 Danh sách Nhân viên hiện tại",
            "tab_add": "➕ Thêm nhân viên",
            "tab_edit": "✏️ Sửa thông tin",
            "tab_del": "🗑️ Xóa nhân viên",
            "step1": "📌 Bước 1: Chọn Quốc tịch nhân viên / Khu vực làm việc",
            "nat_label": "Quốc tịch / Khu vực *",
            "id_label": "Mã nhân viên (Emp ID) *",
            "dept_label": "Phòng ban",
            "phone_label": "Số điện thoại (Phone) *",
            "name_label": "Họ và tên (Full Name) *",
            "title_label": "Chức vụ",
            "role_label": "Vai trò hệ thống (Role)",
            "perm_addr": "Hộ khẩu thường trú (Permanent Address) *",
            "temp_addr": "Chỗ ở hiện tại / Tạm trú (Current Address) *",
            "step2": "📌 Bước 2: Nhập Thông tin CCCD, Lương & Bảo hiểm bắt buộc cho nhân viên VN",
            "cccd_label": "Số CCCD",
            "salary_label": "Lương thỏa thuận / Lương đóng bảo hiểm (VND)",
            "hire_label": "Ngày vào làm",
            "ins_label": "Bảo hiểm xã hội/y tế cá nhân đóng (10.5% VND)",
            "hosp_label": "Bệnh viện KCB ban đầu (Bệnh viện)",
            "allow_label": "Tổng phụ cấp (VND)",
            "contract_label": "Ngày ký hợp đồng",
            "add_btn": "🚀 Thêm nhân viên mới",
            # Sửa & Xóa
            "select_edit_emp": "Chọn nhân viên cần chỉnh sửa",
            "edit_tab_title": "### ✏️ Chỉnh sửa hồ sơ nhân viên",
            "edit_id": "Mã nhân viên (Emp ID)",
            "edit_name": "Họ tên nhân viên (Name)",
            "edit_title_label": "Chức vụ (Title)",
            "edit_phone": "Số điện thoại (Phone)",
            "edit_perm": "Hộ khẩu thường trú (Permanent Address)",
            "edit_temp": "Chỗ ở hiện tại (Current Address)",
            "save_btn": "💾 Lưu thay đổi",
            "del_tab_title": "### 🗑️ Xác nhận xóa nhân viên",
            "select_del_emp": "Chọn nhân viên cần xóa",
            "del_warn": "Bạn có chắc chắn muốn xóa nhân viên **{id} - {name}** khỏi hệ thống không?",
            "del_btn": "🔥 Xác nhận xóa"
        },
        "English": {
            "title": "👤 Management Dept - HR & Employee Records",
            "info": "Manage employee profiles, contracts, work factories, and personnel records (Supports multi-nationality, dual addresses, and insurance/salary settings).",
            "search": "🔍 Search Employee (Name / ID / Title)",
            "search_ph": "Enter keyword to search...",
            "list_title": "### 📋 Current Employee Directory",
            "tab_add": "➕ Add Employee",
            "tab_edit": "✏️ Edit Employee",
            "tab_del": "🗑️ Delete Employee",
            "step1": "📌 Step 1: Select Employee Nationality & Factory",
            "nat_label": "Nationality / Factory *",
            "id_label": "Employee ID *",
            "dept_label": "Department",
            "phone_label": "Phone Number *",
            "name_label": "Full Name *",
            "title_label": "Job Title",
            "role_label": "System Role",
            "perm_addr": "Permanent Address (Hộ khẩu) *",
            "temp_addr": "Current / Temporary Address *",
            "step2": "📌 Step 2: Enter VN National ID, Salary & Statutory Insurance Info",
            "cccd_label": "Citizen ID (CCCD)",
            "salary_label": "Base Salary / Insurance Salary (VND)",
            "hire_label": "Hire Date",
            "ins_label": "Monthly Personal Insurance Contribution (10.5% VND)",
            "hosp_label": "Insurance Hospital",
            "allow_label": "Total Allowances (VND)",
            "contract_label": "Contract Date",
            "add_btn": "🚀 Add Employee",
            # Edit & Delete
            "select_edit_emp": "Select employee to edit",
            "edit_tab_title": "### ✏️ Edit Employee Profile",
            "edit_id": "Employee ID",
            "edit_name": "Employee Name",
            "edit_title_label": "Job Title",
            "edit_phone": "Phone Number",
            "edit_perm": "Permanent Address",
            "edit_temp": "Current Address",
            "save_btn": "💾 Save Changes",
            "del_tab_title": "### 🗑️ Confirm Employee Deletion",
            "select_del_emp": "Select employee to delete",
            "del_warn": "Are you sure you want to delete employee **{id} - {name}** from the system?",
            "del_btn": "🔥 Confirm Delete"
        }
    }

    t_set = texts.get(lang, texts["繁體中文"])

    st.title(t_set["title"])
    st.info(t_set["info"])

    if "employee_db" not in st.session_state:
        st.session_state.employee_db = [
            {
                "工號": "EMP-001", "姓名": "張董事長", "國籍": "台灣 (Taiwan)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "管理部", "職稱": "董事長 (Chairman)", "角色": "admin", "電話": "0912345678", 
                "戶籍地址": "台北市信義區...", "現居地址": "台北市信義區...", "保險資料": "TW-INS-888899", "保險醫院": "台北榮民總醫院", "生物辨識代碼": "FACE-BIO-888899"
            },
            {
                "工號": "VN-003", "姓名": "張小華", "國籍": "越南 (Vietnam)", "工作廠區": "西寧廠 (Tay Ninh)", "部門": "生產部", "職稱": "射出工程師", "角色": "staff", "電話": "0912345678", 
                "戶籍地址": "Tỉnh Tây Ninh, Huyện Trảng Bàng", "現居地址": "台北市信義區忠孝東路", "身分證字號": "038095009999", "入職日期": "2026/10/07", "醫保指定醫院": "Bệnh viện Quốc tế Hạnh Phúc", "合約原署日期": "2026/10/07", "約定起薪": "9000000.00", "每月社醫保扣繳": "945000.00", "津貼總計": "1530000.00", "生物辨識代碼": "FACE-BIO-100234"
            }
        ]

    search_q = st.text_input(t_set["search"], placeholder=t_set["search_ph"], key="emp_search_input")
    filtered_emp = [
        e for e in st.session_state.employee_db 
        if search_q.lower() in e["姓名"].lower() or search_q.lower() in e["工號"].lower() or search_q.lower() in e["職稱"].lower()
    ] if search_q else st.session_state.employee_db

    st.markdown(t_set["list_title"])
    st.dataframe(pd.DataFrame(filtered_emp), use_container_width=True)

    tab_add, tab_edit, tab_del = st.tabs([t_set["tab_add"], t_set["tab_edit"], t_set["tab_del"]])

    with tab_add:
        with st.form("add_employee_form"):
            st.markdown(f"### {t_set['step1']}")
            nat_choice = st.selectbox(t_set["nat_label"], ["越南 (Vietnam)", "台灣 (Taiwan)", "中國 (China)", "其他 (Other)"], key="add_nat_choice")
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                prefix = "VN" if "越南" in nat_choice else ("TW" if "台灣" in nat_choice else ("CN" if "中國" in nat_choice else "OT"))
                e_id = st.text_input(t_set["id_label"], value=f"{prefix}-{len(st.session_state.employee_db)+1:03d}", key="add_e_id")
                
                if lang == "Tiếng Việt":
                    dept_display_map = {
                        "總經理室": "Ban Giám đốc (Executive Office)",
                        "管理部": "Phòng Quản lý (Management Dept)",
                        "工程與設計管理中心": "Trung tâm Kỹ thuật & Thiết kế",
                        "生產部": "Phòng Sản xuất (Production Dept)"
                    }
                elif lang == "English":
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
                e_dept_sel = st.selectbox(t_set["dept_label"], dept_keys, format_func=lambda x: dept_display_map[x], key="add_e_dept")
                e_dept = e_dept_sel

                e_phone = st.text_input(t_set["phone_label"], placeholder="0912345678", key="add_e_phone")
            with c2:
                e_name = st.text_input(t_set["name_label"], placeholder="請輸入姓名 / Nhập họ tên...", key="add_e_name")
                e_title = st.text_input(t_set["title_label"], placeholder="例如: 射出工程師 / Kỹ sư", key="add_e_title")

                if lang == "Tiếng Việt":
                    role_display_map = {
                        "staff": "Nhân viên chung (Staff)",
                        "manager": "Quản lý / Chủ quản (Manager)",
                        "security": "Bảo vệ (Security)",
                        "admin": "Quản trị hệ thống (Admin)"
                    }
                elif lang == "English":
                    role_display_map = {
                        "staff": "General Staff",
                        "manager": "Department Manager",
                        "security": "Security Guard",
                        "admin": "System Administrator"
                    }
                else:
                    role_display_map = {
                        "staff": "一般員工 (Staff)",
                        "manager": "部門主管 (Manager)",
                        "security": "保全 (Security)",
                        "admin": "系統管理員 (Admin)"
                    }
                role_keys = list(role_display_map.keys())
                e_role_sel = st.selectbox(t_set["role_label"], role_keys, format_func=lambda x: role_display_map[x], key="add_e_role")
                e_role = e_role_sel

            ac1, ac2 = st.columns(2)
            with ac1:
                e_perm_addr = st.text_input(t_set["perm_addr"], placeholder="請輸入戶籍地址...", key="add_e_perm_addr")
            with ac2:
                e_temp_addr = st.text_input(t_set["temp_addr"], placeholder="請輸入目前居住地址...", key"add_e_temp_addr")
                
