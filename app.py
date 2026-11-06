import streamlit as st
import importlib
from sqlalchemy import create_engine, text

# 設定網頁標題與佈局
st.set_page_config(
    page_title="裕豐電機工業 - SaaS ERP 戰情室",
    page_icon="🏭",
    layout="wide"
)

# 建立資料庫連線引擎
@st.cache_resource
def init_connection():
    try:
        database_url = st.secrets["SUPABASE_DB_URL"]
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.warning(f"⚠️ 資料庫連線初始化提示: {e}")
        return None

engine = init_connection()

# 從資料庫動態載入企業識別設定 (Logo & 公司名稱)
def get_app_branding(engine):
    branding = {
        "company_name": "裕豐電機工業 (Reetech Industrial) - SaaS ERP",
        "logo_url": "https://raw.githubusercontent.com/tabgshu-ux/RECH/main/assets/logo.png"
    }
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT setting_key, setting_value FROM sys_branding"), con=conn)
                if not df.empty:
                    for _, row in df.iterrows():
                        if row["setting_key"] in branding:
                            branding[row["setting_key"]] = row["setting_value"]
        except Exception:
            pass
    return branding

import pandas as pd
branding_info = get_app_branding(engine)

# 初始化使用者登入狀態
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "current_user_role" not in st.session_state:
    st.session_state.current_user_role = "Staff"

# ==================== 1. 登入畫面 (動態載入資料庫 Logo 與名稱) ====================
if not st.session_state.authenticated:
    # 完美使用資料庫配置的 Logo 圖片與公司名稱
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        try:
            st.image(branding_info["logo_url"], width=80)
        except Exception:
            st.write("🏭")
    with col_title:
        st.title(f"{branding_info['company_name']} - 系統登入中心")
    
    st.markdown("請輸入您的企業帳號與密碼以進入系統（具備 RBAC 內控權限控管與網頁全配置架構）。")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 系統身分驗證")
            username_input = st.text_input("使用者帳號 (Username)", placeholder="例如: admin 或 hr_manager")
            password_input = st.text_input("登入密碼 (Password)", type="password", placeholder="請輸入密碼")
            submit_login = st.form_submit_button("🚀 登入系統", type="primary")

            if submit_login:
                if username_input.strip() == "admin" and password_input.strip() == "Reech999808":
                    st.session_state.authenticated = True
                    st.session_state.current_user = "admin"
                    st.session_state.current_user_role = "Admin"
                    st.success("🎉 登入成功！正在進入系統...")
                    st.rerun()
                elif username_input.strip() == "hr_manager" and password_input.strip() == "hr123456":
                    st.session_state.authenticated = True
                    st.session_state.current_user = "人事主管"
                    st.session_state.current_user_role = "管理部主管"
                    st.success("🎉 登入成功（人事主管權限）！")
                    st.rerun()
                elif username_input.strip() == "staff" and password_input.strip() == "123456":
                    st.session_state.authenticated = True
                    st.session_state.current_user = "一般同仁"
                    st.session_state.current_user_role = "Staff"
                    st.success("🎉 登入成功（一般同仁權限）！")
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤，請重新輸入！")
    
    st.stop()

# ==================== 2. 已登入後的正式 ERP 主畫面 ====================

if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

curr_lang = st.sidebar.selectbox("選擇系統語系 / Select Language", ["繁體中文", "Tiếng Việt", "English"], index=0)
st.session_state.lang = curr_lang

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **當前使用者：{st.session_state.current_user}**")
st.sidebar.caption(f"身分權限：{st.session_state.current_user_role}")

if st.sidebar.button("🚪 登出系統"):
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.session_state.current_user_role = "Staff"
    st.success("已成功登出系統")
    st.rerun()

st.sidebar.markdown("---")

from modules.it_system.department_config import get_department_module_tree
department_tree = get_department_module_tree(engine)

department_names = list(department_tree.keys())

if st.session_state.current_user_role == "Admin":
    department_names.append("💻 系統設定 (System Settings)")

st.sidebar.subheader("選擇一級部門 / Chọn phòng ban :")
selected_dept = st.sidebar.radio("Department", department_names)

if selected_dept == "💻 系統設定 (System Settings)":
    try:
        from modules.it_system import department_config
        department_config.render(engine=engine, lang=curr_lang)
    except Exception as e:
        st.error(f"無法載入系統設定模組: {e}")

else:
    if "總經理室" in selected_dept:
        try:
            from modules import executive_dashboard
            executive_dashboard.render_executive_dashboard_page(engine=engine, lang=curr_lang)
        except Exception as e:
            st.error(f"載入總經理室模組發生錯誤: {e}")

    elif "管理部" in selected_dept:
        st.title("👔 管理部營運管理中心")
        st.caption("採手機優先與三大營運單位分組架構，兼顧內控與高效操作。")
        st.markdown("---")

        tab_hr, tab_fin, tab_GA = st.tabs([
            "👥 1. 人事與行政單位", 
            "💰 2. 財務與會計單位", 
            "🏢 3. 總務與廠務單位"
        ])

        with tab_hr:
            st.subheader("👥 人事與行政作業管理")
            hr_action = st.radio(
                "選擇人事行政功能", 
                ["📢 公司公告佈告欄", "👤 員工檔案管理", "⏰ 員工打卡紀錄", "💵 員工薪資與保險", "🔑 密碼修改"],
                horizontal=True,
                key="hr_sub_action"
            )
            st.markdown("---")
            if "公司公告" in hr_action:
                try:
                    from modules.management import company_announcements
                    company_announcements.show(engine=engine, lang=curr_lang)
                except Exception as e:
                    st.error(f"無法載入公告模組: {e}")
            elif "員工檔案" in hr_action:
                st.info("💡 [員工檔案模組] 正在載入資料庫對接介面...")
            else:
                st.info(f"正在執行：{hr_action} 的業務邏輯...")

        with tab_fin:
            st.subheader("💰 財務與會計作業管理")
            fin_action = st.radio(
                "選擇財務會計功能",
                ["📥 採購與應付帳款 (AP)", "📤 應收帳款管理 (AR)", "📊 越南稅務報表 (Thông tư 200)", "🧾 電子發票管理"],
                horizontal=True,
                key="fin_sub_action"
            )
            st.markdown("---")
            st.info(f"正在執行：{fin_action} 的會計與報表邏輯...")

        with tab_GA:
            st.subheader("🏢 總務與廠務後勤管理")
            ga_action = st.selectbox(
                "選擇總務廠務功能",
                ["宿舍與伙食管理", "工作廠區安全管理", "車輛進出口管制", "車輛維修保養紀錄", "固定資產盤點", "文件檔案管理"]
            )
            st.markdown("---")
            st.info(f"正在執行：{ga_action} 的後勤作業介面...")

    elif "工程與設計管理中心" in selected_dept:
        st.title("🛠️ 工程與設計管理中心")
        st.write("此處處理工程專案、場勘報價、BOM 與 FAT/SAT 驗收。")

    elif "生產部" in selected_dept:
        st.title("🏭 生產部製造戰情室 (西寧廠)")
        st.write("此處處理板金加工工單、粉體塗裝品管與配電盤組裝。")

    elif "倉庫管理" in selected_dept:
        st.title("📦 倉庫與供應鏈管理中心")

    elif "外勤工程打卡" in selected_dept:
        st.title("📍 現場外勤打卡與工作回報")

    elif "電子簽核中心" in selected_dept:
        st.title("✍️ 電子簽核與進度追蹤中心")

    else:
        st.title(f"📌 {selected_dept}")
