# ==========================================
# 檔案路徑：modules/engineering/financial/quotation.py
# 職責：估價中心（支援越南千分位點號顯示、明確新增明細列提示與歷史報價查詢）
# ==========================================

from datetime import datetime
import re
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def format_vn_number(val: float | int | str, decimals: int = 0) -> str:
    """將數字格式化為越南千分號習慣（例如 185.000.000 或 1.250,50）"""
    num = parse_vn_number(val)
    if decimals > 0:
        us_str = f"{num:,.{decimals}f}"
        return us_str.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{round(num):,}".replace(",", ".")


def parse_vn_number(val) -> float:
    """將帶有越南千分點（185.000.000）或逗號（185,000,000）的字串還原為浮點數"""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return 0.0 if pd.isna(val) else float(val)
    s = str(val).strip()
    if not s:
        return 0.0
    # 同時包含點與逗號時（如 1.250,50），點為千分位、逗號為小數點
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        parts = s.split(".")
        # 若為千分位格式（如 185.000.000 或 450.000），移除全部點號
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            s = s.replace(".", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
    s = re.sub(r"[^0-9.\-]", "", s)
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def _ensure_quotation_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_quotations (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        quote_id VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        client_name VARCHAR(200) NOT NULL,
                        client_tier VARCHAR(64) DEFAULT '一般客戶',
                        currency_code VARCHAR(16) DEFAULT 'VND',
                        subtotal_amount NUMERIC(18, 2) DEFAULT 0,
                        tax_rate NUMERIC(6, 2) DEFAULT 8,
                        total_amount NUMERIC(18, 2) DEFAULT 0,
                        status VARCHAR(32) DEFAULT 'DRAFT',
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_quotation_items (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        quote_id VARCHAR(64) NOT NULL,
                        item_name VARCHAR(200) NOT NULL,
                        spec_desc VARCHAR(255),
                        qty NUMERIC(14, 3) DEFAULT 1,
                        unit VARCHAR(32) DEFAULT '式',
                        unit_price NUMERIC(18, 2) DEFAULT 0,
                        line_total NUMERIC(18, 2) DEFAULT 0
                    );
                """)
            )
    except Exception:
        pass


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name", "Estimator")

    txt = {
        "zh": {
            "title": "📐 估價中心",
            "sub": "建立工程與配電盤報價單、自動核算稅額與總價（金額採用越南千分號 . 顯示）。",
            "t1": "1️⃣ 新增／試算報價單",
            "t2": "2️⃣ 歷史報價紀錄",
            "qid": "報價單號 (quote_id)",
            "pid": "關聯專案編號（系統帶出）",
            "client": "客戶名稱",
            "tier": "客戶分級",
            "curr": "幣別",
            "tax": "稅率 (%)",
            "hint": "💡 操作提示：點擊下方明細表最末列空白處（或按右側「➕ 新增項目列」）即可新增品項；單價支援直接輸入或越南千分號（例如：185.000.000）。",
            "add_row": "➕ 新增項目列",
            "save": "💾 儲存報價單",
            "saved": "✅ 已儲存報價單 `{}`（含稅總計：`{}`）。",
            "empty": "目前尚無報價單紀錄。",
        },
        "vi": {
            "title": "📐 Trung Tâm Báo Giá",
            "sub": "Lập báo giá công trình và tủ điện, tự động tính thuế và tổng tiền (hiển thị dấu chấm phân cách hàng nghìn).",
            "t1": "1️⃣ Tạo & Tính Báo Giá",
            "t2": "2️⃣ Lịch Sử Báo Giá",
            "qid": "Mã Báo Giá (quote_id)",
            "pid": "Mã Dự Án Liên Kết (Hệ thống cấp)",
            "client": "Tên Khách Hàng",
            "tier": "Phân Loại Khách",
            "curr": "Loại Tiền",
            "tax": "Thuế Suất (%)",
            "hint": "💡 Hướng dẫn: Nhấn vào dòng trống cuối bảng (hoặc bấm nút '➕ Thêm Dòng Hạng Mục') để thêm hạng mục mới; đơn giá hỗ trợ dấu chấm hàng nghìn (vd: 185.000.000).",
            "add_row": "➕ Thêm Dòng Hạng Mục",
            "save": "💾 Lưu Báo Giá",
            "saved": "✅ Đã lưu báo giá `{}` (Tổng cộng: `{}`).",
            "empty": "Chưa có dữ liệu báo giá.",
        },
        "en": {
            "title": "📐 Quotation Center",
            "sub": "Create project and panel quotations with thousand-dot formatting and automatic tax calculation.",
            "t1": "1️⃣ Create & Calculate Quote",
            "t2": "2️⃣ Quotation History",
            "qid": "Quote ID",
            "pid": "Linked Project ID (System)",
            "client": "Client Name",
            "tier": "Client Tier",
            "curr": "Currency",
            "tax": "Tax Rate (%)",
            "hint": "💡 Tip: Click the bottom blank row of the table (or click '➕ Add Line Item') to add items; unit prices support thousand dots (e.g. 185.000.000).",
            "add_row": "➕ Add Line Item",
            "save": "💾 Save Quotation",
            "saved": "✅ Saved quotation `{}` (Total: `{}`).",
            "empty": "No quotation records yet.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_quotation_tables(engine)

    tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])

    with tab1:
        if "quote_default_stamp" not in st.session_state:
            st.session_state["quote_default_stamp"] = datetime.now().strftime("%Y%m%d-%H%M")
        stamp = st.session_state["quote_default_stamp"]

        c1, c2, c3 = st.columns(3)
        with c1:
            quote_id = st.text_input(txt["qid"], value=f"QT-{stamp}")
            project_id = st.text_input(txt["pid"], value=f"PRJ-{stamp}", disabled=True)
        with c2:
            client_name = st.text_input(txt["client"], value="西寧工業區客戶")
            client_tier = st.selectbox(txt["tier"], ["長期配合建商", "同行調貨", "一般散客"])
        with c3:
            currency_code = st.selectbox(txt["curr"], ["VND", "USD", "TWD"])
            tax_rate = st.number_input(txt["tax"], min_value=0.0, max_value=30.0, value=8.0, step=1.0)

        if "quote_rows_seed" not in st.session_state:
            st.session_state["quote_rows_seed"] = [
                {
                    "項目名稱": "低壓配電盤 LV-MDB-01",
                    "規格說明": "380V/220V 2000A 室內型",
                    "數量": 1.0,
                    "單位": "台",
                    "單價": format_vn_number(185000000),
                },
                {
                    "項目名稱": "主幹電力電纜敷設",
                    "規格說明": "CV 3x150mm² 含PVC管與支架",
                    "數量": 120.0,
                    "單位": "公尺",
                    "單價": format_vn_number(450000),
                },
                {
                    "項目名稱": "現場安裝與送電測試",
                    "規格說明": "含絕緣與耐壓測試報告",
                    "數量": 1.0,
                    "單位": "式",
                    "單價": format_vn_number(25000000),
                },
            ]

        c_hint, c_add = st.columns([4.5, 1.5])
        with c_hint:
            st.info(txt["hint"])
        with c_add:
            st.write("")
            if st.button(txt["add_row"], use_container_width=True):
                st.session_state["quote_rows_seed"].append(
                    {
                        "項目名稱": "",
                        "規格說明": "",
                        "數量": 1.0,
                        "單位": "式",
                        "單價": "0",
                    }
                )
                st.rerun()

        edited = st.data_editor(
            pd.DataFrame(st.session_state["quote_rows_seed"]),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "項目名稱": st.column_config.TextColumn(
                    "項目名稱（點擊下方空白列新增）",
                    help="請輸入工程項目或設備名稱，可直接點表格最下方空白列新增品項",
                    width="medium",
                ),
                "規格說明": st.column_config.TextColumn("規格說明", width="medium"),
                "數量": st.column_config.NumberColumn("數量", min_value=0.0, step=1.0, format="%.2f"),
                "單位": st.column_config.TextColumn("單位", width="small"),
                "單價": st.column_config.TextColumn(
                    "單價（越南千分號 . ）",
                    help="支援輸入如 185.000.000 或純數字",
                    width="medium",
                ),
            },
            key="quote_items_editor",
        )

        subtotal = 0.0
        clean_lines = []
        for _, row in edited.iterrows():
            iname = str(row.get("項目名稱") or "").strip()
            if not iname:
                continue
            qty = float(row.get("數量") or 0)
            uprice = parse_vn_number(row.get("單價"))
            ltotal = round(qty * uprice, 2)
            subtotal += ltotal
            clean_lines.append({
                "item_name": iname,
                "spec_desc": str(row.get("規格說明") or "").strip(),
                "qty": qty,
                "unit": str(row.get("單位") or "式").strip(),
                "unit_price": uprice,
                "line_total": ltotal,
            })

        tax_amt = round(subtotal * (float(tax_rate) / 100.0), 2)
        grand_total = round(subtotal + tax_amt, 2)

        m1, m2, m3 = st.columns(3)
        m1.metric("未稅小計", f"{format_vn_number(subtotal)} {currency_code}")
        m2.metric("稅額", f"{format_vn_number(tax_amt)} {currency_code}")
        m3.metric("含稅總價", f"{format_vn_number(grand_total)} {currency_code}")

        if st.button(txt["save"], type="primary", use_container_width=True):
            if not quote_id.strip() or not client_name.strip():
                st.warning("⚠️ 請填寫報價單號與客戶名稱。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_quotations (
                                    tenant_id, quote_id, project_id, client_name, client_tier,
                                    currency_code, subtotal_amount, tax_rate, total_amount,
                                    status, created_by
                                )
                                VALUES (
                                    :tid, :qid, :pid, :cname, :ctier,
                                    :curr, :sub, :trate, :tot,
                                    'SUBMITTED', :cby
                                )
                                ON CONFLICT (quote_id) DO UPDATE SET
                                    project_id = EXCLUDED.project_id,
                                    client_name = EXCLUDED.client_name,
                                    client_tier = EXCLUDED.client_tier,
                                    currency_code = EXCLUDED.currency_code,
                                    subtotal_amount = EXCLUDED.subtotal_amount,
                                    tax_rate = EXCLUDED.tax_rate,
                                    total_amount = EXCLUDED.total_amount
                            """),
                            {
                                "tid": tenant_id,
                                "qid": quote_id.strip(),
                                "pid": project_id.strip() or f"PRJ-{stamp}",
                                "cname": client_name.strip(),
                                "ctier": client_tier,
                                "curr": currency_code,
                                "sub": subtotal,
                                "trate": float(tax_rate),
                                "tot": grand_total,
                                "cby": user_name,
                            },
                        )
                        conn.execute(
                            text("DELETE FROM eng_quotation_items WHERE tenant_id = :tid AND quote_id = :qid"),
                            {"tid": tenant_id, "qid": quote_id.strip()},
                        )
                        for ln in clean_lines:
                            conn.execute(
                                text("""
                                    INSERT INTO eng_quotation_items (
                                        tenant_id, quote_id, item_name, spec_desc,
                                        qty, unit, unit_price, line_total
                                    )
                                    VALUES (
                                        :tid, :qid, :iname, :spec,
                                        :qty, :unit, :uprice, :ltot
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "qid": quote_id.strip(),
                                    "iname": ln["item_name"],
                                    "spec": ln["spec_desc"],
                                    "qty": ln["qty"],
                                    "unit": ln["unit"],
                                    "uprice": ln["unit_price"],
                                    "ltot": ln["line_total"],
                                },
                            )
                    st.success(txt["saved"].format(quote_id.strip(), f"{format_vn_number(grand_total)} {currency_code}"))
                except Exception as e:
                    st.error(f"❌ 儲存報價單失敗：{e}")

    with tab2:
        if not engine:
            st.info(txt["empty"])
            return
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT quote_id, project_id, client_name, client_tier,
                               currency_code, subtotal_amount, total_amount, status, created_by
                        FROM eng_quotations
                        WHERE tenant_id = :tid
                        ORDER BY id DESC
                        LIMIT 40
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                if not rows:
                    st.info(txt["empty"])
                else:
                    hist_list = []
                    for r in rows:
                        d = r._asdict()
                        hist_list.append({
                            "報價單號": d["quote_id"],
                            "專案編號": d["project_id"],
                            "客戶名稱": d["client_name"],
                            "客戶分級": d["client_tier"],
                            "幣別": d["currency_code"],
                            "未稅小計": format_vn_number(d["subtotal_amount"]),
                            "含稅總價": format_vn_number(d["total_amount"]),
                            "狀態": d["status"],
                            "建立人": d["created_by"],
                        })
                    st.dataframe(pd.DataFrame(hist_list), use_container_width=True, hide_index=True)
        except Exception:
            st.info(txt["empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
