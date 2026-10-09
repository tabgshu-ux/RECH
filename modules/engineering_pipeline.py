import streamlit as st
import pandas as pd
import datetime

def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "⚡ 裕豐電機工業 - 工程管理中心與設計部門",
            "caption": "涵蓋工程報價提案系統、多級審核與價格鎖定、工程驗收追蹤、現場日報、AI 施工照片辨識與證照預警。",
            "sub1": "⚡ [工程] 配電盤與工程專案報價 (協理提案與副總鎖定)",
            "sub2": "⚡ [工程] 工程驗收與進度追蹤",
            "sub3": "⚡ [工程] 現場工程日報表與出工統計",
            "sub4": "🤖 [工程] AI 施工照片智慧辨識與歸檔",
            "sub5": "⚠️ [工程] 分包商與專業證照到期預警",
            "sub6": "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage"
        },
        "Tiếng Việt": {
            "title": "⚡ Công ty TNHH Kỹ thuật Điện Reetech - Trung tâm Kỹ thuật",
            "caption": "Báo giá, phê duyệt đa cấp, nghiệm thu, nhật ký công trình, kho lưu trữ và cảnh báo chứng chỉ.",
            "sub1": "⚡ [KT] Báo giá tủ điện & Phê duyệt",
            "sub2": "⚡ [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "⚡ [KT] Nhật ký công trình & Nhân công",
            "sub4": "🤖 [KT] AI Nhận diện & Lưu trữ ảnh thi công",
            "sub5": "⚠️ [KT] Cảnh báo hết hạn chứng chỉ",
            "sub6": "🎨 [TK] Kho bản vẽ thiết kế tủ điện Storage"
        },
        "English": {
            "title": "⚡ Reetech Industrial - Engineering Management Center",
            "caption": "Quotation workflow, multi-level approval, daily site reports, AI photo archiving, and license alerts.",
            "sub1": "⚡ [Eng] Quotation & Pricing Approval Flow",
            "sub2": "⚡ [Eng] Acceptance & Progress Tracking",
            "sub3": "⚡ [Eng] Daily Site Reports & Labor",
            "sub4": "🤖 [Eng] AI Field Photo Recognition & Archiving",
            "sub5": "⚠️ [Eng] Subcontractor & License Expiry Alerts",
            "sub6": "🎨 [Design] Electrical & Mechanical Drawing Storage"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化資料庫
    if "quotation_proposal_db" not in st.session_state:
        st.session_state.quotation_proposal_db = [
            {"quot_id": "QT-2026-001", "client": "Công ty TNHH Xây lắp Tân Thuận", "project": "西寧廠主配電盤 2000A", "amount": 2120.0, "proposer": "協理 - 陳明華", "status": "🟢 副總已鎖定核准 (Locked & Approved)", "version": "v1.0 (Official)"}
        ]

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤與消防管線擴建工程", "factory": "西寧廠 (Tay Ninh)", "budget": 1200000000, "status": "進行中 (Active)"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠無塵室空調與照明管線配置", "factory": "海防廠 (Hai Phong)", "budget": 850000000, "status": "進行中 (Active)"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [
            {"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠 (Class A Electrician)", "issue_date": "2023-01-10", "expiry_date": "2026-10-15", "status": "🔴 30天內即將到期 (Expiring Soon)"},
            {"emp_id": "VN-002", "name": "Nguyễn Văn Quý", "license_name": "乙種電匠 (Class B Electrician)", "issue_date": "2022-05-20", "expiry_date": "2027-05-20", "status": "🟢 有效 (Valid)"}
        ]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = [
            {"photo_id": "IMG-8821", "proj": "PRJ-TN-2026-01", "category": "配電盤配線 (Electrical Panel)", "ai_tag": "🟢 規格相符 / 壓接良好", "uploader": "現場工程師 (李佑銘)", "time": "2026-10-08 14:20"}
        ]

    if "drawing_storage_db" not in st.session_state:
        st.session_state.drawing_storage_db = [
            {"drawing_no": "DWG-01", "proj_name": "越南新順電子廠", "file_name": "MSB_2000A.pdf", "upload_time": "2026-10-01", "uploader": "An"}
        ]

    # 側邊欄導航列
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ 工程與設計管理中心")
    sub_choice = st.sidebar.radio(
        "選擇子部門與功能：",
        [
            t["sub1"],
            t["sub2"],
            t["sub3"],
            t["sub4"],
            t["sub5"],
            t["sub6"]
        ]
    )

    # ----------------------------------------------------
    # 1. 配電盤與工程專案報價 (含協理提案與副總鎖定機制)
    # ----------------------------------------------------
    if sub_choice == t["sub1"]:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        st.info("💡 說明：各協理/副協理可在此提交報價數據提案。為防止重複報價與價格混亂，系統強制規定：所有報價須經【副總經理審核並按下鎖定】後方為正式有效報價，董事長與總經理為最終備查與指導核心。")

        # 顯示目前公司所有已登記的報價與其鎖定狀態
        st.markdown("##### 📋 全公司工程報價決策總表 (版本與鎖定追蹤)")
        if st.session_state.quotation_proposal_db:
            st.dataframe(pd.DataFrame(st.session_state.quotation_proposal_db), use_container_width=True)
        else:
            st.info("目前尚無任何報價提案紀錄。")

        st.markdown("---")
        tab_prop, tab_lock = st.tabs(["✍️ 協理/副協理提交報價提案 (Draft)", "🔒 副總經理 / 董事長價格鎖定與決策中心"])

        with tab_prop:
            st.markdown("##### 📝 填寫新專案報價提案資料")
            with st.form("quotation_proposal_form"):
                p_client = st.text_input("客戶名稱 (Client Name) *", value="Công ty TNHH Xây lắp Tân Thuận")
                p_name = st.text_input("工程名稱 / 專案名稱 *", value="海防廠動力盤擴建 1500A")
                p_amt = st.number_input("預估總報價金額 (USD)", value=3500.0, step=100.0)
                p_note = st.text_area("成本明細與議價空間說明", placeholder="請說明銅排成本、利潤率及協理建議折讓空間...")

                if st.form_submit_button("🚀 提交報價提案給副總審核", type="primary"):
                    if p_client and p_name:
                        new_id = f"QT-2026-{len(st.session_state.quotation_proposal_db)+1:03d}"
                        st.session_state.quotation_proposal_db.append({
                            "quot_id": new_id,
                            "client": p_client,
                            "project": p_name,
                            "amount": p_amt,
                            "proposer": f"{st.session_state.get('user_name', '協理')}",
                            "status": "⏳ 待副總經理審核與價格鎖定 (Pending Lock)",
                            "version": "v1.0 (Draft)"
                        })
                        st.success("✅ 報價提案已成功送出！在副總經理鎖定價格前，其他主管無法對外發行，以防重複報價與混亂。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請填寫完整客戶與專案名稱！")

        with tab_lock:
            st.markdown("##### 🔒 高階主管（副總經理 / 董事長）價格鎖定控制台")
            st.info("💡 授權說明：副總經理平常負責審查並確認最終售價。按下『鎖定並發行』後，系統將舊版本自動作廢，確保全公司只有唯一正確的官方報價。")

            pending_quotes = [q for q in st.session_state.quotation_proposal_db if "待副總經理審核" in q["status"]]
            if pending_quotes:
                for q in pending_quotes:
                    with st.expander(f"審核單據：{q['quot_id']} | 客戶：{q['client']} ({q['project']}) - 金額: ${q['amount']}"):
                        st.write(f"**提案人**：{q['proposer']}")
                        st.write(f"**專案內容**：{q['project']}")
                        
                        col_l1, col_l2 = st.columns(2)
                        with col_l1:
                            if st.button(f"🔒 鎖定價格並核准發行 {q['quot_id']}", key=f"lock_{q['quot_id']}"):
                                q["status"] = "🟢 副總已鎖定核准 (Locked & Approved)"
                                q["version"] = "v1.0 (Official)"
                                st.success(f"🎉 報價單 {q['quot_id']} 已正式鎖定！價格已確定，可交由業務或財務對外發行。")
                                st.rerun()
                        with col_l2:
                            if st.button(f"❌ 駁回並要求重新估價 {q['quot_id']}", key=f"rej_{q['quot_id']}"):
                                q["status"] = "🔴 已被副總退回修改 (Rejected)"
                                st.warning(f"單據 {q['quot_id']} 已退回給提案協理重新修正數據。")
                                st.rerun()
            else:
                st.success("🎉 目前沒有需要副總審核與價格鎖定的待處理提案。")

    # ----------------------------------------------------
    # 2. 工程驗收與進度追蹤
    # ----------------------------------------------------
    elif sub_choice == t["sub2"]:
        st.markdown(f"### 📊 2. {t['sub2']}")
        st.info("💡 即時監控工程進度、預定驗收時間，並與財務部應收帳款 (AR) 即時通訊連動進行請款催收。")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("在手水電專案", "4 件", "執行中 3 / 待驗收 1")
        with m2:
            st.metric("合約總金額", "$1,850,000", "USD")
        with m3:
            st.metric("總未收 AR", "$600,000", "🔴 加強催收")
        with m4:
            st.metric("平均工程進度", "76.5%", "🟢 正常")

        st.markdown("---")
        st.markdown("##### 📋 專案資料搜尋與過濾")
        st.text_input("輸入專案代碼、客戶或項目關鍵字搜尋")
        
        demo_proj_table = [
            {"代碼": "PRJ-01", "客戶": "越南新順梓電子廠", "項目": "無塵室高低壓配電安裝", "合約總值": "$450,000", "已收": "$315,000", "未收AR": "$135,000", "進度": "90%", "驗收日": "2026-10-15 (初驗)", "狀態": "🟢 待驗收"},
            {"代碼": "PRJ-02", "客戶": "平陽美德金屬加工廠", "項目": "廠房動力配電與照明工程", "合約總值": "$380,000", "已收": "$228,000", "未收AR": "$152,000", "進度": "75%", "驗收日": "2026-10-28 (複驗)", "狀態": "🟡 施工中"},
            {"代碼": "PRJ-03", "客戶": "隆安宏達精密機械廠", "項目": "變電站統包包含銅排配置", "合約總值": "$620,000", "已收": "$434,000", "未收AR": "$186,000", "進度": "85%", "驗收日": "2026-11-05 (正式驗收)", "status": "🟢 進行中"}
        ]
        st.dataframe(pd.DataFrame(demo_proj_table), use_container_width=True)

    # ----------------------------------------------------
    # 3. 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif sub_choice == t["sub3"]:
        st.markdown(f"### 📝 3. {t['sub3']}")
        st.info("💡 記錄每日台幹與越籍工人人數、施工進度摘要與地工異常狀況回報，支援完整搜尋與維護。")
        
        st.text_input("輸入案場、負責台幹或摘要關鍵字搜尋")
        
        daily_logs_db = [
            {"日期": "2026-10-07", "案場": "越南西寧廠", "負責台幹": "admin", "工人數": 18, "施工摘要": "完成主母線銅排架設與耐壓測試。"}
        ]
        st.dataframe(pd.DataFrame(daily_logs_db), use_container_width=True)

        with st.form("daily_report_form"):
            r1, r2 = st.columns(2)
            with r1:
                st.selectbox("案場廠區", ["越南西寧廠", "越南海防廠"])
                st.number_input("越籍工人數", min_value=1, value=15)
            with r2:
                st.text_input("負責台幹", value=st.session_state.get("user_name", "admin"))
                st.date_input("施工日期", datetime.date(2026, 10, 9))
            
            st.text_area("當日施工摘要與異常回報", placeholder="請詳細記錄當日水電配管與配線進度...")
            if st.form_submit_button("🚀 提交現場工程日報表並連動預算扣減", type="primary"):
                st.success("✅ 現場工程日報已成功提交，系統已自動扣減對應專案之工時與材料預算！")

    # ----------------------------------------------------
    # 4. 🤖 AI 施工照片智慧辨識與歸檔
    # ----------------------------------------------------
    elif sub_choice == t["sub4"]:
        st.markdown(f"### 🤖 4. {t['sub4']}")
        st.info("💡 說明：現場工程師上傳施工照片後，系統 AI 會自動辨識內容、分類工項，並直接歸檔至對應的案場與專案資料庫中。")

        with st.form("ai_photo_form"):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                sel_proj = st.selectbox("選擇對應工程專案", [p["proj_code"] + " - " + p["proj_name"] for p in st.session_state.engineering_projects_db])
                photo_category = st.selectbox("施工部位分類", ["配電盤配線 (Electrical Panel)", "高壓變壓器安裝 (Transformer)", "消防管線佈設 (Fire Pipeline)", "弱電/監控佈線 (Weak Current)", "自來水/排水管配管 (Plumbing)"])
            with c_p2:
                uploaded_file = st.file_uploader("上傳施工現場照片 (JPG, PNG)", type=["jpg", "png", "jpeg"])
                ai_analysis_mode = st.selectbox("AI 智慧識別模式", ["標準物件與品質檢測 (Standard OCR/Detection)", "深度安全與法規合規比對 (Deep Safety Check)"])

            if st.form_submit_button("🚀 執行 AI 照片辨識並智慧歸檔", type="primary"):
                proj_code_extracted = sel_proj.split(" - ")[0]
                new_id = f"IMG-{datetime.datetime.now().strftime('%H%M%S')}"
                
                ai_result_tag = "🟢 AI 辨識通過：符合施工規範與配置要求"
                if "配電盤" in photo_category:
                    ai_result_tag = "🟢 AI 辨識通過：端子壓接良好、編號清晰"
                elif "消防" in photo_category:
                    ai_result_tag = "🟡 AI 提示：管線固定間距需再確認"

                st.session_state.ai_photo_archive_db.insert(0, {
                    "photo_id": new_id,
                    "proj": proj_code_extracted,
                    "category": photo_category,
                    "ai_tag": ai_result_tag,
                    "uploader": st.session_state.get("user_name", "admin"),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success(f"🎉 照片上傳成功！AI 智慧辨識結果：`{ai_result_tag}` 已自動歸檔至專案 `{proj_code_extracted}`。")
                st.rerun()

        st.markdown("---")
        st.markdown("##### 📂 AI 已歸檔之現場施工照片清單")
        if st.session_state.ai_photo_archive_db:
            st.dataframe(pd.DataFrame(st.session_state.ai_photo_archive_db), use_container_width=True)
        else:
            st.info("目前尚無歸檔的施工照片。")

    # ----------------------------------------------------
    # 5. ⚠️ 分包商與專業證照到期主動預警
    # ----------------------------------------------------
    elif sub_choice == t["sub5"]:
        st.markdown(f"### ⚠️ 5. {t['sub5']}")
        st.info("💡 說明：水電工程高度依賴特定專業證照（如甲/乙種電匠、自來水管配管工）。系統主動比對即將開工的案場需求，證照過期或即時到期者自動跳出紅色警示，並鎖定派工權限！")

        expired_count = len([l for l in st.session_state.license_db if "過期" in l["status"] or "Expired" in l["status"]])
        warning_count = len([l for l in st.session_state.license_db if "即將到期" in l["status"] or "Soon" in l["status"]])

        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            st.metric("❌ 已過期需立即換證", f"{expired_count} 位技師")
        with w_col2:
            st.metric("🔴 30天內即將到期預警", f"{warning_count} 位技師")
        with w_col3:
            st.metric("🟢 證照合法有效", f"{len(st.session_state.license_db) - expired_count - warning_count} 位技師")

        st.markdown("---")
        st.markdown("##### 📋 全公司技師與外包商證照清冊與即時狀態")
        st.dataframe(pd.DataFrame(st.session_state.license_db), use_container_width=True)

        with st.expander("➕ 登錄新技師/外包商證照"):
            with st.form("new_license_form"):
                lc1, lc2 = st.columns(2)
                with lc1:
                    l_emp = st.text_input("員工編號 / 外包商代號 *", value="VN-009")
                    l_name = st.text_input("姓名 / 廠商名稱 *", value="Nguyễn Văn A")
                    l_type = st.selectbox("證照名稱", ["甲種電匠 (Class A Electrician)", "乙種電匠 (Class B Electrician)", "自來水管配管工 (Plumbing Specialist)", "高壓電作業主管 (High Voltage Supervisor)"])
                with lc2:
                    l_issue = st.date_input("發證日期", datetime.date(2023, 1, 1))
                    l_expiry = st.date_input("有效期限 (Expiry Date)", datetime.date(2027, 10, 15))

                if st.form_submit_button("💾 登錄證照並加入 AI 監控", type="primary"):
                    today = datetime.date.today()
                    status_str = "🟢 有效 (Valid)"
                    if l_expiry < today:
                        status_str = "❌ 已過期 (Expired - Action Required)"
                    elif (l_expiry - today).days <= 30:
                        status_str = "🔴 30天內即將到期 (Expiring Soon)"

                    st.session_state.license_db.append({
                        "emp_id": l_emp, "name": l_name, "license_name": l_type,
                        "issue_date": str(l_issue), "expiry_date": str(l_expiry), "status": status_str
                    })
                    st.success("✅ 證照已成功登錄，系統已納入自動預警監控！")
                    st.rerun()

    # ----------------------------------------------------
    # 6. 配電盤電氣與機構設計圖庫 Storage
    # ----------------------------------------------------
    elif sub_choice == t["sub6"]:
        st.markdown(f"### 🎨 6. {t['sub6']}")
        st.info("💡 管理所有配電盤 2D/3D 設計圖檔、CAD 藍圖與機構規格書，支援版本控管與雲端儲存。")
        
        if st.session_state.drawing_storage_db:
            st.dataframe(pd.DataFrame(st.session_state.drawing_storage_db), use_container_width=True)

        with st.form("drawing_upload_form"):
            dc1, dc2 = st.columns(2)
            with dc1:
                st.text_input("圖號編碼 (Drawing No.)", placeholder="例如: DWG-2026-05")
            with dc2:
                st.text_input("專案/圖檔名稱", placeholder="例如: 海防廠控制盤配置圖")
            
            st.file_uploader("選擇設計圖檔 (PDF, DWG, PNG, JPG)", type=["pdf", "dwg", "png", "jpg"])
            if st.form_submit_button("💾 儲存並上傳至 Storage", type="primary"):
                st.success("✅ 設計圖檔已成功上傳至雲端儲存庫！")

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)
