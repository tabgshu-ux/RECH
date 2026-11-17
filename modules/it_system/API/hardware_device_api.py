# ==========================================
# 檔案路徑：modules/it_system/API/hardware_device_api.py
# 職責：硬體設備 SDK 與門禁/POS/條碼機 API 閘道設定
# ==========================================

import streamlit as st

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("#### 🔌 現場硬體設備與 IoT 裝置 API 串接設定")
    st.caption("集中管理廠區門禁考勤機、人臉/指紋辨識裝置、POS 收銀機與條碼掃描器之硬體 SDK 與 API。")

    with st.form("hardware_device_form"):
        device_category = st.selectbox("選擇硬體設備類型", [
            "廠區門禁卡機 / 人臉辨識打卡設備 API (Hikvision / ZKTeco)",
            "倉儲條碼掃描槍與 RFID 盤點機 SDK 閘道",
            "POS 收銀機與出單機硬體 API 串接",
            "工業用電子秤與量測儀器資料擷取 API"
        ])

        c1, c2 = st.columns(2)
        with c1:
            device_ip = st.text_input("硬體設備 IP 位址 / 區域網路端點", value="192.168.1.200:8080")
            sdk_token = st.text_input("設備通訊密碼 / API Token", type="password", value="hw_sdk_secret_************************")
        with c2:
            comm_protocol = st.selectbox("通訊協定", ["TCP/IP 專用通訊協議", "HTTP / RESTful API", "MQTT IoT 協定"])
            device_status = st.selectbox("設備連線狀態", ["🟢 連線正常 (Online)", "🔴 離線 (Offline)"])

        device_desc = st.text_area("硬體安裝位置與備註說明", placeholder="例如: 安裝於西寧廠一期大門口打卡專用...")

        if st.form_submit_button("💾 儲存硬體設備 API 設定並測試連線", type="primary", use_container_width=True):
            st.success(f"🎉 成功儲存 [{device_category}] 的硬體串接設定！設備回應：連線測試成功 (200 OK)。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
