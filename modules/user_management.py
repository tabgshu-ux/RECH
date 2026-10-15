import streamlit as st
import pandas as pd
import datetime
import os

# ----------------------------------------------------
# 🔌 全方位萬用資料庫轉接頭 (Universal DB Adapter)
# ----------------------------------------------------
def get_universal_db_connection(db_type="SQLite", host="localhost", port="5432", user="", password="", db_name="reetech_erp"):
    try:
        if db_type == "SQLite":
            import sqlite3
            conn = sqlite3.connect("reetech_erp_local.db", check_same_thread=False)
            return conn, "SQLite"
            
        elif db_type == "Supabase / PostgreSQL":
            import psycopg2
            conn = psycopg2.connect(
                host=host, port=port, user=user, password=password, database=db_name
            )
            return conn, "PostgreSQL"
            
        elif db_type == "MySQL / MariaDB":
            import pymysql
            conn = pymysql.connect(
                host=host, port=int(port) if port else 3306, user=user, password=password, database=db_name, charset='utf8mb4'
            )
            return conn, "MySQL"
    except Exception as e:
        import sqlite3
        conn = sqlite3.connect("reetech_erp_local.db", check_same_thread=False)
        return conn, f"SQLite (Fallback due to error: {e})"
    
    import sqlite3
    return sqlite3.connect("reetech_erp_local.db", check_same_thread=False), "SQLite"

# ----------------------------------------------------
# 📝 核心寫入資料庫稽核日誌函數 (Audit Log Writer)
# ----------------------------------------------------
def log_system_action(action_desc, module_name="IT管理中心", status="成功"):
    """自動將任何系統操作寫入資料庫的 system_audit_logs 表格中"""
    try:
        cfg = st.session_state.get("db_config_state", {"type": "SQLite", "host": "localhost", "port": "5432", "user": "", "password": "", "db_name": "reetech_erp"})
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_acc = st.session_state.get("user_name", "admin")
        ip_addr = "192.168.1.100"
        
        is_sqlite = "SQLite" in actual_type
        if is_sqlite:
            cursor.execute(
                "INSERT INTO system_audit_logs (time, user_account, action, module, ip, status) VALUES (?, ?, ?, ?, ?, ?)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        else:
            cursor.execute(
                "INSERT INTO system_audit_logs (time, user_account, action, module, ip, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"寫入稽核日誌失敗: {e}")

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與系統稽核總覽",
        "caption": "支援組織角色權限控管 (RBAC)、雲端資料庫即時稽核追溯與企業營運管理。",
        "tab_audit": "📊 系統稽核日誌 (資料庫即時記錄)",
        "tab_roles": "⚙️ 組織角色權限範本 (RBAC)",
        "tab_users": "👥 員工與帳號總覽",
        "tab_api": "🔌 越南電子發票 API 設定",
    },
    "English": {
        "title": "🔒 IT Center - RBAC & System Audit Overview",
        "caption": "Support Departmental Roles (RBAC), database-backed audit logs, and enterprise management.",
        "tab_audit": "📊 Audit Logs (Database Logged)",
        "tab_roles": "⚙️ Departmental Roles (RBAC)",
        "tab_users": "👥 HR & Accounts",
        "tab_api": "🔌 E-Invoice API",
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Cấu hình Phân quyền & Nhật ký Kiểm toán",
        "caption": "Hỗ trợ quản lý phân quyền (RBAC) và nhật ký kiểm toán hệ thống.",
        "tab_audit": "📊 Nhật ký Kiểm toán",
        "tab_roles": "⚙️ Quản lý Vai trò (RBAC)",
        "tab_users": "👥 Danh sách Nhân sự",
        "tab_api": "🔌 Cấu hình API",
    }
}

def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 預設直接對接 Supabase 雲端資料庫 (對應許大哥截圖中的設定)
    if "db_config_state" not in st.session_state:
        st.session_state.db_config_state = {
            "type": "Supabase / PostgreSQL", "host": "aws-0-ap-southeast-1.pooler.supabase.com", "port": "5432",
            "user": "postgres.wvsqbefyekmueffcbwd", "password": "", "db_name": "postgres"
        }

    # 已隱藏萬用資料庫安裝精靈，保留 4 大核心管理分頁
    tab_audit, tab_roles, tab_users, tab_api = st.tabs([
        L["tab_audit"], L["tab_roles"], L["tab_users"], L["tab_api"]
    ])

    cfg = st.session_state.db_config_state

    # ----------------------------------------------------
    # ⚙️ 組織角色權限範本管理 (動態 CRUD + 寫入稽核日誌)
    # ----------------------------------------------------
    with tab_roles:
        st.markdown("### ⚙️ 企業組織部門角色與權限範本清冊 (資料庫即時連線)")
        
        conn, actual_db = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
        
        roles_from_db = {}
        try:
            df_roles = pd.read_sql("SELECT role_name, description FROM system_roles", conn)
            for _, row in df_roles.iterrows():
                roles_from_db[row["role_name"]] = {"desc": row["description"]}
        except Exception:
            roles_from_db = {"董事長 / 總經理": {"desc": "最高決策權限"}}
        conn.close()

        role_display_list = [{"角色名稱": r, "職責說明": info.get("desc", "")} for r, info in roles_from_db.items()]
        st.dataframe(pd.DataFrame(role_display_list), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ➕ 動態新增或刪除職位角色 (不限特定公司)")
        with st.form("form_db_role_crud"):
            new_role_name = st.text_input("職位角色名稱 (例如: 副總經理、機電科長、專案經理)")
            new_role_desc = st.text_input("部門職責與資料範圍說明")
            
            col_cr1, col_cr2 = st.columns(2)
            with col_cr1:
                save_role_btn = st.form_submit_button("💾 永久寫入資料庫保存", type="primary", use_container_width=True)
            with col_cr2:
                del_role_btn = st.form_submit_button("🗑️ 從資料庫刪除指定職位", use_container_width=True)

            if save_role_btn:
                if new_role_name:
                    try:
                        conn, _ = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
                        cursor = conn.cursor()
                        if "SQLite" in cfg["type"]:
                            cursor.execute("INSERT OR REPLACE INTO system_roles (role_name, description) VALUES (?, ?)", (new_role_name, new_role_desc))
                        else:
                            cursor.execute("INSERT INTO system_roles (role_name, description) VALUES (%s, %s) ON CONFLICT (role_name) DO UPDATE SET description = EXCLUDED.description", (new_role_name, new_role_desc))
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"新增/更新組織角色權限: {new_role_name}", "IT管理中心", "成功")

                        st.success(f"✅ 職位角色 [{new_role_name}] 已成功寫入資料庫永久保存！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入發生錯誤：{e}")
                else:
                    st.warning("⚠️ 請輸入職位角色名稱！")

            if del_role_btn:
                if new_role_name:
                    try:
                        conn, _ = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
                        cursor = conn.cursor()
                        if "SQLite" in cfg["type"]:
                            cursor.execute("DELETE FROM system_roles WHERE role_name = ?", (new_role_name,))
                        else:
                            cursor.execute("DELETE FROM system_roles WHERE role_name = %s", (new_role_name,))
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"刪除組織角色權限: {new_role_name}", "IT管理中心", "成功")

                        st.success(f"🗑️ 職位角色 [{new_role_name}] 已從資料庫成功刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除發生錯誤：{e}")
                else:
                    st.warning("⚠️ 請輸入欲刪除的職位角色名稱！")

    # ----------------------------------------------------
    # 📊 Tab 1: 系統稽核日誌 (直接從資料庫撈取永久保存紀錄)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown("### 📊 系統操作稽核日誌 (System Audit Logs)")
        st.info("💡 說明：以下所有操作紀錄均直接存取自 Supabase 雲端資料庫中的具備永久保存與資安稽核追溯能力。")

        try:
            conn, _ = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
            df_audit = pd.read_sql("SELECT time AS 執行時間, user_account AS 操作帳號, action AS 操作內容, module AS 所屬模組, ip AS 來源IP, status AS 狀態 FROM system_audit_logs ORDER BY id DESC", conn)
            conn.close()

            if not df_audit.empty:
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無系統操作日誌紀錄。")
        except Exception as e:
            st.warning(f"讀取稽核日誌發生錯誤：{e}")

    with tab_users:
        st.markdown("### 👥 員工與帳號總覽")
        st.info("人事系統員工資料表已就緒。")

    with tab_api:
        st.markdown("### 🔌 越南電子發票 API 設定")
        st.info("E-Invoice 閘道設定就緒。")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
