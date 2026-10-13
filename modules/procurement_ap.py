import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 採購與應付帳款 (AP) 控管多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 管理部 - 採購與應付帳款 (AP) 預算控管中心",
        "caption": "自動連動工程部專案預算！採購請款金額超過報價預算時自動鎖定並觸發審核流程。",
        "tab_add": "📝 採購請款單錄入 (預算即時對比)",
        "tab_list": "📋 採購請款歷史紀錄與預算稽核",
        "lbl_po_id": "採購單號 (PO ID)",
        "lbl_project": "關聯工程專案 (連動工程部報價單)",
        "lbl_vendor": "供應商 / 外包商名稱",
        "lbl_amount": "本次請款金額 (VND)",
        "lbl_item_desc": "採購品項 / 資材說明",
        "lbl_budget_info": "📊 專案預算監控：總預算 `{budget:,.0f} VND` | 已請款 `{spent:,.0f} VND` | 剩餘預算 `{rem:,.0f} VND`",
        "btn_submit": "🚀 提交採購請款單",
        "alert_over_budget": "⚠️ 警告：本次請款金額高於專案剩餘預算！系統已自動標記為【超預算審核】狀態。",
        "msg_success": "✅ 採購請款單已成功寫入資料庫！狀態：`{status}`",
        "no_proj": "-- 無專案關聯 (一般行政採購) --"
    },
    "Tiếng Việt": {
        "title": "🛒 Phòng Quản lý - Mua Hàng & Phải Trả (AP) Khống Chế Ngân Sách",
        "caption": "Tự động kết nối ngân sách dự án kỹ thuật! Cảnh báo và khóa phê duyệt khi vượt ngân sách báo giá.",
        "tab_add": "📝 Nhập Yêu Cầu Mua Hàng & Thanh Toán",
        "tab_list": "📋 Lịch Sử Yêu Cầu Mua Hàng & Kiểm Toán Ngân Sách",
        "lbl_po_id": "Mã đơn mua hàng (PO)",
        "lbl_project": "Dự án kỹ thuật liên quan (Báo giá)",
        "lbl_vendor": "Nhà cung cấp / Thầu phụ",
        "lbl_amount": "Số tiền đề nghị thanh toán (VND)",
        "lbl_item_desc": "Mô tả vật tư / Hàng hóa",
        "lbl_budget_info": "📊 Giám sát ngân sách: Tổng `{budget:,.0f} VND` | Đã chi `{spent:,.0f} VND` | Còn lại `{rem:,.0f} VND`",
        "btn_submit": "🚀 Lưu Yêu Cầu Mua Hàng",
        "alert_over_budget": "⚠️ Cảnh báo: Số tiền thanh toán vượt quá ngân sách còn lại! Đã tự động chuyển trạng thái chờ duyệt.",
        "msg_success": "✅ Đã lưu yêu cầu mua hàng vào cơ sở dữ liệu! Trạng thái: `{status}`",
        "no_proj": "-- Không theo dự án (Chi phí hành chính) --"
    },
    "English": {
        "title": "🛒 GA & Procurement - Accounts Payable (AP) Budget Control",
        "caption": "Auto-linked to Engineering Project Budgets! Automatically locks requests that exceed quoted budget caps.",
        "tab_add": "📝 Purchase & AP Request Entry",
        "tab_list": "📋 AP History & Budget Audit Log",
        "lbl_po_id": "PO Number",
        "lbl_project": "Linked Engineering Project",
        "lbl_vendor": "Vendor / Subcontractor",
        "lbl_amount": "Requested Amount (VND)",
        "lbl_item_desc": "Material / Item Description",
        "lbl_budget_info": "📊 Budget Monitor: Total `{budget:,.0f} VND` | Spent `{spent:,.0f} VND` | Remaining `{rem:,.0f} VND`",
        "btn_submit": "🚀 Submit AP Request",
        "alert_over_budget": "⚠️ Warning: Requested amount exceeds remaining project budget! Flagged for manager approval.",
        "msg_success": "✅ AP Request saved to database! Status: `{status}`",
        "no_proj": "-- General Administrative Procurement --"
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
                    amount NUMERIC(12,2) NOT NULL,
                    item_desc TEXT,
                    project_budget NUMERIC(12,2) DEFAULT 0,
                    is_over_budget BOOLEAN DEFAULT FALSE,
                    status VARCHAR(50) DEFAULT '🟢 正常核銷 (Approved)',
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

    # 1. 從工程報價單資料庫動態撈取專案清單與預算
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

    # 若無專案紀錄，提供預設選單供測試
    if not project_budget_map:
        project_budget_map = {
            "PROJ-2026-001 - 西寧廠低壓配電盤案": 150000000.0,
            "PROJ-2026-002 - 海防馬達控制中心": 280000000.0
        }

    tab_add, tab_list = st.tabs([L["tab_add"], L["tab_list"]])

    # ----------------------------------------------------
    # 📝 Tab 1: 採購請款單錄入 (自動連動專案預算)
    # ----------------------------------------------------
    with tab_add:
        with st.form("form_procurement_ap"):
            c1, c2 = st.columns(2)
            with c1:
                po_id = st.text_input(L["lbl_po_id"], value=f"PO-{datetime.datetime.now().strftime('%Y%m%d%H%M')}")
                vendor_name = st.text_input(L["lbl_vendor"], value="Schneider Electric Vietnam")
            with c2:
                proj_options = [L["no_proj"]] + list(project_budget_map.keys())
                selected_proj = st.selectbox(L["lbl_project"], proj_options)
                req_amount = st.number_input(L["lbl_amount"], min_value=1000.0, value=25000000.0, step=1000000.0)

            item_desc = st.text_area(L["lbl_item_desc"], placeholder="請填寫採購之銅排、無熔絲開關 (MCCB) 或箱體材料規格...")

            # 專案預算檢查邏輯
            p_budget = 0.0
            p_spent = 0.0
            is_over = False

            if selected_proj != L["no_proj"]:
                p_budget = project_budget_map.get(selected_proj, 0.0)
                # 算累計已請款金額
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

                if req_amount > rem_budget:
                    is_over = True
                    st.error(L["alert_over_budget"])

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                final_status = "⚠️ 超預算 (待總經理簽核)" if is_over else "🟢 正常核銷 (Approved)"
                p_code_save = selected_proj.split(" - ")[0] if selected_proj != L["no_proj"] else ""

                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.procurement_ap 
                                (po_id, project_id, vendor_name, amount, item_desc, project_budget, is_over_budget, status)
                                VALUES (:po, :pid, :vname, :amt, :desc, :pbud, :over, :st)
                            """), {
                                "po": po_id, "pid": p_code_save, "vname": vendor_name,
                                "amt": req_amount, "desc": item_desc, "pbud": p_budget,
                                "over": is_over, "st": final_status
                            })
                        st.success(L["msg_success"].format(status=final_status))
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")

    # ----------------------------------------------------
    # 📋 Tab 2: 採購請款紀錄與預算稽核
    # ----------------------------------------------------
    with tab_list:
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT po_id, project_id, vendor_name, amount, project_budget, status, created_at
                        FROM public.procurement_ap
                        ORDER BY created_at DESC
                    """))
                    rows = res.fetchall()
                    if rows:
                        df_ap = pd.DataFrame(rows, columns=["採購單號", "專案代碼", "供應商", "請款金額", "專案預算", "審核狀態", "建立時間"])
                        st.dataframe(df_ap, use_container_width=True)
                    else:
                        st.info("目前尚無採購請款紀錄。")
            except Exception:
                st.info("無法載入採購請款紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_procurement_ap_page(engine=engine, lang=lang, **kwargs)
