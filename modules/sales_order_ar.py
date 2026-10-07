import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 應收帳款與工程對帳管理模組多語系字典 (i18n)
# ----------------------------------------------------
SALES_ORDER_AR_I18N = {
    "繁體中文": {
        "title": "📋 財務部 - 工程專案應收帳款 (AR) 與對帳管理中心",
        "caption": "依據裕豐電機工業 2026 年工程請款對帳單（和鼎隆、佳威、彥豪、第一傳動 Timotion、聚苯、Superlon 等），管理合約總額、分期請款百分比、已開立發票與未收款追蹤。",
        "tab_list": "📑 專案應收帳款總表與對帳清冊",
        "tab_details": "📊 各大工程合約分項請款與進度",
        "tab_add": "➕ 新增工程合約與應收帳款 (AR)",
        "table_header": "📋 裕豐電機工業 2026 跨國工程應收帳款總覽",
        "no_records": "目前無應收帳款紀錄。",
        "details_header": "🔍 選擇工程專案檢視詳細請款條件與對帳進度",
        "select_project": "選擇工程專案合約 *",
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
        "col_status": "對帳狀態"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Tài chính - Quản lý Phải thu (AR) & Đối chiếu Hợp đồng",
        "caption": "Quản lý tổng giá trị hợp đồng, tỷ lệ thanh toán theo giai đoạn, hóa đơn đã mở và theo dõi công nợ cho các dự án 2026.",
        "tab_list": "📑 Danh sách Phải thu Dự án & Đối chiếu",
        "tab_details": "📊 Chi tiết Thanh toán theo Hợp đồng",
        "tab_add": "➕ Thêm Hợp đồng & Khoản phải thu (AR)",
        "table_header": "📋 Tổng quan Công nợ Phải thu Dự án 2026",
        "no_records": "Hiện không có bản ghi phải thu nào.",
        "details_header": "🔍 Chọn dự án để xem điều kiện thanh toán chi tiết",
        "select_project": "Chọn dự án hợp đồng *",
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
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "📋 Finance - Engineering AR & Contract Billing Center",
        "caption": "Manage contract amounts, staging percentages, invoiced amounts, and outstanding receivables for 2026 projects.",
        "tab_list": "📑 Project AR & Reconciliation List",
        "tab_details": "📊 Contract Staging & Milestone Details",
        "tab_add": "➕ Register New Engineering Contract (AR)",
        "table_header": "📋 2026 Engineering Accounts Receivable Overview",
        "no_records": "No accounts receivable records found.",
        "details_header": "🔍 Select Contract to View Milestone Details & Status",
        "select_project": "Select Contract Project *",
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
        "col_status": "Status"
    }
}

def smart_translate_ar(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    val_lower = text_val.lower()
    if target_lang == "Tiếng Việt":
        if "進行中" in text_val: return "Đang thực hiện (In Progress)"
        if "已結案" in text_val: return "Đã hoàn thành (Closed)"
    elif target_lang == "English":
        if "進行中" in text_val: return "In Progress"
        if "已結案" in text_val: return "Closed"
    return text_val

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = SALES_ORDER_AR_I18N.get(active_lang, SALES_ORDER_AR_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化 2026 工程請款對帳單資料庫（對應上傳之 2026年工程請款對帳單明細.xls）
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

    tab_list, tab_details, tab_add = st.tabs([
        L["tab_list"], L["tab_details"], L["tab_add"]
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
        col1.metric("合約總金額 (Total Contract)", f"{selected_contract['total']:,.0f} VND")
        col2.metric("已收款金額 (Collected)", f"{selected_contract['collected']:,.0f} VND")
        col3.metric("未收款總計 (Outstanding)", f"{selected_contract['outstanding']:,.0f} VND")

        st.markdown("---")
        st.markdown("#### 📑 分期請款進度與對帳明細 (Milestone Details)")
        milestones_df = pd.DataFrame(selected_contract["milestones"])
        st.dataframe(milestones_df, use_container_width=True)

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

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def render_sales_order_ar(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
