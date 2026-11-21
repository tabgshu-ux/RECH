# ==========================================
# 檔案路徑：modules/management/hr/employee/employee_list.py
# 職責：L2 行政／人事 - 現職員工總名冊查詢與離職辦理
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

EMP_LIST_I18N = {
    "繁體中文": {
        "title": "📋 現職員工總名冊",
        "group_filter": "📂 選擇檢視群組",
        "group_vn": "🇻🇳 越南籍員工名冊",
        "group_expat": "🌐 外派與外籍幹部名冊",
        "group_all": "📋 全部員工總名冊",
        "search_label": "🔍 搜尋員工姓名、工號或部門篩選",
        "search_placeholder": "輸入工號、姓名或部門關鍵字...",
        "terminate_section": "🔄 員工離職狀態異動與結清處理",
        "select_terminate": "選擇要辦理離職的員工 (工號 - 姓名)",
        "btn_terminate": "🔴 辦理離職手續並移至離職名冊",
        "success_terminate": "✅ 員工 `{emp}` 已成功辦理離職！",
        "no_data": "目前尚無在職員工紀錄。",
        "no_conn": "資料庫引擎未連線。",
    },
    "Tiếng Việt": {
        "title": "📋 Danh sách nhân viên đang làm việc",
        "group_filter": "📂 Chọn nhóm hiển thị",
        "group_vn": "🇻🇳 Nhân viên Việt Nam",
        "group_expat": "🌐 Chuyên gia nước ngoài",
        "group_all": "📋 Tất cả nhân sự",
        "search_label": "🔍 Tìm kiếm theo tên, mã NV hoặc bộ phận",
        "search_placeholder": "Nhập từ khóa...",
        "terminate_section": "🔄 Xử lý thủ tục nghỉ việc",
        "select_terminate": "Chọn nhân viên nghỉ việc",
        "btn_terminate": "🔴 Xác nhận nghỉ việc",
        "success_terminate": "✅ Đã chuyển nhân viên `{emp}` sang danh sách nghỉ việc!",
        "no_data": "Hiện chưa có dữ liệu nhân viên.",
        "no_conn": "Chưa kết nối cơ sở dữ liệu.",
    },
    "English": {
        "title": "📋 Active Employee Registry",
        "group_filter": "📂 Select Group View",
        "group_vn": "🇻🇳 Vietnamese Staff",
        "group_expat": "🌐 Expat & Foreign Staff",
        "group_all": "📋 All Employees",
        "search_label": "🔍 Search by Name, ID or Department",
        "search_placeholder": "Enter keyword...",
        "terminate_section": "🔄 Process Employee Termination",
        "select_terminate": "Select Employee to Terminate",
        "btn_terminate": "🔴 Confirm Termination",
        "success_terminate": "✅ Employee `{emp}` moved to resigned list!",
        "no_data": "No employee records found.",
        "no_conn": "Database engine not connected.",
    },
}


def render_employee_list(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in EMP_LIST_I18N else "繁體中文"
    L = EMP_LIST_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS staff_type VARCHAR(100) DEFAULT '越南籍員工';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS attendance_mode VARCHAR(50) DEFAULT '需打卡';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT '在職';"))

            query = """
                SELECT DISTINCT
                    COALESCE(e.emp_code, p.emp_code) AS emp_code,
                    COALESCE(e.emp_name, p.emp_name) AS emp_name,
                    COALESCE(e.department, p.department) AS department,
                    COALESCE(e.position, '-') AS position,
                    COALESCE(e.staff_type, '越南籍員工') AS staff_type,
                    COALESCE(e.attendance_mode, '需打卡') AS attendance_mode,
                    COALESCE(e.base_salary, p.base_salary, 0) AS base_salary,
                    COALESCE(e.status, '在職') AS status
                FROM public.payroll_records p
                FULL OUTER JOIN public.employee_profiles e ON p.emp_code = e.emp_code
                WHERE COALESCE(e.status, '在職', p.status) = '在職';
            """
            df = pd.read_sql(query, con=engine)

            if not df.empty:
                category_filter = st.radio(
                    L["group_filter"],
                    [L["group_vn"], L["group_expat"], L["group_all"]],
                    horizontal=True,
                )

                if L["group_vn"] in category_filter:
                    df_view = df[~df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                elif L["group_expat"] in category_filter:
                    df_view = df[df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                else:
                    df_view = df

                search_query = st.text_input(L["search_label"], placeholder=L["search_placeholder"])
                if search_query:
                    mask = df_view.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                    df_filtered = df_view[mask]
                else:
                    df_filtered = df_view

                st.dataframe(df_filtered, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown(f"#### {L['terminate_section']}")
                active_emp_list = [f"{r['emp_code']} - {r['emp_name']}" for _, r in df.iterrows()]
                selected_to_terminate = st.selectbox(L["select_terminate"], active_emp_list)

                if st.button(L["btn_terminate"], type="secondary"):
                    if selected_to_terminate:
                        target_emp_no = selected_to_terminate.split(" - ")[0]
                        target_emp_name = selected_to_terminate.split(" - ", 1)[1] if " - " in selected_to_terminate else target_emp_no
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO public.employee_profiles (emp_code, emp_name, status)
                                    VALUES (:no, :name, '離職')
                                    ON CONFLICT (emp_code) DO UPDATE SET status = '離職';
                                """),
                                {"no": target_emp_no, "name": target_emp_name},
                            )
                        st.success(L["success_terminate"].format(emp=selected_to_terminate))
                        st.rerun()
            else:
                st.info(L["no_data"])
        except Exception as e:
            st.warning(f"⚠️ 讀取名冊發生異常：{str(e)}")
    else:
        st.info(L["no_conn"])


def render(engine=None, lang="繁體中文", **kwargs):
    return render_employee_list(engine=engine, lang=lang, **kwargs)


def show(engine=None, lang="繁體中文", **kwargs):
    return render_employee_list(engine=engine, lang=lang, **kwargs)
