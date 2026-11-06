# ==========================================
# 檔案路徑：app.py
# 職責：裕豐 SaaS ERP 統一入口與模組動態路由（對齊真實資料夾結構）
# ==========================================

import streamlit as st

st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 狀態初始化
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'
if 'selected_module' not in st.session_state:
    st.session_state['selected_module'] = 'hr_employee'
if 'current_lang' not in st.session_state:
    st.session_state['current_lang'] = 'zh'

# 簡易登入驗證（可依需求對接資料庫）
if not st.session_state['logged_in']:
    st.title("🏭 裕豐電機工業 (Reetech Industrial) - 系統登入")
    with st.form("login_form"):
        username = st.text_input("使用者帳號", value="admin")
        password = st.text_input("登入密碼", type="password", value="Reech999808")
        submit = st.form_submit_button("🚀 登入系統", type="primary")
        if submit:
            if username == "admin" and password == "Reech999808":
                st.session_state['logged_in'] = True
                st.session_state['user_name'] = "Admin"
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤！")
    st.stop()

# 頂部導覽列
col_title, col_user, col_logout = st.columns([6, 2, 2])
with col_title:
    st.subheader("🏭 裕豐電機工業 SaaS ERP 營運戰情室")
with col_user:
    st.caption(f"👤 當前使用者：{st.session_state['user_name']}")
with col_logout:
    if st.button("🚪 登出系統", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

st.divider()

# 側邊欄選單（直接對接您真實的資料夾模組）
st.sidebar.markdown("### 🏢 企業模組導覽選單")
lang = st.sidebar.selectbox("系統語系 / Language", ["繁體中文", "Tiếng Việt", "English"])
st.session_state['current_lang'] = 'zh' if lang == "繁體中文" else ('vi' if lang == "Tiếng Việt" else 'en')

st.sidebar.markdown("---")
st.sidebar.markdown("#### 👥 管理部 - 人事與出勤")

menu_choice = st.sidebar.radio(
    "選擇功能模組",
    [
        "📋 員工名冊 (employee_list)",
        "👤 員工檔案與合約 (employee_profile)",
        "🌏 外派人員管理 (add_expat)",
        "📍 外勤 GPS 打卡 (field_gps_attendance)",
        "⏰ 廠內出勤紀錄 (internal_attendance)",
        "📝 請假紀錄管理 (leave_records)",
        "⚙️ 系統與 IT 設定 (it_system)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("裕豐電機工業內部管理系統 v4.0")

# 路由分發：根據選擇載入對應的真實模組檔案
if "員工名冊" in menu_choice:
    try:
        from modules.management.hr.employee import employee_list
        employee_list.show()
    except Exception as e:
        st.error(f"載入員工名冊模組發生錯誤: {e}")

elif "員工檔案" in menu_choice:
    try:
        from modules.management.hr.employee import employee_profile
        employee_profile.show()
    except Exception as e:
        st.error(f"載入員工檔案模組發生錯誤: {e}")

elif "外派人員" in menu_choice:
    try:
        from modules.management.hr.employee import add_expat
        add_expat.show()
    except Exception as e:
        st.error(f"載入外派人員模組發生錯誤: {e}")

elif "外勤 GPS" in menu_choice:
    try:
        from modules.management.hr.attendance import field_gps_attendance
        field_gps_attendance.show()
    except Exception as e:
        st.error(f"載入外勤打卡模組發生錯誤: {e}")

elif "廠內出勤" in menu_choice:
    try:
        from modules.management.hr.attendance import internal_attendance
        internal_attendance.show()
    except Exception as e:
        st.error(f"載入廠內出勤模組發生錯誤: {e}")

elif "請假紀錄" in menu_choice:
    try:
        from modules.management.hr.attendance import leave_records
        leave_records.show()
    except Exception as e:
        st.error(f"載入請假紀錄模組發生錯誤: {e}")

elif "系統與 IT" in menu_choice:
    try:
        from modules.it_system import admin_settings
        admin_settings.render(None, st.session_state['current_lang'])
    except Exception as e:
        st.error(f"載入系統設定模組發生錯誤: {e}")
