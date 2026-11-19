# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/org_tree_ui.py
# 職責：Tab 1 組織樹檢視（L1～L4）與新增／修改／停用／刪除操作介面
# ==========================================

import streamlit as st
from modules.it_system.org_puzzle import repo

NEXT_TIER = {"L1": "L2", "L2": "L3", "L3": "L4", "L4": None}
PARENT_TIER = {"L2": "L1", "L3": "L2", "L4": "L3"}


def render_org_tree_tab(engine, tenant_id: str, all_nodes: list[dict]):
    active_nodes = [n for n in all_nodes if n.get("is_active", True)]
    col_left, col_right = st.columns([1.25, 1.15])

    with col_left:
        st.markdown("#### 🌲 租戶組織樹狀結構（L1 ～ L4）")
        chosen_tpl = st.selectbox("套用組織模板", list(repo.ORG_TEMPLATES.keys()), key="saas_tpl_select")
        if st.button("📥 套用／校準此組織模板", type="primary", use_container_width=True):
            try:
                repo.apply_org_template(engine, tenant_id, repo.ORG_TEMPLATES[chosen_tpl])
                st.success(f"✅ 已套用【{chosen_tpl}】。")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 套用失敗: {e}")

        show_inactive = st.checkbox("顯示已停用節點", value=False, key="show_inactive_org_nodes")
        display_nodes = all_nodes if show_inactive else active_nodes

        if not display_nodes:
            st.info("目前尚無組織節點，請套用模板或於右側新增。")
        else:
            def _draw_tree(parent_code, level, indent=0):
                items = [n for n in display_nodes if str(n.get("level_tier")).upper() == level and (n.get("parent_node_code") or None) == parent_code]
                for item in items:
                    tag = " `【已停用】`" if not item.get("is_active", True) else ""
                    icon = "🧭" if item.get("node_type") == "L1_FUNC" else "🗂️"
                    st.markdown(f"<div style='margin-left:{indent}px; padding:3px 0;'>{icon} <b>[{item['level_tier']}] {item['node_name']}</b> <code>{item['node_code']}</code>{tag}</div>", unsafe_allow_html=True)
                    if NEXT_TIER.get(level):
                        _draw_tree(item["node_code"], NEXT_TIER[level], indent + 22)

            with st.container(border=True):
                _draw_tree(None, "L1", 0)

    with col_right:
        mode = st.radio("操作模式", ["➕ 新增節點", "✏️ 修改節點", "🗑️ 停用 / 刪除"], horizontal=True, key="org_op_mode")

        if mode == "➕ 新增節點":
            tier = st.selectbox("層級", ["L1", "L2", "L3", "L4"], key="add_tier_sel")
            req_p = PARENT_TIER.get(tier)
            p_code = None
            if req_p:
                cands = [n for n in active_nodes if str(n.get("level_tier")).upper() == req_p and n.get("node_type") == "DEPT"]
                p_opts = {f"[{n['level_tier']}] {n['node_name']}": n["node_code"] for n in cands}
                if p_opts:
                    p_code = p_opts[st.selectbox(f"歸屬上層 {req_p}", list(p_opts.keys()), key="add_parent_sel")]
                else:
                    st.warning(f"⚠️ 請先建立 {req_p} 部門。")

            ntype = "DEPT"
            if tier == "L1":
                ntype = "L1_FUNC" if "功能" in st.radio("L1 性質", ["實體部門", "L1 功能入口"], horizontal=True) else "DEPT"

            with st.form("form_add_node"):
                name_in = st.text_input("名稱（支援中文、英文或越南文，系統自動產碼）", placeholder="例如: 設計三組 / Phòng Kế Toán / Assembly A")
                sort_in = st.number_input("排序權重", min_value=1, max_value=999, value=90)
                st.caption(f"自動產生代碼預覽：`{repo.generate_auto_node_code(tier, name_in, p_code, ntype)}`")

                if st.form_submit_button("💾 建立節點", type="primary", use_container_width=True):
                    if not name_in.strip():
                        st.warning("⚠️ 請輸入名稱。")
                    elif req_p and not p_code:
                        st.warning(f"⚠️ 請選擇上層 {req_p}。")
                    else:
                        code = repo.generate_auto_node_code(tier, name_in, p_code, ntype)
                        try:
                            repo.upsert_node(engine, tenant_id, code, name_in.strip(), tier, p_code, ntype, int(sort_in), True)
                            st.success(f"✅ 已建立【{name_in.strip()}】。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 建立失敗: {e}")

        elif mode == "✏️ 修改節點":
            if not all_nodes:
                st.info("尚無可修改節點。")
                return
            edit_map = {f"[{n['level_tier']}] {n['node_name']} ({n['node_code']})": n for n in all_nodes}
            target = edit_map[st.selectbox("選擇目標節點", list(edit_map.keys()), key="edit_target_sel")]

            upd_tier = st.selectbox("層級", ["L1", "L2", "L3", "L4"], index=["L1", "L2", "L3", "L4"].index(target["level_tier"]), key="upd_tier_sel")
            req_p = PARENT_TIER.get(upd_tier)
            upd_parent = None
            if req_p:
                cands = [n for n in active_nodes if n["level_tier"] == req_p and n["node_code"] != target["node_code"] and n.get("node_type") == "DEPT"]
                p_opts = {f"[{n['level_tier']}] {n['node_name']}": n["node_code"] for n in cands}
                if p_opts:
                    vals = list(p_opts.values())
                    idx = vals.index(target["parent_node_code"]) if target.get("parent_node_code") in vals else 0
                    upd_parent = p_opts[st.selectbox(f"上層 {req_p}", list(p_opts.keys()), index=idx, key="upd_parent_sel")]

            with st.form("form_edit_node"):
                upd_name = st.text_input("顯示名稱（中／英／越文皆可）", value=target["node_name"])
                upd_sort = st.number_input("排序權重", min_value=1, max_value=999, value=int(target.get("sort_order") or 100))
                upd_act = st.checkbox("啟用狀態", value=bool(target.get("is_active", True)))
                st.caption(f"鎖定代碼：`{target['node_code']}`（改名不改代碼，確保已掛載功能與歷史單據不中斷）")

                if st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True):
                    if not upd_name.strip() or (req_p and not upd_parent):
                        st.warning("⚠️ 請確認名稱與上層歸屬已填妥。")
                    else:
                        try:
                            repo.upsert_node(engine, tenant_id, target["node_code"], upd_name.strip(), upd_tier, upd_parent, target.get("node_type", "DEPT"), int(upd_sort), upd_act)
                            st.success("✅ 修改已儲存。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 修改失敗: {e}")

        else:
            if not all_nodes:
                st.info("尚無可操作節點。")
                return
            del_map = {f"[{n['level_tier']}] {n['node_name']} ({n['node_code']})": n for n in all_nodes}
            target = del_map[st.selectbox("選擇目標節點", list(del_map.keys()), key="del_target_sel")]
            has_child = any(n.get("parent_node_code") == target["node_code"] for n in all_nodes)

            c1, c2 = st.columns(2)
            with c1:
                btn_txt = "🔴 停用" if target.get("is_active", True) else "🟢 啟用"
                if st.button(btn_txt, use_container_width=True):
                    if target.get("is_active", True) and any(n.get("parent_node_code") == target["node_code"] and n.get("is_active", True) for n in all_nodes):
                        st.error("❌ 底下仍有啟用中的子節點，請先停用下層。")
                    else:
                        repo.upsert_node(engine, tenant_id, target["node_code"], target["node_name"], target["level_tier"], target.get("parent_node_code"), target.get("node_type", "DEPT"), int(target.get("sort_order") or 100), not bool(target.get("is_active", True)))
                        st.rerun()
            with c2:
                ok_del = st.checkbox("確認永久刪除", key="chk_perm_del")
                if st.button("🗑️ 刪除", use_container_width=True, disabled=not ok_del):
                    if has_child:
                        st.error("❌ 存在子節點紀錄，禁止直接刪除；請改用「停用」。")
                    else:
                        repo.delete_node_permanently(engine, tenant_id, target["node_code"])
                        st.success("✅ 已刪除。")
                        st.rerun()
