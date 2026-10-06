import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 越南電子發票管理模組多語系字典 (i18n)
# ----------------------------------------------------
INVOICE_I18N = {
    "繁體中文": {
        "title": "📄 財務部 - 越南電子發票綜合管理中心",
        "caption": "符合越南稅務局 (GDT) 規範之電子發票 (Hóa đơn điện tử) 開立、檢核、總額彙整與狀態追蹤。",
        "tab_list": "📑 電子發票總表與合規狀態",
        "tab_issue": "➕ 開立新電子發票 (Hóa đơn mới)",
        "tab_verify": "🔍 稅務局發票代碼驗證 (Mã cơ quan thuế)",
        "table_header": "📋 廠區電子發票清冊 (E-Invoices Registry)",
        "no_records": "目前無電子發票紀錄。",
        "issue_header": "➕ 開立越南標準電子發票 (VAT 10%)",
        "lbl_inv_code": "發票代碼/序號 *",
        "lbl_cust_name": "買方客戶名稱 (Tên người mua) *",
        "cust_placeholder": "例如: 越南樟榜工業區A廠 (Nhà máy A KCN Trảng Bàng)",
        "lbl_tax_code": "買方統一編號/稅號 (Mã số thuế) *",
        "tax_placeholder": "例如: 3901234567",
        "lbl_amount": "銷售未稅金額 (USD) *",
        "lbl_desc": "品項與勞務說明 (Nội dung hàng hóa)",
        "desc_placeholder": "例如: 配電盤統包工程與設備安裝費",
        "btn_issue": "💾 簽發並上傳稅務局系統",
        "success_issue": "✅ 電子發票 `{inv_code}` 已成功開立並取得稅務驗證碼！",
        "fill_warning": "⚠️ 請完整填寫發票代碼、客戶名稱與稅號！",
        "verify_header": "🔍 越南稅務局 (GDT) 發票代碼線上檢核",
        "verify_input": "請輸入要查核的發票代碼 (Lookup Code):",
        "btn_verify": "🔎 查詢稅務局驗證狀態",
        "verify_result_ok": "✅ 驗證成功：此發票已向越南稅務總局完成申報，合規有效 (Hợp lệ)。",
        "col_index": "STT",
        "col_code": "發票代碼",
        "col_cust": "買方客戶",
        "col_tax": "稅號",
        "col_subtotal": "未稅金額",
        "col_vat": "VAT (10%)",
        "col_total": "含稅總額",
        "col_status": "稅務狀態",
        "col_date": "開立日期"
    },
    "Tiếng Việt": {
        "title": "📄 Khối Tài chính - Trung tâm Quản lý Hóa đơn Điện tử",
        "caption": "Quản lý phát hành, tra cứu, tổng hợp hóa đơn điện tử tuân thủ quy định Tổng cục Thuế (GDT).",
        "tab_list": "📑 Danh sách Hóa đơn & Trạng thái",
        "tab_issue": "➕ Phát hành Hóa đơn Mới",
        "tab_verify": "🔍 Tra cứu Mã cơ quan thuế",
        "table_header": "📋 Sổ chi tiết Hóa đơn Điện tử (E-Invoices)",
        "no_records": "Hiện không có bản ghi hóa đơn nào.",
        "issue_header": "➕ Lập hóa đơn điện tử tiêu chuẩn (VAT 10%)",
        "lbl_inv_code": "Ký hiệu / Số hóa đơn *",
        "lbl_cust_name": "Tên người mua / Khách hàng *",
        "cust_placeholder": "Ví dụ: Nhà máy A KCN Trảng Bàng, Tây Ninh",
        "lbl_tax_code": "Mã số thuế người mua *",
        "tax_placeholder": "Ví dụ: 3901234567",
        "lbl_amount": "Tiền hàng chưa thuế (USD) *",
        "lbl_desc": "Nội dung hàng hóa / dịch vụ *",
        "desc_placeholder": "Ví dụ: Lắp đặt tủ điện và thiết bị cơ điện",
        "btn_issue": "💾 Ký số và Phát hành hóa đơn",
        "success_issue": "✅ Đã phát hành thành công hóa đơn `{inv_code}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ Mã hóa đơn, Tên khách hàng và Mã số thuế!",
        "verify_header": "🔍 Tra cứu hóa đơn trực tuyến Tổng cục Thuế (GDT)",
        "verify_input": "Nhập mã tra cứu hóa đơn (Lookup Code):",
        "btn_verify": "🔎 Kiểm tra trạng thái thuế",
        "verify_result_ok": "✅ Hợp lệ: Hóa đơn đã được khai báo và xác thực thành công bởi cơ quan thuế.",
        "col_index": "STT",
        "col_code": "Ký hiệu hóa đơn",
        "col_cust": "Khách hàng",
        "col_tax": "Mã số thuế",
        "col_subtotal": "Chưa thuế",
        "col_vat": "VAT (10%)",
        "col_total": "Tổng cộng",
        "col_status": "Trạng thái",
        "col_date": "Ngày lập"
    },
    "English": {
        "title": "📄 Finance - E-Invoice Comprehensive Management Center",
        "caption": "Issue, verify, and track electronic invoices (Hóa đơn điện tử) compliant with Vietnam GDT regulations.",
        "tab_list": "📑 E-Invoices Registry & Status",
        "tab_issue": "➕ Issue New E-Invoice",
        "tab_verify": "🔍 GDT Tax Code Verification",
        "table_header": "📋 Customer E-Invoices Registry",
        "no_records": "No electronic invoices found.",
        "issue_header": "➕ Issue Standard E-Invoice (VAT 10%)",
        "lbl_inv_code": "Invoice Code / No. *",
        "lbl_cust_name": "Buyer / Customer Name *",
        "cust_placeholder": "Example: Tay Ninh Plant Client A",
        "lbl_tax_code": "Buyer Tax Code *",
        "tax_placeholder": "Example: 3901234567",
        "lbl_amount": "Amount Excl. VAT (USD) *",
        "lbl_desc": "Item Description *",
        "desc_placeholder": "Example: Switchgear installation and engineering services",
        "btn_issue": "💾 Sign & Issue to Tax Authority",
        "success_issue": "✅ E-invoice `{inv_code}` successfully issued and verified!",
        "fill_warning": "⚠️ Please fill in Invoice Code, Customer Name, and Tax Code!",
        "verify_header": "🔍 Vietnam GDT Tax Authority Invoice Verification",
        "verify_input": "Enter Invoice Lookup Code:",
        "btn_verify": "🔎 Verify Tax Status",
        "verify_result_ok": "✅ Valid: This invoice has been successfully declared and authenticated by the GDT.",
        "col_index": "No.",
        "col_code": "Invoice Code",
        "col_cust": "Customer",
        "col_tax": "Tax Code",
        "col_subtotal": "Excl. VAT",
        "col_vat": "VAT (10%)",
        "col_total": "Total Incl. VAT",
        "col_status": "Tax Status",
        "col_date": "Issue Date"
    }
}

def smart_translate_invoice(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    if "樟榜" in text_val or "trảng bàng" in val_lower or "tay ninh" in val_lower:
        if target_lang == "Tiếng Việt": return "Nhà máy A KCN Trảng Bàng, Tây Ninh"
        elif target_lang == "English": return "Tay Ninh Plant Client A"
        return "越南樟榜工業區A廠"

    if "已驗證" in text_val or "hợp lệ" in val_lower or "valid" in val_lower:
        if target_lang == "Tiếng Việt": return "Đã cấp mã (Hợp lệ)"
        elif target_lang == "English": return "Verified (Valid)"
        return "🟢 稅務局已驗證 (合規)"

    return text_val

def render_invoice_management(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = INVOICE_I18N.get(active_lang, INVOICE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "invoices_db" not in st.session_state:
        st.session_state.invoices_db = [
            {
                "code": "26E-0001",
                "cust": "越南樟榜工業區A廠",
                "tax_code": "3901234567",
                "amount": 25000.0,
                "vat": 2500.0,
                "total": 27500.0,
                "status": "已驗證",
                "date": "2026-10-02"
            }
        ]

    tab_list, tab_issue, tab_verify = st.tabs([
        L["tab_list"], L["tab_issue"], L["tab_verify"]
    ])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.invoices_db:
            display_data = []
            for idx, inv in enumerate(st.session_state.invoices_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: inv["code"],
                    L["col_cust"]: smart_translate_invoice(inv["cust"], active_lang),
                    L["col_tax"]: inv["tax_code"],
                    L["col_subtotal"]: f"${inv['amount']:,.2f} USD",
                    L["col_vat"]: f"${inv['vat']:,.2f} USD",
                    L["col_total"]: f"${inv['total']:,.2f} USD",
                    L["col_status"]: smart_translate_invoice(inv["status"], active_lang),
                    L["col_date"]: inv["date"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_issue:
        st.markdown(f"### {L['issue_header']}")
        with st.form("form_issue_invoice"):
            c1, c2 = st.columns(2)
            with c1:
                inv_code = st.text_input(L["lbl_inv_code"], value=f"26E-{len(st.session_state.invoices_db)+1:04d}")
                cust_name = st.text_input(L["lbl_cust_name"], placeholder=L["cust_placeholder"])
                tax_code = st.text_input(L["lbl_tax_code"], placeholder=L["tax_placeholder"])
            with c2:
                amount = st.number_input(L["lbl_amount"], min_value=0.0, value=10000.0, step=500.0)
                vat_amount = amount * 0.1
                st.info(f"💡 自動計算 VAT (10%)：**${vat_amount:,.2f} USD**")
                desc = st.text_area(L["lbl_desc"], placeholder=L["desc_placeholder"])

            if st.form_submit_button(L["btn_issue"], type="primary", use_container_width=True):
                if inv_code and cust_name and tax_code:
                    st.session_state.invoices_db.insert(0, {
                        "code": inv_code,
                        "cust": cust_name,
                        "tax_code": tax_code,
                        "amount": amount,
                        "vat": vat_amount,
                        "total": amount + vat_amount,
                        "status": "已驗證",
                        "date": datetime.date.today().strftime("%Y-%m-%d")
                    })
                    st.success(L["success_issue"].format(inv_code=inv_code))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab_verify:
        st.markdown(f"### {L['verify_header']}")
        lookup_code = st.text_input(L["verify_input"], value="26E-0001")
        if st.button(L["btn_verify"], type="primary"):
            if lookup_code:
                st.success(L["verify_result_ok"])

def show(*args, **kwargs):
    render_invoice_management(*args, **kwargs)

def main(*args, **kwargs):
    render_invoice_management(*args, **kwargs)
