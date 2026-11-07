# ==========================================
# 檔案路徑：modules/management/hr/main.py
# 職責：人事行政（HR）模組統一調度中心（具備函式自動探測防護機制）
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
            from modules.management.hr.employee import employee_list
            # 自動探測子模組中可用的渲染函式
            func = getattr(employee_list, "render", None) or \
                   getattr(employee_list, "render_employee_list", None) or \
                   getattr(employee_list, "main", None)
            if func:
                func(db_engine=db_engine, lang=lang)
            else:
                st.info("📂 員工檔案模組已載入，但未找到標準渲染入口。顯示可用屬性：")
                st.write([m for m in dir(employee_list) if not m.startswith("_")])
        except Exception as e:
            st.error(f"載入員工模組失敗: {e}")

    elif "考勤" in sub_tab:
        try:
            from modules.management.hr.attendance import attendance_punch
            func = getattr(attendance_punch, "render", None) or \
                   getattr(attendance_punch, "render_attendance_punch", None) or \
                   getattr(attendance_punch, "main", None)
            if func:
                func(db_engine=db_engine, lang=lang)
            else:
                st.info("⏱️ 考勤打卡模組已載入，但未找到標準渲染入口。")
        except Exception as e:
            st.error(f"載入考勤模組失敗: {e}")

    elif "薪資" in sub_tab:
        try:
            # 嘗試從同級目錄或指定路徑引入薪資模組
            import sys
            from pathlib import Path
            hr_dir = Path(__file__).parent
            if str(hr_dir) not in sys.path:
                sys.path.append(str(hr_dir))
                
            import payroll_management
            func = getattr(payroll_management, "render", None) or \
                   getattr(payroll_management, "render_payroll_management", None) or \
                   getattr(payroll_management, "main", None)
            if func:
                func(db_engine=db_engine, lang=lang)
            else:
                st.info("💰 薪資計算模組已載入，但未找到標準渲染入口。")
        except Exception as e:
            st.error(f"載入薪資模組失敗: {e}")
