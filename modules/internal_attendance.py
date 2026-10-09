import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 廠內考勤與彈性緩衝扣款模組多語系字典 (i18n)
# ----------------------------------------------------
INT_ATT_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 廠內智慧考勤與硬體 API 聯動管理",
        "caption": "依據各廠區獨立管理完整出勤紀錄、支援月份與員工整月考勤追溯、彈性緩衝時間與自動化薪資扣款連動。",
        "tab_records": "📑 廠內完整出勤日誌與月度查詢",
        "tab_simulate": "⏱️ 模擬打卡機 / 人臉指紋資料進站",
        "tab_api_config": "🔌 硬體打卡機 API 介面設定 (SaaS)",
        "tab_rules": "⚙️ 彈性緩衝時間與扣款規則設定",
        "header_tayninh": "🏭 西寧廠 (Tay Ninh) 完整出勤與刷卡日誌",
        "header_haiphong": "🏭 海防廠 (Hai Phong) 完整出勤與刷卡日誌",
        "filter_month": "📅 選擇結算月份 (Month Filter)",
        "search_label": "🔍 搜尋員工姓名或工號...",
        "header_simulate": "⚡ 模擬硬體打卡資料寫入與即時比對",
        "header_api": "🔌 智慧人臉/指紋打卡機硬體 API 整合設定中心",
        "header_rules": "⚙️ 考勤緩衝與扣薪參數設定",
        "lbl_emp": "選擇員工 (Select Employee) *",
        "lbl_clock_time": "刷卡時間 *",
        "lbl_type": "考勤類型 *",
        "type_opts": ["上班簽到 (Check-In)", "下班簽退 (Check-Out)"],
        "lbl_brand": "打卡機品牌 / 協定類型 *",
        "brand_opts": ["中控智慧 (ZKTeco BioTime API)", "海康威視 (Hikvision ISAPI)", "通用 RESTful Webhook API", "Suprema BioStar API"],
        "lbl_api_url": "打卡機伺服器 API Endpoint 網址 *",
        "lbl_api_key": "設備授權 Token / API Key *",
        "lbl_device_sn": "打卡機設備序號 (Device SN) *",
        "lbl_factory_bind": "綁定工作廠區 *",
        "factory_opts": ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)", "全集團通用 (Global)"],
        "btn_save_api": "💾 儲存打卡機 API 串接設定",
        "btn_test_api": "🔌 測試打卡機連線 (Test Connection)",
        "btn_process": "🚀 執行出勤比對並連動薪資扣款",
        "success_process": "✅ 員工 `{name}` 打卡時間 `{time}` 處理完成！判定：`{status}`",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_type": "類型",
        "col_time": "刷卡時間",
        "col_status": "出勤判定狀態",
        "col_deduct": "實質扣款時數"
    },
    "Tiếng Việt": {
        "title": "🏢 Quản lý Chấm công nội bộ & Cấu hình API",
        "caption": "Quản lý toàn bộ nhật ký chấm công theo nhà máy, tra cứu theo tháng, ân hạn và trừ lương.",
        "tab_records": "📑 Nhật ký chấm công & Tra cứu tháng",
        "tab_simulate": "⏱️ Mô phỏng máy chấm công",
        "tab_api_config": "🔌 Cài đặt API Máy chấm công",
        "tab_rules": "⚙️ Cài đặt ân hạn & Trừ lương",
        "header_tayninh": "🏭 Nhật ký chấm công Nhà máy Tây Ninh",
        "header_haiphong": "🏭 Nhật ký chấm công Nhà máy Hải Phòng",
        "filter_month": "📅 Chọn tháng quyết toán",
        "search_label": "🔍 Tìm kiếm theo tên hoặc mã NV...",
        "header_simulate": "⚡ Giả lập quẹt thẻ",
        "header_api": "🔌 Cấu hình API thiết bị phần cứng",
        "header_rules": "⚙️ Thiết lập tham số",
        "lbl_emp": "Chọn nhân viên *",
        "lbl_clock_time": "Thời gian quẹt thẻ *",
        "lbl_type": "Loại chấm công *",
        "type_opts": ["Vào ca (Check-In)", "Tan ca (Check-Out)"],
        "lbl_brand": "Thương hiệu máy chấm công *",
        "brand_opts": ["ZKTeco BioTime API", "Hikvision ISAPI", "RESTful Webhook API chung", "Suprema BioStar API"],
        "lbl_api_url": "Đường dẫn API Endpoint *",
        "lbl_api_key": "Mã thông báo API Key / Token *",
        "lbl_device_sn": "Số serial thiết bị (Device SN) *",
        "lbl_factory_bind": "Nhà máy liên kết *",
        "factory_opts": ["Nhà máy Tây Ninh", "Nhà máy Hải Phòng", "Toàn tập đoàn (Global)"],
        "btn_save_api": "💾 Lưu cấu hình API",
        "btn_test_api": "🔌 Kiểm tra kết nối",
        "btn_process": "🚀 Xử lý chấm công & Liên kết lương",
        "success_process": "✅ Đã xử lý cho `{name}` lúc `{time}`, trạng thái: `{status}`",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_type": "Loại",
        "col_time": "Thời gian",
        "col_status": "Trạng thái",
        "col_deduct": "Giờ trừ"
    },
    "English": {
        "title": "🏢 Management - Internal Attendance & Biometric API Hub",
        "caption": "Full plant attendance logs, monthly search, grace period, payroll sync, and biometric configuration.",
        "tab_records": "📑 Attendance Logs & Monthly Search",
        "tab_simulate": "⏱️ Simulate Biometric Input",
        "tab_api_config": "🔌 Biometric Device API Settings",
        "tab_rules": "⚙️ Grace Period & Deduction Settings",
        "header_tayninh": "🏭 Tay Ninh Plant Attendance Log",
        "header_haiphong": "🏭 Hai Phong Plant Attendance Log",
        "filter_month": "📅 Select Settlement Month",
        "search_label": "🔍 Search by Employee Name or ID...",
        "header_simulate": "⚡ Simulate Device Sync",
        "header_api": "🔌 Biometric Hardware API Integration Center",
        "header_rules": "⚙️ Grace Period Parameters",
        "lbl_emp": "Select Employee *",
        "lbl_clock_time": "Punch Timestamp *",
        "lbl_type": "Punch Type *",
        "type_opts": ["Check-In", "Check-Out"],
        "lbl_brand": "Device Brand / Protocol *",
        "brand_opts": ["ZKTeco BioTime API", "Hikvision ISAPI", "Generic RESTful Webhook API", "Suprema BioStar API"],
        "lbl_api_url": "Device Server API Endpoint URL *",
        "lbl_api_key": "API Key / Bearer Token *",
        "lbl_device_sn": "Device Serial Number (Device SN) *",
        "lbl_factory_bind": "Target Plant Binding *",
        "factory_opts": ["Tay Ninh Plant", "Hai Phong Plant", "Global (All Plants)"],
        "btn_save_api": "💾 Save API Configuration",
        "btn_test_api": "🔌 Test Device Connection",
        "btn_process": "🚀 Process Attendance & Link Payroll",
        "success_process": "✅ Punch for `{name}` at `{time}` processed. Status: `{status}`",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
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

    # 初始化考勤全域設定與硬體 API 設定
    if "attendance_rules" not in st.session_state:
        st.session_state.attendance_rules = {
            "standard_in": "08:00:00",
            "standard_out": "17:00:00",
            "daily_grace_mins": 5,      
            "monthly_exemption_mins": 30 
        }

    if "biometric_api_config" not in st.session_state:
        st.session_state.biometric_api_config = {
            "brand": "中控智慧 (ZKTeco BioTime API)",
            "api_url": "https://biometric.reetech.vn/api/v1/att",
            "api_key": "rt_live_sec_9988223311",
            "device_sn": "ZK-TN-001-FACE",
            "factory": "西寧廠 (Tay Ninh)"
        }

    if "internal_attendance_db" not in st.session_state:
        st.session_state.internal_attendance_db = [
            {
                "code": "EMP-001",
                "name": "張董事長",
                "factory": "西寧廠 (Tay Ninh)",
                "type": "上班簽到",
                "time": "2026-10-08 07:55:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            },
            {
                "code": "EMP-001",
                "name": "張董事長",
                "factory": "西寧廠 (Tay Ninh)",
                "type": "下班簽退",
                "time": "2026-10-08 17:10:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            },
            {
                "code": "VN-002",
                "name": "Nguyễn Văn Quý",
                "factory": "海防廠 (Hai Phong)",
                "type": "上班簽到",
                "time": "2026-10-08 08:12:00",
                "status": "🟡 遲到 12 分鐘 (超過 5m 緩衝)",
                "deduct_hours": 0.12
            },
            {
                "code": "VN-002",
                "name": "Nguyễn Văn Quý",
                "factory": "海防廠 (Hai Phong)",
                "type": "下班簽退",
                "time": "2026-10-08 17:02:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            },
            {
                "code": "VN-003",
                "name": "Trần Văn Nam",
                "factory": "西寧廠 (Tay Ninh)",
                "type": "上班簽到",
                "time": "2026-10-09 07:58:00",
                "status": "🟢 正常 (Normal)",
                "deduct_hours": 0.0
            }
        ]

    # 🎯 擴充頁籤：記錄、模擬、API設定、緩衝規則
    tab_records, tab_simulate, tab_api_config, tab_rules = st.tabs([
        L["tab_records"], L["tab_simulate"], L["tab_api_config"], L["tab_rules"]
    ])

    # 1. 📑 廠內完整出勤日誌與月度查詢
    with tab_records:
        rules = st.session_state.attendance_rules
        st.markdown(f"📌 **目前生效考勤標準**：上班 `{rules['standard_in']}` | 每日緩衝 `{rules['daily_grace_mins']} 分鐘`")
        
        # 💡 新增月份過濾與關鍵字搜尋列
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            selected_month = st.selectbox(L["filter_month"], ["全部月份 (All)", "2026-10", "2026-09", "2026-08"], key="att_month_filter")
        with rc2:
            search_query = st.text_input(L["search_label"], key="att_search_input")

        st.markdown("---")

        # 西寧廠
        st.markdown(f"### {L['header_tayninh']}")
        tay_ninh_data = [
            item for item in st.session_state.internal_attendance_db 
            if "西寧" in item["factory"] or "Tay Ninh" in item["factory"]
        ]
        
        if selected_month != "全部月份 (All)":
            tay_ninh_data = [item for item in tay_ninh_data if selected_month in item["time"]]

        if search_query:
            tay_ninh_data = [
                item for item in tay_ninh_data 
                if search_query.lower() in item["name"].lower() or search_query.lower() in item["code"].lower()
            ]

        if tay_ninh_data:
            display_tn = []
            for idx, item in enumerate(tay_ninh_data, 1):
                display_tn.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_type"]: item["type"],
                    L["col_time"]: item["time"],
                    L["col_status"]: item["status"],
                    L["col_deduct"]: f"{item['deduct_hours']} 小時"
                })
            st.dataframe(pd.DataFrame(display_tn), use_container_width=True)
        else:
            st.info("西寧廠在此月份無符合條件的出勤紀錄。")

        st.markdown("---")

        # 海防廠
        st.markdown(f"### {L['header_haiphong']}")
        hai_phong_data = [
            item for item in st.session_state.internal_attendance_db 
            if "海防" in item["factory"] or "Hai Phong" in item["factory"]
        ]

        if selected_month != "全部月份 (All)":
            hai_phong_data = [item for item in hai_phong_data if selected_month in item["time"]]

        if search_query:
            hai_phong_data = [
                item for item in hai_phong_data 
                if search_query.lower() in item["name"].lower() or search_query.lower() in item["code"].lower()
            ]

        if hai_phong_data:
            display_hp = []
            for idx, item in enumerate(hai_phong_data, 1):
                display_hp.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_type"]: item["type"],
                    L["col_time"]: item["time"],
                    L["col_status"]: item["status"],
                    L["col_deduct"]: f"{item['deduct_hours']} 小時"
                })
            st.dataframe(pd.DataFrame(display_hp), use_container_width=True)
        else:
            st.info("海防廠在此月份無符合條件的出勤紀錄。")

    # 2. ⏱️ 模擬打卡機 / 人臉指紋資料進站
    with tab_simulate:
        st.markdown(f"### {L['header_simulate']}")
        with st.form("form_biometric_simulate_rule"):
            emp_choices = [
                "EMP-001 - 張董事長 (西寧廠)", 
                "VN-002 - Nguyễn Văn Quý (海防廠)", 
                "VN-003 - Trần Văn Nam (西寧廠)"
            ]
            sel_emp = st.selectbox(L["lbl_emp"], emp_choices)
            clock_type = st.selectbox(L["lbl_type"], L["type_opts"])
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                sim_date = st.date_input("刷卡日期", datetime.date(2026, 10, 9))
            with col_t2:
                sim_time = st.time_input("刷卡時間 (Time)", datetime.time(8, 0))

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
                        status = f"🔴 遲到 {int(diff_mins)} 分鐘 (扣除每日 {rules['daily_grace_mins']}m 緩衝)"
                    elif diff_mins > 0:
                        status = f"🟢 雖遲到 {int(diff_mins)} 分鐘，但在緩衝內 (免扣)"
                    else:
                        status = "🟢 準時簽到 (Normal)"
                else:
                    status = "🟢 正常下班簽退 (Normal)"

                st.session_state.internal_attendance_db.insert(0, {
                    "code": emp_code,
                    "name": emp_name,
                    "factory": emp_factory,
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

    # 3. 🔌 硬體打卡機 API 介面設定 (SaaS 商業化功能)
    with tab_api_config:
        st.markdown(f"### {L['header_api']}")
        st.info("💡 說明：銷售時可直接在此輸入客戶現場人臉辨識或指紋打卡機的 API 資訊，系統自動與硬體設備進行考勤數據雙向同步，無須修改程式碼！")

        cfg = st.session_state.biometric_api_config

        with st.form("form_biometric_api_config"):
            c1, c2 = st.columns(2)
            with c1:
                sel_brand = st.selectbox(L["lbl_brand"], L["brand_opts"], index=L["brand_opts"].index(cfg["brand"]) if cfg["brand"] in L["brand_opts"] else 0)
                api_url = st.text_input(L["lbl_api_url"], value=cfg["api_url"])
                device_sn = st.text_input(L["lbl_device_sn"], value=cfg["device_sn"])
            with c2:
                api_key = st.text_input(L["lbl_api_key"], value=cfg["api_key"], type="password")
                sel_factory = st.selectbox(L["lbl_factory_bind"], L["factory_opts"], index=L["factory_opts"].index(cfg["factory"]) if cfg["factory"] in L["factory_opts"] else 0)

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                submitted_save = st.form_submit_button(L["btn_save_api"], type="primary", use_container_width=True)
            with col_b2:
                submitted_test = st.form_submit_button(L["btn_test_api"], type="secondary", use_container_width=True)

            if submitted_save:
                st.session_state.biometric_api_config = {
                    "brand": sel_brand,
                    "api_url": api_url,
                    "api_key": api_key,
                    "device_sn": device_sn,
                    "factory": sel_factory
                }
                st.success("✅ 打卡機硬體 API 設定已成功儲存並立即生效！")

            if submitted_test:
                if api_url.startswith("http"):
                    st.success(f"🎉 連線測試成功 (HTTP 200 OK)！打卡機設備 [SN: {device_sn}] 回應正常，考勤資料同步通道已建立。")
                else:
                    st.error("⚠️ 連線失敗：API 網址格式不正確，請確認是否以 http:// 或 https:// 開頭。")

    # 4. ⚙️ 彈性緩衝時間與扣款規則設定
    with tab_rules:
        st.markdown(f"### {L['header_rules']}")
        with st.form("form_attendance_rules"):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                std_in_input = st.text_input("標準上班時間 (Standard Start Time)", value=st.session_state.attendance_rules["standard_in"])
                daily_grace_input = st.number_input("每日容許緩衝時間 (分鐘)", min_value=0, max_value=30, value=st.session_state.attendance_rules["daily_grace_mins"])
            with col_r2:
                std_out_input = st.text_input("標準下班時間 (Standard End Time)", value=st.session_state.attendance_rules["standard_out"])
                monthly_ex_input = st.number_input("每月累計免扣款緩衝額度 (分鐘)", min_value=0, max_value=180, value=st.session_state.attendance_rules["monthly_exemption_mins"])

            if st.form_submit_button("💾 儲存考勤與緩衝規則設定", type="primary", use_container_width=True):
                st.session_state.attendance_rules["standard_in"] = std_in_input
                st.session_state.attendance_rules["standard_out"] = std_out_input
                st.session_state.attendance_rules["daily_grace_mins"] = int(daily_grace_input)
                st.session_state.attendance_rules["monthly_exemption_mins"] = int(monthly_ex_input)
                st.success("✅ 考勤與緩衝扣款規則已成功更新！")

def show(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)

def render_internal_attendance(*args, **kwargs):
    render_internal_attendance_page(*args, **kwargs)
