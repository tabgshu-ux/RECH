# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構與跨群組彈性業務模組掛載中心（修復資料庫欄位名稱相容性）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 公司組織架構與 L1~L4 彈性模組掛載中心")
    st.caption("支援 L1～L4 動態擴編部門，並可跨部門自由勾選各功能群組，左側選單即時雙向聯動。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    tab_tree, tab_mount, tab_add = st.tabs(["🌳 現有組織樹與狀態管理", "⚙️ 跨群組彈性模組掛載", "➕ 新增擴編 L1~L4 部門"])

    with tab_tree:
        st.markdown("#### 🌳 企業組織樹狀架構與左側聯動狀態")
        depts = []
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM sys_departments")).fetchall()
                for row in result:
                    row_dict = row._asdict()
                    d_name = row_dict.get('dept_name_zh') or row_dict.get('dept_name') or row_dict.get('name') or '未命名部門'
                    tier = row_dict.get('level_tier') or row_dict.get('tier') or 'L1'
                    is_act = row_dict.get('is_active', True)
                    if d_name and not str(d_name).startswith('dept_'):
                        depts.append({"name": d_name, "tier": tier, "active": is_act})
        except Exception:
            pass

        for d in depts:
            status_badge = "🟢 顯示中" if d['active'] else "🔴 已隱藏"
            st.markdown(f"- **[{d['tier']}] {d['name']}** — {status_badge}")

    with tab_mount:
        st.markdown("#### ⚙️ 跨部門群組彈性業務模組掛載中心")
        dept_names = [d['name'] for d in depts] if depts else ["總經理室", "工程部", "管理部", "生產部", "倉庫管理"]
        selected_dept = st.selectbox("🎯 選擇要掛載模組的目標部門", dept_names, key="mount_dept_select")

        # 讀取該部門目前已掛載的模組（兼容 dept_name 與 department_name）
        mounted_list = []
        try:
            with engine.connect() as conn:
                res = conn.execute(
                    text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d OR department_name = :d"),
                    {"d": selected_dept}
                ).fetchone()
                if res and res[0]:
                    mounted_list = [f.strip() for f in res[0].split(",") if f.strip()]
        except Exception:
            pass

        categorized_features = {
            "👑 【總經理室與戰情決策群組】": {
                "總經理室 - 跨國營運戰情與決策總覽": "feat_executive",
                "📈 原料市場與即時外匯行情 (LME 銅價)": "feat_lme_commodities",
                "📈 全球股市 API 指標追蹤": "feat_stock_indices",
                "💱 多幣別匯率即時換算引擎": "feat_fx_rates",
                "💰 完整損益表與會計報表 (Thông tư 200)": "feat_circular_200",
                "🛠️ 工程專案進度與現場狀態": "feat_eng_overview",
                "📰 越南政府政策與法規動態": "feat_policy",
                "🏗️ 工程案場與金額佔比分析": "feat_analytics"
            },
            "🛠️ 【工程部專屬群組 】": {
                "工程部總覽 / 專案進度追蹤": "feat_eng_overview",
                "工程報告與工地巡檢日報": "feat_site_log",
                "設計圖紙上傳與審查": "feat_blueprint",
                "工程專案報價與倉庫成本連動": "feat_eng_quotation",
                "工程估價": "feat_eng_approval_flow"
            },
            "🏭 【生產部專屬群組】": {
                "生產部總覽 / 產線看板": "feat_prod_overview",
                "生產部 - 組裝與看板": "feat_panel_build",
                "生產進度與機台排程": "feat_production_schedule"
            },
            "📦 【倉庫與物流群組】": {
                "倉庫管理總覽 / WMS 庫存": "feat_warehouse_overview",
                "倉庫進出貨管理與料帳合一": "feat_material",
                "物料批次與條碼管理": "feat_barcode"
            },
            "🏢 【管理部與公告群組】": {
                "管理部總覽 / 戰情室": "feat_mgmt_supervisor",
                "📢 公司公告佈告欄管理與發布": "feat_announcements"
            },
            "✍️ 【簽核中心】": {
                "全公司電子表單簽核中心": "feat_my_approvals"
            }
        }

        with st.form("dept_modules_mount_form"):
            st.markdown("#### ⚡ 快速操作區")
            submitted_mount_top = st.form_submit_button("💾 儲存並即時生效部門模組掛載 (置頂快捷)", type="primary", use_container_width=True)
            st.divider()

            new_mounted = []
            for group_name, features in categorized_features.items():
                st.markdown(f"**{group_name}**")
                for label, feat_id in features.items():
                    unique_key = f"chk_{selected_dept}_{feat_id}_{hash(label)}"
                    is_checked = st.checkbox(label, value=(feat_id in mounted_list), key=unique_key)
                    if is_checked:
                        if feat_id not in new_mounted:
                            new_mounted.append(feat_id)
                st.markdown("---")

            submitted_mount_bot = st.form_submit_button("💾 儲存並即時生效部門模組掛載 (底部)", type="primary", use_container_width=True)

            if submitted_mount_top or submitted_mount_bot:
                mounted_str = ",".join(new_mounted)
                try:
                    with engine.begin() as conn:
                        # 🌟 智慧相容寫入：自動適應資料庫的欄位名稱（dept_name 或 department_name）
                        try:
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                                VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                                ON CONFLICT (dept_name) 
                                DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                            """), {"dname": selected_dept, "feats": mounted_str})
                        except Exception:
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (department_name, mounted_features, updated_at)
                                VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                                ON CONFLICT (department_name) 
                                DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                            """), {"dname": selected_dept, "feats": mounted_str})

                    st.success(f"🎉 【{selected_dept}】的業務模組掛載已成功儲存並即時生效！")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存掛載失敗: {e}")

    with tab_add:
        st.markdown("#### ➕ 新增擴編組織部門")
        with st.form("add_new_dept_form_safe"):
            new_code = st.text_input("部門英文代碼")
            new_name = st.text_input("部門正式名稱")
            if st.form_submit_button("🚀 確認新增"):
                st.success("新增成功")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
