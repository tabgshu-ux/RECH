# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：主選單與部門儀表板畫面渲染（完整卡片版）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine):
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

        # 2. 完整二級部門與業務模組卡片區塊
        st.markdown("### 📌 隸屬二級部門與業務模組")
        
        # 人事行政課模組群
        st.markdown("#### 📂 [L2] 人事 / 行政")
        cols1 = st.columns(3)
        hr_features = [
            {"id": "feat_hr", "name": "人事行政 — 員工檔案與履約管理", "desc": "越籍員工、外派幹部證件、合約管理與 90 天到期預警。"},
            {"id": "feat_attendance", "name": "人事行政 — 考勤與打卡紀錄", "desc": "日常上下班打卡、請假與出勤異常審核。"},
            {"id": "feat_payroll", "name": "人事行政 — 薪資計算與 BHXH 保險", "desc": "越南當地薪資結構、社會保險扣繳與合規報表。"},
        ]
        for idx, feat in enumerate(hr_features):
            with cols1[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📌 {feat['name']}")
                    st.caption(feat['desc'])
                    if st.button("進入功能 ➡️", key=f"btn_feat_{feat['id']}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = feat['id']
                        st.rerun()

        st.markdown("---")
        
        # 總務採購課模組群
        st.markdown("#### 📂 [L2] 總務 / 採購")
        cols2 = st.columns(3)
        ga_features = [
            {"id": "feat_ga", "name": "總務採購 — 採購單與應付帳款 (AP)", "desc": "廠區採購、供應商主檔與請款合規紀錄。"},
        ]
        for idx, feat in enumerate(ga_features):
            with cols2[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📌 {feat['name']}")
                    st.caption(feat['desc'])
                    if st.button("進入功能 ➡️", key=f"btn_feat_{feat['id']}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = feat['id']
                        st.rerun()
    else:
        st.info(f"💡 [{current_target['name_zh']}] 相關業務模組建置中...")
