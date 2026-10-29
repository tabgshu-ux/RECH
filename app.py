import streamlit as st
import importlib

# 頁面基本設定
st.set_page_config(
    page_title="REETECH Vietnam SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 🔐 登入驗證模組 (Login Authentication)
# ----------------------------------------------------
def render_login_page():
    st.markdown("<h2 style='text-align: center;'>🏭 REETECH Vietnam SaaS ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>西寧廠企業資源規劃系統 - 請先登入帳號</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("👤 帳號 / Username", placeholder="請輸入帳號 (例如: admin)")
            password_input = st.text_input("🔑 密碼 / Password", type="password", placeholder="請輸入密碼")
            lang_choice = st.selectbox("🌐 語言 / Language", ["繁體中文", "Tiếng Việt", "English"])
            
            submit_login = st.form_submit_button("🚀 登入系統 / Login", type="primary", use_container_width=True)
            
            if submit_login:
                # 簡單驗證（實務上可串接資料庫 users 表格進行雜湊驗證）
                if username_input.strip() == "admin" and password_input == "admin123":
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = "admin"
                    st.session_state["user_role"] = "系統管理員"
                    st.session_state["lang"] = lang_choice
                    st.success("🎉 登入成功！正在進入系統...")
                    st.rerun()
                elif username_input.strip() != "" and password_input.strip() != "":
                    # 一般廠區同仁或主管帳號
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = username_input.strip()
                    st.session_state["user_role"] = "一般使用者 / 員工"
                    st.session_state["lang"] = lang_choice
                    st.success(f"🎉 歡迎 [{username_input}] 登入 REETECH ERP！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入正確的帳號與密碼！")

        st.info("💡 預設測試帳號：\n- 系統管理員: `admin` / `admin123` (可見 IT 資訊管理)\n- 一般同仁: 自行輸入姓名登入")

# ----------------------------------------------------
# 🏭 主系統介面 (Main App)
# ----------------------------------------------------
def main():
    # 檢查是否已登入
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        render_login_page()
        return

    # 已登入後的側邊欄選單
    current_user = st.session_state.get("current_user", "Guest")
    user_role = st.session_state.get("user_role", "員工")
    is_admin = (current_user.lower() == "admin")
    current_lang = st.session_state.get("lang", "繁體中文")

    st.sidebar.title("🏭 REETECH ERP 中樞")
    st.sidebar.markdown(f"👤 **使用者**: {current_user} (`{user_role}`)")
    
    if st.sidebar.button("🚪 登出系統 / Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.rerun()

    st.sidebar.markdown("---")

    # 依造您的要求排序的部門與核心功能選單
    departments_dict = {
        "繁體中文": [
            "📈 總經理室 (Executive Office)",
            "🛠️ 工程與設計管理中心 (Engineering & Design)",
            "👔 管理部 (Management Dept)",
            "🏭 生產部 (Production Dept)",
            "📦 倉庫管理 (Warehouse Management)",
            "📍 外勤工程打卡與即時人數 (Field Attendance)",
            "✍️ 全公司電子簽核中心 (Approval Center)"
        ],
        "Tiếng Việt": [
            "📈 Văn phòng Giám đốc (Executive Office)",
            "🛠️ Trung tâm Kỹ thuật & Thiết kế (Engineering)",
            "👔 Phòng Quản lý (Management Dept)",
            "📦 Quản lý Kho (Warehouse)",
            "📍 Chấm công & Vị trí hiện trường (Field Attendance)",
            "✍️ Trung tâm Phê duyệt điện tử (Approval Center)"
        ],
        "English": [
            "📈 Executive Office",
            "🛠️ Engineering & Design Center",
            "Management Dept",
            "Production Dept",
            "Warehouse Management",
            "Field Attendance & Headcount",
            "Electronic Approval Center"
        ]
    }

    it_menu_label = {
        "繁體中文": "💻 資訊管理部 (IT System - Admin Only)",
        "Tiếng Việt": "💻 Quản lý CNTT (IT System - Admin Only)",
        "English": "💻 IT System (Admin Only)"
    }

    menu_list = list(departments_dict.get(current_lang, departments_dict["繁體中文"]))
    
    # 只有 Admin 才能看到資訊管理部
    if is_admin:
        menu_list.append(it_menu_label.get(current_lang, it_menu_label["繁體中文"]))

    selected_dept = st.sidebar.radio("📌 選擇部門與功能 / Select Module", menu_list)
    st.sidebar.markdown("---")
    
    engine = st.session_state.get("db_engine", None)

    # 路由分發
    try:
        if "資訊管理部" in selected_dept or "Quản lý CNTT" in selected_dept or "IT System" in selected_dept:
            if is_admin:
                mod = importlib.import_module("modules.it_system.main")
                if hasattr(mod, "show"):
                    mod.show(engine=engine, lang=current_lang)
                elif hasattr(mod, "main"):
                    mod.main(engine=engine, lang=current_lang)
            else:
                st.error("🚫 權限不足：資訊管理部僅限系統 Admin 人員存取！")

        elif "總經理室" in selected_dept or "Văn phòng Giám đốc" in selected_dept or "Executive Office" in selected_dept:
            st.markdown("### 📈 總經理室戰情與顧問中心")
            st.info("💡 高階經營戰情室、Gemini 採購顧問與越南法規動態載入中...")

        elif "工程" in selected_dept or "Kỹ thuật" in selected_dept or "Engineering" in selected_dept:
            st.markdown("### 🛠️ 工程與設計管理中心")
            st.info("💡 工程主管戰情室、專案報價、BOM 零件與驗收模組載入中...")

        elif "管理部" in selected_dept or "Quản lý" in selected_dept or "Management" in selected_dept:
            mod = importlib.import_module("modules.management.main")
            if hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)
            elif hasattr(mod, "main"):
                mod.main(engine=engine, lang=current_lang)

        elif "外勤" in selected_dept or "Chấm công" in selected_dept or "Field Attendance" in selected_dept:
            mod = importlib.import_module("modules.management.hr.field_gps_attendance")
            if hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)
            elif hasattr(mod, "render_field_attendance_page"):
                mod.render_field_attendance_page(engine=engine, lang=current_lang)

        else:
            st.info(f"💡 目前選定的模組 [{selected_dept}] 正在準備中...")

    except Exception as e:
        st.error(f"⚠️ 載入模組發生異常: {str(e)}")

if __name__ == "__main__":
    main()
