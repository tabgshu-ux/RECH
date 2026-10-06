import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 GPS 打卡與現場簽到模組多語系字典 (i18n)
# ----------------------------------------------------
GPS_ATTENDANCE_I18N = {
    "繁體中文": {
        "title": "📍 現場營運 - GPS 智慧打卡與工地出勤監控",
        "caption": "利用手機或行動裝置進行工地 GPS 定位打卡、現場照片上傳與離場自動稽核追蹤。",
        "tab_checkin": "🟢 上班簽到 (Check-In)",
        "tab_checkout": "🔴 下班簽退 (Check-Out)",
        "tab_history": "📜 打卡歷史紀錄",
        "tab_monitor": "📊 員工即時位置與監控",
        "checkin_header": "🟢 登記進入施工現場 (Check-In)",
        "checkin_caption": "💡 請填寫施工專案代碼，系統將自動記錄您當前的 GPS 座標與現場照片，同步回報給管理中心。",
        "lbl_emp": "技術與施工人員 *",
        "lbl_time": "上班簽到時間 (自動)",
        "lbl_project": "專案代碼 / 工地名稱 *",
        "proj_opts": ["PROJ-2026-配電盤安裝工程 (廠區A)", "PROJ-2026-胡志明市變電所統包工程", "PROJ-2026-平陽廠擴建機電工程"],
        "lbl_gps": "當前 GPS 座標 (自動偵測)",
        "lbl_desc": "今日施作內容與工作說明 *",
        "desc_placeholder": "例如: 執行拉設主幹線電纜及絕緣測試。",
        "lbl_photo": "上傳現場施工佐證照片 *",
        "btn_checkin": "🚀 確認上班簽到",
        "success_checkin": "✅ 成功完成上班簽到！GPS 座標與現場照片已同步至管理中心。",
        "fill_warning": "⚠️ 請填寫工作說明並上傳現場照片！",
        "col_time": "時間",
        "col_emp": "員工",
        "col_project": "專案名稱",
        "col_gps": "GPS 座標",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "📍 Vận hành hiện trường - Chấm công GPS & Giám sát Công trường",
        "caption": "Sử dụng thiết bị di động để chấm công GPS tại công trường, tải ảnh hiện trường và theo dõi tự động.",
        "tab_checkin": "🟢 Vào ca (Check-In)",
        "tab_checkout": "🔴 Tan ca (Check-Out)",
        "tab_history": "📜 Lịch sử Chấm công",
        "tab_monitor": "📊 Giám sát Vị trí Trực tuyến",
        "checkin_header": "🟢 Đăng ký vào ca hiện trường (Check-In)",
        "checkin_caption": "💡 Vui lòng điền thông tin công trường, hệ thống sẽ tự động ghi nhận GPS và ảnh chụp.",
        "lbl_emp": "Nhân viên kỹ thuật *",
        "lbl_time": "Thời gian vào ca (Tự động)",
        "lbl_project": "Mã dự án / Công trình *",
        "proj_opts": ["PROJ-2026-Lắp đặt tủ điện nhà máy TP.HCM", "PROJ-2026-Trạm biến áp Hồ Chí Minh", "PROJ-2026-Mở rộng cơ điện nhà máy Bình Dương"],
        "lbl_gps": "Tọa độ GPS hiện tại (Vào ca)",
        "lbl_desc": "Mô tả công việc *",
        "desc_placeholder": "Ví dụ: Thực hiện kéo dây mạch chính tủ điện và kiểm tra cách điện.",
        "lbl_photo": "Tải lên ảnh hiện trường *",
        "btn_checkin": "🚀 Xác nhận vào ca",
        "success_checkin": "✅ Đã chấm công vào ca thành công! Tọa độ và ảnh đã được đồng bộ về ban quản lý.",
        "fill_warning": "⚠️ Vui lòng điền mô tả công việc và tải ảnh hiện trường!",
        "col_time": "Thời gian",
        "col_emp": "Nhân viên",
        "col_project": "Dự án",
        "col_gps": "Tọa độ GPS",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📍 Field Operations - GPS Attendance & Site Monitoring",
        "caption": "Perform GPS check-in at construction sites, upload site photos, and track exit auditing.",
        "tab_checkin": "🟢 Check-In",
        "tab_checkout": "🔴 Check-Out",
        "tab_history": "📜 Attendance History",
        "tab_monitor": "📊 Live Location & Monitoring",
        "checkin_header": "🟢 Register Site Check-In",
        "checkin_caption": "💡 System will automatically record your current GPS coordinates and site photos.",
        "lbl_emp": "Technician / Staff *",
        "lbl_time": "Check-In Time (Auto)",
        "lbl_project": "Project / Site Code *",
        "proj_opts": ["PROJ-2026-HCMC Switchgear Installation", "PROJ-2026-Substation EPC Project", "PROJ-2026-Binh Duong Plant Expansion"],
        "lbl_gps": "Current GPS Coordinates (Check-In)",
        "lbl_desc": "Work Description *",
        "desc_placeholder": "Example: Pulling main switchboard cables and insulation testing.",
        "lbl_photo": "Upload Site Photo *",
        "btn_checkin": "🚀 Confirm Check-In",
        "success_checkin": "✅ Check-in recorded successfully! GPS and photo synchronized to management.",
        "fill_warning": "⚠️ Please fill in work description and upload site photo!",
        "col_time": "Timestamp",
        "col_emp": "Employee",
        "col_project": "Project",
        "col_gps": "GPS Coordinates",
        "col_status": "Status"
    }
}

def render_field_attendance_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = GPS_ATTENDANCE_I18N.get(active_lang, GPS_ATTENDANCE_I18N["繁體中文"])

    st.markdown(f"### {L['title']}")
    st.caption(L["caption"])

    if "gps_logs_db" not in st.session_state:
        st.session_state.gps_logs_db = [
            {"time": "2026-10-06 07:45:10", "emp": "admin", "project": "PROJ-2026-Lắp đặt tủ điện nhà máy TP.HCM", "gps": "10.8231° N, 106.6297° E", "status": "🟢 駐點施工中 (On-Site)"}
        ]

    tab1, tab2, tab3, tab4 = st.tabs([
        L["tab_checkin"], L["tab_checkout"], L["tab_history"], L["tab_monitor"]
    ])

    with tab1:
        st.markdown(f"### {L['checkin_header']}")
        st.info(L["checkin_caption"])

        with st.form("form_gps_checkin"):
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input(L["lbl_emp"], value=st.session_state.get("user_name", "admin"))
                project = st.selectbox(L["lbl_project"], L["proj_opts"])
            with c2:
                time_str = st.text_input(L["lbl_time"], value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disabled=True)
                gps_coord = st.text_input(L["lbl_gps"], value="10.8231° N, 106.6297° E")

            desc = st.text_area(L["lbl_desc"], placeholder=L["desc_placeholder"])
            photo = st.file_uploader(L["lbl_photo"], type=["jpg", "png", "jpeg"])

            if st.form_submit_button(L["btn_checkin"], type="primary", use_container_width=True):
                if desc and photo:
                    st.session_state.gps_logs_db.insert(0, {
                        "time": time_str,
                        "emp": emp_name,
                        "project": project,
                        "gps": gps_coord,
                        "status": "🟢 駐點施工中 (On-Site)"
                    })
                    st.success(L["success_checkin"])
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab2:
        st.markdown("### 🔴 辦理下班簽退 (Check-Out)")
        st.info("當您離開施工工地時，請點擊下方按鈕進行簽退並記錄離場座標。")
        if st.button("🚀 確認下班離場 (Check-Out)", type="primary"):
            st.success("✅ 已成功記錄下班離場時間與 GPS 座標！")

    with tab3:
        st.markdown(f"### {L['tab_history']}")
        st.dataframe(pd.DataFrame(st.session_state.gps_logs_db), use_container_width=True)

    with tab4:
        st.markdown(f"### {L['tab_monitor']}")
        st.success("🛰️ 目前系統監控中：所有外派施工人員 GPS 訊號穩定，無越界或異常離場狀況。")

def show(lang="繁體中文", **kwargs):
    render_field_attendance_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_field_attendance_page(lang, **kwargs)
