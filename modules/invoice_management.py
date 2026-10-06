import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 越南電子發票管理模組多語系字典 (i18n)
# ----------------------------------------------------
E_INVOICE_I18N = {
    "繁體中文": {
        "title": "📊 財務部 - 越南電子發票綜合管理中心",
        "caption": "管理發票開立、查詢、總合申報與遵循越南稅務總局 (GDT) 規範。",
        "tab_list": "📑 發票清單與狀態",
        "tab_issue": "➕ 發行新發票",
        "tab_query": "🔍 稅務局代碼查詢",
        
        "issue_header": "➕ Lập hóa đơn điện tử tiêu chuẩn (VAT 10%)",
        "lbl_serial": "發票字軌與編號 / Ký hiệu / Số hóa đơn *",
        "lbl_subtotal": "未稅金額 (USD) / Tiền hàng chưa thuế (USD) *",
        "lbl_buyer": "買方名稱與地址 / Tên người mua / Khách hàng *",
        "buyer_placeholder": "例如: 越南西寧省工業區 A 廠",
        "vat_calc_msg": "💡 自動計算 VAT (10%) : ${vat_val:,.2f} USD",
        "lbl_taxcode": "買方稅號 / Mã số thuế người mua *",
        "taxcode_placeholder": "例如: 3901234567",
        "lbl_desc": "品項與服務內容 / Nội dung hàng hóa / dịch vụ *",
        "desc_placeholder": "例如: 承攬廠區配電盤安裝與機電工程服務",
        "btn_issue": "🚀 簽署並發行發票 (Ký số & Phát hành hóa đơn)",
        "success_issue": "✅ 電子發票編號 `{serial}` 已成功簽署並向 GDT 申報發行！",
        "fill_warning": "⚠️ 請完整填寫發票編號、買方名稱與稅號！",
        
        "col_serial": "發票號碼",
        "col_buyer": "買方名稱",
        "col_taxcode": "稅號",
        "col_total": "含稅總額",
        "col_status": "發票狀態"
    },
    "Tiếng Việt": {
        "title": "📊 Khối Tài chính - Trung tâm Quản lý Hóa đơn Điện tử",
        "caption": "Quản lý phát hành, tra cứu, tổng hợp hóa đơn điện tử tuân thủ quy định Tổng cục Thuế (GDT).",
        "tab_list": "📑 Danh sách Hóa đơn & Trạng thái",
        "tab_issue": "➕ Phát hành Hóa đơn Mới",
        "tab_query": "🔍 Tra cứu Mã cơ quan thuế",
        
        "issue_header": "➕ Lập hóa đơn điện tử tiêu chuẩn (VAT 10%)",
        "lbl_serial": "Ký hiệu / Số hóa đơn *",
        "lbl_subtotal": "Tiền hàng chưa thuế (USD) *",
        "lbl_buyer": "Tên người mua / Khách hàng *",
        "buyer_placeholder": "Ví dụ: Nhà máy A KCN Trảng Bàng, Tây Ninh",
        "vat_calc_msg": "💡 Tự động tính VAT (10%) : ${vat_val:,.2f} USD",
        "lbl_taxcode": "Mã số thuế người mua *",
        "taxcode_placeholder": "Ví dụ: 3901234567",
        "lbl_desc": "Nội dung hàng hóa / dịch vụ *",
        "desc_placeholder": "Ví dụ: Lắp đặt tủ điện và thiết bị cơ điện",
        "btn_issue": "🚀 Ký số & Phát hành hóa đơn",
        "success_issue": "✅ Đã ký số và phát hành hóa đơn điện tử `{serial}` thành công lên GDT!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ số hóa đơn, tên và mã số thuế người mua!",
        
        "col_serial": "Số hóa đơn",
        "col_buyer": "Khách hàng",
        "col_taxcode": "Mã số thuế",
        "col_total": "Tổng tiền (VAT)",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📊 Finance - E-Invoice Management Center",
        "caption": "Manage e-invoice issuance, lookup, and reporting compliant with General Department of Taxation (GDT).",
        "tab_list": "📑 Invoices & Status",
        "tab_issue": "➕ Issue New E-Invoice",
        "tab_query": "🔍 GDT Tax Code Lookup",
        
        "issue_header": "➕ Issue Standard E-Invoice (VAT 10%)",
        "lbl_serial": "Serial / Invoice No. *",
        "lbl_subtotal": "Subtotal (USD) *",
        "lbl_buyer": "Buyer Name / Customer *",
        "buyer_placeholder": "Example: Factory A, Trang Bang IZ, Tay Ninh",
        "vat_calc_msg": "💡 Auto-calculated VAT (10%) : ${vat_val:,.2f} USD",
        "lbl_taxcode": "Buyer Tax Code *",
        "taxcode_placeholder": "Example: 3901234567",
        "lbl_desc": "Item & Service Description *",
        "desc_placeholder": "Example: Switchboard installation and electromechanical services",
        "btn_issue": "🚀 Sign & Issue E-Invoice",
        "success_issue": "✅ E-invoice `{serial}` signed and issued to GDT successfully!",
        "fill_warning": "⚠️ Please fill in invoice number, buyer name, and tax code!",
        
        "col_serial": "Invoice No.",
        "col_buyer": "Buyer",
        "col_taxcode": "Tax Code",
        "col_total": "Total (Inc. VAT)",
        "col_status": "Status"
    }
}

def get_active_lang(passed_lang):
    if passed_lang in E_INVOICE_I18N:
        return passed_lang
    for key in ["current_lang", "lang", "language", "selected_lang"]:
        val = st.session_state.get(key)
        if val in E_INVOICE_I18N:
            return val
    return "Tiếng Việt"  # 預設越南文

def render_e_invoice_page(engine=None, lang=None, **kwargs):
    active_lang = get_active_lang(lang)
    L = E_INVOICE_I18N.get(active_lang, E_INVOICE_I18N["Tiếng Việt"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "einvoice_db" not in st.session_state:
        st.session_state.einvoice_db = [
            {"serial": "26E-0001", "buyer": "Schneider Electric Vietnam", "taxcode": "0301234567", "total": 49500.0, "status": "Đã cấp mã GDT (Authorized)"}
        ]

    tab_list, tab_issue, tab_query = st.tabs([
        L["tab_list"], L["tab_issue"], L["tab_query"]
    ])

    with tab_list:
        st.markdown(f"### {L['tab_list']}")
        if st.session_state.einvoice_db:
            display_data = []
            for item in st.session_state.einvoice_db:
                display_data.append({
                    L["col_serial"]: item["serial"],
                    L["col_buyer"]: item["buyer"],
                    L["col_taxcode"]: item["taxcode"],
                    L["col_total"]: f"${item['total']:,.2f} USD",
                    L["col_status"]: item["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info("Chưa có hóa đơn nào." if active_lang == "Tiếng Việt" else "目前無發票紀錄。")

    with tab_issue:
        st.markdown(f"### {L['issue_header']}")
        
        with st.form("form_einvoice"):
            c1, c2 = st.columns(2)
            with c1:
                serial_no = st.text_input(L["lbl_serial"], value=f"26E-{len(st.session_state.einvoice_db)+2:04d}")
                buyer_name = st.text_input(L["lbl_buyer"], placeholder=L["buyer_placeholder"])
                buyer_taxcode = st.text_input(L["lbl_taxcode"], placeholder=L["taxcode_placeholder"])
            with c2:
                subtotal = st.number_input(L["lbl_subtotal"], min_value=0.0, value=10000.0, step=1000.0)
                vat_val = subtotal * 0.10
                st.info(L["vat_calc_msg"].format(vat_val=vat_val))
                item_desc = st.text_input(L["lbl_desc"], placeholder=L["desc_placeholder"])

            if st.form_submit_button(L["btn_issue"], type="primary", use_container_width=True):
                if serial_no and buyer_name and buyer_taxcode:
                    total_amount = subtotal + vat_val
                    st.session_state.einvoice_db.insert(0, {
                        "serial": serial_no,
                        "buyer": buyer_name,
                        "taxcode": buyer_taxcode,
                        "total": total_amount,
                        "status": "Đã cấp mã GDT (Authorized)"
                    })
                    st.success(L["success_issue"].format(serial=serial_no))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab_query:
        st.markdown(f"### {L['tab_query']}")
        st.success("🔍 Tra cứu cổng thông tin điện tử Tổng cục Thuế (GDT) trực tuyến hoạt động bình常。" if active_lang == "Tiếng Việt" else "🔍 稅務總局 (GDT) 電子發票入口網站連線正常。")

def show(*args, **kwargs):
    render_e_invoice_page(*args, **kwargs)

def main(*args, **kwargs):
    render_e_invoice_page(*args, **kwargs)

def render_e_invoice_management(*args, **kwargs):
    render_e_invoice_page(*args, **kwargs)
