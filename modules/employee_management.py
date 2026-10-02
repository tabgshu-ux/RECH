import pandas as pd
import streamlit as st

# 🌐 人事管理多語系字典 (i18n)
EMP_I18N = {
    "繁體中文": {
        "page_title": "👥 跨國員工檔案與人事管理",
        "tab_profiles": "👤 跨國員工檔案管理",
        "tab_leave": "🌴 請假系統",
        "tab_permissions": "🔑 權限系統後台",
        "tab_dept_setting": "🏢 部門組織與職位維護 (新增/編輯/刪除)",
        "expander_add_emp": "➕ 新增跨國員工/高管個人檔案",
        "step_1": "📍 步驟 1：選擇員工國籍、廠區與部門職位",
        "lbl_nationality": "員工國籍 (Nationality) *",
        "lbl_site": "派駐工作廠區 (Work Plant) *",
        "lbl_dept": "所屬部門/單位 *",
        "lbl_name": "員工全名 *",
        "lbl_job_title": "職位/頭銜 (Job Title) *",
        "lbl_role": "系統權限角色 (Role)",
        "lbl_phone": "聯絡電話 (Phone) *",
        "lbl_address": "居住/戶籍地址 (Address) *",
        "lbl_passport": "護照號碼 / 身份證字號",
        "lbl_work_permit": "工作許可證 / 勞工證號",
        "btn_save_emp": "💾 儲存個人檔案",
        "msg_emp_added": "✅ 已成功新增人員檔案！",
        "table_title": "📋 公司現有員工與高管名冊 (可依廠區/部門篩選)",
        "filter_site": "🔍 依廠區篩選：",
        "filter_dept": "🔍 依部門篩選：",
        "dept_mgr_title": "⚙️ 企業部門組織動態管理 (自由新增/修改/刪除)",
        "dept_mgr_caption": "您在此新增、修改或刪除的部門，將會即時同步至全系統的下拉選單中。",
        "section_add": "➕ 新增新部門",
        "section_edit": "✏️ 修改現有部門名稱",
        "section_delete": "🗑️ 刪除廢止部門",
        "lbl_select_edit_dept": "請選擇欲修改的部門：",
        "lbl_select_del_dept": "請選擇欲刪除的部門：",
        "lbl_new_dept_zh": "部門名稱 (中文)",
        "lbl_new_dept_vn": "部門名稱 (越南文 Tiếng Việt)",
        "lbl_new_dept_en": "部門名稱 (英文 English)",
        "btn_add_dept": "➕ 確定新增部門",
        "btn_update_dept": "💾 儲存修改內容",
        "btn_delete_dept": "🗑️ 確定刪除此部門",
        "msg_dept_added": "✅ 已成功新增部門！",
        "msg_dept_updated": "✅ 已順利更新部門名稱！",
        "msg_dept_deleted": "🗑️️ 已成功刪除該部門！",
        "exist_depts": "📌 目前系統完整部門清單 (可直接在表格內雙擊修改，或最下方新增列)",
        "btn_save_table": "💾 儲存表格修改結果",
    },
    "Tiếng Việt": {
        "page_title": "👥 Quản lý Hồ sơ Nhân sự & Nhân viên Đa quốc gia",
        "tab_profiles": "👤 Hồ sơ Nhân viên & Lãnh đạo",
        "tab_leave": "🌴 Hệ thống Nghỉ phép",
        "tab_permissions": "🔑 Phân quyền Hệ thống",
        "tab_dept_setting": "🏢 Quản lý Cấu hình Phòng ban (Thêm/Sửa/Xóa)",
        "expander_add_emp": "➕ Thêm Hồ sơ Nhân viên / Quản lý Mới",
        "step_1": "📍 Bước 1: Chọn Quốc tịch, Nhà máy, Phòng ban & Chức danh",
        "lbl_nationality": "Quốc tịch Nhân viên (Nationality) *",
        "lbl_site": "Nhà máy làm việc trực thuộc (Work Plant) *",
        "lbl_dept": "Phòng ban / Bộ phận trực thuộc *",
        "lbl_name": "Họ và tên *",
        "lbl_job_title": "Chức danh / Vị trí (Job Title) *",
        "lbl_role": "Vai trò Phân quyền (Role)",
        "lbl_phone": "Số điện thoại liên hệ *",
        "lbl_address": "Địa chỉ thường trú / Tạm trú *",
        "lbl_passport": "Số Hộ chiếu / CMND / CCCD",
        "lbl_work_permit": "Số Giấy phép Lao động (Work Permit)",
        "btn_save_emp": "💾 Lưu Hồ sơ",
        "msg_emp_added": "✅ Đã thêm hồ sơ thành công!",
        "table_title": "📋 Danh sách Nhân viên & Ban Quản lý (Lọc theo Nhà máy/Phòng ban)",
        "filter_site": "🔍 Lọc theo Nhà máy:",
        "filter_dept": "🔍 Lọc theo Phòng ban:",
        "dept_mgr_title": "⚙️ Quản lý Động Cơ cấu Tổ chức Phòng ban",
        "dept_mgr_caption": "Các thay đổi (Thêm/Sửa/Xóa) phòng ban tại đây sẽ tự động đồng bộ vào tất cả các menu chọn trong hệ thống.",
        "section_add": "➕ Thêm Phòng ban Mới",
        "section_edit": "✏️ Chỉnh sửa Tên Phòng ban Hiện có",
        "section_delete": "🗑️ Xóa Phòng ban",
        "lbl_select_edit_dept": "Chọn phòng ban cần chỉnh sửa:",
        "lbl_select_del_dept": "Chọn phòng ban cần xóa:",
        "lbl_new_dept_zh": "Tên phòng ban (Tiếng Trung)",
        "lbl_new_dept_vn": "Tên phòng ban (Tiếng Việt)",
        "lbl_new_dept_en": "Tên phòng ban (Tiếng Anh)",
        "btn_add_dept": "➕ Xác nhận Thêm Phòng ban",
        "btn_update_dept": "💾 Lưu Thay đổi",
        "btn_delete_dept": "🗑️ Xóa Phòng ban này",
        "msg_dept_added": "✅ Đã thêm phòng ban mới thành công!",
        "msg_dept_updated": "✅ Đã cập nhật tên phòng ban thành công!",
        "msg_dept_deleted": "🗑️ Đã xóa phòng ban thành công!",
        "exist_depts": "📌 Danh sách Phòng ban Hiện có (Có thể nhấp đúp trực tiếp vào bảng để sửa)",
        "btn_save_table": "💾 Lưu Kết quả Sửa Bảng",
    },
    "English": {
        "page_title": "👥 Global Employee Profiles & HR Management",
        "tab_profiles": "👤 Employee & Executive Profiles",
        "tab_leave": "🌴 Leave System",
        "tab_permissions": "🔑 Permissions Management",
        "tab_dept_setting": "🏢 Department Settings (Add/Edit/Delete)",
        "expander_add_emp": "➕ Add New Employee / Executive Profile",
        "step_1": "📍 Step 1: Select Nationality, Work Plant, Department & Job Title",
        "lbl_nationality": "Nationality *",
        "lbl_site": "Work Plant Location *",
        "lbl_dept": "Department / Unit *",
        "lbl_name": "Full Name *",
        "lbl_job_title": "Job Title *",
        "lbl_role": "System Permission Role",
        "lbl_phone": "Contact Phone *",
        "lbl_address": "Residential / Permanent Address *",
        "lbl_passport": "Passport / National ID No.",
        "lbl_work_permit": "Work Permit No.",
        "btn_save_emp": "💾 Save Profile",
        "msg_emp_added": "✅ Profile added successfully!",
        "table_title": "📋 Existing Employee List (Filterable by Plant & Dept)",
        "filter_site": "🔍 Filter by Plant:",
        "filter_dept": "🔍 Filter by Dept:",
        "dept_mgr_title": "⚙️ Dynamic Department Management (Full CRUD)",
        "dept_mgr_caption": "Any additions, edits, or deletions here will immediately update all system dropdowns.",
        "section_add": "➕ Add New Department",
        "section_edit": "✏️ Edit Existing Department",
        "section_delete": "🗑 Delete Department",
        "lbl_select_edit_dept": "Select department to edit:",
        "lbl_select_del_dept": "Select department to delete:",
        "lbl_new_dept_zh": "Department Name (Chinese)",
        "lbl_new_dept_vn": "Department Name (Vietnamese)",
        "lbl_new_dept_en": "Department Name (English)",
        "btn_add_dept": "➕ Confirm Add Department",
        "btn_update_dept": "💾 Save Changes",
        "btn_delete_dept": "🗑️ Confirm Delete",
        "msg_dept_added": "✅ New department added successfully!",
        "msg_dept_updated": "✅ Department updated successfully!",
        "msg_dept_deleted": "🗑️ Department deleted successfully!",
        "exist_depts": "📌 Current Department List (Double click cells to edit directly)",
        "btn_save_table": "💾 Save Table Edits",
    },
}

# 👑 標準高管與員工職位選單 (Job Titles i18n)
JOB_TITLES_DICT = {
    "繁體中文": [
        "董事長 (Chairman)",
        "總經理 (General Manager / CEO)",
        "副總經理 (Vice General Manager / Vice President)",
        "廠長 (Plant Manager)",
        "副廠長 (Vice Plant Manager)",
        "經理 (Manager)",
        "副理 (Deputy Manager)",
        "課長 / 主管 (Supervisor)",
        "組長 (Team Leader)",
        "高級工程師 (Senior Engineer)",
        "工程師 (Engineer)",
        "專員 / 助理 (Specialist / Assistant)",
        "現場技術員 (Technician)",
        "✏️ 手動輸入其他職位...",
    ],
    "Tiếng Việt": [
        "Chủ tịch HĐQT (Chairman)",
        "Tổng Giám đốc (General Manager / CEO)",
        "Phó Tổng Giám đốc (Vice General Manager)",
        "Giám đốc Nhà máy (Plant Manager)",
        "Phó Giám đốc Nhà máy (Vice Plant Manager)",
        "Trưởng phòng (Manager)",
        "Phó phòng (Deputy Manager)",
        "Quản lý / Trưởng bộ phận (Supervisor)",
        "Tổ trưởng (Team Leader)",
        "Kỹ sư cao cấp (Senior Engineer)",
        "Kỹ sư (Engineer)",
        "Chuyên viên / Trợ lý (Specialist / Assistant)",
        "Kỹ thuật viên xưởng (Technician)",
        "✏️ Nhập chức danh khác...",
    ],
    "English": [
        "Chairman",
        "General Manager / CEO",
        "Vice General Manager / Vice President",
        "Plant Manager",
        "Vice Plant Manager",
        "Manager",
        "Deputy Manager",
        "Supervisor",
        "Team Leader",
        "Senior Engineer",
        "Engineer",
        "Specialist / Assistant",
        "Technician",
        "✏️ Enter custom title...",
    ],
}

NATIONALITY_OPTIONS = [
    "🇹🇼 台灣籍 (Taiwanese)",
    "🇻🇳 越南籍 (Vietnamese)",
    "🇨🇳 中國籍 (Chinese)",
    "🌐 其他國籍 (Other)"
]


def get_dynamic_site_options():
    """🔗 動態取得與資訊管理部 (IT) 連動的廠區選項"""
    if "factory_list" in st.session_state and st.session_state.factory_list:
        sites = []
        for fact in st.session_state.factory_list:
            if isinstance(fact, dict):
                f_name = fact.get("name", str(fact))
            else:
                f_name = str(fact)
            sites.append(f_name)
        return sites
    else:
        return [
            "🇻🇳 越南西寧廠 (Tay Ninh Plant)",
            "🇻🇳 越南海防廠 (Hai Phong Plant)",
            "🇹🇼 台灣總部 (Taiwan HQ)",
        ]


def render_employee_management(*args, **kwargs):
    lang = (
        kwargs.get("lang")
        or kwargs.get("curr_lang")
        or st.session_state.get("current_lang", "繁體中文")
    )
    L = EMP_I18N.get(lang, EMP_I18N["繁體中文"])
    job_titles = JOB_TITLES_DICT.get(lang, JOB_TITLES_DICT["繁體中文"])

    st.title(L["page_title"])

    # 初始化預設自訂部門
    if "custom_departments" not in st.session_state:
        st.session_state.custom_departments = [
            {"zh": "經營高層 / 董事會 (Executive)", "vn": "Ban Giám đốc / HĐQT", "en": "Executive Board"},
            {"zh": "生產部", "vn": "Bộ phận sản xuất", "en": "Production Department"},
            {"zh": "工程部", "vn": "Bộ phận kỹ thuật", "en": "Engineering Department"},
            {"zh": "總務行政部 (GA)", "vn": "Phòng Hành chính Hậu cần (GA)", "en": "General Affairs (GA)"},
            {"zh": "財務部 (Finance)", "vn": "Phòng Tài chính (Finance)", "en": "Finance Dept"},
            {"zh": "研發部 (R&D)", "vn": "Phòng Nghiên cứu & Phát triển (R&D)", "en": "R&D Dept"},
            {"zh": "配電盤組裝課", "vn": "Tổ Lắp ráp Tủ điện", "en": "Switchgear Assembly Dept"},
            {"zh": "板金加工課", "vn": "Tổ Gia công Cơ khí", "en": "Sheet Metal Dept"},
            {"zh": "烤漆塗裝課", "vn": "Tổ Sơn tĩnh điện", "en": "Powder Coating Dept"},
        ]

    if lang == "Tiếng Việt":
        dept_options = [d["vn"] for d in st.session_state.custom_departments]
    elif lang == "English":
        dept_options = [d["en"] for d in st.session_state.custom_departments]
    else:
        dept_options = [d["zh"] for d in st.session_state.custom_departments]

    # 🔗 動態獲取 IT 設定的廠區選項
    site_options = get_dynamic_site_options()

    # 初始化員工名冊 (增加 nationality 欄位)
    if "employees_db" not in st.session_state:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張董事長",
                "nationality": "🇹🇼 台灣籍 (Taiwanese)",
                "site": site_options[2] if len(site_options) > 2 else site_options[0],
                "dept": dept_options[0],
                "title": "董事長 (Chairman)",
                "phone": "0912345678",
            },
            {
                "id": "EMP-002",
                "name": "Nguyễn Văn A",
                "nationality": "🇻🇳 越南籍 (Vietnamese)",
                "site": site_options[0],
                "dept": dept_options[2] if len(dept_options) > 2 else dept_options[0],
                "title": "Kỹ sư Tủ điện",
                "phone": "0987654321",
            },
        ]

    tab1, tab2, tab3, tab4 = st.tabs([
        L["tab_profiles"],
        L["tab_leave"],
        L["tab_permissions"],
        L["tab_dept_setting"],
    ])

    # ----------------------------------------------------
    # 頁籤 1：跨國員工與高管檔案管理
    # ----------------------------------------------------
    with tab1:
        with st.expander(L["expander_add_emp"], expanded=True):
            st.markdown(f"#### {L['step_1']}")
            
            # 💡 國籍與派駐廠區完全獨立分開
            c_nat, c_site, c_dept = st.columns(3)
            nationality = c_nat.selectbox(L["lbl_nationality"], NATIONALITY_OPTIONS)
            site = c_site.selectbox(L["lbl_site"], site_options)
            dept = c_dept.selectbox(L["lbl_dept"], dept_options)

            c3, c4, c5 = st.columns(3)
            name = c3.text_input(L["lbl_name"], value="")

            selected_title_opt = c4.selectbox(L["lbl_job_title"], job_titles)
            if "✏️" in selected_title_opt:
                final_job_title = c4.text_input("請輸入自訂職位名稱", value="")
            else:
                final_job_title = selected_title_opt

            role = c5.selectbox(
                L["lbl_role"],
                ["Admin (系統管理者)", "Manager (主管)", "User (一般員工)"],
            )

            c6, c7 = st.columns(2)
            phone = c6.text_input(L["lbl_phone"], value="")
            address = c7.text_input(L["lbl_address"], value="")

            c8, c9 = st.columns(2)
            passport = c8.text_input(L["lbl_passport"], value="")
            work_permit = c9.text_input(L["lbl_work_permit"], value="")

            if st.button(L["btn_save_emp"], type="primary"):
                if name and final_job_title:
                    st.session_state.employees_db.append({
                        "id": f"EMP-00{len(st.session_state.employees_db)+1}",
                        "name": name,
                        "nationality": nationality,
                        "site": site,
                        "dept": dept,
                        "title": final_job_title,
                        "phone": phone,
                        "passport": passport,
                        "permit": work_permit,
                    })
                    st.success(L["msg_emp_added"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入全名與職位名稱！")

        st.markdown(f"### {L['table_title']}")

        # 🔍 增加多維度篩選器 (依廠區、依部門篩選)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_site_opt = st.selectbox(L["filter_site"], ["全部廠區 (All Sites)"] + site_options)
        with col_f2:
            filter_dept_opt = st.selectbox(L["filter_dept"], ["全部部門 (All Depts)"] + dept_options)

        # 執行篩選邏輯
        filtered_emps = st.session_state.employees_db
        if filter_site_opt != "全部廠區 (All Sites)":
            filtered_emps = [e for e in filtered_emps if e.get("site") == filter_site_opt]
        if filter_dept_opt != "全部部門 (All Depts)":
            filtered_emps = [e for e in filtered_emps if e.get("dept") == filter_dept_opt]

        st.dataframe(pd.DataFrame(filtered_emps), use_container_width=True)

    with tab2:
        st.info("🌴 請假審核與假勤管理模組運作中。")

    with tab3:
        st.info("🔑 RBAC 權限矩陣控制台運作中。")

    # ----------------------------------------------------
    # 頁籤 4：部門組織動態維護
    # ----------------------------------------------------
    with tab4:
        st.markdown(f"### {L['dept_mgr_title']}")
        st.caption(L["dept_mgr_caption"])

        with st.expander(L["section_add"], expanded=True):
            col_add1, col_add2, col_add3 = st.columns(3)
            add_zh = col_add1.text_input(L["lbl_new_dept_zh"], key="add_dept_zh")
            add_vn = col_add2.text_input(L["lbl_new_dept_vn"], key="add_dept_vn")
            add_en = col_add3.text_input(L["lbl_new_dept_en"], key="add_dept_en")

            if st.button(L["btn_add_dept"], type="primary"):
                if add_zh and add_vn:
                    st.session_state.custom_departments.append({
                        "zh": add_zh, "vn": add_vn, "en": add_en or add_zh
                    })
                    st.success(L["msg_dept_added"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入中文與越南文部門名稱！")

        st.divider()

        st.markdown(f"#### {L['exist_depts']}")
        df_depts = pd.DataFrame(st.session_state.custom_departments)
        edited_df = st.data_editor(df_depts, use_container_width=True, num_rows="dynamic", key="dept_editor")

        if st.button(L["btn_save_table"]):
            st.session_state.custom_departments = edited_df.to_dict("records")
            st.success(L["msg_dept_updated"])
            st.rerun()


def show(*args, **kwargs):
    render_employee_management(*args, **kwargs)


def main(*args, **kwargs):
    render_employee_management(*args, **kwargs)
