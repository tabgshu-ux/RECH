# ==========================================
# 檔案路徑：modules/approval_workflow.py
# 職責：全公司電子簽核中心（Mobile-First 全卡片式操作介面，串接請假/營運/派車/審查/追蹤/門禁）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core import ui_theme
from modules.approval import gate_tab, leave_tab, ops_tab, supervisor_tab, tracker_tab, vehicle_tab, workflow_repo


def _count_pending_stats(engine, tenant_id: str) -> tuple[int, int]:
    """統計待主管簽核筆數與待保全放行車輛數"""
    if not engine:
        return 0, 0
    df_all = workflow_repo.list_requests_df(engine, tenant_id, req_type="ALL", limit=100)
    df_car = workflow_repo.list_vehicles_df(engine, tenant_id, limit=100)
    pending_sup = int((df_all["status"] == "PENDING_SUPERVISOR").sum()) if not df_all.empty else 0
    pending_gate = (
        int(((df_car["status"] == "APPROVED_FOR_GATE") & (df_car["gate_status"] != "DEPARTED")).sum())
        if not df_car.empty
        else 0
    )
    return pending_sup, pending_gate


def render_approval_center(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "admin"
    user_role = st.session_state.get("user_role") or "角色"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### ✍️ 全公司電子簽核中心 (Approval Center)")
    st.caption("請點選下方功能卡片操作請假、採購／倉庫／外出、公務派車、主管審查、進度追蹤或保全放行。")
    workflow_repo.ensure_tables(engine)

    pending_sup, pending_gate = _count_pending_stats(engine, tenant_id)

    if "wf_active_card" not in st.session_state:
        st.session_state["wf_active_card"] = "LEAVE"

    active_card = st.session_state["wf_active_card"]

    cards_row1 = [
        ("LEAVE", "📝 1. 員工請假申請", "特休／病假／事假／公假"),
        ("OPS", "📦 2. 採購／倉庫／外出", "三張獨立卡片快速填單"),
        ("VEHICLE", "🚗 3. 廠區公務派車", "含出車／返回日期與時分"),
    ]
    cards_row2 = [
        ("SUPERVISOR", f"📋 4. 主管案件審查（待審 {pending_sup}）", "核准放行或駁回退件"),
        ("TRACKER", "📊 5. 簽核進度追蹤", "即時查看各單據與門禁狀態"),
        ("GATE", f"🛡️ 6. 保全門禁放行（待放 {pending_gate}）", "核對核准派車與登記里程"),
    ]

    r1_cols = st.columns(3)
    for idx, (ckey, ctitle, csub) in enumerate(cards_row1):
        with r1_cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{ctitle}**")
                st.caption(csub)
                is_sel = active_card == ckey
                lbl = f"✅ 使用中：{ctitle.split(' ', 1)[-1]}" if is_sel else "點此開啟卡片"
                if st.button(
                    lbl,
                    key=f"wf_card_btn_{ckey}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["wf_active_card"] = ckey
                    st.rerun()

    r2_cols = st.columns(3)
    for idx, (ckey, ctitle, csub) in enumerate(cards_row2):
        with r2_cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{ctitle}**")
                st.caption(csub)
                is_sel = active_card == ckey
                lbl = f"✅ 使用中：{ctitle.split(' ', 1)[-1]}" if is_sel else "點此開啟卡片"
                if st.button(
                    lbl,
                    key=f"wf_card_btn_{ckey}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["wf_active_card"] = ckey
                    st.rerun()

    st.divider()

    with st.container(border=True):
        if active_card == "OPS":
            ops_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn)
        elif active_card == "VEHICLE":
            vehicle_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn, code)
        elif active_card == "SUPERVISOR":
            supervisor_tab.render(engine, tenant_id, user_name)
        elif active_card == "TRACKER":
            tracker_tab.render(engine, tenant_id)
        elif active_card == "GATE":
            gate_tab.render(engine, tenant_id, user_name)
        else:
            leave_tab.render(engine, tenant_id, user_name, user_role, project_id, now_vn)


def render(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
