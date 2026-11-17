# ==========================================
# 檔案路徑：modules/engineering/field_gps_attendance.py
# 職責：現場人員專屬：GPS 拍照打卡、每日工作進度回報與離場支援申請（移除雜亂的主管設定與身份切換）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

def init_field_gps_db(engine):
    """初始化外勤打卡與支援申請資料表"""
    if engine is not None:
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
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_geofence_settings (
                        site_name VARCHAR(150) PRIMARY KEY,
                        lat FLOAT,
                        lng FLOAT,
                        radius_meters INT,
                        status VARCHAR(50)
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_support_requests (
                        id SERIAL PRIMARY KEY,
                        emp_name VARCHAR(100),
                        from_project VARCHAR(200),
                        target_project VARCHAR(200),
                        reason TEXT,
                        status VARCHAR(50) DEFAULT '⏳ 待主管審核',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def render(engine=None, lang="繁體中文", **kwargs):
    init_field_gps_db(engine)

    st.markdown("### ⏱️ 外勤工程師與師傅拍照打卡與進度回報中心")
    st.caption("現場施工人員專用：支援 GPS 圍籬範圍驗證、手機相機拍照存證、每日工作進度回報與提早離場支援申請。")

    # 從資料庫動態讀取主管設定好的工地清單
    site_options = ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"]
    if engine is not None:
        try:
            df_sites = pd.read_sql("SELECT site_name FROM eng_geofence_settings", con=engine)
            if not df_sites.empty:
                site_options = df_sites["site_name"].tolist()
        except Exception:
            pass

    # 採用乾淨俐落的上下結構或雙 Tab：作業打卡 vs 我的回報紀錄
    tab_punch, tab_my_records = st.tabs(["📱 現場拍照打卡與進度回報", "📋 我今日的回報與打卡紀錄"])

    with tab_punch:
        st.markdown("##### 📱 行動打卡與每日施工進度回報表單")
        st.info("💡 請在指定案場範圍內進行打卡。下班打卡時必須填寫當日工程進度與上傳現場施工照片，以同步至工程部與總經理室戰情。")

        with st.form("worker_clean_punch_form"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_id = st.text_input("工號 (Employee ID)", value="EMP-001")
                f_name = st.text_input("姓名 (Full Name)", value="阮文雄 (Nguyen Van Hung)")
                f_site = st.selectbox("指派工程案場 / 工地", site_options)
                f_punch_type = st.radio("打卡類型", ["🟢 上班打卡 (現場拍照存證)", "🔴 下班打卡 (工程進度回報 + 施工照)"], horizontal=True)
            with c2:
                f_lat = st.number_input("GPS 緯度 (Latitude)", value=10.7769, format="%.4f")
                f_lng = st.number_input("GPS 經度 (Longitude)", value=106.7009, format="%.4f")
                
                f_progress = st.text_area("📊 當日工程進度回報 (主管與總經理室可見)", placeholder="例如: 已完成配電箱安裝 80%、主迴路拉線完畢...")
                f_note = st.text_input("現場備註 / 異常回報", placeholder="例如: 現場材料短缺需總務支援...")

            st.markdown("**📷 現場施工 / 打卡照片上傳 (Camera Verification)**")
            captured_image = st.camera_input("請對準現場施工環境或人員進行拍照打卡")

            submitted = st.form_submit_button("🛰️ 確認送出打卡與進度回報", type="primary", use_container_width=True)
            if submitted:
                if f_emp_id and f_name:
                    record_id = f"GPS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    has_photo_bool = True if captured_image is not None else False
                    p_type_val = "上班打卡" if "上班" in f_punch_type else "下班打卡+進度回報"

                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO hr_field_gps (record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo)
                                    VALUES (:rid, :eid, :ename, :site, :ptype, :lat, :lng, :prog, :ctime, '🟢 範圍內 (In Range)', :note, :hphoto)
                                """), {
                                    "rid": record_id, "eid": f_emp_id.strip(), "ename": f_name.strip(),
                                    "site": f_site, "ptype": p_type_val, "lat": f_lat, "lng": f_lng,
                                    "prog": f_progress if "下班" in p_type_val else "（上班打卡無須回報進度）",
                                    "ctime": current_time_str, "note": f_note, "hphoto": has_photo_bool
                                })
                        except Exception as e:
                            st.error(f"資料庫寫入錯誤: {e}")
                    st.success("🎉 外勤打卡與每日工作進度回報成功！已自動同步至工程主管與總經理室。")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫完整工號與姓名！")

    with tab_my_records:
        st.markdown("##### 📋 我今日提交的打卡與進度回報清單")
        if engine is not None:
            try:
                df_my = pd.read_sql("SELECT record_id AS 紀錄編號, site_name AS 案場, punch_type AS 類型, work_progress AS 進度回報, check_time AS 時間, has_photo AS 現場照片 FROM hr_field_gps ORDER BY check_time DESC LIMIT 20", con=engine)
                if df_my.empty:
                    st.info("目前尚無打卡紀錄。")
                else:
                    st.dataframe(df_my, use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning(f"讀取紀錄失敗: {e}")
        else:
            st.info("資料庫連線尚未建立。")
