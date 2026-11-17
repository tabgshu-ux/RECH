# ==========================================
# 檔案路徑：modules/management/general_affairs/__init__.py
# 職責：總務採購與後勤支援總分頁路由分發中心
# ==========================================

import streamlit as st
import importlib

def render(db_engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 總務採購與後勤支援中心 (General Affairs & Logistics Hub)")
    st.caption("集中管理台幹證件與生活後勤、廠區 EHS 消防環保、越籍員工食堂團膳、MRO 採購及政府公關。")

    if 'ga_sub_tab' not in st.session_state:
        st.session_state['ga_sub_tab'] = 'expat'

    cols = st.columns(4)
    with cols[0]:
        if st.button("🛂 台幹證件與生活後勤", use_container_width=True, type="primary" if st.session_state['ga_sub_tab'] == 'expat' else "secondary"):
            st.session_state['ga_sub_tab'] = 'expat'
            st.rerun()
    with cols[1]:
        if st.button("🧯 廠務設施與 EHS 環安衛", use_container_width=True, type="primary" if st.session_state['ga_sub_tab'] == 'ehs' else "secondary"):
            st.session_state['ga_sub_tab'] = 'ehs'
            st.rerun()
    with cols[2]:
        if st.button("🍲 食堂團膳與保全門禁", use_container_width=True, type="primary" if st.session_state['ga_sub_tab'] == 'canteen' else "secondary"):
            st.session_state['ga_sub_tab'] = 'canteen'
            st.rerun()
    with cols[3]:
        if st.button("🏛️ MRO 採購與政府公關", use_container_width=True, type="primary" if st.session_state['ga_sub_tab'] == 'mro' else "secondary"):
            st.session_state['ga_sub_tab'] = 'mro'
            st.rerun()

    st.markdown("---")

    current_tab = st.session_state['ga_sub_tab']

    if current_tab == 'expat':
        try:
            from modules.management.general_affairs import expat_support
            expat_support.render(db_engine, lang=lang)
        except Exception as e:
            st.error(f"載入台幹後勤模組失敗: {e}")
    elif current_tab == 'ehs':
        try:
            from modules.management.general_affairs import ehs_maintenance
            ehs_maintenance.render(db_engine, lang=lang)
        except Exception as e:
            st.error(f"載入 EHS 模組失敗: {e}")
    elif current_tab == 'canteen':
        try:
            from modules.management.general_affairs import canteen_security
            canteen_security.render(db_engine, lang=lang)
        except Exception as e:
            st.error(f"載入食堂保全模組失敗: {e}")
    elif current_tab == 'mro':
        try:
            from modules.management.general_affairs import mro_assets_pr
            mro_assets_pr.render(db_engine, lang=lang)
        except Exception as e:
            st.error(f"載入 MRO 公關模組失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(db_engine=engine, lang=lang, **kwargs)
