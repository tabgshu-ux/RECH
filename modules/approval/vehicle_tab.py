from datetime import datetime, time, timedelta
import streamlit as st
from modules.approval.workflow_repo import create_vehicle_dispatch


def render(engine, tenant_id: str, user_name: str, user_role: str, project_id: str | None, now_vn: datetime, code: str):
    txt = {
        "zh": ("🚗 3. 廠區公務派車申請單", "派車申請流程：員工填單 ➔ 部門主管簽核 ➔ 門禁保全確認出廠放行與里程登記。", "📨 提交派車申請單送部門主管審核"),
        "vi": ("🚗 3. Phiếu Đăng Ký Xe Công Vụ Nhà Máy", "Quy trình: Nhân viên gửi phiếu ➔ Trưởng bộ phận duyệt ➔ Bảo vệ xác nhận xuất xe & số km.", "📨 Gửi Phiếu Xin Xe Trình Duyệt"),
        "en": ("🚗 3. Factory Vehicle Dispatch Request", "Workflow: Employee submits ➔ Department manager approves ➔ Security gate logs departure & mileage.", "📨 Submit Dispatch Request for Approval"),
    }[code]
    st.markdown(f"#### {txt[0]}")
    st.info(txt[1])

    default_dep = (now_vn + timedelta(minutes=15)).replace(second=0, microsecond=0)
    default_ret = (default_dep + timedelta(hours=3)).replace(second=0, microsecond=0)
    c_left, c_mid, c_right = st.columns([3.5, 3.5, 3.0])

    with c_left:
        st.text_input("申請人姓名（系統綁定）*", value=user_name, disabled=True, key="v_app_name")
        st.text_input("所屬部門（系統綁定）", value=user_role, disabled=True, key="v_dept_role")
        purpose_type = st.selectbox("派車用途類別*", ["商務／工程公務外出", "工地巡檢與會勘", "物料／設備運送", "客戶驗收與拜訪"], key="v_purpose_type")

    with c_mid:
        vehicle_plate = st.selectbox("選擇公務車輛／車號*", ["60A-888.99 (Toyota Fortuner 7座)", "61C-452.18 (Mitsubishi Triton 皮卡)", "70A-129.66 (Toyota Innova 公務車)"], key="v_vehicle_plate")
        driver_name = st.text_input("駕駛員／司機姓名", value="Nguyễn Văn Tài (專職司機)", key="v_driver_name")
        destination = st.text_input("前往目的地／案場名稱*", placeholder="例：西寧省安平工業區客場", key="v_destination")

    with c_right:
        d1, d2 = st.columns(2)
        with d1:
            dep_date = st.date_input("預計出廠日期", value=default_dep.date(), key="v_dep_date")
        with d2:
            dep_time = st.time_input("預計出廠時間", value=time(default_dep.hour, default_dep.minute), step=900, key="v_dep_time")
        r1, r2 = st.columns(2)
        with r1:
            ret_date = st.date_input("預計返回日期", value=default_ret.date(), key="v_ret_date")
        with r2:
            ret_time = st.time_input("預計返回時間", value=time(default_ret.hour, default_ret.minute), step=900, key="v_ret_time")

    reason_detail = st.text_area("派車公務事由與詳細說明*", placeholder="例：前往西寧廠區載運 400A 配電盤，並陪同客戶驗收。", key="v_reason_detail")
    depart_dt, return_dt = datetime.combine(dep_date, dep_time), datetime.combine(ret_date, ret_time)

    if st.button(txt[2], type="primary", use_container_width=True, key="v_submit_btn"):
        if not destination.strip() or not reason_detail.strip():
            st.warning("⚠️ 請填寫前往目的地與派車事由。")
        elif return_dt <= depart_dt:
            st.warning("⚠️ 預計返回時間必須晚於預計出廠時間。")
        elif not engine:
            st.error("❌ 尚未連線資料庫。")
        else:
            try:
                dno = create_vehicle_dispatch(engine, tenant_id, user_name, user_role, project_id, vehicle_plate, driver_name.strip() or None, purpose_type, destination.strip(), reason_detail.strip(), depart_dt, return_dt, now_vn)
                st.success(f"✅ 已提交派車單 `{dno}`（{depart_dt.strftime('%Y/%m/%d %H:%M')} ➔ {return_dt.strftime('%Y/%m/%d %H:%M')}）。")
            except Exception as e:
                st.error(f"❌ 提交派車申請單失敗：{e}")
