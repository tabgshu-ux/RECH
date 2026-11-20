# ==========================================
# 檔案路徑：modules/engineering/compliance/cert_registry.py
# 職責：工程部 - 外包公司與工程人員證照管理（建檔、效期提醒與篩選）
# ==========================================

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_cert_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS eng_cert_registry (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        project_id VARCHAR(80),
                        holder_type VARCHAR(32) NOT NULL,
                        holder_name VARCHAR(160) NOT NULL,
                        org_or_dept VARCHAR(160),
                        cert_name VARCHAR(160) NOT NULL,
                        cert_no VARCHAR(100),
                        issued_date DATE,
                        expiry_date DATE,
                        notes TEXT,
                        updated_by VARCHAR(100),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _calc_validity(exp_val, today_d: date) -> str:
    if not exp_val:
        return "長期有效"
    try:
        exp_d = exp_val if isinstance(exp_val, date) else date.fromisoformat(str(exp_val)[:10])
    except Exception:
        return "未設定效期"
    days_left = (exp_d - today_d).days
    if days_left < 0:
        return f"🚨 已逾期 ({abs(days_left)} 天)"
    if days_left <= 30:
        return f"⚠️ 即將到期 ({days_left} 天)"
    return "✅ 效期正常"


def _load_certs(engine, tenant_id: str, today_d: date) -> pd.DataFrame:
    fallback = [
        {
            "project_id": "PRJ-2026-01",
            "holder_type": "SUBCON_COMPANY",
            "holder_name": "Công Ty TNHH Cơ Điện Tây Ninh",
            "org_or_dept": "外包商 SUB-01",
            "cert_name": "甲級電器承裝／機電施工資格",
            "cert_no": "CERT-VN-88412",
            "issued_date": "2025-01-15",
            "expiry_date": "2027-01-14",
            "validity_status": "✅ 效期正常",
            "notes": "負責西寧廠區配電盤安裝與測試",
        },
        {
            "project_id": "PRJ-2026-01",
            "holder_type": "ENGINEER",
            "holder_name": "Nguyễn Văn Minh",
            "org_or_dept": "工程部／現場組",
            "cert_name": "高空作業與電氣安全訓練證書",
            "cert_no": "ATLD-2026-0319",
            "issued_date": "2025-12-01",
            "expiry_date": "2026-12-01",
            "validity_status": "⚠️ 即將到期 (11 天)",
            "notes": "須於到期前完成複訓換證",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(project_id, '-') AS project_id,
                           holder_type,
                           holder_name,
                           COALESCE(org_or_dept, '-') AS org_or_dept,
                           cert_name,
                           COALESCE(cert_no, '-') AS cert_no,
                           TO_CHAR(issued_date, 'YYYY-MM-DD') AS issued_date,
                           TO_CHAR(expiry_date, 'YYYY-MM-DD') AS expiry_date,
                           COALESCE(notes, '-') AS notes
                    FROM eng_cert_registry
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if not rows:
                return pd.DataFrame(fallback)
            out = []
            for r in rows:
                d = r._asdict()
                d["validity_status"] = _calc_validity(d.get("expiry_date"), today_d)
                out.append(d)
            return pd.DataFrame(out)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "Eng_Admin"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    today_d = now_vn.date()

    st.markdown("### 🪪 外包公司與工程人員證照管理")
    st.caption("登記外包商資格與工程人員安衛／專業證照，自動標示即將到期（30 天內）與已逾期證照。")
    _ensure_cert_table(engine)

    df = _load_certs(engine, tenant_id, today_d)

    type_filter = st.selectbox(
        "篩選對象類別",
        ["ALL", "SUBCON_COMPANY", "ENGINEER"],
        format_func=lambda x: {
            "ALL": "全部（外包公司＋工程人員）",
            "SUBCON_COMPANY": "🏗️ 外包公司",
            "ENGINEER": "👷 工程人員",
        }[x],
    )

    view_df = df if type_filter == "ALL" else df[df["holder_type"] == type_filter]

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("建檔證照總數", f"{len(df)} 筆")
    c_m2.metric("即將到期 (≤30天)", f"{int(df['validity_status'].str.contains('即將到期').sum())} 筆")
    c_m3.metric("已逾期", f"{int(df['validity_status'].str.contains('已逾期').sum())} 筆")

    if view_df.empty:
        st.info("目前無符合篩選條件的證照紀錄。")
    else:
        disp = view_df.rename(columns={
            "project_id": "專案編號",
            "holder_type": "類別",
            "holder_name": "公司／人員名稱",
            "org_or_dept": "所屬單位／部門",
            "cert_name": "證照／資格名稱",
            "cert_no": "證照編號",
            "issued_date": "發證日期",
            "expiry_date": "到期日期",
            "validity_status": "效期狀態",
            "notes": "備註",
        })
        st.dataframe(disp, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### ➕ 新增外包公司或工程人員證照")

    with st.form("form_eng_cert_registry"):
        c1, c2 = st.columns(2)
        with c1:
            htype = st.selectbox(
                "對象類別*",
                [("SUBCON_COMPANY", "🏗️ 外包公司"), ("ENGINEER", "👷 工程人員")],
                format_func=lambda x: x[1],
            )[0]
            hname = st.text_input("外包公司名稱或工程人員姓名*", placeholder="例：Công Ty TNHH... 或 Nguyễn Văn A")
            org_dept = st.text_input("所屬外包商／部門", placeholder="例：工程部／外包商 SUB-02")
            pid = st.text_input("關聯專案編號 (project_id)", value=st.session_state.get("active_project_id") or "PRJ-2026-01")
        with c2:
            cname = st.text_input("證照／安衛資格名稱*", placeholder="例：電氣安全證書／高空作業證")
            cno = st.text_input("證照編號", placeholder="例：CERT-2026-001")
            issued_d = st.date_input("發證日期", value=today_d)
            has_exp = st.checkbox("設定到期日", value=True)
            exp_d = st.date_input("到期日期", value=today_d + timedelta(days=365))

        notes = st.text_area("備註（施工限制／複訓提醒）", placeholder="例：限西寧與平陽案場使用")

        if st.form_submit_button("💾 儲存證照紀錄", type="primary", use_container_width=True):
            if not hname.strip() or not cname.strip():
                st.warning("⚠️ 請填寫外包公司／人員名稱與證照名稱。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO eng_cert_registry (
                                    tenant_id, project_id, holder_type, holder_name,
                                    org_or_dept, cert_name, cert_no, issued_date,
                                    expiry_date, notes, updated_by, updated_at
                                )
                                VALUES (
                                    :tid, :pid, :htype, :hname,
                                    :odept, :cname, :cno, :idate,
                                    :edate, :notes, :uby, :uat
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "pid": pid.strip() or None,
                                "htype": htype,
                                "hname": hname.strip(),
                                "odept": org_dept.strip() or None,
                                "cname": cname.strip(),
                                "cno": cno.strip() or None,
                                "idate": issued_d,
                                "edate": exp_d if has_exp else None,
                                "notes": notes.strip() or None,
                                "uby": user_name,
                                "uat": now_vn,
                            },
                        )
                    st.success(f"✅ 已儲存【{hname.strip()}】的證照「{cname.strip()}」。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存證照失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
