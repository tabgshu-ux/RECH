import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_announcements_table(engine):
    """確保資料庫中存在公司公告表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS hr_announcements (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        category VARCHAR(50) DEFAULT '一般公告',
                        content TEXT NOT NULL,
                        publisher VARCHAR(100) DEFAULT '管理部',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def show(engine=None, lang="繁體中文", **kwargs):
    st.title("📢 管理部 - 公司公告佈告欄與佈達中心")
    st.caption("100% 透過 PostgreSQL 資料庫驅動，並嚴格遵循企業內控：僅限人事主管與管理部最高主管發布。")
    st.markdown("---")

    if engine is not None:
        init_announcements_table(engine)
    else:
        st.warning("⚠️ 目前處於離線狀態，無法讀寫資料庫。")

    # 取得當前使用者身分與部門角色
    current_role = st.session_state.get("current_user_role", "Staff")
    # 嚴格界定：總務、財務等非人事主管排除在外，僅限最高管理層與人事專職主管
    allowed_publish_roles = ["Admin", "管理部主管", "人事主管", "HR_Manager"]
    is_authorized_publisher = current_role in allowed_publish_roles

    # 1. 權限控管：僅限人事與管理部主管顯示發布表單
    if is_authorized_publisher:
        with st.form("add_announcement_form"):
            st.markdown("#### ➕ [人事/管理主管專屬] 發布新的公司公告或佈達事項")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("公告主旨 *", placeholder="例如: 關於越南廠區端午節休假與薪資發放通知")
            with col2:
                category = st.selectbox("公告類別", ["一般公告", "工安環安", "薪資福利", "作業規範", "緊急通知"])
            
            content = st.text_area("公告詳細內容 *", placeholder="請在此輸入詳細說明、配合事項或法規要求...")
            publisher = st.text_input("發布單位", value="管理部 (人事室)")

            submitted = st.form_submit_button("🚀 立即發布並寫入資料庫", type="primary")
            if submitted:
                if title.strip() and content.strip():
                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO hr_announcements (title, category, content, publisher)
                                    VALUES (:title, :category, :content, :publisher)
                                """), {
                                    "title": title.strip(),
                                    "category": category,
                                    "content": content.strip(),
                                    "publisher": publisher.strip()
                                })
                            st.success("🎉 公告已成功發布並寫入資料庫！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ 寫入資料庫失敗：{e}")
                    else:
                        st.error("⚠️ 資料庫未連線！")
                else:
                    st.warning("⚠️ 請完整填寫公告主旨與內容！")
        st.markdown("---")
    else:
        st.info("💡 根據企業內控規範，總務、財務與一般同仁僅具備公告檢視權限，無法發布公告。")

    st.markdown("#### 📋 歷史公告清單與佈達檢視")

    # 2. 從資料庫讀取公告清單
    announcements = []
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text("SELECT id, title, category, content, publisher, created_at FROM hr_announcements ORDER BY id DESC"), con=conn)
                announcements = df.to_dict(orient="records")
        except Exception:
            pass

    if not announcements:
        st.info("💡 目前尚無任何公司公告。")
    else:
        for ann in announcements:
            with st.expander(f"📌 [{ann['category']}] {ann['title']} (發布時間: {ann['created_at']})"):
                st.markdown(f"**發布單位：** {ann['publisher']}")
                st.markdown(f"**詳細內容：**\n{ann['content']}")
                
                # 刪除權限同步受嚴格控管
                if is_authorized_publisher:
                    if st.button("🗑️ [主管專用] 刪除此公告", key=f"del_ann_{ann['id']}"):
                        if engine is not None:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("DELETE FROM hr_announcements WHERE id = :id"), {"id": ann['id']})
                                st.success("已成功刪除公告！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"刪除失敗: {e}")
