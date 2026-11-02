import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

EMP_LIST_I18N = {
    "繁體中文": {
        "title": "📑 現職員工總名冊、證件預警與外派打卡串聯",
        "group_filter": "📂 選擇檢視群組",
        "group_vn": "🇻🇳 越南籍員工名冊",
        "group_expat": "🌐 外派與外籍幹部名冊",
        "group_site_dispatch": "🏗️ 工程外派工地人員與打卡紀錄",
        "group_all": "📋 全部員工總名冊",
        "alert_title": "🚨 外派/外籍幹部證件（簽證/TRC/護照）90天前提前到期預警（越南辦事需時3個月）",
        "expired_msg": "🔴 **【已過期】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，已逾期 `{dleft}` 天！)",
        "warning_msg": "⚠️ **【90天內到期提醒】** 幹部：`{eno} - {ename}` (證件到期日：`{edate}`，僅剩 `{dleft}` 天，請盡速送件)",
        "search_label": "🔍 搜尋員工姓名、工號或部門篩選",
        "search_placeholder": "輸入工號、姓名或部門關鍵字...",
        "terminate_section": "🔄 員工離職狀態異動與結清處理",
        "select_terminate": "選擇要辦理離職的員工 (工號 - 姓名)",
        "btn_terminate": "🔴 辦理離職手續並移至離職名冊",
        "success_terminate": "✅ 員工 `{emp}` 已成功辦理離職！",
        "no_data": "目前尚無在職員工紀錄。",
        "no_conn": "資料庫引擎未連線。"
    },
    "Tiếng Việt": {
        "title": "📑 Danh sách nhân sự & Cảnh báo hạn sử dụng",
        "group_filter": "📂 Chọn nhóm hiển thị",
        "group_vn": "🇻🇳 Nhân viên Việt Nam",
        "group_expat": "🌐 Chuyên gia nước ngoài",
        "group_site_dispatch": "🏗️ Nhân sự đi công tác ngoài công trường & Chấm công",
        "group_all": "📋 Tất cả nhân sự",
        "alert_title": "🚨 Cảnh báo trước 90 ngày hạn sử dụng giấy tờ (Visa/TRC/Hộ chiếu)",
        "expired_msg": "🔴 **【Đã hết hạn】** Chuyên gia: `{eno} - {ename}` (Hết hạn: `{edate}`, quá hạn `{dleft}` ngày!)",
        "warning_msg": "⚠️ **【Cảnh báo 90 ngày】** Chuyên gia: `{eno} - {ename}` (Hết hạn: `{edate}`, còn lại `{dleft}` ngày)",
        "search_label": "🔍 Tìm kiếm theo tên, mã NV hoặc bộ phận",
        "search_placeholder": "Nhập từ khóa...",
        "terminate_section": "🔄 Xử lý thủ tục nghỉ việc",
        "select_terminate": "Chọn nhân viên nghỉ việc",
        "btn_terminate": "🔴 Xác nhận nghỉ việc",
        "success_terminate": "✅ Đã chuyển nhân viên `{emp}` sang danh sách nghỉ việc!",
        "no_data": "Hiện chưa có dữ liệu nhân viên.",
        "no_conn": "Chưa kết nối cơ sở dữ liệu."
    },
    "English": {
        "title": "📑 Employee Registry & Site Dispatch Tracking",
        "group_filter": "📂 Select Group View",
        "group_vn": "🇻🇳 Vietnamese Staff",
        "group_expat": "🌐 Expat & Foreign Staff",
        "group_site_dispatch": "🏗️ Site Dispatch & Attendance",
        "group_all": "📋 All Employees",
        "alert_title": "🚨 Expat 90-Day Advance Document Expiry Alerts (Visa/TRC/Passport)",
        "expired_msg": "🔴 **[Expired]** Expat: `{eno} - {ename}` (Expiry: `{edate}`, Overdue by `{dleft}` days!)",
        "warning_msg": "⚠️ **[90-Day Warning]** Expat: `{eno} - {ename}` (Expiry: `{edate}`, Remaining: `{dleft}` days)",
        "search_label": "🔍 Search by Name, ID or Department",
        "search_placeholder": "Enter keyword...",
        "terminate_section": "🔄 Process Employee Termination",
        "select_terminate": "Select Employee to Terminate",
        "btn_terminate": "🔴 Confirm Termination",
        "success_terminate": "✅ Employee `{emp}` moved to resigned list!",
        "no_data": "No employee records found.",
        "no_conn": "Database engine not connected."
    }
}

def render_employee_list(engine=None, lang="繁體中文"):
    active_lang = lang if lang in EMP_LIST_I18N else "繁體中文"
    L = EMP_LIST_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS staff_type VARCHAR(100) DEFAULT '越南籍員工';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS attendance_mode VARCHAR(50) DEFAULT '需打卡';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS visa_expire DATE DEFAULT '2027-12-31';"))
                conn.execute(text("ALTER TABLE public.employee_profiles ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT '在職';"))

            query = """
                SELECT DISTINCT 
                    COALESCE(e.emp_code, p.emp_code) as emp_code,
                    COALESCE(e.emp_name, p.emp_name) as emp_name,
                    COALESCE(e.department, p.department) as department,
                    COALESCE(e.position, '-') as position,
                    COALESCE(e.staff_type, '越南籍員工 (VN Local Staff)') as staff_type,
                    COALESCE(e.attendance_mode, '需打卡 (Required Punch)') as attendance_mode,
                    COALESCE(e.base_salary, p.base_salary, 0) as base_salary,
                    COALESCE(e.visa_expire, '2027-12-31') as visa_expire,
                    COALESCE(e.status, '在職') as status
                FROM public.payroll_records p
                FULL OUTER JOIN public.employee_profiles e ON p.emp_code = e.emp_code
                WHERE COALESCE(e.status, '在職', p.status) = '在職';
            """
            df = pd.read_sql(query, con=engine)
            
            if not df.empty:
                category_filter = st.radio(
                    L["group_filter"], 
                    [L["group_vn"], L["group_expat"], L["group_site_dispatch"], L["group_all"]], 
                    horizontal=True
                )
                
                # 依據選擇群組篩選顯示
                if L["group_vn"] in category_filter:
                    df_view = df[~df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                elif L["group_expat"] in category_filter:
                    df_view = df[df["staff_type"].str.contains("外派|外籍|Expat", na=False)]
                elif L["group_site_dispatch"] in category_filter:
                    st.markdown("#### 🏗️ 工程部填報之外派工地人員與出勤打卡紀錄串聯")
                    try:
                        # 嘗試從工程外派表中撈取資料進行串聯顯示
                        df_site = pd.read_sql("SELECT * FROM public.engineering_site_dispatches ORDER BY start_date DESC;", con=engine)
                        if not df_site.empty:
                            st.info("💡 以下為工程部填單外派至各外部工地的技術人員名單與任務資訊：")
                            st.dataframe(df_site, use_container_width=True, hide_index=True)
                        else:
                            st.warning("⚠️ 目前工程部尚未建立任何外派工地派遣單。")
                    except Exception:
                        st.info("💡 尚未建立工程外派工地資料表（engineering_site_dispatches）。")
                    return # 提早結束，避免下方顯示一般總名冊
                else:
                    df_view = df

                # 90天證件預警（針對外派外籍幹部）
                today_date = datetime.date.today()
                expiring_soon = []
                for _, row in df.iterrows():
                    v_exp = row.get("visa_expire")
                    if v_exp and ("外派" in str(row.get("staff_type", "")) or "外籍" in str(row.get("staff_type", ""))):
                        if isinstance(v_exp, str):
                            try:
                                v_exp = datetime.datetime.strptime(v_exp, "%Y-%m-%d").date()
                            except:
                                continue
                        days_left = (v_exp - today_date).days
                        if days_left <= 90:
                            expiring_soon.append((row["emp_code"], row["emp_name"], v_exp, days_left))

                if expiring_soon:
                    st.error(L["alert_title"])
                    for eno, ename, edate, dleft in expiring_soon:
                        if dleft < 0:
                            st.markdown(L["expired_msg"].format(eno=eno, ename=ename, edate=edate, dleft=abs(dleft)))
                        else:
                            st.markdown(L["warning_msg"].format(eno=eno, ename=ename, edate=edate, dleft=dleft))
                    st.markdown("---")

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
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.employee_profiles (emp_code, emp_name, status)
                                VALUES (:no, :name, '離職')
                                ON CONFLICT (emp_code) DO UPDATE SET status = '離職';
                            """), {"no": target_emp_no, "name": selected_to_terminate.split(" - ")[1]})
                        st.success(L["success_terminate"].format(emp=selected_to_terminate))
                        st.rerun()
            else:
                st.info(L["no_data"])
        except Exception as e:
            st.warning(f"⚠️ 讀取名冊發生異常：{str(e)}")
    else:
        st.info(L["no_conn"])
