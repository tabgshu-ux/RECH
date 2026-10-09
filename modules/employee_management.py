import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 員工與人事管理模組多語系字典 (i18n)
# ----------------------------------------------------
EMP_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工個人檔案與人事管理中心",
        "caption": "管理全公司在職員工名冊、離職歷史檔案、越南勞動法合規與外籍幹部護照/暫住證證件管理。",
        "tab_add_vn": "🇻🇳 新增越南員工",
        "tab_add_foreign": "🇹🇼🇨🇳 新增外派員工",
        "tab_edit": "✏️ 修改員工資料",
        "tab_list": "👥 現職員工名冊",
        "tab_delete": "🗑️ 員工離職及刪除",
        "tab_resigned": "📂 離職名冊",
        "header_add_vn": "🇻🇳 新增越南本地員工個人檔案與社會保險設定",
        "header_add_foreign": "🇹🇼🇨🇳 新增台灣籍與中國籍外派幹部護照及暫住證檔案",
        "header_edit": "✏️ 員工資料修改與精準廠區/身份快速過濾",
        "header_list": "📋 全公司現職員工名冊與廠區分流總覽",
        "header_delete": "🗑️ 辦理離職歸檔或徹底刪除重複帳號",
        "header_resigned": "📂 離職歷史人員名冊與廠區分流復職管理",
        "lbl_code": "員工工號 (登入帳號) *",
        "lbl_name": "員工姓名 (Employee Name) *",
        "lbl_phone": "聯絡電話 (Phone No.) *",
        "lbl_id_card": "公民身分證號 (CCCD / 12碼) *",
        "lbl_passport": "護照號碼 (Passport No.) *",
        "lbl_trc": "暫住證號 (TRC / Giấy tạm trú) *",
        "lbl_bhxh": "社會保險證號 (Mã số BHXH)",
        "lbl_hospital": "投保指定醫療院所 (Bệnh viện KCB BHYT)",
        "lbl_factory": "工作廠區 (Factory) *",
        "factory_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
        "factory_filter_opts": ["全部廠區 (All Plants)", "西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
        "identity_filter_opts": ["全部身份 (All)", "越南員工 (Local VN)", "外派幹部 (TW/CN)"],
        "lbl_dept": "部門 *",
        "dept_opts": ["總經理室", "管理部", "工程部", "生產部", "資訊部"],
        "lbl_pwd": "初始登入密碼 (預設) *",
        "lbl_title": "職稱 / 職務 *",
        "lbl_attendance": "出勤性質歸屬 (Attendance Type) *",
        "attendance_opts": ["廠內固定員工 (Plant Fixed Staff)", "外勤工程師 (Field Engineer)"],
        "lbl_country": "國籍 (Nationality) *",
        "country_opts": ["越南 (Vietnam)", "台灣 (Taiwan)", "中國 (China)"],
        "lbl_role": "系統權限角色 *",
        "lbl_addr_perm": "戶籍地址 / 原籍地址",
        "lbl_addr_temp": "越南現住地址 (Temporary Address)",
        "btn_add": "🚀 立即新增員工並建立檔案",
        "btn_update": "💾 儲存修改後員工資料",
        "btn_archive": "📂 將此員工辦理離職歸檔",
        "btn_reactivate": "🔄 辦理回鍋復職 (Reactivate)",
        "btn_hard_delete": "🔥 徹底刪除帳號 (僅適用於重複建檔錯誤)",
        "search_ph": "🔍 搜尋員工姓名、工號或證件號...",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_phone": "電話",
        "col_id_doc": "身分證 / 護照與暫住證",
        "col_factory": "廠區",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_attendance": "出勤性質",
        "col_role": "系統角色",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Nhân sự & Hồ sơ Nhân viên",
        "caption": "Quản lý nhân viên, hộ chiếu, thẻ tạm trú và phân quyền.",
        "tab_add_vn": "🇻🇳 Thêm NV Việt Nam",
        "tab_add_foreign": "🇹🇼🇨🇳 Thêm Cán bộ Nước ngoài",
        "tab_edit": "✏️ Sửa Thông tin",
        "tab_list": "👥 Nhân viên hiện tại",
        "tab_delete": "🗑️ Xử lý Nghỉ việc & Xóa",
        "tab_resigned": "📂 Lịch sử Nghỉ việc",
        "header_add_vn": "🇻🇳 Thêm hồ sơ nhân viên Việt Nam (BHXH & CCCD)",
        "header_add_foreign": "🇹🇼🇨🇳 Thêm hồ sơ Cán bộ Nước ngoài (Hộ chiếu & Thẻ tạm trú)",
        "header_edit": "✏️ Cập nhật thông tin nhân viên",
        "header_list": "📋 Danh sách nhân viên đang làm việc theo nhà máy",
        "header_delete": "🗑️ Xử lý nghỉ việc hoặc Xóa vĩnh viễn",
        "header_resigned": "📂 Hồ sơ nhân viên đã nghỉ việc theo nhà máy",
        "lbl_code": "Mã nhân viên *",
        "lbl_name": "Họ tên nhân viên *",
        "lbl_phone": "Số điện thoại *",
        "lbl_id_card": "Số CCCD *",
        "lbl_passport": "Số Hộ chiếu (Passport) *",
        "lbl_trc": "Số Thẻ tạm trú (TRC) *",
        "lbl_bhxh": "Mã số BHXH",
        "lbl_hospital": "Bệnh viện KCB BHYT",
        "lbl_factory": "Nhà máy *",
        "factory_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "factory_filter_opts": ["Tất cả nhà máy", "Nhà máy Tây Ninh", "Nhà máy Hải Phòng"],
        "identity_filter_opts": ["Tất cả", "Nhân viên VN", "Cán bộ Nước ngoài"],
        "lbl_dept": "Phòng ban *",
        "dept_opts": ["Ban Giám đốc", "Phòng Quản lý", "Phòng Kỹ thuật", "Phòng Sản xuất", "Phòng IT"],
        "lbl_pwd": "Mật khẩu ban đầu *",
        "lbl_title": "Chức vụ *",
        "lbl_attendance": "Tính chất chấm công *",
        "attendance_opts": ["Nhân viên làm việc tại nhà máy", "Kỹ sư hiện trường (Field Engineer)"],
        "lbl_country": "Quốc tịch *",
        "country_opts": ["Việt Nam", "Đài Loan", "Trung Quốc"],
        "lbl_role": "Vai trò hệ thống *",
        "lbl_addr_perm": "Địa chỉ thường trú",
        "lbl_addr_temp": "Chỗ ở hiện tại tại VN",
        "btn_add": "🚀 Thêm nhân viên mới",
        "btn_update": "💾 Lưu thay đổi",
        "btn_archive": "📂 Lưu trữ nghỉ việc",
        "btn_reactivate": "🔄 Tái tuyển dụng",
        "btn_hard_delete": "🔥 Xóa vĩnh viễn",
        "search_ph": "🔍 Tìm kiếm...",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_phone": "Điện thoại",
        "col_id_doc": "CCCD / Hộ chiếu",
        "col_factory": "Nhà máy",
        "col_dept": "Phòng ban",
        "col_title": "Chức vụ",
        "col_attendance": "Chấm công",
        "col_role": "Vai trò",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "👤 Management - Employee Profile & HR Center",
        "caption": "Manage active employees, passports, TRC cards, and roles.",
        "tab_add_vn": "🇻🇳 Add VN Employee",
        "tab_add_foreign": "🇹🇼🇨🇳 Add Foreign Staff",
        "tab_edit": "✏️ Edit Profile",
        "tab_list": "👥 Active Employees",
        "tab_delete": "🗑️ Archive / Delete",
        "tab_resigned": "📂 Resigned Archives",
        "header_add_vn": "🇻🇳 Add Vietnamese Employee Profile",
        "header_add_foreign": "🇹🇼🇨🇳 Add Foreign Staff Profile (Passport & TRC)",
        "header_edit": "✏️ Update Employee Info",
        "header_list": "📋 Active Employee Directory by Plant",
        "header_delete": "🗑️ Archive Resigned or Delete Duplicates",
        "header_resigned": "📂 Resigned Employee History by Plant",
        "lbl_code": "Employee ID *",
        "lbl_name": "Employee Name *",
        "lbl_phone": "Phone Number *",
        "lbl_id_card": "ID Card / CCCD *",
        "lbl_passport": "Passport No. *",
        "lbl_trc": "Temporary Residence Card (TRC) No. *",
        "lbl_bhxh": "Social Insurance (BHXH) No.",
        "lbl_hospital": "Medical Insurance Hospital",
        "lbl_factory": "Work Plant *",
        "factory_opts": ["Tay Ninh Plant", "Hai Phong Plant"],
        "factory_filter_opts": ["All Plants", "Tay Ninh Plant", "Hai Phong Plant"],
        "identity_filter_opts": ["All", "VN Employees", "Foreign Staff"],
        "lbl_dept": "Department *",
        "dept_opts": ["Executive Office", "Management Dept", "Engineering Dept", "Production Dept", "IT Dept"],
        "lbl_pwd": "Initial Password *",
        "lbl_title": "Job Title *",
        "lbl_attendance": "Attendance Nature *",
        "attendance_opts": ["Plant Fixed Staff", "Field Engineer"],
        "lbl_country": "Nationality *",
        "country_opts": ["Vietnam", "Taiwan", "China"],
        "lbl_role": "System Role *",
        "lbl_addr_perm": "Permanent Address",
        "lbl_addr_temp": "Temporary Address in VN",
        "btn_add": "🚀 Create Employee",
        "btn_update": "💾 Save Changes",
        "btn_archive": "📂 Archive as Resigned",
        "btn_reactivate": "🔄 Rehired (Reactivate)",
        "btn_hard_delete": "🔥 Permanently Delete",
        "search_ph": "🔍 Search...",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_phone": "Phone",
        "col_id_doc": "ID / Passport / TRC",
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
                "電話": "+886-912-345-678",
                "國籍": "台灣 (Taiwan)",
                "身分證號": "",
                "護照號碼": "312345678",
                "暫住證號": "TRC-VN-888888",
                "社保證號": "N/A",
                "投保醫院": "N/A",
                "廠區": "西寧廠 (Tay Ninh)",
                "部門": "總經理室",
                "職稱": "董事長",
                "出勤性質": "廠內固定員工",
                "戶籍地址": "台北市信義路五段7號",
                "現住地址": "Tay Ninh, Vietnam",
                "角色": "admin",
                "密碼": "123456",
                "must_change_password": False,
                "狀態": "🟢 在職 (Active)"
            },
            {
                "工號": "VN-002",
                "姓名": "Nguyễn Văn Quý",
                "電話": "+84-901-234-567",
                "國籍": "越南 (Vietnam)",
                "身分證號": "079095012345",
                "護照號碼": "",
                "暫住證號": "",
                "社保證號": "7912345678",
                "投保醫院": "Bệnh viện Đa khoa Xuyên Á",
                "廠區": "海防廠 (Hai Phong)",
                "部門": "管理部",
                "職稱": "財務主管",
                "出勤性質": "廠內固定員工",
                "戶籍地址": "District 1, HCMC",
                "現住地址": "Hai Phong, Vietnam",
                "角色": "manager",
                "密碼": "123456",
                "must_change_password": True,
                "狀態": "🟢 在職 (Active)"
            }
        ]
    else:
        for e in st.session_state.employee_db:
            if "狀態" not in e: e["狀態"] = "🟢 在職 (Active)"
            if "出勤性質" not in e: e["出勤性質"] = "廠內固定員工"
            if "職稱" not in e: e["職稱"] = "一般員工"
            if "電話" not in e: e["電話"] = "+84-900-000-000"
            if "國籍" not in e: e["國籍"] = "越南 (Vietnam)"
            if "身分證號" not in e: e["身分證號"] = ""
            if "護照號碼" not in e: e["護照號碼"] = ""
            if "暫住證號" not in e: e["暫住證號"] = ""
            if "社保證號" not in e: e["社保證號"] = ""
            if "投保醫院" not in e: e["投保醫院"] = ""
            if "戶籍地址" not in e: e["戶籍地址"] = ""
            if "現住地址" not in e: e["現住地址"] = ""

    # 🎯 直覺式操作分頁順序
    tab_add_vn, tab_add_foreign, tab_edit, tab_list, tab_delete, tab_resigned = st.tabs([
        L["tab_add_vn"], L["tab_add_foreign"], L["tab_edit"], L["tab_list"], L["tab_delete"], L["tab_resigned"]
    ])

    # 1. 🇻🇳 新增越南籍員工
    with tab_add_vn:
        st.markdown("### " + L['header_add_vn'])
        auto_emp_id_vn = "VN-00" + str(len(st.session_state.employee_db) + 1)

        with st.form("form_add_vn_employee"):
            c1, c2 = st.columns(2)
            with c1:
                e_code = st.text_input(L["lbl_code"], value=auto_emp_id_vn, key="vn_code")
                e_name = st.text_input(L["lbl_name"], placeholder="例如: Nguyễn Văn An", key="vn_name")
                e_phone = st.text_input(L["lbl_phone"], placeholder="例如: +84-901-234-567", key="vn_phone")
                e_id_card = st.text_input(L["lbl_id_card"], placeholder="例如: 079095012345 (CCCD 12碼)", key="vn_id")
                e_bhxh = st.text_input(L["lbl_bhxh"], placeholder="例如: 7912345678 (社保卡號)", key="vn_bhxh")
                e_attendance = st.selectbox(L["lbl_attendance"], L["attendance_opts"], key="vn_att")
            with c2:
                e_factory = st.selectbox(L["lbl_factory"], L["factory_opts"], key="vn_fact")
                e_dept = st.selectbox(L["lbl_dept"], L["dept_opts"], key="vn_dept")
                e_title = st.text_input(L["lbl_title"], value="技術員 / 作業員", key="vn_title")
                e_hospital = st.text_input(L["lbl_hospital"], value="Bệnh viện Đa khoa Tây Ninh", key="vn_hosp")
                e_pwd = st.text_input(L["lbl_pwd"], value="123456", key="vn_pwd")
                
                role_keys = list(role_dict.keys())
                role_display_names = list(role_dict.values())
                sel_role_display = st.selectbox(L["lbl_role"], role_display_names, key="vn_role")
                e_role = role_keys[role_display_names.index(sel_role_display)]

            e_addr_perm = st.text_input(L["lbl_addr_perm"], placeholder="戶籍地址 (Hộ khẩu thường trú)", key="vn_perm")
            e_addr_temp = st.text_input(L["lbl_addr_temp"], placeholder="現住地址 (Chỗ ở hiện tại)", key="vn_temp")

            submitted_vn = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted_vn:
                if e_code and e_name and e_phone and e_id_card:
                    existing_codes = [e["工號"] for e in st.session_state.employee_db]
                    if e_code in existing_codes:
                        st.error("⚠️ 錯誤：工號 " + e_code + " 已經存在！")
                    else:
                        st.session_state.employee_db.append({
                            "工號": e_code,
                            "姓名": e_name,
                            "電話": e_phone,
                            "國籍": "越南 (Vietnam)",
                            "身分證號": e_id_card,
                            "護照號碼": "",
                            "暫住證號": "",
                            "社保證號": e_bhxh,
                            "投保醫院": e_hospital,
                            "廠區": e_factory,
                            "部門": e_dept,
                            "職稱": e_title,
                            "出勤性質": e_attendance,
                            "戶籍地址": e_addr_perm,
                            "現住地址": e_addr_temp,
                            "角色": e_role,
                            "密碼": e_pwd,
                            "must_change_password": True,
                            "狀態": "🟢 在職 (Active)"
                        })
                        st.success("🇻🇳 成功新增越南籍員工 " + e_name + " (工號: " + e_code + ")！")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫必填欄位：工號、姓名、聯絡電話與公民身分證號 (CCCD)！")

    # 2. 🇹🇼🇨🇳 新增外派幹部
    with tab_add_foreign:
        st.markdown("### " + L['header_add_foreign'])
        auto_emp_id_fo = "TW-00" + str(len(st.session_state.employee_db) + 1)

        with st.form("form_add_foreign_employee"):
            c1, c2 = st.columns(2)
            with c1:
                e_code_fo = st.text_input(L["lbl_code"], value=auto_emp_id_fo, key="fo_code")
                e_name_fo = st.text_input(L["lbl_name"], placeholder="例如: 王大明 / 張偉", key="fo_name")
                e_phone_fo = st.text_input(L["lbl_phone"], placeholder="例如: +886-912-345-678", key="fo_phone")
                e_country_fo = st.selectbox(L["lbl_country"], ["台灣 (Taiwan)", "中國 (China)"], key="fo_country")
                e_passport = st.text_input(L["lbl_passport"], placeholder="例如: 312345678 (護照號碼)", key="fo_pass")
                e_trc = st.text_input(L["lbl_trc"], placeholder="例如: TRC-VN-123456 (暫住證號)", key="fo_trc")
                e_attendance_fo = st.selectbox(L["lbl_attendance"], L["attendance_opts"], key="fo_att")
            with c2:
                e_factory_fo = st.selectbox(L["lbl_factory"], L["factory_opts"], key="fo_fact")
                e_dept_fo = st.selectbox(L["lbl_dept"], L["dept_opts"], key="fo_dept")
                e_title_fo = st.text_input(L["lbl_title"], value="外派專案經理 / 工程師", key="fo_title")
                e_pwd_fo = st.text_input(L["lbl_pwd"], value="123456", key="fo_pwd")
                
                role_keys = list(role_dict.keys())
                role_display_names = list(role_dict.values())
                sel_role_display_fo = st.selectbox(L["lbl_role"], role_display_names, key="fo_role")
                e_role_fo = role_keys[role_display_names.index(sel_role_display_fo)]

            e_addr_perm_fo = st.text_input(L["lbl_addr_perm"], placeholder="台灣或中國原籍地址", key="fo_perm")
            e_addr_temp_fo = st.text_input(L["lbl_addr_temp"], placeholder="越南公司宿舍 / 租屋地址", key="fo_temp")

            st.markdown("---")
            st.markdown("##### 📤 外派幹部官方證照照片上傳 (護照影本、暫住證正反面)")
            uploaded_docs_fo = st.file_uploader(
                "請上傳護照正面與暫住證正反面照片/PDF (可多張)", 
                type=["png", "jpg", "jpeg", "pdf"], 
                accept_multiple_files=True,
                key="fo_uploader"
            )

            submitted_fo = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted_fo:
                if e_code_fo and e_name_fo and e_phone_fo and e_passport and e_trc:
                    existing_codes = [e["工號"] for e in st.session_state.employee_db]
                    if e_code_fo in existing_codes:
                        st.error("⚠️ 錯誤：工號 " + e_code_fo + " 已經存在！")
                    else:
                        doc_status_fo = "已上傳 " + str(len(uploaded_docs_fo)) + " 張證件照" if uploaded_docs_fo else "⚠️ 未上傳證件照"
                        st.session_state.employee_db.append({
                            "工號": e_code_fo,
                            "姓名": e_name_fo,
                            "電話": e_phone_fo,
                            "國籍": e_country_fo,
                            "身分證號": "",
                            "護照號碼": e_passport,
                            "暫住證號": e_trc,
                            "社保證號": "N/A",
                            "投保醫院": "國際商務醫療險",
                            "廠區": e_factory_fo,
                            "部門": e_dept_fo,
                            "職稱": e_title_fo,
                            "出勤性質": e_attendance_fo,
                            "戶籍地址": e_addr_perm_fo,
                            "現住地址": e_addr_temp_fo,
                            "證件照狀態": doc_status_fo,
                            "角色": e_role_fo,
                            "密碼": e_pwd_fo,
                            "must_change_password": True,
                            "狀態": "🟢 在職 (Active)"
                        })
                        st.success("🇹🇼🇨🇳 成功新增外派幹部 " + e_name_fo + " (護照: " + e_passport + ")！(" + doc_status_fo + ")")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫外派幹部必填欄位：工號、姓名、電話、護照號碼與暫住證號！")

    # 3. ✏️ 修改員工資料 (加入「廠區篩選」與「身分篩選」雙重過濾開關，並強化成功儲存通知)
    with tab_edit:
        st.markdown("### " + L['header_edit'])
        if st.session_state.employee_db:
            fc_edit1, fc_edit2 = st.columns(2)
            with fc_edit1:
                edit_plant_filter = st.selectbox("🎯 篩選廠區 (Filter Plant)", L["factory_filter_opts"], key="edit_plant_filter")
            with fc_edit2:
                edit_identity_filter = st.selectbox("👤 篩選人員身分 (Filter Identity)", L["identity_filter_opts"], key="edit_identity_filter")

            filtered_edit_pool = [e for e in st.session_state.employee_db if "在職" in e.get("狀態", "")]
            
            if "西寧" in edit_plant_filter:
                filtered_edit_pool = [e for e in filtered_edit_pool if "西寧" in e.get("廠區", "")]
            elif "海防" in edit_plant_filter:
                filtered_edit_pool = [e for e in filtered_edit_pool if "海防" in e.get("廠區", "")]

            if "越南員工" in edit_identity_filter:
                filtered_edit_pool = [e for e in filtered_edit_pool if "越南" in e.get("國籍", "")]
            elif "外派幹部" in edit_identity_filter:
                filtered_edit_pool = [e for e in filtered_edit_pool if "越南" not in e.get("國籍", "")]

            if filtered_edit_pool:
                emp_codes = [e["工號"] + " - " + e["姓名"] + " (" + e.get("廠區", "") + " / " + e.get("國籍", "") + ")" for e in filtered_edit_pool]
                sel_target = st.selectbox("選擇要修改的員工 (Select Employee)", emp_codes, key="edit_emp_select")
                target_code = sel_target.split(" - ")[0]
                
                target_emp = next((e for e in st.session_state.employee_db if e["工號"] == target_code), None)
                
                if target_emp:
                    with st.form("form_edit_employee"):
                        ed1, ed2 = st.columns(2)
                        with ed1:
                            ed_name = st.text_input(L["lbl_name"], value=target_emp["姓名"])
                            ed_phone = st.text_input(L["lbl_phone"], value=target_emp.get("電話", ""))
                            ed_country = st.selectbox(
                                L["lbl_country"], 
                                L["country_opts"], 
                                index=0 if target_emp.get("國籍") == "越南 (Vietnam)" else (1 if target_emp.get("國籍") == "台灣 (Taiwan)" else 2),
                                key="edit_country_sel"
                            )
                            
                            if ed_country == "越南 (Vietnam)":
                                ed_id_card = st.text_input(L["lbl_id_card"], value=target_emp.get("身分證號", ""))
                                ed_bhxh = st.text_input(L["lbl_bhxh"], value=target_emp.get("社保證號", ""))
                                ed_passport, ed_trc = "", ""
                            else:
                                ed_passport = st.text_input(L["lbl_passport"], value=target_emp.get("護照號碼", ""))
                                ed_trc = st.text_input(L["lbl_trc"], value=target_emp.get("暫住證號", ""))
                                ed_id_card, ed_bhxh = "", ""

                            ed_factory = st.selectbox(
                                L["lbl_factory"], 
                                L["factory_opts"], 
                                index=0 if "西寧" in target_emp["廠區"] else 1,
                                key="edit_factory_sel"
                            )
                        with ed2:
                            ed_title = st.text_input(L["lbl_title"], value=target_emp.get("職稱", ""))
                            ed_hospital = st.text_input(L["lbl_hospital"], value=target_emp.get("投保醫院", ""))
                            
                            current_att = target_emp.get("出勤性質", L["attendance_opts"][0])
                            att_index = L["attendance_opts"].index(current_att) if current_att in L["attendance_opts"] else 0
                            ed_attendance = st.selectbox(
                                L["lbl_attendance"], 
                                L["attendance_opts"], 
                                index=att_index,
                                key="edit_attendance_sel"
                            )
                            
                            role_keys = list(role_dict.keys())
                            role_display_names = list(role_dict.values())
                            current_role_idx = role_keys.index(target_emp["角色"]) if target_emp["角色"] in role_keys else 0
                            sel_ed_role_display = st.selectbox(
                                L["lbl_role"], 
                                role_display_names, 
                                index=current_role_idx,
                                key="edit_role_sel"
                            )
                            ed_role = role_keys[role_display_names.index(sel_ed_role_display)]
                            
                            ed_pwd = st.text_input("重設新密碼 (Reset Password)", value=target_emp.get("密碼", "123456"))

                        ed_addr_perm = st.text_input(L["lbl_addr_perm"], value=target_emp.get("戶籍地址", ""))
                        ed_addr_temp = st.text_input(L["lbl_addr_temp"], value=target_emp.get("現住地址", ""))

                        # 💾 儲存修改按鈕與明確成功通知回饋
                        if st.form_submit_button(L["btn_update"], type="primary", use_container_width=True):
                            target_emp["姓名"] = ed_name
                            target_emp["電話"] = ed_phone
                            target_emp["國籍"] = ed_country
                            target_emp["身分證號"] = ed_id_card
                            target_emp["護照號碼"] = ed_passport
                            target_emp["暫住證號"] = ed_trc
                            target_emp["社保證號"] = ed_bhxh
                            target_emp["投保醫院"] = ed_hospital
                            target_emp["廠區"] = ed_factory
                            target_emp["職稱"] = ed_title
                            target_emp["出勤性質"] = ed_attendance
                            target_emp["角色"] = ed_role
                            target_emp["密碼"] = ed_pwd
                            target_emp["戶籍地址"] = ed_addr_perm
                            target_emp["現住地址"] = ed_addr_temp
                            
                            # 🎯 加入顯著的成功通知與畫面重新整理
                            st.success(f"🎉 成功！員工 [{ed_name} ({target_code})] 的個人檔案與權限已成功更新至系統！")
                            st.balloons()
            else:
                st.info("⚠️ 找不到符合此篩選條件的在職員工。請調整上方的廠區或身分篩選條件。")
        else:
            st.info("尚無員工可供修改。")

    # 4. 👥 現職員工名冊 (加入廠區分流篩選)
    with tab_list:
        st.markdown("### " + L['header_list'])
        
        fc1, fc2 = st.columns([1, 2])
        with fc1:
            sel_plant_filter = st.selectbox("依廠區篩選 (Filter by Plant)", L["factory_filter_opts"], key="list_plant_filter")
        with fc2:
            search_q = st.text_input(L["search_ph"], key="emp_search_box_active")

        active_data = [e for e in st.session_state.employee_db if "在職" in e.get("狀態", "")]
        
        if "西寧" in sel_plant_filter:
            active_data = [e for e in active_data if "西寧" in e.get("廠區", "")]
        elif "海防" in sel_plant_filter:
            active_data = [e for e in active_data if "海防" in e.get("廠區", "")]

        if search_q:
            active_data = [
                e for e in active_data 
                if search_q.lower() in e.get("姓名", "").lower() or search_q.lower() in e.get("工號", "").lower() or search_q.lower() in e.get("身分證號", "").lower() or search_q.lower() in e.get("護照號碼", "").lower()
            ]

        if active_data:
            display_list = []
            for idx, emp in enumerate(active_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                if emp.get("國籍") == "越南 (Vietnam)":
                    doc_no = "CCCD: " + str(emp.get('身分證號', ''))
                else:
                    doc_no = "護照: " + str(emp.get('護照號碼', '')) + " / 暫住證: " + str(emp.get('暫住證號', ''))
                
                display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: emp["工號"],
                    L["col_name"]: emp["姓名"],
                    L["col_phone"]: emp.get("電話", ""),
                    L["col_id_doc"]: doc_no,
                    L["col_factory"]: emp["廠區"],
                    L["col_dept"]: emp["部門"],
                    L["col_title"]: emp["職稱"],
                    L["col_attendance"]: emp.get("出勤性質", "廠內固定員工"),
                    L["col_role"]: role_display,
                    L["col_status"]: emp["狀態"]
                })
            st.dataframe(pd.DataFrame(display_list), use_container_width=True)
        else:
            st.info("目前在該廠區尚無在職員工記錄。")

    # 5. 🗑️ 員工離職及刪除 (加入廠區分流篩選)
    with tab_delete:
        st.markdown("### " + L['header_delete'])
        
        if st.session_state.employee_db:
            del_plant_filter = st.selectbox("依廠區篩選要處理的員工", L["factory_filter_opts"], key="del_plant_filter")
            
            target_pool = [e for e in st.session_state.employee_db if "在職" in e.get("狀態", "")]
            if "西寧" in del_plant_filter:
                target_pool = [e for e in target_pool if "西寧" in e.get("廠區", "")]
            elif "海防" in del_plant_filter:
                target_pool = [e for e in target_pool if "海防" in e.get("廠區", "")]

            if target_pool:
                all_emp_codes = [e["工號"] + " - " + e["姓名"] + " (" + e.get("廠區", "") + ")" for e in target_pool]
                sel_target_del = st.selectbox("選擇要處理的在職員工帳號", all_emp_codes, key="manage_emp_select")
                target_code = sel_target_del.split(" - ")[0]

                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button(L["btn_archive"], type="secondary", use_container_width=True):
                        for e in st.session_state.employee_db:
                            if e["工號"] == target_code:
                                e["狀態"] = "🔴 離職 (Resigned)"
                        st.success("✅ 員工 " + target_code + " 已辦理離職並移至離職歷史名冊。")
                        st.rerun()

                with col_btn2:
                    if st.button(L["btn_hard_delete"], type="primary", use_container_width=True):
                        st.session_state.employee_db = [e for e in st.session_state.employee_db if e["工號"] != target_code]
                        st.success("🔥 帳號 " + target_code + " 已自系統中徹底刪除。")
                        st.rerun()
            else:
                st.info("該廠區目前無在職員工可供處理。")
        else:
            st.info("目前系統中無任何員工記錄。")

    # 6. 📂 離職名冊 (加入廠區分流篩選)
    with tab_resigned:
        st.markdown("### " + L['header_resigned'])
        
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            res_plant_filter = st.selectbox("依廠區篩選離職人員", L["factory_filter_opts"], key="res_plant_filter")
        with rc2:
            resigned_search = st.text_input("🔍 搜尋離職人員姓名或證件號...", key="emp_search_box_resigned")

        resigned_data = [e for e in st.session_state.employee_db if "離職" in e.get("狀態", "")]
        
        if "西寧" in res_plant_filter:
            resigned_data = [e for e in resigned_data if "西寧" in e.get("廠區", "")]
        elif "海防" in res_plant_filter:
            resigned_data = [e for e in resigned_data if "海防" in e.get("廠區", "")]

        if resigned_search:
            resigned_data = [
                e for e in resigned_data 
                if resigned_search.lower() in e.get("姓名", "").lower() or resigned_search.lower() in e.get("工號", "").lower()
            ]

        if resigned_data:
            res_display_list = []
            for idx, emp in enumerate(resigned_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                res_display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: emp["工號"],
                    L["col_name"]: emp["姓名"],
                    L["col_phone"]: emp.get("電話", ""),
                    L["col_factory"]: emp["廠區"],
                    L["col_dept"]: emp["部門"],
                    L["col_title"]: emp["職稱"],
                    L["col_role"]: role_display,
                    L["col_status"]: emp["狀態"]
                })
            st.dataframe(pd.DataFrame(res_display_list), use_container_width=True)
            
            st.markdown("---")
            res_codes = [e["工號"] + " - " + e["姓名"] for e in resigned_data]
            sel_res_target = st.selectbox("選擇要辦理復職回鍋的員工", res_codes, key="reactivate_select")
            res_target_code = sel_res_target.split(" - ")[0]

            if st.button(L["btn_reactivate"], type="primary"):
                for e in st.session_state.employee_db:
                    if e["工號"] == res_target_code:
                        e["狀態"] = "🟢 在職 (Active)"
                st.success("🔄 員工 " + res_target_code + " 已成功辦理復職回鍋！")
                st.rerun()
        else:
            st.info("目前尚無離職歷史記錄。")
