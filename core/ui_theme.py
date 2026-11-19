# ==========================================
# 檔案路徑：core/ui_theme.py
# 職責：全域多語系（繁中/越文/英文）與手機優先（Mobile-First）響應式樣式模組
# ==========================================

import streamlit as st

SUPPORTED_LANGS = {
    "zh": "🇹🇼 繁體中文",
    "vi": "🇻🇳 Tiếng Việt",
    "en": "🌐 English",
}

I18N_DICT = {
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
    "no_org_hint": {
        "zh": "⚠️ 此租戶尚未初始化組織樹與功能拼圖，請先進入「系統設定」套用模板或建立部門。",
        "vi": "⚠️ Chưa khởi tạo cây tổ chức và tính năng cho đơn vị này. Vui lòng vào Cài đặt hệ thống.",
        "en": "⚠️ Organization tree is not initialized for this tenant. Please configure in System Settings.",
    },
    "no_mounted_hint": {
        "zh": "💡 此節點目前尚未掛載功能拼圖，請至「系統設定 ➡️ 功能拼圖掛載」勾選並儲存。",
        "vi": "💡 Chưa gắn chức năng nào vào mục này. Vui lòng cấu hình trong Cài đặt hệ thống.",
        "en": "💡 No feature puzzles mounted here yet. Please configure them in System Settings.",
    },
    "sub_cards_title": {
        "zh": "🗂️ 下屬部門與作業卡片",
        "vi": "🗂️ Các Đơn Vị / Thẻ Nghiệp Vụ Trực Thuộc",
        "en": "🗂️ Sub-Units & Work Cards",
    },
    "mounted_features_title": {
        "zh": "🧩 已掛載功能拼圖",
        "vi": "🧩 Chức Năng Đã Gắn",
        "en": "🧩 Mounted Feature Puzzles",
    },
    "open_sub_card": {
        "zh": "進入卡片 ➡️",
        "vi": "Mở Thẻ ➡️",
        "en": "Open Card ➡️",
    },
    "open_feature": {
        "zh": "開啟功能 ➡️",
        "vi": "Mở Chức Năng ➡️",
        "en": "Open Feature ➡️",
    },
}


def normalize_lang(lang: str | None) -> str:
    val = (lang or "zh").strip().lower()
    if val.startswith("vi") or "việt" in val or "viet" in val:
        return "vi"
    if val.startswith("en"):
        return "en"
    return "zh"


def tr(key: str, lang: str | None = None, fallback: str = "") -> str:
    code = normalize_lang(lang or st.session_state.get("current_lang", "zh"))
    entry = I18N_DICT.get(key)
    if entry:
        return entry.get(code) or entry.get("zh") or fallback or key
    return fallback or key


def render_lang_selector(key_prefix: str = "global_lang"):
    curr = normalize_lang(st.session_state.get("current_lang", "zh"))
    codes = list(SUPPORTED_LANGS.keys())
    idx = codes.index(curr) if curr in codes else 0
    chosen = st.selectbox(
        "🌐 語言 / Ngôn ngữ / Language",
        options=codes,
        index=idx,
        format_func=lambda c: SUPPORTED_LANGS[c],
        key=f"{key_prefix}_select",
    )
    if chosen != curr:
        st.session_state["current_lang"] = chosen
        st.rerun()


def apply_mobile_first_theme():
    """注入手機優先（Mobile-First）響應式 CSS，兼顧觸控按鈕與窄螢幕可讀性"""
    st.markdown(
        """
        <style>
        /* 基礎觸控友善設定 */
        .stButton > button {
            min-height: 2.6rem;
            border-radius: 8px;
            white-space: normal;
            word-break: break-word;
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
            max-width: 100%;
        }

        /* 手機與窄螢幕優先適配（<= 768px） */
        @media only screen and (max-width: 768px) {
            .block-container {
                padding-top: 0.8rem !important;
                padding-left: 0.65rem !important;
                padding-right: 0.65rem !important;
                padding-bottom: 3rem !important;
            }
            h1 { font-size: 1.3rem !important; line-height: 1.35 !important; }
            h2 { font-size: 1.15rem !important; line-height: 1.35 !important; }
            h3 { font-size: 1.05rem !important; line-height: 1.35 !important; }
            h4, h5 { font-size: 0.98rem !important; line-height: 1.35 !important; }
            p, label, .stCaption, .stMarkdown {
                font-size: 0.92rem !important;
                line-height: 1.45 !important;
            }
            .stButton > button {
                min-height: 2.9rem !important;
                font-size: 0.95rem !important;
                padding: 0.45rem 0.75rem !important;
            }
            [data-testid="stMetricValue"] {
                font-size: 1.25rem !important;
            }
            [data-testid="stHorizontalBlock"] {
                gap: 0.5rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
