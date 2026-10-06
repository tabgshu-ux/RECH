import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 工程部專屬模組多語系字典 (i18n)
# ----------------------------------------------------
ENG_DEPT_I18N = {
    "繁體中文": {
        "title": "🛠️ 裕豐電機工業 - 工程部綜合管理中心",
        "caption": "完整涵蓋工程報價系統（含倉庫連動、業務議價折讓、發票稅與一鍵傳動 AR）、設計圖庫、及工程驗收追蹤。",
        "tab_quote": "⚙️ 1. 工程報價系統 (含業務議價與傳動 AR)",
        "tab_design": "📐 2. 設計圖庫與規格",
        "tab_progress": "📊 3. 工程驗收與進度追蹤",
        
        # 報價系統
        "quote_title": "⚙️ 配電盤與工程專案報價系統 (Quotation, Discount & AR Transfer)",
        "quote_caption": "工程部專用報價：填入專案資訊、連動倉庫庫存與單價，支援業務折讓議價，並一鍵傳動至財務應收帳款。",
        "sec1_title": "📋 1. 工程專案基本資訊",
        "lbl_vendor": "廠商名稱 *",
        "vendor_placeholder": "例如: 越南新順工程承攬有限公司",
        "lbl_project": "工程名稱 / 專案名稱 *",
        "proj_placeholder": "例如: 西寧紡織廠 2000A 主配電盤新建工程",
        "lbl_location": "工程位置 / 廠區地點 *",
        "loc_placeholder": "例如: 越南 Tây Ninh 省張幫工業區 A2 廠房",
        "lbl_currency": "計價幣別",
        
        "sec2_title": "📦 2. 報價內容明細 (連動倉庫庫存與金額)",
        "sec2_caption": "選取所需配電資材，系統將自動讀取倉庫剩餘數量、單價並計算小計：",
        "col_item_code": "物料編號",
        "col_item_name": "報價內容 / 資材品項",
        "col_warehouse_stock": "倉庫剩餘數量",
        "col_qty": "報價數量 (Qty)",
        "col_unit_price": "倉庫單價 (USD)",
        "col_subtotal": "金額小計 (USD)",
        
        "sec3_title": "💰 3. 金額加總、發票稅 (VAT) 與業務議價減免",
        "lbl_subtotal_sum": "未稅金額總計 (Subtotal):",
        "lbl_vat_rate": "發票稅率 (VAT %)",
        "lbl_vat_amount": "營業稅金額 (VAT Amount):",
        "lbl_system_total": "系統計算含稅總額:",
        "lbl_final_override": "✍️ 業務最終議價/折讓後報價總金額 (可手動修改減免):",
        "btn_transfer_ar": "🚀 一鍵傳動至財務應收帳款 (AR) 系統",
        "success_ar": "✅ 成功！工程報價已成功傳動至財務部應收帳款（AR）模組！",
        
        # 設計圖庫
        "design_title": "📐 配電盤電氣與機構設計圖庫",
        "design_caption": "管理各廠區高低壓配電盤、ACB/MCCB、Busbar 銅排配置與 CAD/PDF 設計圖檔。",
        "col_drawing_no": "圖號編碼",
        "col_project_name": "專案/廠區名稱",
        "col_spec": "電氣規格",
        "col_version": "版次",
        "col_designer": "設計工程師",
        "col_action": "圖檔操作",
        
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
        "caption": "Bao gồm hệ thống báo giá, chiết khấu thương mại cho nhân viên kinh doanh, thuế VAT và truyền dữ liệu sang AR.",
        "tab_quote": "⚙️ 1. Hệ thống Báo giá (Chiết khấu & AR)",
        "tab_design": "📐 2. Thư viện Bản vẽ Thiết kế",
        "tab_progress": "📊 3. Theo dõi Tiến độ & Nghiệm thu",
        
        "quote_title": "⚙️ Hệ thống Báo giá & Chiết khấu Thương mại (Chuyển dữ liệu AR)",
        "quote_caption": "Hệ thống báo giá: Liên kết kho, cho phép kinh doanh chiết khấu/giảm giá, tính thuế VAT và chuyển sang tài chính.",
        "sec1_title": "📋 1. Thông tin Dự án",
        "lbl_vendor": "Tên Nhà thầu / Khách hàng *",
        "vendor_placeholder": "Ví dụ: Công ty TNHH Xây lắp Tân Thuận",
        "lbl_project": "Tên Dự án / Công trình *",
        "proj_placeholder": "Ví dụ: Nhà máy dệt Tây Ninh - Tủ điện 2000A",
        "lbl_location": "Địa điểm công trình / Nhà máy *",
        "loc_placeholder": "Ví dụ: KCN Trảng Bàng, Tây Ninh, Việt Nam",
        "lbl_currency": "Loại tiền tệ",
        
        "sec2_title": "📦 2. Chi tiết Nội dung Báo giá (Liên kết Tồn kho & Đơn giá)",
        "sec2_caption": "Chọn vật tư thiết bị, hệ thống tự động đọc số lượng tồn kho và đơn giá:",
        "col_item_code": "Mã vật tư",
        "col_item_name": "Nội dung báo giá / Tên vật tư",
        "col_warehouse_stock": "Tồn kho hiện tại",
        "col_qty": "Số lượng báo giá (Qty)",
        "col_unit_price": "Đơn giá kho (USD)",
        "col_subtotal": "Thành tiền (USD)",
        
        "sec3_title": "💰 3. Tổng hợp, Thuế VAT & Chiết khấu Kinh doanh",
        "lbl_subtotal_sum": "Tổng giá trị chưa thuế (Subtotal):",
        "lbl_vat_rate": "Thuế suất VAT (%)",
        "lbl_vat_amount": "Tiền thuế VAT:",
        "lbl_system_total": "Tổng tiền tính toán tự động:",
        "lbl_final_override": "✍️ Tổng giá trị báo giá cuối cùng sau chiết khấu (Kinh doanh có thể chỉnh sửa):",
        "btn_transfer_ar": "🚀 Truyền dữ liệu sang Phải thu Tài chính (AR)",
        "success_ar": "✅ Thành công! Báo giá đã được truyền sang hệ thống Quản lý Phải thu (AR) của Tài chính!",
        
        "design_title": "📐 Thư viện Bản vẽ Thiết kế Tủ điện & Cơ khí",
        "design_caption": "Quản lý bản vẽ CAD/PDF tủ điện trung hạ thế, ACB/MCCB, thanh cái Busbar.",
        "col_drawing_no": "Mã bản vẽ",
        "col_project_name": "Tên dự án / Nhà máy",
        "col_spec": "Quy cách điện",
        "col_version": "Phiên bản",
        "col_designer": "Kỹ sư thiết kế",
        "col_action": "Thao tác",
        
        "prog_title": "⚡ Theo dõi Tiến độ & Nghiệm thu Dự án Cơ điện",
        "prog_caption": "Chuyên dụng kỹ thuật: Tập trung giám sát phần trăm tiến độ thi công, trạng thái nghiệm thu.",
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
        "caption": "Engineering quotation with sales discount override, VAT calculation, and direct AR transfer.",
        "tab_quote": "⚙️️ 1. Quotation System (Sales Discount & AR)",
        "tab_design": "📐 2. Design Drawings Library",
        "tab_progress": "📊 3. M&E Acceptance & Progress Tracking",
        
        "quote_title": "⚙️ Switchgear & Engineering Project Quotation System (AR Integration)",
        "quote_caption": "Engineering quotation: Linked to warehouse inventory, allows sales discount adjustments, VAT calculation, and direct transfer to Finance AR.",
        "sec1_title": "📋 1. Project Basic Information",
        "lbl_vendor": "Vendor / Client Name *",
        "vendor_placeholder": "Example: Tan Thuan M&E Engineering Co., Ltd.",
        "lbl_project": "Project Name / Work Name *",
        "proj_placeholder": "Example: Tay Ninh Textile Plant - 2000A Switchboard",
        "lbl_location": "Project Location / Plant Site *",
        "loc_placeholder": "Example: Trang Bang Industrial Zone, Tay Ninh, Vietnam",
        "lbl_currency": "Currency",
        
        "sec2_title": "📦 2. Quotation Item Details (Linked to Warehouse Stock & Pricing)",
        "sec2_caption": "Select required electrical materials, system auto-retrieves warehouse remaining stock and unit price:",
        "col_item_code": "Item Code",
        "col_item_name": "Quotation Content / Material Name",
        "col_warehouse_stock": "Warehouse Stock",
        "col_qty": "Quoted Qty",
        "col_unit_price": "Warehouse Unit Price (USD)",
        "col_subtotal": "Subtotal (USD)",
        
        "sec3_title": "💰 3. Subtotal, VAT & Sales Discount Override",
        "lbl_subtotal_sum": "Subtotal (Excluding Tax):",
        "lbl_vat_rate": "VAT Rate (%)",
        "lbl_vat_amount": "VAT Amount:",
        "lbl_system_total": "System Calculated Total:",
        "lbl_final_override": "✍️ Final Quoted Amount after Sales Discount (Editable for negotiation):",
        "btn_transfer_ar": "🚀 Transfer to Finance Accounts Receivable (AR)",
        "success_ar": "✅ Success! Engineering quotation successfully transferred to Finance AR module!",
        
        "design_title": "📐 Switchgear & Mechanical Design Drawings Library",
        "design_caption": "Manage CAD/PDF drawings for switchboards, ACB/MCCB, and Busbar configurations.",
        "col_drawing_no": "Drawing No.",
        "col_project_name": "Project / Plant Name",
        "col_spec": "Electrical Spec",
        "col_version": "Version",
        "col_designer": "Designer",
        "col_action": "Action",
        
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

    tab_quote, tab_design, tab_progress = st.tabs([
        L["tab_quote"], L["tab_design"], L["tab_progress"]
    ])

    # ----------------------------------------------------
    # Tab 1: 工程報價系統 (含倉庫連動、業務議價折讓、發票稅與 AR 傳動)
    # ----------------------------------------------------
    with tab_quote:
        st.markdown(f"### {L['quote_title']}")
        st.caption(L['quote_caption'])
        
        st.markdown(f"### {L['sec1_title']}")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            vendor_name = st.text_input(L["lbl_vendor"], placeholder=L["vendor_placeholder"], value="Công ty TNHH Xây lắp Tân Thuận")
        with c2:
            proj_name = st.text_input(L["lbl_project"], placeholder=L["proj_placeholder"], value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A")
        with c3:
            currency = st.selectbox(L["lbl_currency"], ["USD", "VND", "TWD", "EUR"])

        loc_name = st.text_input(L["lbl_location"], placeholder=L["loc_placeholder"], value="KCN Trảng Bàng, Tây Ninh, Việt Nam")

        st.markdown(f"### {L['sec2_title']}")
        st.caption(L['sec2_caption'])

        warehouse_items = [
            {"code": "CU-BUS-10100", "name": "銅排 Busbar 10x100mm (高純度)", "stock": 450.0, "price": 12.50},
            {"code": "CB-ACB-2000A", "name": "空氣斷路器 ACB 2000A (Schneider)", "stock": 8.0, "price": 1850.00},
            {"code": "CB-MCCB-250A", "name": "塑殼斷路器 MCCB 250A (LS/Schneider)", "stock": 35.0, "price": 145.00},
            {"code": "CAB-PVC-4CX95", "name": "控制電纜 PVC 4Cx95mm²", "stock": 1200.0, "price": 8.20}
        ]

        subtotal_sum = 0.0
        for idx, wh in enumerate(warehouse_items):
            cols = st.columns([1.2, 2.5, 1.2, 1.2, 1.2, 1.5])
            with cols[0]:
                st.text_input(f"Code {idx}", value=wh["code"], disabled=True, label_visibility="collapsed")
            with cols[1]:
                st.text_input(f"Name {idx}", value=wh["name"], disabled=True, label_visibility="collapsed")
            with cols[2]:
                st.metric(label="Stock", value=f"{wh['stock']:,.1f}", label_visibility="collapsed")
            with cols[3]:
                qty = st.number_input(f"Qty {idx}", min_value=0.0, value=150.0 if idx == 0 else (2.0 if idx == 1 else 0.0), step=1.0, label_visibility="collapsed")
            with cols[4]:
                st.text_input(f"Price {idx}", value=f"${wh['price']:,.2f}", disabled=True, label_visibility="collapsed")
            with cols[5]:
                line_total = qty * wh["price"]
                subtotal_sum += line_total
                st.text_input(f"Sub {idx}", value=f"${line_total:,.2f}", disabled=True, label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"### {L['sec3_title']}")
        
        q_c1, q_c2 = st.columns(2)
        with q_c1:
            st.metric(label=L["lbl_subtotal_sum"], value=f"${subtotal_sum:,.2f}")
            vat_rate = st.selectbox(L["lbl_vat_rate"], [10, 8, 0, 5], index=0)
        with q_c2:
            vat_amount = subtotal_sum * (vat_rate / 100.0)
            system_grand_total = subtotal_sum + vat_amount
            st.metric(label=L["lbl_vat_amount"], value=f"${vat_amount:,.2f}")
            st.metric(label=L["lbl_system_total"], value=f"${system_grand_total:,.2f}")

        # 業務員減免與最終議價總金額輸入框
        final_quoted_amount = st.number_input(
            L["lbl_final_override"],
            min_value=0.0,
            value=float(system_grand_total),
            step=100.0,
            help="業務員可在此輸入減免後的最終議價總金額"
        )

        st.markdown("---")
        if st.button(L["btn_transfer_ar"], use_container_width=True, type="primary"):
            st.success(L["success_ar"])
            st.info(f"📌 **傳動詳情 (Transferred to AR)**: {vendor_name} | {proj_name} | 最終報價金額: **${final_quoted_amount:,.2f} {currency}** (含 VAT {vat_rate}%)")

    # ----------------------------------------------------
    # Tab 2: 設計圖庫
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
# 萬用相容函式與分身
# ----------------------------------------------------
def render_engineering_department(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_page(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_quotation_page(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs, default_tab=0)

def render_project_tracking(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs, default_tab=2)

def show(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)
