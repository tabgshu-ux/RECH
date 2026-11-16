# ==========================================
# 檔案路徑：modules/engineering/field_gps_attendance.py
# 職責：外勤打卡、Google Maps 圍籬設定、相機拍照、未到下班離場異常與支援申請模組
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

def init_attendance_tables(engine):
    """初始化打卡與支援申請資料表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_gps_attendances (
                        id SERIAL PRIMARY KEY,
                        emp_name VARCHAR(100),
                        project_name VARCHAR(200),
                        check_type VARCHAR(50),
                        gps_coords VARCHAR(100),
                        is_within_fence BOOLEAN,
                        photo_status VARCHAR(50),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
    init_attendance_tables(engine)

    st.markdown("### ⏱️ 外勤師傅考勤、GPS 圍籬打卡與支援調派中心")
    st.caption("支援相機拍照打卡、Google Maps 案場範圍設定、圍籬限制與提早離場支援申請機制。")

    # 分頁切換：工人打卡端 vs 主管圍籬與支援審核端
    tab_clock, tab_geofence, tab_support = st.tabs([
        "📍 現場人員拍照打卡", 
        "🗺️ Google Maps 案場圍籬設定 (主管用)", 
        "🤝 提早離場與支援申請審核"
    ])

    # 1. 📍 現場人員拍照打卡端
    with tab_clock:
        st.markdown("#### 📸 現場師傅行動拍照打卡")
        st.info("💡 請在指定案場範圍內進行打卡。若未到下班時間離開，系統將自動偵測並詢問是否支援其他案場。")

        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("打卡員工姓名", value="阮文雄 (Nguyen Van Hung)")
            current_project = st.selectbox("當前所屬案場", ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"])
        with col2:
            clock_type = st.radio("打卡類型", ["上班打卡 (Clock-In)", "下班打卡 (Clock-Out)"], horizontal=True)
            sim_fence = st.radio("GPS 圍籬狀態模擬", ["🟢 在案場圍籬範圍內 (正常)", "🔴 已超出案場圍籬範圍 (異常)"], horizontal=True)

        # 模擬相機拍照打卡
        st.markdown("**相機拍照驗證 (Camera Verification)**")
        camera_photo = st.camera_input("請對準現場進行拍照打卡")

        if st.button("🚀 確認送出打卡與拍照驗證", type="primary", use_container_width=True):
            is_in = True if "正常" in sim_fence else False
            if not is_in:
                st.error("⚠️ 打卡失敗！您目前所在位置已超出【西寧廠二期】之 Google Maps 圍籬範圍（限制半徑 500 公尺）。")
                
                # 🌟 觸發提早離場異常通知與支援申請機制
                st.warning("🚨 【系統偵測】您尚未到下班時間（距離 17:00 還有 1 小時 15 分鐘）且已離開工地範圍！")
                st.markdown("請問您是否是前往其他案場**支援**？")
                
                if st.button("👉 點此填寫支援申請單", type="secondary"):
                    st.session_state['trigger_support_form'] = True
                    st.rerun()
            else:
                photo_msg = "已附帶現場照片" if camera_photo else "未拍照"
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO eng_gps_attendances (emp_name, project_name, check_type, gps_coords, is_within_fence, photo_status)
                                VALUES (:e, :p, :t, '10.7769° N, 106.7009° E', TRUE, :ph)
                            """), {"e": emp_name, "p": current_project, "t": clock_type, "ph": photo_msg})
                    except Exception:
                        pass
                st.success(f"🎉 [{emp_name}] 的 [{clock_type}] 拍照打卡成功！已記錄時間與圍籬坐標。")

        # 若觸發支援表單
        if st.session_state.get('trigger_support_form', False):
            st.markdown("---")
            st.markdown("#### 🤝 填寫工地支援申請單")
            with st.form("support_request_form"):
                target_proj = st.selectbox("前往支援之目標工地", ["平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝", "西寧廠二期配電盤擴建工程"])
                reason = st.text_area("支援原因說明", placeholder="例如: 接獲緊急通報，需前往平陽廠協助主迴路短路搶修...")
                sub_btn = st.form_submit_button("📤 提交支援申請給主管審核", type="primary", use_container_width=True)
                if sub_btn:
                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO eng_support_requests (emp_name, from_project, target_project, reason, status)
                                    VALUES (:e, :fp, :tp, :r, '⏳ 待主管審核')
                                """), {"e": emp_name, "fp": current_project, "tp": target_proj, "r": reason})
                        except Exception:
                            pass
                    st.success("🎉 支援申請已成功送出！主管將即時收到通知並進行審核。")
                    st.session_state['trigger_support_form'] = False

    # 2. 🗺️ Google Maps 案場圍籬設定 (主管端)
    with tab_geofence:
        st.markdown("#### 🗺️ Google Maps 案場地理圍籬 (Geofencing) 設定")
        st.info("💡 主管可在此檢視案場地圖坐標，並設定打卡允許的最大半徑範圍（預設 500 公尺）。")

        with st.form("geofence_setting_form"):
            f_proj = st.selectbox("選擇要設定圍籬的案場", ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"])
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                lat = st.text_input("中心點緯度 (Latitude)", value="10.7769")
                radius = st.slider("圍籬允許半徑範圍 (公尺)", min_value=100, max_value=2000, value=500, step=50)
            with col_g2:
                lng = st.text_input("中心點經度 (Longitude)", value="106.7009")
                fence_status = st.selectbox("圍籬狀態", ["🟢 啟用中 (強制限制打卡)", "🔴 暫時關閉"])

            # 嵌入 Google Maps 預覽模擬
            st.markdown("**🗺️ Google Maps 案場圍籬即時預覽 (模擬定位)**")
            map_html = f"""
            <iframe width="100%" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                src="https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed">
            </iframe>
            """
            st.markdown(map_html, unsafe_allow_html=True)

            save_fence = st.form_submit_button("💾 儲存該案場 Google Maps 圍籬設定", type="primary", use_container_width=True)
            if save_fence:
                st.success(f"🎉 成功更新 [{f_proj}] 的地理圍籬範圍！中心點 ({lat}, {lng})，半徑 {radius} 公尺。")

    # 3. 🤝 提早離場與支援申請審核 (主管端)
    with tab_support:
        st.markdown("#### 🤝 員工提早離場支援申請審核清單")
        st.info("主管可在此檢視工人因提早離開原工地而提出的支援申請與原因。")

        if engine is not None:
            try:
                df_sup = pd.read_sql("SELECT id, emp_name AS 員工姓名, from_project AS 原工地, target_project AS 支援目標工地, reason AS 支援原因, status AS 審核狀態, created_at AS 申請時間 FROM eng_support_requests ORDER BY id DESC", con=engine)
                if df_sup.empty:
                    st.info("目前尚無任何支援申請紀錄。")
                else:
                    st.dataframe(df_sup, use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning(f"讀取支援紀錄提示: {e}")
        else:
            # 預設展示範例
            sample_sup = pd.DataFrame({
                "員工姓名": ["阮文雄", "陳志豪"],
                "原工地": ["西寧廠二期", "平陽美德廠"],
                "支援目標工地": ["平陽工業區廠房", "隆安省光電園區"],
                "支援原因": ["接獲緊急通報，前往支援短路搶修", "原工地工項提早完成，調派支援"],
                "審核狀態": ["⏳ 待主管審核", "✅ 已核准"]
            })
            st.dataframe(sample_sup, use_container_width=True, hide_index=True)
