import streamlit as st

PASSWORD_I18N = {
    "繁體中文": {
        "title": "🔑 管理部 - 員工密碼重設與授權管理",
        "caption": "由管理部與人事主管協助廠內同仁安全重設密碼與派發初始密碼。",
        "select_emp": "🎯 請選擇或搜尋欲重設密碼的員工 *",
        "new_pwd_lbl": "輸入新密碼 (New Password) *",
        "confirm_pwd_lbl": "再次確認新密碼 (Confirm Password) *",
        "btn_save": "💾 確認替此員工重設密碼",
        "success": "🎉 已成功幫員工 【{name} ({emp_id})】 更新密碼！",
        "error_match": "⚠️ 兩次輸入的新密碼不相符，請重新檢查！"
    },
    "Tiếng Việt": {
        "title": "🔑 Phòng Quản lý - Đặt lại mật khẩu nhân viên",
        "caption": "Phòng Quản lý và nhân sự hỗ trợ nhân viên đặt lại mật khẩu an toàn.",
        "select_emp": "🎯 Chọn nhân viên cần đặt lại mật khẩu *",
        "new_pwd_lbl": "Nhập mật khẩu mới *",
        "confirm_pwd_lbl": "Nhập lại mật khẩu mới *",
        "btn_save": "💾 Xác nhận đặt lại mật khẩu",
        "success": "🎉 Đã cập nhật mật khẩu thành công cho nhân viên 【{name} ({emp_id})】!",
        "error_match": "⚠️ Mật khẩu không khớp, vui lòng kiểm tra lại!"
    },
    "English": {
        "title": "🔑 Management Dept - Employee Password Reset",
        "caption": "HR and Management department assistance for secure password resets.",
        "select_emp": "🎯 Select Employee to Reset Password *",
        "new_pwd_lbl": "New Password *",
        "confirm_pwd_lbl": "Confirm New Password *",
        "btn_save": "💾 Confirm Password Reset",
        "success": "🎉 Successfully reset password for employee 【{name} ({emp_id})】!",
        "error_match": "⚠️ Passwords do not match!"
    }
}

def render_change_password_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in PASSWORD_I18N else "繁體中文"
    L = PASSWORD_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")

    # 取得現有的員工清單資料庫
    if "employee_db" not in st.session_state or not st.session_state.employee_db:
        st.warning("⚠️ 目前系統中尚無員工檔案，請先至【管理部 > 員工檔案】建立員工資料。")
        return

    emp_list = st.session_state.employee_db
    
    # 組合下拉選單格式：「姓名 (工號 - 職位)」讓管理者一眼看出是誰
    emp_options = {f"{emp['姓名']} ({emp['工號']} - {emp.get('職位', 'Staff')})": emp for emp in emp_list}
    
    selected_emp_key = st.selectbox(L["select_emp"], options=list(emp_options.keys()))
    target_emp = emp_options[selected_emp_key]

    st.info(f"📌 目前選定對象：**{target_emp['姓名']}** | 工號：`{target_emp['工號']}` | 部門：{target_emp.get('部門', '未分發')} | 現有角色：`{target_emp.get('角色', 'Staff')}`")

    with st.form("admin_reset_password_form"):
        new_pwd = st.text_input(L["new_pwd_lbl"], type="password", placeholder="請輸入新密碼...")
        confirm_pwd = st.text_input(L["confirm_pwd_lbl"], type="password", placeholder="再次確認新密碼...")

        if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
            if new_pwd and new_pwd == confirm_pwd:
                # 更新該員工的密碼
                target_emp["密碼"] = new_pwd
                target_emp["must_change_password"] = True  # 強制規定該員工下次登入時必須再次變更以策安全
                
                st.success(L["success"].format(name=target_emp['姓名'], emp_id=target_emp['工號']))
            else:
                st.error(L["error_match"])
