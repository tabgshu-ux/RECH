import streamlit as st

PASSWORD_I18N = {
    "繁體中文": {
        "title": "🔑 管理部 - 員工密碼重設與管理中心",
        "caption": "由管理部 / 人事主管協助廠內同仁重設密碼。請選擇員工工號，系統將自動帶出姓名與職位。",
        "input_emp_lbl": "選擇欲重設密碼的員工 (Select Employee) *",
        "emp_name_display": "員工姓名 (Employee Name)：",
        "new_pwd_lbl": "指派新密碼 (New Password) *",
        "confirm_pwd_lbl": "再次確認新密碼 (Confirm New Password) *",
        "btn_save": "💾 確認更新此員工密碼",
        "success": "🎉 已成功幫員工 【{name} ({emp_id})】 更新密碼！",
        "error_match": "⚠️ 兩次輸入的新密碼不相符或未填寫，請重新檢查！",
        "emp_not_found": "⚠️ 目前系統中尚無員工檔案，請先至【管理部 > 員工檔案】建立員工資料。"
    },
    "Tiếng Việt": {
        "title": "🔑 Phòng Quản lý - Đặt lại mật khẩu nhân viên",
        "caption": "Phòng Quản lý / Nhân sự hỗ trợ đặt lại mật khẩu cho nhân viên.",
        "input_emp_lbl": "Chọn nhân viên *",
        "emp_name_display": "Tên nhân viên:",
        "new_pwd_lbl": "Mật khẩu mới *",
        "confirm_pwd_lbl": "Nhập lại mật khẩu mới *",
        "btn_save": "💾 Xác nhận cập nhật mật khẩu",
        "success": "🎉 Đã cập nhật mật khẩu thành công cho nhân viên 【{name} ({emp_id})】!",
        "error_match": "⚠️ Mật khẩu không khớp hoặc chưa điền!",
        "emp_not_found": "⚠️ Không tìm thấy danh sách nhân viên."
    },
    "English": {
        "title": "🔑 Management Dept - Employee Password Reset Center",
        "caption": "HR and Management department assistance for employee password resets.",
        "input_emp_lbl": "Select Employee *",
        "emp_name_display": "Employee Name:",
        "new_pwd_lbl": "New Password *",
        "confirm_pwd_lbl": "Confirm New Password *",
        "btn_save": "💾 Confirm Employee Password Update",
        "success": "🎉 Successfully updated password for 【{name} ({emp_id})】!",
        "error_match": "⚠️ Passwords do not match or are empty!",
        "emp_not_found": "⚠️ No employee records found."
    }
}

def render_change_password_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in PASSWORD_I18N else "繁體中文"
    L = PASSWORD_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")

    # 確保 employee_db 存在（若無則給予預設範例清單，對齊員工名冊畫面）
    if "employee_db" not in st.session_state or not st.session_state.employee_db:
        st.session_state.employee_db = [
            {"工號": "2005010102", "姓名": "PHẠM HOÀNG LÂM 范皇林", "部門": "GD CT 工程經理", "職位": "工程經理", "密碼": "123456"},
            {"工號": "2005060801", "姓名": "HUỲNH VĂN THỊ 黃文詩", "部門": "生產部", "職位": "廠內固定員工", "密碼": "123456"},
            {"工號": "2005091401", "姓名": "LÊ HỒNG LÂM 黎鴻林", "部門": "P.GD CT 工程副理", "職位": "工程副理", "密碼": "123456"},
            {"工號": "2006090101", "姓名": "LÊ NGUYỄN TRÌNH 黎程程", "部門": "Tổ Trưởng CT 工程組長", "職位": "工程組長", "密碼": "123456"},
            {"工號": "2007031201", "姓名": "NGUYỄN THỊ TUYẾT NHUNG 阮氏雪絨", "部門": "管理部財務", "職位": "廠內固定員工", "密碼": "123456"},
            {"工號": "2008041201", "姓名": "ĐẶNG LÝ THUYẾT 鄧理說", "部門": "TT. Tổ điện 配盤組 組長", "職位": "配盤組長", "密碼": "123456"},
            {"工號": "2009111301", "姓名": "NGUYỄN VĂN HÀNH 阮文倖", "部門": "CQ Thiết kế 設計主管", "職位": "設計主管", "密碼": "123456"},
            {"工號": "20010071001", "姓名": "LƯƠNG NHẬT SÁNG 梁瑞隆", "部門": "GĐ Thiết kế 設計經理", "職位": "設計經理", "密碼": "123456"},
        ]

    emp_list = st.session_state.employee_db

    # 建立下拉選單格式
    emp_options = [f"{emp.get('工號', '')} - {emp.get('姓名', '')} ({emp.get('部門', '未分發')})" for emp in emp_list]

    with st.form("admin_reset_emp_pwd_form"):
        selected_option = st.selectbox(L["input_emp_lbl"], options=emp_options)
        
        # 解析工號
        target_emp_code = selected_option.split(" - ")[0].strip()
        matched_emp = next((e for e in emp_list if str(e.get("工號")) == target_emp_code), None)

        if matched_emp:
            st.info(f"📌 **{L['emp_name_display']}** `{matched_emp.get('姓名')}` | 🏢 **部門**：{matched_emp.get('部門', '未分發')} | 👔 **職位**：{matched_emp.get('職位', 'Staff')}")
        else:
            st.warning("⚠️ 請選擇正確的員工。")

        st.markdown("<br>", unsafe_allow_html=True)

        new_pwd = st.text_input(L["new_pwd_lbl"], type="password", placeholder="請輸入新密碼...")
        confirm_pwd = st.text_input(L["confirm_pwd_lbl"], type="password", placeholder="再次確認新密碼...")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
            if matched_emp and new_pwd and new_pwd == confirm_pwd:
                matched_emp["密碼"] = new_pwd
                matched_emp["must_change_password"] = True
                st.success(L["success"].format(name=matched_emp.get('姓名'), emp_id=matched_emp.get('工號')))
            else:
                st.error(L["error_match"])
