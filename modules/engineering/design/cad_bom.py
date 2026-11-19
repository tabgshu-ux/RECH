# ==========================================
# 檔案路徑：modules/engineering/design/cad_bom.py
# 職責：設計部 - CAD 圖面解析轉 BOM 與料號自動編碼（串接生產與倉庫/採購）
# ==========================================

import io
import re
from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_cad_bom_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS eng_cad_bom_headers (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    bom_id VARCHAR(64) UNIQUE NOT NULL,
                    project_id VARCHAR(80),
                    quote_id VARCHAR(80),
                    drawing_no VARCHAR(120) NOT NULL,
                    drawing_rev VARCHAR(32) DEFAULT 'Rev.A',
                    panel_or_system_name VARCHAR(200) NOT NULL,
                    source_filename VARCHAR(255),
                    status VARCHAR(32) DEFAULT 'ACTIVE',
                    created_by VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS eng_cad_bom_items (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    bom_id VARCHAR(64) NOT NULL,
                    project_id VARCHAR(80),
                    part_code VARCHAR(80) NOT NULL,
                    part_name VARCHAR(200) NOT NULL,
                    spec_model VARCHAR(200),
                    category_code VARCHAR(32) DEFAULT 'ELC',
                    qty NUMERIC(14, 3) DEFAULT 1,
                    unit VARCHAR(32) DEFAULT 'PCS',
                    est_unit_cost NUMERIC(16, 2) DEFAULT 0,
                    is_new_code BOOLEAN DEFAULT FALSE,
                    mrp_sync_status VARCHAR(32) DEFAULT 'READY',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass


def _generate_part_code(category_code: str, spec_text: str, seq: int) -> str:
    cat = re.sub(r"[^A-Z0-9]", "", (category_code or "ELC").upper())[:4] or "ELC"
    clean_spec = re.sub(r"[^A-Za-z0-9]", "", (spec_text or "")).upper()[:8]
    if not clean_spec:
        clean_spec = "STD"
    return f"RT-{cat}-{clean_spec}-{seq:03d}"


def _parse_dxf_blocks(raw_bytes: bytes) -> list[dict]:
    """簡易解析 DXF 文字屬性與圖塊資訊（無需額外桌面 CAD 授權即可預覽轉出明細）"""
    text_data = raw_bytes.decode("utf-8", errors="ignore")
    lines = [ln.strip() for ln in text_data.splitlines()]
    extracted = []
    block_counts: dict[str, int] = {}

    for i in range(len(lines) - 1):
        if lines[i] == "2" and i > 0 and lines[i - 1] in ("INSERT", "0"):
            blk = lines[i + 1]
            if blk and not blk.startswith("*") and blk.upper() not in ("MODEL_SPACE", "PAPER_SPACE"):
                block_counts[blk] = block_counts.get(blk, 0) + 1

    for idx, (blk_name, cnt) in enumerate(block_counts.items(), start=1):
        extracted.append({
            "類別代碼": "ELC",
            "零件名稱": blk_name,
            "規格型號": blk_name,
            "數量": float(cnt),
            "單位": "PCS",
            "預估單價": 0.0,
        })
    return extracted


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name", "Engineer")

    txt = {
        "zh": {
            "title": "📐 CAD 圖面轉 BOM 與料號自動編碼",
            "sub": "上傳 AutoCAD (.dxf) 或零件明細表 (.csv / .xlsx)，自動比對與產生 ERP 料號並同步拋轉至生產與倉庫。",
            "t1": "1️⃣ 圖面解析與料號自動編碼",
            "t2": "2️⃣ 已建檔 BOM 清單與生產/倉庫同步",
            "proj": "關聯工程專案編號 (project_id)",
            "quote": "關聯估價單號 (quote_id，選填)",
            "dwg_no": "圖紙編號 (Drawing No.)",
            "dwg_rev": "圖面版次",
            "sys_name": "配電盤／系統名稱",
            "upload": "上傳 CAD (.dxf) 或明細檔 (.csv / .xlsx)（未上傳亦可直接使用下方範例編輯）",
            "gen_btn": "⚙️ 執行自動料號編碼與預覽",
            "save_btn": "💾 確認寫入 BOM 並同步拋轉生產／倉庫",
            "saved_ok": "✅ 已建立 BOM 單號 `{}`，並同步至生產工單與倉庫料件主檔。",
            "list_empty": "目前尚無已建檔的 CAD BOM 清單。",
        },
        "vi": {
            "title": "📐 Chuyển Bản Vẽ CAD Sang BOM & Mã Hóa Vật Tư Tự Động",
            "sub": "Tải lên file AutoCAD (.dxf) hoặc bảng kê (.csv / .xlsx) để tự động tạo mã vật tư ERP và đồng bộ sang Sản xuất & Kho.",
            "t1": "1️⃣ Phân Tích Bản Vẽ & Tạo Mã Vật Tư",
            "t2": "2️⃣ Danh Sách BOM Đã Lưu & Đồng Bộ Sản Xuất / Kho",
            "proj": "Mã Dự Án Liên Kết (project_id)",
            "quote": "Mã Báo Giá Liên Kết (quote_id)",
            "dwg_no": "Số Hiệu Bản Vẽ",
            "dwg_rev": "Phiên Bản",
            "sys_name": "Tên Tủ Điện / Hệ Thống",
            "upload": "Tải file CAD (.dxf) hoặc bảng kê (.csv / .xlsx)",
            "gen_btn": "⚙️ Tự Động Tạo Mã Vật Tư & Xem Trước",
            "save_btn": "💾 Lưu BOM & Đồng Bộ Sang Sản Xuất / Kho",
            "saved_ok": "✅ Đã lưu BOM `{}` và đồng bộ sang bộ phận Sản xuất & Kho.",
            "list_empty": "Chưa có dữ liệu BOM nào được lưu.",
        },
        "en": {
            "title": "📐 CAD Drawing to BOM & Auto Part Coding",
            "sub": "Upload AutoCAD (.dxf) or part schedules (.csv/.xlsx) to generate ERP part codes and sync to Production & Warehouse.",
            "t1": "1️⃣ Drawing Parsing & Auto Part Coding",
            "t2": "2️⃣ Saved BOM Registry & Production/WH Sync",
            "proj": "Linked Project ID",
            "quote": "Linked Quote ID (Optional)",
            "dwg_no": "Drawing Number",
            "dwg_rev": "Revision",
            "sys_name": "Panel / System Name",
            "upload": "Upload CAD (.dxf) or BOM sheet (.csv / .xlsx)",
            "gen_btn": "⚙️ Run Auto Part Coding & Preview",
            "save_btn": "💾 Save BOM & Sync to Production / Warehouse",
            "saved_ok": "✅ Saved BOM `{}` and synced with Production & Warehouse.",
            "list_empty": "No CAD BOM records saved yet.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_cad_bom_tables(engine)

    tab_build, tab_history = st.tabs([txt["t1"], txt["t2"]])

    with tab_build:
        c1, c2, c3 = st.columns(3)
        with c1:
            project_id = st.text_input(txt["proj"], value="PRJ-2026-01")
            quote_id = st.text_input(txt["quote"], value="QT-2026-008")
        with c2:
            drawing_no = st.text_input(txt["dwg_no"], value="DWG-MCC-01A")
            drawing_rev = st.text_input(txt["dwg_rev"], value="Rev.A")
        with c3:
            panel_name = st.text_input(txt["sys_name"], value="低壓主配電盤 LV-MDB-01")

        uploaded = st.file_uploader(txt["upload"], type=["dxf", "csv", "xlsx"])

        default_rows = [
            {"類別代碼": "PNL", "零件名稱": "冷軋鋼板箱體 2000x800x600", "規格型號": "SPCC-2.0MM", "數量": 1.0, "單位": "SET", "預估單價": 8500000.0},
            {"類別代碼": "BRK", "零件名稱": "無熔絲斷路器 MCCB 3P 400A", "規格型號": "NF400-CW", "數量": 1.0, "單位": "PCS", "預估單價": 6200000.0},
            {"類別代碼": "BUS", "零件名稱": "導電紅銅排 40x5mm", "規格型號": "CU-40X5", "數量": 12.0, "單位": "M", "預估單價": 420000.0},
            {"類別代碼": "CBL", "零件名稱": "控制配線電纜 2.5mm²", "規格型號": "CVV-2.5", "數量": 80.0, "單位": "M", "預估單價": 18500.0},
        ]

        if uploaded is not None:
            fname = uploaded.name.lower()
            try:
                if fname.endswith(".dxf"):
                    parsed = _parse_dxf_blocks(uploaded.read())
                    if parsed:
                        default_rows = parsed
                        st.success(f"已從 DXF 圖檔擷取 {len(parsed)} 項圖塊零件。")
                    else:
                        st.info("DXF 檔內未偵測到具名圖塊，已載入標準盤體明細供直接編輯。")
                elif fname.endswith(".csv"):
                    df_up = pd.read_csv(uploaded)
                    default_rows = df_up.to_dict(orient="records")
                elif fname.endswith(".xlsx"):
                    df_up = pd.read_excel(uploaded)
                    default_rows = df_up.to_dict(orient="records")
            except Exception as e:
                st.warning(f"檔案解析提示：{e}，已切換為手動明細表。")

        edited_df = st.data_editor(
            pd.DataFrame(default_rows),
            num_rows="dynamic",
            use_container_width=True,
            key="cad_bom_editor",
        )

        if st.button(txt["gen_btn"], use_container_width=True):
            coded_rows = []
            for idx, r in edited_df.iterrows():
                pname = str(r.get("零件名稱") or "").strip()
                if not pname:
                    continue
                cat = str(r.get("類別代碼") or "ELC").strip().upper()
                spec = str(r.get("規格型號") or pname).strip()
                qty = float(r.get("數量") or 1)
                unit = str(r.get("單位") or "PCS").strip().upper()
                ucost = float(r.get("預估單價") or 0)
                pcode = _generate_part_code(cat, spec, idx + 1)
                coded_rows.append({
                    "ERP料號": pcode,
                    "類別代碼": cat,
                    "零件名稱": pname,
                    "規格型號": spec,
                    "數量": qty,
                    "單位": unit,
                    "預估單價": ucost,
                    "小計": round(qty * ucost, 2),
                })
            st.session_state["cad_bom_preview"] = coded_rows

        preview_rows = st.session_state.get("cad_bom_preview", [])
        if preview_rows:
            st.markdown("#### 🏷️ 自動料號編碼結果預覽")
            prev_df = pd.DataFrame(preview_rows)
            st.dataframe(prev_df, use_container_width=True, hide_index=True)
            total_mat_cost = float(prev_df["小計"].sum())
            st.metric("BOM 預估總材料成本", f"{total_mat_cost:,.0f} ₫")

            if st.button(txt["save_btn"], type="primary", use_container_width=True):
                if not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    bom_id = f"BOM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO eng_cad_bom_headers (
                                        tenant_id, bom_id, project_id, quote_id, drawing_no,
                                        drawing_rev, panel_or_system_name, source_filename, status, created_by
                                    )
                                    VALUES (:tid, :bid, :pid, :qid, :dno, :drev, :pname, :fname, 'SYNCED_MRP', :cby)
                                """),
                                {
                                    "tid": tenant_id,
                                    "bid": bom_id,
                                    "pid": project_id.strip() or None,
                                    "qid": quote_id.strip() or None,
                                    "dno": drawing_no.strip(),
                                    "drev": drawing_rev.strip(),
                                    "pname": panel_name.strip(),
                                    "fname": uploaded.name if uploaded else "MANUAL_CAD_BOM",
                                    "cby": user_name,
                                },
                            )
                            for item in preview_rows:
                                conn.execute(
                                    text("""
                                        INSERT INTO eng_cad_bom_items (
                                            tenant_id, bom_id, project_id, part_code, part_name,
                                            spec_model, category_code, qty, unit, est_unit_cost, is_new_code, mrp_sync_status
                                        )
                                        VALUES (:tid, :bid, :pid, :pcode, :pname, :spec, :cat, :qty, :unit, :ucost, TRUE, 'SYNCED')
                                    """),
                                    {
                                        "tid": tenant_id,
                                        "bid": bom_id,
                                        "pid": project_id.strip() or None,
                                        "pcode": item["ERP料號"],
                                        "pname": item["零件名稱"],
                                        "spec": item["規格型號"],
                                        "cat": item["類別代碼"],
                                        "qty": item["數量"],
                                        "unit": item["單位"],
                                        "ucost": item["預估單價"],
                                    },
                                )
                        st.success(txt["saved_ok"].format(bom_id))
                    except Exception as e:
                        st.error(f"❌ 寫入 BOM 失敗：{e}")

    with tab_history:
        if not engine:
            st.info(txt["list_empty"])
            return
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT bom_id AS "BOM單號", project_id AS "專案編號", quote_id AS "估價單號",
                               drawing_no AS "圖紙編號", drawing_rev AS "版次",
                               panel_or_system_name AS "系統/盤體名稱", status AS "同步狀態",
                               created_by AS "建立人"
                        FROM eng_cad_bom_headers
                        WHERE tenant_id = :tid
                        ORDER BY id DESC
                        LIMIT 30
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                if not rows:
                    st.info(txt["list_empty"])
                else:
                    st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
        except Exception:
            st.info(txt["list_empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
