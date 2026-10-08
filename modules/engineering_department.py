import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 設計圖庫與版本控制模組多語系字典 (i18n)
# ----------------------------------------------------
DESIGN_I18N = {
    "繁體中文": {
        "title": "🎨 工程與設計中心 - 配電盤電氣與機構設計圖庫上傳中心",
        "caption": "專為工程設計人員打造：集中管理配電盤單線圖 (SLD)、PLC 控制圖、機構配置圖 (GA) 與銅排加工圖，支援版本控制與跨廠區下載。",
        "tab_gallery": "📁 設計圖紙與版本庫清冊",
        "tab_upload": "📤 上傳新版本設計圖與規格書",
        "header_gallery": "📋 現有配電盤設計圖面與版本控制清冊",
        "header_upload": "📤 上傳與發布工程設計圖紙",
        "search_label": "🔍 搜尋圖面名稱、專案代碼或設計師...",
        "lbl_proj": "對應工程專案代碼 *",
        "proj_opts": ["HD-2025-HOT (和鼎隆建築-西寧廠)", "HD-2026-JIA (佳威商旅-海防廠)", "HD-2026-YAN (彥豪金屬-西寧廠)"],
        "lbl_name": "圖面/文件名稱 *",
        "name_ph": "例如: 2000A 主配電盤單線圖 (SLD Rev.02)",
        "lbl_category": "圖面分類 *",
        "cat_opts": ["電氣單線圖 (SLD)", "機構外型與配置圖 (GA)", "銅排加工與立體圖 (Busbar)", "控制迴路與 PLC 圖"],
        "lbl_ver": "圖面版本 (Version) *",
        "ver_ph": "例如: Rev.01, Rev.02",
        "lbl_designer": "設計工程師 *",
        "btn_upload": "🚀 確認上傳並發布圖紙",
        "success_upload": "✅ 圖紙 `{name}` 版本 `{ver}` 已成功上傳至設計圖庫！",
        "col_index": "STT",
        "col_code": "專案代碼",
        "col_name": "圖面名稱",
        "col_cat": "分類",
        "col_ver": "版本",
        "col_designer": "設計師",
        "col_date": "上傳時間"
    },
    "Tiếng Việt": {
        "title": "🎨 Trung tâm Kỹ thuật & Thiết kế - Kho lưu trữ Bản vẽ Tủ điện",
        "caption": "Quản lý sơ đồ nguyên lý (SLD), bản vẽ cơ khí (GA), bản vẽ thanh cái đồng, hỗ trợ quản lý phiên bản.",
        "tab_gallery": "📁 Kho bản vẽ & Quản lý phiên bản",
        "tab_upload": "📤 Tải lên bản vẽ thiết kế mới",
        "header_gallery": "📋 Danh sách bản vẽ thiết kế tủ điện",
        "header_upload": "📤 Tải lên & Phát hành bản vẽ kỹ thuật",
        "search_label": "🔍 Tìm kiếm theo tên bản vẽ hoặc mã dự án...",
        "lbl_proj": "Mã dự án liên quan *",
        "proj_opts": ["HD-2025-HOT (Tây Ninh)", "HD-2026-JIA (Hải Phòng)", "HD-2026-YAN (Tây Ninh)"],
        "lbl_name": "Tên bản vẽ / Tài liệu *",
        "name_ph": "Ví dụ: Sơ đồ nguyên lý tủ tổng 2000A (Rev.02)",
        "lbl_category": "Phân loại bản vẽ *",
        "cat_opts": ["Sơ đồ nguyên lý (SLD)", "Bản vẽ cơ khí (GA)", "Bản vẽ thanh cái đồng (Busbar)", "Mạch điều khiển PLC"],
        "lbl_ver": "Phiên bản (Version) *",
        "ver_ph": "Ví dụ: Rev.01, Rev.02",
        "lbl_designer": "Kỹ sư thiết kế *",
        "btn_upload": "🚀 Xác nhận tải lên bản vẽ",
        "success_upload": "✅ Đã tải lên bản vẽ `{name}` phiên bản `{ver}` thành công!",
        "col_index": "STT",
        "col_code": "Mã dự án",
        "col_name": "Tên bản vẽ",
        "col_cat": "Phân loại",
        "col_ver": "Phiên bản",
        "col_designer": "Kỹ sư",
        "col_date": "Thời gian"
    },
    "English": {
        "title": "🎨 Engineering & Design Center - Switchgear Drawing & CAD Repository",
        "caption": "Manage SLD, GA drawings, busbar fabrication files, and revision control.",
        "tab_gallery": "📁 Drawing Repository & Version Control",
        "tab_upload": "📤 Upload New Design Drawings",
        "header_gallery": "📋 Switchgear Engineering Drawing Registry",
        "header_upload": "📤 Upload & Release Engineering Drawings",
        "search_label": "🔍 Search by drawing name, project, or designer...",
        "lbl_proj": "Associated Project Code *",
        "proj_opts": ["HD-2025-HOT (Tay Ninh)", "HD-2026-JIA (Hai Phong)", "HD-2026-YAN (Tay Ninh)"],
        "lbl_name": "Drawing / Document Name *",
        "name_ph": "E.g., 2000A Main Switchgear SLD (Rev.02)",
        "lbl_category": "Drawing Category *",
        "cat_opts": ["Single Line Diagram (SLD)", "General Arrangement (GA)", "Busbar Fabrication Drawing", "Control & PLC Schematic"],
        "lbl_ver": "Drawing Version *",
        "ver_ph": "E.g., Rev.01, Rev.02",
        "lbl_designer": "Lead Designer *",
        "btn_upload": "🚀 Confirm Upload & Release",
        "success_upload": "✅ Drawing `{name}` version `{ver}` uploaded successfully!",
        "col_index": "No.",
        "col_code": "Project Code",
        "col_name": "Drawing Name",
        "col_cat": "Category",
        "col_ver": "Version",
        "col_designer": "Designer",
        "col_date": "Timestamp"
    }
}

def render_engineering_design_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in DESIGN_I18N else "繁體中文"
    L = DESIGN_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    if "engineering_design_db" not in st.session_state:
        st.session_state.engineering_design_db = [
            {
                "project": "HD-2025-HOT",
                "name": "2000A 主配電盤及分路單線圖 (SLD)",
                "category": "電氣單線圖 (SLD)",
                "version": "Rev.02",
                "designer": "張工程師",
                "time": "2026-10-05 14:20:00"
            },
            {
                "project": "HD-2026-JIA",
                "name": "海防廠控制箱外型與機構配置圖 (GA)",
                "category": "機構外型與配置圖 (GA)",
                "version": "Rev.01",
                "designer": "Nguyễn Văn Hùng",
                "time": "2026-10-06 09:10:00"
            }
        ]

    tab_gallery, tab_upload = st.tabs([L["tab_gallery"], L["tab_upload"]])

    with tab_gallery:
        st.markdown(f"### {L['header_gallery']}")
        search_q = st.text_input(L["search_label"], key="design_search_box")

        data = st.session_state.engineering_design_db
        if search_q:
            data = [
                i for i in data 
                if search_q.lower() in i["name"].lower() or search_q.lower() in i["project"].lower() or search_q.lower() in i["designer"].lower()
            ]

        if data:
            display_list = []
            for idx, item in enumerate(data, 1):
                display_list.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["project"],
                    L["col_name"]: item["name"],
                    L["col_cat"]: item["category"],
                    L["col_ver"]: item["version"],
                    L["col_designer"]: item["designer"],
                    L["col_date"]: item["time"]
                })
            st.dataframe(pd.DataFrame(display_list), use_container_width=True)
            
            st.download_button(
                label="📥 下載選中專案之 CAD / PDF 設計圖包",
                data="Mock CAD Drawing Binary Stream",
                file_name="Reetech_Switchgear_Drawings.zip",
                mime="application/zip",
                type="primary"
            )
        else:
            st.info("目前尚無符合條件的設計圖紙。")

    with tab_upload:
        st.markdown(f"### {L['header_upload']}")
        with st.form("form_upload_drawing"):
            c1, c2 = st.columns(2)
            with c1:
                proj = st.selectbox(L["lbl_proj"], L["proj_opts"])
                name = st.text_input(L["lbl_name"], placeholder=L["name_ph"])
                cat = st.selectbox(L["lbl_category"], L["cat_opts"])
            with c2:
                ver = st.text_input(L["lbl_ver"], placeholder=L["ver_ph"], value="Rev.01")
                designer = st.text_input(L["lbl_designer"], value="張工程師")
                uploaded_file = st.file_uploader("選擇上傳檔案 (PDF, DWG, DXF, PNG)", type=["pdf", "dwg", "dxf", "png", "jpg"])

            if st.form_submit_button(L["btn_upload"], type="primary", use_container_width=True):
                if name:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    p_code = proj.split(" ")[0]
                    
                    st.session_state.engineering_design_db.insert(0, {
                        "project": p_code,
                        "name": name,
                        "category": cat,
                        "version": ver,
                        "designer": designer,
                        "time": now_str
                    })
                    st.success(L["success_upload"].format(name=name, ver=ver))
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫圖面名稱！")

def show(*args, **kwargs):
    render_engineering_design_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_design_page(*args, **kwargs)

def render_engineering_design(*args, **kwargs):
    render_engineering_design_page(*args, **kwargs)
