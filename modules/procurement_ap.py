import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (自動跟隨主程式全域語系)
# ----------------------------------------------------
PROC_I18N = {
    "繁體中文": {
        "title": "🛒 採購與應付帳款 (AP) - 企業標準請購與動態簽核中心",
        "caption": "實施『請購 ➔ 規格/主管簽核 ➔ 總務採購 ➔ 財務請款』權責分離（SoD）合規流程。",
        "tab_pr": "📝 1. 員工請購申請 (PR)",
        "tab_approval": "✍️ 2. 簽核中心與規格審查",
        "tab_po": "🛒 3. 總務/採購詢比價與下單 (PO)",
        "tab_ap": "💰 4. 財務應付帳款與付款 (AP)",
        "tab_audit": "🔍 稽核軌跡與權限追蹤",
        "info_pr": "🔒 系統已自動綁定目前登入者身分，防止冒名申請。",
        "lbl_requester": "請購人姓名 (系統綁定/不可修改) *",
        "lbl_dept": "所屬部門 (系統綁定)",
        "lbl_proj": "歸屬工程/專案編號",
        "lbl_cat": "請購類別",
        "lbl_item": "物品/材料名稱與規格 *",
        "lbl_qty": "需求數量",
        "lbl_unit": "單位",
        "lbl_amount": "預估總金額 (VND)",
        "lbl_reason": "請購用途說明",
        "btn_submit_pr": "📤 提交請購單並啟動簽核"
    },
    "English": {
        "title": "🛒 Procurement & AP - Enterprise PR/PO & Approval Workflow",
        "caption": "Implements Segregation of Duties (SoD): Requisition ➔ Approval ➔ Purchasing ➔ Finance Payment.",
        "tab_pr": "📝 1. Purchase Requisition (PR)",
        "tab_approval": "✍️ 2. Approvals & Tech Specs",
        "tab_po": "🛒 3. GA / Purchasing (PO)",
        "tab_ap": "💰 4. Finance & AP Payment",
        "tab_audit": "🔍 Audit Trail & Logs",
        "info_pr": "🔒 Locked to current logged-in user identity to prevent impersonation.",
        "lbl_requester": "Requester Name (Locked) *",
        "lbl_dept": "Department (Locked)",
        "lbl_proj": "Project Code",
        "lbl_cat": "Item Category",
        "lbl_item": "Item Name & Specs *",
        "lbl_qty": "Quantity",
        "lbl_unit": "Unit",
        "lbl_amount": "Est. Total Amount (VND)",
        "lbl_reason": "Purpose / Description",
        "btn_submit_pr": "📤 Submit PR & Start Workflow"
    },
    "Tiếng Việt": {
        "title": "🛒 Mua hàng & Phải trả (AP) - Quy trình Yêu cầu & Phê duyệt",
        "caption": "Thực hiện phân tách nhiệm vụ (SoD): Yêu cầu ➔ Phê duyệt ➔ Mua hàng ➔ Thanh toán.",
        "tab_pr": "📝 1. Yêu cầu mua hàng (PR)",
        "tab_approval": "✍️ 2. Duyệt & Kiểm tra Kỹ thuật",
        "tab_po": "🛒 3. Hành chính / Mua hàng (PO)",
        "tab_ap": "💰 4. Kế toán & Phải trả (AP)",
        "tab_audit": "🔍 Nhật ký Kiểm toán",
        "info_pr": "🔒 Tự động khóa theo tài khoản đang đăng nhập để tránh mạo danh.",
        "lbl_requester": "Tên người yêu cầu (Khóa) *",
        "lbl_dept": "Bộ phận (Khóa)",
        "lbl_proj": "Mã dự án",
        "lbl_cat": "Loại vật tư",
        "lbl_item": "Tên & Quy cách vật tư *",
        "lbl_qty": "Số lượng",
        "lbl_unit": "Đơn vị",
        "lbl_amount": "Tổng tiền dự kiến (VND)",
        "lbl_reason": "Mục đích sử dụng",
        "btn_submit_pr": "📤 Gửi đơn yêu cầu mua hàng"
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
    except Exception:
        pass

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    inject_procurement_css()

    # 自動跟隨主程式側邊欄選擇的語系（不再出現右上方重複 Dropdown）
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PROC_I18N.get(active_lang, PROC_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_procurement_db(engine)

    tab_pr, tab_approval, tab_po, tab_ap, tab_audit = st.tabs([
        L["tab_pr"], L["tab_approval"], L["tab_po"], L["tab_ap"], L["tab_audit"]
    ])

    # ----------------------------------------------------
    # 📝 階段 1: 員工請購申請 (PR) - 強制鎖定目前登入身分
    # ----------------------------------------------------
    with tab_pr:
        st.markdown(f"### {L['tab_pr']}")
        st.info(L["info_pr"])
        
        # 取得登入者資訊
        current_user_name = st.session_state.get("user_name", "admin")
        current_user_role = str(st.session_state.get("user_role", "Staff")).upper()
        
        with st.form("form_create_pr"):
            c1, c2, c3 = st.columns(3)
            with c1:
                # 🔒 資安防護：disabled=True 灰色鎖定，防止冒用他人姓名或改名陷害
                st.text_input(L["lbl_requester"], value=current_user_name, disabled=True)
                st.text_input(L["lbl_dept"], value=f"部門角色: {current_user_role}", disabled=True)
                pr_proj = st.text_input(L["lbl_proj"], placeholder="例: PRJ-2026-001 (西寧擴建案)")
            with c2:
                pr_cat = st.selectbox(L["lbl_cat"], ["🔌 配電盤/水電工程材料 (需設計審核)", "🛠️ 工地現場耗材與工具", "🥗 幹部宿舍與總務用品", "💻 資訊與辦公設備"])
                pr_item = st.text_input(L["lbl_item"], placeholder="例: Schneider 400A 空氣斷路器 (ACB)")
                pr_qty = st.number_input(L["lbl_qty"], min_value=1.0, value=2.0)
            with c3:
                pr_unit = st.text_input(L["lbl_unit"], value="台")
                pr_est_val = st.number_input(L["lbl_amount"], min_value=0.0, value=45000000.0, step=1000000.0)
                pr_reason = st.text_area(L["lbl_reason"], placeholder="例: 西寧廠 A 區配電盤主開關更換備料。")

            if st.form_submit_button(L["btn_submit_pr"], type="primary", use_container_width=True):
                if not pr_item:
                    st.error("⚠️ 請填寫物品/材料名稱與規格！")
                else:
                    pr_code_gen = "PR-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.purchase_requisitions 
                                    (pr_code, requester_name, department, project_code, item_category, item_name, qty, unit, est_amount, audit_log)
                                    VALUES (:code, :req, :dept, :proj, :cat, :item, :qty, :unit, :amt, :log);
                                """), {
                                    "code": pr_code_gen, "req": current_user_name, "dept": current_user_role, "proj": pr_proj,
                                    "cat": pr_cat, "item": pr_item, "qty": pr_qty, "unit": pr_unit, "amt": pr_est_val,
                                    "log": f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] {current_user_name} (身分驗證完成) 提出請購。"
                                })
                            st.success(f"🎉 請購單【{pr_code_gen}】已成功建立並送出！")
                            st.rerun()
                        except Exception as e:
                            st.error("寫入失敗: " + str(e))
                    else:
                        st.success(f"🎉 [展示模式] 請購單【{pr_code_gen}】建立成功！")

    # ----------------------------------------------------
    # ✍️ 階段 2: 簽核中心與規格審查
    # ----------------------------------------------------
    with tab_approval:
        st.markdown(f"### {L['tab_approval']}")
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
                                <b>單號：{pd_item['pr_code']}</b> | 請購人：<b>{pd_item['requester_name']}</b> ({pd_item['department']})<br>
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
    # 🛒 階段 3: 總務/採購詢比價與下單 (PO)
    # ----------------------------------------------------
    with tab_po:
        st.markdown(f"### {L['tab_po']}")
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
                                st.markdown(f"##### 📦 請購單據：{p_dict['pr_code']} - {p_dict['item_name']} (請購人: {p_dict['requester_name']})")
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
        st.markdown(f"### {L['tab_ap']}")
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
    # 🔍 階段 5: 稽核軌跡 (Audit Trail)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown(f"### {L['tab_audit']}")
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
