# ==========================================
# 檔案路徑：modules/approval_workflow.py
# 職責：全公司電子簽核中心入口組裝殼（各分頁與資料流已獨立拆分至 modules/approval/）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core import ui_theme
from modules.approval import gate_tab, leave_tab, ops_tab, supervisor_tab, tracker_tab, vehicle_tab, workflow_repo


def render_approval_center(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "admin"
    user_role = st.session_state.get("user_role") or "角色"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### ✍️ 全公司電子簽核中心 (Approval Center)")
    st.caption("提交請假、採購請款、倉庫領調、外出、公務派車或專案簽呈；系統自動依權限進行多級電子簽核。")
    workflow_repo.ensure_tables(engine)

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📝 1. 員工請假申請",
        "📦 2. 採購／倉庫／外出簽核",
        "🚗 3. 廠區公務派車申請單",
        "📋 4. 待簽核案件審查（主管專區）",
        "📊 5. 簽核進度即時追蹤",
        "🛡️ 6. 保全門禁車輛放行查驗",
    ])

    with t1:
        leave_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn)
    with t2:
        ops_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn)
    with t3:
        vehicle_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn, code)
    with t4:
        supervisor_tab.render(engine, tenant_id, user_name)
    with t5:
        tracker_tab.render(engine, tenant_id)
    with t6:
        gate_tab.render(engine, tenant_id, user_name)


def render(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
