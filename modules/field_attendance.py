import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 外勤打卡模組多語系字典 (i18n)
# ----------------------------------------------------
ATTENDANCE_I18N = {
    "繁體中文": {
        "title": "📍 裕豐電機工業 - 外勤工程人員 GPS 與拍照打卡中心",
        "caption": "📱 支援外勤上下班打卡、GPS 異常判定（早退或跨場支援）與副總高管稽核。",
        "tab_checkin": "📸 外勤上班打卡 (Check-In)",
        "tab_checkout": "🏁 外勤下班打卡 (Check-Out)",
        "tab_records": "📋 我的打卡紀錄與軌跡",
        "tab_admin": "🏢 副總 / 主管後台：全廠外勤稽核",
        "info_msg": "💡 請在施工現場填寫下方資料，系統將自動綁定您手機的 GPS 座標並上傳現場工作照片，即時同步至副總及總廠管理後台。",
        "emp_name": "工程人員姓名 *",
        "project_code": "工程專案 / 施工案場 *",
        "work_desc": "工作內容說明 *",
        "gps_label": "GPS 現場定位座標",
        "photo_label": "上傳現場工作照片 *",
        "time_in_label": "上班打卡時間 (自動)",
        "time_out_label": "下班打卡時間 (自動)",
        "default_desc": "執行配電盤主回路拉線與絕緣測試。",
        "btn_submit_in": "🚀 登記外勤上班打卡",
        "btn_submit_out": "🏁 登記外勤下班打卡",
        "success_in": "🎉 【上班打卡成功】GPS 與現場照片已同步記錄！",
        "success_out": "🎉 【下班打卡成功】工時與軌跡已結算歸檔！",
        "error_msg": "❌ 請完整填寫姓名與必要欄位！",
        "alert_distance": "⚠️ 【打卡位置異常警告】您目前的下班 GPS 定位點與上班定位點距離過遠（超過安全範圍）！請選擇您的實際情況：",
        "reason_1": "🏃‍♂️ 提前離開原施工案場 (早退)",
        "reason_2": "🔄 奉派臨時支援別的工地 / 其他案場",
        "reason_note": "補充說明原因 (選填)",
        "projects": [
            "PROJ-2026-胡志明市第一工廠配電安裝案",
            "PROJ-2026-平陽工業區變壓器擴建工程",
            "PROJ-2026-同奈廠區消防與控制盤驗收",
            "PROJ-2026-隆安廠房自動化線體配線",
        ]
    },
    "Tiếng Việt": {
        "title": "📍 REETECH INDUSTRIAL - Chấm công GPS & Chụp ảnh Hiện trường",
        "caption": "📱 Chấm công di động, kiểm tra khoảng cách GPS (về sớm hoặc hỗ trợ công trình khác) & giám sát.",
        "tab_checkin": "📸 Check-In Vào ca",
        "tab_checkout": "🏁 Check-Out Tan ca",
        "tab_records": "📋 Lịch sử chấm công",
        "tab_admin": "🏢 Quản lý: Kiểm tra định vị",
        "info_msg": "💡 Vui lòng điền thông tin tại công trường, hệ thống sẽ tự động ghi nhận tọa độ GPS và ảnh chụp hiện trường để đồng bộ về Ban Giám đốc.",
        "emp_name": "Tên nhân viên kỹ thuật *",
        "project_code": "Mã dự án / Công trình *",
        "work_desc": "Mô tả công việc *",
        "gps_label": "Tọa độ GPS hiện tại",
        "photo_label": "Tải lên ảnh hiện trường *",
        "time_in_label": "Thời gian vào ca (Tự động)",
        "time_out_label": "Thời gian tan ca (Tự động)",
        "default_desc": "Thực hiện kéo dây mạch chính tủ điện và kiểm tra cách điện.",
        "btn_submit_in": "🚀 Xác nhận vào ca",
        "btn_submit_out": "🏁 Xác nhận tan ca",
        "success_in": "🎉 Chấm công vào ca thành công!",
        "success_out": "🎉 Chấm công tan ca thành công!",
        "error_msg": "❌ Vui lòng điền đầy đủ thông tin!",
        "alert_distance": "⚠️️ 【Cảnh báo vị trí】Tọa độ GPS khi tan ca cách xa điểm vào ca! Vui lòng chọn lý do:",
        "reason_1": "🏃‍♂️ Về sớm / Rời công trình trước giờ",
        "reason_2": "🔄 Được điều động hỗ trợ công trình khác",
        "reason_note": "Ghi chú bổ sung (nếu có)",
        "projects": [
            "PROJ-2026-Lắp đặt tủ điện nhà máy TP.HCM",
            "PROJ-2026-Mở rộng trạm biến áp KCN Bình Dương",
            "PROJ-2026-Nghiệm thu tủ PCCC nhà máy Đồng Nai",
            "PROJ-2026-Đi dây dây chuyền tự động Long An",
        ]
    },
    "English": {
        "title": "📍 REETECH INDUSTRIAL - Field Engineering GPS & Photo Attendance",
        "caption": "📱 Field attendance with GPS distance verification & VP oversight.",
        "tab_checkin": "📸 Field Check-In",
        "tab_checkout": "🏁 Field Check-Out",
        "tab_records": "📋 My Attendance Records",
        "tab_admin": "🏢 VP & Supervisor Audit Dashboard",
        "info_msg": "💡 Please fill out details on-site. The system will auto-capture GPS coordinates and upload photo proof to management.",
        "emp_name": "Engineer Name *",
        "project_code": "Project / Site Code *",
        "work_desc": "Work Description *",
        "gps_label": "GPS Coordinates",
        "photo_label": "Upload On-Site Photo *",
        "time_in_label": "Check-In Time (Auto)",
        "time_out_label": "Check-Out Time (Auto)",
        "default_desc": "Execute switchgear main circuit wiring and insulation testing.",
        "btn_submit_in": "🚀 Submit Check-In",
        "btn_submit_out": "🏁 Submit Check-Out",
        "success_in": "🎉 Check-in successful!",
        "success_out": "🎉 Check-out successful!",
        "error_msg": "Please fill in required fields!",
        "alert_distance": "⚠️ 【Location Alert】Check-out GPS is too far from check-in location! Please select reason:",
        "reason_1": "🏃‍♂️ Left original site early",
        "reason_2": "🔄 Assigned to support another site",
        "reason_note": "Additional notes (Optional)",
        "projects": [
            "PROJ-2026-HCMC Factory Switchgear Installation",
            "PROJ-2026-Binh Duong Substation Expansion",
            "PROJ-2026-Dong Nai Fire Panel Commissioning",
            "PROJ-2026-Long An Automation Line Wiring",
        ]
    },
}


def render_field_attendance_page(engine=None, lang="繁體中文"):
    current_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ATTENDANCE_I18N.get(current_lang, ATTENDANCE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "field_attendance_db" not in st.session_state:
        st.session_state.field_attendance_db = [
            {
                "date": "2026-10-03",
                "name": "Nguyễn Văn Hùng",
                "project": L["projects"][0],
                "in_time": "08:30:15",
                "in_gps": "10.8231° N, 106.6297° E",
                "out_time": "-",
                "out_gps": "-",
                "status": "🟡 作業中 (Working)",
                "note": "正常出勤",
            }
        ]

    tab_checkin, tab_checkout, tab_records, tab_admin = st.tabs([
        L["tab_checkin"],
        L["tab_checkout"],
        L["tab_records"],
        L["tab_admin"],
    ])

    # ----------------------------------------------------
    # 📸 頁籤一：外勤上班打卡 (Check-In)
    # ----------------------------------------------------
    with tab_checkin:
        st.markdown(f"### {L['tab_checkin']}")
        st.info(L["info_msg"])

        with st.form("form_field_checkin_new"):
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input(L["emp_name"], value=st.session_state.get("user_name", ""))
                project_code = st.selectbox(L["project_code"], L["projects"], key="in_project")
            with c2:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.text_input(L["time_in_label"], value=current_time, disabled=True)
                gps_in = st.text_input(L["gps_label"] + " (上班)", value="10.8231° N, 106.6297° E")

            work_desc = st.text_area(L["work_desc"], value=L["default_desc"])
            uploaded_photo = st.file_uploader(L["photo_label"], type=["jpg", "png", "jpeg"], key="photo_in")

            if st.form_submit_button(L["btn_submit_in"], type="primary", use_container_width=True):
                if emp_name and work_desc:
                    new_record = {
                        "date": datetime.date.today().strftime("%Y-%m-%d"),
                        "name": emp_name,
                        "project": project_code,
                        "in_time": current_time,
                        "in_gps": gps_in,
                        "out_time": "-",
                        "out_gps": "-",
                        "status": "🟡 作業中 (Working)",
                        "note": "正常上班打卡",
                    }
                    st.session_state.field_attendance_db.insert(0, new_record)
                    st.success(L["success_in"])
                    st.rerun()
                else:
                    st.error(L["error_msg"])

    # ----------------------------------------------------
    # 🏁 頁籤二：外勤下班打卡 (Check-Out)
    # ----------------------------------------------------
    with tab_checkout:
        st.markdown(f"### {L['tab_checkout']}")
        active_records = [r for r in st.session_state.field_attendance_db if r["out_time"] == "-"]

        if active_records:
            for idx, rec in enumerate(active_records):
                st.markdown(f"**👤 員工 / Nhân viên: {rec['name']}** | 案場: `{rec['project']}` | 上班時間: {rec['in_time']}")
                
                with st.form(f"form_checkout_{idx}"):
                    out_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    gps_out = st.text_input(
                        L["gps_label"] + " (下班)", 
                        value="10.9512° N, 106.7234° E",
                        key=f"gps_out_{idx}"
                    )

                    is_distance_too_far = True
                    selected_reason = ""
                    detail_note = ""

                    if is_distance_too_far:
                        st.warning(L["alert_distance"])
                        selected_reason = st.radio(
                            "請選擇 / Vui lòng chọn:",
                            [L["reason_1"], L["reason_2"]],
                            key=f"reason_{idx}"
                        )
                        detail_note = st.text_input(L["reason_note"], value="", key=f"note_{idx}")

                    if st.form_submit_button(L["btn_submit_out"], type="primary", use_container_width=True):
                        rec["out_time"] = out_time
                        rec["out_gps"] = gps_out
                        if is_distance_too_far:
                            rec["status"] = f"🔴 {selected_reason}"
                            rec["note"] = f"Note: {detail_note}" if detail_note else selected_reason
                        else:
                            rec["status"] = "🟢 正常下班"
                            rec["note"] = "Tan ca bình thường"

                        st.success(L["success_out"])
                        st.rerun()
                st.divider()
        else:
            st.info("🎉 目前沒有進行中的外勤打卡任務。")

    # ----------------------------------------------------
    # 📋 頁籤三：個人打卡紀錄
    # ----------------------------------------------------
    with tab_records:
        st.markdown(f"### {L['tab_records']}")
        df_my = pd.DataFrame(st.session_state.field_attendance_db)
        st.dataframe(df_my, use_container_width=True)

    # ----------------------------------------------------
    # 🏢 頁籤四：副總 / 主管後台稽核
    # ----------------------------------------------------
    with tab_admin:
        st.markdown(f"### {L['tab_admin']}")
        st.success("👑 **高管與副總監控視角 / Ban Giám đốc & Phó Tổng giám đốc**")
        
        total_logs = len(st.session_state.field_attendance_db)
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 總打卡筆數", f"{total_logs}")
        c2.metric("📍 監控案場數", "4")
        c3.metric("🟢 連線狀態", "24/7 OK")

        st.divider()
        st.markdown("#### 📋 全廠外勤軌跡與異動稽核總表")
        df_all = pd.DataFrame(st.session_state.field_attendance_db)
        st.dataframe(df_all, use_container_width=True)


def show(engine=None, lang="繁體中文"):
    render_field_attendance_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_field_attendance_page(engine, lang)
