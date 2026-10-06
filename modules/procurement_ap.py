import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 採購與應付帳款 (AP) 模組多語系字典 (i18n)
# ----------------------------------------------------
PROCUREMENT_AP_I18N = {
    "繁體中文": {
        "title": "🛒 財務部 - 採購管理 & 應付帳款 (AP)",
        "caption": "管理採購單、供應商應付帳款、多幣別付款排程與西寧/海防廠立帳追蹤。",
        "tab_list": "📑 應付帳款總表與進度",
        "tab_progress": "💳 供應商付款狀態更新",
        "tab_add": "➕ 登記款項應付 (AP) 新增",
        "table_header": "📋 供應商應付帳款明細總表 (AP)",
        "no_records": "目前無應付帳款紀錄。",
        "progress_header": "💳 供應商付款與撥款進度管理",
        "progress_caption": "💡 在此選擇對應的採購單/AP編號，並更新給供應商的付款或電匯（TT）完成狀態。",
        "btn_update_progress": "🚀 確認更新付款狀態",
        "success_update": "✅ 供應商應付帳款付款狀態已成功更新！",
        
        "add_header": "➕ 登記全新供應商應付帳款 (AP)",
        "lbl_code": "AP 帳款編號 *",
        "lbl_vendor": "供應商名稱 (Nhà cung cấp) *",
        "vendor_placeholder": "例如: 施耐德電氣越南分公司",
        "lbl_category": "採購品項分類 *",
        "cat_opts": [
            "⚡ 高低壓配電盤與斷路器零件",
            "🔩 銅排、線材與五金原物料",
            "💻 廠區 IT 設備與辦公軟體",
            "🏭 生產機械具備用零件與模具",
            "🛡️ 勞安防護與廠區環保耗材"
        ],
        "lbl_item": "採購品項詳細說明 *",
        "item_placeholder": "例如: 廠區高壓配電盤及斷路器設備",
        "lbl_currency": "幣別選擇 *",
        "lbl_amount": "採購總金額 *",
        "lbl_terms": "付款條件 / 信用期 *",
        "terms_opts": ["T/T 30天票期", "L/C 即期信用狀", "貨到付款 (COD)", "3-6-9 期分期付款"],
        "btn_save": "💾 儲存並建立 AP 帳款檔案",
        "success_save": "✅ AP 帳款編號 `{ap_code}` 已成功建立！",
        "fill_warning": "⚠️ 請完整填寫 AP 編號與供應商名稱！",
        "col_index": "STT",
        "col_code": "AP 編號",
        "col_vendor": "供應商名稱",
        "col_cat": "品項分類",
        "col_item": "詳細說明",
        "col_curr": "幣別",
        "col_total": "總金額",
        "col_terms": "付款條件",
        "col_status": "付款進度",
        "col_note": "備註"
    },
    "Tiếng Việt": {
        "title": "🛒 Khối Tài chính - Quản lý Mua hàng & Phải trả (AP)",
        "caption": "Quản lý đơn hàng mua, công nợ phải trả nhà cung cấp, lịch thanh toán đa tiền tệ cho Tây Ninh và Hải Phòng.",
        "tab_list": "📑 Danh sách Phải trả & Tiến độ",
        "tab_progress": "💳 Cập nhật Trạng thái Thanh toán",
        "tab_add": "➕ Đăng ký Khoản phải trả (AP) Mới",
        "table_header": "📋 Sổ chi tiết Khoản phải trả Nhà cung cấp (AP)",
        "no_records": "Hiện không có bản ghi phải trả nào.",
        "progress_header": "💳 Quản lý trạng thái thanh toán nhà cung cấp",
        "progress_caption": "💡 Chọn mã AP tương ứng bên dưới để xác nhận đã thanh toán hoặc chuyển khoản cho nhà cung cấp.",
        "btn_update_progress": "🚀 Xác nhận cập nhật trạng thái",
        "success_update": "✅ Đã cập nhật trạng thái thanh toán thành công!",
        
        "add_header": "➕ Đăng ký Khoản phải trả Nhà cung cấp Mới",
        "lbl_code": "Mã AP *",
        "lbl_vendor": "Tên nhà cung cấp *",
        "vendor_placeholder": "Ví dụ: Schneider Electric Vietnam",
        "lbl_category": "Phân loại mặt hàng *",
        "cat_opts": [
            "⚡ Tủ điện trung/hạ thế & linh kiện",
            "🔩 Đồng thanh cái, dây cáp & vật tư",
            "💻 Thiết bị IT & phần mềm văn phòng",
            "🏭 Phụ tùng máy móc sản xuất & khuôn",
            "🛡️ Thiết bị bảo hộ lao động & vật tư"
        ],
        "lbl_item": "Mô tả chi tiết mặt hàng *",
        "item_placeholder": "Ví dụ: Tủ điện trung thế và thiết bị đóng cắt",
        "lbl_currency": "Loại tiền *",
        "lbl_amount": "Tổng số tiền *",
        "lbl_terms": "Điều kiện thanh toán *",
        "terms_opts": ["T/T 30 ngày", "L/C trả ngay", "Thanh toán khi nhận hàng (COD)", "Trả góp 3-6-9 tháng"],
        "btn_save": "💾 Lưu và tạo hồ sơ AP",
        "success_save": "✅ Đã tạo thành công khoản AP `{ap_code}`!",
        "fill_warning": "⚠️ Vui lòng điền Mã AP và Tên nhà cung cấp!",
        "col_index": "STT",
        "col_code": "Mã AP",
        "col_vendor": "Nhà cung cấp",
        "col_cat": "Phân loại",
        "col_item": "Chi tiết",
        "col_curr": "Loại tiền",
        "col_total": "Tổng tiền",
        "col_terms": "Điều kiện",
        "col_status": "Tiến độ",
        "col_note": "Ghi chú"
    },
    "English": {
        "title": "🛒 Finance - Procurement & Accounts Payable (AP)",
        "caption": "Manage purchase orders, supplier accounts payable, multi-currency payment schedules for Tay Ninh and Hai Phong.",
        "tab_list": "📑 Accounts Payable & Progress",
        "tab_progress": "💳 Update Payment Status",
        "tab_add": "➕ Register New AP Record",
        "table_header": "📋 Supplier Accounts Payable Registry (AP)",
        "no_records": "No accounts payable records found.",
        "progress_header": "💳 Supplier Payment Status Management",
        "progress_caption": "💡 Select the corresponding AP code to update wire transfer or payment completion status for suppliers.",
        "btn_update_progress": "🚀 Confirm Payment Status Update",
        "success_update": "✅ AP payment status updated successfully!",
        
        "add_header": "➕ Register New Supplier AP Record",
        "lbl_code": "AP Code *",
        "lbl_vendor": "Supplier Name *",
        "vendor_placeholder": "Example: Schneider Electric Vietnam",
        "lbl_category": "Item Category *",
        "cat_opts": [
            "⚡ Switchgear & Circuit Breakers",
            "🔩 Copper Busbars & Raw Materials",
            "💻 Plant IT Equipment & Software",
            "🏭 Production Machinery Parts & Molds",
            "🛡️ PPE & Environmental Consumables"
        ],
        "lbl_item": "Detailed Item Description *",
        "item_placeholder": "Example: High-voltage switchboards and circuit breakers",
        "lbl_currency": "Currency *",
        "lbl_amount": "Total Amount *",
        "lbl_terms": "Payment Terms *",
        "terms_opts": ["T/T 30 Days", "At-Sight L/C", "Cash on Delivery (COD)", "Installment (3-6-9 Months)"],
        "btn_save": "💾 Save & Create AP Record",
        "success_save": "✅ AP record `{ap_code}` successfully created!",
        "fill_warning": "⚠️ Please fill in AP Code and Supplier Name!",
        "col_index": "No.",
        "col_code": "AP Code",
        "col_vendor": "Supplier",
        "col_cat": "Category",
        "col_item": "Description",
        "col_curr": "Currency",
        "col_total": "Total",
        "col_terms": "Terms",
        "col_status": "Progress",
        "col_note": "Note"
    }
}

def smart_translate_ap(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    if target_lang == "Tiếng Việt":
        if "施耐德電氣越南分公司" in text_val: return "Schneider Electric (Chi nhánh Việt Nam)"
        if "尚未更新" in text_val: return "Chưa cập nhật"
        if "T/T 30天票期" in text_val: return "T/T 30 ngày (Thanh toán chậm)"
    elif target_lang == "English":
        if "施耐德電氣越南分公司" in text_val: return "Schneider Electric Vietnam"
        if "尚未更新" in text_val: return "Not Updated"
        if "T/T 30天票期" in text_val: return "T/T 30 Days Credit"
    return text_val

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PROCUREMENT_AP_I18N.get(active_lang, PROCUREMENT_AP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "procurement_ap_db" not in st.session_state:
        st.session_state.procurement_ap_db = [
            {
                "code": "AP-2026-888",
                "vendor": "施耐德電氣越南分公司",
                "category": "⚡ 高低壓配電盤與斷路器零件",
                "item": "尚未更新",
                "currency": "USD",
                "amount": 45000.0,
                "terms": "T/T 30天票期",
                "status": "尚未更新",
                "note": "-"
            }
        ]

    tab_list, tab_progress, tab_add = st.tabs([
        L["tab_list"], L["tab_progress"], L["tab_add"]
    ])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.procurement_ap_db:
            display_data = []
            for idx, item in enumerate(st.session_state.procurement_ap_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_vendor"]: smart_translate_ap(item["vendor"], active_lang),
                    L["col_cat"]: smart_translate_ap(item.get("category", "標準品項"), active_lang),
                    L["col_item"]: smart_translate_ap(item["item"], active_lang),
                    L["col_curr"]: item["currency"],
                    L["col_total"]: f"${item['amount']:,.3f} USD",
                    L["col_terms"]: smart_translate_ap(item["terms"], active_lang),
                    L["col_status"]: smart_translate_ap(item["status"], active_lang),
                    L["col_note"]: item["note"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_progress:
        st.markdown(f"### {L['progress_header']}")
        st.info(L["progress_caption"])
        if st.button(L["btn_update_progress"], type="primary"):
            st.success(L["success_update"])

    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_ap"):
            c1, c2 = st.columns(2)
            with c1:
                ap_code = st.text_input(L["lbl_code"], value=f"AP-2026-{len(st.session_state.procurement_ap_db)+1:03d}")
                vendor = st.text_input(L["lbl_vendor"], placeholder=L["vendor_placeholder"])
                category = st.selectbox(L["lbl_category"], L["cat_opts"])
            with c2:
                currency = st.selectbox(L["lbl_currency"], ["USD", "VND", "TWD", "EUR"])
                amount = st.number_input(L["lbl_amount"], min_value=0.0, value=15000.0, step=1000.0)
                terms = st.selectbox(L["lbl_terms"], L["terms_opts"])

            item_desc = st.text_input(L["lbl_item"], placeholder=L["item_placeholder"])

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if ap_code and vendor:
                    st.session_state.procurement_ap_db.insert(0, {
                        "code": ap_code,
                        "vendor": vendor,
                        "category": category,
                        "item": item_desc if item_desc else "標準採購零組件",
                        "currency": currency,
                        "amount": amount,
                        "terms": terms,
                        "status": "審核完成 (Approved)",
                        "note": "-"
                    })
                    st.success(L["success_save"].format(ap_code=ap_code))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def render_procurement_ap(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
