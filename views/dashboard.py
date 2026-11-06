# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：主頁卡片/九宮格導覽 (動態讀庫、延伸卡片長度)
# ==========================================

import streamlit as st

def render_dashboard(db_conn):
    st.subheader("📌 系統業務導覽主頁")
    
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    if not modules:
        st.info("目前系統尚未設定任何部門模組。")
        return

    col_count = 3
    for i in range(0, len(modules), col_count):
        cols = st.columns(col_count)
        for j in range(col_count):
            if i + j < len(modules):
                mod = modules[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(mod['name_zh'])
                        st.caption(mod['name_vi'])
                        st.divider()
                        
                        sub_features = [f for f in features if f['module_id'] == mod['id']]
                        
                        if sub_features:
                            for feat in sub_features:
                                if st.button(feat['name_zh'], key=f"btn_{mod['id']}_{feat['id']}", use_container_width=True):
                                    st.session_state['active_feature_id'] = feat['id']
                                    st.session_state['current_view'] = 'dynamic_feature'
                                    st.rerun()
                        else:
                            st.caption("尚無配置功能項目")
