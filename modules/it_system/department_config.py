# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：裕豐標準組織樹管理（L1/L2 層級校準、擴編）與各層級功能模組掛載（雙 Tab 精簡版）
# ==========================================

import streamlit as st
from sqlalchemy import text


# 裕豐電機工業標準組織與 L1 功能入口藍圖
REETECH_STANDARD_ORG = [
    # L1 部門
    {"code": "DEPT_EXEC", "name": "總經理室", "tier": "L1", "parent": None, "type": "DEPT", "sort": 10},
    {"code": "DEPT_ENG", "name": "工程部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 20},
    {"code": "DEPT_MGMT", "name": "管理部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 30},
    {"code": "DEPT_PROD", "name": "生產部", "tier": "L1", "parent": None, "type": "DEPT", "sort": 40},
    # L1 工程部 -> L2
    {"code": "DEPT_ENG_DESIGN", "name": "設計", "tier": "L2", "parent": "DEPT_ENG", "type": "DEPT", "sort": 21},
    # L1 管理部 -> L2
    {"code": "DEPT_MGMT_HR", "name": "行政/人事", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 31},
    {"code": "DEPT_MGMT_GA", "name": "總務/採購", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 32},
    {"code": "DEPT_MGMT_FIN", "name": "財務/會計", "tier": "L2", "parent": "DEPT_MGMT", "type": "DEPT", "sort": 33},
    # L1 生產部 -> L2
    {"code": "DEPT_PROD_SHEET", "name": "板金", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 41},
    {"code": "DEPT_PROD_PAINT", "name": "塗裝", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 42},
    {"code": "DEPT_PROD_PANEL", "name": "配盤", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 43},
    {"code": "DEPT_PROD_WH", "name": "倉庫管理", "tier": "L2", "parent": "DEPT_PROD", "type": "DEPT", "sort": 44},
    # L1 獨立功能入口（同時支援指定角色登入後直接進入）
    {"code": "FUNC_APPROVAL_CENTER", "name": "簽核中心", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 50},
    {"code": "FUNC_FIELD_CLOCKIN", "name": "外勤工程人員線上打卡", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 60},
    {"code": "FUNC_SECURITY_GATE", "name": "保全操作頁面", "tier": "L1", "parent": None, "type": "L1_FUNC", "sort": 70},
]


def _ensure_org_schema(engine):
    """確保組織表與功能掛載表具備完整層級欄位（相容舊表結構）"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_departments (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) DEFAULT 'REETECH_VN',
                    dept_code VARCHAR(80) UNIQUE,
                    dept_name_zh VARCHAR(120) NOT NULL,
                    level_tier VARCHAR(16) DEFAULT 'L1',
                    parent_dept_code VARCHAR(80),
                    node_type VARCHAR(32) DEFAULT 'DEPT',
                    sort_order INT DEFAULT 100,
                    is_active BOOLEAN DEFAULT TRUE,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # 補齊舊表可能缺少的欄位
            for ddl in [
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64) DEFAULT 'REETECH_VN';",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS dept_code VARCHAR(80);",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS dept_name_zh VARCHAR(120);",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS level_tier VARCHAR(16) DEFAULT 'L1';",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS parent_dept_code VARCHAR(80);",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS node_type VARCHAR(32) DEFAULT 'DEPT';",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS sort_order INT DEFAULT 100;",
                "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            ]:
                try:
                    conn.execute(text(ddl))
                except Exception:
                    pass

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_dept_feature_bindings (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(64) DEFAULT 'REETECH_VN',
                    dept_code VARCHAR(80) UNIQUE NOT NULL,
                    dept_name_zh VARCHAR(120) NOT NULL,
                    mounted_features TEXT DEFAULT '',
                    default_landing_role VARCHAR(80),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass


def _sync_reetech_standard_org(engine, tenant_id="REETECH_VN"):
    """依標準藍圖校準 L1/L2 層級，並停用無代碼的重複錯亂舊資料"""
    valid_codes = [item["code"] for item in REETECH_STANDARD_ORG]
    with engine.begin() as conn:
        # 1. 將沒有標準 dept_code 且不在白名單內的錯亂舊資料標記停用，避免重複顯示
        conn.execute(text("""
            UPDATE sys_departments
            SET is_active = FALSE
            WHERE dept_code IS NULL OR dept_code = ''
        """))

        # 2. 寫入或更新標準組織節點
        for item in REETECH_STANDARD_ORG:
            exists = conn.execute(
                text("SELECT id FROM sys_departments WHERE dept_code = :c"),
                {"c": item["code"]},
            ).fetchone()
            if exists:
                conn.execute(text("""
                    UPDATE sys_departments
                    SET tenant_id = :tid,
                        dept_name_zh = :name,
                        level_tier = :tier,
                        parent_dept_code = :parent,
                        node_type = :ntype,
                        sort_order = :sort,
                        is_active = TRUE
                    WHERE dept_code = :c
                """), {
                    "tid": tenant_id,
                    "c": item["code"],
                    "name": item["name"],
                    "tier": item["tier"],
                    "parent": item["parent"],
                    "ntype": item["type"],
                    "sort": item["sort"],
                })
            else:
                conn.execute(text("""
                    INSERT INTO sys_departments (
                        tenant_id, dept_code, dept_name_zh, level_tier,
                        parent_dept_code, node_type, sort_order, is_active
                    )
                    VALUES (:tid, :c, :name, :tier, :parent, :ntype, :sort, TRUE)
                """), {
                    "tid": tenant_id,
                    "c": item["code"],
                    "name": item["name"],
                    "tier": item["tier"],
                    "parent": item["parent"],
                    "ntype": item["type"],
                    "sort": item["sort"],
                })


def _fetch_org_nodes(engine):
    """讀取啟用中的標準化組織節點"""
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT dept_code, dept_name_zh, level_tier, parent_dept_code, node_type, sort_order, is_active
                FROM sys_departments
                WHERE is_active = TRUE AND dept_code IS NOT NULL AND dept_code <> ''
                ORDER BY sort_order ASC, id ASC
            """)).fetchall()
            return [r._asdict() for r in rows]
    except Exception:
        return []


def render(engine=None, lang="zh", **kwargs):
    st.markdown("### 🏢 裕豐公司組織樹與功能掛載中心")
    st.caption("精簡為「組織架構管理」與「功能模組掛載」兩大操作區，支援 L1 部門、L2 子部門卡片與 L1 專屬功能入口。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    _ensure_org_schema(engine)
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    nodes = _fetch_org_nodes(engine)

    tab_org, tab_mount = st.tabs([
        "🌳 1. 組織樹管理與部門擴編",
        "🧩 2. 功能模組掛載設定"
    ])

    # ==========================================
    # Tab 1：組織樹管理與部門擴編
    # ==========================================
    with tab_org:
        col_tree, col_edit = st.columns([1.3, 1])

        with col_tree:
            st.markdown("#### 🌲 目前生效的組織樹狀架構")
            if st.button("🔄 一鍵校準裕豐標準組織樹（清理重複錯亂層級）", type="primary", use_container_width=True):
                try:
                    _sync_reetech_standard_org(engine, tenant_id)
                    st.success("✅ 已校準裕豐標準組織樹，重複與錯置的 L1 項目已自動整理。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 校準失敗: {e}")

            if not nodes:
                st.info("尚未載入標準組織節點，請點擊上方「一鍵校準裕豐標準組織樹」。")
            else:
                l1_nodes = [n for n in nodes if str(n.get("level_tier")).upper() == "L1"]
                l2_nodes = [n for n in nodes if str(n.get("level_tier")).upper() == "L2"]

                for l1 in l1_nodes:
                    badge = "🧭 L1 功能入口" if l1.get("node_type") == "L1_FUNC" else "🏛️ L1 部門"
                    with st.container(border=True):
                        st.markdown(f"**{badge}｜{l1['dept_name_zh']}** (`{l1['dept_code']}`)")
                        children = [c for c in l2_nodes if c.get("parent_dept_code") == l1["dept_code"]]
                        if children:
                            for ch in children:
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↳ 📁 **L2 {ch['dept_name_zh']}** (`{ch['dept_code']}`)")
                        elif l1.get("node_type") == "DEPT":
                            st.caption("（此 L1 部門目前無 L2 子部門）")

        with col_edit:
            st.markdown("#### ➕ 新增 / 擴編部門或 L1 功能入口")
            l1_dept_choices = [n for n in nodes if str(n.get("level_tier")).upper() == "L1" and n.get("node_type") == "DEPT"]
            parent_map = {f"{n['dept_name_zh']} ({n['dept_code']})": n["dept_code"] for n in l1_dept_choices}

            with st.form("org_expand_form"):
                new_tier = st.radio("層級類型", ["L1 一級部門", "L2 二級子部門（部門卡片）", "L1 獨立功能入口"], horizontal=False)
                parent_code = None
                if "L2" in new_tier:
                    if parent_map:
                        chosen_parent = st.selectbox("歸屬上層 L1 部門", list(parent_map.keys()))
                        parent_code = parent_map[chosen_parent]
                    else:
                        st.warning("請先校準或建立 L1 部門。")
                new_code = st.text_input("系統代碼（英文大寫，如 DEPT_ENG_QA）", placeholder="例如: DEPT_ENG_QA")
                new_name = st.text_input("顯示名稱", placeholder="例如: 品保組")
                new_sort = st.number_input("排序權重（數字越小越前面）", min_value=1, max_value=999, value=80)

                if st.form_submit_button("💾 確認寫入組織樹", type="primary", use_container_width=True):
                    clean_code = new_code.strip().upper()
                    clean_name = new_name.strip()
                    if not clean_code or not clean_name:
                        st.warning("⚠️ 請完整填寫系統代碼與顯示名稱。")
                    elif "L2" in new_tier and not parent_code:
                        st.warning("⚠️ L2 子部門必須指定歸屬的上層 L1 部門。")
                    else:
                        tier_val = "L2" if "L2" in new_tier else "L1"
                        ntype_val = "L1_FUNC" if "功能入口" in new_tier else "DEPT"
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_departments (
                                        tenant_id, dept_code, dept_name_zh, level_tier,
                                        parent_dept_code, node_type, sort_order, is_active
                                    )
                                    VALUES (:tid, :c, :name, :tier, :parent, :ntype, :sort, TRUE)
                                    ON CONFLICT (dept_code) DO UPDATE SET
                                        dept_name_zh = EXCLUDED.dept_name_zh,
                                        level_tier = EXCLUDED.level_tier,
                                        parent_dept_code = EXCLUDED.parent_dept_code,
                                        node_type = EXCLUDED.node_type,
                                        sort_order = EXCLUDED.sort_order,
                                        is_active = TRUE
                                """), {
                                    "tid": tenant_id,
                                    "c": clean_code,
                                    "name": clean_name,
                                    "tier": tier_val,
                                    "parent": parent_code,
                                    "ntype": ntype_val,
                                    "sort": int(new_sort),
                                })
                            st.success(f"✅ 已新增/更新【{clean_name}】至組織樹！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 寫入失敗: {e}")

    # ==========================================
    # Tab 2：功能模組掛載設定
    # ==========================================
    with tab_mount:
        st.markdown("#### 🧩 為指定部門、L2 子部門或 L1 功能入口掛載模組")
        if not nodes:
            st.info("請先至「1. 組織樹管理與部門擴編」校準組織樹後，再進行功能掛載。")
            return

        node_lookup = {n["dept_code"]: n for n in nodes}
        display_options = []
        option_to_code = {}
        for n in nodes:
            if n["level_tier"] == "L1":
                prefix = "[L1功能]" if n.get("node_type") == "L1_FUNC" else "[L1部門]"
                label = f"{prefix} {n['dept_name_zh']} ({n['dept_code']})"
            else:
                p_name = node_lookup.get(n.get("parent_dept_code"), {}).get("dept_name_zh", "上層部門")
                label = f"[L2子部門] {p_name} ➔ {n['dept_name_zh']} ({n['dept_code']})"
            display_options.append(label)
            option_to_code[label] = n["dept_code"]

        selected_label = st.selectbox("🎯 選擇要配置功能的目標節點", display_options, key="mount_target_node")
        target_code = option_to_code[selected_label]
        target_node = node_lookup[target_code]

        # 讀取既有掛載
        bound_feats = []
        landing_role = ""
        try:
            with engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT mounted_features, default_landing_role
                    FROM sys_dept_feature_bindings
                    WHERE dept_code = :c
                """), {"c": target_code}).fetchone()
                if row:
                    bound_feats = [x.strip() for x in str(row[0] or "").split(",") if x.strip()]
                    landing_role = row[1] or ""
        except Exception:
            pass

        feature_catalog = {
            "👑 總經理室與決策": {
                "📈 原料市場與即時外匯 (LME 銅價)": "feat_lme_commodities",
                "📊 全球股市與匯率引擎": "feat_fx_rates",
                "💰 完整損益與會計報表 (Thông tư 200)": "feat_circular_200",
                "📰 越南政策與法規動態": "feat_policy",
            },
            "🛠️ 工程與設計 (L1 工程部 / L2 設計)": {
                "📐 估價中心": "feat_eng_quotation",
                "📐 設計圖紙上傳與審查": "feat_blueprint",
                "📋 工地巡檢與施工日報": "feat_site_log",
                "📦 工程 BOM 與採購需求": "feat_bom_procurement",
                "📊 工程專案損益追蹤": "feat_project_pnl",
            },
            "🏭 生產與倉庫 (L1 生產部 / L2 板金·塗裝·配盤·倉庫)": {
                "⚡ 配電盤組裝與產線看板": "feat_panel_build",
                "📅 生產進度與機台排程": "feat_production_schedule",
                "📦 倉庫庫存與進出貨料帳合一": "feat_material",
                "🏷️ 物料批次與條碼管理": "feat_barcode",
            },
            "🏢 管理部 (L2 行政/人事·總務/採購·財務/會計)": {
                "📢 公司公告佈告欄管理": "feat_announcements",
                "👥 員工檔案與考勤薪資 (BHXH)": "feat_hr_employee",
                "🛒 總務採購與應付帳款 (AP)": "feat_ga",
                "📊 財務會計與應收應付 (AR/AP)": "feat_fi",
            },
            "🧭 L1 全廠共用與現場專屬入口": {
                "✍️ 共用簽核中心（請假／採購／文書／估價）": "feat_my_approvals",
                "📍 外勤工程人員線上打卡（支援登入直達）": "feat_field_gps_clockin",
                "🛡️ 保全操作頁面（支援保全登入直達）": "feat_security_guard_ops",
            },
        }

        with st.form(f"bind_features_form_{target_code}"):
            landing_role_input = st.text_input(
                "登入後自動直達此頁面的角色代碼（選填，例如：FIELD_ENGINEER 或 SECURITY_GUARD）",
                value=landing_role,
                placeholder="留空則走一般部門選單；填寫角色代碼可讓該角色登入後直接進入此功能",
            )
            st.divider()

            picked = []
            for grp, items in feature_catalog.items():
                st.markdown(f"**{grp}**")
                c1, c2 = st.columns(2)
                for i, (flabel, fid) in enumerate(items.items()):
                    with (c1 if i % 2 == 0 else c2):
                        if st.checkbox(flabel, value=(fid in bound_feats), key=f"bind_{target_code}_{fid}"):
                            picked.append(fid)

            if st.form_submit_button("💾 儲存功能掛載設定", type="primary", use_container_width=True):
                feat_csv = ",".join(picked)
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_dept_feature_bindings (
                                tenant_id, dept_code, dept_name_zh, mounted_features, default_landing_role, updated_at
                            )
                            VALUES (:tid, :c, :name, :feats, :lrole, CURRENT_TIMESTAMP)
                            ON CONFLICT (dept_code) DO UPDATE SET
                                dept_name_zh = EXCLUDED.dept_name_zh,
                                mounted_features = EXCLUDED.mounted_features,
                                default_landing_role = EXCLUDED.default_landing_role,
                                updated_at = CURRENT_TIMESTAMP
                        """), {
                            "tid": tenant_id,
                            "c": target_code,
                            "name": target_node["dept_name_zh"],
                            "feats": feat_csv,
                            "lrole": landing_role_input.strip().upper() or None,
                        })
                        # 同步寫回舊表 sys_department_modules（相容既有讀取邏輯，避免資料斷鏈）
                        try:
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                                VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                                ON CONFLICT (dept_name) DO UPDATE SET
                                    mounted_features = EXCLUDED.mounted_features,
                                    updated_at = CURRENT_TIMESTAMP
                            """), {"dname": target_node["dept_name_zh"], "feats": feat_csv})
                        except Exception:
                            pass

                    st.success(f"✅ 已儲存【{target_node['dept_name_zh']}】的功能掛載與登入導向設定！")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存失敗: {e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
