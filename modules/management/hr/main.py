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
            from modules.management.hr.employee import employee_list
            employee_list.render(db_engine=db_engine, lang=lang)
        except Exception as e:
            st.info("📂 正在載入員工檔案管理模組...")
            # 載入現有檔案備用
            try:
                import employee_list
                employee_list.render(db_engine=db_engine, lang=lang)
            except Exception:
                st.warning("請確認 employee_list 模組路徑。")

    elif "考勤" in sub_tab:
        try:
            from modules.management.hr.attendance import attendance_punch
            attendance_punch.render(db_engine=db_engine, lang=lang)
        except Exception as e:
            st.info("⏱️ 正在載入考勤打卡與審核模組...")
            try:
                import attendance_punch
                attendance_punch.render(db_engine=db_engine, lang=lang)
            except Exception:
                st.warning("請確認 attendance_punch 模組路徑。")

    elif "薪資" in sub_tab:
        try:
            import payroll_management
            payroll_management.render(db_engine=db_engine, lang=lang)
        except Exception as e:
            st.info("💰 正在載入薪資與 BHXH 保險計算模組...")
