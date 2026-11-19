# ==========================================
# 檔案路徑：modules/it_system/org_puzzle/repo.py
# 職責：SaaS 組織樹與拼圖元數據的純資料存取層與多語系自動產碼（無 UI 耦合）
# ==========================================

import hashlib
import re
import unicodedata
from sqlalchemy import text

DEFAULT_PUZZLE_REGISTRY = [
    # 總經理室原有 7 個核心功能拼圖
    {"key": "feat_executive", "name": "👑 跨國營運戰情與決策總覽", "group": "總經理室與戰情決策", "module": "modules.executive.overview", "func": "show"},
    {"key": "feat_lme_commodities", "name": "📈 原料市場與即時外匯行情 (LME 銅價)", "group": "總經理室與戰情決策", "module": "modules.executive.commodities_fx", "func": "show"},
    {"key": "feat_stock_indices", "name": "📊 全球股市 API 指標追蹤", "group": "總經理室與戰情決策", "module": "modules.executive.stock_indices", "func": "show"},
    {"key": "feat_fx_rates", "name": "💱 多幣別匯率即時換算引擎", "group": "總經理室與戰情決策", "module": "modules.executive.fx_rates", "func": "show"},
    {"key": "feat_circular_200", "name": "💰 完整損益表與會計報表 (Thông tư 200)", "group": "總經理室與戰情決策", "module": "modules.executive.financials_pl", "func": "show"},
    {"key": "feat_policy", "name": "📰 越南政府政策與法規動態", "group": "總經理室與戰情決策", "module": "modules.executive.policy_news", "func": "show"},
    {"key": "feat_analytics", "name": "🏗️ 工程案場與金額佔比分析", "group": "總經理室與戰情決策", "module": "modules.executive.project_analytics", "func": "show"},

    # 總經理室 / 營運戰情指標拼圖（原物料價格、應收/應付帳款總計、工程專案進行總數）
    {"key": "feat_raw_material_prices", "name": "🪙 原物料價格監控", "group": "經營指標與帳款總計", "module": "modules.executive.raw_material_prices", "func": "render"},
    {"key": "feat_ar_ap_summary", "name": "💳 財務應收／應付帳款總計 (AR/AP)", "group": "經營指標與帳款總計", "module": "modules.finance.ar_ap_summary", "func": "render"},
    {"key": "feat_active_projects_count", "name": "📌 工程專案進行總數", "group": "經營指標與帳款總計", "module": "modules.engineering.overview.active_projects_kpi", "func": "render"},

    # 工程部與專案拼圖
    {"key": "feat_eng_quotation", "name": "📐 估價中心", "group": "業務與專案", "module": "modules.engineering.financial.quotation", "func": "render"},
    {"key": "feat_site_log", "name": "📋 工地巡檢與施工日報", "group": "現場作業", "module": "modules.engineering.site_ops.daily_report", "func": "render"},
    {"key": "feat_blueprint", "name": "📐 設計圖紙與審查", "group": "設計與品管", "module": "modules.engineering.procurement_qc.testing_acceptance", "func": "render"},
    {"key": "feat_bom_procurement", "name": "📦 工程 BOM 與採購需求", "group": "供應鏈與採購", "module": "modules.engineering.procurement_qc.bom_procurement", "func": "render"},
    {"key": "feat_project_pnl", "name": "📊 專案損益追蹤", "group": "財務與成本", "module": "modules.engineering.financial.project_pnl", "func": "render"},

    # 全公司共用與現場入口拼圖
    {"key": "feat_my_approvals", "name": "✍️ 簽核中心（請假／採購／文書／估價）", "group": "全公司共用", "module": "modules.approval_workflow", "func": "render_approval_center"},
    {"key": "feat_field_gps_clockin", "name": "📍 外勤工程人員線上打卡", "group": "現場作業", "module": "modules.engineering.site_ops.gps_attendance", "func": "render"},
    {"key": "feat_security_guard_ops", "name": "🛡️ 保全操作頁面", "group": "廠區安控", "module": "modules.management.security_gate", "func": "render"},
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
    """依中、英、越文名稱自動產生唯一系統代碼（使用者無需手填）"""
    clean_name = (name or "").strip()
    vn_mapped = clean_name.replace("đ", "d").replace("Đ", "D")
    normalized = unicodedata.normalize("NFD", vn_mapped)
    without_accents = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    ascii_slug = re.sub(r"[^A-Za-z0-9]+", "_", without_accents).strip("_").upper()
    ascii_slug = re.sub(r"_+", "_", ascii_slug)[:14]

    digest_source = f"{tier}|{parent_code or ''}|{node_type}|{clean_name}".encode("utf-8")
    short_hash = hashlib.sha1(digest_source).hexdigest()[:4].upper()
    prefix = "FUNC" if node_type == "L1_FUNC" else (tier or "L1").upper()
    return f"{prefix}_{ascii_slug}_{short_hash}" if ascii_slug else f"{prefix}_NODE_{short_hash}"


def ensure_tables(engine):
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
                    INSERT INTO sys_feature_registry (feature_key, feature_name, feature_group, module_path, entry_func, is_active)
                    VALUES (:k, :n, :g, :m, :f, TRUE)
                    ON CONFLICT (feature_key) DO UPDATE SET
                        feature_group = EXCLUDED.feature_group,
                        module_path = COALESCE(sys_feature_registry.module_path, EXCLUDED.module_path),
                        entry_func = COALESCE(sys_feature_registry.entry_func, EXCLUDED.entry_func),
                        is_active = TRUE
                """), {"k": item["key"], "n": item["name"], "g": item["group"], "m": item["module"], "f": item["func"]})
    except Exception:
        pass


def load_tenant_nodes(engine, tenant_id: str, include_inactive: bool = False) -> list[dict]:
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            sql = "SELECT node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active FROM sys_tenant_org_nodes WHERE tenant_id = :tid"
            if not include_inactive:
                sql += " AND is_active = TRUE"
            sql += " ORDER BY sort_order ASC, id ASC"
            return [r._asdict() for r in conn.execute(text(sql), {"tid": tenant_id}).fetchall()]
    except Exception:
        return []


def upsert_node(engine, tenant_id: str, node_code: str, node_name: str, level_tier: str, parent_code: str | None, node_type: str, sort_order: int, is_active: bool = True):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_tenant_org_nodes (
                tenant_id, node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active, updated_at
            )
            VALUES (:tid, :c, :n, :tier, :p, :nt, :s, :act, CURRENT_TIMESTAMP)
            ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                node_name = EXCLUDED.node_name,
                level_tier = EXCLUDED.level_tier,
                parent_node_code = EXCLUDED.parent_node_code,
                node_type = EXCLUDED.node_type,
                sort_order = EXCLUDED.sort_order,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
        """), {"tid": tenant_id, "c": node_code, "n": node_name, "tier": level_tier, "p": parent_code, "nt": node_type, "s": sort_order, "act": is_active})


def apply_org_template(engine, tenant_id: str, template_items: list[dict]):
    with engine.begin() as conn:
        conn.execute(text("UPDATE sys_tenant_org_nodes SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE tenant_id = :tid"), {"tid": tenant_id})
        for item in template_items:
            conn.execute(text("""
                INSERT INTO sys_tenant_org_nodes (
                    tenant_id, node_code, node_name, level_tier, parent_node_code, node_type, sort_order, is_active, updated_at
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
            """), {"tid": tenant_id, "c": item["code"], "n": item["name"], "tier": item["tier"], "p": item["parent"], "nt": item["type"], "s": item["sort"]})


def delete_node_permanently(engine, tenant_id: str, node_code: str):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM sys_tenant_node_mounts WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code})
        conn.execute(text("DELETE FROM sys_tenant_org_nodes WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code})


def load_registry(engine) -> list[dict]:
    registry = list(DEFAULT_PUZZLE_REGISTRY)
    if not engine:
        return registry
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT feature_key, feature_name, feature_group, module_path, entry_func FROM sys_feature_registry WHERE is_active = TRUE ORDER BY id ASC")).fetchall()
            if rows:
                merged = {}
                for item in registry:
                    merged[item["key"]] = dict(item)
                for r in rows:
                    d = r._asdict()
                    fk = d["feature_key"]
                    base = merged.get(fk, {"key": fk, "name": d["feature_name"], "group": "擴充拼圖", "module": None, "func": "render"})
                    merged[fk] = {
                        "key": fk,
                        "name": d["feature_name"] or base["name"],
                        "group": d.get("feature_group") or base["group"],
                        "module": d.get("module_path") or base["module"],
                        "func": d.get("entry_func") or base["func"],
                    }
                return list(merged.values())
    except Exception:
        pass
    return registry


def load_node_mount(engine, tenant_id: str, node_code: str) -> tuple[list[str], str]:
    try:
        with engine.connect() as conn:
            row = conn.execute(text("SELECT mounted_features, landing_role_code FROM sys_tenant_node_mounts WHERE tenant_id = :tid AND node_code = :c"), {"tid": tenant_id, "c": node_code}).fetchone()
            if row:
                return [x.strip() for x in str(row[0] or "").split(",") if x.strip()], (row[1] or "")
    except Exception:
        pass
    return [], ""


def save_node_mount(engine, tenant_id: str, node_code: str, feature_keys: list[str], landing_role: str | None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_tenant_node_mounts (tenant_id, node_code, mounted_features, landing_role_code, updated_at)
            VALUES (:tid, :c, :feats, :lrole, CURRENT_TIMESTAMP)
            ON CONFLICT (tenant_id, node_code) DO UPDATE SET
                mounted_features = EXCLUDED.mounted_features,
                landing_role_code = EXCLUDED.landing_role_code,
                updated_at = CURRENT_TIMESTAMP
        """), {"tid": tenant_id, "c": node_code, "feats": ",".join(feature_keys), "lrole": landing_role})


def register_puzzle(engine, feature_key: str, feature_name: str, feature_group: str, module_path: str | None):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO sys_feature_registry (feature_key, feature_name, feature_group, module_path, entry_func, is_active)
            VALUES (:k, :n, :g, :m, 'render', TRUE)
            ON CONFLICT (feature_key) DO UPDATE SET
                feature_name = EXCLUDED.feature_name,
                feature_group = EXCLUDED.feature_group,
                module_path = COALESCE(:m, sys_feature_registry.module_path),
                is_active = TRUE
        """), {"k": feature_key, "n": feature_name, "g": feature_group, "m": module_path})
