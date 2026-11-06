# views/dashboard.py
# 職責：通用型動態導覽主頁 (完全無 Hard-code 部門與功能名稱)

import streamlit as st

def render_dynamic_dashboard(db_conn):
    st.title("裕豐 ERP 系統 - 業務導覽主頁")
    
    # 1. 從資料庫讀取目前所有「已啟用的部門/模組」 (依排序權重 sort_order 排序)
    # 不管後台新增了 3 個還是 10 個部門，這裡會自動拉出清單
    modules = db_conn.query(
        "SELECT id, name_zh, name_vi FROM sys_modules WHERE is_active = TRUE ORDER BY sort_order;"
    )
    
    # 2. 從資料庫讀取所有「已啟用的二級功能大項」
    features = db_conn.query(
        "SELECT id, module_id, name_zh, name_vi, route_key FROM sys_features WHERE is_active = TRUE ORDER BY sort_order;"
    )
    
    if not modules:
        st.info("目前系統尚未配置任何部門模組。")
        return

    # 3. 動態 RWD 網格渲染：依據部門數量自動切分欄位，列數隨資料量自動向拉長
    # 使用 3 欄為一列的通用算術切分
    col_count = 3
    for i in range(0, len(modules), col_count):
        cols = st.columns(col_count)
        
        # 遍歷目前這一行的部門卡片
        for j in range(col_count):
            if i + j < len(modules):
                module = modules[i + j]
                with cols[j]:
                    # 外層卡片容器：自動顯示部門名稱
                    with st.container(border=True):
                        st.subheader(module['name_zh'])
                        
                        # 自動篩選歸屬於該部門的所有二級功能
                        sub_features = [f for f in features if f['module_id'] == module['id']]
                        
                        if sub_features:
                            # 自動生成該部門下的所有功能按鈕 (長度自動向拉長)
                            for feat in sub_features:
                                if st.button(
                                    feat['name_zh'], 
                                    key=f"btn_{module['id']}_{feat['id']}", 
                                    use_container_width=True
                                ):
                                    # 記錄選擇的功能與對應路由，動態載入對應模組
                                    st.session_state['active_feature_id'] = feat['id']
                                    st.session_state['active_route'] = feat['route_key']
                                    st.rerun()
                        else:
                            st.caption("尚無配置功能")
