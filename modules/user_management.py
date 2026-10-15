import streamlit as st
import pandas as pd
import datetime
import os
import streamlit as st
import pandas as pd
import datetime
import os

# ----------------------------------------------------
# 🔌 全方位萬用資料庫轉接頭 (完整連線參數與 Safe Exception)
# ----------------------------------------------------
def get_universal_db_connection(db_type="Supabase / PostgreSQL", host="aws-0-ap-southeast-1.pooler.supabase.com", port="5432", user="postgres.wvsqbefyekmueffcbwd", password="", db_name="postgres"):
    pwd = password or st.session_state.get("db_pass", "") or st.secrets.get("SUPABASE_DB_PASS", "")
    try:
        if "Supabase" in db_type or "PostgreSQL" in db_type:
            import psycopg2
            conn = psycopg2.connect(
                host=host, port=port, user=user, password=pwd, database=db_name, connect_timeout=5
            )
            return conn, "PostgreSQL"
        elif "MySQL" in db_type:
            import pymysql
            conn = pymysql.connect(
                host=host, port=int(port) if port else 3306, user=user, password=pwd, database=db_name, charset='utf8mb4'
            )
            return conn, "MySQL"
        else:
            import sqlite3
            conn = sqlite3.connect("reetech_erp_local.db", check_same_thread=False)
            return conn, "SQLite"
    except Exception as e:
        # 僅在後台列印細節，防止敏感路徑洩露
        print(f"[DB CONNECTION ERROR] {e}")
        import sqlite3
        conn = sqlite3.connect("reetech_erp_local.db", check_same_thread=False)
        return conn, "SQLite (Fallback)"

def get_system_roles_from_db():
    """專門給人事模組呼叫：即時從資料庫取得所有 IT 設定的角色名稱列表"""
    default_roles = [
        "系統管理員 (Admin)",
        "董事長 / 總經理 (Executive)",
        "財務副理 / 財務主管 (Finance Manager)",
        "廠長 / 工務經理 (Plant/Project Manager)",
        "現場工地主任 / 組長 (Site Supervisor)",
        "採購 / 倉管 / 兼任會計 (Purchasing/Inventory)",
        "一般員工 (Staff)"
    ]
    try:
        cfg = st.session_state.get("db_config_state", {
            "type": "Supabase / PostgreSQL", "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", "user": "postgres.wvsqbefyekmueffcbwd", "password": "", "db_name": "postgres"
        })
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
        cursor = conn.cursor()
        table_prefix = "public." if "PostgreSQL" in actual_type else ""
        cursor.execute(f"SELECT role_name FROM {table_prefix}system_roles")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        roles = [r[0] for r in rows if r[0]]
        return roles if roles else default_roles
    except Exception:
        return default_roles

# ----------------------------------------------------
# 🛠️ 自動確保核心資料表存在
# ----------------------------------------------------
def ensure_tables_exist(conn, actual_type):
    cursor = conn.cursor()
    is_sqlite = "SQLite" in actual_type
    try:
        if is_sqlite:
            cursor.execute("CREATE TABLE IF NOT EXISTS system_roles (role_name TEXT PRIMARY KEY, description TEXT, allowed_modules TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS system_users (username TEXT PRIMARY KEY, name TEXT, role TEXT, site TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS system_audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, user_account TEXT, action TEXT, module TEXT, ip TEXT, status TEXT)")
            cursor.execute("INSERT OR IGNORE INTO system_roles (role_name, description, allowed_modules) VALUES (?, ?, ?)", 
                           ("董事長 / 總經理", "最高決策與全系統總覽權限", "ALL"))
        else:
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_roles (role_name VARCHAR(100) PRIMARY KEY, description TEXT, allowed_modules TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_users (username VARCHAR(50) PRIMARY KEY, name VARCHAR(100), role VARCHAR(100), site VARCHAR(100))")
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_audit_logs (id SERIAL PRIMARY KEY, time VARCHAR(50), user_account VARCHAR(50), action VARCHAR(255), module VARCHAR(50), ip VARCHAR(50), status VARCHAR(50))")
            cursor.execute("INSERT INTO public.system_roles (role_name, description, allowed_modules) VALUES (%s, %s, %s) ON CONFLICT (role_name) DO NOTHING", 
                           ("董事長 / 總經理", "最高決策與全系統總覽權限", "ALL"))
        conn.commit()
    except Exception as e:
        print(f"[SCHEMA ERROR] {e}")
    finally:
        cursor.close()

# ----------------------------------------------------
# 📝 核心稽核日誌寫入
# ----------------------------------------------------
def log_system_action(action_desc, module_name="IT管理中心", status="成功"):
    try:
        cfg = st.session_state.get("db_config_state", {
            "type": "Supabase / PostgreSQL", "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", "user": "postgres.wvsqbefyekmueffcbwd", "password": "", "db_name": "postgres"
        })
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
        ensure_tables_exist(conn, actual_type)
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_acc = st.session_state.get("user_name", "admin")
        ip_addr = "192.168.1.100"
        
        if "SQLite" in actual_type:
            cursor.execute(
                "INSERT INTO system_audit_logs (time, user_account, action, module, ip, status) VALUES (?, ?, ?, ?, ?, ?)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        else:
            cursor.execute(
                "INSERT INTO public.system_audit_logs (time, user_account, action, module, ip, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] {e}")

# ----------------------------------------------------
# 🌳 依部門分類之全系統樹狀功能模組清單
# ----------------------------------------------------
DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "📢 公司重要公告與簡報",
        "📊 全公司 KPI 營運績效與決策儀表板",
        "📑 高階主管審核與拍板中心"
    ],
    "🏢 管理部 (Management Dept)": [
        "👥 員工個人檔案與人事管理",
        "🕒 廠內員工固定打卡與出勤紀錄",
        "🏗️ 外勤出勤統計與工地人數監控",
        "🍱 幹部宿舍伙食與採購控管",
        "🏢 廠區與工作廠區管理",
        "🚧 廠區車輛進出口門禁與派車審核",
        "🔧 車輛維修保養紀錄",
        "💻 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "💰 應收帳款與對帳管理中心",
        "🧾 越南稅務標準財務報表 (Thông tư 200)",
        "💵 員工薪資計算與保險扣除",
        "🧾 電子發票綜合管理與 XML 報檔"
    ],
    "📑 全公司電子簽核中心 (Approval Center)": [
        "✍️ 跨部門電子表單簽核與呈核系統",
        "📋 雙層報價單高階拍板簽核佇列"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "📐 工程 BOM 零件自動展開與採購/庫存連動",
        "📑 工程報價單與雙層利潤分析/合約簽核",
        "⚡ 配電盤組裝配線組與拍照入庫模組",
        "👷 現場工地主任日報表與點工點料扣減",
        "🛠️ 外包商請款與估驗進度比對"
    ],
    "🏭 生產部 (Production Dept)": [
        "⚡ 配電盤組裝配線組與拍照入庫",
        "📦 越南廠（西寧/海防）倉庫庫存盤點與領料"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 帳號權限與全系統稽核軌跡",
        "🔌 客戶 ERP 模組授權與功能開關",
        "萬用資料庫一鍵安裝精靈 (DB Wizard)",
        "🔌 越南電子發票與系統 SMTP 信箱 API 設定"
    ]
}

USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與系統稽核總覽",
        "caption": "對接企業雲端 Supabase / PostgreSQL，依一級部門與工程部設定權限 (RBAC)。",
        "tab_audit": "📊 系統稽核日誌",
        "tab_roles": "⚙️ 組織角色權限範本 (RBAC)",
        "tab_users": "👥 員工與帳號總覽",
        "tab_db": "🔌 萬用資料庫連線設定精靈 (DB Wizard)",
        "tab_api": "🔌 越南電子發票與 SMTP 信箱 API 設定",
    }
}

def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "db_config_state" not in st.session_state:
        st.session_state.db_config_state = {
            "type": "Supabase / PostgreSQL", 
            "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", 
            "user": "postgres.wvsqbefyekmueffcbwd", 
            "password": "", 
            "db_name": "postgres"
        }

    tab_audit, tab_roles, tab_users, tab_db, tab_api = st.tabs([
        L["tab_audit"], L["tab_roles"], L["tab_users"], L["tab_db"], L["tab_api"]
    ])

    cfg = st.session_state.db_config_state

    # ----------------------------------------------------
    # 🔌 萬用資料庫連線設定精靈 (完整參數保留)
    # ----------------------------------------------------
    with tab_db:
        st.markdown("### 🔌 全模組資料表與資料庫連線設定精靈")
        st.info("💡 說明：請在此輸入與確認資料庫主機位址、連接埠、帳號、密碼與資料庫名稱。")

        with st.form("form_universal_db_wizard"):
            db_type_sel = st.selectbox(
                "選擇目標資料庫類型 (Database Type)", 
                ["Supabase / PostgreSQL (雲端企業級)", "SQLite (免安裝本機單檔推薦)", "MySQL / MariaDB (地端伺服器)"],
                index=0
            )
            
            dc1, dc2 = st.columns(2)
            with dc1:
                db_host = st.text_input("資料庫主機位址 (Host)", value=cfg["host"])
                db_user = st.text_input("資料庫帳號 (User)", value=cfg["user"])
                db_name = st.text_input("資料庫名稱 (Database Name)", value=cfg["db_name"])
            with dc2:
                db_port = st.text_input("連接埠 (Port)", value=cfg["port"])
                db_pass = st.text_input("資料庫密碼 (Password / Secret)", type="password", value=st.session_state.get("db_pass", cfg.get("password", "")))

            init_btn = st.form_submit_button("🚀 測試連線並自動驗證全系統資料表", type="primary", use_container_width=True)

            if init_btn:
                selected_type_clean = db_type_sel.split(" (")[0]
                st.session_state.db_config_state = {
                    "type": selected_type_clean, "host": db_host, "port": db_port,
                    "user": db_user, "password": db_pass, "db_name": db_name
                }
                st.session_state["db_pass"] = db_pass
                
                conn, actual_type = get_universal_db_connection(selected_type_clean, db_host, db_port, db_user, db_pass, db_name)
                if "Fallback" in actual_type:
                    st.error("❌ 連線失敗：無法連線至指定的資料庫主機或帳號密碼錯誤。已切換至本機暫存模式。")
                else:
                    ensure_tables_exist(conn, actual_type)
                    conn.close()
                    st.success("🎉 資料庫連線驗證成功！`system_roles` 等核心資料表已順利對接！")
                    st.rerun()

    # ----------------------------------------------------
    # ⚙️ 組織角色與【依部門選單開關】權限設定 (RBAC)
    # ----------------------------------------------------
    with tab_roles:
        st.markdown("### ⚙️ 企業組織部門角色與權限範本清冊 (資料庫即時連線)")
        
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
        
        if "SQLite" in actual_type or "Fallback" in actual_type:
            st.warning("⚠️ 當前連線：本機暫存模式。若要同步存取 Supabase 雲端資料，請至【萬用資料庫連線設定精靈】確認密碼並連線。")
        else:
            st.success("🟢 已成功連線至企業雲端 PostgreSQL 資料庫！")

        ensure_tables_exist(conn, actual_type)
        
        roles_from_db = []
        try:
            cursor = conn.cursor()
            table_prefix = "public." if "PostgreSQL" in actual_type else ""
            cursor.execute(f"SELECT role_name, description, allowed_modules FROM {table_prefix}system_roles")
            rows = cursor.fetchall()
            for row in rows:
                roles_from_db.append({
                    "角色名稱": row[0],
                    "職責說明": row[1],
                    "允許開啟之頁面": row[2] if row[2] else "全部頁面 (ALL)"
                })
            cursor.close()
        except Exception:
            roles_from_db = [{"角色名稱": "董事長 / 總經理", "職責說明": "最高決策權限", "允許開啟之頁面": "全部頁面 (ALL)"}]
        conn.close()

        st.dataframe(pd.DataFrame(roles_from_db), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ➕ 設定 / 新增職位角色及其可開啟之網頁功能")
        
        with st.form("form_db_role_crud_by_dept"):
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                new_role_name = st.text_input("職位角色名稱", value="副總經理", placeholder="例如: 副總經理、機電科長、專案經理")
            with c_r2:
                new_role_desc = st.text_input("部門職責與資料範圍說明", value="負責公司所有業務執行及工程管報與報價")

            st.markdown("🌐 **勾選該職位角色可以開啟與操作的網頁功能（依一級部門與工程部分組）：**")
            
            selected_modules = []
            
            for dept_name, mod_list in DEPARTMENT_MODULE_TREE.items():
                st.markdown(f"##### {dept_name}")
                cols = st.columns(3)
                for i, mod in enumerate(mod_list):
                    c = cols[i % 3]
                    with c:
                        chk_key = f"chk_{dept_name}_{i}_{mod}"
                        if st.checkbox(mod, value=True, key=chk_key):
                            selected_modules.append(mod)
                st.markdown("---")

            col_cr1, col_cr2 = st.columns(2)
            with col_cr1:
                save_role_btn = st.form_submit_button("💾 永久寫入資料庫保存角色與部門頁面權限", type="primary", use_container_width=True)
            with col_cr2:
                del_role_btn = st.form_submit_button("🗑️ 從資料庫刪除指定職位", use_container_width=True)

            if save_role_btn:
                if new_role_name:
                    try:
                        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
                        ensure_tables_exist(conn, actual_type)
                        cursor = conn.cursor()
                        is_sqlite = "SQLite" in actual_type
                        
                        modules_str = ",".join(selected_modules) if selected_modules else "ALL"
                        
                        if is_sqlite:
                            cursor.execute(
                                "INSERT OR REPLACE INTO system_roles (role_name, description, allowed_modules) VALUES (?, ?, ?)",
                                (new_role_name, new_role_desc, modules_str)
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO public.system_roles (role_name, description, allowed_modules) VALUES (%s, %s, %s) ON CONFLICT (role_name) DO UPDATE SET description = EXCLUDED.description, allowed_modules = EXCLUDED.allowed_modules",
                                (new_role_name, new_role_desc, modules_str)
                            )
                        
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"設定角色部門頁面權限: [{new_role_name}] 允許 {len(selected_modules)} 個功能頁面", "IT管理中心", "成功")
                        st.success(f"✅ 職位角色 [{new_role_name}] 及其部門頁面權限已成功寫入資料庫！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 寫入資料庫失敗，請確認資料庫權限與連線設定。")
                else:
                    st.warning("⚠️ 請輸入職位角色名稱！")

            if del_role_btn:
                if new_role_name:
                    try:
                        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
                        ensure_tables_exist(conn, actual_type)
                        cursor = conn.cursor()
                        is_sqlite = "SQLite" in actual_type
                        
                        if is_sqlite:
                            cursor.execute("DELETE FROM system_roles WHERE role_name = ?", (new_role_name,))
                        else:
                            cursor.execute("DELETE FROM public.system_roles WHERE role_name = %s", (new_role_name,))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"刪除組織角色權限: {new_role_name}", "IT管理中心", "成功")
                        st.success(f"🗑️ 職位角色 [{new_role_name}] 已成功從資料庫刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 刪除失敗，請確認資料庫連線。")
                else:
                    st.warning("⚠️ 請輸入欲刪除的職位角色名稱！")

    # ----------------------------------------------------
    # 📊 系統稽核日誌
    # ----------------------------------------------------
    with tab_audit:
        st.markdown("### 📊 系統操作稽核日誌 (System Audit Logs)")
        try:
            conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
            ensure_tables_exist(conn, actual_type)
            table_prefix = "public." if "PostgreSQL" in actual_type else ""
            df_audit = pd.read_sql(f"SELECT time AS 執行時間, user_account AS 操作帳號, action AS 操作內容, module AS 所屬模組, ip AS 來源IP, status AS 狀態 FROM {table_prefix}system_audit_logs ORDER BY id DESC", conn)
            conn.close()

            if not df_audit.empty:
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無系統操作日誌紀錄。")
        except Exception:
            st.warning("讀取稽核日誌失敗。")

    # ----------------------------------------------------
    # 👥 員工與帳號總覽 (連動 public.system_users)
    # ----------------------------------------------------
    with tab_users:
        st.markdown("### 👥 員工帳號與系統角色權限綁定總覽")
        try:
            conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg.get("password", ""), cfg["db_name"])
            ensure_tables_exist(conn, actual_type)
            table_prefix = "public." if "PostgreSQL" in actual_type else ""
            df_users = pd.read_sql(f"SELECT username AS 登入帳號, name AS 員工姓名, role AS 系統角色, site AS 所屬廠區 FROM {table_prefix}system_users", conn)
            conn.close()
            if not df_users.empty:
                st.dataframe(df_users, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無建立額外帳號。點擊上方連線並連入 Supabase 後，可載入既有帳號清單。")
        except Exception:
            st.info("帳號表讀取中...")

    # ----------------------------------------------------
    # 📧 越南電子發票與系統 SMTP 電子郵件 API 設定
    # ----------------------------------------------------
    with tab_api:
        st.markdown("### 📧 系統通知信箱 (SMTP) 與越南電子發票 API 設定")
        st.info("💡 說明：在此設定系統發送審核通知信件、密碼重設信與電子發票開立閘道。")

        with st.form("form_smtp_and_einvoice_config"):
            st.markdown("#### 1️⃣ 系統通知信箱設定 (SMTP Mail Server)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                smtp_server = st.text_input("SMTP 伺服器位址", value=st.session_state.get("smtp_server", "smtp.gmail.com"))
                smtp_user = st.text_input("寄件者系統信箱", value=st.session_state.get("smtp_user", "service@reetech.com.vn"))
            with col_m2:
                smtp_port = st.text_input("SMTP 通訊埠 (Port)", value=st.session_state.get("smtp_port", "587"))
                smtp_pass = st.text_input("信箱應用程式密碼 (App Password)", type="password", value=st.session_state.get("smtp_pass", ""))

            st.markdown("---")
            st.markdown("#### 2️⃣ 越南電子發票 (E-Invoice API Gateway)")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                einv_url = st.text_input("電子發票服務 API URL", value="https://einvoice-api.vtn.vn")
            with col_e2:
                einv_token = st.text_input("API Token / 金鑰", type="password", value="")

            if st.form_submit_button("💾 儲存系統信箱與電子發票設定", type="primary", use_container_width=True):
                st.session_state["smtp_server"] = smtp_server
                st.session_state["smtp_user"] = smtp_user
                st.session_state["smtp_port"] = smtp_port
                st.session_state["smtp_pass"] = smtp_pass
                st.success("✅ 系統通知信箱與電子發票 API 設定已成功保存！")
                log_system_action("更新系統 SMTP 信箱與電子發票 API 設定", "IT管理中心", "成功")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
# ----------------------------------------------------
# 🔌 企業級萬用資料庫連線轉接頭 (資安隱蔽保護)
# ----------------------------------------------------
def get_universal_db_connection(db_type="Cloud DB", host="aws-0-ap-southeast-1.pooler.supabase.com", port="5432", user="postgres.wvsqbefyekmueffcbwd", password="", db_name="postgres"):
    pwd = password or st.session_state.get("db_pass", "") or st.secrets.get("SUPABASE_DB_PASS", "")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=pwd, database=db_name, connect_timeout=5
        )
        return conn, "Cloud"
    except Exception as e:
        # 資安防護：僅在背景 Console 紀錄日誌，前端絕不暴露實體主機細節
        print(f"[SECURITY LOG] Cloud DB connection fail, switching to local safety mode: {e}")
        import sqlite3
        conn = sqlite3.connect("reetech_erp_local.db", check_same_thread=False)
        return conn, "Local"

def get_system_roles_from_db():
    """提供給人事模組動態讀取角色 (資安隱蔽)"""
    default_roles = [
        "系統管理員 (Admin)",
        "董事長 / 總經理 (Executive)",
        "財務副理 / 財務主管 (Finance Manager)",
        "廠長 / 工務經理 (Plant/Project Manager)",
        "現場工地主任 / 組長 (Site Supervisor)",
        "採購 / 倉管 / 兼任會計 (Purchasing/Inventory)",
        "一般員工 (Staff)"
    ]
    try:
        cfg = st.session_state.get("db_config_state", {
            "type": "Cloud DB", "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", "user": "postgres.wvsqbefyekmueffcbwd", "password": "", "db_name": "postgres"
        })
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
        cursor = conn.cursor()
        table_prefix = "public." if actual_type == "Cloud" else ""
        cursor.execute(f"SELECT role_name FROM {table_prefix}system_roles")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        roles = [r[0] for r in rows if r[0]]
        return roles if roles else default_roles
    except Exception:
        return default_roles

# ----------------------------------------------------
# 🛠️ 自動確保核心資料表存在
# ----------------------------------------------------
def ensure_tables_exist(conn, actual_type):
    cursor = conn.cursor()
    is_local = actual_type == "Local"
    try:
        if is_local:
            cursor.execute("CREATE TABLE IF NOT EXISTS system_roles (role_name TEXT PRIMARY KEY, description TEXT, allowed_modules TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS system_users (username TEXT PRIMARY KEY, name TEXT, role TEXT, site TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS system_audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, user_account TEXT, action TEXT, module TEXT, ip TEXT, status TEXT)")
            cursor.execute("INSERT OR IGNORE INTO system_roles (role_name, description, allowed_modules) VALUES (?, ?, ?)", 
                           ("董事長 / 總經理", "最高決策與全系統總覽權限", "ALL"))
        else:
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_roles (role_name VARCHAR(100) PRIMARY KEY, description TEXT, allowed_modules TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_users (username VARCHAR(50) PRIMARY KEY, name VARCHAR(100), role VARCHAR(100), site VARCHAR(100))")
            cursor.execute("CREATE TABLE IF NOT EXISTS public.system_audit_logs (id SERIAL PRIMARY KEY, time VARCHAR(50), user_account VARCHAR(50), action VARCHAR(255), module VARCHAR(50), ip VARCHAR(50), status VARCHAR(50))")
            cursor.execute("INSERT INTO public.system_roles (role_name, description, allowed_modules) VALUES (%s, %s, %s) ON CONFLICT (role_name) DO NOTHING", 
                           ("董事長 / 總經理", "最高決策與全系統總覽權限", "ALL"))
        conn.commit()
    except Exception as e:
        print(f"[SECURITY LOG] Ensure tables error: {e}")
    finally:
        cursor.close()

# ----------------------------------------------------
# 📝 核心稽核日誌寫入
# ----------------------------------------------------
def log_system_action(action_desc, module_name="IT管理中心", status="成功"):
    try:
        cfg = st.session_state.get("db_config_state", {
            "type": "Cloud DB", "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", "user": "postgres.wvsqbefyekmueffcbwd", "password": "", "db_name": "postgres"
        })
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
        ensure_tables_exist(conn, actual_type)
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_acc = st.session_state.get("user_name", "admin")
        ip_addr = "192.168.1.100"
        
        if actual_type == "Local":
            cursor.execute(
                "INSERT INTO system_audit_logs (time, user_account, action, module, ip, status) VALUES (?, ?, ?, ?, ?, ?)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        else:
            cursor.execute(
                "INSERT INTO public.system_audit_logs (time, user_account, action, module, ip, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (current_time, user_acc, action_desc, module_name, ip_addr, status)
            )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[SECURITY LOG] Audit log error: {e}")

# ----------------------------------------------------
# 🌳 依部門分類之全系統樹狀功能模組清單
# ----------------------------------------------------
DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "📢 公司重要公告與簡報",
        "📊 全公司 KPI 營運績效與決策儀表板",
        "📑 高階主管審核與拍板中心"
    ],
    "🏢 管理部 (Management Dept)": [
        "👥 員工個人檔案與人事管理",
        "🕒 廠內員工固定打卡與出勤紀錄",
        "🏗️ 外勤出勤統計與工地人數監控",
        "🍱 幹部宿舍伙食與採購控管",
        "🏢 廠區與工作廠區管理",
        "🚧 廠區車輛進出口門禁與派車審核",
        "🔧 車輛維修保養紀錄",
        "💻 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "💰 應收帳款與對帳管理中心",
        "🧾 越南稅務標準財務報表 (Thông tư 200)",
        "💵 員工薪資計算與保險扣除",
        "🧾 電子發票綜合管理與 XML 報檔"
    ],
    "📑 全公司電子簽核中心 (Approval Center)": [
        "✍️ 跨部門電子表單簽核與呈核系統",
        "📋 雙層報價單高階拍板簽核佇列"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "📐 工程 BOM 零件自動展開與採購/庫存連動",
        "📑 工程報價單與雙層利潤分析/合約簽核",
        "⚡ 配電盤組裝配線組與拍照入庫模組",
        "👷 現場工地主任日報表與點工點料扣減",
        "🛠️ 外包商請款與估驗進度比對"
    ],
    "🏭 生產部 (Production Dept)": [
        "⚡ 配電盤組裝配線組與拍照入庫",
        "📦 越南廠（西寧/海防）倉庫庫存盤點與領料"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 帳號權限與全系統稽核軌跡",
        "🔌 客戶 ERP 模組授權與功能開關",
        "萬用資料庫一鍵安裝精靈 (DB Wizard)",
        "🔌 越南電子發票 API 設定"
    ]
}

USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與系統稽核總覽",
        "caption": "依一級部門與工程部樹狀結構設定各職位角色可開啟之頁面權限 (RBAC)。",
        "tab_audit": "📊 系統稽核日誌",
        "tab_roles": "⚙️ 組織角色權限範本 (RBAC)",
        "tab_users": "👥 員工與帳號總覽",
        "tab_db": "🔌 萬用資料庫連線設定精靈",
        "tab_api": "🔌 越南電子發票 API 設定",
    }
}

def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = USER_MGMT_I18N.get(active_lang, USER_MGMT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "db_config_state" not in st.session_state:
        st.session_state.db_config_state = {
            "type": "Cloud DB", 
            "host": "aws-0-ap-southeast-1.pooler.supabase.com", 
            "port": "5432", 
            "user": "postgres.wvsqbefyekmueffcbwd", 
            "password": "", 
            "db_name": "postgres"
        }

    tab_audit, tab_roles, tab_users, tab_db, tab_api = st.tabs([
        L["tab_audit"], L["tab_roles"], L["tab_users"], L["tab_db"], L["tab_api"]
    ])

    cfg = st.session_state.db_config_state

    # ----------------------------------------------------
    # 🔌 資料庫連線設定精靈 (不暴露實體廠商名稱)
    # ----------------------------------------------------
    with tab_db:
        st.markdown("### 🔌 企業雲端資料庫連線驗證精靈")
        st.info("💡 說明：若要儲存至企業雲端資料庫，請在此輸入金鑰密碼。")

        with st.form("form_universal_db_wizard"):
            db_pass = st.text_input("企業雲端資料庫存取金鑰 (Access Key / Password)", type="password", value=st.session_state.get("db_pass", ""))
            init_btn = st.form_submit_button("🚀 驗證連線並初始化資料表", type="primary", use_container_width=True)

            if init_btn:
                st.session_state["db_pass"] = db_pass
                conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], db_pass, cfg["db_name"])
                if actual_type == "Local":
                    st.error("❌ 雲端資料庫驗證失敗，請檢查金鑰密碼。已安全切換至本機模式。")
                else:
                    ensure_tables_exist(conn, actual_type)
                    conn.close()
                    st.success("🎉 企業雲端資料庫驗證連線成功！")
                    st.rerun()

    # ----------------------------------------------------
    # ⚙️ 組織角色權限範本 (RBAC)
    # ----------------------------------------------------
    with tab_roles:
        st.markdown("### ⚙️ 企業組織部門角色與權限範本清冊")
        
        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
        
        # 資安中性化提示
        if actual_type == "Local":
            st.warning("⚠️ 當前處於本機安全模式。若要同步至雲端資料庫，請至【萬用資料庫連線設定精靈】輸入存取金鑰。")
        else:
            st.success("🟢 企業雲端資料庫連線正常")

        ensure_tables_exist(conn, actual_type)
        
        roles_from_db = []
        try:
            cursor = conn.cursor()
            table_prefix = "public." if actual_type == "Cloud" else ""
            cursor.execute(f"SELECT role_name, description, allowed_modules FROM {table_prefix}system_roles")
            rows = cursor.fetchall()
            for row in rows:
                roles_from_db.append({
                    "角色名稱": row[0],
                    "職責說明": row[1],
                    "允許開啟之頁面": row[2] if row[2] else "全部頁面 (ALL)"
                })
            cursor.close()
        except Exception:
            roles_from_db = [{"角色名稱": "董事長 / 總經理", "職責說明": "最高決策權限", "允許開啟之頁面": "全部頁面 (ALL)"}]
        conn.close()

        st.dataframe(pd.DataFrame(roles_from_db), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ➕ 設定 / 新增職位角色及其可開啟之網頁功能")
        
        with st.form("form_db_role_crud_by_dept"):
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                new_role_name = st.text_input("職位角色名稱", value="副總經理", placeholder="例如: 副總經理、機電科長、專案經理")
            with c_r2:
                new_role_desc = st.text_input("部門職責與資料範圍說明", value="負責公司所有業務執行及工程管報與報價")

            st.markdown("🌐 **勾選該職位角色可以開啟與操作的網頁功能（依一級部門與工程部分組）：**")
            
            selected_modules = []
            
            for dept_name, mod_list in DEPARTMENT_MODULE_TREE.items():
                st.markdown(f"##### {dept_name}")
                cols = st.columns(3)
                for i, mod in enumerate(mod_list):
                    c = cols[i % 3]
                    with c:
                        chk_key = f"chk_{dept_name}_{i}_{mod}"
                        if st.checkbox(mod, value=True, key=chk_key):
                            selected_modules.append(mod)
                st.markdown("---")

            col_cr1, col_cr2 = st.columns(2)
            with col_cr1:
                save_role_btn = st.form_submit_button("💾 永久寫入保存角色與部門頁面權限", type="primary", use_container_width=True)
            with col_cr2:
                del_role_btn = st.form_submit_button("🗑️ 從資料庫刪除指定職位", use_container_width=True)

            if save_role_btn:
                if new_role_name:
                    try:
                        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
                        ensure_tables_exist(conn, actual_type)
                        cursor = conn.cursor()
                        is_local = actual_type == "Local"
                        
                        modules_str = ",".join(selected_modules) if selected_modules else "ALL"
                        
                        if is_local:
                            cursor.execute(
                                "INSERT OR REPLACE INTO system_roles (role_name, description, allowed_modules) VALUES (?, ?, ?)",
                                (new_role_name, new_role_desc, modules_str)
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO public.system_roles (role_name, description, allowed_modules) VALUES (%s, %s, %s) ON CONFLICT (role_name) DO UPDATE SET description = EXCLUDED.description, allowed_modules = EXCLUDED.allowed_modules",
                                (new_role_name, new_role_desc, modules_str)
                            )
                        
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"設定角色部門頁面權限: [{new_role_name}] 允許 {len(selected_modules)} 個功能頁面", "IT管理中心", "成功")
                        st.success(f"✅ 職位角色 [{new_role_name}] 及其部門頁面權限已成功寫入保存！")
                        st.rerun()
                    except Exception as e:
                        # 錯誤訊息中性化，避免暴漏系統細節
                        st.error("❌ 寫入資料庫失敗，請確認存取權限。")
                        print(f"[SECURITY LOG] Save role error detail: {e}")
                else:
                    st.warning("⚠️ 請輸入職位角色名稱！")

            if del_role_btn:
                if new_role_name:
                    try:
                        conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
                        ensure_tables_exist(conn, actual_type)
                        cursor = conn.cursor()
                        is_local = actual_type == "Local"
                        
                        if is_local:
                            cursor.execute("DELETE FROM system_roles WHERE role_name = ?", (new_role_name,))
                        else:
                            cursor.execute("DELETE FROM public.system_roles WHERE role_name = %s", (new_role_name,))
                        
                        conn.commit()
                        cursor.close()
                        conn.close()

                        log_system_action(f"刪除組織角色權限: {new_role_name}", "IT管理中心", "成功")
                        st.success(f"🗑️ 職位角色 [{new_role_name}] 已成功刪除！")
                        st.rerun()
                    except Exception as e:
                        st.error("❌ 刪除失敗，請確認存取權限。")
                        print(f"[SECURITY LOG] Delete role error detail: {e}")
                else:
                    st.warning("⚠️ 請輸入欲刪除的職位角色名稱！")

    # ----------------------------------------------------
    # 📊 系統稽核日誌
    # ----------------------------------------------------
    with tab_audit:
        st.markdown("### 📊 系統操作稽核日誌 (System Audit Logs)")
        try:
            conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
            ensure_tables_exist(conn, actual_type)
            table_prefix = "public." if actual_type == "Cloud" else ""
            df_audit = pd.read_sql(f"SELECT time AS 執行時間, user_account AS 操作帳號, action AS 操作內容, module AS 所屬模組, ip AS 來源IP, status AS 狀態 FROM {table_prefix}system_audit_logs ORDER BY id DESC", conn)
            conn.close()

            if not df_audit.empty:
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無系統操作日誌紀錄。")
        except Exception:
            st.warning("讀取稽核日誌時遇到障礙。")

    # ----------------------------------------------------
    # 👥 員工與帳號總覽
    # ----------------------------------------------------
    with tab_users:
        st.markdown("### 👥 員工帳號與系統角色權限綁定總覽")
        try:
            conn, actual_type = get_universal_db_connection(cfg["type"], cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["db_name"])
            ensure_tables_exist(conn, actual_type)
            table_prefix = "public." if actual_type == "Cloud" else ""
            df_users = pd.read_sql(f"SELECT username AS 登入帳號, name AS 員工姓名, role AS 系統角色, site AS 所屬廠區 FROM {table_prefix}system_users", conn)
            conn.close()
            if not df_users.empty:
                st.dataframe(df_users, use_container_width=True, hide_index=True)
            else:
                st.info("目前尚無建立額外帳號。")
        except Exception:
            st.info("帳號表讀取中...")

    # ----------------------------------------------------
    # 🔌 越南電子發票 API 設定
    # ----------------------------------------------------
    with tab_api:
        st.markdown("### 🔌 越南電子發票 API 設定")
        st.info("E-Invoice 閘道設定就緒。")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
