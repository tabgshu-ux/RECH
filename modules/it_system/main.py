import streamlit as st
import importlib

def render_it_system_module(engine=None, lang="繁體中文", **kwargs):
    sub_menus = {
        "繁體中文": [
            "🏢 1. 獨立企業部門與模組拼圖 (Department Config)",
            "⚙️ 2. 組織角色與權限指派 (RBAC)",
            "🔌 3. 資料庫與 API 串聯設定 (DB Bridge)",
            "📊 4. 系統稽核日誌與安全監控 (Audit Logs)"
        ],
        "Tiếng Việt": [
            "🏢 1. Cài đặt phòng ban & Module",
            "⚙️ 2. Phân quyền vai trò (RBAC)",
            "🔌 3. Kết nối CSDL & API",
            "📊 4. Nhật ký kiểm toán"
        ],
        "English": [
            "🏢 1. Department Configuration",
            "⚙️ 2. Roles & RBAC",
            "🔌 3. Database Bridge & API",
            "📊 4. System Audit Logs"
        ]
    }

    current_lang = lang if lang in sub_menus else "繁體中文"
    menu_list = sub_menus[current_lang]

    selected_sub = st.selectbox("📌 選擇 IT 資訊管理子模組 / Select IT Module", menu_list, key="it_system_sub_select")
    st.markdown("---")

    try:
        if "獨立企業部門" in selected_sub or "Department" in selected_sub or "phòng ban" in selected_sub.lower():
            mod = importlib.import_module("modules.it_system.department_config")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "組織角色" in selected_sub or "RBAC" in selected_sub or "Phân quyền" in selected_sub or "Roles" in selected_sub:
            mod = importlib.import_module("modules.it_system.role_rbac")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "資料庫" in selected_sub or "Database" in selected_sub or "CSDL" in selected_sub:
            mod = importlib.import_module("modules.it_system.db_bridge")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        elif "稽核日誌" in selected_sub or "Audit" in selected_sub or "Kiểm toán" in selected_sub:
            mod = importlib.import_module("modules.it_system.audit_logs")
            if hasattr(mod, "render"):
                mod.render(engine=engine, lang=current_lang)

        else:
            st.info(f"💡 目前選定的 IT 模組 [{selected_sub}] 正在載入中...")
            
    except Exception as e:
        st.error(f"⚠️ 載入 IT 資訊管理子模組發生異常: {str(e)}")

def show(engine=None, lang="繁體中文", **kwargs):
    render_it_system_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_it_system_module(engine=engine, lang=lang, **kwargs)
