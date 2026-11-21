# ==========================================
# 檔案路徑：modules/management/hr/recruitment_vacancies.py
# 職責：L2 行政／人事 - 人員缺額、開價薪資與應徵網址建檔及查詢
# ==========================================

from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_vacancy_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS hr_job_vacancies (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        vacancy_id VARCHAR(64) UNIQUE NOT NULL,
                        dept_name VARCHAR(120) NOT NULL,
                        role_title VARCHAR(160) NOT NULL,
                        openings INT DEFAULT 1,
                        offered_salary VARCHAR(120) NOT NULL,
                        apply_url VARCHAR(255) NOT NULL,
                        status VARCHAR(32) DEFAULT '招募中',
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _load_vacancies(engine, tenant_id: str) -> pd.DataFrame:
    fallback = [
        {
            "vacancy_id": "VAC-ENG-01",
            "dept_name": "工程部／現場組",
            "role_title": "水電／機電工程師 (Kỹ sư Cơ điện)",
            "openings": 2,
            "offered_salary": "18.000.000 - 25.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/mep-engineer",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-PROD-02",
            "dept_name": "生產部／配盤組",
            "role_title": "配電盤組裝與配線技師 (Thợ lắp tủ điện)",
            "openings": 3,
            "offered_salary": "10.000.000 - 15.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/panel-wirer",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-GA-01",
            "dept_name": "管理部／總務採購",
            "role_title": "採購與後勤專員 (Nhân viên Mua hàng)",
            "openings": 1,
            "offered_salary": "12.000.000 - 16.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/procurement",
            "status": "招募中",
        },
    ]
    if not engine:
        return pd.DataFrame(fallback)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT vacancy_id, dept_name, role_title,
                           COALESCE(openings, 1) AS openings,
                           offered_salary, apply_url,
                           COALESCE(status, '招募中') AS status
                    FROM hr_job_vacancies
                    WHERE tenant_id = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            return pd.DataFrame([r._asdict() for r in rows]) if rows else pd.DataFrame(fallback)
    except Exception:
        return pd.DataFrame(fallback)


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "HR_Admin"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    st.markdown("### 📢 人員缺額、開價薪資與應徵網址（L2 行政／人事）")
    st.caption("維護各部門招募缺額、開價薪資與應徵連結，同步顯示於「管理部總覽」。")
    _ensure_vacancy_table(engine)

    df = _load_vacancies(engine, tenant_id)
    c1, c2 = st.columns(2)
    c1.metric("招募職缺數", f"{len(df)} 項")
    c2.metric("徵才缺額總人數", f"{int(df['openings'].sum()) if not df.empty else 0} 人")

    if not df.empty:
        disp = df.rename(columns={
            "vacancy_id": "職缺編號",
            "dept_name": "需求部門",
            "role_title": "職稱／職務",
            "openings": "缺額人數",
            "offered_salary": "開價薪資",
            "apply_url": "應徵網址",
            "status": "狀態",
        })
        st.dataframe(
            disp,
            use_container_width=True,
            hide_index=True,
            column_config={
                "應徵網址": st.column_config.LinkColumn("應徵網址", display_text="開啟應徵頁面"),
            },
        )

    st.divider()
    st.markdown("#### ➕ 新增招募職缺")
    with st.form("form_hr_vacancy"):
        f1, f2 = st.columns(2)
        with f1:
            dept_name = st.text_input("需求部門*", placeholder="例：工程部／現場組")
            role_title = st.text_input("職稱／職務*", placeholder="例：配電盤配線技師 (Thợ lắp tủ điện)")
            openings = st.number_input("缺額人數*", min_value=1, max_value=100, value=1, step=1)
        with f2:
            offered_salary = st.text_input("開價薪資*", placeholder="例：12.000.000 - 16.000.000 ₫ / 月")
            apply_url = st.text_input("應徵網址*", placeholder="https://...")
            status = st.selectbox("招募狀態", ["招募中", "已額滿", "暫停招募"])

        if st.form_submit_button("💾 儲存職缺資訊", type="primary", use_container_width=True):
            if not dept_name.strip() or not role_title.strip() or not offered_salary.strip() or not apply_url.strip():
                st.warning("⚠️ 請完整填寫需求部門、職稱、開價薪資與應徵網址。")
            elif not engine:
                st.error("❌ 尚未連線資料庫。")
            else:
                vid = f"VAC-{now_vn.strftime('%Y%m%d-%H%M%S')}"
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO hr_job_vacancies (
                                    tenant_id, vacancy_id, dept_name, role_title,
                                    openings, offered_salary, apply_url, status,
                                    created_by, created_at
                                )
                                VALUES (
                                    :tid, :vid, :dname, :rtitle,
                                    :openings, :sal, :url, :st,
                                    :cby, :cat
                                )
                            """),
                            {
                                "tid": tenant_id, "vid": vid, "dname": dept_name.strip(),
                                "rtitle": role_title.strip(), "openings": int(openings),
                                "sal": offered_salary.strip(), "url": apply_url.strip(),
                                "st": status, "cby": user_name, "cat": now_vn,
                            },
                        )
                    st.success(f"✅ 已新增職缺 `{vid}`（{role_title.strip()}）。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存職缺失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
