# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：IT 部門專用 - 選單動態配置管理
# ==========================================

import streamlit as st

def render_admin_settings(db_conn):
    st.subheader("⚙️ IT 系統管理 - 選單與動態架構配置")
    st.info("在此新增的部門或功能，主頁將自動讀取並繪製對應卡片。")
    
    tab1, tab2 = st.tabs(["1. 新增/管理部門 (一級卡片)", "2. 新增/管理功能大項 (二級按鈕)"])
    
    with tab1:
        st.write("#### ➕ 新增一級部門")
        mod_id = st.text_input("部門代碼 (例如: qa, production)", key="mod_id_input")
        mod_name_zh = st.text_input("部門中文名稱 (例如: 品保部)", key="mod_zh_input")
        mod_name_vi = st.text_input("部門越文名稱", key="mod_vi_input")
        
        if st.button("儲存部門設定", type="primary"):
            if mod_id and mod_name_zh:
                db_conn.execute(
                    "INSERT INTO sys_modules (id, name_zh, name_vi) VALUES (%s, %s, %s)",
                    (mod_id, mod_name_zh, mod_name_vi)
                )
                st.success(f"已成功新增部門：{mod_name_zh}！")
            else:
                st.warning("請填寫完整部門代碼與中文名稱。")

    with tab2:
        st.write("#### ➕ 在部門下新增功能大項")
        modules = db_conn.query("SELECT * FROM sys_modules;")
        mod_options = {f"{m['name_zh']} ({m['id']})": m['id'] for m in modules}
        
        if mod_options:
            selected_mod_label = st.selectbox("選擇所屬部門", list(mod_options.keys()))
            selected_mod_id = mod_options[selected_mod_label]
            
            feat_id = st.text_input("功能大項代碼 (例如: feat_iqc)")
            feat_name_zh = st.text_input("功能大項中文名稱 (例如: 進料檢驗紀錄)")
            feat_name_vi = st.text_input("功能大項越文名稱")
            
            if st.button("儲存功能大項設定", type="primary"):
                if feat_id and feat_name_zh:
                    db_conn.execute(
                        "INSERT INTO sys_features (id, module_id, name_zh, name_vi) VALUES (%s, %s, %s, %s)",
                        (feat_id, selected_mod_id, feat_name_zh, feat_name_vi)
                    )
                    st.success(f"已成功於該部門新增功能：{feat_name_zh}！")
                else:
                    st.warning("請填寫完整功能代碼與中文名稱。")
        else:
            st.warning("請先新增至少一個部門。")
