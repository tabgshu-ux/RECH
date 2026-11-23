# ==========================================
# 檔案路徑：modules/management/hr/employee/labor_contract_management.py
# 職責：L2 行政／人事 - 越南勞動合約管理（掃描上傳、條件自訂、產生公司合約與到期/未簽約預警）
# ==========================================

import base64
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text


CONTRACT_TYPES = [
    "定期勞動合約 (Hợp đồng lao động xác định thời hạn)",
    "不定期勞動合約 (Hợp đồng lao động không xác định thời hạn)",
    "試用／特定期限合約 (Thử việc / Thời vụ)",
]

CONTRACT_STATUSES = [
    "生效中",
    "即將到期",
    "已到期",
    "已續簽",
    "已終止",
]


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def _parse_date(val) -> date | None:
    if not val:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return date.fromisoformat(str(val)[:10])
    except Exception:
        return None


def _build_vn_company_contract_text(
    company_name: str,
    company_addr: str,
    company_tax: str,
    rep_name: str,
    rep_title: str,
    contract_no: str,
    emp_code: str,
    emp_name: str,
    dept_name: str,
    position_name: str,
    contract_type: str,
    signed_date: date,
    start_date: date,
    end_date: date | None,
    work_location: str,
    work_hours_rule: str,
    agreed_salary_vnd: float,
    pay_day_rule: str,
    allowance_terms: str,
    insurance_terms: str,
    safety_and_custom_terms: str,
) -> str:
    end_str_vi = end_date.strftime("%d/%m/%Y") if end_date else "Không xác định (不定期)"
    end_str_zh = end_date.strftime("%Y-%m-%d") if end_date else "不定期"
    sal_fmt = _fmt_vnd(agreed_salary_vnd)

    return f"""================================================================================
HỢP ĐỒNG LAO ĐỘNG / 越南勞動合約書
Số hợp đồng / 合約編號：{contract_no}
Ngày ký / 簽約日期：{signed_date.strftime("%d/%m/%Y")} ({signed_date.isoformat()})
================================================================================

ĐIỀU 1: THÔNG TIN CÁC BÊN GIAO KẾT HỢP ĐỒNG / 第一條：簽約雙方資訊

1. Bên sử dụng lao động (甲方 / 雇主)：{company_name}
   - Địa chỉ / 地址：{company_addr}
   - Mã số thuế / 稅號：{company_tax or "Theo đăng ký doanh nghiệp (依營業登記)"}
   - Người đại diện / 法定代表人：{rep_name}    Chức vụ / 職稱：{rep_title}

2. Người lao động (乙方 / 受僱員工)：{emp_name}
   - Mã nhân viên / 工號：{emp_code or "-"}
   - Bộ phận / 部門：{dept_name}
   - Chức vụ / 職稱：{position_name}

--------------------------------------------------------------------------------
ĐIỀU 2: LOẠI HỢP ĐỒNG, THỜI HẠN VÀ ĐỊA ĐIỂM LÀM VIỆC
第二條：合約種類、期間與工作地點

- Loại hợp đồng / 合約種類：{contract_type}
- Thời hạn hợp đồng / 合約期間：Từ ngày {start_date.strftime("%d/%m/%Y")} đến ngày {end_str_vi}
  (自 {start_date.isoformat()} 起至 {end_str_zh} 止)
- Địa điểm làm việc / 工作地點：{work_location}
- Công việc chuyên môn / 工作內容：Thực hiện nhiệm vụ theo chức danh {position_name} (Bộ phận {dept_name}) và sự phân công hợp pháp của Công ty.
  (依 {position_name} 職稱與 {dept_name} 部門職責，並配合公司合法工作指派。)

--------------------------------------------------------------------------------
ĐIỀU 3: THỜI GIỜ LÀM VIỆC VÀ NGHỈ NGƠI
第三條：工時與休假制度

- Thời giờ làm việc & nghỉ ngơi / 工時與休息規定：{work_hours_rule}
- Làm thêm giờ (OT) / 加班安排：Thực hiện theo quy định của Bộ luật Lao động Việt Nam và phê duyệt của Công ty.
  (依越南勞動法規及公司核准流程辦理，並依法計付加班費。)

--------------------------------------------------------------------------------
ĐIỀU 4: TIỀN LƯƠNG, PHỤ CẤP VÀ CHẾ ĐỘ THANH TOÁN
第四條：基本薪資、津貼與發薪方式

- Mức lương cơ bản thỏa thuận / 約定基本薪資：{sal_fmt} / tháng (月薪)
- Hình thức & kỳ trả lương / 發薪日期與方式：{pay_day_rule}
- Phụ cấp & phúc lợi / 津貼與福利條款：{allowance_terms}

--------------------------------------------------------------------------------
ĐIỀU 5: BẢO HIỂM XÃ HỘI, Y TẾ, THẤT NGHIỆP VÀ AN TOÀN LAO ĐỘNG
第五條：社會保險（BHXH/BHYT/BHTN）與職業安全衛生

- Chế độ bảo hiểm / 社保提撥：
  {insurance_terms}
- An toàn, vệ sinh lao động & điều khoản bổ sung của Công ty / 工安與公司自訂條款：
  {safety_and_custom_terms}

--------------------------------------------------------------------------------
ĐIỀU 6: ĐIỀU KHOẢN CHUNG / 第六條：附則

- Hợp đồng này được lập thành bản song ngữ Việt - Hoa có giá trị pháp lý như nhau; trường hợp có khác biệt về cách hiểu thì ưu tiên áp dụng theo quy định pháp luật lao động Việt Nam.
  (本合約採越文與中文對照繕製；如文義解釋有疑義，以越南現行勞動法規為準。)

BÊN SỬ DỤNG LAO ĐỘNG                        NGƯỜI LAO ĐỘNG
甲方（公司代表簽章）                         乙方（員工簽名）


___________________________                  ___________________________
{rep_name}                                   {emp_name}
"""


def ensure_labor_contract_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.hr_labor_contracts (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        contract_no VARCHAR(80) NOT NULL,
                        emp_code VARCHAR(80),
                        emp_name VARCHAR(150) NOT NULL,
                        dept_name VARCHAR(100),
                        position_name VARCHAR(100),
                        contract_type VARCHAR(120) NOT NULL,
                        signed_date DATE,
                        start_date DATE NOT NULL,
                        end_date DATE,
                        agreed_base_salary_vnd NUMERIC(18, 2) DEFAULT 0,
                        work_location VARCHAR(150) DEFAULT 'Tây Ninh, Việt Nam',
                        contract_status VARCHAR(32) DEFAULT '生效中',
                        file_ref VARCHAR(255),
                        scan_file_name VARCHAR(255),
                        scan_mime_type VARCHAR(120),
                        scan_data_b64 TEXT,
                        contract_draft_text TEXT,
                        notes TEXT,
                        created_by VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            )
            conn.execute(text("ALTER TABLE public.hr_labor_contracts ADD COLUMN IF NOT EXISTS scan_file_name VARCHAR(255);"))
            conn.execute(text("ALTER TABLE public.hr_labor_contracts ADD COLUMN IF NOT EXISTS scan_mime_type VARCHAR(120);"))
            conn.execute(text("ALTER TABLE public.hr_labor_contracts ADD COLUMN IF NOT EXISTS scan_data_b64 TEXT;"))
            conn.execute(text("ALTER TABLE public.hr_labor_contracts ADD COLUMN IF NOT EXISTS contract_draft_text TEXT;"))
    except Exception:
        pass


def render_labor_contract_panel(engine, tenant_id: str = "REETECH_VN", lang: str = "zh"):
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    current_user = st.session_state.get("user_name") or "admin"

    st.markdown("### 📄 員工勞動合約管理（掃描建檔・自訂產生越文合約・合規預警）")
    st.caption("支援上傳既有紙本合約掃描檔，也可修改越南勞動合約條件並產生公司版雙語合約（越文／中文）。")

    if not engine:
        st.info("尚未連線資料庫，無法管理勞動合約。")
        return

    ensure_labor_contract_table(engine)

    emp_list: list[dict] = []
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT COALESCE(emp_code, CAST(id AS TEXT)) AS emp_code,
                           emp_name,
                           COALESCE(department, '未指定') AS department,
                           COALESCE(position, '員工') AS position,
                           COALESCE(base_salary, 0) AS base_salary
                    FROM public.employee_profiles
                    WHERE COALESCE(status, '在職') <> '離職'
                    ORDER BY id ASC
                """)
            ).fetchall()
            for r in rows:
                if r[1]:
                    emp_list.append({
                        "emp_code": str(r[0] or "").strip(),
                        "emp_name": str(r[1]).strip(),
                        "department": str(r[2] or "未指定").strip(),
                        "position": str(r[3] or "員工").strip(),
                        "base_salary": float(r[4] or 0.0),
                    })
    except Exception:
        emp_list = []

    emp_names = [e["emp_name"] for e in emp_list]
    emp_map = {e["emp_name"]: e for e in emp_list}

    df_c = pd.DataFrame()
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, contract_no, emp_code, emp_name,
                           COALESCE(dept_name, '-') AS dept_name,
                           COALESCE(position_name, '-') AS position_name,
                           contract_type, signed_date, start_date, end_date,
                           COALESCE(agreed_base_salary_vnd, 0) AS agreed_base_salary_vnd,
                           COALESCE(work_location, 'Tây Ninh, Việt Nam') AS work_location,
                           COALESCE(contract_status, '生效中') AS contract_status,
                           COALESCE(file_ref, '-') AS file_ref,
                           scan_file_name, scan_mime_type, scan_data_b64,
                           contract_draft_text,
                           COALESCE(notes, '-') AS notes
                    FROM public.hr_labor_contracts
                    WHERE COALESCE(tenant_id, 'REETECH_VN') = :tid
                    ORDER BY id DESC
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                df_c = pd.DataFrame([r._asdict() for r in rows])
    except Exception as e:
        st.warning(f"⚠️ 讀取勞動合約紀錄異常：{e}")

    # 未簽約與合約到期預警
    active_contracted = set()
    if not df_c.empty:
        active_contracted = {
            str(r["emp_name"]).strip()
            for _, r in df_c.iterrows()
            if str(r.get("contract_status", "生效中")) != "已終止" and str(r.get("emp_name") or "").strip()
        }
    unsigned_emps = [n for n in emp_names if n not in active_contracted]

    expiring_alerts: list[str] = []
    if not df_c.empty:
        for _, r in df_c.iterrows():
            st_val = str(r.get("contract_status") or "生效中")
            if st_val not in ("生效中", "即將到期"):
                continue
            ed = _parse_date(r.get("end_date"))
            if ed:
                d_left = (ed - today_vn).days
                if d_left < 0:
                    expiring_alerts.append(f"🔴 **【合約已逾期】** `{r['contract_no']}` - `{r['emp_name']}`（到期日 `{ed}`，逾期 `{abs(d_left)}` 天）")
                elif d_left <= 30:
                    expiring_alerts.append(f"⚠️ **【30天內即將到期】** `{r['contract_no']}` - `{r['emp_name']}`（到期日 `{ed}`，剩餘 `{d_left}` 天）")

    if unsigned_emps:
        st.error(f"🚨 勞動合規提醒：目前有 **{len(unsigned_emps)}** 位在職員工尚無有效勞動合約登記，建議盡速補簽建檔！")
        st.caption("尚未簽約人員：" + "、".join(unsigned_emps[:30]) + (" ..." if len(unsigned_emps) > 30 else ""))

    if expiring_alerts:
        st.warning("⏰ 勞動合約到期預警：")
        for msg in expiring_alerts:
            st.markdown(msg)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("在職員工總數", f"{len(emp_names)} 人")
    m2.metric("已建立合約人數", f"{len(active_contracted)} 人")
    m3.metric("尚未簽約人數", f"{len(unsigned_emps)} 人")
    m4.metric("合約紀錄總數", f"{len(df_c) if not df_c.empty else 0} 份")

    tab_create, tab_list = st.tabs([
        "✍️ 掃描建檔 & 修改條件產生越南合約",
        "📋 合約清冊・掃描檔預覽與狀態管理",
    ])

    with tab_create:
        st.markdown("#### 1️⃣ 基本合約與員工資料")
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_emp = st.selectbox("選擇員工*", emp_names if emp_names else ["（尚無在職員工資料）"], key="lc_sel_emp")
            emp_info = emp_map.get(sel_emp, {})
            dept_val = emp_info.get("department", "未指定")
            pos_val = emp_info.get("position", "員工")
            emp_sal_val = float(emp_info.get("base_salary", 0.0))

            st.text_input("部門／職稱", value=f"{dept_val} / {pos_val}", disabled=True, key="lc_dept_pos")
            default_cno = f"HDLD-{today_vn.strftime('%Y%m%d')}-{str(emp_info.get('emp_code') or '001')[-4:]}"
            contract_no = st.text_input("合約編號*", value=default_cno, key="lc_cno_input")
        with c2:
            ctype = st.selectbox("合約類型*", CONTRACT_TYPES, key="lc_ctype_sel")
            signed_dt = st.date_input("簽約日期*", value=today_vn, key="lc_signed_dt")
            start_dt = st.date_input("合約生效日*", value=today_vn, key="lc_start_dt")
        with c3:
            has_end_date = st.checkbox("設定合約到期日（定期／試用合約建議勾選）", value=True, key="lc_has_end")
            end_dt = st.date_input("合約到期日", value=start_dt + timedelta(days=365), key="lc_end_dt") if has_end_date else None
            agreed_sal = st.number_input(
                "合約約定基本薪資 (VND/月)*",
                min_value=0.0,
                value=emp_sal_val,
                step=100000.0,
                key="lc_agreed_sal",
            )

        st.markdown("#### 2️⃣ 越南勞動合約條件修改（可依公司政策與職位自由調整）")
        t1, t2 = st.columns(2)
        with t1:
            comp_name = st.text_input("公司名稱 (Bên sử dụng lao động)", value="CÔNG TY TNHH CÔNG NGHIỆP REETECH (裕豐電機工業有限公司)", key="lc_comp_name")
            comp_addr = st.text_input("公司地址", value="Tỉnh Tây Ninh, Việt Nam", key="lc_comp_addr")
            comp_tax = st.text_input("公司稅號 (Mã số thuế)", value="", placeholder="選填：輸入公司稅號", key="lc_comp_tax")
            rep_name = st.text_input("公司代表人 (Người đại diện)", value="Giám đốc / 總經理", key="lc_rep_name")
            rep_title = st.text_input("代表人職稱", value="Tổng Giám đốc / 總經理", key="lc_rep_title")
        with t2:
            work_loc = st.text_input("工作地點 (Địa điểm làm việc)", value="Tỉnh Tây Ninh, Việt Nam (西寧廠區及公司指派案場)", key="lc_work_loc")
            work_hours_rule = st.text_area(
                "工時與休息條件（可修改）",
                value="Làm việc 08 giờ/ngày, 48 giờ/tuần hoặc theo ca làm việc của Công ty; nghỉ ngơi và nghỉ lễ theo Bộ luật Lao động Việt Nam.\n(每日正常工時 8 小時、每週 48 小時或依排班表執行；例假與國定假日依越南勞動法規辦理。)",
                height=85,
                key="lc_work_hours",
            )
            pay_day_rule = st.text_input(
                "發薪日與方式（可修改）",
                value="Trả lương hàng tháng qua tài khoản ngân hàng hoặc tiền mặt theo quy định kỳ lương của Công ty.\n(每月依公司薪資結算日透過銀行轉帳或現金發放。)",
                key="lc_pay_day",
            )

        t3, t4 = st.columns(2)
        with t3:
            allowance_terms = st.text_area(
                "津貼與福利條件（可修改）",
                value="Các khoản phụ cấp (chức vụ, công trình, đi lại, ăn ca, chuyên cần...) được áp dụng theo quy chế lương và quyết định của Công ty.\n(職務、工程、交通、伙食、全勤等津貼依公司薪資規章與核准明細發給。)",
                height=85,
                key="lc_alw_terms",
            )
        with t4:
            insurance_terms = st.text_area(
                "社保（BHXH/BHYT/BHTN）與工安自訂條款（可修改）",
                value="Tham gia đầy đủ BHXH, BHYT, BHTN theo tỷ lệ quy định pháp luật Việt Nam (phần người lao động và phần doanh nghiệp đóng).\n(依越南法規辦理員工與公司雙方應繳之 BHXH、BHYT、BHTN 社會保險。)",
                height=85,
                key="lc_ins_terms",
            )

        custom_extra_terms = st.text_area(
            "公司自訂補充條款（保密、設備保管、試用期或特殊約定，可自行修改）",
            value="Người lao động có trách nhiệm bảo quản tài sản, thiết bị, hồ sơ kỹ thuật của Công ty và tuân thủ nội quy lao động, an toàn lao động.\n(員工應妥善保管公司財產、設備與技術資料，並遵守勞動紀律與工安規定。)",
            height=75,
            key="lc_custom_terms",
        )

        st.markdown("#### 3️⃣ 紙本合約掃描檔上傳（PDF / 圖片）")
        u_col1, u_col2 = st.columns([2, 2])
        with u_col1:
            scan_file = st.file_uploader(
                "上傳紙本合約掃描檔或照片",
                type=["pdf", "png", "jpg", "jpeg"],
                key="lc_scan_uploader",
            )
        with u_col2:
            file_ref = st.text_input("檔案櫃編號／備註", placeholder="例：紙本正本第 01 櫃、已簽名掃描", key="lc_file_ref")
            notes_txt = st.text_input("合約備註", placeholder="例：新進員工簽約／年度續約", key="lc_notes_txt")

        generated_contract_str = _build_vn_company_contract_text(
            company_name=comp_name.strip() or "CÔNG TY TNHH REETECH",
            company_addr=comp_addr.strip() or "Tây Ninh, Việt Nam",
            company_tax=comp_tax.strip(),
            rep_name=rep_name.strip() or "Giám đốc",
            rep_title=rep_title.strip() or "Giám đốc",
            contract_no=contract_no.strip() or default_cno,
            emp_code=emp_info.get("emp_code", ""),
            emp_name=sel_emp,
            dept_name=dept_val,
            position_name=pos_val,
            contract_type=ctype,
            signed_date=signed_dt,
            start_date=start_dt,
            end_date=end_dt,
            work_location=work_loc.strip() or "Tây Ninh, Việt Nam",
            work_hours_rule=work_hours_rule.strip(),
            agreed_salary_vnd=float(agreed_sal),
            pay_day_rule=pay_day_rule.strip(),
            allowance_terms=allowance_terms.strip(),
            insurance_terms=insurance_terms.strip(),
            safety_and_custom_terms=custom_extra_terms.strip(),
        )

        with st.expander("👁️ 預覽產生的公司版越南勞動合約（越文／中文）並下載", expanded=False):
            st.code(generated_contract_str, language="text")
            st.download_button(
                label="📥 下載產生的公司版勞動合約 (.txt)",
                data=generated_contract_str.encode("utf-8-sig"),
                file_name=f"{(contract_no.strip() or 'Hop_Dong_Lao_Dong')}_{sel_emp}.txt",
                mime="text/plain",
            )

        if st.button("💾 儲存合約紀錄（含掃描檔與產出合約內容）", type="primary", use_container_width=True, key="btn_save_contract_full"):
            if not emp_names or not sel_emp:
                st.warning("⚠️ 請先確認員工名冊已有資料。")
            elif not (contract_no or "").strip():
                st.warning("⚠️ 請填寫合約編號。")
            elif end_dt and end_dt < start_dt:
                st.warning("⚠️ 合約到期日不可早於合約生效日。")
            else:
                scan_name = None
                scan_mime = None
                scan_b64 = None
                if scan_file is not None:
                    raw_bytes = scan_file.getvalue()
                    if len(raw_bytes) > 8 * 1024 * 1024:
                        st.warning("⚠️ 掃描檔超過 8MB，請壓縮後再上傳。")
                        st.stop()
                    scan_name = scan_file.name
                    scan_mime = scan_file.type or "application/octet-stream"
                    scan_b64 = base64.b64encode(raw_bytes).decode("utf-8")

                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO public.hr_labor_contracts (
                                    tenant_id, contract_no, emp_code, emp_name,
                                    dept_name, position_name, contract_type,
                                    signed_date, start_date, end_date,
                                    agreed_base_salary_vnd, work_location,
                                    contract_status, file_ref,
                                    scan_file_name, scan_mime_type, scan_data_b64,
                                    contract_draft_text, notes,
                                    created_by, created_at, updated_at
                                )
                                VALUES (
                                    :tid, :cno, :ecode, :ename,
                                    :dname, :pname, :ctype,
                                    :sdt, :st_dt, :ed_dt,
                                    :asal, :wloc,
                                    '生效中', :fref,
                                    :sname, :smime, :sb64,
                                    :cdraft, :notes,
                                    :cby, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                                )
                            """),
                            {
                                "tid": tenant_id,
                                "cno": contract_no.strip(),
                                "ecode": emp_info.get("emp_code"),
                                "ename": sel_emp,
                                "dname": dept_val,
                                "pname": pos_val,
                                "ctype": ctype,
                                "sdt": signed_dt,
                                "st_dt": start_dt,
                                "ed_dt": end_dt,
                                "asal": float(agreed_sal),
                                "wloc": work_loc.strip() or "Tây Ninh, Việt Nam",
                                "fref": file_ref.strip() or None,
                                "sname": scan_name,
                                "smime": scan_mime,
                                "sb64": scan_b64,
                                "cdraft": generated_contract_str,
                                "notes": notes_txt.strip() or None,
                                "cby": current_user,
                            },
                        )
                    st.success(f"✅ 已儲存【{sel_emp}】的勞動合約（編號：{contract_no.strip()}）" + (f"，並附帶掃描檔 `{scan_name}`" if scan_name else "") + "。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存勞動合約失敗：{e}")

    with tab_list:
        if df_c.empty:
            st.info("目前尚未建立任何員工勞動合約紀錄。")
        else:
            search_kw = st.text_input("🔍 搜尋員工姓名、工號、合約編號或部門", placeholder="輸入關鍵字篩選...", key="lc_search_kw")
            df_view = df_c.copy()
            if search_kw and search_kw.strip():
                kw = search_kw.strip().lower()
                mask = df_view.astype(str).apply(lambda s: s.str.lower().str.contains(kw, na=False)).any(axis=1)
                df_view = df_view[mask]

            df_view["約定底薪"] = df_view["agreed_base_salary_vnd"].apply(_fmt_vnd)
            df_view["到期日顯示"] = df_view["end_date"].apply(lambda d: str(d)[:10] if d else "無期限")
            df_view["掃描檔狀態"] = df_view["scan_file_name"].apply(lambda x: f"📎 {x}" if x else "無掃描檔")

            disp_cols = [
                "id", "contract_no", "emp_code", "emp_name", "dept_name",
                "position_name", "contract_type", "signed_date", "start_date",
                "到期日顯示", "約定底薪", "contract_status", "掃描檔狀態", "file_ref", "notes",
            ]
            st.dataframe(
                df_view[disp_cols].rename(columns={
                    "id": "編號",
                    "contract_no": "合約編號",
                    "emp_code": "工號",
                    "emp_name": "員工姓名",
                    "dept_name": "部門",
                    "position_name": "職稱",
                    "contract_type": "合約類型",
                    "signed_date": "簽約日",
                    "start_date": "生效日",
                    "到期日顯示": "到期日",
                    "contract_status": "合約狀態",
                    "file_ref": "檔案櫃備註",
                    "notes": "備註",
                }),
                use_container_width=True,
                hide_index=True,
            )

            # 檢視／下載掃描檔或產出合約文字
            st.markdown("##### 📎 查看掃描檔／下載合約檔案")
            c_opts = {
                f"#{r['id']}｜{r['contract_no']}｜{r['emp_name']}（{r['contract_status']}）": int(r["id"])
                for _, r in df_c.iterrows()
            }
            sel_cid = st.selectbox("選擇合約紀錄", list(c_opts.keys()), key="lc_view_sel")
            chosen_row = df_c[df_c["id"] == c_opts[sel_cid]].iloc[0]

            if chosen_row.get("scan_data_b64") and chosen_row.get("scan_file_name"):
                file_bytes = base64.b64decode(chosen_row["scan_data_b64"])
                st.download_button(
                    label=f"⬇️ 下載紙本掃描檔：{chosen_row['scan_file_name']}",
                    data=file_bytes,
                    file_name=chosen_row["scan_file_name"],
                    mime=chosen_row.get("scan_mime_type") or "application/octet-stream",
                    key="btn_dl_scan_file",
                )
                if str(chosen_row.get("scan_mime_type") or "").startswith("image/"):
                    st.image(file_bytes, caption=chosen_row["scan_file_name"], use_container_width=True)
            else:
                st.caption("此筆合約尚未上傳紙本掃描檔。")

            if chosen_row.get("contract_draft_text"):
                with st.expander("📄 查看此筆存檔的雙語合約內容"):
                    st.code(chosen_row["contract_draft_text"], language="text")

            st.markdown("##### 🔄 合約狀態變更（續簽／終止／註記）")
            u1, u2, u3 = st.columns([3, 2, 1.5])
            with u1:
                st.text_input("目前選定合約", value=sel_cid, disabled=True, key="lc_upd_disp")
            with u2:
                new_st = st.selectbox("更新狀態", CONTRACT_STATUSES, key="lc_upd_status")
            with u3:
                st.write("")
                if st.button("更新狀態", type="secondary", use_container_width=True, key="btn_lc_upd"):
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("""
                                    UPDATE public.hr_labor_contracts
                                    SET contract_status = :cst, updated_at = CURRENT_TIMESTAMP
                                    WHERE id = :cid
                                """),
                                {"cst": new_st, "cid": c_opts[sel_cid]},
                            )
                        st.success("✅ 已更新合約狀態。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 更新狀態失敗：{e}")


def render(engine=None, lang="zh", **kwargs):
    tid = st.session_state.get("tenant_id", "REETECH_VN")
    cur_lang = lang or st.session_state.get("current_lang", "zh")
    render_labor_contract_panel(engine=engine, tenant_id=tid, lang=cur_lang)


def show(engine=None, lang="zh", **kwargs):
    return render(engine=engine, lang=lang, **kwargs)
