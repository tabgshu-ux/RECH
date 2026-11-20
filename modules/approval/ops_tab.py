from datetime import datetime, time
import streamlit as st
from modules.approval.workflow_repo import create_ops_request


def render(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime):
    st.markdown("#### 📦 2. 採購請款／倉庫領調／外出簽核申請")
    st.info("涵蓋採購請款（PR/PO）、倉庫領料／調撥簽核與人員外出簽核，統一送交權責主管審查。")
    with st.form("wf_form_ops_req"):
        c1, c2 = st.columns(2)
        with c1:
            req_cat = st.selectbox(
                "簽核類別*",
                [("PROCUREMENT", "🛒 採購與請款申請單 (PR/PO)"), ("WAREHOUSE", "🏭 倉庫領料／跨庫調撥簽核"), ("OUTING", "🚶 人員外出／差旅簽核")],
                format_func=lambda x: x[1],
            )
            title_item = st.text_input("申請主旨／品項名稱*", placeholder="例：西寧廠區主配電盤銅排採購 / 領料")
        with c2:
            amount_vnd = st.number_input("涉及金額 (VND，外出／領料可填 0)", min_value=0, value=0, step=100000)
            out_date = st.date_input("預計執行／外出日期", value=now_vn.date())
        detail_text = st.text_area("詳細說明／專案關聯*", placeholder="請填寫規格、數量、倉庫／案場或外出地點與事由...")
        if st.form_submit_button("📨 提交簽核申請", type="primary", use_container_width=True):
            rcode, rlabel = req_cat
            if not title_item.strip() or not detail_text.strip():
                st.warning("⚠️ 請填寫申請主旨與詳細說明。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    req_no = create_ops_request(engine, tenant_id, user_name, user_role, project_id, rcode, rlabel, title_item.strip(), float(amount_vnd), datetime.combine(out_date, time(8, 0)), detail_text.strip(), now_vn)
                    st.success(f"✅ 已提交【{rlabel}】單號 `{req_no}`，送交主管審核。")
                except Exception as e:
                    st.error(f"❌ 提交簽核單失敗：{e}")
