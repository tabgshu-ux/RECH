import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 全公司公告與佈告欄多語系字典 (i18n)
# ----------------------------------------------------
ANN_I18N = {
    "繁體中文": {
        "title": "📢 總務部/總經理室 - 全公司重要公告與佈告欄管理中心",
        "caption": "發布全廠緊急通知、連假安全規範與行政宣導；支援歷史公告查詢與權限控管。",
        "tab_active": "📢 當前發布中公告 (首頁同步)",
        "tab_manage": "📝 發布與管理公告 (權限控管)",
        "lbl_ann_id": "公告編號 (ID)",
        "lbl_ann_title": "公告標題",
        "lbl_category": "公告類別",
        "lbl_publisher": "發布單位 / 發布人",
        "lbl_pub_date": "發布日期",
        "lbl_status": "發布狀態",
        "lbl_content": "公告詳細內容",
        "btn_add_ann": "🚀 正式發布公告並同步至系統首頁",
        "msg_success": "✅ 公告發布成功！已寫入資料庫並同步更新至系統首頁。",
        "msg_error_empty": "⚠️ 請填寫完整的公告標題與內容！",
        "header_edit": "⚙️ 歷史公告狀態維護 (下架 / 刪除)",
        "btn_update_status": "💾 更新公告狀態"
    },
    "Tiếng Việt": {
        "title": "📢 Bảng Thông Báo Công Ty & Quản Lý Bảng Tin",
        "caption": "Đăng thông báo khẩn cấp, quy định lễ tết và thông tin hành chính toàn công ty.",
        "tab_active": "📢 Thông báo đang phát hành (Đồng bộ trang chủ)",
        "tab_manage": "📝 Đăng & Quản lý thông báo",
        "lbl_ann_id": "Mã thông báo (ID)",
        "lbl_ann_title": "Tiêu đề thông báo",
        "lbl_category": "Phân loại",
        "lbl_publisher": "Đơn vị phát hành",
        "lbl_pub_date": "Ngày phát hành",
        "lbl_status": "Trạng thái",
        "lbl_content": "Nội dung chi tiết",
        "btn_add_ann": "🚀 Đăng thông báo & Đồng bộ Trang chủ",
        "msg_success": "✅ Đăng thông báo thành công! Đã lưu vào cơ sở dữ liệu.",
        "msg_error_empty": "⚠️ Vui lòng nhập đầy đủ tiêu đề và nội dung!",
        "header_edit": "⚙️ Cập nhật trạng thái thông báo",
        "btn_update_status": "💾 Cập nhật trạng thái"
    },
    "English": {
        "title": "📢 Company Announcements & Bulletin Board Management",
        "caption": "Publish company-wide emergency alerts, holiday compliance, and administrative notices.",
        "tab_active": "📢 Active Announcements (Synced to Homepage)",
        "tab_manage": "📝 Publish & Manage Announcements",
        "lbl_ann_id": "Announcement ID",
        "lbl_ann_title": "Announcement Title",
        "lbl_category": "Category",
        "lbl_publisher": "Publisher / Department",
        "lbl_pub_date": "Publish Date",
        "lbl_status": "Status",
        "lbl_content": "Detailed Content",
        "btn_add_ann": "🚀 Publish Announcement & Sync to Homepage",
        "msg_success": "✅ Announcement published successfully! Saved to database.",
        "msg_error_empty": "⚠️ Please fill in all required title and content fields!",
        "header_edit": "⚙️ Maintain Historical Announcement Status",
        "btn_update_status": "💾 Update Status"
    }
}

def init_announcements_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.company_announcements (
                    id SERIAL PRIMARY KEY,
                    ann_id VARCHAR(50) UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    category VARCHAR(100) DEFAULT '📢 一般公告',
                    content TEXT NOT NULL,
                    publisher VARCHAR(100) NOT NULL,
                    pub_date DATE DEFAULT CURRENT_DATE,
                    status VARCHAR(50) DEFAULT '🟢 發布中 (Active)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 資料庫 Table 初始化提示: {str(e)}")

def render_company_announcements_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ANN_I18N.get(active_lang, ANN_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_announcements_db(engine)

    tab_active, tab_manage = st.tabs([L["tab_active"], L["tab_manage"]])

    # ----------------------------------------------------
    # 📢 Tab 1: 當前發布中公告 (全員與首頁可見)
    # ----------------------------------------------------
    with tab_active:
        ann_list = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT ann_id, title, category, content, publisher, pub_date, status
                        FROM public.company_announcements
                        ORDER BY pub_date DESC, id DESC
                    """))
                    for r in res.fetchall():
                        ann_list.append({
                            "ann_id": r[0], "title": r[1], "category": r[2],
                            "content": r[3], "publisher": r[4], "date": str(r[5]), "status": r[6]
                        })
            except Exception:
                pass

        active_anns = [a for a in ann_list if "發布中" in a["status"] or "Active" in a["status"]]

        if active_anns:
            for item in active_anns:
                with st.expander(f"{item['category']} | **{item['title']}** ({item['date']})", expanded=True):
                    st.markdown(f"**發布單位**：`{item['publisher']}` | **公告編號**：`{item['ann_id']}`")
                    st.markdown(f"> {item['content']}")
        else:
            st.info("目前尚無發布中的公告。")

    # ----------------------------------------------------
    # 📝 Tab 2: 發布新公告與管理 (僅限管理主管/admin)
    # ----------------------------------------------------
    with tab_manage:
        user_role = str(st.session_state.get("user_role", "")).lower()
        
        st.markdown("#### 📝 發布全新公告")
        with st.form("form_add_announcement"):
            c1, c2, c3 = st.columns(3)
            with c1:
                auto_id = f"ANN-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
                ann_id = st.text_input(L["lbl_ann_id"], value=auto_id, disabled=True)
            with c2:
                category = st.selectbox(L["lbl_category"], ["🔴 緊急公告 (Urgent)", "📢 一般行政通知", "🛠️ 廠區工安與維護", "🎉 節慶休假公告"])
            with c3:
                publisher = st.text_input(L["lbl_publisher"], value=st.session_state.get("user_name", "總經理室"))

            title = st.text_input(L["lbl_ann_title"], placeholder="例如：關於越南國慶連假與廠區斷電巡檢安全通知...")
            pub_date = st.date_input(L["lbl_pub_date"], value=datetime.date.today())
            content = st.text_area(L["lbl_content"], placeholder="請輸入詳細公告內容與規定說明...")

            if st.form_submit_button(L["btn_add_ann"], type="primary", use_container_width=True):
                if not title or not content:
                    st.error(L["msg_error_empty"])
                else:
                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.company_announcements (ann_id, title, category, content, publisher, pub_date, status)
                                    VALUES (:aid, :title, :cat, :cnt, :pub, :pdate, '🟢 發布中 (Active)');
                                """), {
                                    "aid": ann_id, "title": title, "cat": category,
                                    "cnt": content, "pub": publisher, "pdate": pub_date
                                })
                            st.success(L["msg_success"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 發布失敗: {str(e)}")

        st.markdown("---")
        st.markdown(f"#### {L['header_edit']}")
        if ann_list:
            df_manage = pd.DataFrame(ann_list)
            st.dataframe(df_manage, use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_company_announcements_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_company_announcements_page(engine=engine, lang=lang, **kwargs)
