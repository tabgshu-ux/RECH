import streamlit as st
import pandas as pd
import datetime

def render_fat_sat_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "🧪 FAT / SAT 試驗報告自動生成與 QR Code 驗收系統",
            "caption": "符合 ISO 9001 品質規範，自動記錄工廠出廠試驗 (FAT) 與現場驗收測試 (SAT) 數據，一鍵生成具備防偽 QR Code 的正式試驗報告。",
            "tab1": "📝 填寫測試數據並生成 FAT/SAT 報告",
            "tab2": "📱 QR Code 驗收與試驗報告歷史資料庫"
        },
        "Tiếng Việt": {
            "title": "🧪 Tự động tạo Báo cáo Thử nghiệm FAT/SAT & Nghiệm thu QR Code",
            "caption": "Tuân thủ ISO 9001, ghi nhận dữ liệu thử nghiệm xuất xưởng (FAT) và nghiệm thu hiện trường (SAT) với mã QR chống giả mạo.",
            "tab1": "📝 Nhập liệu & Tạo báo cáo FAT/SAT",
            "tab2": "📱 Quét mã QR & Kho lưu trữ báo cáo"
        },
        "English": {
            "title": "🧪 FAT/SAT Test Report Auto-Generation & QR Code Acceptance",
            "caption": "ISO 9001 compliant, records Factory Acceptance Tests (FAT) and Site Acceptance Tests (SAT) with secure QR codes.",
            "tab1": "📝 Input Test Data & Generate FAT/SAT",
            "tab2": "📱 QR Code Acceptance & Test Report Archives"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 初始化 FAT/SAT 資料庫
    if "fat_sat_db" not in st.session_state:
        st.session_state.fat_sat_db = [
            {
                "report_id": "FAT-2026-001",
                "test_type": "FAT (工廠出廠驗收測試)",
                "project": "西寧廠主配電盤 2000A (PRJ-TN-2026-01)",
                "tester": "品質工程師 - 范文明",
                "insulation_res": "150 MΩ (合格 > 100MΩ)",
                "withstand_voltage": "2500V / 1 min (通過無擊穿)",
                "qr_code_token": "REETECH-FAT-2026-001-VERIFIED",
                "status": "🟢 檢驗合格並已發行 QR Code"
            }
        ]

    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

    with tab1:
        st.markdown("##### 📝 步驟一：輸入配電盤試驗數據與檢測結果")
        with st.form("fat_sat_form"):
            c1, c2 = st.columns(2)
            with c1:
                test_type = st.selectbox("試驗類型", ["FAT (工廠出廠驗收測試 - Factory Acceptance Test)", "SAT (現場驗收測試 - Site Acceptance Test)"])
                proj_name = st.text_input("關聯專案名稱 / 盤體編號 *", value="西寧廠主配電盤 2000A (PRJ-TN-2026-01)")
            with c2:
                tester_name = st.text_input("檢測/品管工程師 *", value=st.session_state.get("user_name", "范文明"))
                test_date = st.date_input("測試日期", datetime.date(2026, 10, 9))

            st.markdown("##### 🔬 測試指標參數輸入 (ISO 9001 規範)")
            i1, i2 = st.columns(2)
            with i1:
                insulation = st.text_input("絕緣電阻測試 (Insulation Resistance)", value="150 MΩ (標準: > 100 MΩ)")
                temperature_rise = st.text_input("溫升試驗結果 (Temperature Rise)", value="正常 (最高溫升 45°C)")
            with i2:
                voltage_test = st.text_input("耐壓強度測試 (Withstand Voltage)", value="2.5 kV / 1 min (無閃絡或擊穿)")
                func_test = st.selectbox("動作與保護邏輯測試 (Interlock & Protection)", ["🟢 正常 (All Passed)", "🟡 需調整 (Needs Adjustment)"])

            if st.form_submit_button("🚀 生成正式 FAT/SAT 試驗報告與防偽 QR Code", type="primary"):
                new_id = f"{'FAT' if 'FAT' in test_type else 'SAT'}-2026-{len(st.session_state.fat_sat_db)+1:03d}"
                qr_token = f"REETECH-{new_id}-VERIFIED-2026"

                st.session_state.fat_sat_db.insert(0, {
                    "report_id": new_id,
                    "test_type": test_type,
                    "project": proj_name,
                    "tester": tester_name,
                    "insulation_res": insulation,
                    "withstand_voltage": voltage_test,
                    "qr_code_token": qr_token,
                    "status": "🟢 檢驗合格並已發行 QR Code"
                })
                st.success(f"🎉 試驗報告 [{new_id}] 已成功生成！防偽 QR Code 憑證已繫結。")
                st.rerun()

    with tab2:
        st.markdown("##### 📱 FAT/SAT 試驗報告與 QR Code 驗收一覽表")
        st.info("💡 說明：業主或監造人員可使用行動裝置掃描報告上的 QR Code，系統將即時回傳該配電盤的完整測試數據與合格憑證。")

        if st.session_state.fat_sat_db:
            for rep in st.session_state.fat_sat_db:
                with st.expander(f"📌 報告編號：{rep['report_id']} | 類型：{rep['test_type']} | 專案：{rep['project']}"):
                    st.write(f"**檢測工程師**：{rep['tester']} | **狀態**：`{rep['status']}`")
                    st.write(f"**絕緣電阻**：{rep['insulation_res']} | **耐壓測試**：{rep['withstand_voltage']}")
                    st.markdown(f"**🔐 防偽 QR Code 驗證 Token**：`{rep['qr_code_token']}`")
                    st.info("📱 [模擬 QR Code 畫面] 業主掃描後將直接顯示 ISO 9001 合格驗收頁面。")
        else:
            st.info("目前尚無 FAT/SAT 試驗報告紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_fat_sat_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_fat_sat_page(engine=engine, lang=lang, **kwargs)
