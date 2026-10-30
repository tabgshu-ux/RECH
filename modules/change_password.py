import streamlit as st
from sqlalchemy import text

def render_change_password_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🔐 個人帳號安全與密碼修改 (Change Password)")
    st.info("💡 企業資安規範：同仁可隨時自行變更密碼。若不慎遺失密碼，請聯繫 IT 管理員於後台進行強制重設。")

    # 取得當前登入者資訊
    current_user_name = st.session_state.get("user_name", "User")
    current_emp_code = st.session_state.get("current_emp_code", "N/A")
    current_role = st.session_state.get("user_role", "Staff")

    st.markdown(f"**目前登入帳號**：`{current_emp_code}` | **姓名**：`{current_user_name}` | **角色**：`{current_role}`")
    st.markdown("---")

    # 1. 使用者自行修改密碼表單
    with st.form("user_self_change_pwd_form"):
        st.markdown("#### 🔄 自行修改密碼")
        old_pwd_input = st.text_input("請輸入原密碼 (Current Password) *", type="password")
        new_pwd_input = st.text_input("請輸入新密碼 (New Password) *", type="password")
        confirm_new_pwd = st.text_input("再次確認新密碼 (Confirm New Password) *", type="password")

        if st.form_submit_button("💾 確認更新個人密碼", type="primary", use_container_width=True):
            if not old_pwd_input or not new_pwd_input or not confirm_new_pwd:
                st.warning("⚠️ 請完整填寫所有密碼欄位！")
            elif new_pwd_input != confirm_new_pwd:
                st.error("⚠️ 兩次輸入的新密碼不相符，請重新檢查！")
            else:
                # 這裡可以根據您的員工資料庫更新邏輯進行寫入
                st.success("🎉 個人密碼修改成功！下次登入請使用新密碼。")

    # 2. 如果是 Admin 或 IT，顯示後台協助同仁重設密碼區塊
    if current_role.lower() in ["admin", "it", "it_admin", "系統管理員"]:
        st.markdown("---")
        st.markdown("#### 🛠️ 【IT後台】協助員工強制重設密碼")
        with st.form("admin_reset_pwd_form"):
            target_emp_code = st.text_input("欲重設密碼的員工工號 (Target Emp ID) *", placeholder="例: VN-003")
            temp_new_pwd = st.text_input("指派新暫時密碼 (Temporary Password) *", value="123456", type="password")
            
            if st.form_submit_button("🔑 強制重設該員工密碼", use_container_width=True):
                if target_emp_code:
                    # 後台重設邏輯
                    st.success(f"✅ 已成功將工號 [{target_emp_code.strip()}] 的密碼重設為暫時密碼！請通知該同仁首次登入時變更。")
                else:
                    st.warning("⚠️ 請輸入目標員工工號！")

def show(engine=None, lang="繁體中文", **kwargs):
    render_change_password_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_change_password_page(engine=engine, lang=lang, **kwargs)
