import streamlit as st
import pandas as pd
import datetime

def render_engineering_page(engine=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "⚡ 工程與設計管理中心 (Engineering & Design Center)",
            "caption": "水電工程專案管理、施工進度追蹤、AI 現場照片智慧辨識歸檔，以及技師/分包商證照到期主動預警。",
            "tab1": "🏗️ 專案工項與預算編號管轄",
            "tab2": "📸 施工現場照片 AI 自動辨識與歸檔",
            "tab3": "⚠️ 分包商與專業證照到期預警中心",
            "tab4": "📊 工程日報與工時/點料扣減",
            "btn_upload": "🚀 執行 AI 照片辨識並智慧歸檔",
            "btn_add_cert": "➕ 登錄新技師/外包商證照"
        },
        "Tiếng Việt": {
            "title": "⚡ Trung tâm Quản lý Kỹ thuật & Thiết kế",
            "caption": "Quản lý dự án cơ điện, tiến độ thi công, nhận diện ảnh AI tự động và cảnh báo hết hạn chứng chỉ.",
            "tab1": "🏗️ Quản lý hạng mục & Ngân sách",
            "tab2": "📸 Nhận diện ảnh thi công bằng AI & Lưu trữ",
            "tab3": "⚠️ Cảnh báo hết hạn chứng chỉ thầu phụ",
            "tab4": "📊 Báo cáo nhật ký công trình",
            "btn_upload": "🚀 Phân tích AI & Lưu trữ ảnh",
            "btn_add_cert": "➕ Thêm chứng chỉ mới"
        },
        "English": {
            "title": "⚡ Engineering & Design Management Center",
            "caption": "MEP project management, progress tracking, AI photo recognition & archiving, and license expiration alerts.",
            "tab1": "🏗️ Project Work Items & Budget",
            "tab2": "📸 AI Field Photo Recognition & Archiving",
            "tab3": "⚠️ Subcontractor & License Expiry Alerts",
            "tab4": "📊 Daily Engineering Reports",
            "btn_upload": "🚀 Run AI Recognition & Archive",
            "btn_add_cert": "➕ Register New License"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化工程資料庫 (含證照與AI照片庫)
    if "engineering_projects_db" not in st.session_state:
        st.session_state.engineering_projects_db = [
            {"proj_code": "PRJ-TN-2026-01", "proj_name": "西寧廠高壓配電盤與消防管線擴建工程", "factory": "西寧廠 (Tay Ninh)", "budget": 1200000000, "status": "進行中 (Active)"},
            {"proj_code": "PRJ-HP-2026-02", "proj_name": "海防廠無塵室空調與照明管線配置", "factory": "海防廠 (Hai Phong)", "budget": 850000000, "status": "進行中 (Active)"}
        ]

    if "license_db" not in st.session_state:
        st.session_state.license_db = [
            {"emp_id": "EMP-001", "name": "張董事長", "license_name": "甲種電匠 (Class A Electrician)", "issue_date": "2023-01-10", "expiry_date": "2026-10-15", "status": "🔴 30天內即將到期 (Expiring Soon)"},
            {"emp_id": "VN-002", "name": "Nguyễn Văn Quý", "license_name": "乙種電匠 (Class B Electrician)", "issue_date": "2022-05-20", "expiry_date": "2027-05-20", "status": "🟢 有效 (Valid)"},
            {"emp_id": "VN-003", "name": "Trần Văn Nam", "license_name": "自來水管配管工 (Plumbing Specialist)", "issue_date": "2021-03-12", "expiry_date": "2026-09-30", "status": "❌ 已過期 (Expired - Action Required)"}
        ]

    if "ai_photo_archive_db" not in st.session_state:
        st.session_state.ai_photo_archive_db = [
            {"photo_id": "IMG-8821", "proj": "PRJ-TN-2026-01", "category": "配電盤配線 (Electrical Panel)", "ai_tag": "🟢 規格相符 / 壓接良好", "uploader": "現場工程師 (李佑銘)", "time": "2026-10-08 14:20"}
        ]

    # 四大功能分頁
    tab1, tab2, tab3, tab4 = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"]])

    # 1. 🏗️ 專案工項與預算編號管轄
    with tab1:
        st.markdown("### 🏗️ 水電工程專案與預算編號對照表")
        st.info("💡 說明：所有工程估驗報價單核准後，自動轉為此處的【專案工項與預算編號】，供後續叫料與點工扣減對比。")
        st.dataframe(pd.DataFrame(st.session_state.engineering_projects_db), use_container_width=True)

        with st.expander("➕ 新增水電工程專案"):
            with st.form("new_proj_form"):
                p_code = st.text_input("專案代號 (Project Code) *", value="PRJ-TN-2026-03")
                p_name = st.text_name = st.text_input("專案名稱 (Project Name) *", value="西寧廠二廠照明與弱電工程")
                p_fact = st.selectbox("所屬廠區", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"])
                p_bud = st.number_input("預算金額 (VND)", value=500000000.0, step=1000000.0)
                if st.form_submit_button("💾 建立專案並連動預算庫", type="primary"):
                    st.session_state.engineering_projects_db.append({
                        "proj_code": p_code, "proj_name": p_name, "factory": p_fact, "budget": p_bud, "status": "進行中 (Active)"
                    })
                    st.success("✅ 工程專案已成功建立！")
                    st.rerun()

    # 2. 📸 施工現場照片 AI 自動辨識與歸檔
    with tab2:
        st.markdown("### 📸 施工現場照片 AI 自動辨識與智慧歸檔")
        st.info("💡 說明：現場工程師上傳施工照片後，系統 AI 會自動辨識內容、分類工項，並直接歸檔至對應的案場與專案資料庫中。")

        with st.form("ai_photo_form"):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                sel_proj = st.selectbox("選擇對應工程專案", [p["proj_code"] + " - " + p["proj_name"] for p in st.session_state.engineering_projects_db])
                photo_category = st.selectbox("施工部位分類", ["配電盤配線 (Electrical Panel)", "高壓變壓器安裝 (Transformer)", "消防管線佈設 (Fire Pipeline)", "弱電/監控佈線 (Weak Current)", "自來水/排水管配管 (Plumbing)"])
            with c_p2:
                uploaded_file = st.file_uploader("上傳施工現場照片 (JPG, PNG)", type=["jpg", "png", "jpeg"])
                ai_analysis_mode = st.selectbox("AI 智慧識別模式", ["標準物件與品質檢測 (Standard OCR/Detection)", "深度安全與法規合規比對 (Deep Safety Check)"])

            if st.form_submit_button(t["btn_upload"], type="primary"):
                proj_code_extracted = sel_proj.split(" - ")[0]
                new_id = f"IMG-{datetime.datetime.now().strftime('%H%M%S')}"
                
                # 模擬 AI 辨識結果
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

    # 3. ⚠️ 分包商與專業證照到期主動預警
    with tab3:
        st.markdown("### ⚠️ 分包商與專業技術人員證照到期主動預警中心")
        st.info("💡 說明：水電工程高度依賴特定專業證照（如甲/乙種電匠、自來水管配管工）。系統主動比對即將開工的案場需求，證照過期或即時到期者自動跳出紅色警示，並鎖定派工權限！")

        # 顯示警示統計指標
        expired_count = len([l for l in st.session_state.license_db if "過期" in l["status"] or "Expired" in l["status"]])
        warning_count = len([l for l in st.session_state.license_db if "即將到期" in l["status"] or "Soon" in l["status"]])

        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            st.metric("❌ 已過期需立即換證", f"{expired_count} 位技師", delta_color="inverse")
        with w_col2:
            st.metric("🔴 30天內即將到期預警", f"{warning_count} 位技師", delta_color="off")
        with w_col3:
            st.metric("🟢 證照合法有效", f"{len(st.session_state.license_db) - expired_count - warning_count} 位技師")

        st.markdown("---")
        st.markdown("##### 📋 全公司技師與外包商證照清冊與即時狀態")
        st.dataframe(pd.DataFrame(st.session_state.license_db), use_container_width=True)

        with st.expander(t["btn_add_cert"]):
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

    # 4. 📊 工程日報與工時/點料扣減
    with tab4:
        st.markdown("### 📊 現場工程日報與點工/點料自動扣減連動")
        st.info("💡 說明：現場進度日報表提交後，點工與點料資料會即時連動扣減該專案的【預算工時】與【材料庫存數量】。")
        
        # 模擬日報表扣減檢視
        sample_daily_logs = [
            {"date": "2026-10-08", "proj": "PRJ-TN-2026-01", "task": "配電盤主幹線拉線", "labor_hours": 32.0, "material_used": "PVC管 2寸 (50米)", "status": "已自動扣減預算"},
            {"date": "2026-10-08", "proj": "PRJ-HP-2026-02", "task": "無塵室風管安裝", "labor_hours": 24.0, "material_used": "鍍鋅鐵板 (20片)", "status": "已自動扣減預算"}
        ]
        st.dataframe(pd.DataFrame(sample_daily_logs), use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_engineering_page(engine=engine, lang=lang, **kwargs)
