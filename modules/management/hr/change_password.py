import streamlit as st

PASSWORD_I18N = {
    "繁體中文": {
        "title": "🔑 管理部 - 員工密碼重設與管理中心",
        "caption": "由管理部 / 人事主管協助廠內同仁重設密碼。請輸入或選擇員工工號，系統將自動辨識姓名與職位。",
        "input_emp_lbl": "輸入或選擇欲重設密碼的員工工號 (Emp ID) *",
        "emp_name_display": "員工姓名 (Employee Name)：",
        "new_pwd_lbl": "指派新密碼 (New Password) *",
        "confirm_pwd_lbl": "再次確認新密碼 (Confirm New Password) *",
        "btn_save": "💾 確認更新此員工密碼",
        "success": "🎉 已成功幫員工 【{name} ({emp_id})】 更新密碼！",
        "error_match": "⚠️ 兩次輸入的新密碼不相符或未填寫，請重新檢查！",
        "emp_not_found": "⚠️ 找不到此工號的員工資料，請確認工號是否正確或先至【員工檔案】建立。"
    },
    "Tiếng Việt": {
        "title": "🔑 Phòng Quản lý - Đặt lại mật khẩu nhân viên",
        "caption": "Phòng Quản lý / Nhân sự hỗ trợ đặt lại mật khẩu cho nhân viên.",
        "input_emp_lbl": "Nhập hoặc chọn mã nhân viên (Emp ID) *",
        "emp_name_display": "Tên nhân viên:",
        "new_pwd_lbl": "Mật khẩu mới *",
        "confirm_pwd_lbl": "Nhập lại mật khẩu mới *",
        "btn_save": "💾 Xác nhận cập nhật mật khẩu",
        "success": "🎉 Đã cập nhật mật khẩu thành công cho nhân viên 【{name} ({emp_id})】!",
        "error_match": "⚠️ Mật khẩu không khớp hoặc chưa điền!",
        "emp_not_found": "⚠️ Không tìm thấy mã nhân viên này."
    },
    "English": {
        "title": "🔑 Management Dept - Employee Password Reset Center",
        "caption": "HR and Management department assistance for employee password resets.",
        "input_emp_lbl": "Enter or Select Employee ID *",
        "emp_name_display": "Employee Name:",
        "new_pwd_lbl": "New Password *",
        "confirm_pwd_lbl": "Confirm New Password *",
        "btn_save": "💾 Confirm Employee Password Update",
        "success": "🎉 Successfully updated password for 【{name} ({emp_id})】!",
        "error_match": "⚠️ Passwords do not match or are empty!",
        "emp_not_found": "⚠️ Employee ID not found."
    }
}

def render_change_password_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in PASSWORD_I18N else "繁體中文"
    L = PASSWORD_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")

    # 檢查員工資料庫是否存在
    if "employee_db" not in st.session_state or not st.session_state.employee_db:
        st.warning("⚠️ 目前系統中尚無員工檔案，請先至【管理部 > 員工檔案】建立員工資料。")
        return

    emp_list = st.session_state.employee_db

    # 建立工號選項清單 (讓管理者可以下拉選取，也可以清楚看到工號與姓名)
    emp_options = [f"{emp['工號']} - {emp['姓名']} ({emp.get('職位', 'Staff')})" for emp in emp_list]

    with st.form("admin_reset_emp_pwd_form"):
        # 1. 選擇或輸入工號
        selected_option = st.selectbox(L["input_emp_lbl"], options=emp_options)
        
        # 從選項中解析出工號
        target_emp_code = selected_option.split(" - ")[0].strip()
        
        # 尋找對應的員工物件
        matched_emp = next((e for e in emp_list if e["工號"] == target_emp_code), None)

        if matched_emp:
            # 2. 自動顯示該員工姓名與部門
            st.info(f"📌 **{L['emp_name_display']}** `{matched_emp['姓名']}` | 🏢 **部門**：{matched_emp.get('部門', '未分發')} | 👔 **職位**：{matched_emp.get('職位', 'Staff')}")
        else:
            st.error(L["emp_not_found"])

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. 輸入新密碼與確認密碼
        new_pwd = st.text_input(L["new_pwd_lbl"], type="password", placeholder="請輸入新密碼...")
        confirm_pwd = st.text_input(L["confirm_pwd_lbl"], type="password", placeholder="再次確認新密碼...")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
            if matched_emp and new_pwd and new_pwd == confirm_pwd:
                # 更新該員工密碼
                matched_emp["密碼"] = new_pwd
                matched_emp["must_change_password"] = True  # 強制下次登入需修改
                st.success(L["success"].format(name=matched_emp['姓名'], emp_id=matched_emp['工號']))
            else:
                st.error(L["error_match"])
