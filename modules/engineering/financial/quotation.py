# ==========================================
# 檔案路徑：modules/engineering/financial/quotation.py
# 職責：估價中心（工程專案估價、倉庫數量與成本連動、送交共用簽核中心）
# ==========================================

import streamlit as st
from sqlalchemy import text


def init_quotation_tables(engine):
    """建立估價主表與共用簽核佇列相容表（附降級防護）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS eng_quotations (
                    id SERIAL PRIMARY KEY,
                    quote_id VARCHAR(100) UNIQUE NOT NULL,
                    project_id VARCHAR(100),
                    project_name VARCHAR(255) NOT NULL,
                    client_name VARCHAR(255),
                    warehouse_id VARCHAR(100) DEFAULT 'WH-MAIN',
                    total_cost NUMERIC(15, 2) DEFAULT 0,
                    quoted_amount NUMERIC(15, 2) DEFAULT 0,
                    approved_amount NUMERIC(15, 2),
                    profit_margin NUMERIC(6, 2) DEFAULT 0,
                    status VARCHAR(60) DEFAULT '草稿',
                    approval_request_id VARCHAR(100),
                    pr_id VARCHAR(100),
                    po_id VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # 共用簽核中心佇列表（供請假、採購、文書、估價共用，若已存在則不覆蓋）
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_approval_requests (
                    id SERIAL PRIMARY KEY,
                    request_id VARCHAR(100) UNIQUE NOT NULL,
                    request_type VARCHAR(50) NOT NULL,
                    ref_id VARCHAR(100) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    amount NUMERIC(15, 2) DEFAULT 0,
                    approved_amount NUMERIC(15, 2),
                    applicant_role VARCHAR(100),
                    current_approver_role VARCHAR(100),
                    status VARCHAR(60) DEFAULT '待簽核',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass


def fetch_warehouse_materials(engine):
    """嘗試從倉庫資料表讀取數量與成本；若尚未建立或欄位不同，提供安全降級清單"""
    fallback_items = [
        {"material_id": "MAT-CU-01", "warehouse_id": "WH-MAIN", "name": "導電銅排 (99.9% 銅)", "stock_qty": 1200.0, "unit_cost": 150000.0},
        {"material_id": "MAT-MCCB-250", "warehouse_id": "WH-MAIN", "name": "無熔絲斷路器 MCCB 250A", "stock_qty": 45.0, "unit_cost": 2200000.0},
        {"material_id": "MAT-CAB-SS304", "warehouse_id": "WH-MAIN", "name": "不銹鋼配電箱體 (客製)", "stock_qty": 12.0, "unit_cost": 8500000.0},
        {"material_id": "MAT-CBL-10MM", "warehouse_id": "WH-MAIN", "name": "10mm2 控制電纜 (米)", "stock_qty": 5000.0, "unit_cost": 25000.0},
    ]
    if not engine:
        return fallback_items, True

    candidate_queries = [
        "SELECT material_code, material_name, qty, unit_cost FROM warehouse_inventory LIMIT 100",
        "SELECT sku, name, stock_qty, cost_price FROM inv_items LIMIT 100",
        "SELECT item_code, item_name, quantity, cost FROM inventory LIMIT 100",
    ]
    try:
        with engine.connect() as conn:
            for q in candidate_queries:
                try:
                    rows = conn.execute(text(q)).fetchall()
                    if rows:
                        parsed = []
                        for idx, r in enumerate(rows):
                            m = r._asdict() if hasattr(r, "_asdict") else {}
                            vals = list(r)
                            parsed.append({
                                "material_id": str(m.get("material_code") or m.get("sku") or m.get("item_code") or vals[0] or f"MAT-{idx+1}"),
                                "warehouse_id": "WH-MAIN",
                                "name": str(m.get("material_name") or m.get("name") or m.get("item_name") or vals[1] or "未命名物料"),
                                "stock_qty": float(m.get("qty") or m.get("stock_qty") or m.get("quantity") or vals[2] or 0),
                                "unit_cost": float(m.get("unit_cost") or m.get("cost_price") or m.get("cost") or vals[3] or 0),
                            })
                        if parsed:
                            return parsed, False
                except Exception:
                    continue
    except Exception:
        pass

    return fallback_items, True


def submit_to_shared_approval_center(engine, quote_id, project_id, project_name, quoted_amount, total_cost, applicant_role):
    """將估價單送入全公司共用簽核中心（與請假、採購、文書共用佇列）"""
    req_id = f"APR-{quote_id}"
    # 若為協理估價，預設下一關卡流向副總，再由副總／總經理於簽核中心核定金額
    next_role = "副總 / 總經理" if "協理" in applicant_role else "部門主管 / 副總"
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_approval_requests (
                request_id, request_type, ref_id, title, amount,
                applicant_role, current_approver_role, status
            )
            VALUES (
                :req_id, '工程估價', :ref_id, :title, :amt,
                :app_role, :next_role, '已送交簽核中心'
            )
            ON CONFLICT (request_id) DO UPDATE SET
                title = EXCLUDED.title,
                amount = EXCLUDED.amount,
                applicant_role = EXCLUDED.applicant_role,
                current_approver_role = EXCLUDED.current_approver_role,
                status = '已送交簽核中心'
        """), {
            "req_id": req_id,
            "ref_id": quote_id,
            "title": f"[{project_id or quote_id}] {project_name}（成本 {total_cost:,.0f} ₫）",
            "amt": quoted_amount,
            "app_role": applicant_role,
            "next_role": next_role,
        })
        conn.execute(text("""
            UPDATE eng_quotations
            SET status = '已送交簽核中心',
                approval_request_id = :req_id,
                updated_at = CURRENT_TIMESTAMP
            WHERE quote_id = :qid
        """), {"req_id": req_id, "qid": quote_id})
    return req_id


def render(engine=None, lang="zh", **kwargs):
    st.markdown("### 📐 估價中心")
    st.caption("連動倉庫可用數量與單位成本試算毛利；送審後自動進入全公司共用簽核中心（請假／採購／文書／估價統一簽核）。")

    if not engine:
        st.warning("⚠️ 尚未連線資料庫引擎，目前僅可檢視介面。")
        return

    init_quotation_tables(engine)
    materials, is_fallback = fetch_warehouse_materials(engine)
    if is_fallback:
        st.caption("💡 倉庫庫存表尚未偵測到自訂欄位，目前顯示預設倉庫成本參考資料（已預留倉庫欄位對接）。")

    tab_new, tab_list = st.tabs(["➕ 新增估價單", "📋 估價單列表與送簽"])

    with tab_new:
        with st.form("quotation_center_create_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                quote_id = st.text_input("估價單號 (quote_id)", placeholder="例如: QT-2026-001")
                project_id = st.text_input("專案編號 (project_id)", placeholder="例如: PRJ-TN-001")
            with c2:
                project_name = st.text_input("專案／案場名稱", placeholder="例如: 西寧廠高低壓配電盤工程")
                client_name = st.text_input("客戶名稱", placeholder="請輸入客戶名稱")
            with c3:
                applicant_role = st.selectbox("估價人員職級", ["工程主管", "協理", "專案經理"])
                quoted_amount = st.number_input("初估報價金額 (₫)", min_value=0.0, step=100000.0, value=100000000.0)

            st.markdown("#### 📦 倉庫數量與成本連動")
            total_cost = 0.0
            for item in materials:
                col_chk, col_qty, col_info = st.columns([3, 1.2, 2])
                with col_chk:
                    picked = st.checkbox(
                        f"{item['name']}（`{item['material_id']}`）",
                        key=f"q_pick_{item['material_id']}"
                    )
                with col_qty:
                    use_qty = st.number_input(
                        "使用數量",
                        min_value=0.0,
                        max_value=max(float(item["stock_qty"]), 999999.0),
                        step=1.0,
                        value=0.0,
                        key=f"q_qty_{item['material_id']}"
                    )
                with col_info:
                    line_cost = use_qty * float(item["unit_cost"]) if picked else 0.0
                    if picked:
                        total_cost += line_cost
                    shortage_tip = " ⚠️ 超出庫存" if (picked and use_qty > float(item["stock_qty"])) else ""
                    st.caption(
                        f"庫存: {item['stock_qty']:,.0f} | 成本: {item['unit_cost']:,.0f} ₫ | 小計: {line_cost:,.0f} ₫{shortage_tip}"
                    )

            est_profit = quoted_amount - total_cost
            est_margin = (est_profit / quoted_amount * 100) if quoted_amount > 0 else 0.0
            m1, m2, m3 = st.columns(3)
            m1.metric("倉庫物料成本合計", f"{total_cost:,.0f} ₫")
            m2.metric("預估毛利金額", f"{est_profit:,.0f} ₫")
            m3.metric("預估毛利率", f"{est_margin:.1f}%")

            submit_save = st.form_submit_button("💾 儲存估價單", type="primary", use_container_width=True)
            if submit_save:
                if not quote_id.strip() or not project_name.strip():
                    st.warning("⚠️ 請填寫「估價單號」與「專案／案場名稱」。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO eng_quotations (
                                    quote_id, project_id, project_name, client_name,
                                    total_cost, quoted_amount, profit_margin, status
                                )
                                VALUES (
                                    :qid, :pid, :pname, :cname,
                                    :cost, :qamt, :margin, '草稿'
                                )
                                ON CONFLICT (quote_id) DO UPDATE SET
                                    project_id = EXCLUDED.project_id,
                                    project_name = EXCLUDED.project_name,
                                    client_name = EXCLUDED.client_name,
                                    total_cost = EXCLUDED.total_cost,
                                    quoted_amount = EXCLUDED.quoted_amount,
                                    profit_margin = EXCLUDED.profit_margin,
                                    updated_at = CURRENT_TIMESTAMP
                            """), {
                                "qid": quote_id.strip(),
                                "pid": project_id.strip() or None,
                                "pname": project_name.strip(),
                                "cname": client_name.strip() or None,
                                "cost": total_cost,
                                "qamt": quoted_amount,
                                "margin": round(est_margin, 2),
                            })
                        st.success(f"✅ 已儲存估價單 `{quote_id.strip()}`。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存估價單失敗: {e}")

    with tab_list:
        st.markdown("#### 📋 估價單清單（可送交共用簽核中心）")
        role_for_submit = st.selectbox("送簽時填報職級", ["工程主管", "協理", "專案經理"], key="quote_submit_role")
        try:
            with engine.connect() as conn:
                rows = conn.execute(text("SELECT * FROM eng_quotations ORDER BY id DESC")).fetchall()
        except Exception as e:
            st.error(f"讀取估價單失敗: {e}")
            rows = []

        if not rows:
            st.info("目前尚無估價單，請先於「新增估價單」建立。")
        else:
            for r in rows:
                d = r._asdict()
                qid = d.get("quote_id")
                with st.container(border=True):
                    st.markdown(f"**`{qid}`｜{d.get('project_name')}**（專案: `{d.get('project_id') or '-'}`｜狀態: **{d.get('status')}**）")
                    st.caption(
                        f"倉庫成本: {float(d.get('total_cost') or 0):,.0f} ₫ | "
                        f"初估報價: {float(d.get('quoted_amount') or 0):,.0f} ₫ | "
                        f"核定金額: {f\"{float(d['approved_amount']):,.0f} ₫\" if d.get('approved_amount') is not None else '待簽核中心填寫/核定'} | "
                        f"毛利率: {float(d.get('profit_margin') or 0):.1f}%"
                    )
                    if d.get("status") in ["草稿", "退回修改"]:
                        if st.button("📨 送交共用簽核中心", key=f"send_apr_{qid}", type="primary"):
                            try:
                                req_id = submit_to_shared_approval_center(
                                    engine,
                                    quote_id=qid,
                                    project_id=d.get("project_id"),
                                    project_name=d.get("project_name"),
                                    quoted_amount=float(d.get("quoted_amount") or 0),
                                    total_cost=float(d.get("total_cost") or 0),
                                    applicant_role=role_for_submit,
                                )
                                st.success(f"✅ 已送交共用簽核中心（單號: `{req_id}`），請至簽核中心處理後續審核與金額核定。")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ 送簽失敗: {e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)


def main(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
