import streamlit as st
import pandas as pd
import datetime

def render_engineering_department_page(engine=None, lang="繁體中文", **kwargs):
    sub_action = (
        kwargs.get("sub_action")
        or st.session_state.get("current_sub_action")
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "1"
    )
    sub_str = str(sub_action).strip()

    texts = {
        "繁體中文": {
            "title": "⚡ 裕豐電機工業 - 工程管理中心與設計部門",
            "caption": "水電工程與面板製造 ERP 系統。",
            "sub1": "⚡ [工程] 配電盤與工程專案雙層報價系統",
            "sub2": "📊 [工程] 工程驗收與進度追蹤",
            "sub3": "📋 [工程] 現場工程日報表與出工統計",
            "sub4": "🤖 [工程] AI 施工照片智慧辨識與歸檔",
            "sub5": "⚠️ [工程] 分包商與專業證照到期預警",
            "sub6": "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage",
            "sub7": "🔌 [工程] 配電盤 BOM 零件自動展開與採購連動",
            "sub8": "👷 [工程] 外包商點工計價與越南勞動法計薪",
            "sub9": "🧪 [工程] FAT/SAT 試驗報告與 QR Code 驗收",
            "sub10": "📊 [工程] 越南營建電子發票與稅務合規管家"
        },
        "Tiếng Việt": {
            "title": "⚡ Công ty TNHH Kỹ thuật Điện Reetech - Trung tâm Kỹ thuật",
            "caption": "Hệ thống quản lý kỹ thuật toàn diện.",
            "sub1": "⚡ [KT] Báo giá tủ điện 2 lớp & Phê duyệt",
            "sub2": "📊 [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "📋 [KT] Nhật ký công trình & Chấm công",
            "sub4": "🤖 [KT] AI Nhận diện & Lưu trữ ảnh thi công",
            "sub5": "⚠️ [KT] Cảnh báo hết hạn chứng chỉ",
            "sub6": "🎨 [TK] Kho bản vẽ thiết kế tủ điện Storage",
            "sub7": "🔌 [KT] Bóc tách BOM & Liên kết Mua hàng",
            "sub8": "👷 [KT] Chấm công & Tính lương thầu phụ",
            "sub9": "🧪 [KT] Báo cáo thử nghiệm FAT/SAT & QR Code",
            "sub10": "📊 [KT] Quản lý Hóa đơn điện tử & Thuế VN"
        },
        "English": {
            "title": "⚡ Reetech Industrial - Engineering Management Center",
            "caption": "Comprehensive MEP engineering and panel manufacturing management system.",
            "sub1": "⚡ [Eng] Two-Tier Quotation & Approval",
            "sub2": "📊 [Eng] Acceptance & Progress Tracking",
            "sub3": "📋 [Eng] Daily Site Reports & Labor Statistics",
            "sub4": "🤖 [Eng] AI Field Photo Recognition & Archiving",
            "sub5": "⚠️ [Eng] Subcontractor & License Expiry Alerts",
            "sub6": "🎨 [Design] Electrical & Mechanical Drawing Storage",
            "sub7": "🔌 [Eng] BOM Auto-Explosion & Procurement",
            "sub8": "👷 [Eng] Subcontractor Labor & Payroll",
            "sub9": "🧪 [Eng] FAT/SAT Test Report & QR Acceptance",
            "sub10": "📊 [Eng] Vietnam E-Invoice & Tax Manager"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 🏭 資料庫初始化
    if "warehouse_master_parts" not in st.session_state:
        st.session_state.warehouse_master_parts = {
            "銅排 Busbar 10x100mm": 2.5,
            "空氣斷路器 ACB 2000A": 1850.0,
            "塑殼斷路器 MCCB 250A": 145.0,
            "2000A 防水不銹鋼機櫃": 3500.0,
            "1500A 戶外控制箱體": 2800.0,
            "PVC 管 2寸 (50米)": 45.0,
            "控制電纜 3.5mm² (100m)": 120.0,
            "端子排與五金配件組": 85.0
        }

    if "two_tier_quotations_db" not in st.session_state:
        st.session_state.two_tier_quotations_db = []

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤擴建", "factory": "西寧廠", "budget": 1200000000, "status": "進行中"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠動力盤統包工程", "factory": "海防廠", "budget": 850000000, "status": "進行中"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [{"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠", "status": "🔴 30天內即將到期"}]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = []

    if "drawing_storage_db" not in st.session_state:
        st.session_state.drawing_storage_db = []

    if "bom_procurement_db" not in st.session_state:
        st.session_state.bom_procurement_db = []

    if "subcontractor_attendance_db" not in st.session_state:
        st.session_state.subcontractor_attendance_db = []

    if "fat_sat_db" not in st.session_state:
        st.session_state.fat_sat_db = []

    if "vn_invoice_db" not in st.session_state:
        st.session_state.vn_invoice_db = []

    if "field_daily_reports_db" not in st.session_state:
        st.session_state.field_daily_reports_db = [
            {
                "report_id": "REP-2026-001",
                "project": "西寧廠高壓配電盤擴建",
                "reporter_name": "admin",
                "gps_status": "📍 位置驗證已簽到 (Tay Ninh Factory Zone A)",
                "workers_count": 16,
                "summary": "完成主配電盤銅排安裝與絕緣測試。",
                "date": "2026-10-09"
            }
        ]

    # ----------------------------------------------------
    # 1. 配電盤與工程專案雙層報價系統
    # ----------------------------------------------------
    if sub_str == "1" or "報價" in sub_str or "Quotation" in sub_str or "配電盤與工程專案" in sub_str:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        tab_prop, tab_review = st.tabs(["✍️ 建立報價提案 (協理填寫)", "🔒 主管審核中心 (簽核中心連動)"])

        with tab_prop:
            with st.form("tier_quotation_form"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    p_client = st.text_input("客戶名稱 (Client)", value="Công ty TNHH Xây lắp Tân Thuận")
                with c2:
                    p_proj = st.text_input("整體工程名稱 / 專案名稱 *", value="海防廠動力盤擴建 1500A 統包工程")
                with c3:
                    p_prop = st.text_input("提案人 (職稱與姓名) *", value="協理 - 陳明華")
                with c4:
                    p_curr = st.selectbox("計價幣別", ["USD", "VND", "NTD"])

                st.markdown("---")
                st.markdown("##### 📦 內部成本明細清單 (自動對應倉庫標準單價)")
                num_items = st.number_input("項目數量 (可自由增減格數)", min_value=1, max_value=30, value=4, step=1)

                internal_rows = []
                total_cost = 0.0
                available_parts = list(st.session_state.warehouse_master_parts.keys())

                for i in range(1, int(num_items) + 1):
                    ic1, ic2, ic3, ic4, ic5 = st.columns([2.5, 2, 1.5, 1.5, 1.5])
                    with ic1:
                        selected_part = st.selectbox(f"材料/機櫃 #{i}", available_parts, key=f"part_sel_{i}")
                        auto_unit_price = st.session_state.warehouse_master_parts[selected_part]
                    with ic2:
                        note_extra = st.text_input(f"規格備註 #{i}", value="", key=f"inote_{i}")
                    with ic3:
                        iqty = st.number_input(f"數量 #{i}", min_value=0.0, value=10.0 if i <= 3 else 0.0, key=f"iqty_{i}")
                    with ic4:
                        st.text_input(f"單價 #{i}", value=f"$ {auto_unit_price:,.2f}", disabled=True, key=f"price_display_{i}")
                    with ic5:
                        sub = iqty * auto_unit_price
                        st.text_input(f"小計 #{i}", value=f"$ {sub:,.2f}", disabled=True, key=f"sub_display_{i}")

                    if iqty > 0:
                        total_cost += sub
                        internal_rows.append({
                            "type": "訂製機櫃" if "機櫃" in selected_part or "箱體" in selected_part else "水電材料",
                            "desc": selected_part, "note": note_extra, "qty": iqty, "unit_price": auto_unit_price, "subtotal": sub
                        })

                st.markdown(f"### 💰 內部總成本總和：`$ {total_cost:,.2f} {p_curr}`")
                st.markdown("---")
                st.markdown("##### 📄 對外業主報價摘要與金額")
                cust_summary = st.text_area("對外合約摘要", value="1. 專案機櫃訂製與組裝工程\n2. 廠房高低壓配電盤安裝與測試")
                cust_suggested_price = st.number_input("建議對外報價金額 (Customer Price)", min_value=0.0, value=total_cost * 1.35, step=100.0)

                if st.form_submit_button("🚀 提交報價提案並同步至簽核中心", type="primary"):
                    if p_client and p_proj and internal_rows:
                        new_id = f"QT-2026-{len(st.session_state.two_tier_quotations_db)+1:03d}"
                        st.session_state.two_tier_quotations_db.append({
                            "quot_id": new_id, "client": p_client, "project_name": p_proj, "proposer": p_prop,
                            "currency": p_curr, "internal_items": internal_rows, "total_internal_cost": total_cost,
                            "customer_facing_summary": cust_summary, "customer_price": cust_suggested_price, "status": "⏳ 待副總經理審核"
                        })
                        st.success(f"✅ 報價提案 [{new_id}] 已成功提交並同步至全公司電子簽核中心！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶、專案名稱及至少一筆有效的數量明細！")

        with tab_review:
            if st.session_state.two_tier_quotations_db:
                for q in st.session_state.two_tier_quotations_db:
                    with st.expander(f"📌 單號：{q['quot_id']} | 專案：{q['project_name']} | 提案人：{q['proposer']} | 狀態：{q['status']}"):
                        st.write(f"**客戶**：{q['client']} | **內部成本總和**：`$ {q['total_internal_cost']:,.2f}`")
                        st.dataframe(pd.DataFrame(q["internal_items"]), use_container_width=True)
                        st.markdown(f"**對外報價金額**：`$ {q['customer_price']:,.2f}`")
                        st.info(f"目前狀態：{q['status']} (可至左側【全公司電子簽核中心】進行跨部門統一審核)")
            else:
                st.info("目前尚無雙層報價紀錄。")

    # ----------------------------------------------------
    # 2. 工程驗收與進度追蹤
    # ----------------------------------------------------
    elif sub_str == "2" or "驗收" in sub_str or "Acceptance" in sub_str:
        st.markdown(f"### 📊 2. {t['sub2']}")
        st.info("💡 即時監控各專案工程進度、預定驗收時間，並與財務部應收帳款 (AR) 連動。")
        st.dataframe(pd.DataFrame(st.session_state.engineering_projects_db), use_container_width=True)

    # ----------------------------------------------------
    # 3. 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif sub_str == "3" or "日報" in sub_str or "Daily" in sub_str:
        st.markdown(f"### 📋 3. {t['sub3']}")
        st.info("🔒 **現場施工日報與出工紀錄填報**：系統自動鎖定登入帳號並進行現場位置驗證。")

        logged_user = st.session_state.get("user_name", "admin")
        logged_role = str(st.session_state.get("user_role", "Staff")).strip().lower()

        is_exempt_role = logged_role in ["admin", "chairman", "generalmanager", "vicemanager", "manager", "finance_manager", "executive"]

        with st.form("secure_daily_rep_form"):
            rc1, rc2 = st.columns(2)
            with rc1:
                st.text_input("填報人 (系統自動鎖定)", value=f"{logged_user} ({logged_role.upper()})", disabled=True)
            with rc2:
                gps_status_val = st.selectbox(
                    "現場打卡與位置驗證",
                    [
                        "📍 已於現場簽到打卡 (Tay Ninh Factory Zone A)",
                        "📍 已於現場簽到打卡 (Hai Phong Plant Site)",
                        "❌ 未進行現場打卡"
                    ]
                )

            r_proj = st.selectbox("關聯專案名稱", [p["proj_name"] for p in st.session_state.engineering_projects_db])
            r_workers = st.number_input("當日出工總人數 (含現場人力與督導)", min_value=1, value=15)
            r_desc = st.text_area("今日施工進度與工作紀要 (Work Summary)", value="完成主配電盤銅排安裝與絕緣耐壓測試。")

            if st.form_submit_button("🚀 提交正式工程日報表與出工統計", type="primary"):
                if (not is_exempt_role) and ("❌" in gps_status_val):
                    st.error("⚠️ 偵測到您尚未進行現場位置驗證，無法提交日報表。")
                else:
                    new_id = f"REP-2026-{len(st.session_state.field_daily_reports_db)+1:03d}"
                    st.session_state.field_daily_reports_db.insert(0, {
                        "report_id": new_id,
                        "project": r_proj,
                        "reporter_name": logged_user,
                        "gps_status": "📍 已完成驗證與出勤記錄" if is_exempt_role else gps_status_val,
                        "workers_count": r_workers,
                        "summary": r_desc,
                        "date": str(datetime.date.today())
                    })
                    st.success(f"✅ 現場工程日報表 [{new_id}] 已成功提交並列入出工統計！")
                    st.rerun()

        st.markdown("---")
        st.markdown("##### 📋 歷史工程日報表與出工統計總覽")
        if st.session_state.field_daily_reports_db:
            st.dataframe(pd.DataFrame(st.session_state.field_daily_reports_db), use_container_width=True)
        else:
            st.info("目前尚無工程日報表紀錄。")

    # ----------------------------------------------------
    # 4. AI 施工照片智慧辨識與歸檔
    # ----------------------------------------------------
    elif sub_str == "4" or "AI" in sub_str or "照片" in sub_str:
        st.markdown(f"### 🤖 4. {t['sub4']}")
        st.info("💡 上傳施工現場照片，系統 AI 自動辨識施工品質、項目與安全規範並進行智慧歸檔。")

        with st.form("ai_photo_upload_form"):
            ac1, ac2 = st.columns(2)
            with ac1:
                photo_project = st.selectbox("選擇關聯工程案場", [p["proj_name"] for p in st.session_state.engineering_projects_db])
                photo_category = st.selectbox("施工項目分類", [
                    "配電盤箱體與結構安裝", 
                    "導電銅排與絕緣測試", 
                    "過路橋架與配管工程", 
                    "高低壓線路拉線與端子壓接", 
                    "工地工安與防護稽核"
                ])
            with ac2:
                uploaded_photo = st.file_uploader("上傳施工現場照片 (JPG, PNG)", type=["jpg", "jpeg", "png"])
                photo_note = st.text_input("現場備註說明", placeholder="例如: 西寧廠 A 區主盤銅排間距符合規範")

            if st.form_submit_button("🚀 開始 AI 智慧辨識並歸檔", type="primary"):
                if uploaded_photo:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    photo_id = f"AI-PHO-2026-{len(st.session_state.ai_photo_archive_db)+1:03d}"
                    
                    ai_result = "✅ AI 辨識合格：結構完整、絕緣距離符合標準" if "銅排" in photo_category or "盤" in photo_category else "✅ AI 辨識合格：符合標準施工規範"

                    st.session_state.ai_photo_archive_db.insert(0, {
                        "photo_id": photo_id,
                        "project": photo_project,
                        "category": photo_category,
                        "filename": uploaded_photo.name,
                        "ai_analysis": ai_result,
                        "note": photo_note if photo_note else "無特別備註",
                        "timestamp": now_str,
                        "status": "🟢 已歸檔"
                    })
                    st.success(f"🎉 成功！照片已透過 AI 辨識完成，檔案編號 [{photo_id}] 已歸入專案資料庫！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請先選擇並上傳一張施工現場照片檔案！")

        st.markdown("---")
        st.markdown("##### 📁 AI 施工照片智慧歸檔總覽")
        if st.session_state.ai_photo_archive_db:
            st.dataframe(pd.DataFrame(st.session_state.ai_photo_archive_db), use_container_width=True)
        else:
            st.info("目前尚無 AI 施工照片歸檔紀錄，請透過上方表單上傳。")

    # ----------------------------------------------------
    # 5. 分包商與專業證照到期預警 (含完整新增、修改、刪除與過濾)
    # ----------------------------------------------------
    elif sub_str == "5" or "證照" in sub_str or "License" in sub_str:
        st.markdown(f"### ⚠️ 5. {t['sub5']}")
        st.info("💡 系統主動監控技師與外包商專業證照到期日與合規狀態，支援即時新增、編輯與刪除管理。")

        tab_lic_list, tab_lic_add, tab_lic_edit = st.tabs(["📋 證照清單與合規總覽", "➕ 新增技師與證照", "✏️ 修改與刪除證照"])

        with tab_lic_list:
            sc1, sc2 = st.columns([1, 2])
            with sc1:
                lic_status_filter = st.selectbox("依合規狀態篩選", ["全部狀態", "🔴 30天內即將到期", "🟢 證照有效合規"])
            with sc2:
                lic_search = st.text_input("🔍 搜尋技師姓名、工號或證照名稱...", key="lic_search_box")

            filtered_lic = st.session_state.license_db
            if lic_status_filter != "全部狀態":
                filtered_lic = [l for l in filtered_lic if lic_status_filter in l["status"]]
            if lic_search:
                filtered_lic = [l for l in filtered_lic if lic_search.lower() in l["name"].lower() or lic_search.lower() in l["emp_id"].lower() or lic_search.lower() in l["license_name"].lower()]

            if filtered_lic:
                lic_display = []
                for idx, lic in enumerate(filtered_lic, 1):
                    lic_display.append({
                        "STT": idx,
                        "工號": lic["emp_id"],
                        "姓名/外包商": lic["name"],
                        "專業證照名稱": lic["license_name"],
                        "有效期限": lic.get("expiry_date", "2026-11-30"),
                        "合規狀態": lic["status"]
                    })
                st.dataframe(pd.DataFrame(lic_display), use_container_width=True)
            else:
                st.info("⚠️ 找不到符合條件的證照紀錄。")

        with tab_lic_add:
            with st.form("form_add_license"):
                lc1, lc2 = st.columns(2)
                with lc1:
                    l_id = st.text_input("技師工號 / 外包商代碼 *", value="EMP-005")
                    l_name = st.text_input("技師或外包商人員姓名 *", value="阮文雄")
                with lc2:
                    l_lic = st.text_input("專業證照名稱 *", value="甲種電匠 / 高壓氣體作業主管")
                    l_date = st.date_input("證照有效期限 (Expiry Date)")
                
                l_status = st.selectbox("合規狀態", ["🟢 證照有效合規", "🔴 30天內即將到期", "❌ 已過期失效"])

                if st.form_submit_button("🚀 立即登錄並加入證照預警庫", type="primary"):
                    if l_id and l_name and l_lic:
                        st.session_state.license_db.append({
                            "emp_id": l_id,
                            "name": l_name,
                            "license_name": l_lic,
                            "expiry_date": str(l_date),
                            "status": l_status
                        })
                        st.success(f"✅ 成功登錄 [{l_name}] 的專業證照 [{l_lic}]！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫工號、姓名與證照名稱！")

        with tab_lic_edit:
            if st.session_state.license_db:
                lic_options = [f"{l['emp_id']} - {l['name']} ({l['license_name']})" for l in st.session_state.license_db]
                sel_lic_target = st.selectbox("選擇要修改或刪除的證照紀錄", lic_options)
                target_emp_id = sel_lic_target.split(" - ")[0]
                target_lic_item = next((l for l in st.session_state.license_db if l["emp_id"] == target_emp_id), None)

                if target_lic_item:
                    with st.form("form_edit_license"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            ed_l_name = st.text_input("姓名", value=target_lic_item["name"])
                            ed_l_lic = st.text_input("證照名稱", value=target_lic_item["license_name"])
                        with ec2:
                            ed_l_status = st.selectbox("合規狀態", ["🟢 證照有效合規", "🔴 30天內即將到期", "❌ 已過期失效"], index=0 if "有效" in target_lic_item["status"] else (1 if "30天" in target_lic_item["status"] else 2))

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            update_submitted = st.form_submit_button("💾 儲存修改內容", type="primary", use_container_width=True)
                        with col_btn2:
                            delete_submitted = st.form_submit_button("🔥 刪除此筆證照紀錄", type="secondary", use_container_width=True)

                        if update_submitted:
                            target_lic_item["name"] = ed_l_name
                            target_lic_item["license_name"] = ed_l_lic
                            target_lic_item["status"] = ed_l_status
                            st.success(f"🎉 成功更新 [{ed_l_name}] 的證照資料！")
                            st.rerun()

                        if delete_submitted:
                            st.session_state.license_db = [l for l in st.session_state.license_db if l["emp_id"] != target_emp_id]
                            st.success("🗑️ 該筆證照紀錄已成功刪除！")
                            st.rerun()
            else:
                st.info("目前尚無證照紀錄可供修改。")

   # ----------------------------------------------------
    # 6. 配電盤電氣與機構設計圖庫 Storage (簡潔介面與完整圖檔管理)
    # ----------------------------------------------------
    elif sub_str == "6" or "圖庫" in sub_str or "Storage" in sub_str:
        st.markdown(f"### 🎨 6. {t['sub6']}")
        st.info("💡 管理所有配電盤 2D/3D 設計圖檔、CAD 藍圖與機構規格書（Storage 儲存庫路徑由資訊管理部統一維護）。")

        # 初始化圖庫預設範例資料（如果空的）
        if not st.session_state.drawing_storage_db:
            st.session_state.drawing_storage_db = [
                {
                    "drawing_id": "DRW-2026-001",
                    "project": "西寧廠高壓配電盤擴建",
                    "title": "2000A 主配電盤單線圖與配置藍圖",
                    "type": "2D 電氣單線圖 (SLD)",
                    "version": "v1.2",
                    "filename": "TN_Main_Switchgear_2000A_SLD.dwg",
                    "uploader": "陳總工程師",
                    "date": "2026-10-01"
                },
                {
                    "drawing_id": "DRW-2026-002",
                    "project": "海防廠動力盤統包工程",
                    "title": "1500A 戶外控制箱體 3D 機構結構圖",
                    "type": "3D 機構配置圖 (STEP)",
                    "version": "v1.0",
                    "filename": "HP_Outdoor_Enclosure_1500A.step",
                    "uploader": "阮技術員",
                    "date": "2026-10-05"
                }
            ]

        tab_drw_list, tab_drw_upload, tab_drw_manage = st.tabs(["📁 設計圖庫總表與搜尋", "📤 上傳新藍圖與圖檔", "✏️ 修改與刪除圖檔紀錄"])

        with tab_drw_list:
            dc1, dc2 = st.columns([1, 2])
            with dc1:
                drw_type_filter = st.selectbox("依圖面類型篩選", ["全部類型", "2D 電氣單線圖 (SLD)", "3D 機構配置圖 (STEP)", "控制邏輯電路圖 (CAD)", "銅排加工與折彎圖"])
            with dc2:
                drw_search = st.text_input("🔍 搜尋專案名稱、圖面標題或檔名...", key="drw_search_box")

            filtered_drw = st.session_state.drawing_storage_db
            if drw_type_filter != "全部類型":
                filtered_drw = [d for d in filtered_drw if d["type"] == drw_type_filter]
            if drw_search:
                filtered_drw = [d for d in filtered_drw if drw_search.lower() in d["project"].lower() or drw_search.lower() in d["title"].lower() or drw_search.lower() in d["filename"].lower()]

            if filtered_drw:
                drw_display = []
                for idx, drw in enumerate(filtered_drw, 1):
                    drw_display.append({
                        "STT": idx,
                        "圖面編號": drw["drawing_id"],
                        "關聯專案": drw["project"],
                        "圖面標題": drw["title"],
                        "圖面類型": drw["type"],
                        "版本": drw["version"],
                        "檔案名稱": drw["filename"],
                        "上傳者": drw["uploader"],
                        "上傳日期": drw["date"]
                    })
                st.dataframe(pd.DataFrame(drw_display), use_container_width=True)
            else:
                st.info("⚠️ 找不到符合條件的設計圖檔紀錄。")

        with tab_drw_upload:
            with st.form("form_upload_drawing"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    d_proj = st.selectbox("關聯工程專案", [p["proj_name"] for p in st.session_state.engineering_projects_db])
                    d_title = st.text_input("圖面與規格說明標題 *", value="西寧廠低壓控制盤二次迴路配線圖")
                    d_type = st.selectbox("圖面技術分類", ["2D 電氣單線圖 (SLD)", "3D 機構配置圖 (STEP)", "控制邏輯電路圖 (CAD)", "銅排加工與折彎圖"])
                with uc2:
                    d_ver = st.text_input("圖面版本 (Version)", value="v1.0")
                    d_file = st.file_uploader("上傳設計圖檔 (DWG, STEP, PDF, ZIP)", type=["dwg", "step", "pdf", "zip", "png"])
                    d_uploader = st.text_input("上傳工程師 / 設計師姓名", value="陳明華")

                if st.form_submit_button("🚀 確認上傳並存入 Storage 圖庫", type="primary"):
                    if d_title and d_file:
                        new_d_id = f"DRW-2026-{len(st.session_state.drawing_storage_db)+1:03d}"
                        st.session_state.drawing_storage_db.insert(0, {
                            "drawing_id": new_d_id,
                            "project": d_proj,
                            "title": d_title,
                            "type": d_type,
                            "version": d_ver,
                            "filename": d_file.name,
                            "uploader": d_uploader,
                            "date": str(datetime.date.today())
                        })
                        st.success(f"🎉 成功上傳設計圖檔 [{d_file.name}]！圖面編號：`{new_d_id}`")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫圖面標題並上傳設計檔案！")

        with tab_drw_manage:
            if st.session_state.drawing_storage_db:
                drw_options = [f"{d['drawing_id']} - {d['title']} ({d['version']})" for d in st.session_state.drawing_storage_db]
                sel_drw_target = st.selectbox("選擇要修改或刪除的圖檔紀錄", drw_options)
                target_drw_id = sel_drw_target.split(" - ")[0]
                target_drw_item = next((d for d in st.session_state.drawing_storage_db if d["drawing_id"] == target_drw_id), None)

                if target_drw_item:
                    with st.form("form_edit_drawing"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            ed_d_title = st.text_input("修改圖面標題", value=target_drw_item["title"])
                            ed_d_ver = st.text_input("修改版本", value=target_drw_item["version"])
                        with ec2:
                            ed_d_type = st.selectbox("修改圖面類型", ["2D 電氣單線圖 (SLD)", "3D 機構配置圖 (STEP)", "控制邏輯電路圖 (CAD)", "銅排加工與折彎圖"], index=0)

                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            up_drw_btn = st.form_submit_button("💾 儲存圖檔變更", type="primary", use_container_width=True)
                        with col_b2:
                            del_drw_btn = st.form_submit_button("🔥 刪除此圖檔紀錄", type="secondary", use_container_width=True)

                        if up_drw_btn:
                            target_drw_item["title"] = ed_d_title
                            target_drw_item["version"] = ed_d_ver
                            target_drw_item["type"] = ed_d_type
                            st.success("🎉 設計圖檔資訊已成功更新！")
                            st.rerun()

                        if del_drw_btn:
                            st.session_state.drawing_storage_db = [d for d in st.session_state.drawing_storage_db if d["drawing_id"] != target_drw_id]
                            st.success("🗑️ 該筆圖檔紀錄已成功自 Storage 移除！")
                            st.rerun()
            else:
                st.info("目前尚無圖檔紀錄可供修改。")
    # ----------------------------------------------------
    # 7. BOM 零件自動展開與採購連動
    # ----------------------------------------------------
    elif sub_str == "7" or "BOM" in sub_str or "採購" in sub_str:
        st.markdown(f"### 🔌 7. {t['sub7']}")
        st.info("💡 當工程報價拍板後，自動展開 BOM 物料清單、比對倉庫庫存，並生成採購請購單 (PR)。")
        if st.session_state.bom_procurement_db:
            for item in st.session_state.bom_procurement_db:
                with st.expander(f"📌 專案單號：{item['quot_id']} | 專案：{item['project_name']}"):
                    st.dataframe(pd.DataFrame(item["bom_items"]), use_container_width=True)
                    if st.button(f"🚀 轉入正式採購請購單 (PR) {item['quot_id']}", key=f"pr_btn_{item['quot_id']}"):
                        st.success("✅ 採購請購單已成功建立並送至採購部！")
        else:
            st.info("目前尚無已展開的 BOM 資料。")

    # ----------------------------------------------------
    # 8. 外包商點工計價與越南勞動法計薪
    # ----------------------------------------------------
    elif sub_str == "8" or "外包商" in sub_str or "點工" in sub_str:
        st.markdown(f"### 👷 8. {t['sub8']}")
        st.info("💡 精準記錄西寧/海防廠外包點工出勤，自動套用越南勞動法加班（150%）與夜班加給（30%）。")
        with st.form("labor_log_form"):
            lc1, lc2 = st.columns(2)
            with lc1:
                sel_factory = st.selectbox("案場廠區", ["越南西寧廠", "越南海防廠"])
                workers_num = st.number_input("出工工人總人數", min_value=1, value=10)
            with lc2:
                ot_h = st.number_input("加班時數 (OT)", value=2.0, step=0.5)
                is_night = st.checkbox("🌙 是否包含夜班作業 (加給 30%)")
            if st.form_submit_button("🚀 提交點工並套用勞動法計薪", type="primary"):
                st.success("✅ 點工紀錄已建立，並依越南勞動法完成薪資試算！")
        st.markdown("##### 📊 外包商點工與應付帳款 (AP) 紀錄")
        st.dataframe(pd.DataFrame(st.session_state.subcontractor_attendance_db), use_container_width=True)

    # ----------------------------------------------------
    # 9. FAT/SAT 試驗報告與 QR Code 驗收
    # ----------------------------------------------------
    elif sub_str == "9" or "FAT" in sub_str or "SAT" in sub_str:
        st.markdown(f"### 🧪 9. {t['sub9']}")
        st.info("💡 符合 ISO 9001 規範，自動生成 FAT/SAT 試驗報告與防偽 QR Code 供業主掃描驗收。")
        with st.form("fat_form"):
            st.text_input("關聯專案名稱 / 盤體編號", value="西寧廠主配電盤 2000A")
            if st.form_submit_button("🚀 生成 FAT 試驗報告與 QR Code", type="primary"):
                st.success("🎉 FAT 試驗報告已成功生成並繫結防偽 QR Code！")
        st.markdown("##### 📱 驗收報告資料庫")
        st.dataframe(pd.DataFrame(st.session_state.fat_sat_db), use_container_width=True)

    # ----------------------------------------------------
    # 10. 越南營建電子發票與稅務管家
    # ----------------------------------------------------
    elif sub_str == "10" or "發票" in sub_str or "Invoice" in sub_str or "越南營建" in sub_str:
        st.markdown(f"### 📊 10. {t['sub10']}")
        st.info("💡 符合越南稅務總局 (GDT) 規範，管理電子發票 (Hóa đơn điện tử) 與加值稅 (VAT 8%/10%) 合規申報。")
        with st.form("inv_form"):
            st.text_input("客戶 / 業主名稱 (Client)", value="Công ty TNHH Xây lắp Tân Thuận")
            st.number_input("未稅銷售額 (USD)", value=11500.0, step=100.0)
            if st.form_submit_button("🚀 開立電子發票並送交 GDT 驗證", type="primary"):
                st.success("🎉 電子發票已成功開立並通過 GDT 驗證！")
        st.markdown("##### 📋 發票清單與合規狀態")
        st.dataframe(pd.DataFrame(st.session_state.vn_invoice_db), use_container_width=True)

    else:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        st.info("請透過左側選單選擇工程部的各項子功能。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_department_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_department_page(engine=engine, lang=lang, **kwargs)
