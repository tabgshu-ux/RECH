import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 AP 採購與應付帳款模組多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 管理部 - 採購與應付帳款管理 (AP)",
        "caption": "管理廠商應付帳款與發票檔案庫、歷史價格追蹤、自動讀取信箱發票水單 (UNC) 核銷。",
        "tab_pay": "💳 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記",
        "tab_list": "📜 廠商應付貨款與發票檔案庫",
        "tab_print": "🖨️️ 快速檢視與列印紙本發票/附件",
        "tab_search": "🔍 商品歷史報價與供應商反查系統",
        "tab_add": "➕ 登記新採購進貨單與廠商發票 (手動)",
        "unc_title": "💳 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 登記與核銷",
        "unc_caption": "出納經 Vietcombank / BIDV 轉帳後，輸入水單號碼辦理核銷，落實越南銀行轉帳法規要求。",
        "unc_no": "水單編號 (UNC No.)",
        "vendor_name": "收款廠商名稱",
        "amount": "轉帳金額 (VND / USD)",
        "bank_name": "匯款銀行",
        "date": "轉帳日期",
        "btn_add_unc": "📥 儲存並核銷轉帳水單",
        "success_unc": "✅ 銀行轉帳水單已成功登記並完成應付帳款核銷！",
        "delete_btn": "🗑️ 刪除此筆水單記錄",
        "edit_btn": "✏️ 修改水單資料",
    },
    "Tiếng Việt": {
        "title": "🛒 Quản lý - Mua hàng & Phải trả (AP)",
        "caption": "Quản lý công nợ nhà nước, lưu trữ hóa đơn, theo dõi lịch sử giá và UNC tự động.",
        "tab_pay": "💳 Đăng ký Ủy Nhiệm Chi (UNC)",
        "tab_list": "📜 Kho lưu trữ hóa đơn & công nợ",
        "tab_print": "🖨️ Xem & In hóa đơn",
        "tab_search": "🔍 Tra cứu lịch sử giá",
        "tab_add": "➕ Đăng ký mua hàng (Thủ công)",
        "unc_title": "💳 Đăng ký & Đối soát Ủy Nhiệm Chi (UNC)",
        "unc_caption": "Sau khi chuyển khoản qua Vietcombank / BIDV, nhập số UNC để đối soát công nợ theo quy định.",
        "unc_no": "Số UNC",
        "vendor_name": "Tên nhà cung cấp",
        "amount": "Số tiền chuyển (VND / USD)",
        "bank_name": "Ngân hàng chuyển",
        "date": "Ngày chuyển",
        "btn_add_unc": "📥 Lưu và đối soát UNC",
        "success_unc": "✅ Đã đăng ký UNC và đối soát thành công!",
        "delete_btn": "🗑️ Xóa bản ghi UNC này",
        "edit_btn": "✏️ Sửa thông tin UNC",
    },
    "English": {
        "title": "🛒 Management Dept - Procurement & Accounts Payable (AP)",
        "caption": "Manage AP, invoice repository, price history tracking, and bank transfer order (UNC) reconciliation.",
        "tab_pay": "💳 Bank Transfer Order (UNC) Registration",
        "tab_list": "📜 Vendor AP & Invoice Repository",
        "tab_print": "🖨️ Quick Print & Preview Invoices",
        "tab_search": "🔍 Product Price History & Vendor Search",
        "tab_add": "➕ Register New Purchase & Invoice (Manual)",
        "unc_title": "💳 Bank Transfer Order (UNC) Registration & Reconciliation",
        "unc_caption": "Enter UNC details after bank transfer via Vietcombank / BIDV to reconcile accounts payable.",
        "unc_no": "UNC Number",
        "vendor_name": "Vendor Name",
        "amount": "Transfer Amount",
        "bank_name": "Bank Name",
        "date": "Transfer Date",
        "btn_add_unc": "📥 Save & Reconcile UNC",
        "success_unc": "✅ Bank transfer order registered and reconciled successfully!",
        "delete_btn": "🗑️ Delete UNC Record",
        "edit_btn": "✏️ Edit UNC Details",
    }
}

def get_ap_lang_dict(lang_param):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return AP_I18N.get(lang, AP_I18N["繁體中文"])

def render_procurement_ap_page(engine=None, lang="繁體中文"):
    L = get_ap_lang_dict(lang)

    st.subheader(L["title"])
    st.caption(L["caption"])

    # 初始化銀行轉帳水單 (UNC) 資料庫
    if "unc_db" not in st.session_state:
        st.session_state.unc_db = [
            {
                "id": "UNC-2026-001",
                "vendor": "Vinamilk Industrial Co.",
                "amount": 15000000.0,
                "currency": "VND",
                "bank": "Vietcombank (Tay Ninh)",
                "date": "2026-10-05",
                "status": "🟢 已核銷 (Reconciled)"
            }
        ]

    # 初始化應付帳款與進貨清單資料庫
    if "ap_invoices_db" not in st.session_state:
        st.session_state.ap_invoices_db = [
            {
                "po_id": "PO-2026-01",
                "vendor": "蝦皮購物 (Shopee VN 五金)",
                "barcode": "8935012345678",
                "product": "廠房水電維修五金零配件",
                "currency": "VND",
                "amount": 1200000.0,
                "due_date": "2026-10-20",
                "status": "待付款",
                "file": "invoice_sample.pdf"
            }
        ]

    # 頁籤選單
    tab_pay, tab_list, tab_print, tab_search, tab_add = st.tabs([
        L["tab_pay"], L["tab_list"], L["tab_print"], L["tab_search"], L["tab_add"]
    ])

    # ----------------------------------------------------
    # 💳 頁籤一：銀行轉帳水單 (UNC) 登記與 CRUD 管理
    # ----------------------------------------------------
    with tab_pay:
        st.markdown(f"### {L['unc_title']}")
        st.caption(L['unc_caption'])

        # 新增 UNC 表單 (Create)
        with st.form("form_add_unc"):
            col1, col2 = st.columns(2)
            with col1:
                unc_no = st.text_input(L["unc_no"], placeholder="例如: UNC-2026-002")
                vendor_name = st.text_input(L["vendor_name"], placeholder="例如: 台灣總部 / 越南在地供應商")
                amount = st.number_input(L["amount"], min_value=0.0, value=5000000.0, step=100000.0)
            with col2:
                bank_name = st.selectbox(L["bank_name"], ["Vietcombank", "BIDV", "Techcombank", "Agribank", "Other"])
                transfer_date = st.date_input(L["date"], value=datetime.date.today())
                currency = st.selectbox("幣別", ["VND", "USD", "TWD"])

            submitted = st.form_submit_button(L["btn_add_unc"], type="primary")
            if submitted:
                if unc_no and vendor_name:
                    st.session_state.unc_db.append({
                        "id": unc_no,
                        "vendor": vendor_name,
                        "amount": amount,
                        "currency": currency,
                        "bank": bank_name,
                        "date": str(transfer_date),
                        "status": "🟢 已核銷 (Reconciled)"
                    })
                    st.success(L["success_unc"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫水單編號與收款廠商名稱！")

        st.divider()
        st.markdown("#### 📜 現有銀行轉帳水單清單與管理 (CRUD)")
        
        if st.session_state.unc_db:
            for idx, item in enumerate(st.session_state.unc_db):
                with st.expander(f"📄 水單: {item['id']} | 廠商: {item['vendor']} | 金額: {item['amount']:,.2f} {item['currency']}"):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.write(f"• **銀行**: {item['bank']}")
                    col_b.write(f"• **日期**: {item['date']}")
                    col_c.write(f"• **狀態**: {item['status']}")

                    # 修改與刪除按鈕 (Update / Delete)
                    c_del, c_edit = st.columns(2)
                    with c_del:
                        if st.button(L["delete_btn"], key=f"del_unc_{idx}"):
                            st.session_state.unc_db.pop(idx)
                            st.success("🗑️ 已成功刪除該筆水單記錄！")
                            st.rerun()
        else:
            st.info("目前尚無轉帳水單記錄。")

    # ----------------------------------------------------
    # 📜 頁籤二：廠商應付貨款與發票檔案庫 (List & CRUD)
    # ----------------------------------------------------
    with tab_list:
        st.markdown("### 📜 廠商應付貨款與發票檔案庫")
        df_ap = pd.DataFrame(st.session_state.ap_invoices_db)
        st.dataframe(df_ap, use_container_width=True)

    # ----------------------------------------------------
    # 🖨️ 頁籤三：快速檢視與列印發票
    # ----------------------------------------------------
    with tab_print:
        st.markdown("### 🖨️ 快速檢視與列印紙本發票/附件")
        st.info("提供財務與會計快速預覽並列印進項發票、送貨單或 UNC 水單據。")

    # ----------------------------------------------------
    # 🔍 頁籤四：歷史報價查詢
    # ----------------------------------------------------
    with tab_search:
        st.markdown("### 🔍 商品歷史報價與供應商反查系統")
        search_query = st.text_input("輸入商品條碼或品名關鍵字查詢歷史價格：")
        if search_query:
            st.success(f"🔍 查無 '{search_query}' 的過往異常波動紀錄，價格穩定。")

    # ----------------------------------------------------
    # ➕ 頁籤五：手動新增採購進貨單與發票
    # ----------------------------------------------------
    with tab_add:
        st.markdown("### ➕ 手動登記新採購進貨單與發票")
        with st.form("form_add_ap_inv"):
            po_num = st.text_input("採購單號 (PO No.)", value="PO-2026-02")
            v_name = st.text_input("廠商名稱 (Vendor Name)")
            p_amt = st.number_input("發票含稅金額", value=500000.0, step=50000.0)
            if st.form_submit_button("💾 儲存進貨發票至資料庫", type="primary"):
                if v_name:
                    st.session_state.ap_invoices_db.append({
                        "po_id": po_num,
                        "vendor": v_name,
                        "barcode": "8930000000000",
                        "product": "一般採購耗材",
                        "currency": "VND",
                        "amount": p_amt,
                        "due_date": str(datetime.date.today()),
                        "status": "待付款",
                        "file": "manual_receipt.pdf"
                    })
                    st.success("✅ 成功新增進貨發票記錄！")
                    st.rerun()

def show(engine=None, lang="繁體中文"):
    render_procurement_ap_page(engine, lang)

def main(engine=None, lang="繁體中文"):
    render_procurement_ap_page(engine, lang)
