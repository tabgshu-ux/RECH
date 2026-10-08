import streamlit as st
import pandas as pd
import datetime
import os

# ----------------------------------------------------
# 🌐 工程管理中心與設計部門多語系字典 (i18n)
# ----------------------------------------------------
ENG_DEPT_I18N = {
    "繁體中文": {
        "title": "🛠️ 裕豐電機工業 - 工程管理中心與設計部門",
        "caption": "涵蓋工程報價系統（含倉庫連動、業務議價與一鍵傳動 AR）、設計圖庫 Storage 上傳中心、及工程驗收追蹤。",
        
        # 報價系統
        "quote_title": "⚙️ 配電盤與工程專案報價系統 (Quotation, Discount & AR Transfer)",
        "quote_caption": "工程管理專用報價：填入專案資訊、連動倉庫庫存與單價，支援業務折讓議價，並一鍵傳動至財務應收帳款。",
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
        
        "sec3_title": "💰 3. 金額加總、發票稅 (VAT) 與業務議價減免",
        "lbl_subtotal_sum": "未稅金額總計 (Subtotal):",
        "lbl_vat_rate": "發票稅率 (VAT %)",
        "lbl_vat_amount": "營業稅金額 (VAT Amount):",
        "lbl_system_total": "系統計算含稅總額:",
        "lbl_final_override": "✍️ 業務最終議價/折讓後報價總金額 (可手動修改減免):",
        "btn_transfer_ar": "🚀 一鍵傳動至財務應收帳款 (AR) 系統",
        "success_ar": "✅ 成功！工程報價已成功傳動至財務部應收帳款（AR）模組！",
        
        # 設計圖庫 Storage
        "design_title": "📐 配電盤電氣與機構設計圖庫 Storage 雲端中心",
        "design_caption": "設計工程師可在此上傳 CAD/PDF/圖片圖檔至公司內部 Storage，供管理中心與各廠區直接下載。",
        "upload_header": "📤 上傳新設計圖檔至公司 Storage",
        "lbl_dwg_no": "圖號編碼 *",
        "lbl_dwg_name": "專案/圖檔名稱 *",
        "lbl_file_uploader": "選擇設計圖檔 (PDF, CAD, PNG, JPG)",
        "btn_upload": "💾 儲存並上傳至公司 Storage",
        "success_upload": "✅ 圖檔已成功上傳至公司內部 Storage，管理中心現可隨時下載！",
        "storage_header": "📂 公司內部 Storage 現有圖庫列表",
        "col_drawing_no": "圖號編碼",
        "col_project_name": "專案/廠區名稱",
        "col_spec": "檔案名稱",
        "col_version": "上傳時間",
        "col_designer": "上傳人員",
        "col_action": "圖檔下載",
        
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
        "title": "🛠️ REETECH INDUSTRIAL - Trung tâm Quản lý & Phòng Thiết kế",
        "caption": "Bao gồm báo giá, kho lưu trữ Storage bản vẽ thiết kế, và theo dõi tiến độ nghiệm thu.",
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
        "sec3_title": "💰 3. Tổng hợp, Thuế VAT & Chiết khấu Kinh doanh",
        "lbl_subtotal_sum": "Tổng giá trị chưa thuế (Subtotal):",
        "lbl_vat_rate": "Thuế suất VAT (%)",
        "lbl_vat_amount": "Tiền thuế VAT:",
        "lbl_system_total": "Tổng tiền tính toán tự động:",
        "lbl_final_override": "✍️ Tổng giá trị báo giá cuối cùng sau chiết khấu:",
        "btn_transfer_ar": "🚀 Truyền dữ liệu sang Phải thu Tài chính (AR)",
        "success_ar": "✅ Thành công! Báo giá đã được truyền sang hệ thống Quản lý Phải thu (AR) của Tài chính!",
        "design_title": "📐 Kho Lưu trữ Storage Bản vẽ Thiết kế Điện & Cơ khí",
        "design_caption": "Kỹ sư thiết kế tải lên bản vẽ CAD/PDF lên Storage công ty để bộ phận quản lý tải về.",
        "upload_header": "📤 Tải lên bản vẽ mới vào Storage công ty",
        "lbl_dwg_no": "Mã bản vẽ *",
        "lbl_dwg_name": "Tên dự án / Bản vẽ *",
        "lbl_file_uploader": "Chọn tệp bản vẽ (PDF, CAD, PNG, JPG)",
        "btn_upload": "💾 Lưu và Tải lên Storage",
        "success_upload": "✅ Tệp đã được tải lên Storage thành công, bộ phận quản lý có thể tải về!",
        "storage_header": "📂 Danh sách bản vẽ hiện có trong Storage",
        "col_drawing_no": "Mã bản vẽ",
        "col_project_name": "Tên dự án / Nhà máy",
        "col_spec": "Tên tệp",
        "col_version": "Thời gian",
        "col_designer": "Người tải lên",
        "col_action": "Tải xuống",
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
        "title": "🛠️ REETECH INDUSTRIAL - Engineering Center & Design Dept",
        "caption": "Quotation system, design storage center for uploading/downloading drawings, and acceptance tracking.",
        "quote_title": "⚙️ Switchgear & Engineering Project Quotation System (AR Integration)",
        "quote_caption": "Engineering quotation: Linked to warehouse inventory, allows sales discount adjustments, VAT calculation, and direct transfer to Finance AR.",
        "sec1_title": "📋 1. Project Basic Information",
        "lbl_vendor": "Vendor / Client Name *",
        "vendor_placeholder": "Example: Tan Shuan Engineering Co., Ltd.",
        "lbl_project": "Project Name / Work Name *",
        "proj_placeholder": "Example: Tay Ninh Textile Plant - 2000A Switchboard",
        "lbl_location": "Project Location / Plant Site *",
        "loc_placeholder": "Example: Trang Bang Industrial Zone, Tay Ninh, Vietnam",
        "lbl_currency": "Currency",
        "sec2_title": "📦 2. Quotation Item Details (Linked to Warehouse Stock & Pricing)",
        "sec2_caption": "Select required electrical materials, system auto-retrieves warehouse remaining stock and unit price:",
        "sec3_title": "💰 3. Subtotal, VAT & Sales Discount Override",
        "lbl_subtotal_sum": "Subtotal (Excluding Tax):",
        "lbl_vat_rate": "VAT Rate (%)",
        "lbl_vat_amount": "VAT Amount:",
        "lbl_system_total": "System Calculated Total:",
        "lbl_final_override": "✍️ Final Quoted Amount after Sales Discount:",
        "btn_transfer_ar": "🚀 Transfer to Finance Accounts Receivable (AR)",
        "success_ar": "✅ Success! Engineering quotation successfully transferred to Finance AR module!",
        "design_title": "📐 Switchgear & Mechanical Design Drawings Storage Center",
        "design_caption": "Design engineers can upload CAD/PDF/image drawings to corporate storage for management download.",
        "upload_header": "📤 Upload New Design Drawing to Storage",
        "lbl_dwg_no": "Drawing No. *",
        "lbl_dwg_name": "Project / Drawing Name *",
        "lbl_file_uploader": "Select Drawing File (PDF, CAD, PNG, JPG)",
        "btn_upload": "💾 Save & Upload to Storage",
        "success_upload": "✅ File successfully uploaded to corporate storage, management can now download!",
        "storage_header": "📂 Corporate Storage Drawings Repository",
        "col_drawing_no": "Drawing No.",
        "col_project_name": "Project / Plant Name",
        "col_spec": "File Name",
        "col_version": "Upload Time",
        "col_designer": "Uploader",
        "col_action": "Download",
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
        text = text.replace("越南新順楠梓電子廠", "Tan Shuan Electronics Plant, HCMC")
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

def render_engineering_department_page(engine=None, lang=None, **kwargs):
    active_lang = get_active_lang(lang)
    L = ENG_DEPT_I18N.get(active_lang, ENG_DEPT_I18N["Tiếng Việt"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🎯 智慧偵測左側選單點選的子功能（自動同時相容多種主程式傳參方式）
    sub_action = (
        kwargs.get("sub_action") 
        or st.session_state.get("current_sub_action") 
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "quote"
    )
    
    # 如果主程式傳進來的參數包含中文或越文關鍵字，自動轉換為對應識別碼
    sub_str = str(sub_action)
    if "進度" in sub_str or "Progress" in sub_str or "Nghiệm thu" in sub_str:
        current_mode = "progress"
    elif "日報" in sub_str or "Daily" in sub_str or "Báo cáo" in sub_str:
        current_mode = "daily"
    elif "設計" in sub_str or "Storage" in sub_str or "Thiết kế" in sub_str or "圖庫" in sub_str:
        current_mode = "design"
    else:
        current_mode = "quote"

    # ----------------------------------------------------
    # 1. 📋 [工程] 配電盤與工程專案報價
    # ----------------------------------------------------
    if current_mode == "quote":
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

        final_quoted_amount = st.number_input(
            L["lbl_final_override"],
            min_value=0.0,
            value=float(system_grand_total),
            step=100.0
        )

        st.markdown("---")
        if st.button(L["btn_transfer_ar"], use_container_width=True, type="primary"):
            st.success(L["success_ar"])
            st.info(f"📌 **傳動詳情 (Transferred to AR)**: {vendor_name} | {proj_name} | 最終報價金額: **${final_quoted_amount:,.2f} {currency}** (含 VAT {vat_rate}%)")

    # ----------------------------------------------------
    # 2. 📊 [工程] 水電工程驗收與進度追蹤
    # ----------------------------------------------------
    elif current_mode == "progress":
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
                L["col_total"]: f"${item['total']:,.2f}",
                L["col_paid"]: f"${item['paid']:,.2f}",
                L["col_ar"]: f"${item['ar']:,.2f}",
                L["col_progress"]: f"{item['progress']}%",
                L["col_status"]: smart_translate_project_data(item["status"], active_lang)
            })
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)

    # ----------------------------------------------------
    # 3. 📝 [工程] 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif current_mode == "daily":
        st.markdown("### 📝 現場工程日報表與出工統計 (Daily Construction Reports)")
        st.caption("記錄每日台幹與越籍工人出工數、施工進度摘要與工地異常狀況回報。")
        
        if "daily_reports" not in st.session_state:
            st.session_state.daily_reports = [
                {"日期": "2026-10-07", "案場": "越南西寧廠", "出工台幹": "admin", "越籍工人數": 18, "當日施工摘要": "完成 A 棟車間主母線銅排架設與耐壓測試。", "異常狀況": "無"}
            ]
        
        st.dataframe(pd.DataFrame(st.session_state.daily_reports), use_container_width=True)

        with st.form("form_add_daily_site"):
            dc1, dc2 = st.columns(2)
            with dc1:
                d_date = st.date_input("施工日期 (Date)", value=datetime.date.today())
                d_plant = st.selectbox("案場廠區", ["越南西寧廠 (Tay Ninh)", "越南海防廠 (Hai Phong)", "外部工程工地"])
            with dc2:
                d_leader = st.text_input("負責台幹", value=st.session_state.get("current_user", "admin"))
                d_workers = st.number_input("越籍工人數 (Workers Count)", min_value=1, value=12, step=1)
            
            d_summary = st.text_area("當日施工摘要 (Work Summary)", placeholder="例如: 進行配電盤銅排組裝與穿線作業")
            
            if st.form_submit_button("💾 提交現場施工日報表", type="primary", use_container_width=True):
                st.session_state.daily_reports.insert(0, {
                    "日期": d_date.strftime("%Y-%m-%d"),
                    "案場": d_plant,
                    "出工台幹": d_leader,
                    "越籍工人數": d_workers,
                    "當日施工摘要": d_summary,
                    "異常狀況": "無"
                })
                st.success("✅ 現場施工日報表已成功送出與歸檔！")
                st.rerun()

    # ----------------------------------------------------
    # 4. 📐 [設計] 配電盤電氣與機構設計圖庫 Storage
    # ----------------------------------------------------
    elif current_mode == "design":
        st.markdown(f"### {L['design_title']}")
        st.caption(L['design_caption'])
        
        if "storage_drawings" not in st.session_state:
            st.session_state.storage_drawings = [
                {L["col_drawing_no"]: "DWG-2026-MBD-01", L["col_project_name"]: "越南新順楠梓電子廠 (M&E)", L["col_spec"]: "MSB_2000A_Schematic.pdf", L["col_version"]: "2026-10-01 10:30", L["col_designer"]: "Nguyễn Văn An", L["col_action"]: "📥 Download"},
                {L["col_drawing_no"]: "DWG-2026-MBD-02", L["col_project_name"]: "平陽美德金屬加工廠", L["col_spec"]: "Sub_DB_Layout.dwg", L["col_version"]: "2026-10-03 14:15", L["col_designer"]: "Trần Minh Quân", L["col_action"]: "📥 Download"},
                {L["col_drawing_no"]: "DWG-2026-MBD-03", L["col_project_name"]: "隆安宏遠精密機械廠", L["col_spec"]: "Substation_Busbar.png", L["col_version"]: "2026-10-05 09:00", L["col_designer"]: "Lê Hoàng Phúc", L["col_action"]: "📥 Download"},
            ]

        with st.form("upload_storage_form"):
            st.markdown(f"#### {L['upload_header']}")
            u_col1, u_col2 = st.columns(2)
            with u_col1:
                new_dwg_no = st.text_input(L["lbl_dwg_no"], placeholder="例如: DWG-2026-04")
            with u_col2:
                new_proj_name = st.text_input(L["lbl_dwg_name"], placeholder="例如: 北寧富泰光電廠配電盤圖")
            
            uploaded_file = st.file_uploader(L["lbl_file_uploader"], type=["pdf", "dwg", "png", "jpg", "zip"])
            
            submitted_upload = st.form_submit_button(L["btn_upload"], use_container_width=True)
            if submitted_upload:
                if new_dwg_no and new_proj_name and uploaded_file:
                    file_info = {
                        L["col_drawing_no"]: new_dwg_no,
                        L["col_project_name"]: new_proj_name,
                        L["col_spec"]: uploaded_file.name,
                        L["col_version"]: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        L["col_designer"]: st.session_state.get("user_name", "Designer"),
                        L["col_action"]: "📥 Download"
                    }
                    st.session_state.storage_drawings.insert(0, file_info)
                    st.success(L["success_upload"])
                else:
                    st.warning("⚠️ 請完整填寫圖號編碼、專案名稱並選擇要上傳的圖檔檔案！")

        st.markdown("---")
        st.markdown(f"#### {L['storage_header']}")
        st.dataframe(pd.DataFrame(st.session_state.storage_drawings), use_container_width=True)

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_department(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)
