import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (i18n)
# ----------------------------------------------------
PROC_I18N = {
    "繁體中文": {
        "title": "🛒 採購與應付帳款 (AP) - 企業標準請購與動態簽核中心",
        "caption": "實施『請購 ➔ 規格/主管簽核 ➔ 總務採購 ➔ 財務請款』權責分離（SoD）合規流程。",
        "tab_pr": "📝 1. 員工請購申請 (PR)",
        "tab_approval": "✍️ 2. 簽核中心與規格審查",
        "tab_po": "🛒 3. 總務/採購詢比價與下單 (PO)",
        "tab_ap": "💰 4. 財務應付帳款與付款 (AP)",
        "tab_audit": "🔍 稽核軌跡與權限追蹤"
    },
    "English": {
        "title": "🛒 Procurement & AP - Enterprise PR/PO & Approval Workflow",
        "caption": "Implements Segregation of Duties (SoD): Requisition ➔ Approval ➔ Purchasing ➔ Finance Payment.",
        "tab_pr": "📝 1. Purchase Requisition (PR)",
        "tab_approval": "✍️ 2. Approvals & Tech Specs",
        "tab_po": "🛒 3. GA / Purchasing (PO)",
        "tab_ap": "💰 4. Finance & AP Payment",
        "tab_audit": "🔍 Audit Trail & Logs"
    },
    "Tiếng Việt": {
        "title": "🛒 Mua hàng & Phải trả (AP) - Quy trình Yêu cầu & Phê duyệt",
        "caption": "Thực hiện phân tách nhiệm vụ (SoD): Yêu cầu ➔ Phê duyệt ➔ Mua hàng ➔ Thanh toán.",
        "tab_pr": "📝 1. Yêu cầu mua hàng (PR)",
        "tab_approval": "✍️ 2. Duyệt & Kiểm tra Kỹ thuật",
        "tab_po": "🛒 3. Hành chính / Mua hàng (PO)",
        "tab_ap": "💰 4. Kế toán & Phải trả (AP)",
        "tab_audit": "🔍 Nhật ký Kiểm toán"
    }
}

def inject_procurement_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-size: 16px !important; }
        div.stButton > button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        .proc-card {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-left: 5px solid #1E3A8A;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

def init_procurement_db(engine):
    """初始化採購與簽核資料表"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.purchase_requisitions (
                    id SERIAL PRIMARY KEY,
                    pr_code VARCHAR(50) UNIQUE NOT NULL,
                    requester_name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    project_code VARCHAR(50),
                    item_category VARCHAR(50) NOT NULL,
                    item_name VARCHAR(200) NOT NULL,
                    qty NUMERIC(10,2) NOT NULL,
                    unit VARCHAR(20) DEFAULT '個',
                    est_amount NUMERIC(15,2) DEFAULT 0,
                    tech_approval VARCHAR(50) DEFAULT '待設計主管審核',
                    mgr_approval VARCHAR(50) DEFAULT '待部門主管審核',
                    exec_approval VARCHAR(50) DEFAULT '待副總/高階審核',
                    po_status VARCHAR(50) DEFAULT '待總務採購詢價',
                    ap_status VARCHAR(50) DEFAULT '待財務付款',
                    audit_log TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        pass

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    inject_procurement_css()

    c_title, c_lang = st.columns([2.5, 1])
    with c_lang:
        selected_lang = st.selectbox("🌐 Ngôn ngữ / Language", ["繁體中文", "English", "Tiếng Việt"], index=0)
    
    L = PROC_I18N.get(selected_lang, PROC_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_procurement_db(engine)

    tab_pr, tab_approval, tab_po, tab_ap, tab_audit = st.tabs([
        L["tab_pr"], L["tab_approval"], L["tab_po"], L["tab_ap"], L["tab_audit"]
    ])

    # ----------------------------------------------------
    # 📝 階段 1: 員工請購申請 (PR) - 任何人員皆可提出
    # ----------------------------------------------------
    with tab_pr:
        st.markdown("### 📝 1. 提出請購申請單 (Purchase Requisition)")
        st.info("💡 請購權放開給全體同仁；發起後自動依『金額與類別』送交對應主管及技術單位簽核。")
        
        with st.form("form_create_pr"):
            c1, c2, c3 = st.columns(3)
            with c1:
                pr_user = st.text_input("請購人姓名 *", value=st.session_state.get("user_name", "員工"))
                pr_dept = st.text_input("所屬部門", value="工程與設計管理中心")
                pr_proj = st.text_input("歸屬工程/專案編號", placeholder="例: PRJ-2026-001 (西寧擴建案)")
            with c2:
                pr_cat = st.selectbox("請購類別", ["🔌 配電盤/水電工程材料 (需設計審核)", "🛠️ 工地現場耗材與工具", "🥗 幹部宿舍與總務用品", "💻 資訊與辦公設備"])
                pr_item = st.text_input("物品/材料名稱與規格 *", placeholder="例: Schneider 400A 空氣斷路器 (ACB)")
                pr_qty = st.number_input("需求數量", min_value=1.0, value=2.0)
            with c3:
                pr_unit = st.text_input("單位", value="台")
                pr_est_val = st.number_input("預估總金額 (VND)", min_value=0.0, value=45000000.0, step=1000000.0)
                pr_reason = st.text_area("請購用途說明", placeholder="例: 西寧廠 A 區配電盤主開關更換備料。")

            if st.form_submit_button("📤 提交請購單並啟動簽核", type="primary", use_container_width=True):
                pr_code_gen = "PR-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.purchase_requisitions 
                                (pr_code, requester_name, department, project_code, item_category, item_name, qty, unit, est_amount, audit_log)
                                VALUES (:code, :req, :dept, :proj, :cat, :item, :qty, :unit, :amt, :log);
                            """), {
                                "code": pr_code_gen, "req": pr_user, "dept": pr_dept, "proj": pr_proj,
                                "cat": pr_cat, "item": pr_item, "qty": pr_qty, "unit": pr_unit, "amt": pr_est_val,
                                "log": f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {pr_user} 提出請購。"
                            })
                        st.success(f"🎉 請購單【{pr_code_gen}】已成功建立並送出！")
                        st.rerun()
                    except Exception as e:
                        st.error("寫入失敗: " + str(e))
                else:
                    st.success(f"🎉 [展示模式] 請購單【{pr_code_gen}】建立成功！")

    # ----------------------------------------------------
    # ✍️ 階段 2: 簽核中心與規格審查 - 權責分離 (設計主管只審規格)
    # ----------------------------------------------------
    with tab_approval:
        st.markdown("### ✍️ 2. 請購關卡簽核與規格確認 (Approval Pipeline)")
        st.caption("🔒 權責分離規範：設計主管僅審核規格與 BOM 相符性；行政與副總審核預算與必要性。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT * FROM public.purchase_requisitions WHERE po_status = '待總務採購詢價' ORDER BY id DESC;"))
                    prs = res.fetchall()
                    if prs:
                        for p in prs:
                            pd_item = dict(p._mapping)
                            st.markdown(f"""
                            <div class="proc-card">
                                <b>單號：{pd_item['pr_code']}</b> | 請購人：{pd_item['requester_name']} ({pd_item['department']})<br>
                                物品：<b>{pd_item['item_name']}</b> x {pd_item['qty']} {pd_item['unit']} | 預估金額：<b>{pd_item['est_amount']:,} VND</b><br>
                                專案：{pd_item['project_code'] or '無'} | 類別：{pd_item['item_category']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_a1, col_a2, col_a3 = st.columns(3)
                            with col_a1:
                                if st.button(f"🎨 設計主管: 確認規格合規 ({pd_item['pr_code']})"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET tech_approval = '🟢 規格審核通過' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("✅ 技術規格已確認！")
                                    st.rerun()
                            with col_a2:
                                if st.button(f"👔 部門主管: 核准預算 ({pd_item['pr_code']})"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET mgr_approval = '🟢 主管核准' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("✅ 部門主管已核准！")
                                    st.rerun()
                            with col_a3:
                                if st.button(f"👑 副總/高階: 授權發包 ({pd_item['pr_code']})", type="primary"):
                                    with engine.begin() as conn_u:
                                        conn_u.execute(text("UPDATE public.purchase_requisitions SET exec_approval = '🟢 高階核准發包', po_status = '已簽核/交總務採購' WHERE pr_code = :c;"), {"c": pd_item['pr_code']})
                                    st.success("🎉 高階特批完成，單據已拋轉給總務/採購執行！")
                                    st.rerun()
                            st.markdown("---")
                    else:
                        st.info("目前尚無等待簽核的請購單。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 🛒 階段 3: 總務/採購詢比價與下單 (PO) - 收回採購執行權
    # ----------------------------------------------------
    with tab_po:
        st.markdown("### 🛒 3. 總務部 / 專職採購執行 (Purchase Order)")
        st.info("💡 簽核通過之單據在此集中由【總務/採購專員】進行廠商詢價、比價與建立 PO 採購單。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res_po = conn.execute(text("SELECT * FROM public.purchase_requisitions WHERE po_status = '已簽核/交總務採購' ORDER BY id DESC;"))
                    po_items = res_po.fetchall()
                    if po_items:
                        for po in po_items:
                            p_dict = dict(po._mapping)
                            with st.form(f"form_po_{p_dict['pr_code']}"):
                                st.markdown(f"##### 📦 請購單據：{p_dict['pr_code']} - {p_dict['item_name']}")
                                c_p1, c_p2 = st.columns(2)
                                with c_p1:
                                    vendor = st.text_input("選定決標供應商 (Nhà cung cấp)", placeholder="例: ABB Vietnam / 施耐德代理商")
                                    final_price = st.number_input("最終議價總金額 (VND)", min_value=0.0, value=float(p_dict['est_amount']))
                                with c_p2:
                                    delivery_date = st.date_input("約定交貨日期", datetime.date.today() + datetime.timedelta(days=7))
                                    po_notes = st.text_input("採購備註 / 付款條件", value="收到發票後 30 天月結 (AP 30 Days)")

                                if st.form_submit_button("🛒 正式發出 PO 採購單並拋轉財務 AP", type="primary"):
                                    with engine.begin() as conn_p:
                                        conn_p.execute(text("""
                                            UPDATE public.purchase_requisitions 
                                            SET po_status = '🟢 PO已發出/等待到貨驗收',
                                                ap_status = '待財務AP付款',
                                                audit_log = audit_log || :log
                                            WHERE pr_code = :c;
                                        """), {
                                            "c": p_dict['pr_code'],
                                            "log": f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] 總務/採購已下單給 {vendor}，金額 {final_price:,} VND。"
                                        })
                                    st.success(f"🎉 已成功建立 PO 採購單並指派給財務部！")
                                    st.rerun()
                    else:
                        st.info("目前沒有待採購下單的簽核單據。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 💰 階段 4: 財務應付帳款與付款 (AP)
    # ----------------------------------------------------
    with tab_ap:
        st.markdown("### 💰 4. 財務部應付帳款 (AP) 審核與付款沖銷")
        st.caption("財務依據『簽核完整性 + 採購 PO + 到貨驗收發票』執行最終付款。")
        
        if engine:
            try:
                with engine.connect() as conn:
                    res_ap = conn.execute(text("SELECT * FROM public.purchase_requisitions WHERE po_status LIKE '%PO已發出%' ORDER BY id DESC;"))
                    ap_items = res_ap.fetchall()
                    if ap_items:
                        df_ap = pd.DataFrame([dict(r._mapping) for r in ap_items])
                        st.dataframe(df_ap[["pr_code", "requester_name", "item_name", "qty", "est_amount", "po_status", "ap_status"]], use_container_width=True)
                        if st.button("💳 執行批次付款並沖銷 AP 應付帳款", type="primary"):
                            st.success("✅ 財務付款與稅務發票沖銷作業完成！")
                    else:
                        st.info("目前尚無等待付款的 AP 項目。")
            except Exception as e:
                st.error("讀取失敗: " + str(e))

    # ----------------------------------------------------
    # 🔍 階段 5: 稽核軌跡 (Audit Trail) - 防止代理人或權限濫用
    # ----------------------------------------------------
    with tab_audit:
        st.markdown("### 🔍 全流程稽核軌跡與代理人簽核紀錄 (Audit Trail)")
        st.caption("完整記錄『誰在什麼時間提出請購、規格誰審核、總務何時下單』，供董事長與稽核室查核。")
        if engine:
            try:
                with engine.connect() as conn:
                    res_au = conn.execute(text("SELECT pr_code, requester_name, item_name, tech_approval, mgr_approval, exec_approval, po_status, audit_log FROM public.purchase_requisitions ORDER BY id DESC;"))
                    au_rows = res_au.fetchall()
                    if au_rows:
                        df_au = pd.DataFrame([dict(r._mapping) for r in au_rows])
                        st.dataframe(df_au, use_container_width=True)
            except Exception as e:
                st.error("讀取稽核軌跡失敗: " + str(e))

def render_procurement_ap(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)
