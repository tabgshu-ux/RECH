import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 員工與人事管理模組多語系字典 (i18n)
# ----------------------------------------------------
EMPLOYEE_I18N = {
    "繁體中文": {
        "title": "👤 管理部 - 員工與人事管理",
        "caption": "維護全廠區員工個人檔案、合約記錄、工作廠區、離職歸檔、人臉/指紋打卡機資料彙集。",
        "tab_roster": "📋 員工名冊與詳細編輯",
        "tab_punch": "⏰ 智慧打卡紀錄",
        "tab_leave": "📝 請假簽核中心",
        "roster_header": "📋 現有在職員工名冊",
        "add_emp_header": "➕ 新增員工個人檔案",
        "lbl_emp_id": "員工編號",
        "lbl_name": "員工姓名",
        "lbl_nationality": "國籍",
        "lbl_site": "工作廠區",
        "lbl_title": "職稱",
        "lbl_role": "系統權限角色",
        "btn_add_emp": "💾 立即新增員工",
        "success_add": "✅ 成功新增員工：",
        "warning_fill": "⚠️ 請填寫員工編號與姓名！",
        "punch_header": "⏰ 廠區人臉 / 指紋打卡紀錄彙集",
        "punch_caption": "💡 模擬串接工廠各出入口之生物辨識打卡機資料。",
        "select_emp": "選擇打卡員工",
        "punch_type": "打卡類型",
        "clock_in": "上班簽到 (Clock In)",
        "clock_out": "下班簽退 (Clock Out)",
        "btn_punch": "📍 模擬刷臉打卡",
        "success_punch": "紀錄成功！",
        "no_punch": "目前尚無今日打卡紀錄。",
        "leave_header": "📝 請假申請與簽核流程",
        "lbl_leave_emp": "請假員工",
        "lbl_leave_type": "假別",
        "leave_opts": ["特休假 (Annual Leave)", "事假 (Personal Leave)", "病假 (Sick Leave)", "公出 (Official Business)"],
        "lbl_reason": "請假事由",
        "btn_submit_leave": "📤 送出請假申請",
        "success_leave": "✅ 請假申請已送出，等待主管審核。",
        "leave_list_header": "📋 目前請假單列表",
        "col_id": "工號",
        "col_name": "姓名",
        "col_nation": "國籍",
        "col_site": "廠區",
        "col_dept": "部門",
        "col_title": "職稱",
        "col_role": "角色",
        "col_phone": "電話",
        "col_face": "生物辨識代碼",
        "site_opts": ["西寧廠", "🇻🇳 越南西寧廠 (Tay Ninh Plant)", "平陽廠"],
        "nat_opts": ["🇹🇼 台灣 (Taiwan)", "🇻🇳 越南 (Vietnamese)", "🇨🇳 中國 (Chinese)"]
    },
    "Tiếng Việt": {
        "title": "👤 Khối Quản lý - Quản lý Nhân sự & Nhân viên",
        "caption": "Quản lý hồ sơ nhân viên, hợp đồng lao động, nhà máy làm việc, chấm công sinh trắc học.",
        "tab_roster": "📋 Danh sách Nhân viên",
        "tab_punch": "⏰ Nhật ký Chấm công thông minh",
        "tab_leave": "📝 Trung tâm Đơn nghỉ phép",
        "roster_header": "📋 Danh sách nhân viên đang làm việc",
        "add_emp_header": "➕ Thêm hồ sơ nhân viên mới",
        "lbl_emp_id": "Mã nhân viên",
        "lbl_name": "Họ tên nhân viên",
        "lbl_nationality": "Quốc tịch",
        "lbl_site": "Nhà máy làm việc",
        "lbl_title": "Chức vụ",
        "lbl_role": "Quyền hệ thống",
        "btn_add_emp": "💾 Thêm nhân viên ngay",
        "success_add": "✅ Thêm nhân viên thành công: ",
        "warning_fill": "⚠️ Vui lòng điền mã nhân viên và họ tên!",
        "punch_header": "⏰ Tổng hợp dữ liệu chấm công khuôn mặt / vân tay",
        "punch_caption": "💡 Mô phỏng kết nối máy chấm công sinh trắc học tại các cổng nhà máy.",
        "select_emp": "Chọn nhân viên chấm công",
        "punch_type": "Loại chấm công",
        "clock_in": "Vào ca (Clock In)",
        "clock_out": "Tan ca (Clock Out)",
        "btn_punch": "📍 Mô phỏng chấm công",
        "success_punch": "Ghi nhận thành công!",
        "no_punch": "Hiện chưa có bản ghi chấm công trong ngày.",
        "leave_header": "📝 Đăng ký & Quy trình xét duyệt nghỉ phép",
        "lbl_leave_emp": "Nhân viên nghỉ phép",
        "lbl_leave_type": "Loại nghỉ phép",
        "leave_opts": ["Phép năm (Annual Leave)", "Việc riêng (Personal Leave)", "Nghỉ bệnh (Sick Leave)", "Công tác (Official Business)"],
        "lbl_reason": "Lý do xin nghỉ",
        "btn_submit_leave": "📤 Gửi đơn xin nghỉ",
        "success_leave": "✅ Đơn xin nghỉ đã được gửi, chờ quản lý duyệt.",
        "leave_list_header": "📋 Danh sách đơn nghỉ phép hiện tại",
        "col_id": "Mã NV",
        "col_name": "Họ tên",
        "col_nation": "Quốc tịch",
        "col_site": "Nhà máy",
        "col_dept": "Bộ phận",
        "col_title": "Chức vụ",
        "col_role": "Quyền",
        "col_phone": "Điện thoại",
        "col_face": "Mã sinh trắc",
        "site_opts": ["Nhà máy Tây Ninh", "Nhà máy Tây Ninh (Tay Ninh Plant)", "Nhà máy Bình Dương"],
        "nat_opts": ["🇹🇼 Đài Loan (Taiwan)", "🇻🇳 Việt Nam (Vietnamese)", "🇨🇳 Trung Quốc (Chinese)"]
    },
    "English": {
        "title": "👤 Admin - Employee & HR Management",
        "caption": "Manage employee profiles, contracts, work plants, and biometric attendance records.",
        "tab_roster": "📋 Employee Roster",
        "tab_punch": "⏰ Smart Attendance Log",
        "tab_leave": "📝 Leave Request Center",
        "roster_header": "📋 Active Employee Roster",
        "add_emp_header": "➕ Register New Employee Profile",
        "lbl_emp_id": "Employee ID",
        "lbl_name": "Full Name",
        "lbl_nationality": "Nationality",
        "lbl_site": "Work Plant",
        "lbl_title": "Job Title",
        "lbl_role": "System Role",
        "btn_add_emp": "💾 Save Employee",
        "success_add": "✅ Successfully added employee: ",
        "warning_fill": "⚠️ Please fill in Employee ID and Name!",
        "punch_header": "📦 Biometric Attendance Records",
        "punch_caption": "💡 Simulate face/fingerprint attendance terminals at plant gates.",
        "select_emp": "Select Employee",
        "punch_type": "Attendance Type",
        "clock_in": "Clock In",
        "clock_out": "Clock Out",
        "btn_punch": "📍 Simulate Clock-In",
        "success_punch": "Recorded successfully!",
        "no_punch": "No attendance records for today.",
        "leave_header": "📝 Leave Request & Approval Flow",
        "lbl_leave_emp": "Employee",
        "lbl_leave_type": "Leave Type",
        "leave_opts": ["Annual Leave", "Personal Leave", "Sick Leave", "Official Business"],
        "lbl_reason": "Reason for Leave",
        "btn_submit_leave": "📤 Submit Leave Request",
        "success_leave": "✅ Leave request submitted, pending approval.",
        "leave_list_header": "📋 Current Leave Requests",
        "col_id": "Emp ID",
        "col_name": "Name",
        "col_nation": "Nationality",
        "col_site": "Plant",
        "col_dept": "Department",
        "col_title": "Job Title",
        "col_role": "Role",
        "col_phone": "Phone",
        "col_face": "Biometric Token",
        "site_opts": ["Tay Ninh Plant", "Tay Ninh Plant (Tay Ninh)", "Binh Duong Plant"],
        "nat_opts": ["🇹🇼 Taiwan", "🇻🇳 Vietnamese", "🇨🇳 Chinese"]
    }
}

# ----------------------------------------------------
# 🔄 智慧語意對照引擎 (處理員工姓名、職稱與部門)
# ----------------------------------------------------
def smart_translate_emp(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    if target_lang == "Tiếng Việt":
        if "張董事長" in text_val: return "Chủ tịch Trương (Chairman)"
        if "李元隆" in text_val: return "Lý Nguyên Long (Vice GM)"
        if "董事長" in text_val: return "Chủ tịch HĐQT (Chairman)"
        if "總經理" in text_val: return "Tổng Giám đốc (General Manager)"
        if "副總經理" in text_val: return "Phó Tổng Giám đốc (Vice GM)"
        if "專員" in text_val: return "Chuyên viên (Specialist)"
        if "管理部" in text_val: return "Ban Quản lý"
        if "營運管理中心" in text_val: return "Trung tâm Quản lý Vận hành"
        if "西寧廠" in text_val: return "Nhà máy Tây Ninh"
    elif target_lang == "English":
        if "張董事長" in text_val: return "Chairman Chang"
        if "李元隆" in text_val: return "Lee Yuan-Lung (Vice GM)"
        if "董事長" in text_val: return "Chairman"
        if "總經理" in text_val: return "General Manager"
        if "副總經理" in text_val: return "Vice General Manager"
        if "專員" in text_val: return "Specialist"
        if "管理部" in text_val: return "Management Dept"
        if "營運管理中心" in text_val: return "Operations Management Center"
        if "西寧廠" in text_val: return "Tay Ninh Plant"

    return text_val

def render_employee_management(engine=None, t=None, lang="繁體中文"):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = EMPLOYEE_I18N.get(active_lang, EMPLOYEE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "employees_db" not in st.session_state:
        st.session_state.employees_db = [
            {
                "id": "EMP-001",
                "name": "張董事長",
                "nationality": "🇹🇼 台灣 (Taiwan)",
                "site": "西寧廠",
                "dept": "管理部",
                "title": "董事長 (Chairman)",
                "role": "Chairman",
                "phone": "0912345678",
                "address": "-",
                "face_token": "FACE-BIO-888899",
            },
            {
                "id": "EMP-002",
                "name": "Nguyễn Văn A",
                "nationality": "🇻🇳 越南 (Vietnamese)",
                "site": "西寧廠",
                "dept": "管理部",
                "title": "總經理 (General Manager)",
                "role": "GeneralManager",
                "phone": "0918999080",
                "address": "-",
                "face_token": "FACE-BIO-100234",
            },
            {
                "id": "EMP-003",
                "name": "李元隆",
                "nationality": "🇹🇼 台灣 (Taiwanese)",
                "site": "西寧廠",
                "dept": "👑 經營主管 / 營運管理中心 (Management & Operations)",
                "title": "副總經理 (Vice General Manager)",
                "role": "ViceManager",
                "phone": "-",
                "address": "-",
                "face_token": "FACE-BIO-300451",
            },
        ]

    if "attendance_db" not in st.session_state:
        st.session_state.attendance_db = []
    if "leave_requests_db" not in st.session_state:
        st.session_state.leave_requests_db = []

    tab1, tab2, tab3 = st.tabs([L["tab_roster"], L["tab_punch"], L["tab_leave"]])

    with tab1:
        st.markdown(f"### {L['roster_header']}")
        
        display_list = []
        for emp in st.session_state.employees_db:
            display_list.append({
                L["col_id"]: emp["id"],
                L["col_name"]: smart_translate_emp(emp["name"], active_lang),
                L["col_nation"]: smart_translate_emp(emp["nationality"], active_lang),
                L["col_site"]: smart_translate_emp(emp["site"], active_lang),
                L["col_dept"]: smart_translate_emp(emp["dept"], active_lang),
                L["col_title"]: smart_translate_emp(emp["title"], active_lang),
                L["col_role"]: emp["role"],
                L["col_phone"]: emp["phone"],
                L["col_face"]: emp["face_token"]
            })
        st.dataframe(pd.DataFrame(display_list), use_container_width=True)

        st.markdown("---")
        st.markdown(f"### {L['add_emp_header']}")
        with st.form("add_emp_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input(L["lbl_emp_id"], value="EMP-104")
                new_name = st.text_input(L["lbl_name"])
                new_nationality = st.selectbox(L["lbl_nationality"], L["nat_opts"])
            with c2:
                new_site = st.selectbox(L["lbl_site"], L["site_opts"])
                new_title = st.text_input(L["lbl_title"], value="專員" if active_lang == "繁體中文" else ("Chuyên viên" if active_lang == "Tiếng Việt" else "Specialist"))
                new_role = st.selectbox(L["lbl_role"], ["Chairman", "GeneralManager", "ViceManager", "Director", "Manager", "Supervisor", "Staff", "Admin"])
            
            if st.form_submit_button(L["btn_add_emp"], type="primary"):
                if new_name and new_id:
                    st.session_state.employees_db.append({
                        "id": new_id,
                        "name": new_name,
                        "nationality": new_nationality,
                        "site": new_site,
                        "dept": "管理部",
                        "title": new_title,
                        "role": new_role,
                        "phone": "-",
                        "address": "-",
                        "face_token": f"FACE-{new_id}"
                    })
                    st.success(f"{L['success_add']}{new_name}")
                    st.rerun()
                else:
                    st.warning(L["warning_fill"])

    with tab2:
        st.markdown(f"### {L['punch_header']}")
        st.info(L["punch_caption"])
        
        with st.form("mock_punch"):
            p_id = st.selectbox(L["select_emp"], [e["id"] + " - " + smart_translate_emp(e["name"], active_lang) for e in st.session_state.employees_db])
            p_type = st.radio(L["punch_type"], [L["clock_in"], L["clock_out"]])
            
            if st.form_submit_button(L["btn_punch"], type="primary"):
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.attendance_db.insert(0, {
                    "時間": now_str,
                    "員工": p_id,
                    "類型": p_type
                })
                st.success(f"{L['success_punch']} ({now_str})")
        
        st.markdown("---")
        if st.session_state.attendance_db:
            st.dataframe(pd.DataFrame(st.session_state.attendance_db), use_container_width=True)
        else:
            st.info(L["no_punch"])

    with tab3:
        st.markdown(f"### {L['leave_header']}")
        
        with st.form("leave_form"):
            l_emp = st.selectbox(L["lbl_leave_emp"], [e["id"] + " - " + smart_translate_emp(e["name"], active_lang) for e in st.session_state.employees_db])
            l_type = st.selectbox(L["lbl_leave_type"], L["leave_opts"])
            l_reason = st.text_area(L["lbl_reason"])
            
            if st.form_submit_button(L["btn_submit_leave"], type="primary"):
                st.session_state.leave_requests_db.insert(0, {
                    "申請時間": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "員工": l_emp,
                    "假別": l_type,
                    "事由": l_reason,
                    "狀態": "⏳ 待審核 (Pending)"
                })
                st.success(L["success_leave"])
                st.rerun()

        st.markdown("---")
        st.markdown(f"### {L['leave_list_header']}")
        if st.session_state.leave_requests_db:
            st.dataframe(pd.DataFrame(st.session_state.leave_requests_db), use_container_width=True)
        else:
            st.info("目前尚無請假單紀錄。")
