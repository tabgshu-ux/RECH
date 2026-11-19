# ==========================================
# 檔案路徑：core/ui_theme.py
# 職責：多語系（繁中/越文/英文）與手機優先（Mobile-First）響應式樣式（修正頂部遮擋與捲動）
# ==========================================

import streamlit as st
import streamlit.components.v1 as components

LANG_LABELS = {
    "zh": "🇹🇼 繁體中文",
    "vi": "🇻🇳 Tiếng Việt",
    "en": "🌐 English",
}

TEXTS = {
    "app_title": {
        "zh": "裕豐電機工業 SaaS ERP",
        "vi": "Hệ Thống SaaS ERP Công Nghiệp Dự Phong",
        "en": "Reetech Industrial SaaS ERP",
    },
    "org_nav": {
        "zh": "🏢 企業組織導航",
        "vi": "🏢 Điều Hướng Cơ Cấu Tổ Chức",
        "en": "🏢 Organization Navigation",
    },
    "sys_settings": {
        "zh": "⚙️ 系統設定 (Cấu hình hệ thống)",
        "vi": "⚙️ Cấu Hình Hệ Thống",
        "en": "⚙️ System Settings",
    },
    "back_home": {
        "zh": "🏠 回部門選單",
        "vi": "🏠 Về Danh Sách Phòng Ban",
        "en": "🏠 Back to Menu",
    },
    "logout": {
        "zh": "🚪 登出",
        "vi": "🚪 Đăng Xuất",
        "en": "🚪 Logout",
    },
    "no_org": {
        "zh": "⚠️ 此租戶尚未建立組織節點，請先至「系統設定」套用模板或新增部門。",
        "vi": "⚠️ Chưa có cây tổ chức cho đơn vị này. Hãy vào Cài đặt hệ thống.",
        "en": "⚠️ No organization nodes yet. Please configure in System Settings.",
    },
    "no_feats": {
        "zh": "💡 此節點尚未掛載功能拼圖，請至「系統設定 ➡️ 功能拼圖掛載」勾選並儲存。",
        "vi": "💡 Chưa gắn chức năng nào. Hãy chọn và lưu trong Cài đặt hệ thống.",
        "en": "💡 No feature puzzles mounted yet. Please configure in System Settings.",
    },
    "sub_cards": {
        "zh": "🗂️ 下屬部門與卡片",
        "vi": "🗂️ Các Đơn Vị / Thẻ Trực Thuộc",
        "en": "🗂️ Sub-Units & Cards",
    },
    "mounted_feats": {
        "zh": "🧩 已掛載功能拼圖",
        "vi": "🧩 Chức Năng Đã Gắn",
        "en": "🧩 Mounted Features",
    },
    "enter_card": {
        "zh": "進入卡片 ➡️",
        "vi": "Mở Thẻ ➡️",
        "en": "Open Card ➡️",
    },
    "open_feat": {
        "zh": "開啟功能 ➡️",
        "vi": "Mở Chức Năng ➡️",
        "en": "Open Feature ➡️",
    },
}


def norm_lang(lang: str | None) -> str:
    v = (lang or "zh").strip().lower()
    if v.startswith("vi") or "việt" in v or "viet" in v:
        return "vi"
    if v.startswith("en"):
        return "en"
    return "zh"


def tr(key: str, lang: str | None = None) -> str:
    code = norm_lang(lang or st.session_state.get("current_lang", "zh"))
    row = TEXTS.get(key)
    return row.get(code) or row.get("zh") or key if row else key


def render_lang_selector(key: str = "lang_sel"):
    curr = norm_lang(st.session_state.get("current_lang", "zh"))
    opts = list(LANG_LABELS.keys())
    idx = opts.index(curr) if curr in opts else 0
    sel = st.selectbox(
        "🌐 語言 / Ngôn ngữ / Language",
        options=opts,
        index=idx,
        format_func=lambda x: LANG_LABELS[x],
        key=key,
    )
    if sel != curr:
        st.session_state["current_lang"] = sel
        st.rerun()


def scroll_to_top():
    components.html(
        """
        <script>
        try {
            const main = window.parent.document.querySelector('section.main');
            if (main) { main.scrollTo({top: 0, behavior: 'instant'}); }
            window.parent.scrollTo(0, 0);
        } catch (e) {}
        </script>
        """,
        height=0,
    )


def apply_mobile_first():
    st.markdown(
        """
        <style>
        /* 讓 Streamlit 頂部工具列透明不遮擋自訂標題與返回按鈕 */
        header[data-testid="stHeader"] {
            background: transparent;
            height: 2.8rem;
        }
        .block-container {
            padding-top: 3.3rem !important;
            padding-bottom: 3rem !important;
        }
        .stButton > button {
            min-height: 2.6rem;
            border-radius: 8px;
            white-space: normal;
            word-break: break-word;
        }
        @media only screen and (max-width: 768px) {
            .block-container {
                padding-top: 3.1rem !important;
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
                padding-bottom: 3.5rem !important;
            }
            h1 { font-size: 1.28rem !important; }
            h2 { font-size: 1.12rem !important; }
            h3 { font-size: 1.02rem !important; }
            h4, h5 { font-size: 0.96rem !important; }
            p, label, .stCaption, .stMarkdown { font-size: 0.9rem !important; }
            .stButton > button {
                min-height: 2.9rem !important;
                font-size: 0.95rem !important;
            }
            [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_mobile_first_theme():
    apply_mobile_first()
