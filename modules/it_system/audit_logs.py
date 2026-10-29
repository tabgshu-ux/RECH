import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text

# 手機優先響應式設計
MOBILE_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; }
}
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

AUDIT_I18N = {
    "繁體中文": {
        "title": "📊 系統稽核日誌與操作紀錄追蹤 (Audit Logs)",
        "caption": "即時監控所有使用者登入、資料異動、權限調整與關鍵操作軌跡，確保企業資安無死角。",
        "col_time": "操作時間",
        "col_user": "使用者帳號",
        "col_role": "身份角色",
        "col_action": "動作與模組",
        "col_detail": "詳細異動內容說明",
        "col_ip": "來源 IP / 裝置",
        "clear_btn": "🗑️ 清空歷史稽核日誌",
        "export_btn": "📥 匯出稽核報表 (CSV)",
    },
    "Tiếng Việt": {
        "title": "📊 Nhật ký Kiểm toán Hệ thống & Theo dõi Hoạt động",
        "caption": "Giám sát thời gian thực mọi đăng nhập, thay đổi dữ liệu và phân quyền.",
        "col_time": "Thời gian",
        "col_user": "Tài khoản",
        "col_role": "Vai trò",
        "col_action": "Thao tác",
        "col_detail": "Chi tiết",
        "col_ip": "IP / Thiết bị",
        "clear_btn": "🗑️ Xóa nhật ký",
        "export_btn": "📥 Xuất báo cáo (CSV)",
    },
    "English": {
        "title": "📊 System Audit Logs & Activity Tracking",
        "caption": "Real-time monitoring of user logins, data changes, permission updates, and operational footprints.",
        "col_time": "Timestamp",
        "col_user": "User Account",
        "col_role": "Role",
        "col_action": "Action / Module",
        "col_detail": "Details / Changes",
        "col_ip": "Source IP / Device",
        "clear_btn": "🗑️ Clear Audit Logs",
        "export_btn": "📥 Export Audit CSV",
    }
}

def init_audit_table(engine):
    if engine is None:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_audit_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    username VARCHAR(100),
                    role_name VARCHAR(100),
                    action_type VARCHAR(100),
                    details TEXT,
                    ip_address VARCHAR(50) DEFAULT 'Local/Field'
                );
            """))
    except Exception:
        pass

def render(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in AUDIT_I18N else "繁體中文"
    L = AUDIT_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    init_audit_table(engine)

    # 模擬或從資料庫撈取日誌
    logs_data = []
    if engine is not None:
        try:
            df_logs = pd.read_sql("SELECT timestamp, username, role_name, action_type, details, ip_address FROM system_audit_logs ORDER BY timestamp DESC LIMIT 100", con=engine)
            if not df_logs.empty:
                logs_data = df_logs.to_dict('records')
        except Exception:
            pass

    # 如果資料庫尚無紀錄，提供預設展示與防呆紀錄
    if not logs_data:
        logs_data = [
            {
                "timestamp": str(datetime.now()),
                "username": "admin",
                "role_name": "系統管理員 (Admin)",
                "action_type": "登入系統",
                "details": "管理者成功登入 REETECH SaaS ERP 系統。",
                "ip_address": "192.168.1.50 (Mobile Web)"
            }
        ]

    # 轉成 DataFrame 進行美觀展示
    df_display = pd.DataFrame(logs_data)
    df_display.columns = [L['col_time'], L['col_user'], L['col_role'], L['col_action'], L['col_detail'], L['col_ip']]

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(L['clear_btn'], use_container_width=True):
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM system_audit_logs;"))
                except Exception:
                    pass
            st.success("🗑️ 稽核日誌已清空！")
            st.rerun()
    with col2:
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=L['export_btn'],
            data=csv_data,
            file_name=f"system_audit_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
