import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 廠內考勤與彈性緩衝扣款模組多語系字典 (i18n)
# ----------------------------------------------------
INT_ATT_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 廠內智慧考勤與彈性緩衝扣款設定中心",
        "caption": "設定每日打卡容許緩衝時間與每月累計免扣款額度，自動化判定遲到並精準連動薪資扣款。",
        "tab_records": "📑 即時刷卡紀錄與出勤判定",
        "tab_simulate": "⏱️ 模擬打卡機 / 人臉指紋資料進站",
        "tab_rules": "⚙️ 彈性緩衝時間與扣款規則設定",
        "header_records": "📋 西寧廠與海防廠出勤判定清冊",
        "header_simulate": "⚡ 模擬硬體打卡資料寫入與即時比對",
        "header_rules": "⚙️ 考勤緩衝與扣薪參數設定",
        "lbl_emp": "選擇員工 (Select Employee) *",
        "lbl_clock_time": "刷卡時間 *",
        "lbl_type": "考勤類型 *",
        "type_opts": ["上班簽到 (Check-In)", "下班簽退 (Check-Out)"],
        "btn_process": "🚀 執行出勤比對並連動薪資扣款",
        "success_process": "✅ 員工 `{name}` 打卡時間 `{time}` 處理完成！判定：`{status}`",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_dept": "廠區與部門",
        "col_type": "類型",
        "col_time": "刷卡時間",
        "col_status": "出勤判定狀態",
        "col_deduct": "實質扣款時數"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Chấm công & Cài đặt Thời gian Ân hạn linh hoạt",
        "caption": "Cài đặt thời gian ân hạn hàng ngày và tổng phút miễn trừ hàng tháng, tự động tính toán trừ lương.",
        "tab_records": "📑 Sổ kiểm tra chấm công",
        "tab_simulate": "⏱️ Mô phỏng dữ liệu máy chấm công",
        "tab_rules": "⚙️ Cài đặt thời gian ân hạn & Quy tắc trừ lương",
        "header_records": "📋 Nhật ký chấm công nhà máy",
        "header_simulate": "⚡ Giả lập quẹt thẻ",
        "header_rules": "⚙️ Thiết lập tham số ân hạn",
        "lbl_emp": "Chọn nhân viên *",
        "lbl_clock_time": "Thời gian quẹt thẻ *",
        "lbl_type": "Loại chấm công *",
        "type_opts": ["Vào ca (Check-In)", "Tan ca (Check-Out)"],
        "btn_process": "🚀 Xử lý chấm công & Liên kết lương",
        "success_process": "✅ Đã xử lý cho `{name}` lúc `{time}`, trạng thái: `{status}`",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_dept": "Phòng ban",
        "col_type": "Loại",
        "col_time": "Thời gian",
        "col_status": "Trạng thái",
        "col_deduct": "Giờ trừ"
    },
    "English": {
        "title": "🏢 Management - Smart Attendance & Flexible Grace Period Settings",
        "caption": "Configure daily grace periods and monthly cumulative exemptions for automated payroll deductions.",
        "tab_records": "📑 Attendance Log",
        "tab_simulate": "⏱️ Simulate Biometric Input",
        "tab_rules": "⚙️ Grace Period & Deduction Settings",
        "header_records": "📋 Attendance Verification Log",
        "header_simulate": "⚡ Simulate Device Sync",
        "header_rules": "⚙️ Grace Period Parameters",
        "lbl_emp": "Select Employee *",
        "lbl_clock_time": "Punch Timestamp *",
        "lbl_type": "Punch Type *",
        "type_opts": ["Check-In", "Check-Out"],
        "btn_process": "🚀 Process Attendance & Link Payroll",
        "success_process": "✅ Punch for `{name}` at `{time}` processed. Status: `{status}`",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_dept": "Department",
        "col_type": "Type",
        "col_time": "Timestamp",
        "col_status": "Status",
        "col_deduct": "Deduct Hours"
    }
}

def render_internal_attendance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in INT_ATT_I18N else "繁體中文"
    L = INT_ATT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化考勤全域設定（含緩衝時間）
    if "attendance_rules" not in st.session_state:
        st.session_state.attendance_rules = {
            "standard_in": "08:00:00",
            "standard_out": "17:00:00",
            "daily_grace_mins": 5,      # 預設每日容許緩衝 5 分鐘
            "monthly_exemption_mins": 30 # 預設每月累計免扣款緩衝 30 分鐘
        }

    if "internal_attendance_db" not in st.session_state:
        st.session_state.internal_attendance_db = [
            {
                "code": "EMP-001",
                "name": "張董事長",
                "dept": "西寧廠 (Tay Ninh)",
                "type": "上班簽到",
                "time": "2026-10-08 07:55:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            },
            {
                "code": "EMP-002",
                "name": "Nguyễn Văn Quý",
                "dept": "海防廠 (Hai Phong)",
                "type": "上班簽到",
                "time": "2026-10-08 08:12:00",
                "status": "🟡 遲到 12 分鐘 (超出每日 5 分鐘緩衝)",
                "deduct_hours": 0.12
            }
        ]

    tab_records, tab_simulate, tab_rules = st.tabs([
        L["tab_records"], L["tab_simulate"], L["tab_rules"]
    ])

    with tab_rules:
        st.markdown(f"### {L['header_rules']}")
        st.info("⚙️ 在此可依各越南廠區（西寧廠、海防廠）規範手動調整考勤緩衝與扣款門檻：")
        
        with st.form("form_attendance_rules"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                std_in_input = st.text_input("標準上班時間 (Standard Start Time)", value=st.session_state.attendance_rules["standard_in"])
                daily_grace_input = st.number_input("每日容許緩衝時間 (分鐘) [Daily Grace Period]", min_value=0, max_value=30, value=st.session_state.attendance_rules["daily_grace_mins"])
            with col_r2:
                std_out_input = st.text_input("標準下班時間 (Standard End Time)", value=st.session_state.attendance_rules["standard_out"])
                monthly_ex_input = st.number_input("每月累計免扣款緩衝額度 (分鐘) [Monthly Cumulative Exemption]", min_value=0, max_value=180, value=st.session_state.attendance_rules["monthly_exemption_mins"])

            if st.form_submit_button("💾 儲存考勤與緩衝規則設定", type="primary", use_container_width=True):
                st.session_state.attendance_rules["standard_in"] = std_in_input
                st.session_state.attendance_rules["standard_out"] = std_out_input
                st.session_state.attendance_rules["daily_grace_mins"] = int(daily_grace_input)
                st.session_state.attendance_rules["monthly_exemption_mins"] = int(monthly_ex_input)
                st.success("✅ 考勤與緩衝扣款規則已成功更新！系統將依此標準自動判定遲到。")

    with tab_records:
        st.markdown(f"### {L['header_records']}")
        rules = st.session_state.attendance_rules
        st.markdown(f"📌 **目前生效考勤標準**：上班 `{rules['standard_in']}` | 每日緩衝 `{rules['daily_grace_mins']} 分鐘` | 每月累計緩衝 `{rules['monthly_exemption_mins']} 分鐘`")
        
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
                    L["col_status"]: item["status"],
                    L["col_deduct"]: f"{item['deduct_hours']} 小時"
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info("目前尚無刷卡紀錄。")

    with tab_simulate:
        st.markdown(f"### {L['header_simulate']}")
        
        with st.form("form_biometric_simulate_rule"):
            emp_choices = ["EMP-001 - 張董事長 (西寧廠)", "EMP-002 - Nguyễn Văn Quý (海防廠)", "EMP-003 - 阮文強 (西寧廠)"]
            sel_emp = st.selectbox(L["lbl_emp"], emp_choices)
            clock_type = st.selectbox(L["lbl_type"], L["type_opts"])
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                sim_date = st.date_input("刷卡日期", datetime.date(2026, 10, 8))
            with col_t2:
                sim_time = st.time_input("刷卡時間 (Time)", datetime.time(8, 12))

            if st.form_submit_button(L["btn_process"], type="primary", use_container_width=True):
                emp_code = sel_emp.split(" - ")[0]
                emp_name = sel_emp.split(" - ")[1].split(" (")[0]
                emp_factory = "西寧廠 (Tay Ninh)" if "西寧廠" in sel_emp else "海防廠 (Hai Phong)"
                timestamp_str = f"{sim_date} {sim_time}"
                
                rules = st.session_state.attendance_rules
                std_time_obj = datetime.datetime.strptime(rules["standard_in"], "%H:%M:%S").time()
                
                status = "🟢 正常 (Normal)"
                deduct = 0.0
                
                if "上班" in clock_type or "In" in clock_type:
                    t1 = datetime.datetime.combine(sim_date, std_time_obj)
                    t2 = datetime.datetime.combine(sim_date, sim_time)
                    diff_mins = (t2 - t1).total_seconds() / 60.0
                    
                    if diff_mins > rules["daily_grace_mins"]:
                        net_late_mins = diff_mins - rules["daily_grace_mins"]
                        deduct = round(net_late_mins / 60.0, 2)
                        status = f"🔴 遲到 {int(diff_mins)} 分鐘 (扣除每日 {rules['daily_grace_mins']}m 緩衝，計 {int(net_late_mins)}m 遲到)"
                    elif diff_mins > 0:
                        status = f"🟢 雖遲到 {int(diff_mins)} 分鐘，但在每日 {rules['daily_grace_mins']} 分鐘緩衝內 (免扣)"
                    else:
                        status = "🟢 準時簽到 (Normal)"

                st.session_state.internal_attendance_db.insert(0, {
                    "code": emp_code,
                    "name": emp_name,
                    "dept": emp_factory,
                    "type": clock_type,
                    "time": timestamp_str,
                    "status": status,
                    "deduct_hours": deduct
                })
                
                if "payroll_db" in st.session_state:
                    for p in st.session_state.payroll_db:
                        if p["code"] == emp_code:
                            p["late_hours"] = p.get("late_hours", 0.0) + deduct

                st.success(L["success_process"].format(name=emp_name, time=timestamp_str, status=status))
                st.rerun()

def show(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def render_internal_attendance(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)
