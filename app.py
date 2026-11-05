import streamlit as st
import pandas as pd
import importlib
from sqlalchemy import create_engine, text

# ----------------------------------------------------
# 0. 頁面全域設定與多語系偵測引擎 (Client-side Locale & Metadata UI)
# ----------------------------------------------------
st.set_page_config(
    page_title="RECH 裕豐電機工業 SaaS ERP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化語系與租戶環境
if "current_lang" not in st.session_state:
    st.session_state.current_lang = "Tiếng Việt"  # 預設以越南現場員工母語優先
if "tenant_id" not in st.session_state:
    st.session_state.tenant_id = "REETECH_VN"

curr_lang = st.session_state.current_lang

# 多語系介面字典 (Localization Dictionary)
TEXTS = {
    "繁體中文": {
        "title": "⚡ 裕豐電機工業 SaaS 系統",
        "lang_label": "🌐 選擇系統語系 / Select Language",
        "dept_select": "請選擇一級部門 / Chọn phòng ban",
        "login_title": "⚡ 裕豐電機工業系統登入",
        "account": "帳號 (工號)",
        "password": "密碼",
        "login_btn": "🔑 登入系統",
        "logout_btn": "登出系統",
        "welcome": "歡迎登入",
        "notice_title": "【公司佈告欄】 關於越南全國連假與西寧廠安全生產之重要通知"
    },
    "Tiếng Việt": {
        "title": "⚡ RECH - Hệ thống Quản trị Doanh nghiệp",
        "lang_label": "🌐 Chọn ngôn ngữ / Language",
        "dept_select": "Chọn phòng ban / Department",
        "login_title": "⚡ Đăng nhập hệ thống REETECH",
        "account": "Tài khoản (Mã nhân viên)",
        "password": "Mật khẩu",
        "login_btn": "🔑 Đăng nhập",
        "logout_btn": "Đăng xuất",
        "welcome": "Xin chào",
        "notice_title": "[BẢNG THÔNG BÁO] Về kỳ nghỉ lễ quốc gia và an toàn sản xuất tại nhà máy Tây Ninh"
    },
    "English": {
        "title": "⚡ RECH Industrial ERP System",
        "lang_label": "🌐 Select Language",
        "dept_select": "Select Department",
        "login_title": "⚡ REETECH Industrial System Login",
        "account": "Account (Emp ID)",
        "password": "Password",
        "login_btn": "🔑 Login",
        "logout_btn": "Logout",
        "welcome": "Welcome",
        "notice_title": "[Company Notice] Important announcement regarding national holidays and safety"
    }
}

t = TEXTS.get(curr_lang, TEXTS["繁體中文"])

# ----------------------------------------------------
# 1. 資料庫連線引擎初始化 (Supabase PostgreSQL)
# ----------------------------------------------------
@st.cache_resource
def init_db_engine():
    try:
        db_url = st.secrets.get("SUPABASE_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
        return create_engine(db_url, pool_pre_ping=True)
    except Exception as e:
        print(f"資料庫連線初始化失敗: {e}")
        return None

engine = init_db_engine()

# ----------------------------------------------------
# 2. 安全模組載入器 (Safe Module Loader - 支援鬆耦合與動態加載)
# ----------------------------------------------------
def load_module_safely(module_path, function_name="show", **kwargs):
    try:
        mod = importlib.import_module(module_path)
        importlib.reload(mod) # 確保開發時即時熱更新
        if hasattr(mod, function_name):
            func = getattr(mod, function_name)
            func(**kwargs)
        else:
            st.error(f"⚠️ 模組 `{module_path}` 中找不到方法 `{function_name}`。")
    except Exception as e:
        st.error(f"⚠️ 載入模組 `{module_path}` 發生異常：{str(e)}")

# ----------------------------------------------------
# 3. 登入認證狀態管理 (Authentication State)
# ----------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown(f"<h2 style='text-align: center;'>{t['login_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>REETECH INDUSTRIAL Co., Ltd.</p>", unsafe_allow_html=True)
        
        # 語系切換
        selected_lang = st.selectbox(t['lang_label'], ["繁體中文", "Tiếng Việt", "English"], index=["繁體中文", "Tiếng Việt", "English"].index(curr_lang))
        if selected_lang != curr_lang:
            st.session_state.current_lang = selected_lang
            st.rerun()

        with st.form("login_form"):
            username = st.text_input(t['account'], value="admin")
            password = st.text_input(t['password'], type="password", value="123")
            submitted = st.form_submit_button(t['login_btn'], use_container_width=True)
            if submitted:
                if username == "admin" and password == "123":
                    st.session_state.authenticated = True
                    st.session_state.username = "admin (ADMIN)"
                    st.success("登入成功！")
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤！ (預設 admin / 123)")
    st.stop()

# ----------------------------------------------------
# 4. 主系統介面與側邊欄導航 (Main Application & Sidebar)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### RECH 裕豐電機工業")
    st.caption("CÔNG TY TNHH CN DỮ PHONG")
    
    # 側邊欄語系即時切換
    new_lang = st.selectbox(t['lang_label'], ["繁體中文", "Tiếng Việt", "English"], index=["繁體中文", "Tiếng Việt", "English"].index(curr_lang))
    if new_lang != curr_lang:
        st.session_state.current_lang = new_lang
        st.rerun()

    st.markdown(f"👤 {st.session_state.username}")
    if st.button(t['logout_btn'], use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")
    st.markdown(f"**{t['dept_select']}**")

    # 企業級動態部門導航（符合用戶嚴格順序要求：總經理室置頂）
    dept_options = [
        "📈 總經理室 (Executive Office)",
        "👔 管理部 (Management Dept)",
        "🛠️ 工程與設計管理中心 (Engineering & Design Center)",
        "🏭 生產部 (Production Dept)",
        "📦 倉庫管理 (Warehouse Management)",
        "📍 外勤工程打卡與工作回報 (Field Attendance)",
        "✍️ 電子簽核中心 (Approval Center)",
        "💻 系統設定 (System Settings)"
    ]
    
    selected_dept = st.radio("Department Navigation", dept_options, label_visibility="collapsed")

# ----------------------------------------------------
# 5. 公告欄 (Top Notification Banner)
# ----------------------------------------------------
st.markdown(f"""
> 📢 **{t['notice_title']}**（發布單位：總經理室 / 董事長辦公室 | 日期：2026-10-09）  
> 請各部門主管務必於連假前落實廠區斷電巡檢、消防設備盤點，並確保留守人員通訊暢通。
""")
st.markdown("---")

# ----------------------------------------------------
# 6. 動態路由分發引擎 (Dynamic Routing Dispatcher)
# ----------------------------------------------------
if "總經理室" in selected_dept:
    sub_exec_choice = st.selectbox("📌 選擇總經理室子功能", ["📊 原料價格與匯率戰情室", "💰 財務與損益類", "📈 專案進度與異常監控", "🇻🇳 越南政策與法規"])
    if "原料價格" in sub_exec_choice:
        load_module_safely("modules.executive.commodities_fx", "show", engine=engine, lang=curr_lang)
    elif "財務" in sub_exec_choice:
        load_module_safely("modules.executive.financials_pl", "show", engine=engine, lang=curr_lang)
    elif "專案進度" in sub_exec_choice:
        load_module_safely("modules.executive.project_progress", "show", engine=engine, lang=curr_lang)
    elif "政策" in sub_exec_choice:
        load_module_safely("modules.executive.vietnam_policy", "show", engine=engine, lang=curr_lang)
    else:
        load_module_safely("modules.executive.commodities_fx", "show", engine=engine, lang=curr_lang)

elif "管理部" in selected_dept:
    load_module_safely("modules.management_dept", "show", engine=engine, lang=curr_lang)

elif "工程與設計管理中心" in selected_dept:
    load_module_safely("modules.engineering_center", "show", engine=engine, lang=curr_lang)

elif "生產部" in selected_dept:
    load_module_safely("modules.production_dept", "show", engine=engine, lang=curr_lang)

elif "倉庫管理" in selected_dept:
    load_module_safely("modules.warehouse_dept", "show", engine=engine, lang=curr_lang)

elif "外勤工程打卡" in selected_dept:
    load_module_safely("modules.field_attendance", "show", engine=engine, lang=curr_lang)

elif "電子簽核中心" in selected_dept:
    load_module_safely("modules.approval_center", "show", engine=engine, lang=curr_lang)

elif "系統設定" in selected_dept:
    # 呼叫我們剛剛升級、支援智慧自動掛載的系統設定模組
    load_module_safely("modules.it_system.department_config", "render", engine=engine, lang=curr_lang)
