# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：多租戶 SaaS 拼圖掛載中心（註冊表驅動 + 租戶隔離，不寫死單一公司業務邏輯）
# ==========================================

import streamlit as st
from sqlalchemy import text


# 系統拼圖池（可由資料庫 sys_feature_registry 擴充；新增拼圖只需在此或資料表註冊 feature_key）
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

# 可選套用的組織模板（僅供初始化或一鍵套用，不寫死於畫面渲染）
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

            # 將預設拼圖池同步註冊進 sys_feature_registry（保留客戶自訂名稱）
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
    """從拼圖註冊表讀取所有可用功能拼圖"""
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


def _load_tenant_nodes(engine, tenant_id):
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT node_code, node_name, level_tier, parent_node_code, node_type, sort_order
                FROM sys_tenant_org_nodes
                WHERE tenant_id = :tid AND is_active = TRUE
                ORDER BY sort_order ASC, id ASC
            """), {"tid": tenant_id}).fetchall()
            return [r._asdict() for r in rows]
    except Exception:
        return []


def _apply_template(engine, tenant_id, template_items):
    """套用組織模板時以 tenant_id + node_code 精準更新，避免重複髒資料"""
    valid_codes = [x["code"] for x in template_items]
    with engine.begin() as conn:
        # 停用該租戶不在模板內的舊節點（保留歷史紀錄不斷表）
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


def render(engine=None, lang="zh", **kwargs):
    st.markdown("### 🧩 SaaS 組織與功能拼圖設定中心")
    st.caption("所有功能拼圖與部門層級皆由元數據驅動，可在系統端自由分配 L1／L2 與掛載功能，無需修改業務程式碼。")

    if not engine:
        st.warning("⚠️ 尚未連線資料庫引擎。")
        return

    _ensure_saas_metadata_tables(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    st.caption(f"目前租戶：`{tenant_id}`")

    nodes = _load_tenant_nodes(engine, tenant_id)
    registry = _load_registry(engine)

    tab_org, tab_mount, tab_reg = st.tabs([
        "🌳 1. 組織與卡片結構",
        "🧩 2. 功能拼圖掛載",
        "➕ 3. 註冊新功能拼圖"
    ])

    # ------------------------------------------
    # Tab 1：組織與卡片結構（含模板套用與動態新增 L1/L2）
    # ------------------------------------------
    with tab_org:
        col_left, col_right = st.columns([1.3, 1])

        with col_left:
            st.markdown("#### 🌲 租戶組織樹狀結構")
            chosen_tpl = st.selectbox("選擇套用組織模板", list(ORG_TEMPLATES.keys()), key="saas_tpl_select")
            if st.button("📥 套用／校準此組織模板", type="primary", use_container_width=True):
                try:
                    _apply_template(engine, tenant_id, ORG_TEMPLATES[chosen_tpl])
                    st.success(f"✅ 已為租戶 `{tenant_id}` 套用【{chosen_tpl}】。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 套用模板失敗: {e}")

            if not nodes:
                st.info("目前尚未建立此租戶的組織節點，請點擊上方「套用／校準此組織模板」或於右側新增。")
            else:
                l1_list = [n for n in nodes if str(n.get("level_tier")).upper() == "L1"]
                l2_list = [n for n in nodes if str(n.get("level_tier")).upper() == "L2"]

                for l1 in l1_list:
                    tag = "🧭 L1 功能入口" if l1.get("node_type") == "L1_FUNC" else "🏛️ L1 部門"
                    with st.container(border=True):
                        st.markdown(f"**{tag}｜{l1['node_name']}** (`{l1['node_code']}`)")
                        subs = [s for s in l2_list if s.get("parent_node_code") == l1["node_code"]]
                        for sub in subs:
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ 🗂️ **L2 {sub['node_name']}** (`{sub['node_code']}`)")

        with col_right:
            st.markdown("#### ➕ 新增／調整部門或 L2 卡片")
            l1_depts = [n for n in nodes if str(n.get("level_tier")).upper() == "L1" and n.get("node_type") == "DEPT"]
            parent_opts = {f"{n['node_name']} ({n['node_code']})": n["node_code"] for n in l1_depts}

            with st.form("saas_add_node_form"):
                tier_choice = st.radio("節點層級", ["L1 部門", "L2 子部門／卡片", "L1 功能入口"])
                parent_val = None
                if "L2" in tier_choice:
                    if parent_opts:
                        p_sel = st.selectbox("歸屬 L1 部門", list(parent_opts.keys()))
                        parent_val = parent_opts[p_sel]
                    else:
                        st.warning("請先建立至少一個 L1 部門。")

                node_code = st.text_input("節點代碼", placeholder="例如: DEPT_ENG_QC")
                node_name = st.text_input("顯示名稱", placeholder="例如: 測試與品管卡片")
                sort_ord = st.number_input("排序", min_value=1, max_value=999, value=90)

                if st.form_submit_button("💾 儲存節點", type="primary", use_container_width=True):
                    c_code = node_code.strip().upper()
                    c_name = node_name.strip()
                    if not c_code or not c_name:
                        st.warning("⚠️ 請填寫節點代碼與顯示名稱。")
                    elif "L2" in tier_choice and not parent_val:
                        st.warning("⚠️ L2 子部門／卡片必須選擇歸屬的 L1 部門。")
                    else:
                        t_val = "L2" if "L2" in tier_choice else "L1"
                        nt_val = "L1_FUNC" if "功能入口" in tier_choice else "DEPT"
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
                                    "c": c_code,
                                    "n": c_name,
                                    "tier": t_val,
                                    "p": parent_val,
                                    "nt": nt_val,
                                    "s": int(sort_ord),
                                })
                            st.success(f"✅ 已儲存節點【{c_name}】。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 儲存節點失敗: {e}")

    # ------------------------------------------
    # Tab 2：功能拼圖掛載（選 L1 或 L2 節點，掛載註冊表中的功能）
    # ------------------------------------------
    with tab_mount:
        st.markdown("#### 🧩 為指定 L1 部門、L2 卡片或 L1 入口掛載功能拼圖")
        if not nodes:
            st.info("請先在「1. 組織與卡片結構」建立或套用組織節點。")
            return

        node_map = {n["node_code"]: n for n in nodes}
        labels = []
        label_to_code = {}
        for n in nodes:
            if n["level_tier"] == "L1":
                lbl = f"{'[L1入口]' if n.get('node_type') == 'L1_FUNC' else '[L1部門]'} {n['node_name']} ({n['node_code']})"
            else:
                pname = node_map.get(n.get("parent_node_code"), {}).get("node_name", "上層")
                lbl = f"[L2卡片] {pname} ➔ {n['node_name']} ({n['node_code']})"
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
    # Tab 3：註冊新功能拼圖（無須改掛載清單程式碼即可新增拼圖項目）
    # ------------------------------------------
    with tab_reg:
        st.markdown("#### ➕ 註冊新功能拼圖至系統拼圖池")
        st.caption("新增後，所有租戶的「2. 功能拼圖掛載」都會自動出現此功能，可依需求分配給不同部門或卡片。")
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
