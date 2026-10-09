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
        "tab_list": "👥 現職員工名冊",
        "tab_resigned": "📂 離職與歷史名冊 (Archive)",
        "tab_add": "➕ 新增員工與初始帳密設定",
        "tab_edit": "✏️ 修改員工資料與重設密碼",
        "tab_delete": "🗑️ 離職歸檔與帳號刪除",
        "header_list": "📋 全公司現職員工名冊與權限總覽",
        "header_resigned": "📂 離職歷史人員名冊與復職管理",
        "header_add": "➕ 新增員工個人檔案（含越南本地員工與台/陸籍幹部護照暫住證登錄）",
        "header_edit": "✏️ 修改員工基本資料與證件管理",
        "header_delete": "🗑️ 辦理離職歸檔或徹底刪除重複帳號",
        "lbl_code": "員工工號 (登入帳號) *",
        "lbl_name": "員工姓名 (Employee Name) *",
        "lbl_phone": "聯絡電話 (Phone No.) *",
        "lbl_id_card": "公民身分證號 (CCCD / 越南籍) *",
        "lbl_passport": "護照號碼 (Passport No. / 台陸籍) *",
        "lbl_trc": "暫住證號 (TRC / Giấy tạm trú) *",
        "lbl_bhxh": "社會保險證號 (Mã số BHXH)",
        "lbl_hospital": "投保指定醫療院所 (Bệnh viện KCB BHYT)",
        "lbl_factory": "工作廠區 (Factory) *",
        "factory_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"],
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
        "col_id_doc": "身分證 / 護照 / 暫住證",
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
        "tab_list": "👥 Nhân viên hiện tại",
        "tab_resigned": "📂 Lịch sử nghỉ việc",
        "tab_add": "➕ Thêm Nhân viên mới",
        "tab_edit": "✏️ Chỉnh sửa Thông tin",
        "tab_delete": "🗑️ Lưu trữ & Xóa",
        "header_list": "📋 Danh sách nhân viên đang làm việc",
        "header_resigned": "📂 Hồ sơ nhân viên đã nghỉ việc",
        "header_add": "➕ Thêm hồ sơ nhân viên (Bao gồm Hộ chiếu & Thẻ tạm trú)",
        "header_edit": "✏️ Cập nhật thông tin",
        "header_delete": "🗑️ Xử lý nghỉ việc hoặc Xóa vĩnh viễn",
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
        "tab_list": "👥 Active Employees",
        "tab_resigned": "📂 Resigned Archives",
        "tab_add": "➕ Add Employee",
        "tab_edit": "✏️ Edit Profile",
        "tab_delete": "🗑️ Archive / Delete",
        "header_list": "📋 Active Employee Directory",
        "header_resigned": "📂 Resigned Employee History & Rehiring",
        "header_add": "➕ Add Employee Profile (With Passport & TRC)",
        "header_edit": "✏️ Update Employee Info",
        "header_delete": "🗑️ Archive Resigned or Delete Duplicates",
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

    tab_list, tab_resigned, tab_add, tab_edit, tab_delete = st.tabs([
        L["tab_list"], L["tab_resigned"], L["tab_add"], L["tab_edit"], L["tab_delete"]
    ])

    # 1. 👥 現職員工名冊
    with tab_list:
        st.markdown("### " + L['header_list'])
        search_q = st.text_input(L["search_ph"], key="emp_search_box_active")

        active_data = [e for e in st.session_state.employee_db if "在職" in e.get("狀態", "")]
        if search_q:
            active_data = [
                e for e in active_data 
                if search_q.lower() in e.get("姓名", "").lower() or search_q.lower() in e.get("工號", "").lower() or search_q.lower() in e.get("身分證號", "").lower() or search_q.lower() in e.get("護照號碼", "").lower()
            ]

        if active_data:
            display_list = []
            for idx, emp in enumerate(active_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                doc_no = emp.get("身分證號") if emp.get("國籍") == "越南 (Vietnam)" else ("護照: " + str(emp.get('護照號碼')) + " / 暫住證: " + str(emp.get('暫住證號')))
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
            st.info("目前尚無在職員工記錄。")

    # 2. 📂 離職與歷史名冊
    with tab_resigned:
        st.markdown("### " + L['header_resigned'])
        resigned_search = st.text_input("🔍 搜尋離職人員姓名或證件號...", key="emp_search_box_resigned")

        resigned_data = [e for e in st.session_state.employee_db if "離職" in e.get("狀態", "")]
        if resigned_search:
            resigned_data = [
                e for e in resigned_data 
                if resigned_search.lower() in e.get("姓名", "").lower() or resigned_search.lower() in e.get("工號", "").lower()
            ]

        if resigned_data:
            res_display_list = []
            for idx, emp in enumerate(resigned_data, 1):
                role_display = role_dict.get(emp["角色"], emp["角色"])
                doc_no = emp.get("身分證號") if emp.get("國籍") == "越南 (Vietnam)" else ("護照: " + str(emp.get('護照號碼')))
                res_display_list.append({
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
            st.dataframe(pd.DataFrame(res_display_list), use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🔄 離職人員回鍋復職 (Rehire / Reactivate)")
            rehire_opts = [e["工號"] + " - " + e["姓名"] for e in resigned_data]
            sel_rehire = st.selectbox("選擇要辦理復職的員工", rehire_opts, key="rehire_select")
            
            if st.button("🔄 " + L["btn_reactivate"], type="primary"):
                rehire_code = sel_rehire.split(" - ")[0]
                for e in st.session_state.employee_db:
                    if e["工號"] == rehire_code:
                        e["狀態"] = "🟢 在職 (Active)"
                st.success("🎉 員工 " + rehire_code + " 已成功復職並轉為現職員工！")
                st.rerun()
        else:
            st.info("📂 目前歷史檔案中無離職員工記錄。")

    # 3. ➕ 新增員工
    with tab_add:
        st.markdown("### " + L['header_add'])
        auto_emp_id = "VN-00" + str(len(st.session_state.employee_db) + 1)

        with st.form("form_add_employee"):
            c1, c2 = st.columns(2)
            with c1:
                e_code = st.text_input(L["lbl_code"], value=auto_emp_id)
                e_name = st.text_input(L["lbl_name"], placeholder="例如: Nguyễn Văn An 或 姓名")
                e_phone = st.text_input(L["lbl_phone"], placeholder="例如: +84-901-234-567")
                
                e_country = st.selectbox(L["lbl_country"], L["country_opts"])

                if e_country == "越南 (Vietnam)":
                    e_id_card = st.text_input(L["lbl_id_card"], placeholder="例如: 079095012345 (CCCD 12碼)")
                    e_bhxh = st.text_input(L["lbl_bhxh"], placeholder="例如: 7912345678 (社保卡號)")
                    e_passport, e_trc = "", ""
                else:
                    e_passport = st.text_input(L["lbl_passport"], placeholder="例如: 312345678 (護照號碼)")
                    e_trc = st.text_input(L["lbl_trc"], placeholder="例如: TRC-VN-123456 (暫住證號)")
                    e_id_card, e_bhxh = "", ""

                e_attendance = st.selectbox(L["lbl_attendance"], L["attendance_opts"])

            with c2:
                e_factory = st.selectbox(L["lbl_factory"], L["factory_opts"])
                e_dept = st.selectbox(L["lbl_dept"], L["dept_opts"])
                e_title = st.text_input(L["lbl_title"], value="工程師 / 主管")
                
                if e_country == "越南 (Vietnam)":
                    e_hospital = st.text_input(L["lbl_hospital"], value="Bệnh viện Đa khoa Tây Ninh")
                else:
                    e_hospital = "國際醫療/商務保險"
                    st.text_input("外籍幹部醫療保障", value=e_hospital, disabled=True)

                e_pwd = st.text_input(L["lbl_pwd"], value="123456")
                
                role_keys = list(role_dict.keys())
                role_display_names = list(role_dict.values())
                sel_role_display = st.selectbox(L["lbl_role"], role_display_names)
                e_role = role_keys[role_display_names.index(sel_role_display)]

            e_addr_perm = st.text_input(L["lbl_addr_perm"], placeholder="原籍戶籍地址")
            e_addr_temp = st.text_input(L["lbl_addr_temp"], placeholder="越南暫住地址 / 宿舍地址")

            st.markdown("---")
            st.markdown("##### 📤 證件與官方證照照片上傳區 (護照正面、暫住證正反面等)")
            uploaded_id_docs = st.file_uploader(
                "請上傳護照影本、暫住證正反面或身分證照片（可多張同時上傳）", 
                type=["png", "jpg", "jpeg", "pdf"], 
                accept_multiple_files=True,
                help="台陸籍幹部請上傳護照與暫住證；越南籍請上傳 CCCD 正反面。"
            )

            submitted = st.form_submit_button(L["btn_add"], type="primary", use_container_width=True)
            if submitted:
                doc_check = e_id_card if e_country == "越南 (Vietnam)" else e_passport
                if e_code and e_name and e_phone and doc_check:
                    existing_codes = [e["工號"] for e in st.session_state.employee_db]
                    if e_code in existing_codes:
                        st.error("⚠️ 錯誤：工號 " + e_code + " 已經存在！")
                    else:
                        doc_status = "已上傳 " + str(len(uploaded_id_docs)) + " 張證件照" if uploaded_id_docs else "⚠️ 未上傳證件照"
                        st.session_state.employee_db.append({
                            "工號": e_code,
                            "姓名": e_name,
                            "電話": e_phone,
                            "國籍": e_country,
                            "身分證號": e_id_card,
                            "護照號碼": e_passport,
                            "暫住證號": e_trc,
                            "社保證號": e_bhxh,
                            "投保醫院": e_hospital,
                            "廠區": e_factory,
                            "部門": e_dept,
                            "職稱": e_title,
                            "出勤性質": e_attendance,
                            "戶籍地址": e_addr_perm,
                            "現住地址": e_addr_temp,
                            "證件照狀態": doc_status,
                            "角色": e_role,
                            "密碼": e_pwd,
                            "must_change_password": True,
                            "狀態": "🟢 在職 (Active)"
                        })
                        st.success("✅ 成功新增員工 " + e_name + " (工號: "
