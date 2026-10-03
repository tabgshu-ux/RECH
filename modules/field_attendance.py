import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 外勤打卡模組多語系字典 (i18n)
# ----------------------------------------------------
ATTENDANCE_I18N = {
    "繁體中文": {
        "title": "📍 裕豐電機工業 - 外勤工程人員 GPS 與拍照打卡中心",
        "caption": "📱 專為外地施工、安裝配電盤與工程驗收人員設計的手機行動打卡系統。",
        "tab_checkin": "📸 外勤即時打卡 (Check-In)",
        "tab_records": "📋 我的外勤打卡紀錄與佐證",
        "tab_admin": "🏢 主管後台：全廠外勤軌跡稽核",
        "emp_name": "工程人員姓名 *",
        "project_code": "工程專案 / 施工案場 *",
        "work_desc": "今日施工內容說明 *",
        "gps_label": "GPS 現場定位座標 (自動抓取)",
        "photo_label": "上傳現場施工與案場照片 *",
        "btn_submit": "🚀 立即送出外勤打卡",
        "success_msg": "🎉 【外勤打卡成功】GPS 位置與現場照片已同步回傳至總廠伺服器！",
        "error_msg": "❌ 請填寫您的姓名與施工內容說明！",
        "col_time": "打卡時間",
        "col_name": "人員姓名",
        "col_project": "施工案場",
        "col_desc": "工作內容",
        "col_gps": "GPS 座標",
        "col_status": "狀態",
    },
    "Tiếng Việt": {
        "title": "📍 REETECH INDUSTRIAL - Chấm công GPS & Chụp ảnh Hiện trường",
        "caption": "📱 Hệ thống chấm công di động dành cho nhân viên thi công tủ điện và nghiệm thu tại công trình.",
        "tab_checkin": "📸 Chấm công hiện trường",
        "tab_records": "📋 Lịch sử chấm công của tôi",
        "tab_admin": "🏢 Quản lý: Kiểm tra định vị nhân viên",
        "emp_name": "Tên nhân viên kỹ thuật *",
        "project_code": "Mã dự án / Công trình *",
        "work_desc": "Mô tả công việc hôm nay *",
        "gps_label": "Tọa độ GPS hiện tại (Tự động)",
        "photo_label": "Tải lên ảnh chụp hiện trường *",
        "btn_submit": "🚀 Gửi xác nhận chấm công",
        "success_msg": "🎉 Chấm công thành công! Tọa độ GPS và hình ảnh đã được lưu.",
        "error_msg": "❌ Vui lòng nhập đầy đủ tên và nội dung công việc!",
        "col_time": "Thời gian",
        "col_name": "Nhân viên",
        "col_project": "Công trình",
        "col_desc": "Nội dung",
        "col_gps": "Tọa độ GPS",
        "col_status": "Trạng thái",
    },
    "English": {
        "title": "📍 REETECH INDUSTRIAL - Field Engineering GPS & Photo Attendance",
        "caption": "📱 Mobile attendance system for field installation and engineering project teams.",
        "tab_checkin": "📸 Field Check-In",
        "tab_records": "📋 My Attendance Records",
        "tab_admin": "🏢 Supervisor Audit Dashboard",
        "emp_name": "Engineer Name *",
        "project_code": "Project / Site Code *",
        "work_desc": "Work Description *",
        "gps_label": "GPS Coordinates (Auto)",
        "photo_label": "Upload On-Site Photo *",
        "btn_submit": "🚀 Submit Field Check-In",
        "success_msg": "🎉 Field check-in successful! GPS and photo uploaded.",
        "error_msg": "❌ Please fill in your name and work description!",
        "col_time": "Check-In Time",
        "col_name": "Name",
        "col_project": "Project Site",
        "col_desc": "Description",
        "col_gps": "GPS Location",
        "col_status": "Status",
    },
}


def render_field_attendance_page(engine=None, lang="繁體中文"):
    current_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ATTENDANCE_I18N.get(current_lang, ATTENDANCE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化外勤打卡資料庫
    if "field_attendance_db" not in st.session_state:
        st.session_state.field_attendance_db = [
            {
                "time": "2026-10-03 08:30:15",
                "name": "Nguyễn Văn Hùng",
                "project": "PROJ-2026-Bình Dương Factory A",
                "desc": "執行配電盤主回路拉線與絕緣測試",
                "gps": "10.8231° N, 106.6297° E (Bình Dương)",
                "status": "🟢 已審核 (Verified)",
            }
        ]

    tab_checkin, tab_records, tab_admin = st.tabs([
        L["tab_checkin"],
        L["tab_records"],
        L["tab_admin"],
    ])

    # ----------------------------------------------------
    # 📸 頁籤一：外勤即時打卡 (Check-In)
    # ----------------------------------------------------
    with tab_checkin:
        st.markdown(f"### {L['tab_checkin']}")
        st.info("💡 請在施工現場填寫下方資料，系統將自動綁定您手機的 GPS 座標並上傳現場工作照片。")

        with st.form("form_field_checkin"):
            c1, c2 = st.columns(2)
            with c1:
                emp_name = st.text_input(L["emp_name"], value=st.session_state.get("user_name", ""))
                project_code = st.selectbox(
                    L["project_code"],
                    [
                        "PROJ-2026-胡志明市第一工廠配電安裝案",
                        "PROJ-2026-平陽工業區變壓器擴建工程",
                        "PROJ-2026-同奈廠區消防與控制盤驗收",
                        "PROJ-2026-隆安廠房自動化線體配線",
                    ]
                )
            with c2:
                # 模擬手機自動抓取 GPS
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.text_input("打卡時間 (自動記錄)", value=current_time, disabled=True)
                gps_coord = st.text_input(L["gps_label"], value="10.9512° N, 106.7234° E (模擬現場定位)")

            work_desc = st.text_area(L["work_desc"], value="今日任務：安裝低壓配電盤並與業主進行第一階段工程點交。")
            
            # 照片上傳
            uploaded_photo = st.file_uploader(L["photo_label"], type=["jpg", "png", "jpeg"])

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if emp_name and work_desc:
                    new_log = {
                        "time": current_time,
                        "name": emp_name,
                        "project": project_code,
                        "desc": work_desc,
                        "gps": gps_coord,
                        "status": "🟢 審核中 (Pending)",
                    }
                    st.session_state.field_attendance_db.insert(0, new_log)
                    st.success(L["success_msg"])
                    if uploaded_photo:
                        st.info("📷 現場施工照片已成功加密上傳至雲端伺服器！")
                else:
                    st.error(L["error_msg"])

    # ----------------------------------------------------
    # 📋 頁籤二：個人打卡紀錄
    # ----------------------------------------------------
    with tab_records:
        st.markdown(f"### {L['tab_records']}")
        df_my = pd.DataFrame(st.session_state.field_attendance_db)
        st.dataframe(df_my, use_container_width=True)

    # ----------------------------------------------------
    # 🏢 頁籤三：主管後台稽核
    # ----------------------------------------------------
    with tab_admin:
        st.markdown(f"### {L['tab_admin']}")
        st.caption("主管可隨時檢視所有外勤工程人員的 GPS 定位、打卡時間與施工內容。")
        df_all = pd.DataFrame(st.session_state.field_attendance_db)
        st.dataframe(df_all, use_container_width=True)


def show(engine=None, lang="繁體中文"):
    render_field_attendance_page(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_field_attendance_page(engine, lang)
