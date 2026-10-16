import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 多語系字典 (i18n)
# ----------------------------------------------------
DORM_I18N = {
    "繁體中文": {
        "title": "🥗 幹部宿舍伙食與採購控管中心",
        "caption": "裕豐電機（越南西寧廠）專用：幹部宿舍每日用餐人數登記、伙食預算控管與採購金額連動。",
        "reg_header": "🥗 幹部宿舍每日用餐人數登記",
        "site_lbl": "選擇廠區",
        "meal_type_lbl": "餐別",
        "registrar_lbl": "登記人 / 會監",
        "date_lbl": "選擇用餐日期",
        "count_lbl": "用餐人數",
        "note_lbl": "備註 / 特別菜單需求",
        "note_ph": "如: 不吃牛肉、素食人數...",
        "submit_btn": "🚀 提交登記",
        "budget_info": "💡 越南西寧廠伙食預算控管：今天登記入住/用餐人數 {count} 人 ➡️ 今日全廠食材採購上限額度為 **{budget} VND**（標準：100,000 VND / 人 / 天）。",
        "list_header": "📋 本週宿舍搭夥人數與採購上限預估",
        "col_date": "日期",
        "col_site": "廠區",
        "col_count": "用餐人數",
        "col_budget": "單日採購預算上限",
        "col_owner": "負責人"
    },
    "Tiếng Việt": {
        "title": "🥗 Quản lý Bếp ăn Ký túc xá & Mua sắm Thực phẩm",
        "caption": "Nhà máy Tây Ninh Reetech: Đăng ký suất ăn, kiểm soát ngân sách thực phẩm ký túc xá.",
        "reg_header": "🥗 Đăng ký Suất ăn Ký túc xá Hàng ngày",
        "site_lbl": "Chọn nhà máy",
        "meal_type_lbl": "Buổi ăn",
        "registrar_lbl": "Người đăng ký",
        "date_lbl": "Ngày dùng bữa",
        "count_lbl": "Số lượng người ăn",
        "note_lbl": "Ghi chú / Yêu cầu thực đơn",
        "note_ph": "Ví dụ: Không ăn thịt bò...",
        "submit_btn": "🚀 Gửi đăng ký",
        "budget_info": "💡 Kiểm soát ngân sách Tây Ninh: Hôm nay có {count} người ➡️ Hạn mức mua sắm tối đa **{budget} VND** (Tiêu chuẩn: 100,000 VND/người/ngày).",
        "list_header": "📋 Dự báo số lượng & Ngân sách tuần này",
        "col_date": "Ngày",
        "col_site": "Nhà máy",
        "col_count": "Số người",
        "col_budget": "Hạn mức ngân sách",
        "col_owner": "Phụ trách"
    },
    "English": {
        "title": "🥗 Dormitory Catering & Food Procurement Control",
        "caption": "Tay Ninh Plant: Daily headcount registration, meal budget control and procurement tracking.",
        "reg_header": "🥗 Daily Dormitory Headcount Registration",
        "site_lbl": "Plant Location",
        "meal_type_lbl": "Meal Type",
        "registrar_lbl": "Registrar",
        "date_lbl": "Meal Date",
        "count_lbl": "Headcount",
        "note_lbl": "Remarks / Special Menu",
        "note_ph": "e.g., No beef, vegetarian...",
        "submit_btn": "🚀 Submit Registration",
        "budget_info": "💡 Tay Ninh Plant Budget Control: Today's headcount is {count} ➡️ Procurement limit is **{budget} VND** (Standard: 100,000 VND / person / day).",
        "list_header": "📋 Weekly Headcount & Budget Forecast",
        "col_date": "Date",
        "col_site": "Plant",
        "col_count": "Headcount",
        "col_budget": "Daily Budget Limit",
        "col_owner": "Owner"
    }
}

def format_vnd(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def init_dorm_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.dorm_catering (
                    id SERIAL PRIMARY KEY,
                    meal_date DATE NOT NULL,
                    site_location VARCHAR(100) NOT NULL,
                    meal_type VARCHAR(50) NOT NULL,
                    headcount INT NOT NULL,
                    budget_limit NUMERIC(15,2) NOT NULL,
                    registrar VARCHAR(100),
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_dorm_catering_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = DORM_I18N.get(active_lang, DORM_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_dorm_db(engine)

    # 初始化 session_state 備援
    if "dorm_records_db" not in st.session_state:
        st.session_state.dorm_records_db = [
            {"date": str(datetime.date.today()), "site": "越南西寧廠 (Tay Ninh)", "count": 12, "budget": 1200000.0, "owner": st.session_state.get("user_name", "admin")}
        ]

    st.markdown(f"### {L['reg_header']}")
    
    with st.form("form_dorm_catering"):
        c1, c2, c3 = st.columns(3)
        with c1:
            # 廠區嚴格限定為【越南西寧廠 (Tay Ninh)】
            site_loc = st.selectbox(L["site_lbl"], ["越南西寧廠 (Tay Ninh)"])
        with c2:
            meal_type = st.selectbox(L["meal_type_lbl"], ["全天三餐 (All Day)", "早餐 (Breakfast)", "午餐 (Lunch)", "晚餐 (Dinner)"])
        with c3:
            registrar = st.text_input(L["registrar_lbl"], value=st.session_state.get("user_name", "admin"))

        c4, c5 = st.columns(2)
        with c4:
            meal_date = st.date_input(L["date_lbl"], value=datetime.date.today())
        with c5:
            headcount = st.number_input(L["count_lbl"], min_value=1, value=12, step=1)

        notes = st.text_input(L["note_lbl"], placeholder=L["note_ph"])

        # 每人每日伙食標準：100,000 VND
        daily_budget = float(headcount) * 100000.0
        st.info(L["budget_info"].format(count=headcount, budget=format_vnd(daily_budget)))

        submitted = st.form_submit_button(L["submit_btn"], type="primary", use_container_width=True)
        if submitted:
            success_saved = False
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO public.dorm_catering 
                                (meal_date, site_location, meal_type, headcount, budget_limit, registrar, notes)
                                VALUES (:mdate, :site, :mtype, :cnt, :budget, :reg, :notes);
                            """),
                            {
                                "mdate": meal_date, "site": site_loc, "mtype": meal_type,
                                "cnt": headcount, "budget": daily_budget, "reg": registrar, "notes": notes
                            }
                        )
                    success_saved = True
                except Exception as e:
                    st.error(f"⚠️ 資料庫寫入異常: {str(e)}")

            # 同時寫入 session_state 確保雙軌順暢
            st.session_state.dorm_records_db.insert(0, {
                "date": str(meal_date),
                "site": site_loc,
                "count": headcount,
                "budget": daily_budget,
                "owner": registrar
            })

            st.success(f"🎉 成功登記 {meal_date} 越南西寧廠宿舍用餐人數：{headcount} 人！預算上限：{format_vnd(daily_budget)}")
            st.rerun()

    st.markdown("---")
    st.markdown(f"### {L['list_header']}")

    records_list = []
    if engine is not None:
        try:
            df_dorm = pd.read_sql("SELECT * FROM public.dorm_catering ORDER BY meal_date DESC, id DESC", con=engine)
            if not df_dorm.empty:
                for _, r in df_dorm.iterrows():
                    records_list.append({
                        L["col_date"]: str(r["meal_date"])[:10],
                        L["col_site"]: r["site_location"],
                        L["col_count"]: r["headcount"],
                        L["col_budget"]: format_vnd(r["budget_limit"]),
                        L["col_owner"]: r["registrar"]
                    })
        except Exception:
            pass

    if not records_list and "dorm_records_db" in st.session_state:
        for item in st.session_state.dorm_records_db:
            records_list.append({
                L["col_date"]: item["date"],
                L["col_site"]: item["site"],
                L["col_count"]: item["count"],
                L["col_budget"]: format_vnd(item["budget"]),
                L["col_owner"]: item["owner"]
            })

    if records_list:
        st.dataframe(pd.DataFrame(records_list), use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無宿舍用餐登記紀錄。")
