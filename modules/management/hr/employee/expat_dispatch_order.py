import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def init_expat_dispatch_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.expat_dispatch_orders (
                    id SERIAL PRIMARY KEY,
                    order_no VARCHAR(50) UNIQUE NOT NULL,
                    emp_code VARCHAR(50) NOT NULL,
                    emp_name VARCHAR(150) NOT NULL,
                    destination VARCHAR(150) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    dispatch_purpose TEXT,
                    overseas_allowance NUMERIC(15, 2) DEFAULT 0,
                    accommodation_support VARCHAR(250),
                    status VARCHAR(50) DEFAULT '執行中 (Active)',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_expat_dispatch_page(engine=None, lang="繁體中文"):
    st.markdown("### ✈️ 外派人員派遣單與任務記錄中心 (Expatriate Dispatch Order)")
    st.caption("管理外派幹部與跨廠區／海外專案之任務指派、起訖時間、津貼設定與差旅記錄。")

    init_expat_dispatch_db(engine)

    tab_create, tab_query = st.tabs(["📝 開立新外派派遣單", "📋 歷史外派派遣單總覽"])

    # ----------------------------------------------------
    # Tab 1: 開立新外派單
    # ----------------------------------------------------
    with tab_create:
        st.markdown("#### 📄 填寫外派任務派遣單")
        
        # 嘗試從 employee_profiles 抓取現有的外派/外籍幹部名單
        expat_candidates = ["TW-001 - 許福村 (台灣)", "CN-002 - 張偉 (中國)"]
        if engine:
            try:
                df_exp = pd.read_sql("SELECT emp_code, emp_name, staff_type FROM public.employee_profiles WHERE staff_type LIKE '%外派%' OR staff_type LIKE '%外籍%';", con=engine)
                if not df_exp.empty:
                    expat_candidates = [f"{r['emp_code']} - {r['emp_name']}" for _, r in df_exp.iterrows()]
            except Exception:
                pass

        with st.form("form_expat_dispatch"):
            c1, c2 = st.columns(2)
            with c1:
                default_order_no = f"EXP-{datetime.datetime.now().strftime('%Y%m%d')}-01"
                order_no = st.text_input("外派單編號 (Dispatch Order No.) *", value=default_order_no)
                selected_emp = st.selectbox("選擇外派人員 (Expat Staff) *", expat_candidates)
                destination = st.selectbox("派駐地點 / 目標廠區 (Destination)", ["西寧廠 (Tay Ninh)", "胡志明辦事處 (HCMC)", "平陽專案現場 (Binh Duong)", "台灣總公司 (Taiwan HQ)", "其他外部工地 (Other Site)"])
            with c2:
                today = datetime.date.today()
                start_date = st.date_input("外派開始日期 (Start Date) *", value=today)
                end_date = st.date_input("外派結束日期 / 預計返回日 (End Date) *", value=today + datetime.timedelta(days=90))
                allowance = st.number_input("本專案海外津貼 / 差旅補助 (VND)", value=10000000.0, step=1000000.0)

            dispatch_purpose = st.text_area("外派任務目的與工作內容說明 (Purpose of Dispatch)", placeholder="例如：西寧廠新產線自動化系統建置與 ERP 現場技術支援。")
            accommodation = st.text_input("住宿與交通安排備註 (Accommodation & Transport)", placeholder="公司提供廠區宿舍與專車接送。")

            if st.form_submit_button("🚀 發布並存檔外派派遣單", type="primary", use_container_width=True):
                if order_no and selected_emp:
                    parts = selected_emp.split(" - ")
                    emp_code = parts[0].strip()
                    emp_name = parts[1].strip() if len(parts) > 1 else "Unknown"

                    if engine:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO public.expat_dispatch_orders 
                                    (order_no, emp_code, emp_name, destination, start_date, end_date, dispatch_purpose, overseas_allowance, accommodation_support, status)
                                    VALUES (:ono, :ecode, :ename, :dest, :sdate, :edate, :purp, :allow, :accom, '執行中 (Active)')
                                    ON CONFLICT (order_no) DO UPDATE SET 
                                    destination = :dest, start_date = :sdate, end_date = :edate, dispatch_purpose = :purp, overseas_allowance = :allow, accommodation_support = :accom;
                                """), {
                                    "ono": order_no.strip(),
                                    "ecode": emp_code,
                                    "ename": emp_name,
                                    "dest": destination,
                                    "sdate": start_date,
                                    "edate": end_date,
                                    "purp": dispatch_purpose,
                                    "allow": allowance,
                                    "accom": accommodation
                                })
                        except Exception as e:
                            st.error(f"❌ 存檔失敗: {str(e)}")

                    st.success(f"🎉 成功開立外派單：`{order_no}`，已指派給 `{emp_name}` 駐點至 `{destination}`！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫外派單編號並選擇外派人員！")

    # ----------------------------------------------------
    # Tab 2: 歷史外派單總覽
    # ----------------------------------------------------
    with tab_query:
        st.markdown("### 📋 所有外派任務與派遣單記錄")
        if engine:
            try:
                df_orders = pd.read_sql("SELECT * FROM public.expat_dispatch_orders ORDER BY start_date DESC;", con=engine)
                if not df_orders.empty:
                    st.dataframe(df_orders, use_container_width=True, hide_index=True)
                else:
                    st.info("目前尚無外派派遣單記錄。")
            except Exception:
                st.info("目前尚無外派派遣單記錄。")
        else:
            st.info("資料庫引擎未連線。")

def show(*args, **kwargs):
    render_expat_dispatch_page(*args, **kwargs)

def main(*args, **kwargs):
    render_expat_dispatch_page(*args, **kwargs)
