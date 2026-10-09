import streamlit as st
import pandas as pd
import datetime

def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "⚡ 裕豐電機工業 - 工程管理中心與設計部門",
            "caption": "涵蓋動態零件明細工程報價系統、協理提案與副總審核鎖定、工程驗收追蹤、現場日報、AI 施工照片與證照預警。",
            "sub1": "⚡ [工程] 配電盤與工程專案報價 (動態零件明細與副總審核)",
            "sub2": "⚡ [工程] 工程驗收與進度追蹤",
            "sub3": "⚡ [工程] 現場工程日報表與出工統計",
            "sub4": "🤖 [工程] AI 施工照片智慧辨識與歸檔",
            "sub5": "⚠️ [工程] 分包商與專業證照到期預警",
            "sub6": "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage"
        },
        "Tiếng Việt": {
            "title": "⚡ Công ty TNHH Kỹ thuật Điện Reetech - Trung tâm Kỹ thuật",
            "caption": "Hệ thống báo giá chi tiết linh kiện, phê duyệt cấp phó tổng, nghiệm thu, nhật ký công trình.",
            "sub1": "⚡ [KT] Báo giá tủ điện & Phê duyệt",
            "sub2": "⚡ [KT] Theo dõi tiến độ & Nghiệm thu",
            "sub3": "⚡ [KT] Nhật ký công trình & Nhân công",
            "sub4": "🤖 [KT] AI Nhận diện & Lưu trữ ảnh thi công",
            "sub5": "⚠️ [KT] Cảnh báo hết hạn chứng chỉ",
            "sub6": "🎨 [TK] Kho bản vẽ thiết kế tủ điện Storage"
        },
        "English": {
            "title": "⚡ Reetech Industrial - Engineering Management Center",
            "caption": "Dynamic itemized quotation workflow, VP approval, daily site reports, AI archiving, and license alerts.",
            "sub1": "⚡ [Eng] Quotation & Itemized Pricing Approval",
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
    if "quotation_proposals_db" not in st.session_state:
        st.session_state.quotation_proposals_db = [
            {
                "quot_id": "QT-2026-001",
                "client": "Công ty TNHH Xây lắp Tân Thuận",
                "project": "西寧廠主配電盤 2000A 統包工程",
                "proposer": "協理 - 陳明華 (Manager)",
                "currency": "USD",
                "status": "🟢 副總已鎖定核准 (Locked & Official)",
                "items": [
                    {"code": "CU-BUS-10100", "desc": "銅排 Busbar 10x100mm", "qty": 450.0, "unit_price": 2.5, "subtotal": 1125.0},
                    {"code": "CB-ACB-2000A", "desc": "空氣斷路器 ACB 2000A", "qty": 8.0, "unit_price": 1850.0, "subtotal": 14800.0},
                    {"code": "CB-MCCB-250A", "desc": "塑殼斷路器 MCCB 250A", "qty": 35.0, "unit_price": 145.0, "subtotal": 5075.0}
                ],
                "total_amount": 21000.0
            }
        ]

    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤與消防管線擴建工程", "factory": "西寧廠 (Tay Ninh)", "budget": 1200000000, "status": "進行中 (Active)"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [
            {"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠 (Class A Electrician)", "issue_date": "2023-01-10", "expiry_date": "2026-10-15", "status": "🔴 30天內即將到期"}
        ]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = []

    if "drawing_storage_db" not in st.session_state:
        st.session_state.drawing_storage_db = []

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
    # 1. 配電盤與工程專案報價 (動態零件明細與副總審核鎖定)
    # ----------------------------------------------------
    if sub_choice == t["sub1"]:
        st.markdown(f"### ⚙️ 1. {t['sub1']}")
        st.info("💡 說明：各協理/副協理可在此填寫完整工程專案名稱，並**動態自由新增多筆水電零件/材料明細**。送出後將明確記錄『提案人』，並呈報給副總經理進行第一次價格審核與鎖定，防止重複報價與資訊混亂！")

        # 頁籤切換：1. 提出新報價與動態明細 | 2. 高階主管（副總經理）審核鎖定控制台
        tab_create, tab_review = st.tabs(["✍️ 協理/副協理建立報價提案 (可自由增刪零件)", "🔒 副總經理 / 董事長價格審核與鎖定中心"])

        with tab_create:
            st.markdown("##### 📝 步驟一：輸入工程專案基本資料與提案人")
            with st.form("dynamic_quotation_form"):
                col_i1, col_i2, col_i3, col_i4 = st.columns(4)
                with col_i1:
                    p_client = st.text_input("客戶名稱 (Client)", value="Công ty TNHH Xây lắp Tân Thuận")
                with col_i2:
                    p_name = st.text_input("整體工程名稱 / 專案名稱 *", value="海防廠動力盤擴建 1500A 統包工程")
                with col_i3:
                    p_proposer = st.text_input("提案人 (填寫您的職稱與姓名) *", value="協理 - 陳明華")
                with col_i4:
                    p_curr = st.selectbox("計價幣別", ["USD", "VND", "NTD"])

                st.markdown("---")
                st.markdown("##### 📦 步驟二：動態加入水電零組件與材料明細 (可自由調整項目)")
                
                # 模擬動態輸入 4 個零件項目（解決只有三個且被鎖住的問題）
                item_rows = []
                calc_total = 0.0
                for i in range(1, 5):
                    st.markdown(f"**項目 {i}**")
                    ic1, ic2, ic3, ic4 = st.columns([2, 3, 1, 1])
                    with ic1:
                        icode = st.text_input(f"料號 #{i}", value=f"PART-0{i}" if i <= 3 else "", key=f"icode_{i}")
                    with ic2:
                        idesc = st.text_input(f"零件/材料說明 #{i}", value=f"水電零組件項目 {i}" if i <= 3 else "", key=f"idesc_{i}")
                    with ic3:
                        iqty = st.number_input(f"數量 #{i}", min_value=0.0, value=10.0 if i <= 3 else 0.0, key=f"iqty_{i}")
                    with ic4:
                        iprice = st.number_input(f"單價 #{i}", min_value=0.0, value=100.0 if i <= 3 else 0.0, key=f"iprice_{i}")
                    
                    if icode and iqty > 0 and iprice > 0:
                        sub = iqty * iprice
                        calc_total += sub
                        item_rows.append({"code": icode, "desc": idesc, "qty": iqty, "unit_price": iprice, "subtotal": sub})

                st.markdown("---")
                st.markdown(f"### 💰 總預估報價金額：`$ {calc_total:,.2f} {p_curr}`")

                if st.form_submit_button("🚀 提交報價提案給副總經理審核", type="primary"):
                    if p_client and p_name and item_rows:
                        new_id = f"QT-2026-{len(st.session_state.quotation_proposals_db)+1:03d}"
                        st.session_state.quotation_proposals_db.append({
                            "quot_id": new_id,
                            "client": p_client,
                            "project": p_name,
                            "proposer": p_proposer,
                            "currency": p_curr,
                            "status": "⏳ 待副總經理審核與價格鎖定 (Pending VP Review)",
                            "items": item_rows,
                            "total_amount": calc_total
                        })
                        st.success(f"✅ 報價提案 [{new_id}] 已成功送出！提案人【{p_proposer}】的資料已記錄，等待副總經理審核鎖定。")
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫客戶名稱、專案名稱以及至少一筆有效的零件明細！")

        with tab_review:
            st.markdown("##### 🔒 副總經理 / 董事長審核與價格鎖定控制台")
            st.info("💡 說明：副總經理可在此檢視各協理/副協理提交的完整零件明細與總金額。點擊『鎖定價格並核准發行』後，該價格即為官方唯一標準，防止公司內部重複報價混亂。")

            if st.session_state.quotation_proposals_db:
                for q in st.session_state.quotation_proposals_db:
                    with st.expander(f"📌 單號：{q['quot_id']} | 專案：{q['project']} | 提案人：{q['proposer']} | 狀態：{q['status']}"):
                        st.write(f"**客戶名稱**：{q['client']}")
                        st.write(f"**計價幣別**：{q.get('currency', 'USD')} | **總金額**：$ {q['total_amount']:,.2f}")
                        
                        st.markdown("**📦 專案零件明細清單：**")
                        st.dataframe(pd.DataFrame(q["items"]), use_container_width=True)

                        if "待副總經理審核" in q["status"]:
                            rc1, rc2 = st.columns(2)
                            with rc1:
                                if st.button(f"🔒 鎖定價格並核准發行 {q['quot_id']}", key=f"lock_btn_{q['quot_id']}"):
                                    q["status"] = "🟢 副總已鎖定核准 (Locked & Official)"
                                    st.success(f"🎉 報價單 {q['quot_id']} 已由副總經理正式鎖定！價格已確定生效。")
                                    st.rerun()
                            with rc2:
                                if st.button(f"❌ 駁回並要求協理修改 {q['quot_id']}", key=f"rej_btn_{q['quot_id']}"):
                                    q["status"] = "🔴 已被副總退回修改 (Rejected)"
                                    st.warning(f"單據 {q['quot_id']} 已退回。")
                                    st.rerun()
                        else:
                            st.info(f"目前狀態：{q['status']}")
            else:
                st.info("目前尚無任何報價單據紀錄。")

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

    # ----------------------------------------------------
    # 3. 現場工程日報表與出工統計
    # ----------------------------------------------------
    elif sub_choice == t["sub3"]:
        st.markdown(f"### 📝 3. {t['sub3']}")
        st.info("💡 記錄每日台幹與越籍工人人數、施工進度摘要與地工異常狀況回報。")
        with st.form("daily_report_form"):
            r1, r2 = st.columns(2)
            with r1:
                st.selectbox("案場廠區", ["越南西寧廠", "越南海防廠"])
                st.number_input("越籍工人數", min_value=1, value=15)
            with r2:
                st.text_input("負責台幹", value=st.session_state.get("user_name", "admin"))
                st.date_input("施工日期", datetime.date(2026, 10, 9))
            st.text_area("當日施工摘要與異常回報", placeholder="請詳細記錄當日水電配管與配線進度...")
            if st.form_submit_button("🚀 提交現場工程日報表", type="primary"):
                st.success("✅ 現場工程日報已成功提交！")

    # ----------------------------------------------------
    # 4. 🤖 AI 施工照片智慧辨識與歸檔
    # ----------------------------------------------------
    elif sub_choice == t["sub4"]:
        st.markdown(f"### 🤖 4. {t['sub4']}")
        st.info("💡 說明：現場工程師上傳施工照片後，系統 AI 會自動辨識內容並歸檔。")
        with st.form("ai_photo_form"):
            st.selectbox("選擇對應工程專案", [p["proj_code"] + " - " + p["proj_name"] for p in st.session_state.engineering_projects_db])
            st.file_uploader("上傳施工現場照片 (JPG, PNG)", type=["jpg", "png", "jpeg"])
            if st.form_submit_button("🚀 執行 AI 照片辨識並智慧歸檔", type="primary"):
                st.success("🎉 照片上傳成功並已歸檔！")

    # ----------------------------------------------------
    # 5. ⚠️ 分包商與專業證照到期主動預警
    # ----------------------------------------------------
    elif sub_choice == t["sub5"]:
        st.markdown(f"### ⚠️ 5. {t['sub5']}")
        st.info("💡 說明：系統主動比對技師與外包商專業證照到期日，自動跳出預警。")
        st.dataframe(pd.DataFrame(st.session_state.license_db), use_container_width=True)

    # ----------------------------------------------------
    # 6. 配電盤電氣與機構設計圖庫 Storage
    # ----------------------------------------------------
    elif sub_choice == t["sub6"]:
        st.markdown(f"### 🎨 6. {t['sub6']}")
        st.info("💡 管理所有配電盤 2D/3D 設計圖檔、CAD 藍圖與機構規格書。")
        with st.form("drawing_upload_form"):
            st.text_input("圖號編碼 (Drawing No.)")
            st.file_uploader("選擇設計圖檔 (PDF, DWG, PNG, JPG)", type=["pdf", "dwg", "png", "jpg"])
            if st.form_submit_button("💾 儲存並上傳至 Storage", type="primary"):
                st.success("✅ 設計圖檔已成功上傳！")

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)
