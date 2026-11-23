# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/org_tree_ui.py
# 職責：L1 系統設定／功能拼圖 - 清晰階層組織樹視覺化（Graphviz）與勾選排序編號
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text


DEFAULT_FALLBACK_NODES = [
    {"node_code": "COMPANY_ROOT", "node_name": "裕豐電機工業有限公司", "parent_node_code": None, "level_tier": "L0", "sort_order": 1, "is_active": True},
    {"node_code": "DEPT_EXEC", "node_name": "總經理室", "parent_node_code": "COMPANY_ROOT", "level_tier": "L1", "sort_order": 10, "is_active": True},
    {"node_code": "DEPT_ENG", "node_name": "工程部", "parent_node_code": "DEPT_EXEC", "level_tier": "L2", "sort_order": 20, "is_active": True},
    {"node_code": "DEPT_MGMT", "node_name": "管理部", "parent_node_code": "DEPT_EXEC", "level_tier": "L2", "sort_order": 30, "is_active": True},
    {"node_code": "DEPT_PROD", "node_name": "生產部", "parent_node_code": "DEPT_EXEC", "level_tier": "L2", "sort_order": 40, "is_active": True},
    {"node_code": "DEPT_ENG_DESIGN", "node_name": "設計", "parent_node_code": "DEPT_ENG", "level_tier": "L3", "sort_order": 21, "is_active": True},
    {"node_code": "DEPT_MGMT_HR", "node_name": "行政/人事", "parent_node_code": "DEPT_MGMT", "level_tier": "L3", "sort_order": 31, "is_active": True},
    {"node_code": "DEPT_MGMT_GA", "node_name": "總務/採購", "parent_node_code": "DEPT_MGMT", "level_tier": "L3", "sort_order": 32, "is_active": True},
    {"node_code": "DEPT_MGMT_FIN", "node_name": "財務/會計", "parent_node_code": "DEPT_MGMT", "level_tier": "L3", "sort_order": 33, "is_active": True},
    {"node_code": "DEPT_PROD_SHEET", "node_name": "板金", "parent_node_code": "DEPT_PROD", "level_tier": "L3", "sort_order": 41, "is_active": True},
    {"node_code": "DEPT_PROD_PAINT", "node_name": "塗裝", "parent_node_code": "DEPT_PROD", "level_tier": "L3", "sort_order": 42, "is_active": True},
]


def _escape_dot_label(text_val: str) -> str:
    return str(text_val or "").replace("\\", "\\\\").replace('"', '\\"')


def _build_org_tree_dot(nodes: list[dict]) -> str:
    """產生乾淨易讀的由上而下組織樹 Graphviz DOT 語法"""
    lines = [
        "digraph OrgTree {",
        '  rankdir=TB;',
        '  splines=polyline;',
        '  nodesep=0.35;',
        '  ranksep=0.55;',
        '  bgcolor="transparent";',
        '  node [shape=box, style="rounded,filled", fontname="Microsoft JhengHei", fontsize=11, margin="0.18,0.10", penwidth=1.2, color="#64748B"];',
        '  edge [color="#475569", penwidth=1.3, arrowsize=0.7];',
    ]

    valid_codes = {str(n.get("node_code")): n for n in nodes if n.get("node_code")}

    for n in nodes:
        code = str(n.get("node_code") or "")
        if not code:
            continue
        name = _escape_dot_label(n.get("node_name") or code)
        tier = str(n.get("level_tier") or "")

        if tier == "L0":
            fill = "#DBEAFE"
            shape_attr = "shape=ellipse,"
        elif tier == "L1":
            fill = "#E0F2FE"
            shape_attr = ""
        elif tier == "L2":
            fill = "#E2E8F0"
            shape_attr = ""
        elif "設計" in name:
            fill = "#FEF3C7"
            shape_attr = ""
        elif any(k in name for k in ("人事", "總務", "採購", "財務", "會計", "管理")):
            fill = "#DCFCE7"
            shape_attr = ""
        elif any(k in name for k in ("板金", "塗裝", "生產", "製造")):
            fill = "#FEE2E2"
            shape_attr = ""
        else:
            fill = "#F1F5F9"
            shape_attr = ""

        lines.append(f'  "{code}" [{shape_attr}fillcolor="{fill}", label="{name}"];')

    for n in nodes:
        code = str(n.get("node_code") or "")
        parent = str(n.get("parent_node_code") or "").strip()
        if code and parent and parent in valid_codes:
            lines.append(f'  "{parent}" -> "{code}";')

    lines.append("}")
    return "\n".join(lines)


def render_numbered_puzzle_selector(
    puzzle_items: list[dict],
    initial_selected_keys: list[str] | None = None,
    state_prefix: str = "puzzle_order",
) -> list[str]:
    """
    依勾選先後順序自動標示 1. 2. 3. 4... 編號，並回傳有序的已勾選 key 清單。
    """
    order_key = f"{state_prefix}_ordered_keys"
    init_flag = f"{state_prefix}_initialized"

    if init_flag not in st.session_state:
        st.session_state[init_flag] = True
        st.session_state[order_key] = list(initial_selected_keys or [])

    valid_keys = [str(item.get("key")) for item in (puzzle_items or []) if item.get("key")]
    valid_set = set(valid_keys)
    name_map = {
        str(item.get("key")): str(item.get("name") or item.get("key"))
        for item in (puzzle_items or [])
        if item.get("key")
    }

    ordered_keys: list[str] = [k for k in st.session_state.get(order_key, []) if k in valid_set]

    if ordered_keys:
        preview_line = " ".join([f"**{idx + 1}.** {name_map.get(k, k)}" for idx, k in enumerate(ordered_keys)])
        st.markdown(f"📌 **目前勾選排序（依勾選先後）：** {preview_line}")
    else:
        st.caption("📌 尚未勾選任何功能，勾選後將依先後顯示 1.、2.、3.、4. 排序編號。")

    c_ctrl1, _ = st.columns([1.8, 5.2])
    with c_ctrl1:
        if st.button("🔄 清除全部勾選", key=f"{state_prefix}_clear_all"):
            st.session_state[order_key] = []
            for k in valid_keys:
                st.session_state[f"{state_prefix}_chk_{k}"] = False
            st.rerun()

    current_rank_map = {k: idx + 1 for idx, k in enumerate(ordered_keys)}
    groups: list[str] = []
    for item in puzzle_items or []:
        g = str(item.get("group") or "其他")
        if g not in groups:
            groups.append(g)

    updated_order: list[str] = list(ordered_keys)

    for grp in groups:
        st.markdown(f"#### {grp}")
        grp_items = [it for it in (puzzle_items or []) if str(it.get("group") or "其他") == grp]
        cols = st.columns(2)

        for idx_in_grp, item in enumerate(grp_items):
            pkey = str(item.get("key"))
            pname = str(item.get("name") or pkey)
            chk_state_key = f"{state_prefix}_chk_{pkey}"

            if chk_state_key not in st.session_state:
                st.session_state[chk_state_key] = pkey in current_rank_map

            rank_num = current_rank_map.get(pkey)
            label_text = f"**{rank_num}.** {pname} (`{pkey}`)" if rank_num else f"{pname} (`{pkey}`)"

            with cols[idx_in_grp % 2]:
                checked = st.checkbox(label_text, key=chk_state_key)

            if checked and pkey not in updated_order:
                updated_order.append(pkey)
            elif (not checked) and pkey in updated_order:
                updated_order.remove(pkey)

    if updated_order != ordered_keys:
        st.session_state[order_key] = updated_order
        st.rerun()

    return updated_order


def _ensure_org_nodes_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.sys_tenant_org_nodes (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        node_code VARCHAR(80) NOT NULL,
                        node_name VARCHAR(150) NOT NULL,
                        parent_node_code VARCHAR(80),
                        level_tier VARCHAR(20) DEFAULT 'L2',
                        sort_order INT DEFAULT 1,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (tenant_id, node_code)
                    );
                """)
            )
    except Exception:
        pass


def render_org_tree_tab(engine=None, tenant_id: str = "REETECH_VN", active_nodes: list[dict] | None = None, **kwargs):
    """供 department_config 呼叫的組織樹管理分頁（視覺化組織樹＋節點明細＋新增節點）"""
    tid = tenant_id or st.session_state.get("tenant_id", "REETECH_VN")
    st.markdown("#### 🌳 組織樹架構圖（L1～L4）")
    st.caption("由上而下呈現公司、總經理室、各部門與下轄組別的從屬關係。")

    _ensure_org_nodes_table(engine)

    nodes: list[dict] = []
    if engine:
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT node_code, node_name, parent_node_code, level_tier, sort_order, is_active
                        FROM public.sys_tenant_org_nodes
                        WHERE tenant_id = :tid AND COALESCE(is_active, TRUE) = TRUE
                        ORDER BY sort_order ASC, id ASC
                    """),
                    {"tid": tid},
                ).fetchall()
                nodes = [r._asdict() for r in rows]
        except Exception:
            nodes = []

    if not nodes:
        nodes = list(active_nodes or DEFAULT_FALLBACK_NODES)

    # 視覺化組織樹圖
    dot_code = _build_org_tree_dot(nodes)
    st.graphviz_chart(dot_code, use_container_width=True)

    st.divider()
    st.markdown("##### 📋 組織節點明細表")
    df_n = pd.DataFrame(nodes)
    disp_cols = [c for c in ["node_code", "node_name", "parent_node_code", "level_tier", "sort_order", "is_active"] if c in df_n.columns]
    st.dataframe(
        df_n[disp_cols].rename(columns={
            "node_code": "節點代碼",
            "node_name": "節點名稱",
            "parent_node_code": "上層節點",
            "level_tier": "層級",
            "sort_order": "排序",
            "is_active": "啟用",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("##### ➕ 新增／更新組織節點")
    parent_options = ["（無上層／頂層）"] + [str(n.get("node_code")) for n in nodes if n.get("node_code")]
    with st.form("form_add_org_node_quick"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            n_code = st.text_input("節點代碼*", placeholder="例: DEPT_MGMT_HR2")
        with c2:
            n_name = st.text_input("節點名稱*", placeholder="例: 薪資組")
        with c3:
            n_tier = st.selectbox("層級", ["L1", "L2", "L3", "L4"], index=2)
        with c4:
            n_parent_sel = st.selectbox("上層節點代碼", parent_options, index=0)

        if st.form_submit_button("💾 儲存組織節點", type="primary", use_container_width=True):
            if not n_code.strip() or not n_name.strip():
                st.warning("⚠️ 請填寫節點代碼與名稱。")
            elif not engine:
                st.warning("⚠️ 目前尚未連線資料庫，僅做畫面預覽。")
            else:
                parent_val = None if n_parent_sel == "（無上層／頂層）" else n_parent_sel
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO public.sys_tenant_org_nodes (
                                    tenant_id, node_code, node_name, parent_node_code, level_tier, sort_order, is_active
                                )
                                VALUES (:tid, :nc, :nn, :pn, :lt, 99, TRUE)
                                ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                                    node_name = EXCLUDED.node_name,
                                    parent_node_code = EXCLUDED.parent_node_code,
                                    level_tier = EXCLUDED.level_tier,
                                    is_active = TRUE
                            """),
                            {
                                "tid": tid,
                                "nc": n_code.strip(),
                                "nn": n_name.strip(),
                                "pn": parent_val,
                                "lt": n_tier,
                            },
                        )
                    st.success(f"✅ 已儲存組織節點【{n_name.strip()}】，組織樹已同步更新。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存節點失敗：{e}")


def _load_default_puzzle_items() -> list[dict]:
    try:
        from modules.it_system.org_puzzle import repo

        for attr_name in ("DEFAULT_PUZZLE_REGISTRY", "PUZZLE_REGISTRY", "ALL_PUZZLES"):
            val = getattr(repo, attr_name, None)
            if isinstance(val, list) and val:
                return val
    except Exception:
        pass
    return []


def render_org_puzzle_order_ui(
    engine=None,
    tenant_id: str = "REETECH_VN",
    node_key: str = "management",
    puzzle_items: list[dict] | None = None,
    initial_selected_keys: list[str] | None = None,
    **kwargs,
):
    tid = tenant_id or st.session_state.get("tenant_id", "REETECH_VN")
    items = puzzle_items if puzzle_items is not None else _load_default_puzzle_items()

    st.markdown("### 🧩 功能拼圖勾選與排序（依勾選先後編號 1. 2. 3. 4...）")
    if not items:
        st.info("目前尚未取得功能拼圖清單。")
        return []

    selected_keys = render_numbered_puzzle_selector(
        puzzle_items=items,
        initial_selected_keys=initial_selected_keys or [],
        state_prefix=f"puzzle_order_{tid}_{node_key}",
    )

    if engine and st.button(
        "💾 儲存目前勾選排序",
        type="primary",
        use_container_width=True,
        key=f"btn_save_puzzle_order_{tid}_{node_key}",
    ):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        CREATE TABLE IF NOT EXISTS public.sys_tenant_node_mounts (
                            id SERIAL PRIMARY KEY,
                            tenant_id VARCHAR(64) NOT NULL,
                            node_key VARCHAR(80) NOT NULL,
                            feat_key VARCHAR(120) NOT NULL,
                            sort_order INT DEFAULT 1,
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE (tenant_id, node_key, feat_key)
                        );
                    """)
                )
                conn.execute(
                    text("DELETE FROM public.sys_tenant_node_mounts WHERE tenant_id = :tid AND node_key = :nk"),
                    {"tid": tid, "nk": node_key},
                )
                for idx, fkey in enumerate(selected_keys, start=1):
                    conn.execute(
                        text("""
                            INSERT INTO public.sys_tenant_node_mounts (tenant_id, node_key, feat_key, sort_order, updated_at)
                            VALUES (:tid, :nk, :fk, :so, CURRENT_TIMESTAMP)
                        """),
                        {"tid": tid, "nk": node_key, "fk": fkey, "so": idx},
                    )
            st.success(f"✅ 已依勾選順序儲存 {len(selected_keys)} 項功能拼圖。")
        except Exception as e:
            st.error(f"❌ 儲存排序失敗：{e}")

    return selected_keys


def render(engine=None, lang="zh", **kwargs):
    return render_org_tree_tab(engine=engine, **kwargs)


def show(engine=None, lang="zh", **kwargs):
    return render_org_tree_tab(engine=engine, **kwargs)
