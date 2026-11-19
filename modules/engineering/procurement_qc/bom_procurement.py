# ==========================================
# 檔案路徑：modules/engineering/procurement_qc/bom_procurement.py
# 職責：工程 BOM 算料與採購需求（介面聚焦業務填報，庫存比對由後台靜默處理）
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_bom_proc_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_bom_procurement_items (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        quote_id VARCHAR(80),
                        project_id VARCHAR(80),
                        part_code VARCHAR(80) NOT NULL,
                        part_name VARCHAR(200) NOT NULL,
                        required_qty NUMERIC(14, 3) DEFAULT 1,
                        unit VARCHAR(32) DEFAULT 'PCS',
                        pr_status VARCHAR(32) DEFAULT 'PENDING_PR',
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _lookup_silent_stock(engine, tenant_id: str, part_code: str) -> float:
    """後台靜默查詢可用庫存量（不在前端干擾操作人員）"""
    if not engine or not part_code:
        return 0.0
    for sql in [
        "SELECT COALESCE(SUM(available_qty), 0) FROM wh_inventory_balances WHERE tenant_id = :tid AND part_code = :pc",
        "SELECT COALESCE(SUM(stock_qty), 0) FROM inventory_items WHERE item_code = :pc",
    ]:
        try:
            with engine.connect() as conn:
                val = conn.execute(text(sql), {"tid": tenant_id, "pc": part_code}).scalar()
                if val is not None:
                    return float(val)
        except Exception:
            continue
    return 0.0


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name", "Engineer")

    txt = {
        "zh": {
            "title": "📦 工程 BOM 算料與採購需求",
            "sub": "建立或調整工程專案 BOM 用料明細，系統自動核算缺料並產生採購請購需求。",
            "t1": "📋 專案 BOM 需求明細",
            "t2": "🛒 採購請購清單",
            "t3": "➕ 新增／調整 BOM 物料需求",
            "add_hdr": "➕ 手動新增或調整專案 BOM 物料需求",
            "q_id": "專案報價／案場編號",
            "p_code": "材料料號",
            "p_name": "材料名稱與規格",
            "unit": "單位 (Unit)",
            "qty": "需求數量（支援小數，如 2.5）",
            "save": "💾 儲存並加入 BOM 需求清單",
            "saved": "✅ 已儲存【{}】至 BOM 需求清單。",
            "empty": "目前尚無 BOM 物料需求紀錄。",
            "gen_pr": "📤 依缺料自動產生採購請購單",
            "pr_ok": "✅ 已依淨需求產生採購請購單，送交採購／簽核流程。",
        },
        "vi": {
            "title": "📦 Tính Toán Vật Tư BOM & Yêu Cầu Mua Hàng",
            "sub": "Lập và điều chỉnh định mức vật tư BOM cho dự án, hệ thống tự động tổng hợp nhu cầu mua hàng.",
            "t1": "📋 Danh Mục Nhu Cầu BOM",
            "t2": "🛒 Danh Sách Đề Nghị Mua Hàng",
            "t3": "➕ Thêm / Điều Chỉnh Vật Tư BOM",
            "add_hdr": "➕ Thêm Hoặc Điều Chỉnh Nhu Cầu Vật Tư BOM",
            "q_id": "Mã Báo Giá / Dự Án",
            "p_code": "Mã Vật Tư",
            "p_name": "Tên & Quy Cách Vật Tư",
            "unit": "Đơn Vị Tính",
            "qty": "Số Lượng Yêu Cầu (hỗ trợ số lẻ, vd: 2.5)",
            "save": "💾 Lưu Vào Danh Sách BOM",
            "saved": "✅ Đã lưu [{}] vào danh sách nhu cầu BOM.",
            "empty": "Chưa có dữ liệu nhu cầu vật tư BOM.",
            "gen_pr": "📤 Tạo Đề Nghị Mua Hàng Tự Động",
            "pr_ok": "✅ Đã tạo đề nghị mua hàng theo nhu cầu thực tế.",
        },
        "en": {
            "title": "📦 Engineering BOM & Procurement Requisition",
            "sub": "Manage project BOM material requirements and automatically generate purchase requisitions.",
            "t1": "📋 Project BOM Requirements",
            "t2": "🛒 Purchase Requisition List",
            "t3": "➕ Add / Adjust BOM Item",
            "add_hdr": "➕ Add or Adjust Project BOM Material Requirement",
            "q_id": "Quote / Project ID",
            "p_code": "Part Code",
            "p_name": "Material Name & Specification",
            "unit": "Unit",
            "qty": "Required Quantity (decimals supported, e.g. 2.5)",
            "save": "💾 Save to BOM Requirement List",
            "saved": "✅ Saved [{}] to BOM requirement list.",
            "empty": "No BOM requirement records yet.",
            "gen_pr": "📤 Generate Purchase Requisition",
            "pr_ok": "✅ Purchase requisition generated from net requirements.",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    _ensure_bom_proc_tables(engine)

    tab1, tab2, tab3 = st.tabs([txt["t1"], txt["t2"], txt["t3"]])

    with tab3:
        st.markdown(f"#### {txt['add_hdr']}")
        with st.form("form_bom_req_add"):
            c1, c2, c3 = st.columns(3)
            with c1:
                quote_id = st.text_input(txt["q_id"], value="QT-2026-002")
                part_code = st.text_input(txt["p_code"], value="PART-CBL-04")
            with c2:
                part_name = st.text_input(txt["p_name"], value="XLPE 電力電纜 4x16mm²")
                unit = st.selectbox(
                    txt["unit"],
                    ["捲 (Cuộn)", "個 (Cái)", "公尺 (Mét)", "式 (Bộ)", "箱 (Thùng)", "支 (Cây)"],
                )
            with c3:
                req_qty = st.number_input(txt["qty"], min_value=0.01, value=2.50, step=0.50, format="%.2f")

            if st.form_submit_button(txt["save"], type="primary", use_container_width=True):
                if not part_code.strip() or not part_name.strip():
                    st.warning("⚠️ 請填寫材料料號與名稱規格。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO eng_bom_procurement_items (
                                        tenant_id, quote_id, project_id, part_code, part_name,
                                        required_qty, unit, pr_status, created_by
                                    )
                                    VALUES (:tid, :qid, :pid, :pc, :pn, :qty, :u, 'READY_FOR_PR', :cby)
                                """),
                                {
                                    "tid": tenant_id,
                                    "qid": quote_id.strip() or None,
                                    "pid": quote_id.strip() or None,
                                    "pc": part_code.strip().upper(),
                                    "pn": part_name.strip(),
                                    "qty": float(req_qty),
                                    "u": unit,
                                    "cby": user_name,
                                },
                            )
                        st.success(txt["saved"].format(part_name.strip()))
                    except Exception as e:
                        st.error(f"❌ 儲存失敗：{e}")

    with tab1:
        if not engine:
            st.info(txt["empty"])
        else:
            try:
                with engine.connect() as conn:
                    rows = conn.execute(
                        text("""
                            SELECT quote_id AS "案場/報價單號", part_code AS "材料料號",
                                   part_name AS "材料名稱與規格", required_qty AS "需求數量",
                                   unit AS "單位", pr_status AS "狀態"
                            FROM eng_bom_procurement_items
                            WHERE tenant_id = :tid
                            ORDER BY id DESC
                            LIMIT 50
                        """),
                        {"tid": tenant_id},
                    ).fetchall()
                if not rows:
                    st.info(txt["empty"])
                else:
                    st.dataframe(pd.DataFrame([r._asdict() for r in rows]), use_container_width=True, hide_index=True)
                    if st.button(txt["gen_pr"], type="primary", use_container_width=True):
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    UPDATE eng_bom_procurement_items
                                    SET pr_status = 'PR_SUBMITTED'
                                    WHERE tenant_id = :tid AND pr_status = 'READY_FOR_PR'
                                """),
                                {"tid": tenant_id},
                            )
                        st.success(txt["pr_ok"])
                        st.rerun()
            except Exception:
                st.info(txt["empty"])

    with tab2:
        if not engine:
            st.info(txt["empty"])
        else:
            try:
                with engine.connect() as conn:
                    rows = conn.execute(
                        text("""
                            SELECT id, quote_id, part_code, part_name, required_qty, unit, pr_status
                            FROM eng_bom_procurement_items
                            WHERE tenant_id = :tid AND pr_status = 'PR_SUBMITTED'
                            ORDER BY id DESC
                            LIMIT 50
                        """),
                        {"tid": tenant_id},
                    ).fetchall()
                if not rows:
                    st.info("目前尚無已送出的採購請購項目。")
                else:
                    display_list = []
                    for r in rows:
                        d = r._asdict()
                        # 後台靜默扣除可用量，直接算出建議請購數量
                        silent_avail = _lookup_silent_stock(engine, tenant_id, d["part_code"])
                        net_buy = max(float(d["required_qty"] or 0) - silent_avail, 0.0)
                        display_list.append({
                            "案場/報價單號": d["quote_id"],
                            "材料料號": d["part_code"],
                            "材料名稱與規格": d["part_name"],
                            "BOM需求量": d["required_qty"],
                            "建議請購量": net_buy if net_buy > 0 else d["required_qty"],
                            "單位": d["unit"],
                            "請購狀態": "已送出請購",
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True, hide_index=True)
            except Exception:
                st.info("目前尚無已送出的採購請購項目。")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
