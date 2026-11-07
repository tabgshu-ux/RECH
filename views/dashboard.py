# 若是管理部 L1，渲染戰情儀表板與二級部門業務模組卡片
    if current_target['id'] == 'mgmt':
        # 1. 管理部主管綜合戰情儀表板
        try:
            from modules.management.supervisor_dashboard import render as render_supervisor
            render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.warning(f"戰情資料載入提示: {e}")
        st.markdown("---")

        # 2. 二級部門與業務模組卡片區塊
        st.markdown("### 📌 隸屬二級部門與業務模組")
        
        # 人事行政課模組
        st.markdown("#### 📂 [L2] 人事 / 行政")
        cols1 = st.columns(3)
        hr_features = [
            {"id": "feat_hr", "name": "人事行政 — 員工檔案與履約管理", "desc": "管理越籍員工、外派幹部證件與 90 天到期預警。"},
            {"id": "feat_attendance", "name": "人事行政 — 考勤與打卡紀錄", "desc": "日常上下班打卡、請假與出勤異常審核。"},
            {"id": "feat_payroll", "name": "人事行政 — 薪資計算與 BHXH 保險", "desc": "越南當地薪資結構、社會保險扣繳與報表。"},
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
        
        # 總務採購課模組
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
