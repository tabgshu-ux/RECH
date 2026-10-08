import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 廠內員工打卡與出勤模組多語系字典 (i18n)
# ----------------------------------------------------
INT_ATT_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 廠內員工固定打卡與出勤管理中心",
        "caption": "管理西寧廠與海防廠內勤員工、作業員之上下班刷卡紀錄、遲到早退統計、加班時數與出勤異常審核，並直接連動薪資扣款模組。",
        "tab_records": "📑 廠內今日出勤與刷卡總冊",
        "tab_clock": "⏱️ 內勤員工上下班打卡",
        "tab_stats": "📊 月度出勤統計與薪資連動",
        "header_records": "📋 西寧廠與海防廠內勤即時打卡紀錄",
        "header_clock": "⏱️ 廠內固定終端機 / 人事代打卡登記",
        "header_stats": "📊 員工月度出勤與薪資扣款時數彙總",
        "lbl_emp": "選擇員工 (Select Employee) *",
        "lbl_type": "打卡類型 (Clock Type) *",
        "type_opts": ["上班簽到 (Check-In)", "下班簽退 (Check-Out)"],
        "lbl_note": "備註說明 / 異常原因 (如: 公出、遲到)",
        "btn_clock": "💾 確認送出打卡紀錄",
        "success_clock": "✅ 員工 `{name}` 於 `{time}` 成功完成廠內打卡！",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_dept": "部門/廠區",
        "col_type": "類型",
        "col_time": "打卡時間",
        "col_status": "出勤狀態"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Chấm công & Điểm danh Nhân viên Nội bộ",
        "caption": "Quản lý thời gian ra vào, thống kê đi trễ/về sớm, tăng ca và liên kết trực tiếp với module tính lương.",
        "tab_records": "📑 Sổ điểm danh nội bộ hôm nay",
        "tab_clock": "⏱️ Chấm công nhân viên nội bộ",
        "tab_stats": "📊 Thống kê chấm công tháng & Liên kết lương",
        "header_records": "📋 Nhật ký chấm công nhà máy Tây Ninh & Hải Phòng",
        "header_clock": "⏱️ Đăng ký chấm công tại văn phòng/nhà máy",
        "header_stats": "📊 Tổng hợp giờ công tháng để tính lương",
        "lbl_emp": "Chọn nhân viên *",
        "lbl_type": "Loại chấm công *",
        "type_opts": ["Vào ca (Check-In)", "Tan ca (Check-Out)"],
        "lbl_note": "Ghi chú / Lý do đi trễ",
        "btn_clock": "💾 Lưu bản ghi chấm công",
        "success_clock": "✅ Đã chấm công thành công cho nhân viên `{name}` lúc `{time}`!",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_dept": "Phòng ban",
        "col_type": "Loại",
        "col_time": "Thời gian",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🏢 Management - Internal Employee Attendance & Time Clock Center",
        "caption": "Manage internal staff and factory worker clock-ins, late arrivals, overtime, and integrate with payroll deductions.",
        "tab_records": "📑 Today's Internal Attendance Log",
        "tab_clock": "⏱️ Internal Time Clock Terminal",
        "tab_stats": "📊 Monthly Attendance & Payroll Summary",
        "header_records": "📋 Plant Internal Attendance Records",
        "header_clock": "⏱️ Staff Time Clock Registration",
        "header_stats": "📊 Monthly Attendance & Deduction Summary",
        "lbl_emp": "Select Employee *",
        "lbl_type": "Clock Type *",
        "type_opts": ["Check-In", "Check-Out"],
        "lbl_note": "Notes / Exception Reason",
        "btn_clock": "💾 Save Attendance Record",
        "success_clock": "✅ Attendance recorded for `{name}` at `{time}` successfully!",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_dept": "Department",
        "col_type": "Type",
        "col_time": "Timestamp",
        "col_status": "Status"
    }
}

def render_internal_attendance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in INT_ATT_I18N else "繁體中文"
    L = INT_ATT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    if "internal_attendance_db" not in st.session_state:
        st.session_state.internal_attendance_db = [
            {
                "code": "EMP-001",
                "name": "張董事長",
                "dept": "總經理室 (台灣總部)",
                "type": "上班簽到",
                "time": "2026-10-08 07:50:12",
                "status": "🟢 正常 (Normal)"
            },
            {
                "code": "EMP-002",
                "name": "Nguyễn Văn Quý",
                "dept": "管理部 (西寧廠)",
                "type": "上班簽到",
                "time": "2026-10-08 08:15:30",
                "status": "🟡 遲到 15 分鐘 (Late)"
            }
        ]

    tab_records, tab_clock, tab_stats = st.tabs([
        L["tab_records"], L["tab_clock"], L["tab_stats"]
    ])

    with tab_records:
        st.markdown(f"### {L['header_records']}")
        if st.session_state.internal_attendance_db:
            display_data = []
            for idx, item in enumerate(st.session_state.internal_attendance_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_dept"]: item["dept"],
                    L["col_type"]: item["type"],
                    L["col_time"]: item["time"],
                    L["col_status"]: item["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info("目前尚無廠內打卡紀錄。")

    with tab_clock:
        st.markdown(f"### {L['header_clock']}")
        with st.form("form_internal_clock"):
            emp_choices = ["EMP-001 - 張董事長", "EMP-002 - Nguyễn Văn Quý", "EMP-003 - 阮文強"]
            sel_emp = st.selectbox(L["lbl_emp"], emp_choices)
            clock_type = st.selectbox(L["lbl_type"], L["type_opts"])
            note = st.text_input(L["lbl_note"])

            if st.form_submit_button(L["btn_clock"], type="primary", use_container_width=True):
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                emp_name = sel_emp.split(" - ")[1]
                emp_code = sel_emp.split(" - ")[0]
                
                status = "🟢 正常 (Normal)"
                if "上班" in clock_type or "In" in clock_type:
                    current_hour = datetime.datetime.now().hour
                    current_minute = datetime.datetime.now().minute
                    if current_hour > 8 or (current_hour == 8 and current_minute > 0):
                        status = "🟡 遲到 (Late)"

                st.session_state.internal_attendance_db.insert(0, {
                    "code": emp_code,
                    "name": emp_name,
                    "dept": "管理部 / 廠區內勤",
                    "type": clock_type,
                    "time": now_str,
                    "status": status
                })
                st.success(L["success_clock"].format(name=emp_name, time=now_str))
                st.rerun()

    with tab_stats:
        st.markdown(f"### {L['header_stats']}")
        st.info("💡 系統已自動將廠內人員之月度遲到時數、請假扣薪時數與加班時數彙整，可隨時同步至【員工薪資計算與保險扣除模組】進行扣款計算。")
        
        monthly_stats = [
            {"工號": "EMP-001", "姓名": "張董事長", "本月出勤天數": "26 天", "遲到總時數": "0 小時", "請假時數": "0 小時", "薪資連動狀態": "🟢 正常計算"},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn Quý", "本月出勤天數": "26 天", "遲到總時數": "1.5 小時", "請假時數": "0 小時", "薪資連動狀態": "🟢 已自動帶入遲到扣款"}
        ]
        st.dataframe(pd.DataFrame(monthly_stats), use_container_width=True)

def show(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def render_internal_attendance(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)
