import streamlit as st
import importlib

# 頁面基本設定
st.set_page_config(
    page_title="REETECH Vietnam SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("🏭 REETECH ERP 中樞選單")
    
    # 語言選擇
    lang = st.sidebar.selectbox("🌐 語言 / Language / Ngôn ngữ", ["繁體中文", "Tiếng Việt", "English"])

    # 模擬取得當前登入者身份（實務上可從 st.session_state 取得，若為 admin 才能看到 IT 系統）
    current_user = st.session_state.get("current_user", "admin")  # 預設測試用，可改為實際登入帳號
    is_admin = (current_user.lower() == "admin")

    # 依造您的要求重新排序的部門與核心功能選單
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
            "🏭 Bộ phận Sản xuất (Production Dept)",
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

    # 如果是 admin，才在選單最下方加入「資訊管理 IT」
    it_menu_label = {
        "繁體中文": "💻 資訊管理部 (IT System - Admin Only)",
        "Tiếng Việt": "💻 Quản lý CNTT (IT System - Admin Only)",
        "English": "💻 IT System (Admin Only)"
    }

    current_lang = lang if lang in departments_dict else "繁體中文"
    menu_list = list(departments_dict[current_lang])
    
    if is_admin:
        menu_list.append(it_menu_label[current_lang])

    selected_dept = st.sidebar.radio("📌 選擇部門與功能 / Select Module", menu_list)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"👤 當前登入: {current_user} | 權限: {'Admin 授權'}")
    
    # 模擬資料庫引擎
    engine = st.session_state.get("db_engine", None)

    # 路由分發與掛載
    try:
        # 1. 資訊管理部 (僅限 admin)
        if "資訊管理部" in selected_dept or "Quản lý CNTT" in selected_dept or "IT System" in selected_dept:
            if is_admin:
                mod = importlib.import_module("modules.it_system.main")
                if hasattr(mod, "show"):
                    mod.show(engine=engine, lang=current_lang)
                elif hasattr(mod, "main"):
                    mod.main(engine=engine, lang=current_lang)
            else:
                st.error("🚫 權限不足：資訊管理部僅限系統 Admin 人員存取與設定！")

        # 2. 總經理室
        elif "總經理室" in selected_dept or "Văn phòng Giám đốc" in selected_dept or "Executive Office" in selected_dept:
            st.markdown("### 📈 總經理室戰情與顧問中心")
            st.info("💡 正在載入高階經營戰情室、Gemini 採購顧問與越南法規動態...")

        # 3. 工程與設計管理中心
        elif "工程" in selected_dept or "Kỹ thuật" in selected_dept or "Engineering" in selected_dept:
            st.markdown("### 🛠️ 工程與設計管理中心")
            st.info("💡 正在載入工程主管戰情室、專案報價、BOM 零件與驗收模組...")

        # 4. 管理部
        elif "管理部" in selected_dept or "Quản lý" in selected_dept or "Management" in selected_dept:
            mod = importlib.import_module("modules.management.main")
            if hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)
            elif hasattr(mod, "main"):
                mod.main(engine=engine, lang=current_lang)

        # 5. 外勤工程打卡
        elif "外勤" in selected_dept or "Chấm công" in selected_dept or "Field Attendance" in selected_dept:
            mod = importlib.import_module("modules.management.hr.field_gps_attendance")
            if hasattr(mod, "show"):
                mod.show(engine=engine, lang=current_lang)
            elif hasattr(mod, "render_field_attendance_page"):
                mod.render_field_attendance_page(engine=engine, lang=current_lang)

        else:
            st.info(f"💡 目前選定的模組 [{selected_dept}] 正在準備中，即將完成掛載！")

    except Exception as e:
        st.error(f"⚠️ 載入模組發生異常: {str(e)}")

if __name__ == "__main__":
    main()
