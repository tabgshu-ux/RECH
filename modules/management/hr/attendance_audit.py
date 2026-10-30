import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_management_attendance_audit(engine, lang="繁體中文"):
    st.markdown("### 📊 管理部專用：外勤出勤與薪資稽核中心")
    st.info("💡 說明：管理部後勤人員可在此檢視各工地的即時打卡人數、工人姓名、打卡時間與現場照片，作為薪資計算與出勤佐證之依據。（註：案場 GPS 範圍與圍籬設定請至【工程管理部】設定）")

    # 讀取打卡紀錄與工地人數
    logs = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM field_punch_logs ORDER BY punch_time DESC")).fetchall()
                for r in res:
                    logs.append({
                        "punch_id": r[0], "emp_id": r[1], "emp_name": r[2],
                        "site_name": r[3], "type": r[4], "lat": r[5], "lng": r[6],
                        "dist_m": r[7], "photo": r[8], "time": r[9], "status": r[10], "note": r[11]
                    })
        except Exception:
            pass

    if logs:
        df_logs = pd.DataFrame(logs)
        
        # 簡易即時工地人數統計
        st.markdown("##### 🏗️ 各工地今日即時出勤人數統計")
        if not df_logs.empty:
            site_counts = df_logs.groupby("site_name")["emp_id"].nunique().reset_index()
            site_counts.columns = ["工程案場名稱", "不重複打卡人數"]
            st.dataframe(site_counts, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 📋 全體外勤人員打卡明細與現場照片查驗 (薪資計算用)")
        for log in logs:
            with st.expander(f"🕒 [{log['time']}] 案場: {log['site_name']} ➔ 員工: {log['emp_name']} ({log['emp_id']}) [{log['type']}]"):
                c_img, c_det = st.columns([1, 2])
                with c_img:
                    if log["photo"] and str(log["photo"]).startswith("http"):
                        st.image(log["photo"], width=160, caption="現場打卡照片")
                    else:
                        st.markdown("📷 `無照片`")
                with c_det:
                    st.write(f"- **員工工號**: `{log['emp_id']}`")
                    st.write(f"- **員工姓名**: **{log['emp_name']}**")
                    st.write(f"- **打卡類型**: {log['type']}")
                    st.write(f"- **GPS 座標**: ({log['lat']}, {log['lng']})")
                    st.write(f"- **距離案場中心**: {log['dist_m']} 公尺")
                    st.write(f"- **工作備註**: {log['note']}")
                    st.markdown(f"- **狀態**: :{ 'green' if '合格' in log['status'] else 'red' }[{log['status']}]")
            st.markdown("---")
    else:
        st.info("目前尚無外勤打卡紀錄可供稽核。")
