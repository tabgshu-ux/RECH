# ==========================================
# 檔案路徑：modules/management/general_affairs/ga_expenses_hub.py
# 職責：L2 總務／採購 - 總務採購、設備維修與宿舍開銷統一建檔及查詢
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from core import ui_theme
from modules.management.general_affairs.ga_repo import add_ga_expense, ensure_ga_tables, load_ga_items_df


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "GA_Admin"
    project_id = st.session_state.get("active_project_id")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 🛍️ 總務採購、設備維修與宿舍開銷（L2 總務／採購）")
    st.caption("登記與查詢總務採購、設備維修及宿舍開銷，同步連動「管理部總覽」。")
    ensure_ga_tables(engine)

    df = load_ga_items_df(engine, tenant_id)
    pur_sum = float(df[df["expense_type"] == "總務採購"]["amount_vnd"].sum()) if not df.empty else 0.0
    mnt_sum = float(df[df["expense_type"] == "設備維修"]["amount_vnd"].sum()) if not df.empty else 0.0
    drm_sum = float(df[df["expense_type"] == "宿舍開銷"]["amount_vnd"].sum()) if not df.empty else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("總務採購金額", f"{_fmt_vnd(pur_sum)} ₫")
    c2.metric("設備維修金額", f"{_fmt_vnd(mnt_sum)} ₫")
    c3.metric("宿舍開銷金額", f"{_fmt_vnd(drm_sum)} ₫")

    if not df.empty:
        disp = df.copy()
        disp["金額(₫)"] = disp["amount_vnd"].apply(_fmt_vnd)
        disp = disp.rename(columns={
            "item_id": "項目編號",
            "expense_type": "費用類別",
            "item_name": "項目與說明",
            "ref_no": "關聯單號",
            "detail_text": "明細說明",
            "status": "狀態",
        })
        st.dataframe(
            disp[["項目編號", "費用類別", "項目與說明", "金額(₫)", "關聯單號", "明細說明", "狀態"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### ➕ 新增總務開銷項目")
    with st.form("form_ga_hub_add"):
        f1, f2 = st.columns(2)
        with f1:
            exp_type = st.selectbox("費用類別*", ["總務採購", "設備維修", "宿舍開銷"])
            item_name = st.text_input("項目名稱*", placeholder="例：安全帽與勞保用品 / 空壓機檢修 / 宿舍租金水電")
            amount_vnd = st.number_input("金額 (VND)*", min_value=0.0, value=0.0, step=500000.0)
        with f2:
            ref_no = st.text_input("關聯單號", placeholder="例：PR-202611-10 / MNT-01 / DORM-01")
            status = st.selectbox("狀態", ["已核准", "處理中", "本月帳單", "已完成"])
            detail_text = st.text_input("明細說明", placeholder="選填，補充規格或用途")

        if st.form_submit_button("💾 儲存總務開銷", type="primary", use_container_width=True):
            if not item_name.strip():
                st.warning("⚠️ 請填寫項目名稱。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                iid = add_ga_expense(
                    engine, tenant_id, project_id, exp_type, item_name.strip(),
                    float(amount_vnd), ref_no.strip() or None, detail_text.strip() or None,
                    status, user_name, now_vn,
                )
                st.success(f"✅ 已新增【{exp_type}】單號 `{iid}`（{_fmt_vnd(amount_vnd)} ₫）。")
                st.rerun()


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
