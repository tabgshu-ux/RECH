import streamlit as st
from modules.approval.workflow_repo import list_requests_df


def render(engine, tenant_id: str):
    st.markdown("#### 📊 5. 簽核進度即時追蹤")
    df = list_requests_df(engine, tenant_id, req_type="ALL", limit=50)
    if df.empty:
        st.info("目前尚無簽核追蹤紀錄。")
        return
    disp = df.rename(columns={"req_no": "單號", "req_type": "類別", "applicant_name": "申請人", "title_or_item": "申請內容", "status": "簽核狀態", "approver_name": "簽核主管", "gate_status": "門禁狀態"})
    st.dataframe(disp[["單號", "類別", "申請人", "申請內容", "簽核狀態", "簽核主管", "門禁狀態"]], use_container_width=True, hide_index=True)
