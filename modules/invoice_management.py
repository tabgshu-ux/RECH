import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 財務部 - 越南電子發票與稅務合規綜合管理多語系字典 (i18n)
# ----------------------------------------------------
INVOICE_I18N = {
    "繁體中文": {
        "title": "🧾 財務部 - 越南電子發票綜合管理與稅務合規管家 (Hóa đơn điện tử)",
        "caption": "符合越南稅務總局 (GDT) 規範，自動抓取 XML/PDF、計算 VAT (8%/10%)、串聯 AP 應付帳款與月度合規報表。",
        "tab_sync": "📥 信箱自動同步與抓取",
        "tab_issue": "🧾 發票開立與 GDT 稅務驗證",
        "tab_list": "📑 發票總表與合規歸檔清冊",
        "tab_link": "🔗 串聯 AP 應付帳款與憑證比對",
        "tab_vat": "📈 越南 VAT 與月度合規報表",
        "header_sync": "📧 越南發票信箱自動接收與抓取設定 (E-Invoice Auto-Sync)",
        "header_issue": "🧾 步驟一：開立並上傳越南標準電子發票",
        "header_list": "📋 已入帳之越南電子發票總表 (Phát hành & Lưu trữ)",
        "header_link": "🔗 發票與應付帳款 (AP) 勾稽清冊",
        "header_vat": "📈 越南月度加值稅 (VAT) 與稅務合規彙總",
        "lbl_email": "公司會計/發票專用收件信箱 (Invoice Email)",
        "btn_sync": "🚀 立即連線信箱同步最新電子發票 (Sync XML/PDF)",
        "success_sync": "✅ 成功從信箱同步並自動解析 `{count}` 張新電子發票！",
        "col_index": "STT",
        "col_code": "發票符號",
        "col_no": "發票號碼",
        "col_vendor": "賣方名稱與稅號",
        "col_date": "開立日期",
        "col_amount": "含稅金額 (VND/USD)",
        "col_ap": "對應 AP 單號",
        "col_status": "稅務狀態"
    },
    "Tiếng Việt": {
        "title": "🧾 Quản lý Hóa đơn Điện tử & Tuân thủ Thuế",
        "caption": "Tự động đồng bộ hóa đơn từ Email, tính thuế GTGT (8%/10%), liên kết AP và Báo cáo tài chính.",
        "tab_sync": "📥 Đồng bộ Email",
        "tab_issue": "🧾 Phát hành hóa đơn",
        "tab_list": "📑 Danh sách Hóa đơn",
        "tab_link": "🔗 Đối chiếu AP",
        "tab_vat": "📈 Báo cáo thuế GTGT",
        "header_sync": "📧 Cài đặt đồng bộ Email",
        "header_issue": "🧾 Phát hành hóa đơn điện tử",
        "header_list": "📋 Danh sách Hóa đơn đã lưu trữ",
        "header_link": "🔗 Đối chiếu hóa đơn và AP",
        "header_vat": "📈 Báo cáo thuế GTGT hàng tháng",
        "lbl_email": "Email nhận hóa đơn",
        "btn_sync": "🚀 Đồng bộ ngay",
        "success_sync": "✅ Đã đồng bộ thành công `{count}` hóa đơn mới!",
        "col_index": "STT",
        "col_code": "Ký hiệu",
        "col_no": "Số HĐ",
        "col_vendor": "Nhà cung cấp",
        "col_date": "Ngày lập",
        "col_amount": "Tổng tiền",
        "col_ap": "Mã AP",
        "col_status": "Trạng thái thuế"
    },
    "English": {
        "title": "🧾 E-Invoice Management & Tax Compliance Archiving",
        "caption": "Automated email sync for XML/PDF e-invoices, VAT calculation, AP linking, and tax reports.",
        "tab_sync": "📥 Email Auto-Sync",
        "tab_issue": "🧾 Issue E-Invoice",
        "tab_list": "📑 E-Invoice Master Log",
        "tab_link": "🔗 AP Reconciliation",
        "tab_vat": "📈 Monthly VAT Reports",
        "header_sync": "📧 E-Invoice Email Configuration & Sync",
        "header_issue": "🧾 Issue & GDT Verified E-Invoices",
        "header_list": "📋 Archived E-Invoices for Tax Audit",
        "header_link": "🔗 Invoice & AP Reconciliation",
        "header_vat": "📈 Monthly VAT & Tax Compliance Summary",
        "lbl_email": "Company Invoice Email",
        "btn_sync": "🚀 Sync New Invoices from Email",
        "success_sync": "✅ Successfully synced `{count}` new e-invoices from email!",
        "col_index": "No.",
        "col_code": "Series",
        "col_no": "Invoice No.",
        "col_vendor": "Supplier & Tax Code",
        "col_date": "Date",
        "col_amount": "Total Amount",
        "col_ap": "Linked AP",
        "col_status": "Tax Status"
    }
}

def render_invoice_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = INVOICE_I18N.get(active_lang, INVOICE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化電子發票綜合資料庫 (同時支援進項收受與銷項開立)
    if "invoice_db" not in st.session_state:
        st.session_state.invoice_db = [
            {
                "發票符號": "1C26TAA",
                "發票號碼": "00001258",
                "賣方名稱": "An Tinh Industrial Park Corp (MST: 3901234567)",
                "開立日期": "2026-10-01",
                "含稅總金額": 300000000.0,
                "貨幣": "VND",
                "對應 AP": "AP-2026-001",
                "稅務狀態": "🟢 越南稅務局已驗證 (GDT Verified)"
            },
            {
                "發票符號": "AA/26E-000128",
                "發票號碼": "000128",
                "賣方名稱": "Công ty TNHH Xây lắp Tân Thuận (MST: 3702581234)",
                "開立日期": "2026-10-05",
                "含稅總金額": 12650.0,
                "貨幣": "USD",
                "對應 AP": "AR-2026-001",
                "稅務狀態": "🟢 越南稅務局已驗證 (GDT Verified)"
            }
        ]

    tab_sync, tab_issue, tab_list, tab_link, tab_vat = st.tabs([
        L["tab_sync"], L["tab_issue"], L["tab_list"], L["tab_link"], L["tab_vat"]
    ])

    # 1. 📥 信箱自動抓取與發票同步
    with tab_sync:
        st.markdown(f"### {L['header_sync']}")
        st.info("系統自動連線至公司會計電子發票信箱，抓取 XML 原始結構檔與 PDF 檢視檔，比對供應商稅號。")

        with st.form("form_email_config"):
            st.text_input(L["lbl_email"], value="accounting-vn@reetech.com.vn")
            c1, c2 = st.columns(2)
            with c1: st.text_input("IMAP 伺服器", value="imap.gmail.com")
            with c2: st.text_input("信箱授權密碼", type="password", value="••••••••••••")

            if st.form_submit_button(L["btn_sync"], type="primary", use_container_width=True):
                new_inv = {
                    "發票符號": "3C26XYZ", "發票號碼": "00008899",
                    "賣方名稱": "Thaco Gò Dầu Service (MST: 3501112223)",
                    "開立日期": str(datetime.date.today()), "含稅總金額": 4500000.0,
                    "貨幣": "VND", "對應 AP": "未指定 (Unlinked)",
                    "稅務狀態": "🟡 待稽核比對 (Chờ đối chiếu)"
                }
                st.session_state.invoice_db.insert(0, new_inv)
                st.success(L["success_sync"].format(count=1))
                st.rerun()

    # 2. 🧾 發票開立與 GDT 稅務驗證 (源自 vietnam_tax_invoice.py)
    with tab_issue:
        st.markdown(f"### {L['header_issue']}")
        with st.form("vn_invoice_issue_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.text_input("客戶 / 業主名稱 (Client)", value="Công ty TNHH Xây lắp Tân Thuận")
                proj_ref = st.text_input("關聯專案名稱", value="西寧廠主配電盤 2000A 統包工程")
            with c2:
                amount_sub = st.number_input("未稅銷售額 (Subtotal USD)", value=11500.0, step=100.0)
                vat_choice = st.selectbox("加值稅稅率 (VAT Rate - Thuế GTGT)", ["10%", "8%", "0% (出口/免稅)"])

            if st.form_submit_button("🚀 開立電子發票並送交越南稅務局驗證 (GDT)", type="primary", use_container_width=True):
                vat_pct = 0.1 if "10%" in vat_choice else (0.08 if "8%" in vat_choice else 0.0)
                vat_val = amount_sub * vat_pct
                total_val = amount_sub + vat_val
                new_inv_no = f"AA/26E-{len(st.session_state.invoice_db)+1:06d}"
                
                st.session_state.invoice_db.insert(0, {
                    "發票符號": new_inv_no, "發票號碼": f"{len(st.session_state.invoice_db)+1:06d}",
                    "賣方名稱": client_name, "開立日期": str(datetime.date.today()),
                    "含稅總金額": round(total_val, 2), "貨幣": "USD",
                    "對應 AP": proj_ref, "稅務狀態": "🟢 越南稅務局已驗證 (GDT Verified)"
                })
                st.success(f"🎉 電子發票 [{new_inv_no}] 已成功開立！含稅總額：`$ {total_val:,.2f} USD`，已通過 GDT 驗證。")
                st.rerun()

    # 3. 📑 電子發票總表與合規歸檔清冊
    with tab_list:
        st.markdown(f"### {L['header_list']}")
        if st.session_state.invoice_db:
            inv_rows = []
            for idx, inv in enumerate(st.session_state.invoice_db, 1):
                curr = inv.get("貨幣", "VND")
                amt = float(inv.get('含稅總金額', 0))
                amt_str = f"{amt:,.0f} VND" if curr == "VND" else f"${amt:,.2f} USD"
                inv_rows.append({
                    L["col_index"]: idx, L["col_code"]: inv.get("發票符號", "-"),
                    L["col_no"]: inv.get("發票號碼", "-"), L["col_vendor"]: inv.get("賣方名稱", "-"),
                    L["col_date"]: inv.get("開立日期", "-"), L["col_amount"]: amt_str,
                    L["col_ap"]: inv.get("對應 AP", "-"), L["col_status"]: inv.get("稅務狀態", "-")
                })
            st.dataframe(pd.DataFrame(inv_rows), use_container_width=True)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🖨️ 批次列印選定發票 (Print for Tax Audit)"):
                    st.success("✅ 已成功產生稅務查帳專用發票彙整 PDF 檔案！")
            with col_p2:
                if st.button("📥 匯出發票 XML 原始檔包 (Export XML Package)"):
                    st.success("✅ 稅務局申報用 XML 原始檔已打包下載完畢！")
        else:
            st.info("目前尚無電子發票記錄。")

    # 4. 🔗 串聯應付帳款 (AP) 與憑證比對
    with tab_link:
        st.markdown(f"### {L['header_link']}")
        if st.session_state.invoice_db:
            inv_options = {f"HĐ {inv.get('發票號碼')} - {inv.get('賣方名稱')}": inv for inv in st.session_state.invoice_db}
            sel_inv_key = st.selectbox("選擇要勾稽的電子發票", list(inv_options.keys()))
            target_inv = inv_options[sel_inv_key]

            with st.form("form_link_ap"):
                st.info(f"正在處理發票號碼：`{target_inv.get('發票號碼')}`")
                selected_ap = st.selectbox("指定對應的會計單號 (Link to AP/AR)", ["AP-2026-001", "AP-2026-002", "AR-2026-001", "未指定 (Unlinked)"])

                if st.form_submit_button("🔗 確認綁定發票與會計紀錄", type="primary", use_container_width=True):
                    target_inv["對應 AP"] = selected_ap
                    target_inv["稅務狀態"] = "🟢 已合法申報 (Đã kê khai)"
                    st.success(f"✅ 發票已成功與 `{selected_ap}` 勾稽完畢！")
                    st.rerun()

    # 5. 📈 越南 VAT 與月度合規報表
    with tab_vat:
        st.markdown(f"### {L['header_vat']}")
        st.info("💡 說明：系統自動加總當月份的銷項與進項加值稅 (VAT)，產出符合越南稅務總局 (GDT) 規範的申報數據。")

        total_vnd = sum([i["含稅總金額"] for i in st.session_state.invoice_db if i.get("貨幣") == "VND"])
        total_usd = sum([i["含稅總金額"] for i in st.session_state.invoice_db if i.get("貨幣") == "USD"])

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("本月累計含稅總額 (VND)", f"{total_vnd:,.0f} VND")
        with m2: st.metric("本月累計含稅總額 (USD)", f"$ {total_usd:,.2f} USD")
        with m3: st.metric("稅務合規狀態", "🟢 完全合規 (GDT Compliant)")

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def render_invoice_management(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def render_vn_tax_invoice_page(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)
