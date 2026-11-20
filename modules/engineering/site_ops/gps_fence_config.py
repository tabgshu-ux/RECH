# ==========================================
# 檔案路徑：modules/engineering/site_ops/gps_fence_config.py
# 職責：工程部 - 設定工程打卡施工範圍（GPS 圍籬中心座標與允許半徑）
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_fence_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_gps_fences (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        project_id VARCHAR(80),
                        site_name VARCHAR(160) NOT NULL,
                        lat NUMERIC(10, 6) NOT NULL,
                        lng NUMERIC(10, 6) NOT NULL,
                        radius_meters INT DEFAULT 300,
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_fences(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "lat": 10.980400,
            "lng": 106.651900,
            "radius_meters": 300,
            "is_active": True,
            "updated_by": "系統預設",
        },
        {
            "project_id": "PRJ-2026-02",
            "site_name": "平陽工業區機電工程",
            "lat": 11.051200,
            "lng": 106.665400,
            "radius_meters": 500,
            "is_active": True,
            "updated_by": "系統預設",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(project_id, '-') AS project_id,
                           site_name, lat, lng,
                           COALESCE(radius_meters, 300) AS radius_meters,
                           COALESCE(is_active, TRUE) AS is_active,
                           COALESCE(updated_by, '-') AS updated_by
                    FROM eng_gps_fences
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Manager"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    txt = {
        "zh": {
            "title": "🧭 設定工程打卡施工範圍（GPS 圍籬）",
            "sub": "設定各工程案場的中心 GPS 座標與允許打卡半徑（公尺），供外勤人員定位查核。",
            "pid": "專案編號 (project_id)",
            "sname": "工地／案場名稱*",
            "lat": "中心緯度 (Latitude)*",
            "lng": "中心經度 (Longitude)*",
            "rad": "允許打卡半徑（公尺）*",
            "save": "💾 儲存 GPS 施工範圍",
            "ok": "✅ 已儲存工地【{}】GPS 圍籬（半徑 {} 公尺）。",
        },
        "vi": {
            "title": "🧭 Cấu Hình Phạm Vi Chấm Công Công Trường (Hàng Rào GPS)",
            "sub": "Thiết lập tọa độ GPS trung tâm và bán kính cho phép chấm công (mét) theo từng dự án.",
            "pid": "Mã Dự Án",
            "sname": "Tên Công Trường*",
            "lat": "Vĩ Độ Trung Tâm*",
            "lng": "Kinh Độ Trung Tâm*",
            "rad": "Bán Kính Cho Phép (Mét)*",
            "save": "💾 Lưu Phạm Vi GPS",
            "ok": "✅ Đã lưu hàng rào GPS công trường [{}] (bán kính {} m).",
        },
        "en": {
            "title": "🧭 Configure Field Clock-In Geofence",
            "sub": "Set center GPS coordinates and allowed check-in radius (meters) per engineering site.",
            "pid": "Project ID",
            "sname": "Site Name*",
            "lat": "Center Latitude*",
            "lng": "Center Longitude*",
            "rad": "Allowed Radius (Meters)*",
            "save": "💾 Save GPS Geofence",
            "ok": "✅ Saved geofence for [{}] (radius {} m).",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_fence_table(engine)

    df = _load_fences(engine, tenant_id)
    disp = df.rename(columns={
        "project_id": "專案編號",
        "site_name": "工地／案場",
        "lat": "緯度 (Lat)",
        "lng": "經度 (Lng)",
        "radius_meters": "允許半徑(m)",
        "is_active": "啟用中",
        "updated_by": "更新人",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.divider()
    with st.form("form_eng_gps_fence"):
        c1, c2 = st.columns(2)
        with c1:
            pid = st.text_input(txt["pid"], value="PRJ-2026-01")
            sname = st.text_input(txt["sname"], placeholder="例：西寧廠二期配電盤擴建")
            lat = st.number_input(txt["lat"], value=10.980400, format="%.6f")
        with c2:
            lng = st.number_input(txt["lng"], value=106.651900, format="%.6f")
            radius = st.number_input(txt["rad"], min_value=20, max_value=10000, value=300, step=10)
            is_act = st.checkbox("立即啟用此圍籬", value=True)

        if st.form_submit_button(txt["save"], type="primary", use_container_width=True):
            if not sname.strip():
                st.warning("⚠️ 請填寫工地／案場名稱。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_gps_fences (
                                    tenant_id, project_id, site_name, lat, lng,
                                    radius_meters, is_active, updated_by, updated_at
                                )
                                VALUES (
                                    :tid, :pid, :sname, :lat, :lng,
                                    :rad, :act, :uby, :uat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "pid": pid.strip() or None,
                                "sname": sname.strip(),
                                "lat": float(lat),
                                "lng": float(lng),
                                "rad": int(radius),
                                "act": bool(is_act),
                                "uby": user_name,
                                "uat": now_vn,
                            },
                        )
                    st.success(txt["ok"].format(sname.strip(), int(radius)))
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存 GPS 圍籬失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
