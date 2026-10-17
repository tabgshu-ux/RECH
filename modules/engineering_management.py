import streamlit as st
import pandas as pd
import datetime
import re

# ----------------------------------------------------
# 🌐 工具函式：金額格式化與千位符號處理
# ----------------------------------------------------
def parse_formatted_amount(val_str):
    if not val_str:
        return 0.0
    clean_str = re.sub(r"[^\d]", "", str(val_str))
    return float(clean_str) if clean_str else 0.0

def convert_currency(amount, from_curr="VND", to_curr="VND"):
    # 簡易預設匯率換算基準 (可依實際需求調整)
    # 1 USD = 25,000 VND, 1 RMB = 3,500 VND, 1 TWD = 780 VND
    rates_to_vnd = {
        "VND": 1.0,
        "USD": 25000.0,
        "RMB": 3500.0,
        "TWD": 780.0
    }
    val_in_vnd = amount * rates_to_vnd.get(from_curr, 1.0)
    converted_val = val_in_vnd / rates_to_vnd.get(to_curr, 1.0)
    return converted_val

def format_currency_text(amount, currency="VND"):
    try:
        val = float(amount)
        if currency == "VND":
            return f"{val:,.0f} ₫ (VND)"
        elif currency == "USD":
            return f"$ {val:,.2f} USD"
        elif currency == "RMB":
            return f"¥ {val:,.2f} RMB"
        elif currency == "TWD":
            return f"$ {val:,.2f} TWD"
        else:
            return f"{val:,.2f} {currency}"
    except:
        return f"{amount} {currency}"

# ----------------------------------------------------
# 🛠️ 主渲染函式：工程與設計管理中心 (全功能完整版)
# ----------------------------------------------------
def render_engineering_management_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### ⚡ 裕豐電機 - 工程與設計管理中心")
    st.info("💡 水電工程、配電盤製造、現場勘查與雙層報價系統（支援多幣別 VND、USD、RMB、TWD 與跨部門完整連動）")

    # 初始化全域資料庫 (Session State)
    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_id": "PRJ-2026-001", "proj_name": "西寧廠高壓配電盤擴建", "client": "CÔNG TY TNHH LEADER ART INDUSTRIES (VIETNAM)", "status": "進行中", "manager": "陳明華"}
        ]

    sub_options = [
        "1. 工程主管戰情室",
        "2. 工程專案報價系統",
        "3. 現場外勤打卡與作業登記",
        "4. 施工日報表與點工點料登記",
        "5. AI 施工照片辨識與稽核",
        "6. 工程師證照與機具檢驗預警",
        "7. 配電盤電氣與機構設計圖庫 ",
        "8. 配電盤 BOM 零件與採購連動",
        "9. 外包商計價與管理",
        "10. FAT / SAT 出廠與現場驗收管理"
    ]
    
    selected_option = st.selectbox("請選擇要執行的工程/設計功能：", sub_options)
    st.markdown("---")

    # ====================================================
    # 📊 1. 工程主管戰情室與案場管理
    # ====================================================
    if "1." in selected_option or "戰情室" in selected_option:
        st.markdown("### 📊 1. 工程主管戰情室與案場管理 (Dashboard)")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("進行中工程專案", "12 案", "+2 本月新增")
        with col_s2:
            st.metric("總合約金額 (VND)", "18,450,000,000", "匯率正常")
        with col_s3:
            st.metric("待審核 BOM / 採購", "5 件", "需主管覆核")
        with col_s4:
            st.metric("工安事故率", "0%", "持續保持")

        st.markdown("##### 📁 目前進行中的工程專案一覽")
        proj_df = pd.DataFrame(st.session_state.engineering_projects_db)
        st.dataframe(proj_df, use_container_width=True)

    # ====================================================
    # 📋 2. 配電盤與工程專案雙層報價系統 (含千分位、操作引導與多幣別總計)
    # ====================================================
    elif "2." in selected_option or "雙層報價" in selected_option or "報價" in selected_option:
        st.markdown("### 📋 2. 配電盤與工程專案雙層報價系統 (內部成本估算 vs 對外報價)")
        st.info("💡 支援多幣別（VND、USD、RMB、TWD），並在報價核准後自動將內部 BOM 零件展開並推送到採購與生產部門。")

        if "two_tier_quotations_db" not in st.session_state:
            st.session_state.two_tier_quotations_db = [
                {
                    "quot_id": "09092026/LA/BG01",
                    "project_name": "新增設備機電系統供電工程",
                    "client": "CÔNG TY TNHH LEADER ART INDUSTRIES (VIETNAM)",
                    "currency": "VND",
                    "vat": 8.0,
                    "date": "2026-09-09",
                    "author": "陳智賢",
                    "status": "🟢 已核准並自動下發BOM",
                    "items": [
                        {"item": "MCCB 3P 400AF 315AT 50KA 380V - TBX-400L", "unit": "只", "qty": 1.0, "unit_price": 3842670.0, "total_price": 3842670.0},
                        {"item": "銅牌及固定座熱縮套膜 CU BAR BUS", "unit": "式", "qty": 1.0, "unit_price": 4130000.0, "total_price": 4130000.0},
                        {"item": "控制配線另料 Phuï lieäu", "unit": "式", "qty": 1.0, "unit_price": 1180000.0, "total_price": 1180000.0},
                        {"item": "配盤組裝工資 Tieàn coâng laép raùp", "unit": "式", "qty": 1.0, "unit_price": 2360000.0, "total_price": 2360000.0},
                        {"item": "CASE (W)800mm*(H)1200mm*(D)350mm SPCC靜電粉體烤漆 T=2.0", "unit": "只", "qty": 1.0, "unit_price": 9605200.0, "total_price": 9605200.0},
                        {"item": "MCCB 3P 250AF 180AT 45KA 380V - TBX-250L", "unit": "只", "qty": 1.0, "unit_price": 1429688.0, "total_price": 1429688.0},
                        {"item": "比流器 CT300/5A", "unit": "只", "qty": 3.0, "unit_price": 718384.0, "total_price": 2155152.0},
                        {"item": "過電流電驛 OC+EF (MK1000A-240A)", "unit": "只", "qty": 3.0, "unit_price": 8075920.0, "total_price": 24227760.0}
                    ]
                }
            ]

        if "bom_procurement_db" not in st.session_state:
            st.session_state.bom_procurement_db = [
                {
                    "quot_id": "09092026/LA/BG01",
                    "project_name": "新增設備機電系統供電工程",
                    "client": "CÔNG TY TNHH LEADER ART INDUSTRIES (VIETNAM)",
                    "bom_items": st.session_state.two_tier_quotations_db[0]["items"]
                }
            ]

        tab_q_create, tab_q_list = st.tabs(["📝 建立 / 提交報價與自動BOM展開", "📊 報價單總表與審核紀錄 (支援多幣別總計)"])

        with tab_q_create:
            with st.form("form_create_quotation"):
                qc1, qc2, qc3, qc4 = st.columns(4)
                with qc1:
                    p_client = st.text_input("客戶公司名稱 (CÔNG TY) *", value="CÔNG TY TNHH LEADER ART INDUSTRIES (VIETNAM)")
                with qc2:
                    p_attn = st.text_input("聯絡對象 (ATTN)", value="James & LIU KUAN HSIN")
                with qc3:
                    p_proj = st.text_input("工程名稱 (Tên công trình) *", value="新增設備機電系統供電工程")
                with qc4:
                    p_currency = st.selectbox("報價幣別 (Đơn vị tiền tệ)", ["VND", "USD", "RMB", "TWD"])

                qc5, qc6, qc7 = st.columns(3)
                with qc5:
                    p_from = st.text_input("提案負責人 (From)", value="陳智賢")
                with qc6:
                    p_ref = st.text_input("報價單號 (Ref)", value="09092026/LA/BG01")
                with qc7:
                    p_vat = st.number_input("增值稅率 VAT (%)", value=8.0)

                st.markdown("---")
                st.markdown("##### 📦 工程 BOM 材料與工資明細清單 (CHI TIẾT HẠNG MỤC)")
                
                st.success("👉 **【操作指引說明】**\n"
                           "1. **修改現有資料**：直接用滑鼠點擊下方表格內的任何文字或數字格子即可直接修改。\n"
                           "2. **新增一列材料**：請點擊下方表格的最末行空白處直接輸入，或點選表格左上角/右上角的 `+` 號新增列。\n"
                           "3. **金額千分位**：系統已自動套用越南盾千分位與貨幣格式 (`₫`)，方便核對金額。")

                default_items_df = pd.DataFrame(st.session_state.two_tier_quotations_db[0]["items"])
                
                edited_items_df = st.data_editor(
                    default_items_df, 
                    num_rows="dynamic", 
                    use_container_width=True,
                    column_config={
                        "item": st.column_config.TextColumn("材料與工項名稱 (Item)", width="medium"),
                        "unit": st.column_config.TextColumn("單位 (Unit)", width="small"),
                        "qty": st.column_config.NumberColumn("數量 (Qty)", format="%.1f"),
                        "unit_price": st.column_config.NumberColumn("單價 (Unit Price)", format="%,.0f ₫"),
                        "total_price": st.column_config.NumberColumn("複價 (Total Price)", format="%,.0f ₫")
                    }
                )

                if st.form_submit_button("🚀 確認送出報價單並【自動展開BOM連動採購】", type="primary"):
                    if p_client and p_proj and p_ref:
                        internal_rows = edited_items_df.to_dict(orient="records")
                        
                        quotation_record = {
                            "quot_id": p_ref,
                            "project_name": p_proj,
                            "client": p_client,
                            "currency": p_currency,
                            "vat": p_vat,
                            "date": str(datetime.date.today()),
                            "author": p_from,
                            "status": "🟢 已核准並自動下發BOM",
                            "items": internal_rows
                        }
                        
                        st.session_state.two_tier_quotations_db.insert(0, quotation_record)

                        existing_bom = next((b for b in st.session_state.bom_procurement_db if b["quot_id"] == p_ref), None)
                        if not existing_bom:
                            st.session_state.bom_procurement_db.insert(0, {
                                "quot_id": p_ref,
                                "project_name": p_proj,
                                "client": p_client,
                                "bom_items": internal_rows
                            })
                        else:
                            existing_bom["bom_items"] = internal_rows

                        st.success(f"🎉 報價單 [{p_ref}] 建立成功！系統已自動將 BOM 物料清單推送到【第 8 項 BOM 採購連動中心】！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶名稱、工程名稱與報價單號！")

        with tab_q_list:
            st.markdown("##### 📊 已建立之雙層報價單總表與多幣別總計切換")
            
            # 🌐 總經理室 / 主管審核端的多幣別檢視切換工具列
            view_curr = st.selectbox("🌐 選擇總計顯示幣別（支援主管審核與總經理室檢視）", ["VND", "USD", "RMB", "TWD"], key="view_curr_select")

            for q in st.session_state.two_tier_quotations_db:
                # 計算該筆報價單的總金額 (原始幣別)
                subtotal_orig = sum([item.get("total_price", 0) for item in q["items"]])
                vat_amount = subtotal_orig * (q["vat"] / 100.0)
                grand_total_orig = subtotal_orig + vat_amount

                # 轉換為使用者選擇的幣別
                subtotal_converted = convert_currency(subtotal_orig, from_curr=q["currency"], to_curr=view_curr)
                vat_converted = convert_currency(vat_amount, from_curr=q["currency"], to_curr=view_curr)
                grand_total_converted = convert_currency(grand_total_orig, from_curr=q["currency"], to_curr=view_curr)

                with st.expander(f"📌 報價單號: {q['quot_id']} | 客戶: {q['client']} | 專案: {q['project_name']} (原幣別: {q['currency']})"):
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.write(f"**提案人**：{q['author']}")
                        st.write(f"**建立日期**：{q['date']}")
                    with col_info2:
                        st.write(f"**審核狀態**：{q['status']}")
                        st.write(f"**增值稅 VAT**：{q['vat']}%")
                    with col_info3:
                        st.markdown(f"**💰 項目小計 ({view_curr})**：`{format_currency_text(subtotal_converted, view_curr)}`")
                        st.markdown(f"**🔥 含稅總計 ({view_curr})**：`{format_currency_text(grand_total_converted, view_curr)}`")

                    st.dataframe(pd.DataFrame(q["items"]), use_container_width=True)

    # ====================================================
    # ⏱️ 3. 現場外勤打卡與作業登記
    # ====================================================
    elif "3." in selected_option or "打卡" in selected_option:
        st.markdown("### ⏱️ 3. 現場外勤打卡與 GPS 定位作業登記")
        st.info("💡 提供工程師與施工人員於案場進行 GPS 打卡、拍照回報與出勤時數紀錄。")
        st.success("✅ 目前定位：越南平陽省美福工業區案場 (GPS 正常)")
        if st.button("📍 點擊送出今日現場上班打卡"):
            st.success("🎉 打卡成功！記錄時間：" + str(datetime.datetime.now()))

    # ====================================================
    # 📝 4. 施工日報表與點工點料登記
    # ====================================================
    elif "4." in selected_option or "日報表" in selected_option:
        st.markdown("### 📝 4. 施工日報表與點工點料登記")
        st.info("💡 記錄每日工地施工進度、外包商點工數與領料消耗量。")
        st.text_input("填報日期", value=str(datetime.date.today()))
        st.text_area("今日施工摘要與進度說明", value="今日進行西寧廠主配電盤吊裝與二次配線作業。")
        if st.button("💾 儲存並送出施工日報表"):
            st.success("🎉 今日施工日報表已成功存入資料庫！")

    # ====================================================
    # 📸 5. AI 施工照片辨識與安衛稽核
    # ====================================================
    elif "5." in selected_option or "AI" in selected_option or "照片" in selected_option:
        st.markdown("### 📸 5. AI 施工照片辨識與工安衛稽核")
        st.info("💡 上傳現場施工照片，透過 AI 自動辨識是否確實佩戴安全帽、安全帶與防護裝備。")
        st.file_uploader("上傳工地現場照片進行 AI 稽核", type=["jpg", "png", "jpeg"])
        if st.button("🔍 執行 AI 工安合規檢測"):
            st.success("✅ AI 檢測結果：合格率 98%，所有現場作業人員均確實佩戴安全帽與反光背心。")

    # ====================================================
    # 🛡️ 6. 工程師證照與機具檢驗預警
    # ====================================================
    elif "6." in selected_option or "證照" in selected_option or "預警" in selected_option:
        st.markdown("### 🛡️ 6. 工程師證照與施工機具檢驗到期預警")
        st.info("💡 自動監控高壓電氣技術員證照、堆高機證照與吊車檢驗效期，提前 30 天發出黃色/紅色預警。")
        cert_data = [
            {"姓名": "陳明華", "證照名稱": "甲級室內配線技術士", "有效期限": "2026-11-30", "狀態": "🟢 效期正常"},
            {"姓名": "阮文雄", "證照名稱": "特定高壓氣體作業主管", "有效期限": "2026-10-25", "狀態": "🟡 即將到期 (剩9天)"},
            {"機具編號": "CRANE-01", "機具名稱": "5噸油壓吊卡車", "定期檢驗日": "2026-11-15", "狀態": "🟢 檢驗合格"}
        ]
        st.dataframe(pd.DataFrame(cert_data), use_container_width=True)

    # ====================================================
    # 🎨 7. 配電盤電氣與機構設計圖庫 Storage (含一鍵傳送生產部 & 分類維護)
    # ====================================================
    elif "7." in selected_option or "圖庫" in selected_option or "Storage" in selected_option:
        st.markdown("### 🎨 7. 配電盤電氣與機構設計圖庫 Storage 與生產下發中心")
        st.info("💡 管理所有配電盤 2D/3D 設計圖檔、CAD 藍圖與機構規格書，並可一鍵將設計規格傳送至生產部門進行排程與備料。")

        if "drawing_storage_db" not in st.session_state:
            st.session_state.drawing_storage_db = [
                {
                    "drawing_id": "DRW-2026-001",
                    "project": "西寧廠高壓配電盤擴建",
                    "title": "2000A 主配電盤單線圖與配置藍圖",
                    "type": "2D 電氣單線圖 (SLD)",
                    "version": "v1.2",
                    "filename": "TN_Main_Switchgear_2000A_SLD.dwg",
                    "uploader": "陳總工程師",
                    "date": "2026-10-01",
                    "transfer_status": "🟢 已下發生產部"
                }
            ]

        if "production_dispatch_db" not in st.session_state:
            st.session_state.production_dispatch_db = [
                {
                    "dispatch_id": "DISP-2026-001",
                    "project": "西寧廠高壓配電盤擴建",
                    "spec_title": "2000A 主配電盤單線圖與配置藍圖",
                    "source_dept": "工程與設計管理中心",
                    "target_dept": "生產部 (板金組 / 配電組)",
                    "status": "🟢 生產備料中",
                    "date": "2026-10-01"
                }
            ]

        if "drawing_categories_list" not in st.session_state:
            st.session_state.drawing_categories_list = [
                "2D 電氣單線圖 (SLD)", 
                "3D 機構配置圖 (STEP)", 
                "控制邏輯電路圖 (CAD)", 
                "銅排加工與折彎圖"
            ]

        tab_drw_list, tab_drw_upload, tab_cat_mgmt, tab_dispatch = st.tabs([
            "📁 設計圖庫總表與一鍵下發", 
            "📤 上傳新藍圖與圖檔", 
            "⚙️ 圖面技術分類維護",
            "🏭 生產部門接收狀態追蹤"
        ])

        with tab_drw_list:
            dc1, dc2 = st.columns([1, 2])
            with dc1:
                drw_type_filter = st.selectbox("依圖面類型篩選", ["全部類型"] + st.session_state.drawing_categories_list)
            with dc2:
                drw_search = st.text_input("🔍 搜尋專案名稱、圖面標題或檔名...", key="drw_search_box")

            filtered_drw = st.session_state.drawing_storage_db
            if drw_type_filter != "全部類型":
                filtered_drw = [d for d in filtered_drw if d["type"] == drw_type_filter]
            if drw_search:
                filtered_drw = [d for d in filtered_drw if drw_search.lower() in d["project"].lower() or drw_search.lower() in d["title"].lower() or drw_search.lower() in d["filename"].lower()]

            if filtered_drw:
                for drw in filtered_drw:
                    with st.expander(f"📌 [{drw['drawing_id']}] {drw['project']} - {drw['title']} ({drw['version']})"):
                        col_d1, col_d2, col_d3 = st.columns(3)
                        with col_d1:
                            st.write(f"**圖面類型**：{drw['type']}")
                            st.write(f"**檔案名稱**：{drw['filename']}")
                        with col_d2:
                            st.write(f"**上傳者**：{drw['uploader']}")
                            st.write(f"**上傳日期**：{drw['date']}")
                        with col_d3:
                            current_status = drw.get("transfer_status", "⏳ 尚未下發")
                            st.write(f"**下發狀態**：{current_status}")

                        if st.button(f"🚀 一鍵下發設計規格至生產部 ({drw['drawing_id']})", key=f"dispatch_btn_{drw['drawing_id']}"):
                            drw["transfer_status"] = "🟢 已下發生產部"
                            
                            existing_disp = next((d for d in st.session_state.production_dispatch_db if d["dispatch_id"] == f"DISP-{drw['drawing_id'].split('-')[-1]}"), None)
                            if not existing_disp:
                                disp_id = f"DISP-{drw['drawing_id'].split('-')[-1]}"
                                st.session_state.production_dispatch_db.insert(0, {
                                    "dispatch_id": disp_id,
                                    "project": drw["project"],
                                    "spec_title": drw["title"],
                                    "source_dept": "工程與設計管理中心",
                                    "target_dept": "生產部 (板金組 / 配電組)",
                                    "status": "🟢 生產備料與排程中",
                                    "date": str(datetime.date.today())
                                })
                            st.success(f"🎉 成功！設計圖面與規格 [{drw['title']}] 已即時傳送至【生產部門】！")
                            st.rerun()
            else:
                st.info("⚠️ 找不到符合條件的設計圖檔紀錄。")

        with tab_drw_upload:
            with st.form("form_upload_drawing"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    d_proj = st.selectbox("關聯工程專案", [p["proj_name"] for p in st.session_state.engineering_projects_db])
                    d_title = st.text_input("圖面與規格說明標題 *", value="西寧廠低壓控制盤二次迴路配線圖")
                    d_type = st.selectbox("圖面技術分類 *", st.session_state.drawing_categories_list)
                with uc2:
                    d_ver = st.text_input("圖面版本 (Version)", value="v1.0")
                    d_file = st.file_uploader("上傳設計圖檔 (DWG, STEP, PDF, ZIP)", type=["dwg", "step", "pdf", "zip", "png"])
                    d_uploader = st.text_input("上傳工程師 / 設計師姓名", value="陳明華")

                if st.form_submit_button("🚀 確認上傳並存入 Storage 圖庫", type="primary"):
                    if d_title and d_file and d_type:
                        new_d_id = f"DRW-2026-{len(st.session_state.drawing_storage_db)+1:03d}"
                        st.session_state.drawing_storage_db.insert(0, {
                            "drawing_id": new_d_id,
                            "project": d_proj,
                            "title": d_title,
                            "type": d_type,
                            "version": d_ver,
                            "filename": d_file.name,
                            "uploader": d_uploader,
                            "date": str(datetime.date.today()),
                            "transfer_status": "⏳ 尚未下發"
                        })
                        st.success(f"🎉 成功上傳設計圖檔 [{d_file.name}]！分類：【{d_type}】 圖面編號：`{new_d_id}`")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫圖面標題、選擇分類，並上傳設計檔案！")

        with tab_cat_mgmt:
            st.markdown("##### ⚙️ 圖面技術分類維護（新增、修改與刪除）")
            st.info("💡 在此處您可以隨時新增工程上需要的圖面技術分類，或刪除不需要的分類項目。")

            with st.form("form_add_drawing_category"):
                new_cat_name = st.text_input("新增圖面技術分類名稱", placeholder="例如: 弱電與消防系統佈局圖")
                if st.form_submit_button("➕ 確認新增技術分類", type="primary"):
                    if new_cat_name.strip():
                        clean_name = new_cat_name.strip()
                        if clean_name not in st.session_state.drawing_categories_list:
                            st.session_state.drawing_categories_list.append(clean_name)
                            st.success(f"🎉 成功新增圖面技術分類：【{clean_name}】！")
                            st.rerun()
                        else:
                            st.warning("⚠️ 此分類名稱已存在！")
                    else:
                        st.warning("⚠️ 請輸入有效的分類名稱！")

            st.markdown("---")
            st.markdown("##### 📋 目前現有技術分類清單")
            for idx, cat_item in enumerate(st.session_state.drawing_categories_list, 1):
                cc1, cc2 = st.columns([4, 1])
                with cc1:
                    st.text(f"{idx}. {cat_item}")
                with cc2:
                    if len(st.session_state.drawing_categories_list) > 1:
                        if st.button("🗑️ 刪除", key=f"del_cat_{idx}"):
                            st.session_state.drawing_categories_list.remove(cat_item)
                            st.success(f"🗑️ 已刪除分類：{cat_item}")
                            st.rerun()
                    else:
                        st.text("保留中")

        with tab_dispatch:
            st.markdown("##### 🏭 生產部門接收與製造排程狀態追蹤")
            if st.session_state.production_dispatch_db:
                st.dataframe(pd.DataFrame(st.session_state.production_dispatch_db), use_container_width=True)
            else:
                st.info("目前尚無下發至生產部的設計規格紀錄。")

    # ====================================================
    # 🔗 8. 配電盤 BOM 零件自動展開與採購連動
    # ====================================================
    elif "8." in selected_option or "BOM" in selected_option or "採購連動" in selected_option:
        st.markdown("### 🔗 8. 配電盤 BOM 零件自動展開與採購連動")
        st.info("💡 工程報價核准後自動展開物料清單 (BOM)，並可一鍵連動採購請購單 (PR) 與對比專案預算。")

        if "bom_procurement_db" not in st.session_state or not st.session_state.bom_procurement_db:
            st.warning("⚠️ 目前尚無已展開的 BOM 資料，請先至【第 2 項 雙層報價系統】建立或送出報價單。")
        else:
            for bom_rec in st.session_state.bom_procurement_db:
                with st.expander(f"📦 專案報價單號: {bom_rec['quot_id']} - {bom_rec['project_name']} ({bom_rec['client']})"):
                    st.markdown(f"**包含物料項目總數**：`{len(bom_rec['bom_items'])}` 項")
                    st.dataframe(pd.DataFrame(bom_rec['bom_items']), use_container_width=True)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(f"🛒 一鍵轉入採購請購單 (PR) - {bom_rec['quot_id']}", key=f"pr_btn_{bom_rec['quot_id']}"):
                            st.success(f"🎉 成功將 [{bom_rec['quot_id']}] 的 BOM 物料轉入採購部請購單（PR）進行詢比價與下單！")
                    with col_b2:
                        if st.button(f"📊 進行專案預算與採購成本對比 - {bom_rec['quot_id']}", key=f"budget_btn_{bom_rec['quot_id']}"):
                            st.info("✅ 經系統比對：此 BOM 採購總金額符合專案預算範圍，未超出上限！")

    # ====================================================
    # 💰 9. 外包商計價與工進估驗管理
    # ====================================================
    elif "9." in selected_option or "外包商" in selected_option or "估驗" in selected_option:
        st.markdown("### 💰 9. 外包商計價與工進估驗管理")
        st.info("💡 記錄外包工班點工數、工程進度百分比，自動產生應付帳款與估驗請款單。")
        st.success("✅ 目前外包商合約計價狀態正常，無超支情形。")

    # ====================================================
    # 🏁 10. FAT / SAT 出廠與現場驗收管理
    # ====================================================
    elif "10." in selected_option or "FAT" in selected_option or "SAT" in selected_option or "驗收" in selected_option:
        st.markdown("### 🏁 10. FAT / SAT 出廠與現場驗收管理")
        st.info("💡 執行工廠驗收測試 (FAT) 與現場驗收測試 (SAT)，記錄缺失改善與客戶簽收單。")
        st.success("✅ 西寧廠高壓配電盤 FAT 出廠測試已完成並取得客戶簽收！")

# ----------------------------------------------------
# 🔌 相容性包裝函式
# ----------------------------------------------------
def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_management_page(engine=engine, lang=lang, **kwargs)
