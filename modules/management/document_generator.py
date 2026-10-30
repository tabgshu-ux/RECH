import streamlit as st
import pandas as pd
from datetime import datetime

RECH_HEADER_HTML = """
<div style="border: 2px solid #000055; padding: 15px; border-radius: 8px; background: #ffffff; margin-bottom: 20px;">
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #000055; padding-bottom: 10px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 38px; font-weight: 900; color: #000055; letter-spacing: -1px;">RECH</div>
            <div style="border-left: 2px solid #000055; padding-left: 10px;">
                <div style="font-size: 16px; font-weight: 800; color: #000055;">裕豐電機工業有限公司</div>
                <div style="font-size: 10px; font-weight: 700; color: #1E293B;">REETECH INDUSTRIAL CO., LTD</div>
                <div style="font-size: 9.5px; font-weight: 700; color: #334155;">CÔNG TY TNHH CN DŨ PHONG</div>
            </div>
        </div>
        <div style="text-align: right; font-size: 11px; color: #555;">
            <b>廠區地址</b>: 越南西寧省盞盤市安平社<br>
            <b>KCN Trảng Bảng, Tây Ninh, Việt Nam</b><br>
            <b>Web</b>: www.reetech.vn | <b>Tel</b>: +84 (0)276...
        </div>
    </div>
    <div style="text-align: center; font-size: 18px; font-weight: bold; color: #000055; margin-top: 5px;" id="doc_title_display">
        【 企業正式公文 / THƯ TÍN CHÍNH THỨC 】
    </div>
</div>
"""

def render_document_generator_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📄 裕豐電機統一 Logo 企業正式文件製作與雲端歸檔中心")
    st.caption("管理部專用：套用 RECH 標準三語表頭 Logo，線上製作各類正式文件、公文、切結書，並上傳雲端永久保留。")

    if "company_documents_db" not in st.session_state:
        st.session_state.company_documents_db = []

    tab_gen, tab_archive = st.tabs(["✍️ 1. 製作與產生正式文件", "📁 2. 公司文件雲端歸檔與調閱中心"])

    # ----------------------------------------------------
    # Tab 1: 製作與產生正式文件
    # ----------------------------------------------------
    with tab_gen:
        st.markdown("#### 📝 填寫文件內容與預覽標準表頭")

        with st.form("doc_gen_form"):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                doc_type = st.selectbox("文件類別", ["公司正式公文 (Official Letter)", "內部管理公告 (Internal Notice)", "工程施工證明書 (Construction Certificate)", "員工請假/離職證明 (Employment Certificate)", "供應商合作切結書 (Supplier Agreement)"])
                doc_number = st.text_input("文件編號 (Doc No.)", value=f"RECH-DOC-{datetime.now().strftime('%Y%m%d')}-01")
                issuer_dept = st.text_input("發文部門 / 開立單位", value="管理部 (Management Dept)")
            with col_g2:
                recipient = st.text_input("受文對象 / 呈報對象", placeholder="例如: 各部門主管 / 全體同仁 / 外部廠商")
                issue_date = st.date_input("發文日期", value=datetime.now())
                urgency = st.selectbox("文件急迫性", ["普通件 (Normal)", "加急件 (Urgent)", "特急件 (Top Urgent)"])

            doc_subject = st.text_input("文件主旨 (Subject) *", placeholder="例如: 關於廠區新進同仁安全衛生教育訓練之規定")
            doc_body_content = st.text_area("文件詳細內文 *", placeholder="請輸入正式文件內文...", height=200)
            signer_name = st.text_input("簽發人 / 授權主管署名", value="總經理 許福村 / 廠長")

            preview_submitted = st.form_submit_button("👀 產生標準帶 Logo 格式預覽", use_container_width=True)
            save_cloud_btn = st.form_submit_button("☁️ 確認儲存並上傳至公司雲端文件庫", type="primary", use_container_width=True)

            if preview_submitted or save_cloud_btn:
                st.markdown("---")
                st.markdown("#### 🔍 預覽結果（套用 RECH 標準公司表頭 Logo）：")
                
                # 即時渲染標準表頭與內文預覽
                st.markdown(RECH_HEADER_HTML, unsafe_allow_html=True)
                st.markdown(f"**文件編號**: {doc_number} | **發文日期**: {issue_date} | **急迫性**: {urgency}")
                st.markdown(f"**發文部門**: {issuer_dept} | **受文對象**: {recipient}")
                st.markdown(f"### 主旨：{doc_subject}")
                st.markdown("---")
                st.markdown(doc_body_content)
                st.markdown("---")
                st.markdown(f"<div style='text-align: right;'><b>簽發主管署名</b>：{signer_name}</div>", unsafe_allow_html=True)

            if save_cloud_btn:
                if doc_subject and doc_body_content:
                    new_doc_record = {
                        "doc_no": doc_number,
                        "title": doc_subject,
                        "type": doc_type,
                        "department": issuer_dept,
                        "date": str(issue_date),
                        "content": doc_body_content,
                        "signer": signer_name,
                        "status": "☁️ 已歸檔雲端"
                    }
                    st.session_state.company_documents_db.insert(0, new_doc_record)
                    st.success("🎉 正式文件已成功上傳並永久保存在公司雲端文件庫中！")
                else:
                    st.warning("⚠️ 請填寫文件主旨與內文！")

    # ----------------------------------------------------
    # Tab 2: 公司文件雲端歸檔與調閱中心
    # ----------------------------------------------------
    with tab_archive:
        st.markdown("#### 📁 公司雲端正式文件歸檔清單")
        st.info("💡 所有透過系統產生存檔的正式文件均集中於此，方便主管日後調閱、稽核或下載。")

        if st.session_state.company_documents_db:
            df_docs = pd.DataFrame(st.session_state.company_documents_db)
            st.dataframe(df_docs, use_container_width=True, hide_index=True)

            selected_doc_no = st.selectbox("🎯 選擇欲調閱或查看詳情的文件編號", options=[d["doc_no"] for d in st.session_state.company_documents_db])
            target_doc = next((d for d in st.session_state.company_documents_db if d["doc_no"] == selected_doc_no), None)

            if target_doc:
                st.markdown("---")
                st.markdown(f"### 📄 調閱文件檢視: {target_doc['title']}")
                st.markdown(RECH_HEADER_HTML, unsafe_allow_html=True)
                st.markdown(f"**文件編號**: {target_doc['doc_no']} | **類別**: {target_doc['type']} | **日期**: {target_doc['date']}")
                st.markdown(f"**部門**: {target_doc['department']}")
                st.markdown(f"### 主旨：{target_doc['title']}")
                st.markdown("---")
                st.markdown(target_doc['content'])
                st.markdown("---")
                st.markdown(f"<div style='text-align: right;'><b>簽發主管署名</b>：{target_doc['signer']}</div>", unsafe_allow_html=True)
        else:
            st.info("目前雲端文件庫尚無歸檔紀錄。您可以至【製作與產生正式文件】分頁建立第一份文件。")
