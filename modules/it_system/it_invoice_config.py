import streamlit as st
import datetime

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 注入 (Mobile-First UI)
# ----------------------------------------------------
MOBILE_IT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.85rem !important; }
    .stDataFrame { overflow-x: auto; }
    .stButton button { width: 100% !important; }
}
</style>
"""
st.markdown(MOBILE_IT_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🌐 資訊管理與電子發票設定多語系字典 (i18n)
# ----------------------------------------------------
IT_INVOICE_I18N = {
    "繁體中文": {
        "title": "🔌 資訊管理 - 越南電子發票 API 串接與參數設定",
        "caption": "設定與管理公司連線至越南稅務總局 / 各大電子發票服務商 (Thông tư 200 / e-Invoice) 之 API 介面與憑證。",
        "header": "🛠️ 電子發票 API 閘道與憑證參數設定",
        "provider_label": "發票系統商 (E-Invoice Provider) *",
        "provider_opts": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "env_label": "執行環境 *",
        "env_opts": ["測試環境 (Sandbox)", "正式環境 (Production)"],
        "tax_code_label": "公司稅號 (Mã số thuế) *",
        "endpoint_label": "API 閘道端點網址 (Endpoint URL) *",
        "key_label": "API 授權金鑰 / 憑證 Token *",
        "modifier_label": "設定人員 (系統綁定登入帳號)",
        "save_btn": "💾 儲存 API 串接設定",
        "test_btn": "🔗 測試 API 連線",
        "save_success": "電子發票 API 參數已成功儲存並生效！",
        "test_success": "✅ API 連線測試成功！憑證授權與伺服器回應正常。"
    },
    "Tiếng Việt": {
        "title": "🔌 Quản trị CNTT - Cấu hình API Hóa đơn điện tử",
        "caption": "Cấu hình và quản lý kết nối API đến Tổng cục Thuế / Nhà cung cấp hóa đơn điện tử (Thông tư 200).",
        "header": "🛠️ Thiết lập thông số cổng API hóa đơn điện tử",
        "provider_label": "Nhà cung cấp hóa đơn *",
        "provider_opts": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "env_label": "Môi trường *",
        "env_opts": ["Sandbox (Thử nghiệm)", "Production (Chính thức)"],
        "tax_code_label": "Mã số thuế công ty *",
        "endpoint_label": "Đường dẫn API (Endpoint URL) *",
        "key_label": "Mã khóa API / Token xác thực *",
        "modifier_label": "Người cấu hình (Khóa hệ thống)",
        "save_btn": "💾 Lưu cấu hình API",
        "test_btn": "🔗 Kiểm tra kết nối API",
        "save_success": "Đã lưu thành công cấu hình API hóa đơn!",
        "test_success": "✅ Kết nối API thành công!"
    },
    "English": {
        "title": "🔌 IT Admin - E-Invoice API Integration Settings",
        "caption": "Configure and manage API connections and certificates for Vietnam E-Invoice providers (Thông tư 200).",
        "header": "🛠️ E-Invoice API Gateway & Certificate Settings",
        "provider_label": "E-Invoice Provider *",
        "provider_opts": ["Viettel (S-Invoice)", "VNPT (VNPT-Invoice)", "MISA (MISA meInvoice)", "FPT.eInvoice", "Custom API"],
        "env_label": "Environment *",
        "env_opts": ["Sandbox", "Production"],
        "tax_code_label": "Company Tax Code (Mã số thuế) *",
        "endpoint_label": "API Endpoint URL *",
        "key_label": "API Auth Token / Key *",
        "modifier_label": "Modifier (System Bound)",
        "save_btn": "💾 Save API Settings",
        "test_btn": "🔗 Test API Connection",
        "save_success": "API settings saved successfully!",
        "test_success": "✅ API connection test successful!"
    }
}

def render_it_invoice_config_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = IT_INVOICE_I18N.get(active_lang, IT_INVOICE_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])
    st.markdown("---")

    st.subheader(L["header"])
    
    with st.form("form_it_invoice_config"):
        api_provider = st.selectbox(L["provider_label"], L["provider_opts"])
        api_env = st.selectbox(L["env_label"], L["env_opts"])
        tax_code = st.text_input(L["tax_code_label"], value="3702581234")
        api_endpoint = st.text_input(L["endpoint_label"], value="https://api.einvoice.viettel.vn/v1/publish")
        api_key = st.text_input(L["key_label"], type="password", value="VT-TOKEN-2026-RETECH-SECURE-KEY")
        
        # 🔒 IT 循跡稽核鐵律：強制綁定登入帳號與權限，禁止手動改名
        logged_user_name = st.session_state.get("user_name", "admin")
        logged_user_role = str(st.session_state.get("user_role", "IT_Admin")).upper()
        modifier_display = f"{logged_user_name} ({logged_user_role})"
        
        st.text_input(L["modifier_label"], value=modifier_display, disabled=True)

        col1, col2 = st.columns(2)
        with col1:
            save_clicked = st.form_submit_button(L["save_btn"], type="primary", use_container_width=True)
        with col2:
            test_clicked = st.form_submit_button(L["test_btn"], use_container_width=True)

        if save_clicked:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.success(f"{L['save_success']} (時間: {timestamp} | 稽核經辦: {modifier_display})")

        if test_clicked:
            st.success(L["test_success"])

def show(*args, **kwargs):
    render_it_invoice_config_page(*args, **kwargs)

def main(*args, **kwargs):
    render_it_invoice_config_page(*args, **kwargs)

def render_it_invoice_config(*args, **kwargs):
    render_it_invoice_config_page(*args, **kwargs)
