import streamlit as st
from modules.approval.workflow_repo import list_vehicles_df, release_vehicle_gate


def render(engine, tenant_id: str, guard_name: str):
    st.markdown("#### 🛡️ 6. 保全門禁車輛放行查驗（保全專區）")
    st.info("查驗已核准之公務派車單，登記出廠里程數並確認放行。")
    df = list_vehicles_df(engine, tenant_id, limit=30)
    if df.empty:
        st.info("目前尚無派車門禁紀錄。")
        return

    disp = df.rename(columns={"dispatch_no": "派車單號", "applicant_name": "申請人", "vehicle_plate": "車輛", "driver_name": "司機", "destination": "目的地", "dep_str": "預計出廠", "ret_str": "預計返回", "status": "簽核狀態", "gate_status": "門禁放行"})
    st.dataframe(disp[["派車單號", "申請人", "車輛", "司機", "目的地", "預計出廠", "預計返回", "簽核狀態", "門禁放行"]], use_container_width=True, hide_index=True)

    ready = df[(df["status"] == "APPROVED_FOR_GATE") & (df["gate_status"] != "DEPARTED")]["dispatch_no"].tolist()
    if ready:
        sel_dno = st.selectbox("選擇已核准派車單進行放行登記", ready, key="wf_gate_car_sel")
        km_val = st.text_input("出廠里程數 (KM)", placeholder="例：45280 km", key="wf_gate_km")
        if st.button("🚦 確認出廠放行", type="primary", use_container_width=True, key="wf_gate_go"):
            release_vehicle_gate(engine, tenant_id, sel_dno, km_val.strip() or None)
            st.success(f"🚦 已登記派車單 `{sel_dno}` 出廠放行（經辦保全：{guard_name}）。")
            st.rerun()
