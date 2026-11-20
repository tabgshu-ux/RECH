# ==========================================
# 檔案路徑：modules/engineering/site_ops/gps_fence_config.py
# 職責：工程部 - 設定工程打卡施工範圍（支援整塊工地邊界框選／多點圍籬 + 範圍外擴緩衝公尺數）
# ==========================================

from datetime import datetime
import json
import math
import re
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
                        address_text VARCHAR(255),
                        lat NUMERIC(10, 6) NOT NULL,
                        lng NUMERIC(10, 6) NOT NULL,
                        radius_meters INT DEFAULT 300,
                        buffer_meters INT DEFAULT 300,
                        boundary_points TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(text("ALTER TABLE eng_gps_fences ADD COLUMN IF NOT EXISTS address_text VARCHAR(255);"))
            conn.execute(text("ALTER TABLE eng_gps_fences ADD COLUMN IF NOT EXISTS buffer_meters INT DEFAULT 300;"))
            conn.execute(text("ALTER TABLE eng_gps_fences ADD COLUMN IF NOT EXISTS boundary_points TEXT;"))
    except Exception:
        pass


def _polygon_area_hectares(points: list[dict]) -> float:
    """估算多邊形工地範圍面積（公頃，平面近似供管理員參考）"""
    if len(points) < 3:
        return 0.0
    ref_lat = sum(float(p["lat"]) for p in points) / len(points)
    m_per_deg_lat = 111320.0
    m_per_deg_lng = 111320.0 * math.cos(math.radians(ref_lat))
    xy = [
        ((float(p["lng"]) - float(points[0]["lng"])) * m_per_deg_lng,
         (float(p["lat"]) - float(points[0]["lat"])) * m_per_deg_lat)
        for p in points
    ]
    area_m2 = 0.0
    n = len(xy)
    for i in range(n):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % n]
        area_m2 += (x1 * y2 - x2 * y1)
    return round(abs(area_m2) / 2.0 / 10000.0, 2)


def _polygon_centroid(points: list[dict]) -> tuple[float, float]:
    lat_avg = sum(float(p["lat"]) for p in points) / len(points)
    lng_avg = sum(float(p["lng"]) for p in points) / len(points)
    return round(lat_avg, 6), round(lng_avg, 6)


def _load_fences(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "address_text": "Tây Ninh, Việt Nam",
            "lat": 10.980400,
            "lng": 106.651900,
            "boundary_pts_count": 0,
            "est_ha": 0.0,
            "buffer_meters": 300,
            "is_active": True,
            "updated_by": "系統預設",
        }
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(project_id, '-') AS project_id,
                           site_name,
                           COALESCE(address_text, '-') AS address_text,
                           lat, lng,
                           COALESCE(buffer_meters, radius_meters, 300) AS buffer_meters,
                           boundary_points,
                           COALESCE(is_active, TRUE) AS is_active,
                           COALESCE(updated_by, '-') AS updated_by
                    FROM eng_gps_fences
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if not rows:
                return pd.DataFrame(fallback)
            out = []
            for r in rows:
                d = r._asdict()
                pts = []
                if d.get("boundary_points"):
                    try:
                        parsed = json.loads(d["boundary_points"])
                        if isinstance(parsed, list):
                            pts = parsed
                    except Exception:
                        pts = []
                out.append({
                    "project_id": d["project_id"],
                    "site_name": d["site_name"],
                    "address_text": d["address_text"],
                    "lat": d["lat"],
                    "lng": d["lng"],
                    "boundary_pts_count": len(pts),
                    "est_ha": _polygon_area_hectares(pts) if len(pts) >= 3 else 0.0,
                    "buffer_meters": d["buffer_meters"],
                    "is_active": d["is_active"],
                    "updated_by": d["updated_by"],
                })
            return pd.DataFrame(out)
    except Exception:
        return pd.DataFrame(fallback)


def _geocode_address(query: str) -> tuple[float | None, float | None, str]:
    clean_q = (query or "").strip()
    if not clean_q:
        return None, None, "請先輸入地址或案場地名。"
    try:
        url = "https://nominatim.openstreetmap.org/search?" + urlencode(
            {"q": clean_q, "format": "json", "limit": 1}
        )
        req = Request(url, headers={"User-Agent": "RECH-SaaS-ERP/1.0"})
        with urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                return round(float(data[0]["lat"]), 6), round(float(data[0]["lon"]), 6), data[0].get("display_name", clean_q)
        return None, None, "查無此地址座標，建議改用 Google Map 選點或貼上座標。"
    except Exception:
        return None, None, "目前無法連線地址查詢服務，請改用 Google Map 選點或裝置 GPS 定位。"


def _parse_gmap_coords(raw_text: str) -> tuple[float | None, float | None]:
    txt = (raw_text or "").strip()
    if not txt:
        return None, None
    patterns = [
        r"@(-?\d+\.\d+),\s*(-?\d+\.\d+)",
        r"[?&](?:q|ll|query)=(-?\d+\.\d+),\s*(-?\d+\.\d+)",
        r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, txt)
        if m:
            lat_v = float(m.group(1))
            lng_v = float(m.group(2))
            if -90.0 <= lat_v <= 90.0 and -180.0 <= lng_v <= 180.0:
                return round(lat_v, 6), round(lng_v, 6)
    return None, None


def _render_device_gps_helper():
    components.html(
        """
        <div style="font-family: sans-serif; padding: 8px 10px; border: 1px solid #d0d7de; border-radius: 8px; background: #f8fafc;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">📱 目前裝置 GPS 定位（人在工地邊界／角點時可直接抓座標）</div>
            <button type="button" onclick="getLoc()" style="padding: 6px 12px; border-radius: 6px; border: 1px solid #0f766e; background: #0f766e; color: #fff; cursor: pointer; font-size: 13px;">
                📡 取得目前 GPS 座標
            </button>
            <div id="gps_out" style="margin-top: 8px; font-size: 13px; color: #1e293b;">尚未取得定位</div>
        </div>
        <script>
        function getLoc() {
            const out = document.getElementById('gps_out');
            if (!navigator.geolocation) {
                out.innerText = '此瀏覽器不支援 GPS 定位。';
                return;
            }
            out.innerText = '正在定位中...';
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude.toFixed(6);
                    const lng = pos.coords.longitude.toFixed(6);
                    out.innerHTML = '目前座標：<b>' + lat + ', ' + lng + '</b>';
                },
                () => {
                    out.innerText = '無法取得 GPS 定位，請改用地址搜尋或 Google Map。';
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }
        </script>
        """,
        height=105,
    )


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Manager"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🧭 設定工程打卡施工範圍（整塊工地框選＋外擴緩衝）")
    st.caption("大型工地可把工地各角點框選成範圍，再加上「範圍外擴緩衝（公尺，如 300m）」，整塊工地與周邊 300m 內都能打卡。")
    _ensure_fence_table(engine)

    if "fence_lat" not in st.session_state:
        st.session_state["fence_lat"] = 10.980400
    if "fence_lng" not in st.session_state:
        st.session_state["fence_lng"] = 106.651900
    if "fence_addr" not in st.session_state:
        st.session_state["fence_addr"] = ""
    if "fence_poly_pts" not in st.session_state:
        st.session_state["fence_poly_pts"] = []

    df = _load_fences(engine, tenant_id)
    disp = df.rename(columns={
        "project_id": "專案編號",
        "site_name": "工地／案場",
        "address_text": "地址／位置",
        "lat": "中心緯度",
        "lng": "中心經度",
        "boundary_pts_count": "框選角點數",
        "est_ha": "估算面積(公頃)",
        "buffer_meters": "範圍外擴(m)",
        "is_active": "啟用中",
        "updated_by": "更新人",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 📍 1. 找地點並框選工地範圍（地址搜尋 / Google Map / 裝置 GPS）")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        addr_query = st.text_input(
            "輸入工地地址或工業區名稱",
            value=st.session_state["fence_addr"],
            placeholder="例：KCN An Bình, Tây Ninh 或 西寧省工業區",
            key="fence_addr_input",
        )
    with col_s2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 搜尋地址座標", use_container_width=True, key="btn_geocode_addr"):
            glat, glng, gmsg = _geocode_address(addr_query)
            if glat is not None and glng is not None:
                st.session_state["fence_lat"] = glat
                st.session_state["fence_lng"] = glng
                st.session_state["fence_addr"] = gmsg
                st.success(f"✅ 已找到座標：{glat}, {glng}（{gmsg}）")
                st.rerun()
            else:
                st.warning(f"⚠️ {gmsg}")

    gmap_query = addr_query.strip() or f"{st.session_state['fence_lat']},{st.session_state['fence_lng']}"
    gmap_url = f"https://www.google.com/maps/search/?api=1&query={quote(gmap_query)}"

    col_m1, col_m2 = st.columns([1.2, 2.8])
    with col_m1:
        st.link_button("🗺️ 開啟 Google Map 選點", gmap_url, use_container_width=True)
        _render_device_gps_helper()
    with col_m2:
        gmap_paste = st.text_input(
            "貼上 Google Map 網址或座標（例：10.9804, 106.6519 或含 @緯度,經度 的網址）",
            placeholder="在 Google 地圖點選工地角點或中心後，複製網址或座標貼在這裡",
            key="fence_gmap_paste",
        )
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("📌 設為中心座標", key="btn_parse_center", use_container_width=True):
                plat, plng = _parse_gmap_coords(gmap_paste)
                if plat is not None and plng is not None:
                    st.session_state["fence_lat"] = plat
                    st.session_state["fence_lng"] = plng
                    st.success(f"✅ 已設為中心座標：{plat}, {plng}")
                    st.rerun()
                else:
                    st.warning("⚠️ 無法辨識經緯度。")
        with p_col2:
            if st.button("➕ 加入工地框選角點", key="btn_add_poly_pt", type="primary", use_container_width=True):
                plat, plng = _parse_gmap_coords(gmap_paste)
                if plat is not None and plng is not None:
                    st.session_state["fence_poly_pts"].append({"lat": plat, "lng": plng})
                    clat, clng = _polygon_centroid(st.session_state["fence_poly_pts"])
                    st.session_state["fence_lat"] = clat
                    st.session_state["fence_lng"] = clng
                    st.success(f"✅ 已加入第 {len(st.session_state['fence_poly_pts'])} 個工地角點（{plat}, {plng}）。")
                    st.rerun()
                else:
                    st.warning("⚠️ 請先貼上角點座標或 Google Map 網址。")
        with p_col3:
            if st.button("🗑️ 清除框選角點", key="btn_clear_poly_pt", use_container_width=True):
                st.session_state["fence_poly_pts"] = []
                st.info("已清除目前框選角點，將改用單點半徑模式。")
                st.rerun()

    poly_pts = st.session_state["fence_poly_pts"]
    if poly_pts:
        est_ha = _polygon_area_hectares(poly_pts)
        st.info(
            f"📐 目前已框選 **{len(poly_pts)}** 個工地角點（估算範圍約 **{est_ha} 公頃**），儲存時會自動以範圍中心與邊界＋外擴距離計算打卡範圍。"
        )
        st.dataframe(
            pd.DataFrame([{"角點序號": i + 1, "緯度 (Lat)": p["lat"], "經度 (Lng)": p["lng"]} for i, p in enumerate(poly_pts)]),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### 💾 2. 確認並儲存工地打卡範圍")

    with st.form("form_eng_gps_fence"):
        c1, c2 = st.columns(2)
        with c1:
            pid = st.text_input("專案編號 (project_id)", value="PRJ-2026-01")
            sname = st.text_input("工地／案場名稱*", placeholder="例：西寧廠二期配電盤擴建")
            lat = st.number_input("中心緯度 (Lat)", value=float(st.session_state["fence_lat"]), format="%.6f")
        with c2:
            lng = st.number_input("中心經度 (Lng)", value=float(st.session_state["fence_lng"]), format="%.6f")
            buffer_m = st.number_input(
                "工地範圍外擴緩衝（公尺，預設 300m）*",
                min_value=0,
                max_value=5000,
                value=300,
                step=10,
            )
            is_act = st.checkbox("立即啟用此工地範圍", value=True)

        if st.form_submit_button("💾 儲存工地打卡範圍", type="primary", use_container_width=True):
            if not sname.strip():
                st.warning("⚠️ 請填寫工地／案場名稱。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                pts_json = json.dumps(poly_pts) if len(poly_pts) >= 3 else None
                eff_radius = int(buffer_m)
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_gps_fences (
                                    tenant_id, project_id, site_name, address_text,
                                    lat, lng, radius_meters, buffer_meters, boundary_points,
                                    is_active, updated_by, updated_at
                                )
                                VALUES (
                                    :tid, :pid, :sname, :addr,
                                    :lat, :lng, :rad, :buf, :bpts,
                                    :act, :uby, :uat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "pid": pid.strip() or None,
                                "sname": sname.strip(),
                                "addr": (addr_query.strip() or st.session_state.get("fence_addr") or None),
                                "lat": float(lat),
                                "lng": float(lng),
                                "rad": eff_radius,
                                "buf": int(buffer_m),
                                "bpts": pts_json,
                                "act": bool(is_act),
                                "uby": user_name,
                                "uat": now_vn,
                            },
                        )
                    st.session_state["fence_poly_pts"] = []
                    st.success(
                        f"✅ 已儲存工地【{sname.strip()}】打卡範圍（角點：{len(poly_pts)} 點｜外擴緩衝：{int(buffer_m)} 公尺）。"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存工地打卡範圍失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
