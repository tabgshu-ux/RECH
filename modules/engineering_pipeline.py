import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 工程與報價模組多語系字典 (i18n)
# ----------------------------------------------------
QUOTATION_I18N = {
    "繁體中文": {
        "title": "⚙️ 工程部 – 配電盤與物料報價系統",
        "caption": "供工程與業務管理：自由選取物料、規格、數量和工資以自動計算總報價。",
        "sec1_title": "📋 1. 專案資訊 & 技術規格",
        "lbl_project": "專案名稱 / 客戶名稱 *",
        "proj_placeholder": "例如: 西寧紡織廠 2000A 主配電盤新建工程",
        "lbl_currency": "計價幣別",
        "lbl_req": "技術需求與規格說明 *",
        "req_placeholder": "例如: 包含高純度銅排母線加工、2000A ACB 空氣斷路器組裝與現場耐壓絕緣測試。",
        
        "sec2_title": "📦 2. 選擇配電盤物料 & 計算金額 (自動計算)",
        "sec2_caption": "請由下拉式選單選擇所需的配電強弱電材，並填入數量：",
        "lbl_item1": "資材品項 #1",
        "lbl_item2": "資材品項 #2",
        "lbl_item3": "資材品項 #3",
        "col_qty": "數量 (Qty)",
        "col_price": "單價 (USD)",
        "col_subtotal": "小計 (USD)"
    },
    "Tiếng Việt": {
        "title": "⚙️ Khối Kỹ thuật – Hệ thống Báo giá Tủ điện & Vật tư",
        "caption": "Dành cho quản lý kỹ thuật và kinh doanh: Tự do chọn vật tư, quy cách, số lượng và giá công để hệ thống tự động tính tổng báo giá.",
        "sec1_title": "📋 1. Thông tin Dự án & Quy cách Kỹ thuật",
        "lbl_project": "Tên Dự án / Tên Khách hàng *",
        "proj_placeholder": "Ví dụ: Nhà máy dệt Tây Ninh - Tủ điện chính 2000A",
        "lbl_currency": "Loại tiền tệ",
        "lbl_req": "Mô tả yêu cầu kỹ thuật *",
        "req_placeholder": "Ví dụ: Bao gồm gia công thanh cái đồng, lắp đặt ACB 2000A và kiểm tra cách điện tại hiện trường.",
        
        "sec2_title": "📦 2. Chọn Vật tư Tủ điện & Thành tiền (Tự động tính)",
        "sec2_caption": "Chọn từ danh sách để chọn vật tư, quy cách, số lượng để hệ thống tính tiền tự động:",
        "lbl_item1": "Mặt hàng #1",
        "lbl_item2": "Mặt hàng #2",
        "lbl_item3": "Mặt hàng #3",
        "col_qty": "Số lượng (Qty)",
        "col_price": "Đơn giá (USD)",
        "col_subtotal": "Thành tiền (USD)"
    },
    "English": {
        "title": "⚙️ Engineering – Switchboard & Material Quotation System",
        "caption": "For engineering and sales: Select materials, specifications, quantities, and labor costs for automatic quotation calculation.",
        "sec1_title": "📋 1. Project Information & Technical Specs",
        "lbl_project": "Project Name / Client Name *",
        "proj_placeholder": "Example: Tay Ninh Textile Plant - 2000A Switchboard",
        "lbl_currency": "Currency",
        "lbl_req": "Technical Requirements & Specs *",
        "req_placeholder": "Example: Includes copper busbar fabrication, 2000A ACB assembly, and site insulation testing.",
        
        "sec2_title": "📦 2. Select Switchboard Materials & Subtotal (Auto-calculated)",
        "sec2_caption": "Select required switchboard materials from the dropdown and enter quantities:",
        "lbl_item1": "Item #1",
        "lbl_item2": "Item #2",
        "lbl_item3": "Item #3",
        "col_qty": "Quantity (Qty)",
        "col_price": "Unit Price (USD)",
        "col_subtotal": "Subtotal (USD)"
    }
}

def get_active_lang(passed_lang):
    if passed_lang in QUOTATION_I18N:
        return passed_lang
    for key in ["current_lang", "lang", "language", "selected_lang"]:
        val = st.session_state.get(key)
        if val in QUOTATION_I18N:
            return val
    return "Tiếng Việt"  # 預設越南文

def render_engineering_quotation_page(engine=None, lang=None, **kwargs):
    active_lang = get_active_lang(lang)
    L = QUOTATION_I18N.get(active_lang, QUOTATION_I18N["Tiếng Việt"])

    st.title(L["title"])
    st.caption(L["caption"])

    st.markdown(f"### {L['sec1_title']}")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        proj_name = st.text_input(
            L["lbl_project"], 
            value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A" if active_lang == "Tiếng Việt" else "西寧紡織廠 2000A 主配電盤新建工程"
        )
    with c2:
        currency = st.selectbox(L["lbl_currency"], ["USD", "VND", "TWD", "EUR"])

    req_desc = st.text_area(
        L["lbl_req"], 
        value="Bao gồm gia công thanh cái đồng, lắp đặt ACB 2000A và kiểm tra cách điện." if active_lang == "Tiếng Việt" else "包含高純度銅排母線加工、2000A ACB 空氣斷路器組裝與現場耐壓絕緣測試。"
    )

    st.markdown(f"### {L['sec2_title']}")
    st.caption(L["sec2_caption"])

    c_item1, c_q1, c_p1, c_s1 = st.columns([3, 1, 1, 1])
    with c_item1:
        st.text_input(L["lbl_item1"], value="[CU-BUS-10100] Đồng thanh cái Busbar 10x100mm", disabled=True)
    with c_q1:
        q1 = st.number_input("Qty 1", min_value=0.0, value=150.0, step=10.0, label_visibility="collapsed")
    with c_p1:
        st.text_input("Price 1", value="$12.50", disabled=True, label_visibility="collapsed")
    with c_s1:
        st.text_input("Sub 1", value=f"${q1 * 12.50:,.2f}", disabled=True, label_visibility="collapsed")

    c_item2, c_q2, c_p2, c_s2 = st.columns([3, 1, 1, 1])
    with c_item2:
        st.text_input(L["lbl_item2"], value="[CB-ACB-2000A] Máy cắt không khí ACB 2000A (Schneider)", disabled=True)
    with c_q2:
        q2 = st.number_input("Qty 2", min_value=0.0, value=2.0, step=1.0, label_visibility="collapsed")
    with c_p2:
        st.text_input("Price 2", value="$1,850.00", disabled=True, label_visibility="collapsed")
    with c_s2:
        st.text_input("Sub 2", value=f"${q2 * 1850.00:,.2f}", disabled=True, label_visibility="collapsed")

def render_engineering_page(*args, **kwargs):
    render_engineering_quotation_page(*args, **kwargs)

def render_engineering_quotation(*args, **kwargs):
    render_engineering_quotation_page(*args, **kwargs)

def render_quotation(*args, **kwargs):
    render_engineering_quotation_page(*args, **kwargs)

def show(*args, **kwargs):
    render_engineering_quotation_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_quotation_page(*args, **kwargs)
