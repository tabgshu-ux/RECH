# ==========================================
# 檔案路徑：modules/approval_workflow.py（公務派車申請單區塊範例／覆蓋）
# 職責：全公司電子簽核中心 - 廠區公務派車申請單（支援日期 + 出車／返回時間）
# ==========================================

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _ensure_vehicle_dispatch_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS approval_vehicle_dispatches (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        dispatch_no VARCHAR(64) UNIQUE NOT NULL,
                        project_id VARCHAR(80),
                        applicant_name VARCHAR(120) NOT NULL,
                        dept_or_role VARCHAR(120),
                        vehicle_plate VARCHAR(120) NOT NULL,
                        driver_name VARCHAR(120),
                        purpose_type VARCHAR(100),
                        destination VARCHAR(200) NOT NULL,
                        reason_detail TEXT,
                        depart_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        return_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                        status VARCHAR(32) DEFAULT 'PENDING_SUPERVISOR',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
    except Exception:
        pass


def _render_vehicle_dispatch_form(engine=None, lang="zh"):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name") or "admin"
    user_role = st.session_state.get("user_role") or "角色"
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    txt = {
        "zh": {
            "hdr": "🚗 3. 廠區公務派車申請單",
            "flow": "派車申請流程：員工填單 ➔ 部門主管簽核 ➔ 門禁保全確認出廠放行與里程登記。",
            "app_name": "申請人姓名（系統綁定）*",
            "dept_role": "所屬部門（系統綁定）",
            "veh": "選擇公務車輛／車號*",
            "drv": "駕駛員／司機姓名",
            "ptype": "派車用途類別*",
            "dest": "前往目的地／案場名稱*",
            "reason": "派車公務事由與詳細說明*",
            "dep_date": "預計出廠日期",
            "dep_time": "預計出廠時間（時:分）",
            "ret_date": "預計返回日期",
            "ret_time": "預計返回時間（時:分）",
            "submit": "📨 提交派車申請單送部門主管審核",
            "time_err": "⚠️ 預計返回時間必須晚於預計出廠時間，請重新確認。",
            "req_err": "⚠️ 請填寫前往目的地與派車事由。",
            "ok": "✅ 已提交派車單 `{}`（出車：{} ➔ 返回：{}），送交部門主管審核。",
        },
        "vi": {
            "hdr": "🚗 3. Phiếu Đăng Ký Xe Công Vụ Nhà Máy",
            "flow": "Quy trình: Nhân viên gửi phiếu ➔ Trưởng bộ phận duyệt ➔ Bảo vệ xác nhận xuất xe & số km.",
            "app_name": "Người Đề Nghị (Hệ thống)*",
            "dept_role": "Bộ Phận / Chức Vụ",
            "veh": "Chọn Xe Công Vụ / Biển Số*",
            "drv": "Tài Xế / Người Lái",
            "ptype": "Loại Mục Đích Đi Xe*",
            "dest": "Điểm Đến / Tên Công Trường*",
            "reason": "Lý Do & Chi Tiết Công Tác*",
            "dep_date": "Ngày Dự Kiến Xuất Xe",
            "dep_time": "Giờ Dự Kiến Xuất Xe",
            "ret_date": "Ngày Dự Kiến Về",
            "ret_time": "Giờ Dự Kiến Về",
            "submit": "📨 Gửi Phiếu Xin Xe Trình Duyệt",
            "time_err": "⚠️ Thời gian dự kiến về phải sau thời gian dự kiến xuất xe.",
            "req_err": "⚠️ Vui lòng nhập điểm đến và lý do đi xe.",
            "ok": "✅ Đã gửi phiếu `{}` (Xuất: {} ➔ Về: {}).",
        },
        "en": {
            "hdr": "🚗 3. Factory Vehicle Dispatch Request",
            "flow": "Workflow: Employee submits ➔ Department manager approves ➔ Security gate logs departure & mileage.",
            "app_name": "Applicant (System)*",
            "dept_role": "Department / Role",
            "veh": "Select Vehicle / Plate*",
            "drv": "Driver Name",
            "ptype": "Dispatch Purpose Type*",
            "dest": "Destination / Site Name*",
            "reason": "Purpose & Detailed Notes*",
            "dep_date": "Est. Departure Date",
            "dep_time": "Est. Departure Time",
            "ret_date": "Est. Return Date",
            "ret_time": "Est. Return Time",
            "submit": "📨 Submit Dispatch Request for Approval",
            "time_err": "⚠️ Return time must be later than departure time.",
            "req_err": "⚠️ Please enter destination and dispatch purpose.",
            "ok": "✅ Submitted dispatch `{}` (Depart: {} ➔ Return: {}).",
        },
    }[code]

    st.markdown(f"#### {txt['hdr']}")
    st.info(txt["flow"])
    _ensure_vehicle_dispatch_table(engine)

    default_dep_dt = (now_vn + timedelta(minutes=15)).replace(second=0, microsecond=0)
    default_ret_dt = (default_dep_dt + timedelta(hours=3)).replace(second=0, microsecond=0)

    c_left, c_mid, c_right = st.columns([3.5, 3.5, 3.0])

    with c_left:
        st.text_input(txt["app_name"], value=user_name, disabled=True, key="v_app_name")
        st.text_input(txt["dept_role"], value=user_role, disabled=True, key="v_dept_role")
        purpose_type = st.selectbox(
            txt["ptype"],
            ["商務／工程公務外出", "工地巡檢與會勘", "物料／設備運送", "客戶驗收與拜訪"],
            key="v_purpose_type",
        )

    with c_mid:
        vehicle_plate = st.selectbox(
            txt["veh"],
            [
                "60A-888.99 (Toyota Fortuner 7座)",
                "61C-452.18 (Mitsubishi Triton 皮卡)",
                "70A-129.66 (Toyota Innova 公務車)",
            ],
            key="v_vehicle_plate",
        )
        driver_name = st.text_input(txt["drv"], value="Nguyễn Văn Tài (專職司機)", key="v_driver_name")
        destination = st.text_input(
            txt["dest"],
            placeholder="例：西寧省安平工業區客場",
            key="v_destination",
        )

    with c_right:
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            dep_date = st.date_input(txt["dep_date"], value=default_dep_dt.date(), key="v_dep_date")
        with d_col2:
            dep_time = st.time_input(
                txt["dep_time"],
                value=time(default_dep_dt.hour, default_dep_dt.minute),
                step=900,
                key="v_dep_time",
            )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            ret_date = st.date_input(txt["ret_date"], value=default_ret_dt.date(), key="v_ret_date")
        with r_col2:
            ret_time = st.time_input(
                txt["ret_time"],
                value=time(default_ret_dt.hour, default_ret_dt.minute),
                step=900,
                key="v_ret_time",
            )

    reason_detail = st.text_area(
        txt["reason"],
        placeholder="例：前往西寧廠區載運 400A 配電盤，並陪同客戶驗收。",
        key="v_reason_detail",
    )

    depart_dt = datetime.combine(dep_date, dep_time)
    return_dt = datetime.combine(ret_date, ret_time)

    if st.button(txt["submit"], type="primary", use_container_width=True, key="v_submit_btn"):
        if not destination.strip() or not reason_detail.strip():
            st.warning(txt["req_err"])
        elif return_dt <= depart_dt:
            st.warning(txt["time_err"])
        elif not engine:
            st.error("❌ 尚未連線資料庫。")
        else:
            dispatch_no = f"CAR-{now_vn.strftime('%Y%m%d-%H%M%S')}"
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO approval_vehicle_dispatches (
                                tenant_id, dispatch_no, project_id, applicant_name,
                                dept_or_role, vehicle_plate, driver_name, purpose_type,
                                destination, reason_detail, depart_at, return_at, status
                            )
                            VALUES (
                                :tid, :dno, :pid, :aname,
                                :drole, :vplate, :dname, :ptype,
                                :dest, :rsn, :dep_at, :ret_at, 'PENDING_SUPERVISOR'
                            )
                        """),
                        {
                            "tid": tenant_id,
                            "dno": dispatch_no,
                            "pid": st.session_state.get("active_project_id"),
                            "aname": user_name,
                            "drole": user_role,
                            "vplate": vehicle_plate,
                            "dname": driver_name.strip() or None,
                            "ptype": purpose_type,
                            "dest": destination.strip(),
                            "rsn": reason_detail.strip(),
                            "dep_at": depart_dt,
                            "ret_at": return_dt,
                        },
                    )
                st.success(
                    txt["ok"].format(
                        dispatch_no,
                        depart_dt.strftime("%Y/%m/%d %H:%M"),
                        return_dt.strftime("%Y/%m/%d %H:%M"),
                    )
                )
            except Exception as e:
                st.error(f"❌ 提交派車申請單失敗：{e}")
