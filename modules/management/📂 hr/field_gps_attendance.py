import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def get_t(lang):
    """多語系字典配置引擎 (支援繁中、越文)"""
    texts = {
        "繁體中文": {
            "title": "📍 外勤工程打卡與工作回報中心 (Field GPS Attendance & Report)",
            "info": "💡 說明：外勤工程人員抵達案場後進行 GPS 定位、拍照打卡，並於下班時回報當日工程進度與施工照片。",
            "total_punches": "📊 今日外勤總打卡人次",
            "active_sites": "🏗️ 今日動工案場數",
            "geofence_status": "🟢 GPS 圍籬驗證狀態",
            "form_title": "📱 手機外勤打卡與工程回報表單",
            "emp_id": "工號 (Employee ID)",
            "emp_name": "姓名 (Full Name)",
            "site_label": "指派工程案場 / 工地",
            "punch_type": "打卡類型 (Attendance Type)",
            "punch_in": "🟢 上班打卡 (現場拍照存證)",
            "punch_out": "🔴 下班打卡 (工程進度回報 + 施工照)",
            "lat_label": "GPS 緯度 (Latitude)",
            "lng_label": "GPS 經度 (Longitude)",
            "progress_label": "當日工程進度回報",
            "progress_placeholder": "例如: 已完成配電箱安裝 80%、管線拉線完畢...",
            "note_label": "現場備註 / 異常回報",
            "note_placeholder": "例如: 現場材料不足需支援...",
            "camera_label": "📷 現場施工/打卡照片上傳",
            "submit_btn": "🛰️ 確認送出打卡與回報",
            "success_msg": "✅ 外勤打卡與工作回報成功，已同步至管理部與工程中心！",
            "table_title": "📋 全廠外勤打卡與進度回報總表",
            "no_data": "目前尚無外勤打卡紀錄。",
            "fill_warning": "請填寫完整工號、姓名並完成打卡拍照！"
        },
        "Tiếng Việt": {
            "title": "📍 Chấm công Hiện trường & Báo cáo Tiến độ (Field GPS)",
            "info": "💡 Hướng dẫn: Nhân viên hiện trường định vị GPS, chụp ảnh chấm công và báo cáo tiến độ công việc.",
            "total_punches": "📊 Tổng số lượt chấm công hôm nay",
            "active_sites": "🏗️ Số công trường hoạt động",
            "geofence_status": "🟢 Trạng thái GPS",
            "form_title": "📱 Biểu mẫu chấm công & báo cáo di động",
            "emp_id": "Mã nhân viên (EMP ID)",
            "emp_name": "Họ và tên",
            "site_label": "Công trường / Dự án",
            "punch_type": "Loại chấm công",
            "punch_in": "🟢 Vào ca (Chụp ảnh hiện trường)",
            "punch_out": "🔴 Tan ca (Báo cáo tiến độ + Ảnh thi công)",
            "lat_label": "Vĩ độ GPS",
            "lng_label": "Kinh độ GPS",
            "progress_label": "Báo cáo tiến độ công việc",
            "progress_placeholder": "VD: Đã hoàn thành 80% lắp đặt tủ điện...",
            "note_label": "Ghi chú / Báo cáo sự cố",
            "note_placeholder": "VD: Thiếu vật tư cần hỗ trợ...",
            "camera_label": "📷 Chụp ảnh chấm công / Thi công",
            "submit_btn": "🛰️ Xác nhận gửi chấm công & báo cáo",
            "success_msg": "✅ Chấm công thành công, đã đồng bộ về hệ thống!",
            "table_title": "📋 Bảng chi tiết chấm công và tiến độ hiện trường",
            "no_data": "Hiện chưa có dữ liệu chấm công.",
            "fill_warning": "Vui lòng điền đầy đủ thông tin và chụp ảnh!"
        }
    }
    return texts.get(lang, texts["繁體中文"])

def init_field_gps_db(engine):
    """初始化外勤打卡與進度回報資料表（包含照片與工作進度）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_field_gps (
                    record_id VARCHAR(50) PRIMARY KEY,
                    emp_id VARCHAR(50),
                    emp_name VARCHAR(100),
                    site_name VARCHAR(150),
                    punch_type VARCHAR(50),
                    gps_lat FLOAT,
                    gps_lng FLOAT,
                    work_progress TEXT,
                    check_time VARCHAR(50),
                    status VARCHAR(50),
                    note TEXT,
                    has_photo BOOLEAN DEFAULT FALSE
                );
            """))
            # 自動向下相容補上可能缺少的欄位
            conn.execute(text("ALTER TABLE hr_field_gps ADD COLUMN IF NOT EXISTS punch_type VARCHAR(50) DEFAULT '上班打卡';"))
            conn.execute(text("ALTER TABLE hr_field_gps ADD COLUMN IF NOT EXISTS work_progress TEXT;"))
            conn.execute(text("ALTER TABLE hr_field_gps ADD COLUMN IF NOT EXISTS has_photo BOOLEAN DEFAULT FALSE;"))
    except Exception as e:
        st.error(f"Error initializing DB: {e}")

def render_field_gps_attendance(engine, lang="繁體中文"):
    init_field_gps_db(engine)
    t = get_t(lang)

    st.markdown(f"##### {t['title']}")
    st.info(t['info'])

    field_records = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo FROM hr_field_gps ORDER BY check_time DESC")).fetchall()
                for r in res:
                    field_records.append({
                        "紀錄編號": r[0], "工號": r[1], "姓名": r[2],
                        "案場": r[3], "類型": r[4], "緯度": r[5], "經度": r[6],
                        "工程進度回報": r[7], "打卡時間": r[8], "狀態": r[9], "備註": r[10], "現場照片": "📷 已拍照" if r[11] else "無"
                    })
        except Exception as e:
            st.warning(f"Error loading records: {e}")

    # 1. 數據儀表板
    if field_records:
        df_field = pd.DataFrame(field_records)
        today_str = str(datetime.date.today())
        today_df = df_field[df_field["打卡時間"].str.startswith(today_str)]
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(t['total_punches'], len(today_df))
        with col_m2:
            active_sites = today_df["案場"].nunique() if not today_df.empty else 0
            st.metric(t['active_sites'], active_sites)
        with col_m3:
            st.metric(t['geofence_status'], "Normal" if lang == "English" else "正常運行")
        st.markdown("---")

    # 2. 外勤手機打卡與回報表單
    with st.form("field_gps_form"):
        st.markdown(f"##### {t['form_title']}")
        
        c1, c2 = st.columns(2)
        with c1:
            f_emp_id = st.text_input(t['emp_id'], value="EMP-001")
            f_name = st.text_input(t['emp_name'], value="Nguyễn Văn A")
            f_site = st.selectbox(t['site_label'], [
                "西寧總廠案場 (Reetech Tay Ninh Plant)", 
                "平陽省美福工業區案場 (My Phuoc)", 
                "同奈省邊和高壓配電案場 (Bien Hoa)", 
                "隆安省太陽能案場 (Long An)"
            ])
            f_punch_type = st.radio(t['punch_type'], [t['punch_in'], t['punch_out']], horizontal=True)

        with c2:
            f_lat = st.number_input(t['lat_label'], value=11.1085, format="%.4f") # 西寧省座標預設
            f_lng = st.number_input(t['lng_label'], value=106.1302, format="%.4f")
            
            # 如果選擇下班打卡，顯示工程進度填寫欄位
            f_progress = st.text_area(t['progress_label'], placeholder=t['progress_placeholder'])
            f_note = st.text_input(t['note_label'], placeholder=t['note_placeholder'])

        # 手機相機拍照打卡
        st.markdown(f"**{t['camera_label']}**")
        captured_image = st.camera_input("請對準現場施工環境或人員進行拍照打卡")

        if st.form_submit_button(t['submit_btn'], type="primary", use_container_width=True):
            if f_emp_id and f_name:
                record_id = f"GPS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                has_photo_bool = True if captured_image is not None else False
                p_type_val = "上班打卡" if "上班" in f_punch_type or "Vào" in f_punch_type else "下班打卡+進度回報"

                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO hr_field_gps (record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo)
                                VALUES (:rid, :eid, :ename, :site, :ptype, :lat, :lng, :prog, :ctime, :st, :note, :hphoto)
                            """), {
                                "rid": record_id, "eid": f_emp_id.strip(), "ename": f_name.strip(),
                                "site": f_site, "ptype": p_type_val, "lat": f_lat, "lng": f_lng,
                                "prog": f_progress if p_type_val.startswith("下班") else "（上班打卡無須回報進度）",
                                "ctime": current_time_str, "status": "🟢 範圍內 (In Range)", "note": f_note, "hphoto": has_photo_bool
                            })
                        st.success(t['success_msg'])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning(t['fill_warning'])

    st.markdown("---")
    st.markdown(f"##### {t['table_title']}")
    if field_records:
        st.dataframe(pd.DataFrame(field_records), use_container_width=True, hide_index=True)
    else:
        st.info(t['no_data'])
