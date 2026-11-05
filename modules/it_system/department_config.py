import streamlit as st
import pandas as pd
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 獨立企業部門與模組拼圖管理 (Tenant Department & Module Config)")
    st.caption("多租戶 SaaS 架構核心：本介面允許企業 IT 在網頁端動態新增部門、調整順序與掛載模組，絕不寫死於程式碼中。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    # 1. 取得當前租戶代碼（預設裕豐 REETECH）
    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    
    st.info(f"📍 目前作用中企業租戶 (Tenant ID)：**{current_tenant_id}**")

    # 2. 從資料庫讀取該租戶目前的部門與拼圖配置
    try:
        with engine.connect() as conn:
            query = text("SELECT dept_id, dept_name, sort_order, assigned_modules, is_active FROM tenant_departments WHERE tenant_id = :tid ORDER BY sort_order ASC")
            df_depts = pd.read_sql(query, con=conn, params={"tid": current_tenant_id})
    except Exception as e:
        # 若資料表尚未建立的降級防護與初始化提示
        st.warning("💡 偵測到資料庫尚無 `tenant_departments` 配置表。系統已自動載入預設架構清單。")
        df_depts = pd.DataFrame([
            {"dept_id": "D01", "dept_name": "📈 總經理室 (Executive Office)", "sort_order": 1, "assigned_modules": "commodities_fx, financials_pl, project_progress, vietnam_policy", "is_active": True},
            {"dept_id": "D02", "dept_name": "👔 管理部 (Management Dept)", "sort_order": 2, "assigned_modules": "announcements, hr_records, accounting_ap_ar", "is_active": True},
            {"dept_id": "D03", "dept_name": "🛠️ 工程與設計管理中心", "sort_order": 3, "assigned_modules": "eng_dashboard, quotation, daily_report, fat_sat", "is_active": True},
            {"dept_id": "D04", "dept_name": "🏭 生產部 (Production Dept)", "sort_order": 4, "assigned_modules": "sheet_metal, painting, assembly", "is_active": True},
            {"dept_id": "D05", "dept_name": "📦 倉庫管理 (Warehouse Management)", "sort_order": 5, "assigned_modules": "inventory_barcodes", "is_active": True},
            {"dept_id": "D06", "dept_name": "📍 外勤工程打卡與工作回報", "sort_order": 6, "assigned_modules": "field_gps_attendance", "is_active": True},
            {"dept_id": "D07", "dept_name": "✍️ 電子簽核中心 (Approval Center)", "sort_order": 7, "assigned_modules": "approval_workflow", "is_active": True},
            {"dept_id": "D08", "dept_name": "💻 系統設定 (System Settings)", "sort_order": 8, "assigned_modules": "department_config, role_rbac, db_bridge, audit_logs", "is_active": True},
        ])

    st.markdown("#### 📋 現有部門與模組掛載對照表")
    st.dataframe(df_depts, use_container_width=True)

    st.markdown("---")
    st.markdown("#### ➕ 動態新增或調整企業部門")
    
    with st.form("add_dept_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_dept_name = st.text_input("新部門名稱 (例如: 永續發展辦公室)")
            new_sort_order = st.number_input("排序編號 (Sort Order)", min_value=1, max_value=99, value=9)
        with col2:
            available_modules = ["commodities_fx", "financials_pl", "eng_dashboard", "sheet_metal", "inventory_barcodes", "field_gps_attendance", "approval_workflow"]
            selected_modules = st.multiselect("勾選掛載模組拼圖 (Modules)", available_modules)
            is_active_flag = st.checkbox("立即啟用此部門", value=True)

        submitted = st.form_submit_button("💾 儲存並寫入租戶元數據 (Save Metadata)")
        if submitted:
            if new_dept_name:
                try:
                    with engine.begin() as conn:
                        insert_sql = text("""
                            INSERT INTO tenant_departments (tenant_id, dept_name, sort_order, assigned_modules, is_active)
                            VALUES (:tid, :dname, :sort, :mods, :act)
                        """)
                        conn.execute(insert_sql, {
                            "tid": current_tenant_id,
                            "dname": new_dept_name,
                            "sort": new_sort_order,
                            "mods": ", ".join(selected_modules),
                            "act": is_active_flag
                        })
                    st.success(f"🎉 成功為租戶 {current_tenant_id} 新增部門：【{new_dept_name}】！系統已動態更新選單。")
                    st.rerun()
                except Exception as db_err:
                    st.error(f"⚠️ 寫入資料庫失敗（可能是資料表尚未建立）：{str(db_err)}")
            else:
                st.error("⚠️ 請輸入有效的部門名稱！")
