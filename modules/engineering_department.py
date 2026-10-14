import streamlit as st
import pandas as pd
import datetime
import base64
import re
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 三語系字典 (i18n)
# ----------------------------------------------------
QUO_I18N = {
    "繁體中文": {
        "title": "⚡ 配電盤與工程專案雙層報價與現場探勘系統",
        "caption": "探勘人員選擇倉庫材料/手動輸入未在庫項目，上傳現場勘查照片並計算多幣別總價呈報副總經理。",
        "lbl_code": "報價單編號 *",
        "lbl_customer": "客戶名稱 *",
        "lbl_proj": "專案/工程名稱 *",
        "lbl_currency": "💱 報價幣別選擇 *",
        "lbl_total_amount": "💰 預估工程總報價金額 *",
        "lbl_photo_site": "📸 上傳現場探勘照片與勘查圖檔 (供副總經理審核參考) *",
        "lbl_file_doc": "📄 上傳詳細報價單與附件 (Excel / PDF / DWG)",
        "lbl_site_notes": "📝 現場探勘狀況與特殊施工說明",
        "btn_submit": "🚀 送出探勘報價單並呈報副總經理審核"
    },
    "English": {
        "title": "⚡ Project Quotation & Site Exploration System",
        "caption": "Select warehouse inventory, input custom materials, upload site photos, and submit to VP.",
        "lbl_code": "Quotation Code *",
        "lbl_customer": "Customer Name *",
        "lbl_proj": "Project Name *",
        "lbl_currency": "💱 Currency *",
        "lbl_total_amount": "💰 Est. Total Amount *",
        "lbl_photo_site": "📸 Upload Site Survey Photos (For Vice President Review) *",
        "lbl_file_doc": "📄 Upload Detailed Quotation (Excel / PDF / DWG)",
        "lbl_site_notes": "📝 Site Condition & Engineering Notes",
        "btn_submit": "🚀 Submit Quotation to Vice President"
    },
    "Tiếng Việt": {
        "title": "⚡ Hệ thống Báo giá Dự án & Khảo sát Thực địa",
        "caption": "Chọn vật tư kho, nhập vật tư ngoài, tải ảnh thực địa và trình Phó Tổng Giám Đốc duyệt.",
        "lbl_code": "Mã báo giá *",
        "lbl_customer": "Tên khách hàng *",
        "lbl_proj": "Tên dự án / Công trình *",
        "lbl_currency": "💱 Loại tiền tệ *",
        "lbl_total_amount": "💰 Tổng giá trị báo giá dự kiến *",
        "lbl_photo_site": "📸 Tải ảnh khảo sát thực địa (Gửi Phó Tổng Giám Đốc tham khảo) *",
        "lbl_file_doc": "📄 Tải tệp báo giá chi tiết (Excel / PDF / DWG)",
        "lbl_site_notes": "📝 Ghi chú khảo sát thực địa",
        "btn_submit": "🚀 Gửi báo giá trình Phó Tổng Giám Đốc"
    }
}

def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def format_currency_text(amount, currency="VND"):
    try:
        val = float(amount)
        if currency == "VND":
            return f"{val:,.0f}".replace(",", ".") + " VND"
        elif currency == "USD":
            return f"${val:,.2f} USD"
        elif currency == "RMB":
            return f"¥{val:,.2f} RMB"
        elif currency == "TWD":
            return f"NT${val:,.0f} TWD"
        else:
            return f"{val:,.0f} {currency}"
    except Exception:
        return f"{amount} {currency}"

def inject_quo_css():
    st.markdown("""
        <style>
        html, body, [class*="css"] { font-size: 16px !important; }
        div.stButton > button {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            border-radius: 8px !important;
        }
        .bom-box {
            background-color: #F0FDFA;
            border: 2px dashed #0D9488;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }
        .site-photo-box {
            background-color: #FEF3C7;
            border: 2px dashed #D97706;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def init_quo_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.project_quotations (
                    id SERIAL PRIMARY KEY,
                    quo_code VARCHAR(50) UNIQUE NOT NULL,
                    customer_name VARCHAR(200) NOT NULL,
                    project_name VARCHAR(200) NOT NULL,
                    currency VARCHAR(10) DEFAULT 'VND',
                    total_amount NUMERIC(15,2) DEFAULT 0,
                    site_photos TEXT,
                    quote_doc TEXT,
                    site_notes TEXT,
                    bom_details JSONB,
                    vp_approval VARCHAR(50) DEFAULT '🟡 待副總經理簽核',
                    created_by VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_engineering_quotation_page(engine=None, lang="繁體中文", **kwargs):
    inject_quo_css()

    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = QUO_I18N.get(active_lang, QUO_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_quo_db(engine)

    current_user_name = st.session_state.get("user_name", "探勘工程師")

    # ----------------------------------------------------
    # 初始化探勘 BOM 清單 Session State
    # ----------------------------------------------------
    if "survey_bom_items" not in st.session_state:
        st.session_state.survey_bom_items = [
            {"item_name": "Schneider 400A 空氣斷路器 (ACB)", "spec": "3P 65kA", "qty": 1.0, "unit": "台", "price": 45000000.0, "source": "倉庫連線物料"},
            {"item_name": "高壓電纜 3x240mm2", "spec": "24kV XLPE", "qty": 50.0, "unit": "米", "price": 1200000.0, "source": "倉庫連線物料"}
        ]

    with st.form("form_project_quotation_survey"):
        # 1. 報價基本資料
        st.markdown("#### 📝 1. 專案報價基本資訊")
        c1, c2 = st.columns(2)
        with c1:
            default_qcode = "QUO-" + datetime.datetime.now().strftime("%Y%m%d-%H%M")
            q_code = st.text_input(L["lbl_code"], value=default_qcode)
            p_name = st.text_input(L["lbl_proj"], placeholder="例: 西寧廠高壓配電盤擴建案")
        with c2:
            cust_name = st.text_input(L["lbl_customer"], placeholder="例: 台商越南造紙廠")
            
            # 💱 4 種幣別選擇 (VND, USD, RMB, TWD)
            q_currency = st.selectbox(L["lbl_currency"], ["VND", "USD", "RMB", "TWD"], index=0)

        # 2. 探勘 BOM 材料明細（倉庫連線 + 未在庫手動新增）
        st.markdown("""
        <div class="bom-box">
            <h5 style="color:#0F766E; margin-top:0;">📦 2. 探勘工程 BOM 材料清單 (倉庫連線 + 現場手動輸入)</h5>
        """, unsafe_allow_html=True)
        
        st.caption("探勘人員可直接從倉庫物料連線挑選，若倉庫沒有則可直接在下方編輯器新增：")

        # 編輯 BOM 材料表格
        bom_df = pd.DataFrame(st.session_state.survey_bom_items)
        edited_bom = st.data_editor(
            bom_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "item_name": st.column_config.TextColumn("材料/設備名稱 *", required=True),
                "spec": st.column_config.TextColumn("規格型號"),
                "qty": st.column_config.NumberColumn("需求數量", min_value=0.1, step=1.0),
                "unit": st.column_config.TextColumn("單位"),
                "price": st.column_config.NumberColumn(f"預估單價 ({q_currency})", min_value=0.0),
                "source": st.column_config.SelectboxColumn("物料來源", options=["倉庫連線物料", "現場手動新增未在庫"])
            }
        )

        # 計算 BOM 總價與自動帶入
        bom_total = 0.0
        if not edited_bom.empty:
            try:
                bom_total = (edited_bom["qty"] * edited_bom["price"]).sum()
            except Exception:
                bom_total = 0.0

        st.markdown(f"**💡 BOM 自動加總參考金額：** `:red[{format_currency_text(bom_total, q_currency)}]`")
        st.markdown("</div>", unsafe_allow_html=True)

        # 3. 金額輸入與現場探勘照片上傳 (呈報副總經理)
        st.markdown("#### 💰 3. 專案預估總價與現場探勘照片呈報")
        
        # 💰 使用點號千分位格式輸入框 (絕不帶 .00)
        default_amt_str = f"{bom_total:,.0f}".replace(",", ".") if q_currency in ["VND", "TWD"] else f"{bom_total:,.2f}"
        total_amt_str = st.text_input(
            L["lbl_total_amount"],
            value=default_amt_str,
            help="請輸入金額，系統支援千位點號格式 (例如: 250.000.000)"
        )
        total_amt_val = parse_formatted_amount(total_amt_str)

        st.markdown("""
        <div class="site-photo-box">
            <h5 style="color:#B45309; margin-top:0;">📸 4. 現場探勘照片與備註 (提供副總經理/高階簽核參考)</h5>
        """, unsafe_allow_html=True)
        
        site_photos = st.file_uploader(
            L["lbl_photo_site"],
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="請拍攝上傳現場變壓器、開關箱、配線走線與施工現場照片"
        )

        quote_doc_file = st.file_uploader(L["lbl_file_doc"], type=["xlsx", "xls", "pdf", "dwg"])
        site_notes = st.text_area(L["lbl_site_notes"], placeholder="例: 現場高壓走線受限，需要額外增加 15 米線槽；客戶要求週六停電施工。")
        st.markdown("</div>", unsafe_allow_html=True)

        # 4. 提交按鈕
        if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
            if not p_name or not cust_name:
                st.error("⚠️ 請填寫專案名稱與客戶名稱！")
            elif total_amt_val <= 0:
                st.error("⚠️ 請輸入正確的預估工程總金額！")
            else:
                # 處理照片編碼
                encoded_photos = []
                if site_photos:
                    for ph in site_photos:
                        encoded_photos.append(base64.b64encode(ph.read()).decode("utf-8"))

                # 處理報價單檔案
                encoded_doc = ""
                if quote_doc_file:
                    encoded_doc = base64.b64encode(quote_doc_file.read()).decode("utf-8")

                bom_json = edited_bom.to_dict(orient="records") if not edited_bom.empty else []

                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.project_quotations 
                                (quo_code, customer_name, project_name, currency, total_amount, site_photos, quote_doc, site_notes, bom_details, created_by)
                                VALUES (:code, :cust, :proj, :curr, :amt, :photos, :doc, :notes, :bom, :user);
                            """), {
                                "code": q_code, "cust": cust_name, "proj": p_name,
                                "curr": q_currency, "amt": total_amt_val,
                                "photos": ",".join(encoded_photos), "doc": encoded_doc,
                                "notes": site_notes, "bom": pd.io.json.dumps(bom_json),
                                "user": current_user_name
                            })
                        st.success(f"🎉 探勘報價單【{q_code}】已成功建立！總金額：{format_currency_text(total_amt_val, q_currency)}，已自動呈報給【副總經理】進行審核。")
                        st.rerun()
                    except Exception as e:
                        st.error("寫入失敗: " + str(e))
                else:
                    st.success(f"🎉 [展示模式] 報價單【{q_code}】（金額: {format_currency_text(total_amt_val, q_currency)}）已建立並呈報副總經理！")

# ----------------------------------------------------
# 🔗 相容性進入點
# ----------------------------------------------------
def render_quotation_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_quotation_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_quotation_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_quotation_page(engine=engine, lang=lang, **kwargs)
