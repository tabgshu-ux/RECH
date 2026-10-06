import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 工程部專屬模組多語系字典 (i18n)
# ----------------------------------------------------
ENG_DEPT_I18N = {
    "繁體中文": {
        "title": "🛠️ 裕豐電機工業 - 工程部綜合管理中心",
        "caption": "完整涵蓋配電盤電氣機構設計圖庫、資材估價報價、以及全球廠區水電工程驗收與進度追蹤。",
        "tab_design": "📐 1. 設計圖庫與規格",
        "tab_quote": "⚙️ 2. 配電盤估價與報價",
        "tab_progress": "📊 3. 工程驗收與進度追蹤",
        
        # 設計圖庫
        "design_title": "📐 配電盤電氣與機構設計圖庫 (Switchgear Design & Drawings)",
        "design_caption": "管理各廠區高低壓配電盤、ACB/MCCB、Busbar 銅排配置與 CAD/PDF 設計圖檔。",
        "col_drawing_no": "圖號編碼",
        "col_project_name": "專案/廠區名稱",
        "col_spec": "電氣規格",
        "col_version": "版次",
        "col_designer": "設計工程師",
        "col_action": "圖檔操作",
        
        # 報價系統
        "quote_title": "⚙️ 配電盤與物料報價系統 (Costing & Quotation)",
        "quote_caption": "供工程與業務管理：自由選取物料、規格、數量和工資以自動計算總報價。",
        "sec1_title": "📋 1. 專案資訊 & 技術規格",
        "lbl_project": "專案名稱 / 客戶名稱 *",
        "lbl_currency": "計價幣別",
        "lbl_req": "技術需求與規格說明 *",
        "sec2_title": "📦 2. 選擇配電盤物料 & 計算金額 (自動計算)",
        "sec2_caption": "請由下拉式選單選擇所需的配電強弱電材，並填入數量：",
        "lbl_item1": "資材品項 #1",
        "lbl_item2": "資材品項 #2",
        "col_qty": "數量 (Qty)",
        "col_price": "單價 (USD)",
        "col_subtotal": "小計 (USD)",
        
        # 工程驗收進度
        "prog_title": "⚡ 全球廠區水電工程驗收與進度追蹤",
        "prog_caption": "純工程導向：專注監控工程現場施工進度百分比、驗收狀態與合約管控。",
        "kpi1_title": "在手水電專案總數",
        "kpi1_val": "8 件",
        "kpi1_sub": "↑ 執行中 6 件 / 驗收 2 件",
        "kpi2_title": "合約總金額 (USD)",
        "kpi2_sub": "↑ 累計已收: $1,250,000",
        "kpi3_title": "總未收款/應收尾款 (AR)",
        "kpi3_sub": "↑ 需加強催收",
        "kpi4_title": "平均工程進度",
        "kpi4_sub": "● 進度正常",
        "table_header": "📋 專案明細、工程進度與驗收狀態管控表",
        "col_code": "專案代碼",
        "col_client": "客戶名稱 / 廠區",
        "col_item": "水電工程項目",
        "col_total": "合約總值 (USD)",
        "col_paid": "已收款金額 (USD)",
        "col_ar": "未收款/尾款 (USD)",
        "col_progress": "工程進度 (%)",
        "col_status": "工程與驗收狀態"
    },
    "Tiếng Việt": {
        "title": "🛠️ REETECH INDUSTRIAL - Trung tâm Quản lý Khối Kỹ thuật",
        "caption": "Quản lý toàn diện kho bản vẽ thiết kế điện/cơ khí, báo giá vật tư tủ điện, và theo dõi tiến độ nghiệm thu công trình cơ điện.",
        "tab_design": "📐 1. Thư viện Bản vẽ Thiết kế",
        "tab_quote": "⚙️ 2. Báo giá Tủ điện & Vật tư",
        "tab_progress": "📊 3. Theo dõi Tiến độ & Nghiệm thu",
        
        "design_title": "📐 Thư viện Bản vẽ Thiết kế Tủ điện & Cơ khí",
        "design_caption": "Quản lý bản vẽ CAD/PDF tủ điện trung hạ thế, ACB/MCCB, thanh cái Busbar cho các nhà máy.",
        "col_drawing_no": "Mã bản vẽ",
        "col_project_name": "Tên dự án / Nhà máy",
        "col_spec": "Quy cách điện",
        "col_version": "Phiên bản",
        "col_designer": "Kỹ sư thiết kế",
        "col_action": "Thao tác",
        
        "quote_title": "⚙️ Hệ thống Báo giá Tủ điện & Vật tư",
        "quote_caption": "Dành cho quản lý kỹ thuật và kinh doanh: Tự do chọn vật tư, quy cách, số lượng và giá công để tính tổng báo giá.",
        "sec1_title": "📋 1. Thông tin Dự án & Quy cách Kỹ thuật",
        "lbl_project": "Tên Dự án / Tên Khách hàng *",
        "lbl_currency": "Loại tiền tệ",
        "lbl_req": "Mô tả yêu cầu kỹ thuật *",
        "sec2_title": "📦 2. Chọn Vật tư Tủ điện & Thành tiền (Tự động tính)",
        "sec2_caption": "Chọn từ danh sách để chọn vật tư, quy cách, số lượng:",
        "lbl_item1": "Mặt hàng #1",
        "lbl_item2": "Mặt hàng #2",
        "col_qty": "Số lượng (Qty)",
        "col_price": "Đơn giá (USD)",
        "col_subtotal": "Thành tiền (USD)",
        
        "prog_title": "⚡ Theo dõi Tiến độ & Nghiệm thu Dự án Cơ điện",
        "prog_caption": "Chuyên dụng kỹ thuật: Tập trung giám sát phần trăm tiến độ thi công, trạng thái nghiệm thu và hợp đồng.",
        "kpi1_title": "Tổng số dự án cơ điện",
        "kpi1_val": "8 dự án",
        "kpi1_sub": "↑ Đang thực hiện 6 / Nghiệm thu 2",
        "kpi2_title": "Tổng giá trị hợp đồng (USD)",
        "kpi2_sub": "↑ Đã thu lũy kế: $1,250,000",
        "kpi3_title": "Tổng công nợ phải thu (AR)",
        "kpi3_sub": "↑ Cần đẩy mạnh thu hồi",
        "kpi4_title": "Tiến độ thi công trung bình",
        "kpi4_sub": "● Tiến độ bình thường",
        "table_header": "📋 Bảng chi tiết dự án, tiến độ thi công và trạng thái nghiệm thu",
        "col_code": "Mã dự án",
        "col_client": "Tên khách hàng / Nhà máy",
        "col_item": "Hạng mục cơ điện",
        "col_total": "Giá trị HĐ (USD)",
        "col_paid": "Đã thu (USD)",
        "col_ar": "Còn lại/Phải thu (USD)",
        "col_progress": "Tiến độ (%)",
        "col_status": "Trạng thái thi công & Nghiệm thu"
    },
    "English": {
        "title": "🛠️ REETECH INDUSTRIAL - Engineering Department Management Center",
        "caption": "Comprehensive management of switchgear design drawings, material costing/quotations, and M&E project acceptance progress.",
        "tab_design": "📐 1. Design Drawings Library",
        "tab_quote": "⚙️ 2. Switchgear Costing & Quotation",
        "tab_progress": "📊 3. M&E Acceptance & Progress Tracking",
        
        "design_title": "📐 Switchgear & Mechanical Design Drawings Library",
        "design_caption": "Manage CAD/PDF drawings for medium/low voltage switchboards, ACB/MCCB, and Busbar configurations.",
        "col_drawing_no": "Drawing No.",
        "col_project_name": "Project / Plant Name",
        "col_spec": "Electrical Spec",
        "col_version": "Version",
        "col_designer": "Designer",
        "col_action": "Action",
        
        "quote_title": "⚙️ Switchgear & Material Quotation System",
        "quote_caption": "For engineering and sales: Select materials, specifications, quantities, and labor costs for automatic quotation.",
        "sec1_title": "📋 1. Project Information & Technical Specs",
        "lbl_project": "Project Name / Client Name *",
        "lbl_currency": "Currency",
        "lbl_req": "Technical Requirements & Specs *",
        "sec2_title": "📦 2. Select Switchboard Materials & Subtotal (Auto-calculated)",
        "sec2_caption": "Select required switchboard materials from the dropdown and enter quantities:",
        "lbl_item1": "Item #1",
        "lbl_item2": "Item #2",
        "col_qty": "Quantity (Qty)",
        "col_price": "Unit Price (USD)",
        "col_subtotal": "Subtotal (USD)",
        
        "prog_title": "⚡ M&E Engineering Progress & Acceptance Tracking",
        "prog_caption": "Engineering focused: Dedicated monitoring of site construction progress, acceptance status, and contract control.",
        "kpi1_title": "Total M&E Projects",
        "kpi1_val": "8 projects",
        "kpi1_sub": "↑ Active: 6 / Acceptance: 2",
        "kpi2_title": "Total Contract Value (USD)",
        "kpi2_sub": "↑ Cumulative Collected: $1,250,000",
        "kpi3_title": "Total Accounts Receivable (AR)",
        "kpi3_sub": "↑ Follow-up Required",
        "kpi4_title": "Average Engineering Progress",
        "kpi4_sub": "● Progress Normal",
        "table_header": "📋 Project Details, Progress & Acceptance Status Table",
        "col_code": "Project Code",
        "col_client": "Client / Plant",
        "col_item": "M&E Item",
        "col_total": "Contract Value (USD)",
        "col_paid": "Collected (USD)",
        "col_ar": "Receivable (USD)",
        "col_progress": "Progress (%)",
        "col_status": "Status & Acceptance"
    }
}

def get_active_lang(passed_lang):
    if passed_lang in ENG_DEPT_I18N:
        return passed_lang
    for key in ["current_lang", "lang", "language", "selected_lang"]:
        val = st.session_state.get(key)
        if val in ENG_DEPT_I18N:
            return val
    return "Tiếng Việt"

def smart_translate_project_data(text, target_lang):
    if not text or not isinstance(text, str):
        return text
    if target_lang == "Tiếng Việt":
        text = text.replace("越南新順楠梓電子廠", "Nhà máy Điện tử Tân Thuận, TP.HCM")
        text = text.replace("平陽美德金屬加工廠", "Nhà máy Cơ khí Meide Bình Dương")
        text = text.replace("隆安宏遠精密機械廠", "Nhà máy Cơ khí chính xác Hồng Viễn, Long An")
        text = text.replace("北寧富泰光電科技", "Công ty Công nghệ Quang điện FuTai, Bắc Ninh")
        text = text.replace("無塵室高低壓配電安裝與強弱電配管", "Lắp đặt tủ điện trung/hạ thế phòng sạch & ống đi dây điện nhẹ")
        text = text.replace("廠房動力配電、給排水系統與照明工程", "Hệ thống điện động lực nhà máy, cấp thoát nước & chiếu sáng")
        text = text.replace("變電站統包工程、銅排配置與空調系統配電", "Dự án trạm biến áp EPC, lắp đặt thanh cái & điện hệ thống điều hòa")
        text = text.replace("廠房大樓消防警報系統與機房不間斷電源(UPS)配電", "Hệ thống báo cháy tòa nhà & nguồn điện dự phòng UPS phòng máy")
        text = text.replace("🟢 設備安裝完成，待驗收", "🟢 Hoàn thành lắp đặt thiết bị, chờ nghiệm thu")
        text = text.replace("🟡 正在進行主幹管配線", "🟡 Đang thi công hệ thống cáp chính")
        text = text.replace("🟢 變電站主體完工", "🟢 Hoàn thành trạm biến áp chính")
        text = text.replace("🟡 機架架設與線槽施工", "🟡 Lắp đặt tủ rack và máng cáp")
    elif target_lang == "English":
        text = text.replace("越南新順楠梓電子廠", "Tan Thuan Electronics Plant, HCMC")
        text = text.replace("平陽美德金屬加工廠", "Meide Metal Processing Plant, Binh Duong")
        text = text.replace("隆安宏遠精密機械廠", "HongYuan Precision Machinery, Long An")
        text = text.replace("北寧富泰光電科技", "FuTai Optoelectronics, Bac Ninh")
        text = text.replace("無塵室高低壓配電安裝與強弱電配管", "Cleanroom switchboard installation & wiring")
        text = text.replace("廠房動力配電、給排水系統與照明工程", "Plant power distribution, plumbing & lighting")
        text = text.replace("變電站統包工程、銅排配置與空調系統配電", "Substation EPC, busbars & HVAC power")
        text = text.replace("廠房大樓消防警報系統與機房不間斷電源(UPS)配電", "Building fire alarm & server room UPS power")
        text = text.replace("🟢 設備安裝完成，待驗收", "🟢 Equipment Installed, Pending Acceptance")
        text = text.replace("🟡 正在進行主幹管配線", "🟡 Main Trunk Cabling in Progress")
        text = text.replace("🟢 變電站主體完工", "🟢 Substation Main Structure Completed")
        text = text.replace("🟡 機架架設與線槽施工", "🟡 Rack Installation & Cable Tray Works")
    return text

def render_engineering_department_page(engine=None, lang=None, default_tab=0, **kwargs):
    active_lang = get_active_lang(lang)
    L = ENG_DEPT_I18N.get(active_lang, ENG_DEPT_I18N["Tiếng Việt"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_design, tab_quote, tab_progress = st.tabs([
        L["tab_design"], L["tab_quote"], L["tab_progress"]
    ])

    # ----------------------------------------------------
    # Tab 1: 設計圖庫
    # ----------------------------------------------------
    with tab_design:
        st.markdown(f"### {L['design_title']}")
        st.caption(L['design_caption'])
        
        drawings_data = [
            {L["col_drawing_no"]: "DWG-2026-MBD-01", L["col_project_name"]: "越南新順楠梓電子廠 (M&E)", L["col_spec"]: "2000A 主配電盤 (MSB)", L["col_version"]: "V2.1", L["col_designer"]: "Nguyễn Văn An", L["col_action"]: "📥 Download CAD / PDF"},
            {L["col_drawing_no"]: "DWG-2026-MBD-02", L["col_project_name"]: "平陽美德金屬加工廠", L["col_spec"]: "1200A 動力分電盤 (Sub-DB)", L["col_version"]: "V1.0", L["col_designer"]: "Trần Minh Quân", L["col_action"]: "📥 Download CAD / PDF"},
            {L["col_drawing_no"]: "DWG-2026-MBD-03", L["col_project_name"]: "隆安宏遠精密機械廠", L["col_spec"]: "變電站 22kV 綜合控制盤", L["col_version"]: "V3.0", L["col_designer"]: "Lê Hoàng Phúc", L["col_action"]: "📥 Download CAD / PDF"},
        ]
        st.dataframe(pd.DataFrame(drawings_data), use_container_width=True)

    # ----------------------------------------------------
    # Tab 2: 配電盤估價與報價
    # ----------------------------------------------------
    with tab_quote:
        st.markdown(f"### {L['quote_title']}")
        st.caption(L['quote_caption'])
        
        st.markdown(f"### {L['sec1_title']}")
        c1, c2 = st.columns([3, 1])
        with c1:
            proj_name = st.text_input(L["lbl_project"], value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A" if active_lang == "Tiếng Việt" else "西寧紡織廠 2000A 主配電盤新建工程")
        with c2:
            currency = st.selectbox(L["lbl_currency"], ["USD", "VND", "TWD", "EUR"])

        req_desc = st.text_area(L["lbl_req"], value="Bao gồm gia công thanh cái đồng, lắp đặt ACB 2000A và kiểm tra cách điện." if active_lang == "Tiếng Việt" else "包含高純度銅排母線加工、2000A ACB 空氣斷路器組裝與現場耐壓絕緣測試。")

        st.markdown(f"### {L['sec2_title']}")
        st.caption(L['sec2_caption'])

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

    # ----------------------------------------------------
    # Tab 3: 工程驗收與進度追蹤
    # ----------------------------------------------------
    with tab_progress:
        st.markdown(f"### {L['prog_title']}")
        st.caption(L['prog_caption'])

        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            st.metric(label=L["kpi1_title"], value=L["kpi1_val"], delta=L["kpi1_sub"])
        with kc2:
            st.metric(label=L["kpi2_title"], value="$1,850,000", delta=L["kpi2_sub"])
        with kc3:
            st.metric(label=L["kpi3_title"], value="$600,000", delta=L["kpi3_sub"])
        with kc4:
            st.metric(label=L["kpi4_title"], value="76.5%", delta=L["kpi4_sub"])

        st.markdown("---")
        st.markdown(f"### {L['table_header']}")

        raw_data = [
            {"code": "PRJ-2026-01", "client": "越南新順楠梓電子廠 (XinShun Electronics)", "item": "無塵室高低壓配電安裝與強弱電配管", "total": 450000, "paid": 315000, "ar": 135000, "progress": 90, "status": "🟢 設備安裝完成，待驗收"},
            {"code": "PRJ-2026-02", "client": "平陽美德金屬加工廠 (Meide Metal)", "item": "廠房動力配電、給排水系統與照明工程", "total": 380000, "paid": 228000, "ar": 152000, "progress": 75, "status": "🟡 正在進行主幹管配線"},
            {"code": "PRJ-2026-03", "client": "隆安宏遠精密機械廠 (HongYuan Precision)", "item": "變電站統包工程、銅排配置與空調系統配電", "total": 620000, "paid": 434000, "ar": 186000, "progress": 85, "status": "🟢 變電站主體完工"},
            {"code": "PRJ-2026-04", "client": "北寧富泰光電科技 (FuTai Optoelectronics)", "item": "廠房大樓消防警報系統與機房不間斷電源(UPS)配電", "total": 400000, "paid": 273000, "ar": 127000, "progress": 55, "status": "🟡 機架架設與線槽施工"}
        ]

        display_data = []
        for item in raw_data:
            display_data.append({
                L["col_code"]: item["code"],
                L["col_client"]: smart_translate_project_data(item["client"], active_lang),
                L["col_item"]: smart_translate_project_data(item["item"], active_lang),
                L["col_total"]: f"${item['total']:,.0f}",
                L["col_paid"]: f"${item['paid']:,.0f}",
                L["col_ar"]: f"${item['ar']:,.0f}",
                L["col_progress"]: f"{item['progress']}%",
                L["col_status"]: smart_translate_project_data(item["status"], active_lang)
            })

        st.dataframe(pd.DataFrame(display_data), use_container_width=True)

# ----------------------------------------------------
# 萬用相容函式與分身 (確保無論 app.py 呼叫哪一個都 100% 成功)
# ----------------------------------------------------
def render_engineering_department(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_page(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_quotation_page(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs, default_tab=1)

def render_project_tracking(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs, default_tab=2)

def show(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)
