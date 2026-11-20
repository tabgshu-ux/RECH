import pandas as pd
import streamlit as st
from modules.approval.workflow_repo import decide_request, list_requests_df


def render(engine, tenant_id: str, approver_name: str):
    st.markdown("#### 📋 4. 待簽核案件審查（主管專區）")
    filter_type = st.selectbox(
        "篩選簽核類別",
        ["ALL", "LEAVE", "PROCUREMENT", "WAREHOUSE", "OUTING", "VEHICLE"],
        format_func=lambda x: {"ALL": "全部類別", "LEAVE": "📝 請假簽核", "PROCUREMENT": "🛒 採購請款", "WAREHOUSE": "🏭 倉庫簽核", "OUTING": "🚶 外出簽核", "VEHICLE": "🚗 公務派車"}[x],
    )
    df = list_requests_df(engine, tenant_id, req_type=filter_type)
    if df.empty:
        st.info("目前無符合條件的簽核單據。")
        return

    disp = df.rename(columns={"req_no": "單號", "req_type": "類別", "applicant_name": "申請人", "title_or_item": "主旨／項目", "s_str": "開始時間", "e_str": "結束時間", "status": "簽核狀態"})
    disp["金額(₫)"] = disp["amount_vnd"].apply(lambda v: f"{round(float(v or 0)):,}".replace(",", "."))
    st.dataframe(disp[["單號", "類別", "申請人", "主旨／項目", "金額(₫)", "開始時間", "結束時間", "簽核狀態"]], use_container_width=True, hide_index=True)

    pending = df[df["status"] == "PENDING_SUPERVISOR"]["req_no"].tolist()
    if pending:
        sel_no = st.selectbox("選擇待審核單號", pending, key="wf_sel_pending_no")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ 核准放行", key="wf_btn_approve", type="primary", use_container_width=True):
                decide_request(engine, tenant_id, sel_no, True, approver_name)
                st.success(f"✅ 已核准單號 `{sel_no}`。")
                st.rerun()
        with b2:
            if st.button("❌ 駁回退件", key="wf_btn_reject", use_container_width=True):
                decide_request(engine, tenant_id, sel_no, False, approver_name)
                st.warning(f"已駁回單號 `{sel_no}`。")
                st.rerun()
