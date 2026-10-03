import pandas as pd
import streamlit as st


def render_approval_center(lang="繁體中文"):
    st.title("✍️ 管理部 - 電子簽核與請款審核中心")
    st.caption("跨部門電子流程審核：涵蓋請假、採購、合約、請款、借款與資產報廢等全方位簽核。")

    # 取得當前登入者身分
    current_user = st.session_state.get("user_name", "Staff")
    current_role = st.session_state.get("user_role", "staff").lower()

    # 初始化簽核表單資料庫 (若無資料)
    if "approval_tasks_db" not in st.session_state or not st.session_state.approval_tasks_db:
        st.session_state.approval_tasks_db = [
            {
                "id": "APP-2026-001",
                "category": "🌴 人事行政 - 員工請假申請",
                "title": "越南西寧廠技術員事假 2 天",
                "applicant": "Nguyễn Văn An (Staff)",
                "date": "2026-10-02",
                "amount": "-",
                "details": "因家屬探親請假 2 天 (已安排職務代理人)",
                "status": "待審核",
            },
            {
                "id": "APP-2026-002",
                "category": "💰 財務採購 - 採購與請款單",
                "title": "西寧廠塗裝粉體原料採購款",
                "applicant": "陳美璇 (Finance Staff)",
                "date": "2026-10-02",
                "amount": "$12,500 USD",
                "details": "採購環保靜電粉末塗料 500 公斤",
                "status": "待審核",
            },
            {
                "id": "APP-2026-003",
                "category": "📜 業務合約 - 工程合約審核",
                "title": "西寧紡織廠 2000A 主配電櫃合約",
                "applicant": "張偉豪 (Manager)",
                "date": "2026-10-01",
                "amount": "₫ 6,350,000,000 VND",
                "details": "合約條款已由法務與財務確認，申請董事長用印",
                "status": "待審核",
            },
            {
                "id": "APP-2026-004",
                "category": "💳 財務行政 - 員工借款/預支申請",
                "title": "生產部作業員急難預支薪資",
                "applicant": "王小明 (Staff)",
                "date": "2026-10-01",
                "amount": "5,000,000 VND",
                "details": "家中急需，申請預支並分 2 個月從薪資扣回",
                "status": "待審核",
            },
        ]

    tab_pending, tab_history, tab_new = st.tabs([
        "📥 待審核清單 (Pending)",
        "📜 歷史簽核紀錄 (History)",
        "➕ 提交新簽核申請 (Submit)"
    ])

    # ----------------------------------------------------
    # 📥 頁籤一：待審核清單
    # ----------------------------------------------------
    with tab_pending:
        st.markdown(f"### 📥 待審核項目列表 (當前登入: `{current_user}` | 角色: `{current_role.upper()}`)")
        
        pending_items = [item for item in st.session_state.approval_tasks_db if item["status"] == "待審核"]

        if not pending_items:
            st.success("🎉 目前沒有需要您審核的待辦事項！")
        else:
            for item in pending_items:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 12px;">
                            <div style="font-size: 13px; color: #64748b; font-weight: 700;">📂 類別: {item['category']} | 編號: <code>{item['id']}</code></div>
                            <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 4px;">📌 {item['title']}</div>
                            <div style="font-size: 14px; color: #334155; margin-top: 6px;">
                                • <b>申請人</b>: {item['applicant']} &nbsp;|&nbsp; <b>申請日期</b>: {item['date']} &nbsp;|&nbsp; <b>金額/影響</b>: <span style="color: #047857; font-weight:bold;">{item['amount']}</span><br>
                                • <b>內容細節</b>: {item['details']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                    with col_btn1:
                        if st.button("✅ 核准簽核", type="primary", key=f"approve_{item['id']}"):
                            item["status"] = "已核准"
                            st.success(f"🎉 已成功核准單據 [{item['id']}]！")
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ 駁回退回", key=f"reject_{item['id']}"):
                            item["status"] = "已駁回"
                            st.warning(f"⚠️ 已將單據 [{item['id']}] 駁回並退給申請人。")
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 📜 頁籤二：歷史紀錄
    # ----------------------------------------------------
    with tab_history:
        st.markdown("### 📜 歷史簽核與歸檔紀錄")
        df_history = pd.DataFrame(st.session_state.approval_tasks_db)
        st.dataframe(df_history, use_container_width=True)

    # ----------------------------------------------------
    # ➕ 頁籤三：提交新簽核申請
    # ----------------------------------------------------
    with tab_new:
        st.markdown("### ➕ 提交跨部門電子簽核申請")
        with st.form("form_submit_approval"):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox(
                    "選擇簽核項目類別 *",
                    [
                        "🌴 人事行政 - 員工請假/加班單",
                        "💰 財務採購 - 採購單與請款單 (AP)",
                        "📜 業務合約 - 客戶報價與工程合約",
                        "💳 財務行政 - 員工借款/預支薪資申請",
                        "🛠️ 工務技術 - 設計變更與驗收單",
                        "📦 生產總務 - 設備報廢與資產購置",
                    ]
                )
                title = st.text_input("簽核主旨標題 *", value="西寧廠新進技術員請假單")
            with c2:
                amount = st.text_input("涉及金額 / 數量 (若無填 -)", value="-")
                applicant = st.text_input("申請人姓名與職稱 *", value=f"{current_user} ({current_role.upper()})")

            details = st.text_area("填寫詳細事由與說明 *", value="因個人因素申請請假...")

            if st.form_submit_button("🚀 提交送出電子簽核", type="primary", use_container_width=True):
                if title and details:
                    new_id = f"APP-2026-{len(st.session_state.approval_tasks_db)+1:03d}"
                    st.session_state.approval_tasks_db.append({
                        "id": new_id,
                        "category": category,
                        "title": title,
                        "applicant": applicant,
                        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "amount": amount,
                        "details": details,
                        "status": "待審核",
                    })
                    st.success(f"🎉 簽核單 [{new_id}] 已成功提交並發送給部門主管與管理中心！")
                    st.rerun()
                else:
                    st.error("請完整填寫主旨與詳細事由！")


def show(lang="繁體中文"):
    render_approval_center(lang)


def main(lang="繁體中文"):
    render_approval_center(lang)
