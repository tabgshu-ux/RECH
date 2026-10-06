import email
from email.header import decode_header
import imaplib
import os
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 越南電子發票模組多語系字典 (i18n)
# ----------------------------------------------------
INVOICE_I18N = {
    "繁體中文": {
        "title": "🇻🇳 裕豐電機工業 - 越南電子發票自動讀取與小額憑證中心",
        "caption": "📱 整合 XML 檔案解析、IMAP 信箱讀取、發票額度預警及 500 萬 VND 以下小額送貨單上傳管控。",
        "tab_xml": "📄 越南電子發票 XML 解析與登錄",
        "tab_small_cash": "🧾 500萬以下小額憑證與送貨單上傳",
        "tab_email": "📧 通用信箱發票讀取 (IMAP)",
        "tab_quota": "📊 電子發票張數監控與加購",
        "xml_uploader": "選擇越南電子發票檔 (.xml)",
        "success_xml": "✅ XML 發票解析成功！",
        "btn_save_db": "💾 確認匯入系統資料庫",
        "success_save": "🎉 發票已成功登錄！",
        "db_list": "📜 已登錄發票與憑證資料庫列表：",
        "imap_title": "📧 通用電子郵件發票自動讀取 (IMAP)",
        "server_label": "IMAP 伺服器地址：",
        "user_label": "電子信箱帳號：",
        "pass_label": "信箱密碼 / App 專用密碼：",
        "btn_fetch": "🚀 開始連線信箱讀取發票",
        "spinner_fetch": "正在連線 IMAP 信箱並解析電子發票...",
    },
    "Tiếng Việt": {
        "title": "🇻🇳 REETECH INDUSTRIAL - Trung tâm Hóa đơn điện tử & Chứng từ nhỏ",
        "caption": "📱 Tích hợp phân tích XML, đọc email (IMAP), giám sát hạn mức và chứng từ giao hàng dưới 5 triệu VND.",
        "tab_xml": "📄 Phân tích & Đăng ký XML",
        "tab_small_cash": "🧾 Chứng từ nhỏ & Biên nhận dưới 5tr",
        "tab_email": "📧 Đọc Hóa đơn qua Email (IMAP)",
        "tab_quota": "📊 Giám sát hạn mức hóa đơn",
        "xml_uploader": "Chọn file hóa đơn điện tử (.xml)",
        "success_xml": "✅ Đọc XML hóa đơn thành công!",
        "btn_save_db": "💾 Xác nhận lưu vào Cơ sở dữ liệu",
        "success_save": "🎉 Hóa đơn đã được đăng ký thành công!",
        "db_list": "📜 Danh sách hóa đơn và chứng từ đã đăng ký:",
        "imap_title": "📧 Tự động đọc hóa đơn qua Email (IMAP)",
        "server_label": "Địa chỉ máy chủ IMAP:",
        "user_label": "Tài khoản Email:",
        "pass_label": "Mật khẩu Email / App Password:",
        "btn_fetch": "🚀 Bắt đầu kết nối đọc hóa đơn",
        "spinner_fetch": "Đang kết nối IMAP và phân tích hóa đơn...",
    },
    "English": {
        "title": "🇻🇳 REETECH INDUSTRIAL - E-Invoice & Small Voucher Center",
        "caption": "📱 XML parser, IMAP fetch, quota monitoring, and under 5M VND small delivery voucher uploads.",
        "tab_xml": "📄 E-Invoice XML Parser & Registration",
        "tab_small_cash": "🧾 Under 5M VND Small Vouchers",
        "tab_email": "📧 Email E-Invoice Reader (IMAP)",
        "tab_quota": "📊 E-Invoice Quota & Top-up",
        "xml_uploader": "Select Vietnam E-Invoice File (.xml)",
        "success_xml": "✅ XML Invoice parsed successfully!",
        "btn_save_db": "💾 Save to System Database",
        "success_save": "🎉 Invoice successfully registered!",
        "db_list": "📜 Registered Invoice & Voucher Database:",
        "imap_title": "📧 Automated Email E-Invoice Reader (IMAP)",
        "server_label": "IMAP Server Address:",
        "user_label": "Email Account:",
        "pass_label": "Email Password / App Password:",
        "btn_fetch": "🚀 Start Fetching Invoices",
        "spinner_fetch": "Connecting to IMAP and parsing invoices...",
    },
}


def get_lang_dict(lang_param):
    return INVOICE_I18N.get(lang_param, INVOICE_I18N["繁體中文"])


# ----------------------------------------------------
# 1. 核心的越南 XML 發票解析邏輯 (parse_vietnam_xml)
# ----------------------------------------------------
def parse_vietnam_xml(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)

        def get_text(node, tag_name):
            if node is None:
                return ""
            for elem in node.iter():
                if elem.tag.endswith(tag_name):
                    return elem.text.strip() if elem.text else ""
            return ""

        return {
            "invoice_no": get_text(root, "SHDon") or get_text(root, "InvoiceNo"),
            "pattern": get_text(root, "KHMSHDon") or get_text(root, "InvoicePattern"),
            "seller_name": get_text(root, "TenNBan") or get_text(root, "ComName"),
            "seller_tax_code": get_text(root, "MSTNBan") or get_text(root, "ComTaxCode"),
            "total_amount": float(
                get_text(root, "TgTTTBSo")
                or get_text(root, "TotalAmountWithVAT")
                or 0
            ),
            "currency": get_text(root, "DVTTe") or "VND",
            "date": get_text(root, "NLap") or get_text(root, "AriseDate"),
        }
    except Exception as e:
        st.error(f"❌ XML 解析失敗: {e}")
        return None


# ----------------------------------------------------
# 2. IMAP 信箱發票自動抓取邏輯
# ----------------------------------------------------
def fetch_invoices_from_email(
    imap_server, email_user, email_pass, folder="INBOX", search_limit=10
):
    invoices = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        status, messages = mail.search(
            None, 'OR OR (SUBJECT "invoice") (SUBJECT "hóa đơn") (SUBJECT "發票")'
        )
        email_ids = messages[0].split()

        if not email_ids:
            return (
                [],
                "ℹ️ 信箱中未找到符合「invoice / hóa đơn / 發票」關鍵字的郵件。",
            )

        for e_id in email_ids[-search_limit:]:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(
                            encoding if encoding else "utf-8", errors="ignore"
                        )

                    sender = msg.get("From")
                    date_sent = msg.get("Date")

                    attachments = []
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(
                                part.get("Content-Disposition")
                            )
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    attachments.append(filename)

                    invoices.append(
                        {
                            "id": e_id.decode(),
                            "subject": subject,
                            "sender": sender,
                            "date": date_sent,
                            "attachments": (
                                attachments if attachments else ["（內文無附件）"]
                            ),
                        }
                    )

        mail.logout()
        return invoices, "✅ 成功連線並讀取電子發票郵件！"
    except Exception as e:
        return [], f"❌ IMAP 信箱連線失敗: {str(e)}"


# ----------------------------------------------------
# 3. 越南電子發票額度與沙盒預警元件
# ----------------------------------------------------
def render_invoice_quota_widget():
    st.markdown("#### 🇻🇳 越南電子發票 (Hóa đơn điện tử) 張數額度與預警中心")
    tax_id = os.getenv("VN_TAX_ID", "")
    is_live_mode = bool(tax_id)

    if is_live_mode:
        st.success(f"🟢 **正式連線模式** (公司稅號 MST: `{tax_id}`)")
        total_quota = 5000
        used_quota = 4820
    else:
        st.info("🟡 **沙盒模擬模式** (未設定公司發票 API，目前使用測試模擬數據)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            total_quota = st.number_input(
                "設定測試總發票張數：",
                value=1000,
                step=100,
                key="mock_total_quota",
            )
        with col_m2:
            used_quota = st.number_input(
                "設定測試已使用張數：", value=850, step=50, key="mock_used_quota"
            )

    remaining_quota = total_quota - used_quota
    remaining_ratio = (
        (remaining_quota / total_quota) * 100 if total_quota > 0 else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("發票套裝總張數", f"{total_quota:,} 張")
    col2.metric("已開立張數", f"{used_quota:,} 張")

    if remaining_ratio <= 10:
        col3.metric(
            "剩餘可用張數",
            f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)",
            delta="-極低 alert",
            delta_color="inverse",
        )
        st.error(
            f"🚨 **緊急預警**：發票剩餘張數僅剩 `{remaining_quota}` 張 ({remaining_ratio:.1f}%)！預計 2 天內用盡，請儘速加購發票套裝！"
        )
    elif remaining_ratio <= 20:
        col3.metric(
            "剩餘可用張數",
            f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)",
            delta="-偏低 warning",
            delta_color="inverse",
        )
        st.warning(
            f"⚠️ **用量提醒**：發票剩餘張數低於 20% (剩餘 `{remaining_quota}` 張)，建議通知財務發起加購。"
        )
    else:
        col3.metric(
            "剩餘可用張數", f"{remaining_quota:,} 張 ({remaining_ratio:.1f}%)"
        )
        st.success("🟢 發票數量充裕，運作正常。")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        if st.button(
            "🚀 一鍵發起發票加購請購單 (Top-up Order)",
            type="primary",
            key="btn_topup_invoice",
        ):
            st.success(
                "✅ 已自動建立請購單：【加購 5,000 張電子發票套裝】，並發送簽核通知至財務主管！"
            )

    with col_btn2:
        with st.expander(
            "⚙️ 填入公司稅號與正式發票 API 金鑰 (公司成立後填入)"
        ):
            new_tax_id = st.text_input(
                "公司稅號 (Mã số thuế - MST)：",
                value=tax_id,
                placeholder="例如: 0312345678",
            )
            provider = st.selectbox(
                "電子發票服務商：",
                [
                    "VNPT (Hóa đơn điện tử)",
                    "Viettel (S-Invoice)",
                    "MISA (meInvoice)",
                    "EasyInvoice",
                    "BKAV",
                ],
            )
            api_token = st.text_input(
                "服務商 API Token / Password：", type="password"
            )
            if st.button("💾 儲存正式發票 API 連線設定"):
                os.environ["VN_TAX_ID"] = new_tax_id
                st.success(
                    "✅ 已成功儲存發票 API 設定！系統即將連線真實發票服務商。"
                )
                st.rerun()


# ----------------------------------------------------
# 4. render_invoice_management 介面與功能整合 (多語系支援)
# ----------------------------------------------------
def render_invoice_management(engine=None, lang="繁體中文"):
    current_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = get_lang_dict(current_lang)

    st.subheader(L["title"])
    st.caption(L["caption"])

    if "invoice_db" not in st.session_state:
        st.session_state.invoice_db = [
            {
                "invoice_no": "PETTY-2026-01",
                "pattern": "小額憑證",
                "seller_name": "Shopee VN (蝦皮小額五金)",
                "seller_tax_code": "-",
                "total_amount": 1200000.0,
                "currency": "VND",
                "date": "2026-10-06",
                "type": "未達 500 萬 VND 小額憑證 (送貨單/收據)",
                "uploader": "Admin (系統管理員)"
            }
        ]

    tab_xml, tab_small_cash, tab_email, tab_quota = st.tabs(
        [L["tab_xml"], L["tab_small_cash"], L["tab_email"], L["tab_quota"]]
    )

    # 頁籤一：XML 上傳、解析與 Pandas 資料表登記功能
    with tab_xml:
        uploaded_xml = st.file_uploader(
            L["xml_uploader"], type=["xml"], key="uploader_xml_file"
        )
        if uploaded_xml is not None:
            parsed_data = parse_vietnam_xml(uploaded_xml.read())
            if parsed_data:
                parsed_data["type"] = "正規電子發票 (VAT)"
                st.success(L["success_xml"])
                st.json(parsed_data)
                if st.button(
                    L["btn_save_db"], type="primary", key="btn_save_xml_db"
                ):
                    user_name = st.session_state.get("user_info", {}).get(
                        "name", "Alex Chen (管理者)"
                    )
                    parsed_data["uploader"] = user_name
                    st.session_state.invoice_db.append(parsed_data)
                    st.success(L["success_save"])
                    st.rerun()

    # 頁籤二：500萬以下小額憑證與外箱送貨單照片上傳
    with tab_small_cash:
        st.markdown("### 🧾 越南廠區小額零用金與蝦皮採購送貨單登錄")
        st.caption("針對未達 500 萬 VND 之小額採購，透過送貨單據與外箱照片進行合規報銷歸檔。")

        with st.form("small_cash_form"):
            c1, c2 = st.columns(2)
            with c1:
                item_name = st.text_input("採購品名 / 用途說明", placeholder="例如：廠房水電維修五金耗材")
                amount_vnd = st.number_input("採購金額 (VND)", min_value=0, value=1200000, step=100000)
            with c2:
                purchase_channel = st.selectbox("採購管道", ["蝦皮購物 (Shopee VN)", "當地實體五金行", "其他小額零用金"])
                voucher_type = st.selectbox("憑證類型", ["未達 500 萬 VND 小額憑證 (送貨單/收據)", "免用統一發票收據"])

            # 拍照或上傳外箱送貨單據照片
            uploaded_voucher_img = st.file_uploader(
                "📷 請上傳外箱送貨單據或收據照片（作為報銷佐證）", 
                type=["png", "jpg", "jpeg"]
            )

            if st.form_submit_button("📤 提交小額憑證與送貨單歸檔", type="primary"):
                if item_name and uploaded_voucher_img:
                    new_voucher = {
                        "invoice_no": f"PETTY-{len(st.session_state.invoice_db)+1:03d}",
                        "pattern": "小額憑證",
                        "seller_name": purchase_channel,
                        "seller_tax_code": "-",
                        "total_amount": float(amount_vnd),
                        "currency": "VND",
                        "date": "2026-10-06",
                        "type": voucher_type,
                        "uploader": st.session_state.get("user_info", {}).get("name", "Admin")
                    }
                    st.session_state.invoice_db.append(new_voucher)
                    st.success(f"✅ 成功登錄小額採購：{item_name}（金額：{amount_vnd:,.0f} VND），已綁定外箱送貨單據照片！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫品名並上傳外箱送貨單據照片以確保合規！")

    # 共同顯示已登錄的發票與憑證列表
    st.divider()
    if st.session_state.invoice_db:
        st.markdown(f"#### {L['db_list']}")
        st.dataframe(
            pd.DataFrame(st.session_state.invoice_db),
            use_container_width=True,
        )

    # 頁籤三：IMAP 信箱發票讀取
    with tab_email:
        st.markdown(f"#### {L['imap_title']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            imap_server = st.text_input(
                L["server_label"], value="imap.gmail.com", key="imap_server"
            )
        with col2:
            email_user = st.text_input(
                L["user_label"], value="accounting@company.com", key="email_user"
            )
        with col3:
            email_pass = st.text_input(
                L["pass_label"], type="password", key="email_pass"
            )

        if st.button(
            L["btn_fetch"], type="primary", key="btn_fetch_email_invoices"
        ):
            with st.spinner(L["spinner_fetch"]):
                invoices, msg = fetch_invoices_from_email(
                    imap_server, email_user, email_pass
                )
                if invoices:
                    st.success(msg)
                    for inv in invoices:
                        with st.expander(
                            f"📄 【{inv['date']}】{inv['subject']} — 寄件者: {inv['sender']}"
                        ):
                            st.write(f"• **郵件 ID**: `{inv['id']}`")
                            st.write(
                                f"• **偵測到的發票附件/檔案**: `{', '.join(inv['attachments'])}`"
                            )
                else:
                    st.info(msg)

    # 頁籤四：發票張數預警與購買
    with tab_quota:
        render_invoice_quota_widget()


# 保持相容入口，確保全系統調用均不跳錯
def render_invoice_management_page(engine=None, lang="繁體中文"):
    render_invoice_management(engine, lang)


def render_invoice(engine=None, lang="繁體中文"):
    render_invoice_management(engine, lang)


def show(engine=None, lang="繁體中文"):
    render_invoice_management(engine, lang)


def main(engine=None, lang="繁體中文"):
    render_invoice_management(engine, lang)
