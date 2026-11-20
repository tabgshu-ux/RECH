# ==========================================
# 檔案路徑：modules/engineering/site_ops/gps_attendance.py
# 職責：外勤工程人員極簡一鍵打卡（自動帶出時間、GPS 定位與現場拍照回傳）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import text
from core import ui_theme


def _ensure_clockin_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_field_clockins (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        employee_name VARCHAR(120) NOT NULL,
                        project_id VARCHAR(80),
                        clock_type VARCHAR(24) DEFAULT 'CLOCK_IN',
                        clock_time TIMESTAMP WITH TIME ZONE NOT NULL,
                        gps_lat NUMERIC(10, 6),
                        gps_lng NUMERIC(10, 6),
                        gps_address VARCHAR(255),
                        photo_base64 TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _render_geo_bridge():
    """自動取得瀏覽器目前 GPS 經緯度並寫入網址 query params（無需手動填寫）"""
    components.html(
        """
        <script>
        (function() {
            if (!navigator.geolocation) return;
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    const lat = pos.coords.latitude.toFixed(6);
                    const lng = pos.coords.longitude.toFixed(6);
                    try {
                        const url = new URL(window.parent.location.href);
                        if (url.searchParams.get("gps_lat") !== lat || url.searchParams.get("gps_lng") !== lng) {
                            url.searchParams.set("gps_lat", lat);
                            url.searchParams.set("gps_lng", lng);
                            window.parent.history.replaceState({}, "", url.toString());
                        }
                    } catch (e) {}
                },
                function() {},
                { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
            );
        })();
        </script>
        """,
        height=0,
    )


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    emp_name = st.session_state.get("user_name") or "外勤工程人員"

    txt = {
        "zh": {
            "title": "📍 外勤工程人員打卡",
            "sub": "點選拍照後一鍵打卡，系統自動帶出時間與定位回傳。",
            "cam_label": "📷 拍攝工程人員／工地現場照片",
            "btn_in": "🟢 一鍵打卡回傳",
            "sent_ok": "✅ 已打卡回傳！時間：{}｜定位：{}",
            "no_photo": "⚠️ 請先完成拍照再按打卡回傳。",
            "recent": "🕒 今日打卡回傳紀錄",
            "empty": "尚無打卡紀錄。",
        },
        "vi": {
            "title": "📍 Chấm Công Kỹ Sư Ngoài Công Trường",
            "sub": "Chụp ảnh và bấm chấm công một chạm, hệ thống tự gửi thời gian và vị trí.",
            "cam_label": "📷 Chụp ảnh nhân sự / hiện trường công trình",
            "btn_in": "🟢 Gửi Chấm Công",
            "sent_ok": "✅ Đã gửi chấm công! Thời gian: {} | Vị trí: {}",
            "no_photo": "⚠️ Vui lòng chụp ảnh trước khi gửi chấm công.",
            "recent": "🕒 Lịch Sử Chấm Công Hôm Nay",
            "empty": "Chưa có dữ liệu chấm công.",
        },
        "en": {
            "title": "📍 Field Engineer Quick Clock-In",
            "sub": "Take a photo and clock in with one tap; timestamp and GPS location are sent automatically.",
            "cam_label": "📷 Capture Engineer / Site Photo",
            "btn_in": "🟢 Clock In Now",
            "sent_ok": "✅ Clock-in sent! Time: {} | Location: {}",
            "no_photo": "⚠️ Please capture a photo before clocking in.",
            "recent": "🕒 Today's Clock-In Log",
            "empty": "No clock-in records yet.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_clockin_table(engine)
    _render_geo_bridge()

    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    time_str = now_vn.strftime("%Y-%m-%d %H:%M:%S")

    q_lat = st.query_params.get("gps_lat")
    q_lng = st.query_params.get("gps_lng")
    gps_lat = float(q_lat) if q_lat else None
    gps_lng = float(q_lng) if q_lng else None
    loc_text = f"{gps_lat:.6f}, {gps_lng:.6f}" if (gps_lat is not None and gps_lng is not None) else "定位取得中 / 依裝置定位回傳"

    st.caption(f"👤 {emp_name}  ｜  🕒 {time_str}  ｜  📌 {loc_text}")

    photo = st.camera_input(txt["cam_label"], key="field_quick_camera")

    if st.button(txt["btn_in"], type="primary", use_container_width=True):
        if photo is None:
            st.warning(txt["no_photo"])
        elif not engine:
            st.error("❌ 尚未連線資料庫。")
        else:
            import base64

            raw_bytes = photo.getvalue()
            b64_str = base64.b64encode(raw_bytes).decode("utf-8")
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO eng_field_clockins (
                                tenant_id, employee_name, project_id, clock_type,
                                clock_time, gps_lat, gps_lng, gps_address, photo_base64
                            )
                            VALUES (
                                :tid, :ename, :pid, 'CLOCK_IN',
                                :ctime, :lat, :lng, :addr, :b64
                            )
                        """),
                        {
                            "tid": tenant_id,
                            "ename": emp_name,
                            "pid": st.session_state.get("active_project_id"),
                            "ctime": now_vn,
                            "lat": gps_lat,
                            "lng": gps_lng,
                            "addr": loc_text,
                            "b64": b64_str,
                        },
                    )
                st.success(txt["sent_ok"].format(time_str, loc_text))
                st.rerun()
            except Exception as e:
                st.error(f"❌ 打卡回傳失敗：{e}")

    st.divider()
    st.markdown(f"#### {txt['recent']}")
    if not engine:
        st.info(txt["empty"])
        return
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT employee_name AS "人員",
                           TO_CHAR(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh', 'YYYY-MM-DD HH24:MI:SS') AS "打卡時間",
                           COALESCE(gps_address, '-') AS "定位座標"
                    FROM eng_field_clockins
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                    LIMIT 20
                """),
                {"tid": tenant_id},
            ).fetchall()
            if not rows:
                st.info(txt["empty"])
            else:
                st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
    except Exception:
        st.info(txt["empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
