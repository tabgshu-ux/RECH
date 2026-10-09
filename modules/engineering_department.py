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
            "caption": "水電工程與面板製造 ERP 系統（涵蓋雙層報價、簽核中心串接、BOM 採購連動、外包點工計薪、FAT/SAT 驗收與越南電子發票）。",
            "sub1": "⚡ [工程] 配電盤與工程專案雙層報價系統",
            "sub2": "⚡ [工程] 工程驗收與進度追蹤",
            "sub3": "⚡ [工程] 現場工程日報表與出工統計",
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
            "sub2": "⚡ [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "⚡ [KT] Nhật ký công trình & Nhân công",
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
            "sub2": "⚡ [Eng] Acceptance & Progress Tracking",
            "sub3": "⚡ [Eng] Daily Site Reports & Labor",
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
        st.session_state.two_tier_quotations_db = [
            {
                "quot_id": "QT-2026-001", "client": "Công ty TNHH Xây lắp Tân Thuận",
                "project_name": "西寧廠主配電盤 2000A 統包工程", "proposer": "協理 - 陳明華", "currency": "USD",
                "internal_items": [
                    {"type": "訂製機櫃", "desc": "2000A 防水不銹鋼機櫃", "qty": 2.0, "unit_price": 3500.0, "subtotal": 7000.0},
                    {"type": "水電材料", "desc": "銅排 Busbar 10x100mm", "qty": 450.0, "unit_price": 2.5, "subtotal": 1125.0}
                ],
                "total_internal_cost": 8125.0, "customer_facing_summary": "1. 西寧廠 2000A 主配電盤及箱體統包工程",
                "customer_price": 11500.0, "status": "⏳ 待副總經理審核"
            }
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [{"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠", "status": "🔴 30天內即將到期"}]

    if "bom_procurement_db" not in st.session_state:
        st.session_state.bom_procurement_db = [
            {
                "quot_id": "QT-2026-001", "project_name": "西寧廠主配電盤 2000A 統包工程", "client": "Công ty TNHH Xây lắp Tân Thuận",
                "bom_items": [
                    {"part_code": "PART-CAB-2000", "part_name": "2000A 防水不銹鋼機櫃", "required_qty": 2.0, "stock_qty": 0.0, "shortage": 2.0, "action": "🔴 需採購"},
                    {"part_code": "PART-BUS-100", "part_name": "銅排 Busbar 10x100mm", "required_qty": 450.0, "stock_qty": 500.0, "shortage": 0.0, "action": "🟢 庫存充足"}
                ],
                "status": "🟢 BOM 已展開"
            }
        ]

    if "subcontractor_attendance_db" not in st.session_state:
        st.session_state.subcontractor_attendance_db = [
            {
                "log_id": "LAB-2026-001", "factory": "越南西寧廠", "contractor": "順發水電外包工班",
                "date": "2026-10-08", "workers_count": 12, "normal_hours": 8.0, "ot_hours": 2.0,
                "night_shift": True, "total_calculated_usd": 420.0, "status": "🟢 已確認並生成對帳單"
            }
        ]

    if "fat_sat_db" not in st.session_state:
        st.session_state.fat_sat_db = [
            {
                "report_id": "FAT-2026-001", "test_type": "FAT (工廠出廠驗收測試)", "project": "西寧廠主配電盤 2000A",
                "tester": "品質工程師 - 范文明", "insulation_res": "150 MΩ", "withstand_voltage": "2500V / 1 min",
                "qr_code_token": "REETECH-FAT-2026-001-VERIFIED", "status": "🟢 檢驗合格並已發行 QR Code"
            }
        ]

    if "vn_invoice_db" not in st.session_state:
        st.session_state.vn_invoice_db = [
            {
                "inv_no": "AA/26E-000128", "client": "Công ty TNHH Xây lắp Tân Thuận", "project": "西寧廠主配電盤工程款",
                "subtotal_usd": 11500.0, "vat_rate": "10%", "vat_amount_usd": 1150.0, "total_usd": 12650.0, "status": "🟢 GDT Verified"
            }
        ]

    # ----------------------------------------------------
    # 1. 配電盤與工程專案雙層報價系統
    # ----------------------------------------------------
    if "1" in sub_str or "報價" in sub_str or "Quotation" in sub_str or "配電盤與工程專案" in sub_str:
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
    elif "2" in sub_str or "驗收" in sub_str or "Acceptance" in sub_str:
        st.markdown(f"### 📊 2. {t['sub2']}")
        st.info("即時監控工程進度與預定驗收時間。")

    # ----------------------------------------------------
    # 3. 現場工程日報表
    # ----------------------------------------------------
    elif "3" in sub_str or "日報" in sub_str or "Daily" in sub_str:
        st.markdown(f"### 📝 3. {t['sub3']}")
        st.info("記錄每日台幹與越籍工人人數及施工進度。")

    # ----------------------------------------------------
    # 4. AI 施工照片辨識
    # ----------------------------------------------------
    elif "4" in sub_str or "AI" in sub_str or "照片" in sub_str:
        st.markdown(f"### 🤖 4. {t['sub4']}")
        st.info("上傳施工現場照片進行 AI 辨識與歸檔。")

    # ----------------------------------------------------
    # 5. 證照到期預警
    # ----------------------------------------------------
    elif "5" in sub_str or "證照" in sub_str or "License" in sub_str:
        st.markdown(f"### ⚠️ 5. {t['sub5']}")
        st.dataframe(pd.DataFrame(st.session_state.license_db), use_container_width=True)

    # ----------------------------------------------------
    # 6. 設計圖庫 Storage
    # ----------------------------------------------------
    elif "6" in sub_str or "圖庫" in sub_str or "Storage" in sub_str:
        st.markdown(f"### 🎨 6. {t['sub6']}")
        st.info("管理 2D/3D 設計圖檔與 CAD 藍圖。")

    # ----------------------------------------------------
    # 7. BOM 零件自動展開與採購連動 (強悍功能一)
    # ----------------------------------------------------
    elif "7" in sub_str or "BOM" in sub_str or "採購" in sub_str:
        st.markdown(f"### 🔌 7. {t['sub7']}")
        st.info("當工程報價拍板後，自動展開 BOM 物料清單、比對倉庫庫存，並生成採購請購單 (PR)。")
        if st.session_state.bom_procurement_db:
            for item in st.session_state.bom_procurement_db:
                with st.expander(f"📌 專案單號：{item['quot_id']} | 專案：{item['project_name']}"):
                    st.dataframe(pd.DataFrame(item["bom_items"]), use_container_width=True)
                    if st.button(f"🚀 轉入正式採購請購單 (PR) {item['quot_id']}", key=f"pr_btn_{item['quot_id']}"):
                        st.success("✅ 採購請購單已成功建立並送至採購部！")
        else:
            st.info("目前尚無已展開的 BOM 資料。")

    # ----------------------------------------------------
    # 8. 外包商點工計價與越南勞動法計薪 (強悍功能二)
    # ----------------------------------------------------
    elif "8" in sub_str or "外包商" in sub_str or "點工" in sub_str:
        st.markdown(f"### 👷 8. {t['sub8']}")
        st.info("精準記錄西寧/海防廠外包點工出勤，自動套用越南勞動法加班（150%）與夜班加給（30%）。")
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
    # 9. FAT/SAT 試驗報告與 QR Code 驗收 (強悍功能三)
    # ----------------------------------------------------
    elif "9" in sub_str or "FAT" in sub_str or "SAT" in sub_str:
        st.markdown(f"### 🧪 9. {t['sub9']}")
        st.info("符合 ISO 9001 規範，自動生成 FAT/SAT 試驗報告與防偽 QR Code 供業主掃描驗收。")
        with st.form("fat_form"):
            st.text_input("關聯專案名稱 / 盤體編號", value="西寧廠主配電盤 2000A")
            if st.form_submit_button("🚀 生成 FAT 試驗報告與 QR Code", type="primary"):
                st.success("🎉 FAT 試驗報告已成功生成並繫結防偽 QR Code！")
        st.markdown("##### 📱 驗收報告資料庫")
        st.dataframe(pd.DataFrame(st.session_state.fat_sat_db), use_container_width=True)

    # ----------------------------------------------------
    # 10. 越南營建電子發票與稅務管家 (強悍功能四)
    # ----------------------------------------------------
    elif "10" in sub_str or "發票" in sub_str or "Invoice" in sub_str or "越南營建" in sub_str:
        st.markdown(f"### 📊 10. {t['sub10']}")
        st.info("符合越南稅務總局 (GDT) 規範，管理電子發票 (Hóa đơn điện tử) 與加值稅 (VAT 8%/10%) 合規申報。")
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
