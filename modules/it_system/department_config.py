# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：系統設定「組織樹管理（L1~L4）與功能拼圖掛載」主入口
# ==========================================

import streamlit as st
from core import ui_theme
from modules.it_system.org_puzzle import mount_ui, org_tree_ui, repo


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    header_map = {
        "zh": ("🧩 系統設定：組織樹與功能拼圖中心", "在系統設定完成 L1～L4 組織建置與功能拼圖掛載，無需修改業務程式。"),
        "vi": ("🧩 Cài Đặt Hệ Thống: Cây Tổ Chức & Gắn Chức Năng", "Cấu hình cấp bậc L1–L4 và gắn các khối chức năng trực tiếp trên hệ thống."),
        "en": ("🧩 System Settings: Org Tree & Feature Puzzle Hub", "Configure L1–L4 organization nodes and mount feature puzzles directly in settings."),
    }
    h_title, h_sub = header_map[code]

    st.markdown(f"### {h_title}")
    st.caption(h_sub)

    if not engine:
        st.warning("⚠️ 尚未連線資料庫引擎。")
        return

    repo.ensure_tables(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    all_nodes = repo.load_tenant_nodes(engine, tenant_id, include_inactive=True)
    active_nodes = [n for n in all_nodes if n.get("is_active", True)]
    registry = repo.load_registry(engine)

    t1, t2, t3 = st.tabs([
        "🌳 1. 組織樹管理（L1～L4）",
        "🧩 2. 功能拼圖掛載",
        "➕ 3. 拼圖註冊與管理",
    ])
    with t1:
        org_tree_ui.render_org_tree_tab(engine, tenant_id, all_nodes)
    with t2:
        mount_ui.render_mount_tab(engine, tenant_id, active_nodes, registry)
    with t3:
        mount_ui.render_register_tab(engine)


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
