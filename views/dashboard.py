# views/dashboard.py
# 職責：主頁卡片導覽 (從資料庫讀取 sys_modules 與 sys_features 動態渲染)

import streamlit as st

def render_dashboard_page(db_conn):
    st.title("裕豐 ERP 系統 - 主選單")
    
    # 1. 從資料庫撈取主選單資料 (Metadata)
    modules = db_conn.query("SELECT * FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;")
    features = db_conn.query("SELECT * FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;")
    
    # 2. 畫出卡片選單 (如：人事/行政、總務/採購、財務/會計)
    cols = st.columns(len(modules))
    for idx, module in enumerate(modules):
        with cols[idx]:
            st.subheader(module['name_zh']) # 顯示大分類名稱
            
            # 過濾該分類下的二級大項按鈕
            sub_items = [f for f in features if f['module_id'] == module['id']]
            for item in sub_items:
                # 點擊按鈕後記錄選擇的功能 ID 並跳轉
                if st.button(item['name_zh'], key=f"btn_{item['id']}", use_container_width=True):
                    st.session_state['selected_feature_id'] = item['id']
                    st.session_state['current_view'] = item['route_key']
                    st.rerun()
