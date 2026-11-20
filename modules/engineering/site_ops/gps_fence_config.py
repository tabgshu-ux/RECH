# ==========================================
# 檔案路徑：modules/engineering/site_ops/gps_fence_config.py
# 職責：工程部 - 設定工程打卡施工範圍（支援地址搜尋、Google Map 選點/網址解析、裝置 GPS 定位）
# ==========================================

from datetime import datetime
import json
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
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("ALTER TABLE eng_gps_fences ADD COLUMN IF NOT EXISTS address_text VARCHAR(255);")
            )
    except Exception:
        pass


def _load_fences(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "project_id": "PRJ-2026-01",
            "site_name": "西寧廠二期配電盤擴建",
            "address_text": "Tây Ninh, Việt Nam",
            "lat": 10.980400,
            "lng": 106.651900,
            "radius_meters": 300,
            "is_active": True,
            "updated_by": "系統預設",
        },
        {
            "project_id": "PRJ-2026-02",
            "site_name": "平陽工業區機電工程",
            "address_text": "Bình Dương, Việt Nam",
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
                           site_name,
                           COALESCE(address_text, '-') AS address_text,
                           lat, lng,
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


def _geocode_address(query: str) -> tuple[float | None, float | None, str]:
    """透過公開地理編碼服務查詢地址經緯度（含安全降級）"""
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
                lat_v = round(float(data[0]["lat"]), 6)
                lng_v = round(float(data[0]["lon"]), 6)
                disp = data[0].get("display_name", clean_q)
                return lat_v, lng_v, disp
        return None, None, "查無此地址座標，建議改用下方「開啟 Google Map 選點」後貼上座標或網址。"
    except Exception:
        return None, None, "目前無法連線地址查詢服務，請改用 Google Map 選點或裝置 GPS 定位。"


def _parse_gmap_coords(raw_text: str) -> tuple[float | None, float | None]:
    """從 Google Maps 網址（如 @10.9804,106.6519 或 ?q=10.9804,106.6519）或純文字座標解析經緯度"""
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
    """提供手機／瀏覽器目前 GPS 定位擷取工具"""
    components.html(
        """
        <div style="font-family: sans-serif; padding: 8px 10px; border: 1px solid #d0d7de; border-radius: 8px; background: #f8fafc;">
            <div style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">📱 目前裝置 GPS 定位（若您就在案場現場）</div>
            <button type="button" onclick="getLoc()" style="padding: 6px 12px; border-radius: 6px; border: 1px solid #0f766e; background: #0f766e; color: #fff; cursor: pointer; font-size: 13px;">
                📡 取得目前 GPS 座標
            </button>
            <div id="gps_out" style="margin-top: 8px; font-size: 13px; color: #1e293b;">尚未取得定位</div>
        </div>
        <script>
        function getLoc() {
            const out = document.getElementById('gps_out');
            if (!navigator.geolocation) {
                out.innerText = '此瀏覽器不支援 GPS 定位，請改用地址搜尋或 Google Map。';
                return;
            }
            out.innerText = '正在定位中，請稍候...';
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude.toFixed(6);
                    const lng = pos.coords.longitude.toFixed(6);
                    out.innerHTML = '已取得座標：<b>' + lat + ', ' + lng + '</b>（可複製貼到下方 Google Map / 座標解析框）';
                },
                (err) => {
                    out.innerText = '無法取得 GPS 定位（請確認已允許定位權限，或改用地址搜尋／Google Map）。';
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }
        </script>
        """,
        height=105,
    )


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Manager"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    _ = code
    st.markdown("### 🧭 設定工程打卡施工範圍（GPS 圍籬）")
    st.caption("免背經緯度：可用「地址搜尋」、「Google Map 選點／貼上網址」或「目前裝置 GPS」自動帶入案場位置。")
    _ensure_fence_table(engine)

    if "fence_lat" not in st.session_state:
        st.session_state["fence_lat"] = 10.980400
    if "fence_lng" not in st.session_state:
        st.session_state["fence_lng"] = 106.651900
    if "fence_addr" not in st.session_state:
        st.session_state["fence_addr"] = ""

    df = _load_fences(engine, tenant_id)
    disp = df.rename(columns={
        "project_id": "專案編號",
        "site_name": "工地／案場",
        "address_text": "地址／位置",
        "lat": "緯度 (Lat)",
        "lng": "經度 (Lng)",
        "radius_meters": "允許半徑(m)",
        "is_active": "啟用中",
        "updated_by": "更新人",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 📍 1. 找地點（地址搜尋 / Google Map 選點 / 目前 GPS）")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        addr_query = st.text_input(
            "輸入工地地址或地標名稱",
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
            placeholder="在 Google 地圖點選案場後，複製網址或座標貼在這裡",
            key="fence_gmap_paste",
        )
        if st.button("📌 解析並帶入經緯度", key="btn_parse_gmap", use_container_width=True):
            plat, plng = _parse_gmap_coords(gmap_paste)
            if plat is not None and plng is not None:
                st.session_state["fence_lat"] = plat
                st.session_state["fence_lng"] = plng
                st.success(f"✅ 已帶入座標：{plat}, {plng}")
                st.rerun()
            else:
                st.warning("⚠️ 無法從輸入內容辨識經緯度，請確認包含「緯度, 經度」或 Google Map `@lat,lng` 網址。")

    st.divider()
    st.markdown("#### 💾 2. 確認並儲存 GPS 施工範圍")

    with st.form("form_eng_gps_fence"):
        c1, c2 = st.columns(2)
        with c1:
            pid = st.text_input("專案編號 (project_id)", value="PRJ-2026-01")
            sname = st.text_input("工地／案場名稱*", placeholder="例：西寧廠二期配電盤擴建")
            lat = st.number_input("緯度 (Lat，自動帶入或微調)", value=float(st.session_state["fence_lat"]), format="%.6f")
        with c2:
            lng = st.number_input("經度 (Lng，自動帶入或微調)", value=float(st.session_state["fence_lng"]), format="%.6f")
            radius = st.number_input("允許打卡半徑（公尺）*", min_value=20, max_value=10000, value=300, step=10)
            is_act = st.checkbox("立即啟用此圍籬", value=True)

        if st.form_submit_button("💾 儲存 GPS 施工範圍", type="primary", use_container_width=True):
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
                                    tenant_id, project_id, site_name, address_text,
                                    lat, lng, radius_meters, is_active, updated_by, updated_at
                                )
                                VALUES (
                                    :tid, :pid, :sname, :addr,
                                    :lat, :lng, :rad, :act, :uby, :uat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "pid": pid.strip() or None,
                                "sname": sname.strip(),
                                "addr": (addr_query.strip() or st.session_state.get("fence_addr") or None),
                                "lat": float(lat),
                                "lng": float(lng),
                                "rad": int(radius),
                                "act": bool(is_act),
                                "uby": user_name,
                                "uat": now_vn,
                            },
                        )
                    st.success(f"✅ 已儲存工地【{sname.strip()}】GPS 圍籬（座標：{lat:.6f}, {lng:.6f}｜半徑 {int(radius)} 公尺）。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存 GPS 圍籬失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
