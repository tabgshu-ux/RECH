# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：SaaS 組織樹（L1~L4 新增/修改/停用/刪除 + 中/英/越文自動產碼）與功能拼圖掛載中心
# ==========================================

import hashlib
import re
import unicodedata
import streamlit as st
from sqlalchemy import text


DEFAULT_PUZZLE_REGISTRY = [
    {"key": "feat_eng_quotation", "name": "📐 估價中心", "group": "業務與專案", "module": "modules.engineering.financial.quotation", "func": "render"},
    {"key": "feat_site_log", "name": "📋 工地巡檢與施工日報", "group": "現場作業", "module": "modules.engineering.site_ops.daily_report", "func": "render"},
    {"key": "feat_blueprint", "name": "📐 設計圖紙與審查", "group": "設計與品管", "module": "modules.engineering.procurement_qc.testing_acceptance", "func": "render"},
    {"key": "feat_bom_procurement", "name": "📦 工程 BOM 與採購需求", "group": "供應鏈與採購", "module": "modules.engineering.procurement_qc.bom_procurement", "func": "render"},
    {"key": "feat_project_pnl", "name": "📊 專案損益追蹤", "group": "財務與成本", "module": "modules.engineering.financial.project_pnl", "func": "render"},
    {"key": "feat_my_approvals", "name": "✍️ 簽核中心（請假／採購／文書／估價）", "group": "全公司共用", "module": "modules.approval_workflow", "func": "render_approval_center"},
    {"key": "feat_field_gps_clockin", "name": "📍 外勤工程人員線上打卡", "group": "現場作業", "module": "modules.engineering.site_ops.gps_attendance", "func": "render"},
    {"key": "feat_security_guard_ops", "name": "🛡️ 保全操作頁面", "group": "廠區安控", "module": "modules.management.security_gate", "func": "render"},
    {"key": "feat_lme_commodities", "name": "📈 原料市場與外匯行情", "group": "經營決策", "module": "modules.executive.commodities_fx", "func": "show"},
    {"key": "feat_circular_200", "name": "💰 財務會計與標準財報", "group": "財務與成本", "module": "modules.executive.financials_pl", "func": "show"},
]

ORG_TEMPLATES = {
    "裕豐電機標準模板（L1/L2 + 現場入口）": [
        {"code": "DEPT_EXEC", "name": "總經理室", "tier": "L1", "parent": None, "type": "DEPT", "sort": 10},
        {"code": "DEPT_ENG", "name": "工程部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 20},
        {"code": "DEPT_ENG_DESIGN", "name": "設計", "tier": "L2", "parent": "DEPT_ENG", "type": "DEPT", "sort": 21},
        {"code": "DEPT_MGMT", "name": "管理部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 30},
        {"code": "DEPT_MGMT_HR", "name": "行政/人事", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 31},
        {"code": "DEPT_MGMT_GA", "name": "總務/採購", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 32},
        {"code": "DEPT_MGMT_FIN", "name": "財務/會計", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 33},
        {"code": "DEPT_PROD", "name": "生產部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 40},
        {"code": "DEPT_PROD_SHEET", "name": "板金", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 41},
        {"code": "DEPT_PROD_PAINT", "name": "塗裝", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 42},
        {"code": "DEPT_PROD_PANEL", "name": "配盤", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 43},
        {"code": "DEPT_PROD_WH", "name": "倉庫管理", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 44},
        {"code": "FUNC_APPROVAL_CENTER", "name": "簽核中心", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 50},
        {"code": "FUNC_FIELD_CLOCKIN", "name": "外勤工程人員線上打卡", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 60},
        {"code": "FUNC_SECURITY_GATE", "name": "保全操作頁面", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 70},
    ],
    "通用製造／工程精簡模板": [
        {"code": "DEPT_EXEC", "name": "總經理室", "tier": "L1", "parent": None, "type": "DEPT", "sort": 10},
        {"code": "DEPT_ENG", "name": "工程部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 20},
        {"code": "DEPT_ENG_DESIGN", "name": "設計組", "tier": "L2", "parent": "DEPT_ENG", "type": "DEPT", "sort": 21},
        {"code": "DEPT_OPS", "name": "營運管理部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 30},
        {"code": "FUNC_APPROVAL_CENTER", "name": "簽核中心", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 40},
    ],
}


def generate_auto_node_code(tier: str, name: str, parent_code: str | None = None, node_type: str = "DEPT") -> str:
    """
    依中文、英文或越南文名稱自動產生唯一且可讀的系統代碼（使用者免填寫）。
    例如：Kế toán -> KE_TOAN_xxxx；設計三組 -> UNIT_xxxx。
    """
    clean_name = (name or "").strip()
    # 處理越南文 đ / Đ
    vn_mapped = clean_name.replace("đ", "d").replace("Đ", "D")
    # 拆解重音符號（適用越南文與拉丁字母）
    normalized = unicodedata.normalize("NFD", vn_mapped)
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    ascii_slug = re.sub(r"[^A-Za-z0-9]+", "_", without_accents).strip("_").upper()
    ascii_slug = re.sub(r"_+", "_", ascii_slug)[:14]

    digest_source = f"{tier}|{parent_code or ''}|{node_type}|{clean_name}".encode("utf-8")
    short_hash = hashlib.sha1(digest_source).hexdigest()[:4].upper()

    prefix = "FUNC" if node_type == "L1_FUNC" else (tier or "L1").upper()
    if ascii_slug:
        return f"{prefix}_{ascii_slug}_{short_hash}"
    return f"{prefix}_NODE_{short_hash}"


def _ensure_saas_metadata_tables(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_feature_registry (
                    id SERIAL PRIMARY KEY,
                    feature_key VARCHAR(120) UNIQUE NOT NULL,
                    feature_name VARCHAR(160) NOT NULL,
                    feature_group VARCHAR(100) DEFAULT '通用拼圖',
                    module_path VARCHAR(255),
                    entry_func VARCHAR(100) DEFAULT 'render',
                    is_active BOOLEAN DEFAULT TRUE
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_tenant_org_nodes (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    node_code VARCHAR(80) NOT NULL,
                    node_name VARCHAR(120) NOT NULL,
                    level_tier VARCHAR(16) DEFAULT 'L1',
                    parent_node_code VARCHAR(80),
                    node_type VARCHAR(32) DEFAULT 'DEPT',
                    sort_order INT DEFAULT 100,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (tenant_id, node_code)
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_tenant_node_mounts (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) NOT NULL,
                    node_code VARCHAR(80) NOT NULL,
                    mounted_features TEXT DEFAULT '',
                    landing_role_code VARCHAR(80),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (tenant_id, node_code)
                );
            """))

            for item in DEFAULT_PUZZLE_REGISTRY:
                conn.execute(text("""
                    INSERT INTO sys_feature_registry (
                        feature_key, feature_name, feature_group, module_path, entry_func, is_active
                    )
                    VALUES (:k, :n, :g, :m, :f, TRUE)
                    ON CONFLICT (feature_key) DO UPDATE SET
                        feature_group = EXCLUDED.feature_group,
                        module_path = COALESCE(sys_feature_registry.module_path, EXCLUDED.module_path),
                        entry_func = COALESCE(sys_feature_registry.entry_func, EXCLUDED.entry_func),
                        is_active = TRUE
                """), {
                    "k": item["key"],
                    "n": item["name"],
                    "g": item["group"],
                    "m": item["module"],
                    "f": item["func"],
                })
    except Exception:
        pass


def _load_registry(engine):
    registry = list(DEFAULT_PUZZLE_REGISTRY)
    if not engine:
        return registry
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT feature_key, feature_name, feature_group, module_path, entry_func
                FROM sys_feature_registry
                WHERE is_active = TRUE
                ORDER BY id ASC
            """)).fetchall()
            if rows:
                db_map = {}
                for r in rows:
                    d = r._asdict()
                    db_map[d["feature_key"]] = {
                        "key": d["feature_key"],
                        "name": d["feature_name"],
                        "group": d.get("feature_group") or "擴充拼圖",
                        "module": d.get("module_path"),
                        "func": d.get("entry_func") or "render",
                    }
                for item in registry:
                    if item["key"] in db_map:
                        db_map[item["key"]]["module"] = db_map[item["key"]]["module"] or item["module"]
                return list(db_map.values())
    except Exception:
        pass
    return registry


def _load_tenant_nodes(engine, tenant_id, include_inactive=False):
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            sql = """
                SELECT node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active
                FROM sys_tenant_org_nodes
                WHERE tenant_id = :tid
            """
            if not include_inactive:
                sql += " AND is_active = TRUE"
            sql += " ORDER BY sort_order ASC, id ASC"
            rows = conn.execute(text(sql), {"tid": tenant_id}).fetchall()
            return [r._asdict() for r in rows]
    except Exception:
        return []


def _apply_template(engine, tenant_id, template_items):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE sys_tenant_org_nodes
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE tenant_id = :tid
        """), {"tid": tenant_id})

        for item in template_items:
            conn.execute(text("""
                INSERT INTO sys_tenant_org_nodes (
                    tenant_id, node_code, node_name, level_tier,
                    parent_node_code, node_type, sort_order, is_active, updated_at
                )
                VALUES (:tid, :c, :n, :tier, :parent, :ntype, :sort, TRUE, CURRENT_TIMESTAMP)
                ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                    node_name = EXCLUDED.node_name,
                    level_tier = EXCLUDED.level_tier,
                    parent_node_code = EXCLUDED.parent_node_code,
                    node_type = EXCLUDED.node_type,
                    sort_order = EXCLUDED.sort_order,
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
            """), {
                "tid": tenant_id,
                "c": item["code"],
                "n": item["name"],
                "tier": item["tier"],
                "parent": item["parent"],
                "ntype": item["type"],
                "sort": item["sort"],
            })


def _get_allowed_parent_tier(tier: str) -> str | None:
    mapping = {"L2": "L1", "L3": "L2", "L4": "L3"}
    return mapping.get((tier or "").upper())


def render(engine=None, lang="zh", **kwargs):
    st.markdown("### 🧩 SaaS 組織與功能拼圖設定中心")
    st.caption("支援 L1～L4 組織新增／修改／停用／刪除，輸入中／英／越文名稱自動產生代碼；所有功能皆可自由拼裝掛載。")

    if not engine:
        st.warning("⚠️ 尚未連線資料庫引擎。")
        return

    _ensure_saas_metadata_tables(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    st.caption(f"目前租戶：`{tenant_id}`")

    all_nodes = _load_tenant_nodes(engine, tenant_id, include_inactive=True)
    active_nodes = [n for n in all_nodes if n.get("is_active", True)]
    registry = _load_registry(engine)

    tab_org, tab_mount, tab_reg = st.tabs([
        "🌳 1. 組織樹管理（L1～L4）",
        "🧩 2. 功能拼圖掛載",
        "➕ 3. 註冊新功能拼圖"
    ])

    # ------------------------------------------
    # Tab 1：L1~L4 組織樹檢視、新增、修改、停用／刪除
    # ------------------------------------------
    with tab_org:
        col_left, col_right = st.columns([1.25, 1.15])

        with col_left:
            st.markdown("#### 🌲 租戶組織樹狀結構（L1 ～ L4）")
            chosen_tpl = st.selectbox("套用組織模板", list(ORG_TEMPLATES.keys()), key="saas_tpl_select")
            if st.button("📥 套用／校準此組織模板", type="primary", use_container_width=True):
                try:
                    _apply_template(engine, tenant_id, ORG_TEMPLATES[chosen_tpl])
                    st.success(f"✅ 已套用【{chosen_tpl}】。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 套用模板失敗: {e}")

            show_inactive = st.checkbox("顯示已停用節點", value=False, key="show_inactive_org_nodes")
            display_nodes = all_nodes if show_inactive else active_nodes

            if not display_nodes:
                st.info("目前尚無組織節點，請套用模板或於右側新增。")
            else:
                def _render_subtree(parent_code, level_target, indent_px=0):
                    matched = [
                        n for n in display_nodes
                        if str(n.get("level_tier")).upper() == level_target
                        and (n.get("parent_node_code") or None) == parent_code
                    ]
                    next_tier_map = {"L1": "L2", "L2": "L3", "L3": "L4", "L4": None}
                    for n in matched:
                        status_txt = "" if n.get("is_active", True) else " `【已停用】`"
                        role_icon = "🧭" if n.get("node_type") == "L1_FUNC" else "🗂️"
                        st.markdown(
                            f"<div style='margin-left:{indent_px}px; padding:4px 0;'>"
                            f"{role_icon} <b>[{n['level_tier']}] {n['node_name']}</b> "
                            f"<code>{n['node_code']}</code>{status_txt}</div>",
                            unsafe_allow_html=True,
                        )
                        nxt = next_tier_map.get(level_target)
                        if nxt:
                            _render_subtree(n["node_code"], nxt, indent_px + 22)

                with st.container(border=True):
                    _render_subtree(None, "L1", indent_px=0)

        with col_right:
            action_mode = st.radio(
                "操作模式",
                ["➕ 新增節點", "✏️ 修改現有節點", "🗑️ 停用 / 刪除節點"],
                horizontal=True,
                key="org_action_mode",
            )

            # --- 新增節點（支援 L1~L4，自動依中/英/越文產碼）---
            if action_mode == "➕ 新增節點":
                st.markdown("#### ➕ 新增 L1 ～ L4 節點（自動產生代碼）")
                tier_choice = st.selectbox("選擇層級", ["L1", "L2", "L3", "L4"], key="add_node_tier")
                req_parent_tier = _get_allowed_parent_tier(tier_choice)
                parent_code_val = None

                if req_parent_tier:
                    candidates = [
                        n for n in active_nodes
                        if str(n.get("level_tier")).upper() == req_parent_tier and n.get("node_type") == "DEPT"
                    ]
                    p_opts = {f"[{n['level_tier']}] {n['node_name']} ({n['node_code']})": n["node_code"] for n in candidates}
                    if p_opts:
                        p_sel = st.selectbox(f"選擇上層 {req_parent_tier} 部門", list(p_opts.keys()), key="add_node_parent")
                        parent_code_val = p_opts[p_sel]
                    else:
                        st.warning(f"⚠️ 尚無啟用中的 {req_parent_tier} 部門可作為上層，請先建立 {req_parent_tier}。")

                node_type_val = "DEPT"
                if tier_choice == "L1":
                    ntype_label = st.radio("L1 節點性質", ["實體部門 (DEPT)", "L1 功能入口 (L1_FUNC)"], horizontal=True, key="add_l1_ntype")
                    node_type_val = "L1_FUNC" if "L1_FUNC" in ntype_label else "DEPT"

                with st.form("saas_add_l1_l4_form"):
                    name_input = st.text_input(
                        "節點名稱（支援中文、英文或越南文，系統自動產生代碼）",
                        placeholder="例如: 設計三組 / Phòng Thiết Kế / Design Team",
                    )
                    sort_input = st.number_input("排序權重", min_value=1, max_value=999, value=90)
                    preview_code = generate_auto_node_code(tier_choice, name_input, parent_code_val, node_type_val)
                    st.caption(f"系統自動產生代碼預覽：`{preview_code}`")

                    if st.form_submit_button("💾 建立節點", type="primary", use_container_width=True):
                        c_name = name_input.strip()
                        if not c_name:
                            st.warning("⚠️ 請輸入節點名稱。")
                        elif req_parent_tier and not parent_code_val:
                            st.warning(f"⚠️ 請先選擇上層 {req_parent_tier} 部門。")
                        else:
                            auto_code = generate_auto_node_code(tier_choice, c_name, parent_code_val, node_type_val)
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        INSERT INTO sys_tenant_org_nodes (
                                            tenant_id, node_code, node_name, level_tier,
                                            parent_node_code, node_type, sort_order, is_active, updated_at
                                        )
                                        VALUES (:tid, :c, :n, :tier, :p, :nt, :s, TRUE, CURRENT_TIMESTAMP)
                                        ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                                            node_name = EXCLUDED.node_name,
                                            level_tier = EXCLUDED.level_tier,
                                            parent_node_code = EXCLUDED.parent_node_code,
                                            node_type = EXCLUDED.node_type,
                                            sort_order = EXCLUDED.sort_order,
                                            is_active = TRUE,
                                            updated_at = CURRENT_TIMESTAMP
                                    """), {
                                        "tid": tenant_id,
                                        "c": auto_code,
                                        "n": c_name,
                                        "tier": tier_choice,
                                        "p": parent_code_val,
                                        "nt": node_type_val,
                                        "s": int(sort_input),
                                    })
                                st.success(f"✅ 已建立【{c_name}】（代碼：`{auto_code}`）。")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ 建立節點失敗: {e}")

            # --- 修改現有節點（改名稱、層級、上層、排序；保留原有代碼避免關聯斷鏈）---
            elif action_mode == "✏️ 修改現有節點":
                st.markdown("#### ✏️ 修改現有節點（保留既有代碼避免歷史關聯斷鏈）")
                if not all_nodes:
                    st.info("目前沒有可修改的節點。")
                else:
                    edit_map = {
                        f"[{n['level_tier']}] {n['node_name']} ({n['node_code']}){'' if n.get('is_active', True) else ' [已停用]'}": n
                        for n in all_nodes
                    }
                    sel_edit_lbl = st.selectbox("選擇要修改的節點", list(edit_map.keys()), key="edit_node_sel")
                    target_n = edit_map[sel_edit_lbl]

                    upd_tier = st.selectbox(
                        "調整層級",
                        ["L1", "L2", "L3", "L4"],
                        index=["L1", "L2", "L3", "L4"].index(str(target_n.get("level_tier") or "L1").upper())
                        if str(target_n.get("level_tier") or "L1").upper() in ["L1", "L2", "L3", "L4"] else 0,
                        key="edit_node_tier",
                    )
                    req_p = _get_allowed_parent_tier(upd_tier)
                    upd_parent = None
                    if req_p:
                        p_cands = [
                            n for n in active_nodes
                            if str(n.get("level_tier")).upper() == req_p
                            and n["node_code"] != target_n["node_code"]
                            and n.get("node_type") == "DEPT"
                        ]
                        p_dict = {f"[{n['level_tier']}] {n['node_name']} ({n['node_code']})": n["node_code"] for n in p_cands}
                        if p_dict:
                            default_idx = 0
                            for idx_k, (_, c_val) in enumerate(p_dict.items()):
                                if c_val == target_n.get("parent_node_code"):
                                    default_idx = idx_k
                                    break
                            p_choice = st.selectbox(f"調整上層 {req_p} 部門", list(p_dict.keys()), index=default_idx, key="edit_node_parent")
                            upd_parent = p_dict[p_choice]
                        else:
                            st.warning(f"⚠️ 找不到可掛載的 {req_p} 上層部門。")

                    with st.form("saas_edit_node_form"):
                        upd_name = st.text_input("新的顯示名稱（中／英／越文皆可）", value=target_n["node_name"])
                        upd_sort = st.number_input("排序權重", min_value=1, max_value=999, value=int(target_n.get("sort_order") or 100))
                        upd_active = st.checkbox("啟用狀態", value=bool(target_n.get("is_active", True)))
                        st.caption(f"鎖定代碼：`{target_n['node_code']}`（維持既有代碼以確保掛載與歷史單據不中斷）")

                        if st.form_submit_button("💾 儲存修改", type="primary", use_container_width=True):
                            if not upd_name.strip():
                                st.warning("⚠️ 名稱不可為空。")
                            elif req_p and not upd_parent:
                                st.warning(f"⚠️ {upd_tier} 必須指定上層 {req_p}。")
                            else:
                                try:
                                    with engine.begin() as conn:
                                        conn.execute(text("""
                                            UPDATE sys_tenant_org_nodes
                                            SET node_name = :n,
                                                level_tier = :tier,
                                                parent_node_code = :p,
                                                sort_order = :s,
                                                is_active = :act,
                                                updated_at = CURRENT_TIMESTAMP
                                            WHERE tenant_id = :tid AND node_code = :c
                                        """), {
                                            "tid": tenant_id,
                                            "c": target_n["node_code"],
                                            "n": upd_name.strip(),
                                            "tier": upd_tier,
                                            "p": upd_parent,
                                            "s": int(upd_sort),
                                            "act": bool(upd_active),
                                        })
                                    st.success(f"✅ 已更新節點【{upd_name.strip()}】。")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 更新失敗: {e}")

            # --- 停用 / 刪除節點（含子節點防呆與關聯安全檢查）---
            else:
                st.markdown("#### 🗑️ 停用或刪除節點")
                if not all_nodes:
                    st.info("目前沒有可操作的節點。")
                else:
                    del_map = {
                        f"[{n['level_tier']}] {n['node_name']} ({n['node_code']}){'' if n.get('is_active', True) else ' [已停用]'}": n
                        for n in all_nodes
                    }
                    sel_del_lbl = st.selectbox("選擇目標節點", list(del_map.keys()), key="del_node_sel")
                    target_d = del_map[sel_del_lbl]
                    has_children = any(
                        n.get("parent_node_code") == target_d["node_code"] and n.get("is_active", True)
                        for n in all_nodes
                    )

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        toggle_label = "🔴 停用節點" if target_d.get("is_active", True) else "🟢 重新啟用"
                        if st.button(toggle_label, use_container_width=True):
                            if target_d.get("is_active", True) and has_children:
                                st.error("❌ 此節點底下仍有啟用中的下層部門，請先調整或停用下層節點。")
                            else:
                                try:
                                    with engine.begin() as conn:
                                        conn.execute(text("""
                                            UPDATE sys_tenant_org_nodes
                                            SET is_active = :act, updated_at = CURRENT_TIMESTAMP
                                            WHERE tenant_id = :tid AND node_code = :c
                                        """), {
                                            "tid": tenant_id,
                                            "c": target_d["node_code"],
                                            "act": not bool(target_d.get("is_active", True)),
                                        })
                                    st.success("✅ 已更新節點啟用狀態。")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 狀態更新失敗: {e}")

                    with col_b2:
                        confirm_del = st.checkbox("確認永久刪除", key="confirm_perm_del_node")
                        if st.button("🗑️ 永久刪除", use_container_width=True, disabled=not confirm_del):
                            any_child = any(n.get("parent_node_code") == target_d["node_code"] for n in all_nodes)
                            if any_child:
                                st.error("❌ 此節點存在子節點紀錄，為避免資料斷鏈禁止直接刪除；請改用「停用節點」。")
                            else:
                                try:
                                    with engine.begin() as conn:
                                        conn.execute(text("""
                                            DELETE FROM sys_tenant_node_mounts
                                            WHERE tenant_id = :tid AND node_code = :c
                                        """), {"tid": tenant_id, "c": target_d["node_code"]})
                                        conn.execute(text("""
                                            DELETE FROM sys_tenant_org_nodes
                                            WHERE tenant_id = :tid AND node_code = :c
                                        """), {"tid": tenant_id, "c": target_d["node_code"]})
                                    st.success(f"✅ 已刪除節點【{target_d['node_name']}】。")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 刪除失敗: {e}")

    # ------------------------------------------
    # Tab 2：功能拼圖掛載（支援 L1～L4 所有啟用節點）
    # ------------------------------------------
    with tab_mount:
        st.markdown("#### 🧩 為指定 L1～L4 節點掛載功能拼圖")
        if not active_nodes:
            st.info("請先在「1. 組織樹管理（L1～L4）」建立或套用組織節點。")
            return

        node_map = {n["node_code"]: n for n in active_nodes}
        labels = []
        label_to_code = {}
        for n in active_nodes:
            p_code = n.get("parent_node_code")
            p_name = node_map.get(p_code, {}).get("node_name") if p_code else None
            path_prefix = f"{p_name} ➔ " if p_name else ""
            lbl = f"[{n['level_tier']}] {path_prefix}{n['node_name']} ({n['node_code']})"
            labels.append(lbl)
            label_to_code[lbl] = n["node_code"]

        chosen_lbl = st.selectbox("選擇掛載目標節點", labels, key="saas_mount_target")
        target_code = label_to_code[chosen_lbl]
        target_info = node_map[target_code]

        current_feats = []
        current_landing_role = ""
        try:
            with engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT mounted_features, landing_role_code
                    FROM sys_tenant_node_mounts
                    WHERE tenant_id = :tid AND node_code = :c
                """), {"tid": tenant_id, "c": target_code}).fetchone()
                if row:
                    current_feats = [x.strip() for x in str(row[0] or "").split(",") if x.strip()]
                    current_landing_role = row[1] or ""
        except Exception:
            pass

        with st.form(f"saas_mount_form_{target_code}"):
            landing_role = st.text_input(
                "登入後自動直達角色代碼（選填，如 FIELD_ENGINEER / SECURITY_GUARD）",
                value=current_landing_role,
            )
            st.divider()

            grouped = {}
            for item in registry:
                grouped.setdefault(item.get("group") or "通用拼圖", []).append(item)

            selected_keys = []
            for grp_name, items in grouped.items():
                st.markdown(f"**{grp_name}**")
                cols = st.columns(2)
                for idx, feat in enumerate(items):
                    with cols[idx % 2]:
                        if st.checkbox(
                            f"{feat['name']} (`{feat['key']}`)",
                            value=(feat["key"] in current_feats),
                            key=f"mchk_{tenant_id}_{target_code}_{feat['key']}",
                        ):
                            selected_keys.append(feat["key"])

            if st.form_submit_button("💾 儲存並套用拼圖掛載", type="primary", use_container_width=True):
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_tenant_node_mounts (
                                tenant_id, node_code, mounted_features, landing_role_code, updated_at
                            )
                            VALUES (:tid, :c, :feats, :lrole, CURRENT_TIMESTAMP)
                            ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                                mounted_features = EXCLUDED.mounted_features,
                                landing_role_code = EXCLUDED.landing_role_code,
                                updated_at = CURRENT_TIMESTAMP
                        """), {
                            "tid": tenant_id,
                            "c": target_code,
                            "feats": ",".join(selected_keys),
                            "lrole": landing_role.strip().upper() or None,
                        })
                    st.success(f"✅ 已儲存【{target_info['node_name']}】的功能拼圖掛載！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存掛載失敗: {e}")

    # ------------------------------------------
    # Tab 3：註冊新功能拼圖
    # ------------------------------------------
    with tab_reg:
        st.markdown("#### ➕ 註冊新功能拼圖至系統拼圖池")
        with st.form("saas_register_puzzle_form"):
            c1, c2 = st.columns(2)
            with c1:
                fkey = st.text_input("拼圖代碼 (feature_key)", placeholder="例如: feat_warehouse_stock_check")
                fname = st.text_input("拼圖顯示名稱", placeholder="例如: 📦 即時庫存查詢")
            with c2:
                fgroup = st.text_input("功能群組分類", value="擴充拼圖")
                fmod = st.text_input("模組路徑（選填）", placeholder="例如: modules.warehouse.stock_check")

            if st.form_submit_button("🧩 註冊新拼圖", type="primary", use_container_width=True):
                ck = fkey.strip()
                cn = fname.strip()
                if not ck or not cn:
                    st.warning("⚠️ 請填寫拼圖代碼與顯示名稱。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_feature_registry (
                                    feature_key, feature_name, feature_group, module_path, entry_func, is_active
                                )
                                VALUES (:k, :n, :g, :m, 'render', TRUE)
                                ON CONFLICT (feature_key) DO UPDATE SET
                                    feature_name = EXCLUDED.feature_name,
                                    feature_group = EXCLUDED.feature_group,
                                    module_path = COALESCE(:m, sys_feature_registry.module_path),
                                    is_active = TRUE
                            """), {
                                "k": ck,
                                "n": cn,
                                "g": fgroup.strip() or "擴充拼圖",
                                "m": fmod.strip() or None,
                            })
                        st.success(f"✅ 已註冊新拼圖【{cn}】(`{ck}`)！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 註冊拼圖失敗: {e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
