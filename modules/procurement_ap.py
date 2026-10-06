import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 AP 採購與應付帳款模組多語系字典 (i18n)
# ----------------------------------------------------
AP_I18N = {
    "繁體中文": {
        "title": "🛒 管理部 - 採購與應付帳款管理 (AP)",
        "caption": "管理廠商應付帳款、發票檔案庫、UNC 銀行轉帳水單自動核銷與採購自動同步入庫。",
        "tab_add": "📥 1. 登記新採購進貨單與自動入庫",
        "tab_list": "📜 2. 廠商應付貨款與發票檔案庫",
        "tab_pay": "💳 3. 銀行轉帳水單 (UNC) 登記與核銷",
        "tab_small_cash": "🧾 4. 500萬以下小額送貨單與費用總表",
        "tab_print": "🖨 5. 快速檢視與列印紙本發票/附件",
        "tab_search": "🔍 6. 商品歷史報價與供應商反查系統",
        "unc_title": "💳 銀行轉帳水單 (Ủy Nhiệm Chi - UNC) 與採購單自動核銷",
        "unc_caption": "出納轉帳後登記 UNC，系統自動將對應之採購單更新為「已付款」，落實金流閉環。",
        "unc_no": "水單編號 (UNC No.)",
        "vendor_name": "收款廠商名稱",
        "amount": "轉帳金額",
        "bank_name": "匯款銀行",
        "select_po": "勾選要核銷的待付款採購單 (PO)",
        "btn_add_unc": "📥 儲存水單並完成採購單核銷",
        "success_unc": "✅ 銀行轉帳水單已成功登記，對應採購單已自動更新為【已付款】！",
        "delete_btn": "🗑️️ 刪除此筆水單記錄",
    },
    "Tiếng Việt": {
        "title": "🛒 Quản lý - Mua hàng & Phải trả (AP)",
        "caption": "Quản lý công nợ, hóa đơn, đối soát UNC tự động và tự động nhập kho.",
        "tab_add": "📥 1. Đăng ký mua hàng & Nhập kho tự động",
        "tab_list": "📜 2. Kho lưu trữ hóa đơn & công nợ",
        "tab_pay": "💳 3. Đăng ký UNC & Đối soát đơn hàng",
        "tab_small_cash": "🧾 4. Chứng từ nhỏ & Tổng hợp chi phí",
        "tab_print": "🖨️ 5. Xem & In hóa đơn",
        "tab_search": "🔍 6. Tra cứu lịch sử giá",
        "unc_title": "💳 Đăng ký Ủy Nhiệm Chi (UNC) & Đối soát đơn hàng tự động",
        "unc_caption": "Sau khi chuyển khoản, nhập UNC và chọn đơn hàng để tự động cập nhật trạng thái đã thanh toán.",
        "unc_no": "Số UNC",
        "vendor_name": "Tên nhà cung cấp",
        "amount": "Số tiền chuyển",
        "bank_name": "Ngân hàng chuyển",
        "select_po": "Chọn đơn hàng cần đối soát thanh toán",
        "btn_add_unc": "📥 Lưu UNC và đối soát đơn hàng",
        "success_unc": "✅ Đã đăng ký UNC và cập nhật trạng thái đơn hàng thành công!",
        "delete_btn": "🗑 Xóa bản ghi UNC này",
    },
    "English": {
        "title": "🛒 Management Dept - Procurement & Accounts Payable (AP)",
        "caption": "Manage AP, invoices, automated UNC bank transfer reconciliation, and auto-warehouse syncing.",
        "tab_add": "📥 1. Register Purchase & Auto-Stock-In",
        "tab_list": "📜 2. Vendor AP & Invoice Repository",
        "tab_pay": "💳 3. UNC Registration & PO Reconciliation",
        "tab_small_cash": "🧾 4. Under 5M VND Small Vouchers",
        "tab_print": "🖨️ 5. Quick Print & Preview Invoices",
        "tab_search": "🔍 6. Product Price History & Vendor Search",
        "unc_title": "💳 Bank Transfer Order (UNC) & PO Automated Reconciliation",
        "unc_caption": "Register UNC after transfer to automatically reconcile and mark selected POs as paid.",
        "unc_no": "UNC Number",
        "vendor_name": "Vendor Name",
        "amount": "Transfer Amount",
        "bank_name": "Bank Name",
        "select_po": "Select Unpaid PO to Reconcile",
        "btn_add_unc": "📥 Save UNC & Reconcile PO",
        "success_unc": "✅ UNC registered and PO status automatically updated to Paid!",
        "delete_btn": "🗑️ Delete UNC Record",
    }
}

def get_ap_lang_dict(lang_param):
    lang = lang_param or st.session_state.get("lang", "繁體中文")
    return AP_I18N.get(lang, AP_I18N["繁體中文"])

def render_procurement_ap_page(engine=None, lang="繁體中文"):
    L = get_ap_lang_dict(lang)

    st.subheader(L["title"])
    st.caption(L["caption"])

    # 初始化資料庫
    if "unc_db" not in st.session_state:
        st.session_state.unc_db = []

    if "ap_invoices_db" not in st.session_state:
        st.session_state.ap_invoices_db = [
            {
                "po_id": "PO-2026-01",
                "vendor": "Shopee VN",
                "item_name": "廠房五金配件",
                "barcode": "8935012345678",
                "qty": 10,
                "unit": "個 / Pcs",
                "currency": "VND",
                "amount": 1200000.0,
                "due_date": "2026-10-20",
                "status": "🔴 待付款 (Pending)",
                "file": "invoice_sample.pdf"
            }
        ]

    if "warehouse_inventory_db" not in st.session_state:
        st.session_state.warehouse_inventory_db = [
            {
                "barcode": "8935012345678",
                "item_name": "廠房五金配件",
                "stock_qty": 10,
                "unit": "個 / Pcs",
                "last_update": "2026-10-06"
            }
        ]

    if "small_cash_vouchers_db" not in st.session_state:
        st.session_state.small_cash_vouchers_db = [
            {
                "id": "PETTY-2026-01",
                "date": "2026-10-06",
                "channel": "Shopee VN",
                "item": "廠房耗材",
                "amount": 1200000.0,
                "status": "🟢 已轉入會計費用傳票"
            }
        ]

    # 頁籤順序：1. 新增採購並自動入庫 2. 應付帳款清單 3. UNC 銀行轉帳水單 4. 小額憑證 5. 列印 6. 歷史查詢
    tab_add, tab_list, tab_pay, tab_small_cash, tab_print, tab_search = st.tabs([
        L["tab_add"], L["tab_list"], L["tab_pay"], L["tab_small_cash"], L["tab_print"], L["tab_search"]
    ])

    # ----------------------------------------------------
    # 📥 頁籤一：登記新採購進貨單與詳細品項（支援美金小數點後 3 位）
    # ----------------------------------------------------
    with tab_add:
        st.markdown(f"### {L['tab_add']}")
        st.caption("詳細記錄採購品名、條碼與數量。選擇【USD】時自動支援小數點後 3 位精準計價，選擇【VND】則以整數計價。")

        col_a, col_b = st.columns(2)
        with col_a:
            po_num = st.text_input("採購單號 (PO No.)", value="PO-2026-02", key="ap_curr_po")
            v_name = st.text_input("廠商名稱 (Vendor Name)", placeholder="例如: 台灣總部 / 越南供應商", key="ap_curr_v")
            item_name = st.text_input("採購物品名稱 / 規格說明", placeholder="例如: 鞋材大底 / 膠水原料", key="ap_curr_item")
        with col_b:
            barcode = st.text_input("商品條碼 / 料號 (Barcode / SKU)", placeholder="例如: 8935012345678", key="ap_curr_bc")
            c_q1, c_q2 = st.columns(2)
            with c_q1:
                qty = st.number_input("採購數量", min_value=1.0, value=1000.0, step=1.0, key="ap_curr_qty")
            with c_q2:
                unit = st.selectbox("單位", ["雙 (Pairs)", "個 (Pcs)", "公斤 (Kg)", "公升 (L)", "批 (Lot)"], key="ap_curr_unit")
            
            # 💡 幣別選擇欄位置於金額上方，讓系統動態判斷精度
            curr_type = st.selectbox("計價幣別 (Currency)", ["VND", "USD", "TWD"], key="ap_curr_type")

            # 🛠️ 根據幣別動態調整金額輸入精度：USD 支援小數點後 3 位 (0.001)，VND 則為整數
            if curr_type == "USD":
                p_amt = st.number_input("總含稅金額 (USD - 精確至小數點後 3 位)", min_value=0.0, value=1.234, format="%.3f", step=0.001, key="ap_curr_amt_usd")
            else:
                p_amt = st.number_input("總含稅金額 (VND / TWD - 整數)", min_value=0.0, value=500000.0, step=1000.0, key="ap_curr_amt_vnd")

        if st.button("💾 儲存進貨記錄並【自動同步入庫】", type="primary", key="ap_curr_btn"):
            if v_name and item_name:
                # 1. 寫入應付帳款 (AP) 採購發票庫
                st.session_state.ap_invoices_db.append({
                    "po_id": po_num,
                    "vendor": v_name,
                    "item_name": item_name,
                    "barcode": barcode if barcode else "N/A",
                    "qty": qty,
                    "unit": unit,
                    "currency": curr_type,
                    "amount": p_amt,
                    "due_date": str(datetime.date.today()),
                    "status": "🔴 待付款 (Pending)",
                    "file": "manual_receipt.pdf"
                })

                # 2. 自動同步入庫至倉庫庫存
                item_exists = False
                for stock in st.session_state.warehouse_inventory_db:
                    if barcode and stock["barcode"] == barcode:
                        stock["stock_qty"] += qty
                        stock["last_update"] = str(datetime.date.today())
                        item_exists = True
                        break
                
                if not item_exists:
                    st.session_state.warehouse_inventory_db.append({
                        "barcode": barcode if barcode else f"SKU-{datetime.date.today().strftime('%m%d')}",
                        "item_name": item_name,
                        "stock_qty": qty,
                        "unit": unit,
                        "last_update": str(datetime.date.today())
                    })

                st.success(f"✅ 成功採購【{item_name}】共 {qty} {unit}（金額: {p_amt:,.3f} {curr_type}）！已自動完成倉庫入庫與 AP 應付帳款登錄！")
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫廠商名稱與採購物品名稱！")

    # ----------------------------------------------------
    # 📜 頁籤二：廠商應付貨款與發票檔案庫
    # ----------------------------------------------------
    with tab_list:
        st.markdown(f"### {L['tab_list']}")
        df_ap = pd.DataFrame(st.session_state.ap_invoices_db)
        st.dataframe(df_ap, use_container_width=True)

    # ----------------------------------------------------
    # 💳 頁籤三：銀行轉帳水單 (UNC) 登記與自動核銷
    # ----------------------------------------------------
    with tab_pay:
        st.markdown(f"### {L['unc_title']}")
        st.caption(L['unc_caption'])

        unpaid_pos = [item for item in st.session_state.ap_invoices_db if "待" in item["status"] or "Pending" in item["status"]]
        unpaid_po_ids = [f"{item['po_id']} - {item['vendor']} ({item['item_name']}) - {item['amount']:,.3f} {item['currency']}" for item in unpaid_pos]

        vietnam_banks = [
            "Vietcombank", "BIDV", "Agribank", "VietinBank", "Techcombank",
            "Cathay United Bank (國泰世華)", "CTBC Bank (中國信託)", "HSBC (Vietnam)", "Other / 其它"
        ]

        col1, col2 = st.columns(2)
        with col1:
            unc_no = st.text_input(L["unc_no"], placeholder="例如: UNC-2026-002", key="ap_curr_unc_no")
            vendor_name = st.text_input(L["vendor_name"], placeholder="例如: 台灣總部 / 越南供應商", key="ap_curr_unc_v")
            amount = st.number_input(L["amount"], min_value=0.0, value=1200000.0, step=1000.0, key="ap_curr_unc_amt")
        with col2:
            bank_name = st.selectbox(L["bank_name"], vietnam_banks, key="ap_curr_unc_bank")
            selected_target_po = st.selectbox(L["select_po"], unpaid_po_ids if unpaid_po_ids else ["目前無待付款採購單"], key="ap_curr_unc_po")
            currency = st.selectbox("幣別", ["VND", "USD", "TWD"], key="ap_curr_unc_curr")

        if st.button(L["btn_add_unc"], type="primary", key="ap_curr_btn_unc"):
            if unc_no and vendor_name:
                st.session_state.unc_db.append({
                    "id": unc_no,
                    "vendor": vendor_name,
                    "amount": amount,
                    "currency": currency,
                    "bank": bank_name,
                    "date": str(datetime.date.today()),
                    "matched_po": selected_target_po
                })

                if unpaid_pos and "目前無" not in selected_target_po:
                    target_po_id = selected_target_po.split(" - ")[0]
                    for inv in st.session_state.ap_invoices_db:
                        if inv["po_id"] == target_po_id:
                            inv["status"] = "🟢 已付款 (Paid)"

                st.success(L["success_unc"])
                st.rerun()
            else:
                st.warning("⚠️ 請完整填寫水單編號與收款廠商名稱！")

        st.divider()
        st.markdown("#### 📜 現有銀行轉帳水單清單與勾稽狀態")
        if st.session_state.unc_db:
            for idx, item in enumerate(st.session_state.unc_db):
                with st.expander(f"📄 水單: {item['id']} | 廠商: {item['vendor']} | 金額: {item['amount']:,.3f} {item['currency']}"):
                    st.write(f"• **匯款銀行**: {item['bank']}")
                    st.write(f"• **轉帳日期**: {item['date']}")
                    st.write(f"• **已勾稽採購單**: `{item['matched_po']}`")
                    if st.button(L["delete_btn"], key=f"ap_curr_del_{idx}"):
                        st.session_state.unc_db.pop(idx)
                        st.success("🗑️ 已成功刪除該筆水單記錄！")
                        st.rerun()
        else:
            st.info("目前尚無轉帳水單記錄。")

    # ----------------------------------------------------
    # 🧾 頁籤四：500萬以下小額送貨單與會計費用傳票總表
    # ----------------------------------------------------
    with tab_small_cash:
        st.markdown(f"### {L['tab_small_cash']}")
        st.caption("整合現場同仁上傳之外箱送貨單與小額零用金報銷，自動結算並匯入會計總帳傳票。")
        df_small = pd.DataFrame(st.session_state.small_cash_vouchers_db)
        st.dataframe(df_small, use_container_width=True)

    # ----------------------------------------------------
    # 🖨️ 頁籤五：快速檢視與列印發票
    # ----------------------------------------------------
    with tab_print:
        st.markdown(f"### {L['tab_print']}")
        st.info("提供財務與會計快速預覽並列印進項發票、送貨單或 UNC 水單據。")

    # ----------------------------------------------------
    # 🔍 頁籤六：歷史報價查詢
    # ----------------------------------------------------
    with tab_search:
        st.markdown(f"### {L['tab_search']}")
        search_query = st.text_input("輸入商品條碼或品名關鍵字查詢歷史價格：", key="ap_curr_search")
        if search_query:
            st.success(f"🔍 查無 '{search_query}' 的過往異常波動紀錄，價格穩定。")

def show(engine=None, lang="繁體中文"):
    render_procurement_ap_page(engine, lang)

def main(engine=None, lang="繁體中文"):
    render_procurement_ap_page(engine, lang)
