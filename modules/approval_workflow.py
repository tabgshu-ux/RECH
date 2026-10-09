import streamlit as st
import pandas as pd

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "✍️ 全公司電子簽核與工程報價/請款審核中心",
            "info": "提交請假、採購或工程雙層報價，系統自動依據權限進行多級簽核（協理提案 ➔ 副總核准 ➔ 總經理/董事長拍板）。",
            "tab1": "✍️ 員工請假申請單",
            "tab2": "📦 採購與請款申請單",
            "tab3": "📊 簽核進度即時追蹤",
            "tab4": "📋 待簽核案件審查 (主管專區)",
            "form1_title": "### 📝 填寫請假申請單",
            "applicant": "申請人 (已鎖定登入帳號)",
            "dept": "所屬部門 (依帳號自動對應)",
            "days": "請假天數 (天) *",
            "reason": "申請事由與說明 *",
            "reason_ph": "例如: 因家庭事務請假 4 天...",
            "submit_btn": "🚀 提交送出簽核",
            "success_msg": "✅ 請假申請已成功提交並進入電子簽核流程！"
        },
        "Tiếng Việt": {
            "title": "✍️ Trung tâm Phê duyệt Điện tử & Báo giá Kỹ thuật",
            "info": "Gửi đơn nghỉ phép, mua hàng hoặc báo giá 2 lớp, hệ thống tự động phê duyệt đa cấp.",
            "tab1": "✍️ Đơn xin nghỉ phép",
            "tab2": "📦 Đơn mua hàng & Thanh toán",
            "tab3": "📊 Theo dõi tiến độ phê duyệt",
            "tab4": "📋 Xét duyệt chờ xử lý (Dành cho cấp quản lý)",
            "form1_title": "### 📝 Điền đơn xin nghỉ phép",
            "applicant": "Người nộp đơn",
            "dept": "Phòng ban",
            "days": "Số ngày nghỉ (ngày) *",
            "reason": "Lý do & Mô tả chi tiết *",
            "reason_ph": "Ví dụ: Nghỉ việc gia đình...",
            "submit_btn": "🚀 Gửi yêu cầu phê duyệt",
            "success_msg": "✅ Đơn xin nghỉ phép đã được gửi thành công!"
        },
        "English": {
            "title": "✍️ Enterprise Approval & Engineering Quotation Center",
            "info": "Submit leave, procurement, or two-tier engineering quotations with automated multi-level approval workflows.",
            "tab1": "✍️ Submit Leave Request",
            "tab2": "📦 Purchase & Payment Request",
            "tab3": "📊 Real-time Approval Tracking",
            "tab4": "📋 Pending Approvals Review (Management)",
            "form1_title": "### 📝 Leave Application Form",
            "applicant": "Applicant",
            "dept": "Department",
            "days": "Leave Days *",
            "reason": "Reason & Description *",
            "reason_ph": "e.g., Family affairs...",
            "submit_btn": "🚀 Submit for Approval",
            "success_msg": "✅ Leave application submitted successfully!"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.info(t["info"])

    # 初始化簽核資料庫
    if "approval_db" not in st.session_state:
        st.session_state.approval_db = [
            {
                "單號": "APV-2026-001", "類型": "請假單", "申請人": "admin", "部門": "總經理室",
                "內容": "家庭事務請假 3 天", "狀態": "簽核中 (Pending)", "送出時間": "2026-10-07"
            }
        ]

    tab1, tab2, tab3, tab4 = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"]])

    with tab1:
        with st.form("leave_application_form"):
            st.markdown(t["form1_title"])
            c1, c2 = st.columns(2)
            with c1:
                st.text_input(t["applicant"], value=st.session_state.get("user_name", "admin"), disabled=True, key="lev_user")
            with c2:
                st.text_input(t["dept"], value="總經理室 / Executive Office", disabled=True, key="lev_dept")

            leave_days = st.number_input(t["days"], min_value=0.5, value=3.0, step=0.5, key="lev_days")
            leave_reason = st.text_area(t["reason"], placeholder=t["reason_ph"], key="lev_reason")

            if st.form_submit_button(t["submit_btn"], type="primary"):
                if leave_reason:
                    new_no = f"APV-2026-{len(st.session_state.approval_db)+1:03d}"
                    st.session_state.approval_db.append({
                        "單號": new_no,
                        "類型": "請假單 (Leave)",
                        "申請人": st.session_state.get("user_name", "admin"),
                        "部門": "總經理室",
                        "內容": f"請假 {leave_days} 天: {leave_reason}",
                        "狀態": "簽核中 (Pending)",
                        "送出時間": datetime_str_now() if 'datetime_str_now' in globals() else "2026-10-09"
                    })
                    st.success(t["success_msg"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫申請事由！")

    with tab2:
        st.markdown("### 📦 採購與請款申請單 (Purchase & Payment Request)")
        with st.form("purchase_approval_form"):
            p_item = st.text_input("採購項目 / 品名 (Item Name) *", placeholder="例如: 變壓器 / 零件...")
            p_amt = st.number_input("預估金額 (Estimated Amount VND)", value=5000000.0, step=100.00)
            p_desc = st.text_area("採購用途與必要性說明", placeholder="請說明採購原因...")

            if st.form_submit_button("🚀 提交採購請款簽核", type="primary"):
                if p_item:
                    new_no = f"APV-2026-{len(st.session_state.approval_db)+1:03d}"
                    st.session_state.approval_db.append({
                        "單號": new_no,
                        "類型": "採購請款單",
                        "申請人": st.session_state.get("user_name", "admin"),
                        "部門": "工程與設計管理中心",
                        "內容": f"採購: {p_item} (金額: {p_amt:,.0f} VND)",
                        "狀態": "簽核中 (Pending)",
                        "送出時間": "2026-10-09"
                    })
                    st.success("✅ 採購申請已送出並進入電子簽核流程！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫採購項目名稱！")

    with tab3:
        st.markdown("### 📊 全公司簽核進度即時追蹤")
        if st.session_state.approval_db:
            st.dataframe(pd.DataFrame(st.session_state.approval_db), use_container_width=True)
        else:
            st.info("目前尚無任何簽核單據紀錄。")

    with tab4:
        st.markdown("### 📋 主管待簽核案件審查 (副總 / 總經理 / 董事長專區)")
        st.info("💡 說明：主管可在此審查一般請假、採購單，以及**工程部提交的雙層報價案（包含內部機密成本與對外業主報價）**。")

        # 1. 審查一般簽核單據 (請假、採購)
        st.markdown("##### 📌 一般電子簽核案件")
        pending_general = [item for item in st.session_state.approval_db if "簽核中" in item["狀態"]]
        if pending_general:
            for idx, item in enumerate(pending_general):
                with st.expander(f"單據：{item['單號']} - {item['類型']} ({item['申請人']})"):
                    st.write(f"**部門**：{item['部門']} | **內容**：{item['內容']}")
                    c_g1, c_g2 = st.columns(2)
                    with c_g1:
                        if st.button(f"✅ 核准單據 {item['單號']}", key=f"app_gen_{idx}"):
                            item["狀態"] = "🟢 已核准 (Approved)"
                            st.success("已核准！")
                            st.rerun()
                    with c_g2:
                        if st.button(f"❌ 駁回單據 {item['單號']}", key=f"rej_gen_{idx}"):
                            item["狀態"] = "🔴 已退回 (Rejected)"
                            st.error("已退回。")
                            st.rerun()
        else:
            st.success("🎉 目前沒有一般待辦簽核案件。")

        st.markdown("---")
        st.markdown("##### ⚡ 工程部雙層報價與重大採購核決專區 (副總 ➔ 總經理/董事長兩階段)")
        
        # 2. 審查工程部雙層報價單 (`two_tier_quotations_db`)
        if "two_tier_quotations_db" in st.session_state and st.session_state.two_tier_quotations_db:
            for q in st.session_state.two_tier_quotations_db:
                with st.expander(f"📌 工程報價單號：{q['quot_id']} | 專案：{q['project_name']} | 提案人：{q['proposer']} | 狀態：{q['status']}", expanded=True):
                    st.write(f"**客戶名稱**：{q['client']} | **幣別**：{q.get('currency', 'USD')}")
                    st.write(f"**🔒 【內部機密】內部成本總和**：`$ {q['total_internal_cost']:,.2f}`")
                    
                    st.markdown("**📦 內部成本明細表 (機櫃、材料、人工)：**")
                    st.dataframe(pd.DataFrame(q["internal_items"]), use_container_width=True)

                    st.markdown("---")
                    st.markdown(f"**📄 【對外業主報價金額】**：`$ {q['customer_price']:,.2f}`")
                    st.text_area(f"對外業主合約摘要預覽 ({q['quot_id']})", value=q["customer_facing_summary"], disabled=True, key=f"app_sum_{q['quot_id']}")

                    st.markdown(f"**📍 目前關卡**：`{q['status']}`")

                    # 🎯 兩階段核決按鈕
                    col_b1, col_b2 = st.columns(2)
                    if "待副總經理審核" in q["status"] or "[階段一]" in q["status"] or "待副總" in q["status"]:
                        with col_b1:
                            if st.button(f"🔒 【副總經理】核准並鎖定價格 (呈報總經理) {q['quot_id']}", key=f"center_vp_{q['quot_id']}", type="primary"):
                                q["status"] = "🟢 副總已核准，待總經理/董事長最終確認 (Waiting Board Sign-off)"
                                st.success("🎉 副總已核准！單據已自動轉交至總經理與董事長進行最終拍板。")
                                st.rerun()
                        with col_b2:
                            if st.button(f"❌ 副總退回修改 {q['quot_id']}", key=f"center_rej_vp_{q['quot_id']}"):
                                q["status"] = "🔴 已被副總退回修改"
                                st.warning("已退回給提案協理。")
                                st.rerun()

                    elif "待總經理" in q["status"] or "等待總經理" in q["status"] or "Waiting Board" in q["status"]:
                        with col_b1:
                            if st.button(f"👑 【總經理 / 董事長】最終拍板發行 {q['quot_id']}", key=f"center_board_{q['quot_id']}", type="primary"):
                                q["status"] = "🎉 董事長/總經理已最終拍板發行 (Official)"
                                st.success("🎉 恭喜！總經理與董事長已完成最終拍板，報價單正式生效！")
                                st.rerun()
                        with col_b2:
                            if st.button(f"❌ 董事長退回複查 {q['quot_id']}", key=f"center_rej_board_{q['quot_id']}"):
                                q["status"] = "🔴 董事長要求重新評估成本"
                                st.warning("已退回複查。")
                                st.rerun()
                    else:
                        st.success("✅ 此工程報價單已完成所有高階主管核決流程。")
        else:
            st.info("目前尚無工程雙層報價待審案件。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_approval_center(engine=engine, lang=lang, **kwargs)
