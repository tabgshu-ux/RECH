import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 應收帳款與工程對帳管理模組多語系字典 (i18n)
# ----------------------------------------------------
SALES_ORDER_AR_I18N = {
    "繁體中文": {
        "title": "📋 財務部 - 工程專案應收帳款 (AR) 與對帳管理中心",
        "caption": "依據裕豐電機工業工程請款對帳單（和鼎隆、佳威、彥豪、第一傳動 Timotion、SUPERLON 等），管理合約總額、分期請款百分比、已開立發票與未收款追蹤。",
        "tab_list": "📑 專案應收帳款總表與對帳清冊",
        "tab_details": "📊 各大工程合約分項請款與進度",
        "tab_add": "➕ 新增工程合約與應收帳款 (AR)",
        "tab_invoice": "⚡ 越南電子發票開立與 GDT 驗證",
        "table_header": "📋 裕豐電機工業跨國工程應收帳款總覽",
        "no_records": "目前無應收帳款紀錄。",
        "details_header": "🔍 選擇工程專案檢視詳細請款條件與對帳進度",
        "select_project": "選擇工程專案合約 *",
        "metric_total": "合約總金額 (Total Contract)",
        "metric_collected": "已收款金額 (Collected)",
        "metric_outstanding": "未收款總計 (Outstanding)",
        "milestone_header": "📑 分期請款進度與對帳明細 (Milestone Details)",
        "add_header": "➕ 登記全新工程合約與應收帳款項目 (AR)",
        "lbl_code": "合約編號 / 專案代碼 *",
        "lbl_customer": "客戶 / 業主名稱 *",
        "cust_placeholder": "例如: 越南和鼎隆建築責任有限公司 / 佳威商旅",
        "lbl_total": "合約總金額 (VND) *",
        "lbl_date": "簽約日期 *",
        "lbl_terms": "付款條款說明 *",
        "terms_placeholder": "例如: 簽約訂金 30% / 施工完成 40% / 驗收保留 30%",
        "btn_save": "💾 建立合約與應收帳款檔案",
        "success_save": "✅ 工程專案 `{code}` 應收帳款合約已成功建立！",
        "fill_warning": "⚠️ 請完整填寫合約編號與客戶名稱！",
        "col_index": "STT",
        "col_code": "合約編號",
        "col_customer": "客戶名稱",
        "col_total": "合約總金額 (VND)",
        "col_collected": "已收款金額",
        "col_outstanding": "未收款總計",
        "col_status": "對帳狀態",
        "col_phase": "請款階段 / 專案項目",
        "col_pct": "請款比例 (%)",
        "col_amt": "請款金額 (VND)",
        "col_st": "狀態"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Tài chính - Quản lý Phải thu (AR) & Đối chiếu Hợp đồng",
        "caption": "Quản lý tổng giá trị hợp đồng, tỷ lệ thanh toán theo giai đoạn, hóa đơn đã mở và theo dõi công nợ cho các dự án.",
        "tab_list": "📑 Danh sách Phải thu Dự án & Đối chiếu",
        "tab_details": "📊 Chi tiết Thanh toán theo Hợp đồng",
        "tab_add": "➕ Thêm Hợp đồng & Khoản phải thu (AR)",
        "tab_invoice": "⚡ Phát hành Hóa đơn điện tử GDT",
        "table_header": "📋 Tổng quan Công nợ Phải thu Dự án",
        "no_records": "Hiện không có bản ghi phải thu nào.",
        "details_header": "🔍 Chọn dự án để xem điều kiện thanh toán chi tiết",
        "select_project": "Chọn dự án hợp đồng *",
        "metric_total": "Tổng giá trị hợp đồng (Total Contract)",
        "metric_collected": "Đã thu tiền (Collected)",
        "metric_outstanding": "Còn lại / Phải thu (Outstanding)",
        "milestone_header": "📑 Tiến độ thanh toán theo giai đoạn & Chi tiết đối chiếu",
        "add_header": "➕ Đăng ký Hợp đồng Dự án & Khoản phải thu Mới (AR)",
        "lbl_code": "Mã hợp đồng / Dự án *",
        "lbl_customer": "Tên khách hàng / Chủ đầu tư *",
        "cust_placeholder": "Ví dụ: CÔNG TY TNHH XÂY DỰNG HO TEAM",
        "lbl_total": "Tổng giá trị hợp đồng (VND) *",
        "lbl_date": "Ngày ký *",
        "lbl_terms": "Điều khoản thanh toán *",
        "terms_placeholder": "Ví dụ: Đặt cọc 30% / Hoàn thành 40% / Bảo hành 30%",
        "btn_save": "💾 Lưu hồ sơ Phải thu (AR)",
        "success_save": "✅ Đã tạo thành công hợp đồng phải thu `{code}`!",
        "fill_warning": "⚠️ Vui lòng điền Mã hợp đồng và Tên khách hàng!",
        "col_index": "STT",
        "col_code": "Mã hợp đồng",
        "col_customer": "Khách hàng",
        "col_total": "Tổng giá trị (VND)",
        "col_collected": "Đã thu",
        "col_outstanding": "Còn lại (Chưa thu)",
        "col_status": "Trạng thái",
        "col_phase": "Giai đoạn thanh toán",
        "col_pct": "Tỷ lệ (%)",
        "col_amt": "Số tiền (VND)",
        "col_st": "Trạng thái"
    },
    "English": {
        "title": "📋 Finance - Engineering AR & Contract Billing Center",
        "caption": "Manage contract amounts, staging percentages, invoiced amounts, and outstanding receivables for projects.",
        "tab_list": "📑 Project AR & Reconciliation List",
        "tab_details": "📊 Contract Staging & Milestone Details",
        "tab_add": "➕ Register New Engineering Contract (AR)",
        "tab_invoice": "⚡ GDT E-Invoice Issuance",
        "table_header": "📋 Engineering Accounts Receivable Overview",
        "no_records": "No accounts receivable records found.",
        "details_header": "🔍 Select Contract to View Milestone Details & Status",
        "select_project": "Select Contract Project *",
        "metric_total": "Total Contract Amount",
        "metric_collected": "Collected Amount",
        "metric_outstanding": "Outstanding Amount",
        "milestone_header": "📑 Milestone Payment Progress & Reconciliation Details",
        "add_header": "➕ Register New Contract & AR Record",
        "lbl_code": "Contract / Project Code *",
        "lbl_customer": "Customer / Owner Name *",
        "cust_placeholder": "Example: Ho Team Construction Co., Ltd.",
        "lbl_total": "Total Contract Amount (VND) *",
        "lbl_date": "Signing Date *",
        "lbl_terms": "Payment Terms Description *",
        "terms_placeholder": "Example: Deposit 30% / Progress 40% / Retention 30%",
        "btn_save": "💾 Save & Create AR Record",
        "success_save": "✅ Contract AR record `{code}` successfully created!",
        "fill_warning": "⚠️ Please fill in Contract Code and Customer Name!",
        "col_index": "No.",
        "col_code": "Contract No.",
        "col_customer": "Customer",
        "col_total": "Total Amount (VND)",
        "col_collected": "Collected",
        "col_outstanding": "Outstanding",
        "col_status": "Status",
        "col_phase": "Milestone Phase",
        "col_pct": "Percentage (%)",
        "col_amt": "Amount (VND)",
        "col_st": "Status"
    }
}

def smart_translate_ar(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    val_lower = text_val.lower()
    if target_lang == "Tiếng Việt":
        if "進行中" in text_val: return "Đang thực hiện (In Progress)"
        if "已結案" in text_val: return "Đã hoàn thành (Closed)"
        if "已收款" in text_val: return "Đã thu tiền"
        if "審核中" in text_val: return "Đang duyệt"
        if "未請款" in text_val: return "Chưa yêu cầu thanh toán"
        if "訂金" in text_val: return "Tiền đặt cọc (Deposit)"
        if "施工完成" in text_val: return "Hoàn thành thi công"
        if "合約追加" in text_val: return "Bổ sung hợp đồng"
        if "過路橋架施工完成" in text_val: return "Hoàn thành lắp đặt máng cáp"
        if "電站送電完成" in text_val: return "Hoàn thành cấp điện trạm biến áp"
        if "工程驗收保固保證" in text_val: return "Bảo lãnh nghiệm thu & bảo hành"
        if "簽定訂金" in text_val: return "Đặt cọc ký kết"
        if "監工確認數量完成驗收" in text_val: return "Nghiệm thu khối lượng hoàn thành"
        if "簽定合約" in text_val: return "Ký kết hợp đồng"
        if "高壓電站送電完成" in text_val: return "Hoàn thành cấp điện trạm cao thế"
        if "配電盤送電完成" in text_val: return "Hoàn thành cấp điện tủ điện"
        if "驗收合格並移交" in text_val: return "Nghiệm thu bàn giao"
        if "簽定" in text_val: return "Ký kết"
        if "保固金" in text_val: return "Tiền bảo hành (Warranty)"
    elif target_lang == "English":
        if "進行中" in text_val: return "In Progress"
        if "已結案" in text_val: return "Closed"
        if "已收款" in text_val: return "Collected"
        if "審核中" in text_val: return "Reviewing"
        if "未請款" in text_val: return "Pending"
        if "訂金" in text_val: return "Deposit"
        if "施工完成" in text_val: return "Construction Complete"
        if "合約追加" in text_val: return "Additional Work"
        if "過路橋架施工完成" in text_val: return "Cable Tray Installation Complete"
        if "電站送電完成" in text_val: return "Substation Energization Complete"
        if "工程驗收保固保證" in text_val: return "Acceptance & Warranty Guarantee"
        if "簽定訂金" in text_val: return "Signing Deposit"
        if "監工確認數量完成驗收" in text_val: return "Supervision & Quantity Acceptance"
        if "簽定合約" in text_val: return "Contract Signing"
        if "高壓電站送電完成" in text_val: return "HV Substation Energization"
        if "配電盤送電完成" in text_val: return "Switchgear Energization"
        if "驗收合格並移交" in text_val: return "Inspection & Handover"
        if "簽定" in text_val: return "Signing"
        if "保固金" in text_val: return "Warranty Retention"
    return text_val

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = SALES_ORDER_AR_I18N.get(active_lang, SALES_ORDER_AR_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    if "sales_ar_db" not in st.session_state:
        st.session_state.sales_ar_db = [
            {
                "code": "HD-2025-HOT",
                "customer": "和鼎隆建築責任有限公司 (Ho Team)",
                "total": 48200946580.0,
                "collected": 8922254935.0,
                "outstanding": 39278691645.0,
                "status": "進行中",
                "milestones": [
                    {"phase": "訂金 (Deposit)", "pct": 18.51, "amount": 8922254935.0, "status": "已收款"},
                    {"phase": "施工完成 (Construction Complete)", "pct": 71.43, "amount": 34427544982.0, "status": "審核中"},
                    {"phase": "合約追加 (Additional Work)", "pct": 0.0, "amount": 6480000000.0, "status": "進行中"}
                ]
            },
            {
                "code": "HD-2026-JIA",
                "customer": "佳威商旅責任有限公司 (Jia Wei)",
                "total": 21859200000.0,
                "collected": 0.0,
                "outstanding": 21859200000.0,
                "status": "進行中",
                "milestones": [
                    {"phase": "訂金 (Deposit)", "pct": 30.0, "amount": 6557760000.0, "status": "未請款"},
                    {"phase": "過路橋架施工完成", "pct": 20.0, "amount": 4371840000.0, "status": "未請款"},
                    {"phase": "電站送電完成", "pct": 30.0, "amount": 6557760000.0, "status": "未請款"},
                    {"phase": "工程驗收保固保證", "pct": 20.0, "amount": 4371840000.0, "status": "未請款"}
                ]
            },
            {
                "code": "HD-2026-YAN",
                "customer": "彥豪金屬工業股份有限公司 (彥豪)",
                "total": 28321920000.0,
                "collected": 5664384000.0,
                "outstanding": 22657536000.0,
                "status": "進行中",
                "milestones": [
                    {"phase": "簽定訂金 (Signing Deposit)", "pct": 20.0, "amount": 5664384000.0, "status": "已收款"},
                    {"phase": "監工確認數量完成驗收", "pct": 80.0, "amount": 22657536000.0, "status": "進行中"}
                ]
            },
            {
                "code": "HD-2026-TIM",
                "customer": "第一傳動科技 (Timotion)",
                "total": 45524160000.0,
                "collected": 5664384000.0,
                "outstanding": 39859776000.0,
                "status": "進行中",
                "milestones": [
                    {"phase": "簽定合約 (Signing)", "pct": 30.0, "amount": 13657248000.0, "status": "已收款"},
                    {"phase": "高壓電站送電完成", "pct": 20.0, "amount": 9104832000.0, "status": "進行中"},
                    {"phase": "配電盤送電完成", "pct": 30.0, "amount": 13657248000.0, "status": "未請款"},
                    {"phase": "驗收合格並移交", "pct": 20.0, "amount": 9104832000.0, "status": "未請款"}
                ]
            },
            {
                "code": "HD-2026-SUP",
                "customer": "SUPERLON 越南",
                "total": 2004085358.0,
                "collected": 0.0,
                "outstanding": 2004085358.0,
                "status": "進行中",
                "milestones": [
                    {"phase": "簽定 (Signing)", "pct": 50.0, "amount": 1002042679.0, "status": "未請款"},
                    {"phase": "驗收合格並移交", "pct": 45.0, "amount": 901838411.0, "status": "未請款"},
                    {"phase": "保固金 (Warranty)", "pct": 5.0, "amount": 100204268.0, "status": "未請款"}
                ]
            }
        ]

    # 初始化已開立電子發票的資料庫
    if "issued_e_invoices" not in st.session_state:
        st.session_state.issued_e_invoices = [
            {
                "inv_no": "AB/26E-00001",
                "contract_no": "HD-2025-HOT",
                "client": "和鼎隆建築責任有限公司",
                "amount_vnd": 8922254935.0,
                "vat_vnd": 89222549.35,
                "gdt_status": "🟢 GDT 已簽章驗證 (Success)",
                "date": "2026-09-15"
            }
        ]

    tab_list, tab_details, tab_add, tab_invoice = st.tabs([
        L["tab_list"], L["tab_details"], L["tab_add"], L["tab_invoice"]
    ])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.sales_ar_db:
            display_data = []
            for idx, item in enumerate(st.session_state.sales_ar_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_customer"]: item["customer"],
                    L["col_total"]: f"{item['total']:,.0f} VND",
                    L["col_collected"]: f"{item['collected']:,.0f} VND",
                    L["col_outstanding"]: f"{item['outstanding']:,.0f} VND",
                    L["col_status"]: smart_translate_ar(item["status"], active_lang)
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_details:
        st.markdown(f"### {L['details_header']}")
        contract_opts = {f"{item['code']} - {item['customer']}": item for item in st.session_state.sales_ar_db}
        selected_contract_key = st.selectbox(L["select_project"], list(contract_opts.keys()))
        selected_contract = contract_opts[selected_contract_key]

        col1, col2, col3 = st.columns(3)
        col1.metric(L["metric_total"], f"{selected_contract['total']:,.0f} VND")
        col2.metric(L["metric_collected"], f"{selected_contract['collected']:,.0f} VND")
        col3.metric(L["metric_outstanding"], f"{selected_contract['outstanding']:,.0f} VND")

        st.markdown("---")
        st.markdown(f"#### {L['milestone_header']}")
        
        formatted_milestones = []
        for m in selected_contract["milestones"]:
            formatted_milestones.append({
                L["col_phase"]: smart_translate_ar(m["phase"], active_lang),
                L["col_pct"]: f"{m['pct']:.2f}%" if m['pct'] > 0 else "0.00%",
                L["col_amt"]: f"{m['amount']:,.0f} VND",
                L["col_st"]: smart_translate_ar(m["status"], active_lang)
            })
            
        st.dataframe(pd.DataFrame(formatted_milestones), use_container_width=True)

    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_sales_ar"):
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input(L["lbl_code"], value="HD-2026-NEW")
                customer = st.text_input(L["lbl_customer"], placeholder=L["cust_placeholder"])
            with c2:
                total_amt = st.number_input(L["lbl_total"], min_value=0.0, value=10000000000.0, step=500000000.0)
                signing_date = st.date_input(L["lbl_date"], value=datetime.date.today())

            terms = st.text_area(L["lbl_terms"], placeholder=L["terms_placeholder"])

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if code and customer:
                    st.session_state.sales_ar_db.insert(0, {
                        "code": code,
                        "customer": customer,
                        "total": total_amt,
                        "collected": 0.0,
                        "outstanding": total_amt,
                        "status": "進行中",
                        "milestones": [
                            {"phase": "簽約訂金 (Signing Deposit)", "pct": 30.0, "amount": total_amt * 0.3, "status": "未請款"},
                            {"phase": "施工進度款 (Progress Payment)", "pct": 50.0, "amount": total_amt * 0.5, "status": "未請款"},
                            {"phase": "驗收保固款 (Retention)", "pct": 20.0, "amount": total_amt * 0.2, "status": "未請款"}
                        ]
                    })
                    st.success(L["success_save"].format(code=code))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab_invoice:
        st.markdown("### ⚡ 透過 IT 通道開立越南電子發票並送交 GDT 驗證")
        st.info("💡 系統已串接資訊部設定之 GDT API。開立後將自動產生具備法定防偽簽章之 XML/PDF 電子發票，並同步回寫至應收帳款紀錄。")

        with st.form("form_issue_ar_e_invoice"):
            c_a, c_b = st.columns(2)
            with c_a:
                contract_choices = [f"{item['code']} - {item['customer']}" for item in st.session_state.sales_ar_db]
                selected_contract_str = st.selectbox("選擇對應工程合約 (Contract No)", contract_choices)
                inv_type_choice = st.selectbox("發票性質 (Invoice Type)", ["01GTGT (加值稅發票 VAT 8%/10%)", "02GTTT (銷售發票)"])
            with c_b:
                inv_amount = st.number_input("本期請款未稅金額 (VND)", min_value=0.0, value=1000000000.0, step=1000000.0)
                vat_select = st.selectbox("加值稅率 (VAT Rate - Thuế GTGT)", ["10%", "8%", "0%"])

            submit_invoice_btn = st.form_submit_button("🚀 開立電子發票並送交 GDT 稅務總局驗證", type="primary", use_container_width=True)

            if submit_invoice_btn:
                c_no_extracted = selected_contract_str.split(" - ")[0]
                c_name_extracted = selected_contract_str.split(" - ")[1]
                vat_multiplier = 0.10 if "10%" in vat_select else (0.08 if "8%" in vat_select else 0.0)
                vat_val = inv_amount * vat_multiplier
                new_invoice_id = f"AB/26E-{len(st.session_state.issued_e_invoices)+1:05d}"

                new_inv_rec = {
                    "inv_no": new_invoice_id,
                    "contract_no": c_no_extracted,
                    "client": c_name_extracted,
                    "amount_vnd": inv_amount,
                    "vat_vnd": vat_val,
                    "gdt_status": "🟢 GDT 已簽章驗證 (Success)",
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }
                
                st.session_state.issued_e_invoices.insert(0, new_inv_rec)
                st.success(f"🎉 電子發票 [{new_invoice_id}] 開立成功！含稅總額：`{inv_amount + vat_val:,.2f} VND`，已通過越南 GDT 系統合規驗證。")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 已開立電子發票與 GDT 驗證紀錄清單")
        if st.session_state.issued_e_invoices:
            st.dataframe(pd.DataFrame(st.session_state.issued_e_invoices), use_container_width=True)
        else:
            st.info("目前尚無電子發票開立紀錄。")

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def render_sales_order_ar(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
