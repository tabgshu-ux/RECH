# ==========================================
# 檔案路徑：modules/engineering/financial/quotation.py
# 職責：估價中心（工程／設備估價單建立、明細試算與歷史報價查詢）
# ==========================================

from datetime import datetime
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


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
            "sub": "建立工程與配電盤報價單、自動核算稅額與總價，並查詢歷史報價紀錄。",
            "t1": "1️⃣ 新增／試算報價單",
            "t2": "2️⃣ 歷史報價紀錄",
            "qid": "報價單號 (quote_id)",
            "pid": "關聯專案編號 (project_id)",
            "client": "客戶名稱",
            "tier": "客戶分級",
            "curr": "幣別",
            "tax": "稅率 (%)",
            "save": "💾 儲存報價單",
            "saved": "✅ 已儲存報價單 `{}`（含稅總計：`{}`）。",
            "empty": "目前尚無報價單紀錄。",
        },
        "vi": {
            "title": "📐 Trung Tâm Báo Giá",
            "sub": "Lập báo giá công trình và tủ điện, tự động tính thuế và tổng tiền, tra cứu lịch sử báo giá.",
            "t1": "1️⃣ Tạo & Tính Báo Giá",
            "t2": "2️⃣ Lịch Sử Báo Giá",
            "qid": "Mã Báo Giá (quote_id)",
            "pid": "Mã Dự Án (project_id)",
            "client": "Tên Khách Hàng",
            "tier": "Phân Loại Khách",
            "curr": "Loại Tiền",
            "tax": "Thuế Suất (%)",
            "save": "💾 Lưu Báo Giá",
            "saved": "✅ Đã lưu báo giá `{}` (Tổng cộng: `{}`).",
            "empty": "Chưa có dữ liệu báo giá.",
        },
        "en": {
            "title": "📐 Quotation Center",
            "sub": "Create project and panel quotations, calculate tax and totals, and review quotation history.",
            "t1": "1️⃣ Create & Calculate Quote",
            "t2": "2️⃣ Quotation History",
            "qid": "Quote ID",
            "pid": "Project ID",
            "client": "Client Name",
            "tier": "Client Tier",
            "curr": "Currency",
            "tax": "Tax Rate (%)",
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
        c1, c2, c3 = st.columns(3)
        with c1:
            default_qid = f"QT-{datetime.now().strftime('%Y%m%d-%H%M')}"
            quote_id = st.text_input(txt["qid"], value=default_qid)
            project_id = st.text_input(txt["pid"], value="PRJ-2026-01")
        with c2:
            client_name = st.text_input(txt["client"], value="西寧工業區客戶")
            client_tier = st.selectbox(txt["tier"], ["長期配合建商", "同行調貨", "一般散客"])
        with c3:
            currency_code = st.selectbox(txt["curr"], ["VND", "USD", "TWD"])
            tax_rate = st.number_input(txt["tax"], min_value=0.0, max_value=30.0, value=8.0, step=1.0)

        sample_items = [
            {"項目名稱": "低壓配電盤 LV-MDB-01", "規格說明": "380V/220V 2000A 室內型", "數量": 1.0, "單位": "台", "單價": 185000000.0},
            {"項目名稱": "主幹電力電纜敷設", "規格說明": "CV 3x150mm² 含PVC管與支架", "數量": 120.0, "單位": "公尺", "單價": 450000.0},
            {"項目名稱": "現場安裝與送電測試", "規格說明": "含絕緣與耐壓測試報告", "數量": 1.0, "單位": "式", "單價": 25000000.0},
        ]

        edited = st.data_editor(
            pd.DataFrame(sample_items),
            num_rows="dynamic",
            use_container_width=True,
            key="quote_items_editor",
        )

        subtotal = 0.0
        clean_lines = []
        for _, row in edited.iterrows():
            iname = str(row.get("項目名稱") or "").strip()
            if not iname:
                continue
            qty = float(row.get("數量") or 0)
            uprice = float(row.get("單價") or 0)
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
        m1.metric("未稅小計", f"{subtotal:,.0f} {currency_code}")
        m2.metric("稅額", f"{tax_amt:,.0f} {currency_code}")
        m3.metric("含稅總價", f"{grand_total:,.0f} {currency_code}")

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
                                "pid": project_id.strip() or None,
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
                    st.success(txt["saved"].format(quote_id.strip(), f"{grand_total:,.0f} {currency_code}"))
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
                        SELECT quote_id AS "報價單號", project_id AS "專案編號",
                               client_name AS "客戶名稱", client_tier AS "客戶分級",
                               currency_code AS "幣別", subtotal_amount AS "未稅小計",
                               total_amount AS "含稅總價", status AS "狀態",
                               created_by AS "建立人"
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
                    st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
        except Exception:
            st.info(txt["empty"])


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
