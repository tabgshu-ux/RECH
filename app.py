# ==========================================
# 檔案路徑：app.py
# 職責：系統主入口（多語系 + 手機優先 + 動態元數據路由 + 切頁自動置頂）
# ==========================================

import os
import streamlit as st
from sqlalchemy import create_engine
from core import dynamic_router, ui_theme
from modules.it_system.admin_settings import render_admin_settings
from views.login import render_login_page
from views.dashboard import render_dashboard
from modules.management.announcements import render_global_announcement_banner

st.set_page_config(
    page_title="裕豐電機工業 SaaS ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui_theme.apply_mobile_first()

DEFAULTS = {
    "logged_in": False,
    "user_name": "",
    "user_role": "",
    "current_view": "dashboard",
    "active_feature_id": None,
    "current_lang": "zh",
    "tenant_id": "REETECH_VN",
    "selected_node_code": None,
    "role_landing_applied": False,
    "tenant_company_name": "裕豐電機工業有限公司",
    "_last_route_sig": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


@st.cache_resource
def get_db_engine():
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if not db_url:
        return None
    clean_url = db_url.strip()
    if "pooler.supabase.com" in clean_url and "?" not in clean_url:
        clean_url += "?sslmode=require"
    try:
        return create_engine(clean_url, pool_pre_ping=True, connect_args={"prepare_threshold": None})
    except Exception:
        return None


db_engine = get_db_engine()
lang = ui_theme.norm_lang(st.session_state.get("current_lang", "zh"))

if not st.session_state["logged_in"]:
    render_login_page(db_engine)
    st.stop()

tenant_id = st.session_state["tenant_id"]

if db_engine and not st.session_state["role_landing_applied"]:
    landing = dynamic_router.get_role_landing(db_engine, tenant_id, st.session_state.get("user_role", ""))
    st.session_state["role_landing_applied"] = True
    if landing:
        st.session_state["selected_node_code"] = landing["node_code"]
        feats = [x.strip() for x in str(landing.get("mounted_features") or "").split(",") if x.strip()]
        if feats:
            st.session_state["current_view"] = "dynamic_feature"
            st.session_state["active_feature_id"] = feats[0]

# 切換部門或功能時自動捲動到最上方
route_sig = f"{st.session_state['current_view']}|{st.session_state.get('selected_node_code')}|{st.session_state.get('active_feature_id')}"
if st.session_state["_last_route_sig"] != route_sig:
    st.session_state["_last_route_sig"] = route_sig
    ui_theme.scroll_to_top()

with st.sidebar:
    ui_theme.render_lang_selector("sidebar_lang")
    st.divider()
    st.markdown(f"### {ui_theme.tr('org_nav', lang)}")
    l1_nodes = dynamic_router.get_l1_nodes(db_engine, tenant_id) if db_engine else []

    for node in l1_nodes:
        icon = "🧭" if node.get("node_type") == "L1_FUNC" else "🏛️"
        is_sel = (
            st.session_state["current_view"] == "dashboard"
            and st.session_state.get("selected_node_code") == node["node_code"]
        )
        if st.button(
            f"{icon} {node['node_name']}",
            key=f"sb_{node['node_code']}",
            use_container_width=True,
            type="primary" if is_sel else "secondary",
        ):
            st.session_state["selected_node_code"] = node["node_code"]
            st.session_state["current_view"] = "dashboard"
            st.session_state["active_feature_id"] = None
            st.rerun()

    st.divider()
    is_sys = (
        st.session_state["current_view"] == "dynamic_feature"
        and st.session_state.get("active_feature_id") == "feat_it_menu"
    )
    if st.button(
        ui_theme.tr("sys_settings", lang),
        use_container_width=True,
        type="primary" if is_sys else "secondary",
    ):
        st.session_state["current_view"] = "dynamic_feature"
        st.session_state["active_feature_id"] = "feat_it_menu"
        st.rerun()

c_title, c_user, c_back, c_out = st.columns([4.5, 2, 2.2, 1.3])
with c_title:
    st.markdown(f"#### 🏭 {st.session_state['tenant_company_name']}")
with c_user:
    st.caption(f"👤 {st.session_state['user_name']}")
with c_back:
    if st.session_state["current_view"] != "dashboard":
        if st.button(ui_theme.tr("back_home", lang), use_container_width=True):
            st.session_state["current_view"] = "dashboard"
            st.session_state["active_feature_id"] = None
            st.rerun()
with c_out:
    if st.button(ui_theme.tr("logout", lang), use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["role_landing_applied"] = False
        st.session_state["current_view"] = "dashboard"
        st.rerun()

st.divider()
render_global_announcement_banner(engine=db_engine, tenant_id=tenant_id)

if st.session_state["current_view"] == "dashboard":
    render_dashboard(db_engine)
elif st.session_state["current_view"] == "dynamic_feature":
    fid = str(st.session_state.get("active_feature_id") or "")
    if fid == "feat_it_menu":
        render_admin_settings(db_engine, lang=lang)
    else:
        dynamic_router.dispatch_feature(db_engine, fid, lang=lang)
