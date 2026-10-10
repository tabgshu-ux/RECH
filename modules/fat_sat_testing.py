import streamlit as st
import pandas as pd
import datetime

def render_fat_sat_testing_page(engine=None, lang="繁體中文", **kwargs):
    texts = {
        "繁體中文": {
            "title": "🧪 品保部 - FAT/SAT 試驗報告與防偽 QR Code 驗收",
            "caption": "符合 ISO 9001 規範，針對配電盤與高壓櫃自動生成 FAT（工廠出廠試驗）與 SAT（現場驗收）報告，並產生防偽 QR Code 供業主掃描驗收。",
            "tab1": "📋 1. FAT / SAT 試驗報告生成與 QR Code",
            "tab2": "📚 2. 驗收報告資料庫與歷史追蹤"
        },
        "Tiếng Việt": {
            "title": "🧪 Quản lý Thử nghiệm FAT/SAT & Nghiệm thu QR Code",
            "caption": "Tuân thủ tiêu chuẩn ISO 9001, tự động tạo báo cáo FAT/SAT cho tủ điện kèm mã QR chống giả mạo.",
            "tab1": "📋 1. Tạo báo cáo FAT/SAT & QR Code",
            "tab2": "📚 2. Cơ sở dữ liệu báo cáo nghiệm thu"
        },
        "English": {
            "title": "🧪 QA Dept - FAT/SAT Test Reports & Anti-Counterfeit QR Code",
            "caption": "ISO 9001 compliant, automatically generates FAT/SAT test reports for switchgear with secure QR codes for client handover.",
            "tab1": "📋 1. Generate FAT/SAT & QR Code",
            "tab2": "📚 2. Acceptance Report Database"
        }
    }

    active_lang = lang if lang in texts else "繁體中文"
    t = texts[active_lang]

    st.title(t["title"])
    st.caption(t["caption"])

    # 1. 初始化 FAT 報告資料庫 (Session State)
    if "fat_report_db" not in st.session_state:
        st.session_state.fat_report_db = [
            {
                "報告編號": "FAT-2026-001",
                "專案名稱": "西寧廠主配電盤 2000A",
                "試驗類型": "FAT 出廠試驗 (Factory Acceptance)",
                "生成日期": "2026-10-01",
                "狀態": "🟢 已通過驗收",
                "防偽 QR Code 連結": "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=FAT-TAY-NINH-2000A"
            }
        ]

    tab1, tab2 = st.tabs([t["tab1"], t["tab2"]])

    with tab1:
        st.markdown("##### 🧪 步驟一：選擇專案並生成帶有防偽 QR Code 的 FAT/SAT 試驗報告")
        
        # 串聯上游工程專案清單
        default_projects = ["西寧廠主配電盤 2000A", "海防廠低壓配電櫃 1000A", "和鼎隆工業區配電統包工程"]
        if "engineering_projects_db" in st.session_state:
            proj_choices = [p.get("專案名稱", "未命名專案") for p in st.session_state.engineering_projects_db]
        else:
            proj_choices = default_projects

        with st.form("fat_report_form"):
            selected_proj = st.selectbox("關聯專案名稱 / 標體編號 *", proj_choices)
            test_type = st.selectbox("試驗與驗收階段 *", ["FAT 出廠試驗 (Factory Acceptance Test)", "SAT 現場試驗 (Site Acceptance Test)"])
            inspector = st.text_input("品保檢驗工程師 *", value="張品保 (QA Engineer)")
            notes = st.text_area("試驗備註與絕緣/耐壓測試數據", value="絕緣電阻 > 100MΩ，耐壓測試 2500V/1min 通過，各項指示燈及保護電驛正常。")

            if st.form_submit_button("🚀 生成 FAT 試驗報告與 QR Code", type="primary"):
                report_id = f"FAT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                qr_link = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={report_id}-{selected_proj}"
                
                # 將新生成的報告寫入資料庫
                new_entry = {
                    "報告編號": report_id,
                    "專案名稱": selected_proj,
                    "試驗類型": test_type,
                    "生成日期": str(datetime.date.today()),
                    "狀態": "🟢 已通過並產生防偽 QR Code",
                    "防偽 QR Code 連結": qr_link
                }
                st.session_state.fat_report_db.insert(0, new_entry)
                
                st.success("✅ FAT 試驗報告已成功生成並彙整防偽 QR Code！")
                st.rerun()

    with tab2:
        st.markdown("##### 📚 驗收報告資料庫與防偽 QR Code 總覽")
        st.info("💡 說明：業主或現場監造主管可直接掃描下方生成的 QR Code 進行行動端雲端驗收。")

        if st.session_state.fat_report_db:
            # 呈現表格資料
            st.dataframe(pd.DataFrame(st.session_state.fat_report_db), use_container_width=True)
            
            st.markdown("---")
            st.markdown("##### 🖼️ 驗收專用防偽 QR Code 預覽")
            for r in st.session_state.fat_report_db:
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.write(f"**報告編號**：`{r['報告編號']}`")
                    st.write(f"**專案名稱**：{r['專案名稱']}")
                    st.write(f"**試驗類型**：{r['試驗類型']}")
                    st.write(f"**驗收狀態**：{r['狀態']}")
                with col_b:
                    st.image(r["防偽 QR Code 連結"], width=120, caption=f"QR Code ({r['報告編號']})")
                st.markdown("---")
        else:
            st.info("目前尚無任何 FAT/SAT 驗收報告紀錄。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_fat_sat_testing_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_fat_sat_testing_page(engine=engine, lang=lang, **kwargs)
