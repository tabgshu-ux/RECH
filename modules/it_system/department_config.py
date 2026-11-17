# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構與跨群組彈性業務模組掛載中心（純元數據動態驅動 + 頂部快捷儲存免捲動）
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

    # ==========================================
    # 分頁一：組織樹檢視與狀態控制
    # ==========================================
    with tab_tree:
        st.markdown("#### 🌳 企業組織樹狀架構與左側聯動狀態")
        
        depts = []
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM sys_departments")).fetchall()
                for row in result:
                    row_dict = row._asdict()
                    d_code = row_dict.get('dept_code') or row_dict.get('code') or str(row_dict.get('id', ''))
                    d_name = row_dict.get('dept_name_zh') or row_dict.get('dept_name') or row_dict.get('name') or row_dict.get('title') or '未命名部門'
                    tier = row_dict.get('level_tier') or row_dict.get('tier') or 'L1'
                    is_act = row_dict.get('is_active', True)
                    if is_act is None: is_act = True
                    
                    if d_name and str(d_name).strip() and not str(d_name).startswith('dept_'):
                        depts.append({"id": row_dict.get('id'), "code": d_code, "name": d_name, "tier": tier, "active": is_act})
        except Exception as e:
            st.error(f"讀取部門資料發生異常: {e}")

        if depts:
            for d in depts:
                status_badge = "🟢 顯示中 (Active)" if d['active'] else "🔴 已隱藏 (Disabled)"
                with st.expander(f"[{d['tier']}] {d['name']} (代碼: {d['code']}) — {status_badge}"):
                    st.markdown(f"**部門名稱:** {d['name']} | **層級:** {d['tier']}")
        else:
            st.info("💡 目前資料庫中尚無有效部門資料，請至右側「新增擴編部門」建立。")

    # ==========================================
    # 分頁二：跨群組彈性業務模組動態掛載
    # ==========================================
    with tab_mount:
        st.markdown("#### ⚙️ 跨部門群組彈性業務模組掛載中心")
        
        dept_names = [d['name'] for d in depts] if depts else ["總經理室", "工程部", "管理部", "生產部", "倉庫管理"]
        selected_dept = st.selectbox("🎯 選擇要掛載模組的目標部門", dept_names, key="mount_dept_select")

        # 讀取該部門目前已掛載的模組
        mounted_list = []
        try:
            with engine.connect() as conn:
                res = conn.execute(
                    text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d"),
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
            "🛠️ 【工程部專屬群組】": {
                "工程部總覽 / 專案進度追蹤": "feat_eng_overview",
                "工程報告與工地巡檢日報": "feat_site_log",
                "設計圖紙上傳與審查": "feat_blueprint"
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
            "📁 【行政人事群組】": {
                "人事行政課 - 員工檔案與履約管理": "feat_hr_employee",
                "人事行政課 - 考勤與打卡紀錄": "feat_hr_attendance",
                "人事行政課 - 薪資計算與 BHXH 保險": "feat_hr_payroll",
                "外勤油費與外出補助津貼管理": "feat_allowance"
            },
            "📂 【總務後勤群組】": {
                "總務採購課 - 採購單與應付帳款 (AP)": "feat_ga",
                "🛂 總務後勤 - 台幹證件與生活支援 (Expat Support)": "feat_ga_expat",
                "🧯 總務後勤 - 廠務設施與 EHS 環安衛合規": "feat_ga_ehs",
                "🍲 總務後勤 - 越籍員工食堂團膳與門禁秩序": "feat_ga_canteen",
                "🏛️ 總務後勤 - MRO 採購與政府公關 (PR)": "feat_ga_mro"
            },
            "💰 【財務會計群組】": {
                "財務會計課 - 應收帳款管理 (AR) 與財報": "feat_fi",
                "越南 Thông tư 200 標準財務報告": "feat_circular_200"
            },
            "✍️ 【簽核中心】": {
                "全公司電子表單簽核中心": "feat_my_approvals"
            }
        }

        with st.form("dept_modules_mount_form"):
            # 🌟 貼心優化：把儲存按鈕放在頂部，免去您捲動到手指發炎的痛苦！
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
                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                            VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                            ON CONFLICT (dept_name) 
                            DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                        """), {"dname": selected_dept, "feats": mounted_str})
                        conn.commit()

                    st.success(f"🎉 【{selected_dept}】的業務模組掛載已成功儲存並即時生效！")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存掛載失敗: {e}")

    # ==========================================
    # 分頁三：新增擴編 L1~L4 部門
    # ==========================================
    with tab_add:
        st.markdown("#### ➕ 新增擴編組織部門 (支援 L1～L4 層級)")
        
        with st.form("add_new_dept_form_safe"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_code = st.text_input("部門英文代碼 (例如: EXEC, ENG)", placeholder="請輸入唯一代碼")
                new_name = st.text_input("部門正式名稱 (例如: 總經理室 / 工程部總覽)", placeholder="請輸入部門名稱")
            with col_b:
                parent_opt = st.selectbox("上級所屬部門", ["總公司"] + [d['name'] for d in depts])
                tier_opt = st.selectbox("組織層級 (Tier)", ["L1 (一級大部門)", "L2 (二級子部門/課)", "L3 (三級分組)", "L4 (四級小組)"])

            submitted_create = st.form_submit_button("🚀 確認新增擴編部門", type="primary", use_container_width=True)

            if submitted_create:
                if new_code and new_name:
                    try:
                        tier_code = tier_opt.split(" ")[0]
                        with engine.connect() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_departments (dept_code, dept_name_zh, dept_name, name, parent_dept, level_tier, is_active)
                                VALUES (:code, :name, :name, :name, :parent, :tier, TRUE)
                                ON CONFLICT (dept_code) DO UPDATE 
                                SET dept_name_zh = :name, dept_name = :name, name = :name, parent_dept = :parent, level_tier = :tier, is_active = TRUE
                            """), {
                                "code": new_code.upper().strip(),
                                "name": new_name.strip(),
                                "parent": parent_opt,
                                "tier": tier_code
                            })
                            conn.commit()
                        st.success(f"🎉 成功新增擴編部門：[{tier_code}] {new_name.strip()}！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫部門代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
