# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：依元數據渲染子卡片與已掛載拼圖；總經理室與各 L1 部門首頁皆直接顯示總覽（不顯示 L1/L2 前綴）
# ==========================================

import streamlit as st
from core import dynamic_router, ui_theme
from modules.common.l1_dept_overviews import render_l1_department_overview
from modules.executive.widgets.overview_panels import render_executive_home_panels
from modules.it_system.org_puzzle import repo


def render_dashboard(engine=None, lang=None, **kwargs):
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    curr_lang = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    active_code = st.session_state.get("selected_node_code")

    all_nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=False) if engine else []
    node_map = {n["node_code"]: n for n in all_nodes}

    if not active_code or active_code not in node_map:
        l1_nodes = [n for n in all_nodes if str(n.get("level_tier")).upper() == "L1"]
        active_code = l1_nodes[0]["node_code"] if l1_nodes else "DEPT_EXEC"
        st.session_state["selected_node_code"] = active_code

    curr_node = node_map.get(
        active_code,
        {
            "node_code": active_code or "DEPT_EXEC",
            "node_name": "總經理室",
            "level_tier": "L1",
            "parent_node_code": None,
            "node_type": "DEPT",
        },
    )

    trail = []
    cur = curr_node
    seen = set()
    while cur and cur["node_code"] not in seen:
        seen.add(cur["node_code"])
        trail.insert(0, cur)
        p = cur.get("parent_node_code")
        cur = node_map.get(p) if p else None

    if len(trail) > 1:
        cols = st.columns(len(trail))
        for idx, t in enumerate(trail):
            with cols[idx]:
                is_here = t["node_code"] == curr_node["node_code"]
                if st.button(
                    f"{'📍' if is_here else '↩️'} {t['node_name']}",
                    key=f"crumb_{t['node_code']}",
                    disabled=is_here,
                    use_container_width=True,
                ):
                    st.session_state["selected_node_code"] = t["node_code"]
                    st.rerun()

    st.markdown(f"### 🏛️ {curr_node['node_name']}")

    is_exec_room = (
        str(curr_node.get("node_code") or "").upper() == "DEPT_EXEC"
        or "總經理" in str(curr_node.get("node_name") or "")
    )
    has_l1_overview = False

    if is_exec_room and str(curr_node.get("level_tier") or "L1").upper() == "L1":
        render_executive_home_panels(engine, tenant_id, lang=curr_lang)
        has_l1_overview = True
        st.divider()
    elif str(curr_node.get("level_tier") or "L1").upper() == "L1":
        has_l1_overview = render_l1_department_overview(engine, tenant_id, curr_node, lang=curr_lang)
        if has_l1_overview:
            st.divider()

    if not all_nodes:
        if not is_exec_room and not has_l1_overview:
            st.warning(ui_theme.tr("no_org", curr_lang))
        return

    mounted = dynamic_router.get_mounted_features(engine, tenant_id, curr_node["node_code"])
    children = dynamic_router.get_child_nodes(engine, tenant_id, curr_node["node_code"])

    if curr_node.get("node_type") == "L1_FUNC" and len(mounted) == 1 and not children:
        dynamic_router.dispatch_feature(engine, mounted[0]["key"], lang=curr_lang)
        return

    if children:
        st.markdown(f"#### {ui_theme.tr('sub_cards', curr_lang)}")
        s_cols = st.columns(2)
        for idx, sub in enumerate(children):
            with s_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**{sub['node_name']}**")
                    if st.button(ui_theme.tr("enter_card", curr_lang), key=f"sub_{sub['node_code']}", use_container_width=True):
                        st.session_state["selected_node_code"] = sub["node_code"]
                        st.rerun()
        st.divider()

    st.markdown(f"#### {ui_theme.tr('mounted_feats', curr_lang)}")
    if not mounted:
        if not is_exec_room and not has_l1_overview:
            st.info(ui_theme.tr("no_feats", curr_lang))
    else:
        f_cols = st.columns(2)
        for idx, feat in enumerate(mounted):
            with f_cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"#### {feat['name']}")
                    st.caption(feat.get("group", ""))
                    if st.button(
                        ui_theme.tr("open_feat", curr_lang),
                        key=f"feat_{curr_node['node_code']}_{feat['key']}_{idx}",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state["current_view"] = "dynamic_feature"
                        st.session_state["active_feature_id"] = feat["key"]
                        st.rerun()


def show(engine=None, lang=None, **kwargs):
    render_dashboard(engine=engine, lang=lang, **kwargs)


def render(engine=None, lang=None, **kwargs):
    render_dashboard(engine=engine, lang=lang, **kwargs)
