# ==========================================
# 檔案路徑：modules/management/hr/recruitment_vacancies.py
# 職責：L2 行政／人事 - 需應徵人員、缺額數量與建立應徵網頁資訊（同步連動管理部總覽）
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
                        job_desc TEXT,
                        status VARCHAR(32) DEFAULT '招募中',
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(
                text("ALTER TABLE hr_job_vacancies ADD COLUMN IF NOT EXISTS job_desc TEXT;")
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
            "job_desc": "負責西寧與平陽案場機電配管、配電盤安裝與現場監造。",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-PROD-02",
            "dept_name": "生產部／配盤組",
            "role_title": "配電盤組裝與配線技師 (Thợ lắp tủ điện)",
            "openings": 3,
            "offered_salary": "10.000.000 - 15.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/panel-wirer",
            "job_desc": "看懂電氣單線圖與控制迴路圖，進行高低壓配電盤配線。",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-GA-01",
            "dept_name": "管理部／總務採購",
            "role_title": "採購與後勤專員 (Nhân viên Mua hàng)",
            "openings": 1,
            "offered_salary": "12.000.000 - 16.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/procurement",
            "job_desc": "負責廠區工程材料詢價、採購追蹤與總務後勤支援。",
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
                           COALESCE(job_desc, '-') AS job_desc,
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

    st.markdown("### 📢 需應徵人員、缺額數量與建立應徵網頁資訊")
    st.caption("建立與維護各部門招募職缺、需求人數、開價薪資與應徵網頁連結，同步即時顯示於「管理部總覽」。")
    _ensure_vacancy_table(engine)

    df = _load_vacancies(engine, tenant_id)
    active_df = df[df["status"] == "招募中"] if not df.empty else df

    c1, c2, c3 = st.columns(3)
    c1.metric("目前招募中職缺", f"{len(active_df)} 項")
    c2.metric("尚需應徵總人數", f"{int(active_df['openings'].sum()) if not active_df.empty else 0} 人")
    c3.metric("已建立應徵網頁", f"{len(df)} 頁")

    if not df.empty:
        disp = df.rename(columns={
            "vacancy_id": "職缺編號",
            "dept_name": "需求部門",
            "role_title": "需應徵職稱",
            "openings": "需求人數",
            "offered_salary": "開價薪資",
            "apply_url": "應徵網頁連結",
            "job_desc": "工作內容與條件",
            "status": "招募狀態",
        })
        st.dataframe(
            disp,
            use_container_width=True,
            hide_index=True,
            column_config={
                "應徵網頁連結": st.column_config.LinkColumn("應徵網頁連結", display_text="開啟應徵網頁"),
            },
        )

    st.divider()
    tab_add, tab_edit = st.tabs(["➕ 建立新應徵職缺與應徵網頁", "✏️ 更新缺額人數／招募狀態"])

    with tab_add:
        with st.form("form_hr_vacancy_create"):
            f1, f2 = st.columns(2)
            with f1:
                dept_name = st.text_input("需求部門*", placeholder="例：工程部／現場組")
                role_title = st.text_input("需應徵人員職稱*", placeholder="例：水電／機電工程師 (Kỹ sư Cơ điện)")
                openings = st.number_input("需應徵人數*", min_value=1, max_value=200, value=1, step=1)
            with f2:
                offered_salary = st.text_input("開價薪資範圍*", placeholder="例：15.000.000 - 22.000.000 ₫ / 月")
                apply_url = st.text_input(
                    "應徵網頁網址 (URL)*",
                    placeholder="例：https://forms.gle/... 或公司招募網頁網址",
                )
                status = st.selectbox("招募狀態", ["招募中", "已額滿", "暫停招募"])

            job_desc = st.text_area(
                "應徵網頁工作內容與條件說明*",
                placeholder="例：1. 具備工業配電或水電工程經驗 2 年以上\n2. 工作地點：越南西寧廠／平陽案場\n3. 享社保、宿舍與餐費津貼",
            )

            if st.form_submit_button("💾 建立職缺並發布應徵網頁資訊", type="primary", use_container_width=True):
                if not dept_name.strip() or not role_title.strip() or not offered_salary.strip() or not apply_url.strip():
                    st.warning("⚠️ 請完整填寫需求部門、職稱、開價薪資與應徵網頁網址。")
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
                                        openings, offered_salary, apply_url, job_desc,
                                        status, created_by, created_at
                                    )
                                    VALUES (
                                        :tid, :vid, :dname, :rtitle,
                                        :openings, :sal, :url, :jdesc,
                                        :st, :cby, :cat
                                    )
                                """),
                                {
                                    "tid": tenant_id,
                                    "vid": vid,
                                    "dname": dept_name.strip(),
                                    "rtitle": role_title.strip(),
                                    "openings": int(openings),
                                    "sal": offered_salary.strip(),
                                    "url": apply_url.strip(),
                                    "jdesc": job_desc.strip() or "-",
                                    "st": status,
                                    "cby": user_name,
                                    "cat": now_vn,
                                },
                            )
                        st.success(f"✅ 已建立職缺 `{vid}`（{role_title.strip()}，需求 {int(openings)} 人），並同步至管理部總覽。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 建立職缺失敗：{e}")

    with tab_edit:
        if df.empty or not engine:
            st.info("目前無可更新的資料庫職缺紀錄。")
        else:
            options = {f"{r['vacancy_id']}｜{r['role_title']}（目前 {r['openings']} 人／{r['status']}）": r for _, r in df.iterrows()}
            sel_label = st.selectbox("選擇要調整的職缺", list(options.keys()))
            target = options[sel_label]
            with st.form("form_hr_vacancy_update"):
                u1, u2 = st.columns(2)
                with u1:
                    new_openings = st.number_input("調整後需求人數", min_value=0, max_value=200, value=int(target["openings"]), step=1)
                    new_salary = st.text_input("調整後開價薪資", value=str(target["offered_salary"]))
                with u2:
                    new_url = st.text_input("調整後應徵網頁網址", value=str(target["apply_url"]))
                    st_list = ["招募中", "已額滿", "暫停招募"]
                    st_idx = st_list.index(target["status"]) if target["status"] in st_list else 0
                    new_status = st.selectbox("招募狀態", st_list, index=st_idx)

                if st.form_submit_button("💾 更新職缺資訊", type="primary", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    UPDATE hr_job_vacancies
                                    SET openings = :op, offered_salary = :sal, apply_url = :url, status = :st
                                    WHERE tenant_id = :tid AND vacancy_id = :vid
                                """),
                                {
                                    "op": int(new_openings),
                                    "sal": new_salary.strip(),
                                    "url": new_url.strip(),
                                    "st": new_status,
                                    "tid": tenant_id,
                                    "vid": target["vacancy_id"],
                                },
                            )
                        st.success(f"✅ 已更新職缺 `{target['vacancy_id']}`。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 更新失敗：{e}")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
