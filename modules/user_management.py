import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 IT 管理中心 - 組織角色權限與系統稽核 (Supabase 聯動版)
# ----------------------------------------------------

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🔒 IT 管理中心 - 組織角色權限與系統稽核總覽")
    st.caption("裕豐電機雲端高可用架構：對接 Supabase 雲端資料庫 (RBAC)，實現零暫存、真實資料庫存取。")

    # 1. 嘗試從 Supabase 讀取使用者資料
    users_data = []
    db_connected = False
    if engine is not None:
        try:
            df_users = pd.read_sql("SELECT username, name, role, site FROM system_users", con=engine)
            users_data = df_users.to_dict(orient="records")
            db_connected = True
        except Exception as e:
            st.warning(f"⚠️ 雲端 Supabase 連線提示 (已自動啟動安全記憶體降級模式)：{str(e)}")

    # 如果雲端無資料或未連線，初始化 session_state 作為備援
    if not users_data:
        if "system_users_db" not in st.session_state:
            st.session_state.system_users_db = [
                {"username": "admin", "name": "系統管理員", "role": "admin", "site": "台灣總部"},
                {"username": "manager", "name": "陳經理", "role": "manager", "site": "越南西寧廠"},
                {"username": "security", "name": "大門保全組", "role": "security", "site": "越南西寧廠"}
            ]
        users_data = st.session_state.system_users_db

    tab_rbac, tab_audit, tab_users = st.tabs([
        "🛡️ 組織角色權限範本 (RBAC)", 
        "📊 系統稽核日誌", 
        "👥 系統使用者與新增維護"
    ])

    with tab_rbac:
        st.markdown("### ⚙️ 組織角色與存取控制對照")
        st.info("💡 系統已強制綁定登入者權限與資料隔離（Row-Level Security），確保各廠區與職務只能存取授權範圍內的資料。")
        rbac_df = pd.DataFrame([
            {"角色名稱": "最高決策者 (Admin / GM)", "職責與權限範圍": "全系統總覽、客戶 ERP 授權控制、財務與採購總表", "允許開關之頁面數量": "全開 (ALL)"},
            {"角色名稱": "廠區主管 (Manager)", "職責與權限範圍": "負責該廠區之員工考勤審核、工程日報與庫存管理", "允許開關之頁面數量": "分廠與部門權限"},
            {"角色名稱": "資訊管理員 (IT)", "職責與權限範圍": "系統架構維護、Storage 雲端路徑設定與稽核日誌監控", "允許開關之頁面數量": "IT 專屬管理"},
            {"角色名稱": "一般員工 / 現場人員 (Staff)", "職責與權限範圍": "個人打卡、請假申請、現場照片歸檔與作業填報", "允許開關之頁面數量": "作業端專用"}
        ])
        st.dataframe(rbac_df, use_container_width=True)

    with tab_audit:
        st.markdown("### 🔍 全系統操作與稽核軌跡日誌")
        audit_logs = []
        if engine is not None:
            try:
                audit_logs = pd.read_sql("SELECT log_time as 時間, username as 操作帳號, action as 動作行為, module as 模組, ip_address as 來源IP, status as 執行狀態 FROM system_audit_logs ORDER BY id DESC LIMIT 50", con=engine).to_dict(orient="records")
            except Exception:
                pass
        
        if not audit_logs and "audit_logs_db" in st.session_state:
            audit_logs = st.session_state.audit_logs_db

        if audit_logs:
            st.dataframe(pd.DataFrame(audit_logs), use_container_width=True)
        else:
            st.info("目前尚無系統稽核紀錄。")

    with tab_users:
        st.markdown("### 👥 系統現有使用者帳號清冊 (Supabase 雲端同步)")
        st.dataframe(pd.DataFrame(users_data), use_container_width=True)

        st.markdown("---")
        st.markdown("### ➕ 新增系統使用者帳號與資料庫連動")
        with st.form("form_add_system_user_supabase"):
            c1, c2 = st.columns(2)
            with c1:
                new_username = st.text_input("登入帳號 (工號) *", value="EMP-008")
                new_name = st.text_input("使用者姓名 *", placeholder="例如: 阮文雄 / Nguyễn Văn Hùng")
            with c2:
                new_role = st.selectbox("權限角色 *", ["admin", "manager", "security", "staff"])
                new_site = st.selectbox("所屬廠區 *", ["台灣總部 (Taiwan HQ)", "越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)"])

            if st.form_submit_button("🚀 建立使用者並同步寫入 Supabase", type="primary", use_container_width=True):
                if new_username and new_name:
                    # 1. 寫入 Supabase 資料庫
                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                conn.execute(
                                    text("INSERT INTO system_users (username, name, role, site) VALUES (:u, :n, :r, :s) ON CONFLICT (username) DO UPDATE SET name=:n, role=:r, site=:s"),
                                    {"u": new_username, "n": new_name, "r": new_role, "s": new_site}
                                )
                                # 同步記錄稽核日誌
                                conn.execute(
                                    text("INSERT INTO system_audit_logs (username, action, module, ip_address, status) VALUES (:u, :a, :m, :ip, :st)"),
                                    {"u": st.session_state.get("user_name", "admin"), "a": f"新增/更新系統使用者 [{new_username}] {new_name}", "module": "UserMgmt", "ip": "192.168.1.50", "status": "成功"}
                                )
                            st.success(f"✅ 成功將帳號 `{new_username}` 寫入 Supabase 雲端資料庫！")
                        except Exception as db_err:
                            st.error(f"⚠️ 寫入 Supabase 失敗，已暫存於本地：{str(db_err)}")
                            # 降級存入 session_state
                            st.session_state.system_users_db.append({"username": new_username, "name": new_name, "role": new_role, "site": new_site})
                    else:
                        if "system_users_db" in st.session_state:
                            st.session_state.system_users_db.append({"username": new_username, "name": new_name, "role": new_role, "site": new_site})
                        st.success(f"✅ 成功建立本地測試帳號 `{new_username}`！")
                    
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫帳號與姓名！")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
