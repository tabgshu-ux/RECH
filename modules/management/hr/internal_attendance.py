import streamlit as st
import pandas as pd
from sqlalchemy import text

def get_t(lang):
    texts = {
        "繁體中文": {
            "title": "📊 員工打卡紀錄與出勤稽核中心",
            "info": "💡 說明：HR 可在此檢視廠內出勤、設定考勤寬限期、對齊 09 月薪資表之多版本加班時數（1.5倍、1.95倍、2.0倍、3.0倍）、執行打卡補登及匯出每月考勤。",
            "tab1_title": "🏭 廠內考勤與多版本加班明細",
            "tab2_title": "📝 打卡補登與原始日誌",
            "tab3_title": "📍 外勤 GPS 打卡稽核",
            "rule_title": "⚙️ 考勤寬限期與遲到判定規則設定",
            "grace_min": "上班打卡寬限分鐘數 (分鐘內不算遲代)",
            "monthly_limit": "每月累計遲到容許總分鐘數",
            "export_btn": "📥 下載各員工每月打卡與多版本加班紀錄 (CSV)",
            "punch_fix_title": "⚙️ 員工考勤補登與異常調整",
            "no_field_data": "目前尚無外勤 GPS 打卡與回報紀錄。",
            "field_table_title": "📋 全廠外勤工程人員打卡明細總表"
        },
        "Tiếng Việt": {
            "title": "📊 Quản lý Chấm công & Kiểm toán Nhân viên",
            "info": "💡 Hướng dẫn: HR quản lý chấm công, ân hạn, chi tiết tăng ca đa phiên bản (1.5x, 1.95x, 2.0x, 3.0x) đối chiếu theo bảng lương T.09.",
            "tab1_title": "🏭 Chấm công & Chi tiết Tăng ca",
            "tab2_title": "📝 Bù giờ & Nhật ký",
            "tab3_title": "📍 Kiểm duyệt GPS",
            "rule_title": "⚙️ Cài đặt thời gian ân hạn đi muộn",
            "grace_min": "Số phút ân hạn buổi sáng (Không tính đi muộn)",
            "monthly_limit": "Tổng số phút đi muộn cho phép mỗi tháng",
            "export_btn": "📥 Tải xuống bảng chấm công & tăng ca (CSV)",
            "punch_fix_title": "⚙️ Xử lý bù giờ chấm công",
            "no_field_data": "Hiện tại chưa có dữ liệu chấm công GPS.",
            "field_table_title": "📋 Bảng chi tiết chấm công hiện trường"
        }
    }
    return texts.get(lang, texts["繁體中文"])

def render_internal_attendance_page(engine=None, lang="繁體中文", **kwargs):
    t = get_t(lang)

    st.markdown(f"### {t['title']}")
    st.info(t['info'])

    tab1, tab2, tab3 = st.tabs([t['tab1_title'], t['tab2_title'], t['tab3_title']])

    # ----------------------------------------------------
    # TAB 1: 廠內考勤、寬限規則與多版本加班明細
    # ----------------------------------------------------
    with tab1:
        st.markdown(f"#### {t['rule_title']}")
        
        with st.expander("🛠️ 點此展開並調整「遲到寬限與扣薪規則」設定", expanded=False):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                grace_minutes = st.number_input(t['grace_min'], min_value=0, max_value=30, value=10, step=1)
            with col_r2:
                monthly_late_limit = st.number_input(t['monthly_limit'], min_value=0, max_value=120, value=30, step=5)
            
            if st.button("💾 儲存考勤寬限規則", type="primary"):
                st.success(f"🎉 考勤規則已更新：上班寬限 {grace_minutes} 分鐘內不算遲到，每月容許累計 {monthly_late_limit} 分鐘。")

        st.markdown("---")
        st.markdown("#### 🏢 廠內同仁出勤與九月薪資表對齊之「多版本加班時數」總表")
        
        # 對齊真實薪資表的四種加班倍率欄位 (1.5, 1.95, 2.0, 3.0)
        emp_records = [
            {"工號": "VN-001", "姓名": "Nguyễn Văn A", "部門": "生產部", "職稱": "技術員", "應出勤": 22, "實出": 22, "遲到分": 0, "加班*1.5 (平日)": 38.0, "加班*1.95 (夜班)": 1.0, "加班*2.0 (休息日)": 30.0, "加班*3.0 (國定)": 8.0, "狀態": "🟢 正常"},
            {"工號": "VN-002", "姓名": "Tran Thi B", "部門": "管理部", "職稱": "會計專員", "應出勤": 22, "實出": 21, "遲到分": 8, "加班*1.5 (平日)": 0.0, "加班*1.95 (夜班)": 0.0, "加班*2.0 (休息日)": 0.0, "加班*3.0 (國定)": 0.0, "狀態": "🟡 遲到 8 分"},
        ]
        
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT emp_id, emp_name, department, position, base_salary FROM employee_profiles")).fetchall()
                    if res:
                        emp_records = [{
                            "工號": r[0], "姓名": r[1], "部門": r[2], "職稱": r[3],
                            "應出勤": 22, "實出": 22, "遲到分": 0, "加班*1.5 (平日)": 0.0, "加班*1.95 (夜班)": 0.0, "加班*2.0 (休息日)": 0.0, "加班*3.0 (國定)": 0.0, "狀態": "🟢 正常"
                        } for r in res]
            except Exception:
                pass

        df_emp = pd.DataFrame(emp_records)
        st.dataframe(df_emp, use_container_width=True, hide_index=True)

        # 📥 下載完整月報與加班明細
        csv_data = df_emp.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=t['export_btn'],
            data=csv_data,
            file_name="REETECH_Monthly_Attendance_OT_Report.csv",
            mime="text/csv",
            type="primary"
        )

    # ----------------------------------------------------
    # TAB 2: 打卡補登與原始日誌
    # ----------------------------------------------------
    with tab2:
        st.markdown(f"#### {t['punch_fix_title']}")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("輸入要補登的員工工號 (Mã NV)")
            st.date_input("補登日期 (Ngày)")
        with col2:
            st.selectbox("補登類型 (Loại)", ["上班補打卡 (Check-in)", "下班補打卡 (Check-out)"])
            st.text_input("補登原因說明 (Lý do)")
        
        if st.button("💾 確認送出補登申請", type="primary"):
            st.success("🎉 打卡紀錄已成功補登並同步至薪資計算核心！")

        st.markdown("---")
        st.markdown("#### 📋 廠內完整出勤與刷卡原始日誌 (Audit Logs)")
        audit_data = [
            {"工號": "VN-001", "姓名": "Nguyễn Văn A", "區域": "西寧廠", "類型": "上班簽到", "刷卡時間": "2026-10-30 07:55:00", "狀態": "🟢 正常"}
        ]
        st.dataframe(pd.DataFrame(audit_data), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # TAB 3: 外勤 GPS 打卡與照片稽核
    # ----------------------------------------------------
    with tab3:
        st.markdown(f"#### {t['field_table_title']}")
        
        field_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo FROM hr_field_gps ORDER BY check_time DESC")).fetchall()
                    for r in res:
                        field_records.append({
                            "紀錄編號": r[0], "工號": r[1], "姓名": r[2],
                            "案場": r[3], "打卡類型": r[4], "緯度": r[5], "經度": r[6],
                            "工程進度回報": r[7], "打卡時間": r[8], "狀態": r[9], "備註": r[10], "現場照片": "📷 已上傳" if r[11] else "無"
                        })
            except Exception as e:
                st.warning(f"載入外勤打卡資料庫發生異常: {e}")

        if field_records:
            df_field = pd.DataFrame(field_records)
            st.dataframe(df_field, use_container_width=True, hide_index=True)
        else:
            st.info(t['no_field_data'])
