import streamlit as st
import importlib
from sqlalchemy import create_engine, text

# 設定網頁標題與佈局
st.set_page_config(
    page_title="裕豐電機工業 - SaaS ERP 戰情室",
    page_icon="🏭",
    layout="wide"
)

# 建立資料庫連線引擎 (精準對應您 Secrets 中的 SUPABASE_DB_URL)
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

# 語系與基本狀態初始化
if "lang" not in st.session_state:
    st.session_state.lang = "繁體中文"

curr_lang = st.sidebar.selectbox("選擇系統語系 / Select Language", ["繁體中文", "Tiếng Việt", "English"], index=0)
st.session_state.lang = curr_lang

# 模擬登入使用者狀態 (Admin)
if "current_user_role" not in st.session_state:
    st.session_state.current_user_role = "Admin"

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **當前使用者：admin**")
st.sidebar.caption(f"身分權限：{st.session_state.current_user_role}")

if st.sidebar.button("🚪 登出系統"):
    st.success("已成功登出系統")

st.sidebar.markdown("---")

# 引入正式部門樹狀結構
from modules.it_system.department_config import get_department_module_tree
department_tree = get_department_module_tree(engine)

# 建立動態側邊欄選項清單
department_names = list(department_tree.keys())

# 只有當登入者身分為 Admin 時，才將「💻 系統設定 (System Settings)」加入選單中
if st.session_state.current_user_role == "Admin":
    department_names.append("💻 系統設定 (System Settings)")

st.sidebar.subheader("選擇一級部門 / Chọn phòng ban :")
selected_dept = st.sidebar.radio("Department", department_names)

# 判斷使用者選擇的是否為「系統設定」
if selected_dept == "💻 系統設定 (System Settings)":
    try:
        from modules.it_system import department_config
        department_config.render(engine=engine, lang=curr_lang)
    except Exception as e:
        st.error(f"無法載入系統設定模組: {e}")

else:
    # 取得該正式部門底下的子功能模組列表
    sub_modules = department_tree.get(selected_dept, [])

    st.sidebar.markdown("---")
    st.sidebar.subheader("選擇子部門與功能 / Chọn chức năng :")
    selected_sub_mod = st.sidebar.radio("Sub-module", sub_modules)

    # 根據一級部門與子功能進行動態路由分發
    if "總經理室" in selected_dept:
        try:
            from modules import executive_dashboard
            executive_dashboard.render_executive_dashboard_page(engine=engine, lang=curr_lang)
        except Exception as e:
            st.error(f"載入總經理室模組發生錯誤: {e}")

    elif "管理部" in selected_dept:
        st.title("👔 管理部營運管理中心")
        st.info(f"當前選定功能：{selected_sub_mod}")
        
        if "公司公告" in selected_sub_mod:
            try:
                from modules.management import company_announcements
                company_announcements.show(engine=engine, lang=curr_lang)
            except Exception as e:
                st.error(f"無法載入公司公告模組: {e}")
                
        elif "員工檔案" in selected_sub_mod:
            try:
                from modules.management import employee_profile
                employee_profile.show(engine=engine, lang=curr_lang)
            except Exception as e:
                st.info("💡 員工檔案模組正在進行資料庫對接...")
                st.write(f"正在執行：{selected_sub_mod} 的業務邏輯與表單介面...")
        else:
            st.write(f"正在執行：{selected_sub_mod} 的業務邏輯與表單介面...")

    elif "工程與設計管理中心" in selected_dept:
        st.title("🛠️ 工程與設計管理中心")
        st.info(f"當前選定功能：{selected_sub_mod}")
        st.write("此處處理工程專案、場勘報價、BOM 與 FAT/SAT 驗收。")

    elif "生產部" in selected_dept:
        st.title("🏭 生產部製造戰情室 (西寧廠)")
        st.info(f"當前選定功能：{selected_sub_mod}")
        st.write("此處處理板金加工工單、粉體塗裝品管與配電盤組裝。")

    elif "倉庫管理" in selected_dept:
        st.title("📦 倉庫與供應鏈管理中心")
        st.info(f"當前選定功能：{selected_sub_mod}")

    elif "外勤工程打卡" in selected_dept:
        st.title("📍 現場外勤打卡與工作回報")
        st.info("手機端極簡打卡與施工日報表填報。")

    elif "電子簽核中心" in selected_dept:
        st.title("✍️ 電子簽核與進度追蹤中心")
        st.info("請假、採購與各項流程簽核。")

    else:
        st.title(f"📌 {selected_dept}")
        st.info(f"目前選定功能：{selected_sub_mod}")
