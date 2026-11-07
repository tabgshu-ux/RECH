# ==========================================
# 檔案路徑：modules/management/hr/main.py
# 職責：人事行政（HR）模組統一調度中心
# ==========================================

import streamlit as st

def render(db_engine=None, lang="繁體中文", **kwargs):
    st.subheader("👔 人事行政與員工管理中心")
    st.caption("在此統一管理員工履歷、護照工作證、考勤打卡與薪資保險。")
    st.markdown("---")

    # 提供子分頁導覽
    sub_tab = st.radio(
        "📌 選擇人事管理子功能", 
        ["👥 員工與外勞檔案管理", "⏱️ 考勤打卡與請假紀錄", "💰 薪資計算與 BHXH 保險"],
        horizontal=True
    )
    
    st.markdown("---")

    if "員工" in sub_tab:
        try:
            # 依據實際目錄結構：modules/management/hr/employee/employee_list.py
            from modules.management.hr.employee import employee_list
            if hasattr(employee_list, "render"):
                employee_list.render(db_engine=db_engine, lang=lang)
            else:
                st.warning("employee_list 模組未包含 render 函式。")
        except Exception as e:
            st.error(f"載入員工模組失敗: {e}")

    elif "考勤" in sub_tab:
        try:
            # 依據實際目錄結構：modules/management/hr/attendance/attendance_punch.py
            from modules.management.hr.attendance import attendance_punch
            if hasattr(attendance_punch, "render"):
                attendance_punch.render(db_engine=db_engine, lang=lang)
            else:
                st.warning("attendance_punch 模組未包含 render 函式。")
        except Exception as e:
            st.error(f"載入考勤模組失敗: {e}")

    elif "薪資" in sub_tab:
        try:
            # 依據實際目錄結構：modules/management/hr/payroll_management.py
            import payroll_management
            if hasattr(payroll_management, "render"):
                payroll_management.render(db_engine=db_engine, lang=lang)
            else:
                st.warning("payroll_management 模組未包含 render 函式。")
        except Exception as e:
            # 嘗試從同級目錄匯入
            try:
                from . import payroll_management
                payroll_management.render(db_engine=db_engine, lang=lang)
            except Exception as e2:
                st.error(f"載入薪資模組失敗: {e2}")
