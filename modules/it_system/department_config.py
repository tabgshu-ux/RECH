# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：SaaS 組織與功能拼圖設定中心主入口（純路由外殼，業務邏輯已完全拆分）
# ==========================================

import streamlit as st
from modules.it_system.org_puzzle import repo, org_tree_ui, mount_ui


def render(engine=None, lang="zh", **kwargs):
    st.markdown("### 🧩 SaaS 組織與功能拼圖設定中心")
    if not engine:
        st.warning("⚠️ 尚未連線資料庫引擎。")
        return

    repo.ensure_tables(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    all_nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=True)
    active_nodes = [n for n in all_nodes if n.get("is_active", True)]
    registry = repo.load_registry(engine)

    t1, t2, t3 = st.tabs(["🌳 1. 組織樹管理（L1～L4）", "🧩 2. 功能拼圖掛載", "➕ 3. 註冊新功能拼圖"])
    with t1:
        org_tree_ui.render_org_tree_tab(engine, tenant_id, all_nodes)
    with t2:
        mount_ui.render_mount_tab(engine, tenant_id, active_nodes, registry)
    with t3:
        mount_ui.render_register_tab(engine)


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
