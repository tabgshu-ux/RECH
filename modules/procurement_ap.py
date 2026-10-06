import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 採購與應付帳款模組多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 財務部 - 採購與應付帳款 (AP) 管理中心",
        "caption": "記錄跨國廠區（西寧廠/海防廠）採購訂單、應付帳款、多幣別付款排程與供應商請款追蹤。",
        "tab_list": "📑 應付款項總表與付款進度",
        "tab_edit": "✍️ 修改付款進度與審核紀錄",
        "tab_add": "➕ 登記新採購與應付帳款 (AP)",
        "table_header": "📋 供應商應付帳款 (AP) 清冊",
        "no_records": "目前無應付帳款紀錄。",
        "read_error": "讀取資料失敗: ",
        "edit_header": "✍️ 修改採購應付款與審核備註",
        "select_ap": "請選擇要更新的採購單：",
        "current_ap": "當前採購案",
        "total_amount_label": "總應付款額",
        "new_progress_label": "更新「付款與交貨進度說明」*",
        "new_reason_label": "更新/追加「供應商對帳備註」",
        "modifier_label": "修改人員姓名*",
        "save_update_btn": "💾 儲存並更新 AP 紀錄",
        "update_success": "採購單 `{target_id}` 之付款進度與備註已更新！",
        "add_header": "➕ 登記新採購與應付帳款專案",
        "ap_id_label": "採購/請款編號 *",
        "supplier_label": "供應商名稱 *",
        "supplier_placeholder": "例如: 越南胡志明市鋼鐵股份公司",
        "item_name_label": "採購品項名稱 *",
        "item_placeholder": "例如: 2000A 銅排母線原料 500kg",
        "currency_label": "交易幣別 *",
        "currency_opts": ["越南盾", "美金", "台幣", "人民幣"],
        "usd_label": "總金額 (USD - 小數點後 3 位) *",
        "total_lbl": "總金額 *",
        "pay_terms_label": "付款條件 *",
        "terms_opts": ["即期票", "月結 30 天", "月結 60 天", "分期付款"],
        "desc_label": "採購備註說明",
        "desc_placeholder": "填寫合約細節或交貨注意事項...",
        "save_new_btn": "💾 儲存並建立應付帳款項目",
        "create_success": "採購應付款專案 `{ap_id}` 建立成功！",
        "fill_warning": "⚠️ 請完整填寫供應商名稱與品項名稱！",
        # 表格欄位
        "col_index": "STT",
        "col_ap_id": "採購編號",
        "col_supplier": "供應商名稱",
        "col_item": "採購品項",
        "col_currency": "幣別",
        "col_total": "總金額",
        "col_terms": "付款條件",
        "col_progress": "交貨進度",
        "col_desc": "備註說明"
    },
    "Tiếng Việt": {
        "title": "🛒 Khối Tài chính - Quản lý Mua hàng & Phải trả (AP)",
        "caption": "Quản lý đơn hàng mua, công nợ phải trả nhà cung cấp, lịch thanh toán đa tiền tệ cho Tây Ninh và Hải Phòng.",
        "tab_list": "📑 Danh sách Phải trả & Tiến độ",
        "tab_edit": "✍️ Cập nhật Tiến độ Thanh toán",
        "tab_add": "➕ Đăng ký Khoản phải trả (AP) Mới",
        "table_header": "📋 Sổ chi tiết Khoản phải trả Nhà cung cấp (AP)",
        "no_records": "Hiện không có bản ghi khoản phải trả nào.",
        "read_error": "Lỗi đọc dữ liệu: ",
        "edit_header": "✍️ Sửa đổi tiến độ thanh toán & Ghi chú đối chiếu",
        "select_ap": "Chọn đơn hàng cần cập nhật:",
        "current_ap": "Đơn hàng hiện tại",
        "total_amount_label": "Tổng tiền phải trả",
        "new_progress_label": "Cập nhật \"Tiến độ giao hàng & thanh toán\" *",
        "new_reason_label": "Cập nhật/Bổ sung \"Ghi chú đối chiếu nhà cung cấp\"",
        "modifier_label": "Họ tên người sửa*",
        "save_update_btn": "💾 Lưu và cập nhật AP",
        "update_success": "Đã cập nhật đơn hàng `{target_id}` thành công!",
        "add_header": "➕ Đăng ký khoản phải trả nhà cung cấp mới",
        "ap_id_label": "Mã đơn hàng / AP *",
        "supplier_label": "Tên nhà cung cấp *",
        "supplier_placeholder": "Ví dụ: Công ty Cổ phần Thép TP.HCM",
        "item_name_label": "Tên mặt hàng mua *",
        "item_placeholder": "Ví dụ: Đồng thanh cái 2000A 500kg",
        "currency_label": "Loại tiền tệ *",
        "currency_opts": ["Đồng Việt Nam (VND)", "Đô la Mỹ (USD)", "Đài tệ (TWD)", "Nhân dân tệ (CNY)"],
        "usd_label": "Tổng tiền (USD - 3 chữ số thập phân) *",
        "total_lbl": "Tổng tiền *",
        "pay_terms_label": "Điều kiện thanh toán *",
        "terms_opts": ["Thanh toán ngay", "Công nợ 30 ngày", "Công nợ 60 ngày", "Thanh toán theo đợt"],
        "desc_label": "Ghi chú mua hàng",
        "desc_placeholder": "Nhập chi tiết hợp đồng hoặc lưu ý giao hàng...",
        "save_new_btn": "💾 Lưu và đăng ký khoản phải trả",
        "create_success": "Đã tạo thành công đơn hàng `{ap_id}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ Tên nhà cung cấp và Mặt hàng!",
        # Tiêu đề bảng
        "col_index": "STT",
        "col_ap_id": "Mã AP",
        "col_supplier": "Nhà cung cấp",
        "col_item": "Mặt hàng",
        "col_currency": "Loại tiền",
        "col_total": "Tổng tiền",
        "col_terms": "Điều kiện",
        "col_progress": "Tiến độ",
        "col_desc": "Ghi chú"
    },
    "English": {
        "title": "📋 Finance - Procurement & Accounts Payable (AP)",
        "caption": "Track procurement orders, accounts payable, multi-currency payment terms, and supplier reconciliation.",
        "tab_list": "📑 AP Summary & Payment Schedule",
        "tab_edit": "✍️ Update Payment Progress & Audit",
        "tab_add": "➕ Register New AP Project",
        "table_header": "📋 Supplier Accounts Payable Registry",
        "no_records": "No accounts payable records found.",
        "read_error": "Failed to read data: ",
        "edit_header": "✍️ Modify Payment Progress & Remarks",
        "select_project": "Select AP to update:",
        "current_ap": "Current AP",
        "total_amount_label": "Total Amount",
        "new_progress_label": "Update Progress Description *",
        "new_reason_label": "Update/Append Supplier Remarks",
        "modifier_label": "Modifier Name *",
        "save_update_btn": "💾 Save & Update AP Progress",
        "update_success": "AP record `{target_id}` updated successfully!",
        "add_header": "➕ Register New Accounts Payable",
        "ap_id_label": "AP ID *",
        "supplier_label": "Supplier Name *",
        "supplier_placeholder": "Example: Ho Chi Minh Steel JSC",
        "item_name_label": "Item Name *",
        "item_placeholder": "Example: 2000A Copper Busbar 500kg",
        "currency_label": "Currency *",
        "currency_opts": ["VND", "USD", "TWD", "CNY"],
        "usd_label": "Total Amount (USD - 3 decimals) *",
        "total_lbl": "Total Amount *",
        "pay_terms_label": "Payment Terms *",
        "terms_opts": ["Immediate (Cash)", "Net 30 Days", "Net 60 Days", "Installments"],
        "desc_label": "Procurement Remarks",
        "desc_placeholder": "Enter contract details...",
        "save_new_btn": "💾 Save & Register AP",
        "create_success": "AP project `{ap_id}` successfully created!",
        "fill_warning": "⚠️ Please fill in Supplier Name and Item Name!",
        # Table headers
        "col_index": "No.",
        "col_ap_id": "AP ID",
        "col_entity": "Supplier",
        "col_item": "Item",
        "col_currency": "Currency",
        "col_total": "Total",
        "col_terms": "Terms",
        "col_progress": "Progress",
        "col_desc": "Remarks"
    }
}

# ----------------------------------------------------
# 🔄 採購模組專用：中越英雙向智慧對照引擎
# ----------------------------------------------------
def smart_translate_ap(text_val, target_lang):
    if not text_val or not isinstance(text_val, str) or text_val.strip() in ["None", "-", ""]:
        if target_lang == "Tiếng Việt": return "Chưa cập nhật"
        elif target_lang == "English": return "N/A"
        return "-"

    val_lower = text_val.lower()

    # 供應商與品項智慧對應
    if "鋼鐵" in text_val or "steel" in val_lower or "thép" in val_lower:
        if target_lang == "Tiếng Việt": return "Công ty Cổ phần Thép TP.HCM"
        elif target_lang == "English": return "Ho Chi Minh Steel JSC"
        return "越南胡志明市鋼鐵股份公司"
    if "銅排" in text_val or "busbar" in val_lower or "đồng" in val_lower:
        if target_lang == "Tiếng Việt": return "Đồng thanh cái 2000A 500kg"
        elif target_lang == "English": return "2000A Copper Busbar 500kg"
        return "2000A 銅排母線原料 500kg"

    return text_val

def format_curr_ap(amt, curr):
    if not curr: curr = "越南盾"
    if "VND" in curr or "越南盾" in curr or "Đồng" in curr: return f"₫ {amt:,.0f} VND"
    elif "USD" in curr or "美金" in curr or "Đô la" in curr: return f"$ {amt:,.3f} USD"
    elif "TWD" in curr or "台幣" in curr or "Đài tệ" in curr: return f"NT$ {amt:,.0f} TWD"
    elif "CNY" in curr or "人民幣" in curr or "Nhân dân tệ" in curr: return f"¥ {amt:,.2f} CNY"
    return f"{amt:,.3f} {curr}"

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = AP_I18N.get(active_lang, AP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    # 1. 應付帳款總覽
    with tab_list:
        st.subheader(L["table_header"])
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    display_list = []
                    for idx, r in df_ap.iterrows():
                        supp_disp = smart_translate_ap(r.get("entity_name"), active_lang)
                        proj_disp = smart_translate_ap(r.get("project_name"), active_lang)
                        prog_disp = smart_translate_ap(r.get("progress_note"), active_lang)

                        display_list.append({
                            L["col_index"]: idx + 1,
                            L["col_ap_id"]: r.get("invoice_id"),
                            L["col_supplier"]: supp_disp,
                            L["col_item"]: proj_disp,
                            L["col_currency"]: r.get("currency"),
                            L["col_total"]: format_curr_ap(r.get("quoted_amount", 0.0), r.get("currency")),
                            L["col_terms"]: r.get("payment_terms", "月結"),
                            L["col_progress"]: prog_disp,
                            L["col_desc"]: r.get("project_desc", "-")
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info(L["no_records"])
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    # 2. 修改付款進度
    with tab_edit:
        st.subheader(L["edit_header"])
        if engine:
            try:
                df_ap = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AP'", engine)
                if not df_ap.empty:
                    ap_opts = {f"{r['invoice_id']} - {smart_translate_ap(r['entity_name'], active_lang)}": r['invoice_id'] for _, r in df_ap.iterrows()}
                    sel_label = st.selectbox(L["select_ap"], list(ap_opts.keys()))
                    target_id = ap_opts[sel_label]
                    target_row = df_ap[df_ap['invoice_id'] == target_id].iloc[0]

                    st.markdown(f"**{L['current_ap']}**：`{target_row['invoice_id']}` | **{L['total_amount_label']}**：{format_curr_ap(target_row['quoted_amount'], target_row['currency'])}")
                    
                    with st.form("form_update_ap"):
                        default_prog = smart_translate_ap(target_row.get("progress_note", ""), active_lang)
                        new_progress = st.text_area(L["new_progress_label"], value=default_prog)
                        new_reason = st.text_area(L["new_reason_label"], value=target_row.get("uncollected_reason", ""))
                        modifier = st.text_input(L["modifier_label"], value=st.session_state.get("user_name", "admin"))

                        if st.form_submit_button(L["save_update_btn"], use_container_width=True):
                            with engine.connect() as conn:
                                conn.execute(
                                    text("UPDATE invoices SET progress_note = :prog, uncollected_reason = :reason WHERE invoice_id = :id"),
                                    {"prog": new_progress, "reason": new_reason, "id": target_id}
                                )
                                conn.commit()
                            st.success(L["update_success"].format(target_id=target_id))
                            st.rerun()
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    # 3. 新增採購應付帳款
    with tab_add:
        st.subheader(L["add_header"])
        c1, c2 = st.columns(2)
        with c1:
            ap_id = st.text_input(L["ap_id_label"], value=f"AP-2026-{datetime.datetime.now().strftime('%m%d%H%M')}")
            supplier_name = st.text_input(L["supplier_label"], placeholder=L["supplier_placeholder"])
            item_name = st.text_input(L["item_name_label"], placeholder=L["item_placeholder"])
            currency = st.selectbox(L["currency_label"], L["currency_opts"])
            
            if "USD" in currency or "美金" in currency or "Đô la" in currency:
                total_amount = st.number_input(L["usd_label"], min_value=0.0, value=5000.000, format="%.3f", step=0.001)
            else:
                total_amount = st.number_input(L["total_lbl"], min_value=0.0, value=120000000.0, step=1000000.0)

        with c2:
            pay_terms = st.selectbox(L["pay_terms_label"], L["terms_opts"])
            desc = st.text_area(L["desc_label"], placeholder=L["desc_placeholder"])
            progress_note = st.text_input("初始交貨進度", value="已發出採購訂單 / 等待廠商確認")

        if st.button(L["save_new_btn"], type="primary", use_container_width=True):
            if supplier_name and item_name:
                if engine:
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO invoices (
                                    invoice_id, entity_name, project_name, currency, amount, quoted_amount, 
                                    payment_terms, project_desc, progress_note, invoice_type, is_paid
                                ) VALUES (
                                    :id, :entity, :prj, :curr, :amt, :q_amt, :terms, :desc, :prog, 'AP', false
                                )
                            """),
                            {
                                "id": ap_id, "entity": supplier_name, "prj": item_name, "curr": currency,
                                "amt": total_amount, "q_amt": total_amount, "terms": pay_terms,
                                "desc": desc, "prog": progress_note
                            }
                        )
                        conn.commit()
                st.success(L["create_success"].format(ap_id=ap_id))
                st.rerun()
            else:
                st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
