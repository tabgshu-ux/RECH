# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：主選單與部門儀表板畫面渲染（精簡版：僅顯示戰情與三大二級部門入口）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine):
    # 取得當前選擇的部門資訊（預設為管理部）
    if 'selected_dept_id' not in st.session_state:
        st.session_state['selected_dept_id'] = 'mgmt'

    current_dept_id = st.session_state['selected_dept_id']

    departments = [
        {"id": "ceo", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": None},
        {"id": "eng", "name_zh": "工程部", "name_vi": "Phòng Kỹ thuật", "level": "L1", "parent": None},
        {"id": "mgmt", "name_zh": "管理部", "name_vi": "Phòng Hành chính Quản trị", "level": "L1", "parent": None},
        {"id": "prod", "name_zh": "生產部", "name_vi": "Phòng Sản xuất", "level": "L1", "parent": None},
    ]

    current_target = next((d for d in departments if d['id'] == current_dept_id), departments[2])

    # 側邊欄導覽
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    st.sidebar.markdown("---")

    for dept in departments:
        is_selected = (dept['id'] == current_dept_id)
        btn_type = "primary" if is_selected else "secondary"
        
        if st.sidebar.button(f"{dept['name_zh']} ({dept['name_vi']})", key=f"btn_dept_{dept['id']}", use_container_width=True, type=btn_type):
            st.session_state['selected_dept_id'] = dept['id']
            st.session_state['current_view'] = 'dashboard'
            st.session_state['active_feature_id'] = None
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # 主畫面區域
    if current_target['id'] == 'mgmt':
        # 1. 管理部主管綜合戰情儀表板
        try:
            from modules.management.supervisor_dashboard import render as render_supervisor
            render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.warning(f"戰情資料載入提示: {e}")
        st.markdown("---")

        # 2. 精簡的三大二級部門入口功能列
        st.markdown("### 📌 管理部二級部門導覽入口")
        
        cols = st.columns(3)
        l2_sections = [
            {"id": "feat_hr", "name": "📂 人事 / 行政", "desc": "管理越籍員工、外派幹部證件、考勤與薪資保險。"},
            {"id": "feat_ga", "name": "📂 總務 / 採購", "desc": "廠區採購、供應商主檔、宿舍與車輛維修管理。"},
            {"id": "feat_fi", "name": "📂 財務 / 會計", "desc": "應收帳款 (AR) 與越南稅務標準財報 (Thông tư 200)。"},
        ]
        
        for idx, sec in enumerate(l2_sections):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"#### {sec['name']}")
                    st.caption(sec['desc'])
                    if st.button("進入該部門專區 ➡️", key=f"btn_sec_{sec['id']}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = sec['id']
                        st.rerun()
    else:
        st.info(f"💡 [{current_target['name_zh']}] 相關業務模組建置中...")
