from modules.security.gate_repo import fetch_security_summary_for_ga


def render_security_logistics_panel(engine, tenant_id: str):
    st.markdown("#### 🛡️ 保全與後勤門禁統計中心")
    st.caption("即時彙整保全操作頁面回傳之車輛／物品查驗、人員進出、廠內訪客與待領包裹統計。")
    stats = fetch_security_summary_for_ga(engine, tenant_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("車輛進出查驗", f"{stats['vehicle_logs_count']} 筆")
    c2.metric("物品查驗異常", f"{stats['cargo_abnormal_count']} 筆")
    c3.metric("廠內在場訪客", f"{stats['visitors_in_site']} 位")
    c4.metric("待領郵件／包裹", f"{stats['packages_unpicked']} 件")
