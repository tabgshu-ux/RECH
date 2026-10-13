import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 採購與應付帳款 (AP) 控管完整多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 管理部 - 採購與應付帳款 (AP) 預算控管中心",
        "caption": "自動連動工程部專案預算！採購請款金額超過報價預算時自動鎖定並觸發審核流程。",
        "tab_add": "📝 採購與應付請款登記 (預算即時對比)",
        "tab_audit": "⚖️ AP 帳款審核與沖銷付款",
        "tab_list": "📊 採購請款歷史紀錄與預算稽核看板",
        "lbl_po_id": "採購單號 (PO ID)",
        "lbl_project": "關聯工程專案 (連動工程部報價單)",
        "lbl_vendor": "供應商 / 外包商名稱",
        "lbl_currency": "幣別 (Currency)",
        "lbl_exchange_rate": "對越盾匯率 (VND Exchange Rate)",
        "lbl_amount": "本次請款金額 (VND)",
        "lbl_item_name": "資材/品項名稱",
        "lbl_item_spec": "規格與材質說明",
        "lbl_qty": "數量",
        "lbl_unit_price": "單價 (VND)",
        "btn_add_item": "➕ 新增採購品項至清單",
        "lbl_cart": "📋 本次採購請款明細清單：",
        "lbl_budget_info": "📊 專案預算監控：總預算 `{budget:,.0f} VND` | 已請款 `{spent:,.0f} VND` | 剩餘預算 `{rem:,.0f} VND`",
        "btn_submit": "🚀 提交採購請款單並進行預算稽核",
        "alert_over_budget": "⚠️ 警告：本次請款總金額高於專案剩餘預算！系統已自動鎖定並轉入【超預算總經理簽核】流程。",
        "msg_success": "✅ 採購請款單已成功寫入資料庫！狀態：`{status}`",
        "no_proj": "-- 無專案關聯 (一般行政採購) --",
        "btn_pay": "💳 付款沖銷",
        "btn_approve": "✅ 審核通過"
    },
    "Tiếng Việt": {
        "title": "🛒 Phòng Quản lý - Mua Hàng & Phải Trả (AP) Khống Chế Ngân Sách",
        "caption": "Tự động kết nối ngân sách dự án kỹ thuật! Cảnh báo và khóa phê duyệt khi vượt ngân sách báo giá.",
        "tab_add": "📝 Nhập Yêu Cầu Mua Hàng & Thanh Toán",
        "tab_audit": "⚖️ Duyệt AP & Phê Duyệt Thanh Toán",
        "tab_list": "📊 Lịch Sử Mua Hàng & Bảng Báo Cáo Ngân Sách",
        "lbl_po_id": "Mã đơn mua hàng (PO)",
        "lbl_project": "Dự án kỹ thuật liên quan (Báo giá)",
        "lbl_vendor": "Nhà cung cấp / Thầu phụ",
        "lbl_currency": "Loại tiền",
        "lbl_exchange_rate": "Tỷ giá quy đổi (VND)",
        "lbl_amount": "Số tiền đề nghị thanh toán (VND)",
        "lbl_item_name": "Tên vật tư / Hàng hóa",
        "lbl_item_spec": "Quy cách & Quy chuẩn",
        "lbl_qty": "Số lượng",
        "lbl_unit_price": "Đơn giá (VND)",
        "btn_add_item": "➕ Thêm món vào danh sách",
        "lbl_cart": "📋 Danh sách chi tiết vật tư đề nghị mua:",
        "lbl_budget_info": "📊 Giám sát ngân sách: Tổng `{budget:,.0f} VND` | Đã chi `{spent:,.0f} VND` | Còn lại `{rem:,.0f} VND`",
        "btn_submit": "🚀 Lưu Yêu Cầu Mua Hàng & Kiểm Soát Ngân Sách",
        "alert_over_budget": "⚠️ Cảnh báo: Số tiền thanh toán vượt quá ngân sách còn lại! Đã tự động chuyển trạng thái chờ duyệt.",
        "msg_success": "✅ Đã lưu yêu cầu mua hàng vào cơ sở dữ liệu! Trạng thái: `{status}`",
        "no_proj": "-- Không theo dự án (Chi phí hành chính) --",
        "btn_pay": "💳 Thanh toán",
        "btn_approve": "✅ Phê duyệt"
    },
    "English": {
        "title": "🛒 GA & Procurement - Accounts Payable (AP) Budget Control",
        "caption": "Auto-linked to Engineering Project Budgets! Automatically locks requests that exceed quoted budget caps.",
        "tab_add": "📝 Purchase & AP Request Entry",
        "tab_audit": "⚖️ AP Audit & Payment Settlement",
        "tab_list": "📊 AP History & Budget Audit Log",
        "lbl_po_id": "PO Number",
        "lbl_project": "Linked Engineering Project",
        "lbl_vendor": "Vendor / Subcontractor",
        "lbl_currency": "Currency",
        "lbl_exchange_rate": "Exchange Rate (VND)",
        "lbl_amount": "Requested Amount (VND)",
        "lbl_item_name": "Material / Item Name",
        "lbl_item_spec": "Specification & Material",
        "lbl_qty": "Quantity",
        "lbl_unit_price": "Unit Price (VND)",
        "btn_add_item": "➕ Add Item to List",
        "lbl_cart": "📋 Requisition Item Details:",
        "lbl_budget_info": "📊 Budget Monitor: Total `{budget:,.0f} VND` | Spent `{spent:,.0f} VND` | Remaining `{rem:,.0f} VND`",
        "btn_submit": "🚀 Submit AP Request & Audit",
        "alert_over_budget": "⚠️ Warning: Requested amount exceeds remaining project budget! Flagged for manager approval.",
        "msg_success": "✅ AP Request saved to database! Status: `{status}`",
        "no_proj": "-- General Administrative Procurement --",
        "btn_pay": "💳 Pay Settlement",
        "btn_approve": "✅ Approve"
    }
}

def init_procurement_ap_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.procurement_ap (
                    id SERIAL PRIMARY KEY,
                    po_id VARCHAR(50) UNIQUE NOT NULL,
                    project_id VARCHAR(100) DEFAULT '',
                    vendor_name VARCHAR(150) NOT NULL,
                    currency VARCHAR(20) DEFAULT 'VND',
                    exchange_rate NUMERIC(12,2) DEFAULT 1.0,
                    amount NUMERIC(12,2) NOT NULL,
                    item_desc TEXT,
                    project_budget NUMERIC(12,2) DEFAULT 0,
                    is_over_budget BOOLEAN DEFAULT FALSE,
                    status VARCHAR(50) DEFAULT '🟡 待審核 (Pending)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 資料庫 Table 初始化提示: {str(e)}")

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = AP_I18N.get(active_lang, AP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_procurement_ap_db(engine)

    # 1. 動態讀取工程報價專案清單與總預算
    project_budget_map = {}
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT project_code, project_name, total_quote_amount FROM public.project_quotations"))
                for r in res.fetchall():
                    p_key = f"{r[0]} - {r[1]}"
                    project_budget_map[p_key] = float(r[2])
        except Exception:
            pass

    if not project_budget_map:
        project_budget_map = {
            "PROJ-2026-001 - 西寧廠低壓配電盤案": 150000000.0,
            "PROJ-2026-002 - 海防馬達控制中心": 280000000.0
        }

    # 完整三大頁籤
    tab_add, tab_audit, tab_list = st.tabs([L["tab_add"], L["tab_audit"], L["tab_list"]])

    # ----------------------------------------------------
    # 📝 1. 採購與應付請款登記 (完整含多項明細表單與外幣匯率)
    # ----------------------------------------------------
    with tab_add:
        c1, c2, c3 = st.columns(3)
        with c1:
            po_id = st.text_input(L["lbl_po_id"], value=f"PO-{datetime.datetime.now().strftime('%Y%m%d%H%M')}")
            vendor_name = st.text_input(L["lbl_vendor"], value="Schneider Electric Vietnam")
        with c2:
            proj_options = [L["no_proj"]] + list(project_budget_map.keys())
            selected_proj = st.selectbox(L["lbl_project"], proj_options)
            currency = st.selectbox(L["lbl_currency"], ["VND", "USD", "TWD", "RMB"])
        with c3:
            ex_rate = 1.0
            if currency == "USD":
                ex_rate = st.number_input(L["lbl_exchange_rate"], value=25400.0, step=100.0)
            elif currency == "TWD":
                ex_rate = st.number_input(L["lbl_exchange_rate"], value=780.0, step=10.0)
            else:
                ex_rate = st.number_input(L["lbl_exchange_rate"], value=1.0, disabled=True)

        st.markdown("---")
        st.markdown("##### 📦 錄入本次採購資材品項與規格明細：")

        if "ap_temp_cart" not in st.session_state:
            st.session_state.ap_temp_cart = []

        with st.form("form_add_ap_item"):
            col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 1, 1.5])
            with col_i1:
                i_name = st.text_input(L["lbl_item_name"], value="無熔絲斷路器 (MCCB)")
            with col_i2:
                i_spec = st.text_input(L["lbl_item_spec"], value="3P 400A 36kA")
            with col_i3:
                i_qty = st.number_input(L["lbl_qty"], min_value=1, value=2, step=1)
            with col_i4:
                i_price = st.number_input(L["lbl_unit_price"], min_value=0.0, value=12500000.0, step=500000.0)

            if st.form_submit_button(L["btn_add_item"], type="secondary"):
                amt = i_qty * i_price * ex_rate
                st.session_state.ap_temp_cart.append({
                    "item_name": i_name,
                    "spec": i_spec,
                    "qty": i_qty,
                    "unit_price": i_price,
                    "amount_vnd": amt
                })
                st.rerun()

        # 展示臨時清單與預算對比
        total_req_amount_vnd = 0.0
        if st.session_state.ap_temp_cart:
            st.markdown(f"##### {L['lbl_cart']}")
            df_cart = pd.DataFrame(st.session_state.ap_temp_cart)
            st.dataframe(df_cart, use_container_width=True)
            total_req_amount_vnd = df_cart["amount_vnd"].sum()
            st.markdown(f"**💰 本次採購請款總金額：`{total_req_amount_vnd:,.0f} VND`**")

        p_budget = 0.0
        p_spent = 0.0
        is_over = False

        if selected_proj != L["no_proj"]:
            p_budget = project_budget_map.get(selected_proj, 0.0)
            if engine:
                try:
                    with engine.connect() as conn:
                        p_code = selected_proj.split(" - ")[0]
                        res = conn.execute(text("SELECT SUM(amount) FROM public.procurement_ap WHERE project_id LIKE :pcode"), {"pcode": f"%{p_code}%"})
                        val = res.fetchone()[0]
                        if val:
                            p_spent = float(val)
                except Exception:
                    pass

            rem_budget = p_budget - p_spent
            st.info(L["lbl_budget_info"].format(budget=p_budget, spent=p_spent, rem=rem_budget))

            if total_req_amount_vnd > rem_budget:
                is_over = True
                st.error(L["alert_over_budget"])

        if st.button(L["btn_submit"], type="primary", use_container_width=True):
            if not st.session_state.ap_temp_cart:
                st.error("⚠️ 請至少新增一項採購品項資材明細！")
            else:
                final_status = "⚠️ 超預算 (待總經理簽核)" if is_over else "🟡 待主管審核 (Pending)"
                p_code_save = selected_proj.split(" - ")[0] if selected_proj != L["no_proj"] else ""
                desc_text = " | ".join([f"{x['item_name']}({x['spec']})x{x['qty']}" for x in st.session_state.ap_temp_cart])

                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.procurement_ap 
                                (po_id, project_id, vendor_name, currency, exchange_rate, amount, item_desc, project_budget, is_over_budget, status)
                                VALUES (:po, :pid, :vname, :curr, :ex, :amt, :desc, :pbud, :over, :st)
                            """), {
                                "po": po_id, "pid": p_code_save, "vname": vendor_name,
                                "curr": currency, "ex": ex_rate, "amt": total_req_amount_vnd,
                                "desc": desc_text, "pbud": p_budget, "over": is_over, "st": final_status
                            })
                        st.success(L["msg_success"].format(status=final_status))
                        st.session_state.ap_temp_cart = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")
                else:
                    st.success(L["msg_success"].format(status=final_status))
                    st.session_state.ap_temp_cart = []
                    st.rerun()

    # ----------------------------------------------------
    # ⚖️ 2. AP 帳款審核與沖銷付款 (修復語法錯誤)
    # ----------------------------------------------------
    with tab_audit:
        st.markdown("#### ⚖️ 應付帳款 (AP) 審核與沖銷處置")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT id, po_id, vendor_name, amount, status, item_desc 
                        FROM public.procurement_ap 
                        WHERE status LIKE '%待%' OR status LIKE '%超預算%'
                        ORDER BY id DESC
                    """))
                    pending_rows = res.fetchall()
                    if pending_rows:
                        for row in pending_rows:
                            col_a1, col_a2, col_a3 = st.columns([2.5, 1, 1])
                            col_a1.write(f"**{row[1]}** | {row[2]} | `{float(row[3]):,.0f} VND` ({row[4]})\n> 明細: {row[5]}")
                            if col_a2.button(L["btn_approve"], key=f"app_{row[0]}"):
                                with engine.begin() as c_up:
                                    c_up.execute(text("UPDATE public.procurement_ap SET status = '🟢 已審核 (待付款)' WHERE id = :id"), {"id": row[0]})
                                st.rerun()
                            if col_a3.button(L["btn_pay"], key=f"pay_{row[0]}"):
                                with engine.begin() as c_up:
                                    c_up.execute(text("UPDATE public.procurement_ap SET status = '🔵 已付款沖銷 (Paid)' WHERE id = :id"), {"id": row[0]})
                                st.rerun()
                    else:
                        st.success("🎉 目前無待審核或待付款之 AP 帳款項目。")
            except Exception as e:
                st.info("尚未讀取到待處置 AP 項目。")

    # ----------------------------------------------------
    # 📊 3. 採購請款歷史紀錄與預算稽核看板
    # ----------------------------------------------------
    with tab_list:
        st.markdown("#### 📊 全廠採購請款總表與預算執行率")
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT po_id, project_id, vendor_name, currency, amount, project_budget, status, created_at, item_desc
                        FROM public.procurement_ap
                        ORDER BY created_at DESC
                    """))
                    rows = res.fetchall()
                    if rows:
                        df_ap = pd.DataFrame(rows, columns=["採購單號", "專案代碼", "供應商", "幣別", "請款金額(VND)", "專案預算", "審核狀態", "建立時間", "品項明細"])
                        st.dataframe(df_ap, use_container_width=True)
                    else:
                        st.info("目前尚無採購請款紀錄。")
            except Exception:
                st.info("無法載入採購請款紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)
