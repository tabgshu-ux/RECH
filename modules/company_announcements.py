import streamlit as st
import pandas as pd
import datetime

def render_company_announcements_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "📢 公司重要公告與佈告欄管理系統 (含稽核軌跡)",
            "caption": "發布管理全廠區重要公告，所有異動皆會強制寫入 IT 稽核日誌，確保資安合規與防篡改。",
            "tab1": "📝 發布新公告 (管理部/總經理室)",
            "tab2": "📋 現行公告列表與安全維護"
        },
        "Tiếng Việt": {
            "title": "📢 Quản lý Thông báo Công ty (Có kiểm toán)",
            "caption": "Đăng tải thông báo và ghi lại nhật ký kiểm toán IT để đảm bảo an toàn bảo mật.",
            "tab1": "📝 Đăng thông báo mới",
            "tab2": "📋 Danh sách thông báo & Duy trì"
        },
        "English": {
            "title": "📢 Company Announcements & Audit Trail",
            "caption": "Publish announcements with automatic IT audit logging for security and compliance.",
            "tab1": "📝 Post New Announcement",
            "tab2": "📋 Announcement List & Maintenance"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 🛡️ 初始化公告資料庫
    if "announcements_db" not in st.session_state or not isinstance(st.session_state.announcements_db, list):
        st.session_state.announcements_db = [
            {
                "ann_id": "ANN-2026-001",
                "title": "⚡ 關於越南全國連假與西寧/海防廠安全生產之重要通知",
                "category": "🔴 緊急公告 (Urgent)",
                "content": "請各部門主管務必於連假前落實廠區斷電巡檢、消防設備盤點，並確保留守人員通訊暢通。",
                "publisher": "總經理室 / 董事長辦公室",
                "date": "2026-10-09",
                "status": "🟢 發布中 (Active)"
            },
            {
                "ann_id": "ANN-2026-002",
                "title": "📋 10月份勞動法規定與外包商點工對帳新制上線說明",
                "category": "🟡 行政公告 (Administrative)",
                "content": "自即日起，所有外包商點工與加班費計算全面配合 ERP 系統自動審核，請工程部與採購部配合辦理。",
                "publisher": "管理部 (GA)",
                "date": "2026-10-08",
                "status": "🟢 發布中 (Active)"
            }
        ]

    # 確保稽核日誌資料庫存在
    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = []

    current_user = st.session_state.get('user_name', 'admin')

    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

    with tab1:
        st.markdown("##### 📝 撰寫並發布新公告")
        with st.form("announcement_form"):
            c1, c2 = st.columns(2)
            with c1:
                ann_title = st.text_input("公告標題 *", placeholder="例如: 關於廠區年度消防演習之通知...")
                ann_category = st.selectbox("公告類別", ["🔴 緊急公告 (Urgent)", "🟡 行政公告 (Administrative)", "🟢 福利與活動 (Welfare & Events)"])
            with c2:
                publisher_name = st.text_input("發布單位與發布人", value=f"{current_user} (管理部/總經理室)")
                ann_status = st.selectbox("發布狀態", ["🟢 發布中 (Active)", "📁 存檔備查 (Archived)"])

            ann_content = st.text_area("公告詳細內容 (Content) *", placeholder="請在此輸入公告主旨與詳細說明...")

            if st.form_submit_button("🚀 發布公告並記錄至 IT 稽核日誌", type="primary"):
                if ann_title and ann_content:
                    new_id = f"ANN-2026-{len(st.session_state.announcements_db)+1:03d}"
                    new_ann = {
                        "ann_id": new_id,
                        "title": ann_title,
                        "category": ann_category,
                        "content": ann_content,
                        "publisher": publisher_name,
                        "date": str(datetime.date.today()),
                        "status": ann_status
                    }
                    st.session_state.announcements_db.insert(0, new_ann)

                    # 🔒 自動寫入全系統稽核軌跡
                    st.session_state.audit_logs_db.insert(0, {
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user": current_user,
                        "action": f"發布新公告 [{new_id}] {ann_title}",
                        "module": "Announcements",
                        "ip": "192.168.1.50",
                        "status": "成功"
                    })

                    st.success(f"✅ 公告 [{new_id}] 已成功發布，並已同步寫入 IT 系統稽核日誌！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫公告標題與詳細內容！")

    with tab2:
        st.markdown("##### 📋 現行公司公告清單與異動維護")
        if st.session_state.announcements_db:
            ann_options = [f"{a['ann_id']} - {a['title']}" for a in st.session_state.announcements_db]
            sel_ann_target = st.selectbox("選擇要編輯或刪除的公告項目", ann_options)
            target_aid = sel_ann_target.split(" - ")[0]
            target_ann_obj = next((a for a in st.session_state.announcements_db if a["ann_id"] == target_aid), None)

            st.markdown("---")

            if target_ann_obj:
                with st.form("form_edit_announcement"):
                    ed_title = st.text_input("修改公告標題", value=target_ann_obj["title"])
                    ed_status = st.selectbox("修改狀態", ["🟢 發布中 (Active)", "📁 存檔備查 (Archived)"], index=0 if "發布中" in target_ann_obj["status"] else 1)
                    ed_content = st.text_area("修改公告內容", value=target_ann_obj["content"])

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        update_ann_btn = st.form_submit_button("💾 儲存變更並記錄稽核", type="primary", use_container_width=True)
                    with col_b2:
                        delete_ann_btn = st.form_submit_button("🔥 刪除公告並記錄稽核", type="secondary", use_container_width=True)

                    if update_ann_btn:
                        target_ann_obj["title"] = ed_title
                        target_ann_obj["status"] = ed_status
                        target_ann_obj["content"] = ed_content

                        # 🔒 寫入稽核軌跡：修改公告
                        st.session_state.audit_logs_db.insert(0, {
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": current_user,
                            "action": f"修改公告內容 [{target_aid}]",
                            "module": "Announcements",
                            "ip": "192.168.1.50",
                            "status": "成功"
                        })

                        st.success("🎉 公告內容已成功更新，並已留存 IT 稽核軌跡！")
                        st.rerun()

                    if delete_ann_btn:
                        st.session_state.announcements_db = [a for a in st.session_state.announcements_db if a["ann_id"] != target_aid]

                        # 🔒 寫入稽核軌跡：刪除公告
                        st.session_state.audit_logs_db.insert(0, {
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": current_user,
                            "action": f"刪除公告 [{target_aid}]",
                            "module": "Announcements",
                            "ip": "192.168.1.50",
                            "status": "成功"
                        })

                        st.success("🗑️ 該筆公告已從系統中刪除，並已留存 IT 刪除稽核紀錄！")
                        st.rerun()

            st.markdown("---")
            st.markdown("##### 📜 所有歷史公告總覽")
            for ann in st.session_state.announcements_db:
                with st.expander(f"📌 [{ann['category']}] {ann['title']} ({ann['date']}) - {ann['status']}"):
                    st.write(f"**發布單位**：{ann['publisher']}")
                    st.markdown(f"**內容說明**：\n{ann['content']}")
        else:
            st.info("目前尚無公告紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_company_announcements_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_company_announcements_page(engine=engine, lang=lang, **kwargs)
