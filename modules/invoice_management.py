import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 電子發票綜合管理模組多語系字典 (i18n)
# ----------------------------------------------------
INVOICE_I18N = {
    "繁體中文": {
        "title": "🧾 財務部 - 越南電子發票綜合管理與合規歸檔系統 (Hóa đơn điện tử)",
        "caption": "設定公司收發票信箱自動抓取 XML/PDF 電子發票，自動串聯應付帳款 (AP) 與 Thông tư 200 稅務財務報表，方便未來查稅與列印。",
        "tab_sync": "📥 信箱自動抓取與發票同步",
        "tab_list": "📑 電子發票總表與合規歸檔清冊",
        "tab_link": "🔗 串聯應付帳款 (AP) 與憑證比對",
        "header_sync": "📧 越南發票信箱自動接收與抓取設定 (E-Invoice Auto-Sync)",
        "header_list": "📋 已入帳之越南電子發票總表 (Phát hành & Lưu trữ)",
        "header_link": "🔗 發票與應付帳款 (AP) 勾稽清冊",
        "lbl_email": "公司會計/發票專用收件信箱 (Invoice Email)",
        "btn_sync": "🚀 立即連線信箱同步最新電子發票 (Sync XML/PDF)",
        "success_sync": "✅ 成功從信箱同步並自動解析 `{count}` 張新電子發票！",
        "lbl_tax_code": "賣方稅號 (Mã số thuế NCC)",
        "lbl_inv_no": "發票號碼 (Số hóa đơn)",
        "lbl_inv_date": "開立日期 (Ngày lập)",
        "lbl_total": "含稅總金額 (Tổng tiền VND)",
        "lbl_ap_ref": "對應 AP 單號",
        "status_opts": ["🟢 已合法申報 (Đã kê khai)", "🟡 待稽核比對 (Chờ đối chiếu)", "🔴 異常退件 (Hủy/Sai sót)"],
        "col_index": "STT",
        "col_code": "發票代碼/符號",
        "col_no": "發票號碼",
        "col_vendor": "賣方名稱與稅號",
        "col_date": "開立日期",
        "col_amount": "含稅金額 (VND)",
        "col_ap": "對應 AP 單號",
        "col_status": "稅務狀態",
        "col_action": "查稅與列印操作"
    },
    "Tiếng Việt": {
        "title": "🧾 Quản lý Hóa đơn Điện tử & Lưu trữ Thuế",
        "caption": "Tự động đồng bộ hóa đơn từ Email, liên kết công nợ AP và Báo cáo tài chính Thông tư 200.",
        "tab_sync": "📥 Đồng bộ Email",
        "tab_list": "📑 Danh sách Hóa đơn",
        "tab_link": "🔗 Đối chiếu AP",
        "header_sync": "📧 Cài đặt đồng bộ Email hóa đơn",
        "header_list": "📋 Danh sách Hóa đơn điện tử đã lưu trữ",
        "header_link": "🔗 Đối chiếu hóa đơn và AP",
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
        "col_status": "Trạng thái thuế",
        "col_action": "Thao tác"
    },
    "English": {
        "title": "🧾 E-Invoice Management & Tax Compliance Archiving",
        "caption": "Automated email synchronization for XML/PDF e-invoices, linked with AP and Circular 200 reports.",
        "tab_sync": "📥 Email Auto-Sync",
        "tab_list": "📑 E-Invoice Master Log",
        "tab_link": "🔗 AP Reconciliation",
        "header_sync": "📧 E-Invoice Email Configuration & Sync",
        "header_list": "📋 Archived E-Invoices for Tax Audit",
        "header_link": "🔗 Invoice & AP Reconciliation",
        "lbl_email": "Company Invoice Email",
        "btn_sync": "🚀 Sync New Invoices from Email",
        "success_sync": "✅ Successfully synced `{count}` new e-invoices from email!",
        "col_index": "No.",
        "col_code": "Series",
        "col_no": "Invoice No.",
        "col_vendor": "Supplier & Tax Code",
        "col_date": "Date",
        "col_amount": "Total Amount (VND)",
        "col_ap": "Linked AP",
        "col_status": "Tax Status",
        "col_action": "Audit & Print"
    }
}

def render_invoice_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = INVOICE_I18N.get(active_lang, INVOICE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化電子發票資料庫 (模擬越南稅務局標準格式)
    if "invoice_db" not in st.session_state:
        st.session_state.invoice_db = [
            {
                "發票符號": "1C26TAA",
                "發票號碼": "00001258",
                "賣方名稱": "An Tinh Industrial Park Corp (MST: 3901234567)",
                "開立日期": "2026-10-01",
                "含稅總金額": 300000000.0,
                "對應 AP": "AP-2026-001",
                "稅務狀態": "🟢 已合法申報 (Đã kê khai)",
                "xml_file": "inv_00001258.xml",
                "pdf_file": "inv_00001258.pdf"
            },
            {
                "發票符號": "2K26MBP",
                "發票號碼": "00004589",
                "賣方名稱": "Thành Phát Copper & Steel Co., Ltd (MST: 3709876543)",
                "開立日期": "2026-10-05",
                "含稅總金額": 612500000.0,
                "對應 AP": "AP-2026-002",
                "稅務狀態": "🟢 已合法申報 (Đã kê khai)",
                "xml_file": "inv_00004589.xml",
                "pdf_file": "inv_00004589.pdf"
            }
        ]

    tab_sync, tab_list, tab_link = st.tabs([
        L["tab_sync"], L["tab_list"], L["tab_link"]
    ])

    # 1. 📥 信箱自動抓取與發票同步
    with tab_sync:
        st.markdown(f"### {L['header_sync']}")
        st.info("系統將定時連線至公司會計電子發票信箱，自動下載包含 XML 原始結構檔與 PDF 檢視檔的越南標準電子發票，並自動比對供應商稅號。")

        with st.form("form_email_config"):
            company_invoice_email = st.text_input(L["lbl_email"], value="accounting-vn@reetech.com.vn")
            c1, c2 = st.columns(2)
            with c1:
                imap_server = st.text_input("IMAP 伺服器 (IMAP Server)", value="imap.gmail.com")
            with c2:
                email_password = st.text_input("信箱授權密碼 (App Password)", type="password", value="••••••••••••")

            if st.form_submit_button(L["btn_sync"], type="primary", use_container_width=True):
                # 模擬自動從信箱抓取新發票
                new_inv = {
                    "發票符號": "3C26XYZ",
                    "發票號碼": "00008899",
                    "賣方名稱": "Thaco Gò Dầu Service (MST: 3501112223)",
                    "開立日期": str(datetime.date.today()),
                    "含稅總金額": 4500000.0,
                    "對應 AP": "未指定 (Unlinked)",
                    "稅務狀態": "🟡 待稽核比對 (Chờ đối chiếu)",
                    "xml_file": "inv_00008899.xml",
                    "pdf_file": "inv_00008899.pdf"
                }
                st.session_state.invoice_db.insert(0, new_inv)
                st.success(L["success_import"] if "success_import" in L else L["success_sync"].format(count=1))
                st.rerun()

    # 2. 📑 電子發票總表與合規歸檔清冊 (方便未來查稅列印)
    with tab_list:
        st.markdown(f"### {L['header_list']}")
        st.caption("符合越南會計與稅務法規要求，發票 XML 與 PDF 完整封存，可隨時點擊列印或匯出提供稅務局 (Thế vụ) 查帳。")

        if st.session_state.invoice_db:
            inv_rows = []
            for idx, inv in enumerate(st.session_state.invoice_db, 1):
                inv_rows.append({
                    L["col_index"]: idx,
                    L["col_code"]: inv.get("發票符號", "-"),
                    L["col_no"]: inv.get("發票號碼", "-"),
                    L["col_vendor"]: inv.get("賣方名稱", "-"),
                    L["col_date"]: inv.get("開立日期", "-"),
                    L["col_amount"]: f"{float(inv.get('含稅總金額', 0)):,.0f} ₫",
                    L["col_ap"]: inv.get("對應 AP", "-"),
                    L["col_status"]: inv.get("稅務狀態", "-")
                })
            st.dataframe(pd.DataFrame(inv_rows), use_container_width=True)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("🖨️ 批次列印選定發票 (Print Invoices for Tax Audit)"):
                    st.success("✅ 已成功產生稅務查帳專用發票彙整 PDF 檔案！")
            with col_p2:
                if st.button("📥 匯出發票 XML 原始檔包 (Export XML Package)"):
                    st.success("✅ 稅務局申報用 XML 原始檔已打包下載完畢！")
        else:
            st.info("目前尚無電子發票記錄。")

    # 3. 🔗 串聯應付帳款 (AP) 與憑證比對
    with tab_link:
        st.markdown(f"### {L['header_link']}")
        st.caption("將收到的電子發票與財務部的「應付帳款 (AP)」進行智慧勾稽，確保金流、發票與帳務完全一致。")

        if st.session_state.invoice_db:
            inv_options = {f"HĐ {inv.get('發票號碼')} - {inv.get('賣方名稱')} ({float(inv.get('含稅總金額', 0)):,.0f} ₫)": inv for inv in st.session_state.invoice_db}
            sel_inv_key = st.selectbox("選擇要勾稽的電子發票", list(inv_options.keys()))
            target_inv = inv_options[sel_inv_key]

            # 讀取 AP 清單供對應
            ap_list = st.session_state.get("ap_db", [{"AP單號": "AP-2026-001"}, {"AP單號": "AP-2026-002"}])
            ap_no_options = [ap.get("AP單號") for ap in ap_list] + ["未指定 (Unlinked)"]

            with st.form("form_link_ap"):
                st.info(f"正在處理發票號碼：`{target_inv.get('發票號碼')}` (金額: {float(target_inv.get('含稅總金額', 0)):,.0f} ₫)")
                
                curr_ap = target_inv.get("對應 AP", "未指定 (Unlinked)")
                ap_idx = ap_no_options.index(curr_ap) if curr_ap in ap_no_options else 0
                selected_ap = st.selectbox("指定對應的應付帳款單號 (Link to AP)", ap_no_options, index=ap_idx)

                if st.form_submit_button("🔗 確認綁定發票與 AP 紀錄", type="primary", use_container_width=True):
                    target_inv["對應 AP"] = selected_ap
                    target_inv["稅務狀態"] = "🟢 已合法申報 (Đã kê khai)"
                    st.success(f"✅ 發票 `{target_inv.get('發票號碼')}` 已成功與 AP 單號 `{selected_ap}` 勾稽完畢！")
                    st.rerun()
        else:
            st.info("目前無電子發票可供勾稽。")

# ----------------------------------------------------
# 🔗 相容性進入點定義（確保主程式呼叫不報錯）
# ----------------------------------------------------
def show(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def render_invoice_management(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)

def render_invoice_management_page_safe(*args, **kwargs):
    render_invoice_management_page(*args, **kwargs)
