# ==========================================
# 檔案路徑：modules/management/general_affairs/assets_facilities.py
# 職責：L2 總務／採購 - 固定資產、折舊、耗材、公務車與宿舍開銷管理
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme
from modules.management.general_affairs.ga_repo import add_ga_expense, ensure_ga_tables, load_ga_items_df


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _ensure_assets_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS ga_fixed_assets (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        asset_code VARCHAR(64) UNIQUE NOT NULL,
                        asset_name VARCHAR(160) NOT NULL,
                        asset_group VARCHAR(64) NOT NULL,
                        location_or_plate VARCHAR(120),
                        cost_vnd NUMERIC(18, 2) DEFAULT 0,
                        useful_life_months INT DEFAULT 36,
                        status VARCHAR(32) DEFAULT '使用中',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "GA_Assets"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🏗️ 固定資產、折舊、耗材、公務車與宿舍（L2 總務）")
    st.caption("維護資產台帳與公務車／宿舍／維修／採購開銷，並同步連動「管理部總覽」。")
    ensure_ga_tables(engine)
    _ensure_assets_table(engine)

    df_exp = load_ga_items_df(engine, tenant_id)
    pur_v = float(df_exp[df_exp["expense_type"] == "總務採購"]["amount_vnd"].sum()) if not df_exp.empty else 0.0
    mnt_v = float(df_exp[df_exp["expense_type"] == "設備維修"]["amount_vnd"].sum()) if not df_exp.empty else 0.0
    drm_v = float(df_exp[df_exp["expense_type"] == "宿舍開銷"]["amount_vnd"].sum()) if not df_exp.empty else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("總務採購金額", f"{_fmt_vnd(pur_v)} ₫")
    c2.metric("設備維修金額", f"{_fmt_vnd(mnt_v)} ₫")
    c3.metric("宿舍開銷金額", f"{_fmt_vnd(drm_v)} ₫")

    tab_exp, tab_asset = st.tabs(["💰 採購／維修／宿舍開銷登記", "🏛️ 固定資產與公務車台帳"])

    with tab_exp:
        if not df_exp.empty:
            disp_e = df_exp.copy()
            disp_e["金額(₫)"] = disp_e["amount_vnd"].apply(_fmt_vnd)
            st.dataframe(
                disp_e.rename(columns={"item_id": "單號", "expense_type": "類別", "item_name": "項目", "ref_no": "單號/車牌", "status": "狀態"})[
                    ["單號", "類別", "項目", "金額(₫)", "單號/車牌", "狀態"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with st.form("form_ga_assets_exp"):
            f1, f2 = st.columns(2)
            with f1:
                etype = st.selectbox("費用類別*", ["總務採購", "設備維修", "宿舍開銷"])
                iname = st.text_input("項目名稱*", placeholder="例：公務車保養／宿舍水電／耗材採購")
                amt = st.number_input("金額 (VND)*", min_value=0.0, value=0.0, step=500000.0)
            with f2:
                rno = st.text_input("關聯單號／車牌", placeholder="例：61C-452.18 或 PR-01")
                st_val = st.selectbox("狀態", ["已核准", "處理中", "本月帳單", "已完成"])
                dtxt = st.text_input("備註", placeholder="選填")

            if st.form_submit_button("💾 儲存開銷紀錄", type="primary", use_container_width=True):
                if not iname.strip():
                    st.warning("⚠️ 請填寫項目名稱。")
                elif not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    iid = add_ga_expense(engine, tenant_id, project_id, etype, iname.strip(), float(amt), rno.strip() or None, dtxt.strip() or None, st_val, user_name, now_vn)
                    st.success(f"✅ 已新增開銷單 `{iid}`（{_fmt_vnd(amt)} ₫）。")
                    st.rerun()

    with tab_asset:
        assets_df = pd.DataFrame()
        if engine:
            try:
                with engine.connect() as conn:
                    rows = conn.execute(
                        text("""
                            SELECT asset_code, asset_name, asset_group,
                                   COALESCE(location_or_plate, '-') AS location_or_plate,
                                   COALESCE(cost_vnd, 0) AS cost_vnd,
                                   COALESCE(useful_life_months, 36) AS useful_life_months,
                                   COALESCE(status, '使用中') AS status
                            FROM ga_fixed_assets WHERE tenant_id = :tid ORDER BY id DESC
                        """),
                        {"tid": tenant_id},
                    ).fetchall()
                    if rows:
                        assets_df = pd.DataFrame([r._asdict() for r in rows])
            except Exception:
                pass

        if assets_df.empty:
            st.info("目前尚無固定資產／公務車建檔紀錄，可於下方新增。")
        else:
            disp_a = assets_df.copy()
            disp_a["原值(₫)"] = disp_a["cost_vnd"].apply(_fmt_vnd)
            disp_a["月折舊估算(₫)"] = (disp_a["cost_vnd"] / disp_a["useful_life_months"].replace(0, 36)).apply(_fmt_vnd)
            st.dataframe(
                disp_a.rename(columns={"asset_code": "資產編號", "asset_name": "名稱", "asset_group": "類別", "location_or_plate": "位置/車牌", "useful_life_months": "耐用月數", "status": "狀態"})[
                    ["資產編號", "名稱", "類別", "位置/車牌", "原值(₫)", "耐用月數", "月折舊估算(₫)", "狀態"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with st.form("form_ga_fixed_asset"):
            a1, a2, a3 = st.columns(3)
            with a1:
                acode = st.text_input("資產編號*", value=f"AST-{now_vn.strftime('%m%d-%H%M')}")
                aname = st.text_input("資產／車輛名稱*", placeholder="例：公務貨車 / 折床設備")
            with a2:
                agroup = st.selectbox("資產類別*", ["公務車輛", "廠務設備", "宿舍設備", "辦公設備"])
                loc_plate = st.text_input("存放位置／車牌號碼", placeholder="例：西寧廠 或 61C-452.18")
            with a3:
                cost_v = st.number_input("取得原值 (VND)*", min_value=0.0, value=0.0, step=1000000.0)
                life_m = st.number_input("耐用月數*", min_value=1, max_value=240, value=36, step=1)

            if st.form_submit_button("💾 新增資產紀錄", type="primary", use_container_width=True):
                if not aname.strip() or not engine:
                    st.warning("⚠️ 請填寫資產名稱並確認已連線資料庫。")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    INSERT INTO ga_fixed_assets (
                                        tenant_id, asset_code, asset_name, asset_group,
                                        location_or_plate, cost_vnd, useful_life_months, status
                                    )
                                    VALUES (:tid, :ac, :an, :ag, :lp, :cv, :lm, '使用中')
                                """),
                                {
                                    "tid": tenant_id, "ac": acode.strip(), "an": aname.strip(),
                                    "ag": agroup, "lp": loc_plate.strip() or None,
                                    "cv": float(cost_v), "lm": int(life_m),
                                },
                            )
                        st.success(f"✅ 已新增資產 `{acode.strip()}`。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增資產失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
