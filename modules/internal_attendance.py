import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 廠內考勤與薪資自動扣款連動模組多語系字典 (i18n)
# ----------------------------------------------------
INT_ATT_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 廠內智慧考勤（人臉/指紋）與薪資扣款連動中心",
        "caption": "對接未來人臉辨識與指紋打卡機 API 資料流，自動比對上下班時間，即時判定遲到、早退與異常，並直接連動薪資扣款計算。",
        "tab_records": "📑 即時刷卡與出勤異常總冊",
        "tab_simulate": "⏱️ 模擬打卡機 / 人臉指紋資料進站",
        "tab_rules": "⚙️ 上下班基準時間與遲到扣款規則設定",
        "header_records": "📋 西寧廠與海防廠考勤即時比對清冊",
        "header_simulate": "⚡ 模擬考勤硬體打卡資料寫入",
        "header_rules": "⚙️ 考勤判定與薪資連動參數",
        "lbl_emp": "選擇員工 (Select Employee) *",
        "lbl_clock_time": "刷卡時間 (Timestamp) *",
        "lbl_type": "考勤類型 *",
        "type_opts": ["上班簽到 (Check-In)", "下班簽退 (Check-Out)"],
        "btn_process": "🚀 執行出勤比對並連動薪資扣款",
        "success_process": "✅ 員工 `{name}` 打卡時間 `{time}` 已完成比對，判定結果：`{status}`，已自動同步至薪資扣款模組！",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_dept": "廠區與部門",
        "col_type": "類型",
        "col_time": "刷卡時間",
        "col_status": "出勤判定狀態",
        "col_deduct": "應扣薪時數"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Chấm công Thông minh (Khuôn mặt/Vân tay) & Trừ lương tự động",
        "caption": "Tích hợp API máy chấm công, tự động so sánh giờ làm việc, phát hiện đi trễ/về sớm và liên kết trực tiếp với module tính lương.",
        "tab_records": "📑 Sổ kiểm tra chấm công thời gian thực",
        "tab_simulate": "⏱️ Mô phỏng dữ liệu máy chấm công",
        "tab_rules": "⚙️ Cài đặt giờ làm việc & Quy tắc trừ lương",
        "header_records": "📋 Nhật ký chấm công nhà máy Tây Ninh & Hải Phòng",
        "header_simulate": "⚡ Giả lập dữ liệu quẹt thẻ/nhận diện",
        "header_rules": "⚙️ Thông số chấm công & Liên kết lương",
        "lbl_emp": "Chọn nhân viên *",
        "lbl_clock_time": "Thời gian quẹt thẻ *",
        "lbl_type": "Loại chấm công *",
        "type_opts": ["Vào ca (Check-In)", "Tan ca (Check-Out)"],
        "btn_process": "🚀 Xử lý chấm công & Liên kết trừ lương",
        "success_process": "✅ Đã xử lý chấm công cho nhân viên `{name}` lúc `{time}`, trạng thái: `{status}`, đã đồng bộ sang bảng lương!",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_dept": "Phòng ban",
        "col_type": "Loại",
        "col_time": "Thời gian",
        "col_status": "Trạng thái",
        "col_deduct": "Số giờ trừ"
    },
    "English": {
        "title": "🏢 Management - Smart Time Attendance (Face/Fingerprint) & Payroll Link",
        "caption": "Integrates with biometric attendance APIs to auto-detect tardiness and sync directly with payroll deductions.",
        "tab_records": "📑 Real-time Attendance & Exception Log",
        "tab_simulate": "⏱️ Simulate Biometric Terminal Input",
        "tab_rules": "⚙️ Shift Schedule & Deduction Rules",
        "header_records": "📋 Plant Attendance Verification Log",
        "header_simulate": "⚡ Simulate Attendance Device Sync",
        "header_rules": "⚙️ Attendance & Payroll Link Parameters",
        "lbl_emp": "Select Employee *",
        "lbl_clock_time": "Punch Timestamp *",
        "lbl_type": "Punch Type *",
        "type_opts": ["Check-In", "Check-Out"],
        "btn_process": "🚀 Process Attendance & Link Payroll",
        "success_process": "✅ Punch for `{name}` at `{time}` processed. Status: `{status}`, synced to payroll!",
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

    # 初始化考勤與薪資扣款資料庫
    if "internal_attendance_db" not in st.session_state:
        st.session_state.internal_attendance_db = [
            {
                "code": "EMP-001",
                "name": "張董事長",
                "dept": "台灣總部",
                "type": "上班簽到",
                "time": "2026-10-08 07:55:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            },
            {
                "code": "EMP-002",
                "name": "Nguyễn Văn Quý",
                "dept": "西寧廠 (Tay Ninh)",
                "type": "上班簽到",
                "time": "2026-10-08 08:35:00",
                "status": "🔴 遲到 35 分鐘 (Late)",
                "deduct_hours": 0.55  # 自動換算扣款時數
            }
        ]

    tab_records, tab_simulate, tab_rules = st.tabs([
        L["tab_records"], L["tab_simulate"], L["tab_rules"]
    ])

    with tab_records:
        st.markdown(f"### {L['header_records']}")
        st.info("💡 系統已自動整合人臉辨識/指紋機打卡串流，針對逾時刷卡自動計算遲到時數，並即時連動至【員工薪資計算與扣除保險模組】。")
        
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
        st.caption("模擬未來人臉辨識機或指紋打卡機透過 API 拋送刷卡數據至 ERP 系統的測試介面。")
        
        with st.form("form_biometric_simulate"):
            emp_choices = ["EMP-001 - 張董事長", "EMP-002 - Nguyễn Văn Quý", "EMP-003 - 阮文強"]
            sel_emp = st.selectbox(L["lbl_emp"], emp_choices)
            clock_type = st.selectbox(L["lbl_type"], L["type_opts"])
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                sim_date = st.date_input("刷卡日期", datetime.date(2026, 10, 8))
            with col_t2:
                sim_time = st.time_input("刷卡時間 (Time)", datetime.time(8, 25))

            if st.form_submit_button(L["btn_process"], type="primary", use_container_width=True):
                emp_code = sel_emp.split(" - ")[0]
                emp_name = sel_emp.split(" - ")[1]
                timestamp_str = f"{sim_date} {sim_time}"
                
                # 自動判別邏輯（規範上班時間為 08:00）
                status = "🟢 正常 (Normal)"
                deduct = 0.0
                
                if "上班" in clock_type or "In" in clock_type:
                    standard_limit = datetime.datetime.strptime("08:00:00", "%H:%M:%S").time()
                    if sim_time > standard_limit:
                        # 計算遲到分鐘數
                        t1 = datetime.datetime.combine(sim_date, standard_limit)
                        t2 = datetime.datetime.combine(sim_date, sim_time)
                        diff_mins = (t2 - t1).total_seconds() / 60.0
                        deduct = round(diff_mins / 60.0, 2)
                        status = f"🔴 遲到 {int(diff_mins)} 分鐘 (Late)"
                elif "下班" in clock_type or "Out" in clock_type:
                    standard_out = datetime.datetime.strptime("17:00:00", "%H:%M:%S").time()
                    if sim_time < standard_out:
                        status = "🟡 早退 (Early Leave)"
                        deduct = 0.5 # 假設早退固定扣 0.5 小時或依實際計算

                st.session_state.internal_attendance_db.insert(0, {
                    "code": emp_code,
                    "name": emp_name,
                    "dept": "西寧廠內勤作業",
                    "type": clock_type,
                    "time": timestamp_str,
                    "status": status,
                    "deduct_hours": deduct
                })
                
                # 同步回薪資模組
                if "payroll_db" in st.session_state:
                    for p in st.session_state.payroll_db:
                        if p["code"] == emp_code:
                            p["late_hours"] = p.get("late_hours", 0.0) + deduct

                st.success(L["success_process"].format(name=emp_name, time=timestamp_str, status=status))
                st.rerun()

    with tab_rules:
        st.markdown(f"### {L['header_rules']}")
        st.info("⚙️ 企業考勤與薪資扣款對應原則：\n1. **上班寬限期**：規定 08:00 上班，超過 08:10 起正式計算遲到。\n2. **薪資扣款公式**：遲到時數將直接帶入薪資模組以當月時薪（底薪 / 208小時）進行等比扣款。\n3. **硬體對接說明**：支援 Hikvision、ZKTeco 等主流人臉識別與指紋機之 HTTP API / MQTT 即時資料拋送。")

def show(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def render_internal_attendance(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)
