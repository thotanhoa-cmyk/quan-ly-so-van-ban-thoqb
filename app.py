import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- CẤU HÌNH ---
MA_TRUONG = "THQOB"
LOGO_URL = ""
URL_DATA = "https://docs.google.com/spreadsheets/d/1VQZ4uFtvb0Ur4livO5qPy5HGRntETgUOjnGpfgqDXtc/edit?usp=sharing"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"

LOAI_VB_DICT = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
DANH_SACH_NGUOI_KY = ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"]
DANH_SACH_CHUC_VU = ["Hiệu trưởng", "Phó Hiệu trưởng"]

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- KẾT NỐI DỮ LIỆU TỐI ƯU ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Dùng cache để không phải load đi load lại mỗi khi bấm nút
@st.cache_data(ttl=10) # Dữ liệu sẽ được làm mới sau mỗi 10 giây nếu có thay đổi
def load_data_cached():
    df_vb = conn.read(spreadsheet=URL_DATA, worksheet="0")
    df_us = conn.read(spreadsheet=URL_USERS, worksheet="0")
    return df_vb, df_us

df_vanban, df_users = load_data_cached()

# --- CSS ---
st.markdown("""<style>.main { background-color: #f0f2f6; } .stButton>button { border-radius: 8px; font-weight: bold; background-color: #1e3a8a; color: white; }</style>""", unsafe_allow_html=True)

# --- ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        st.image(LOGO_URL, width=150)
        st.markdown("<h1>TRƯỜNG TIỂU HỌC QUỐC OAI B</h1>", unsafe_allow_html=True)
        u_input = st.text_input("👤 Tên đăng nhập")
        p_input = st.text_input("🔑 Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            user_row = df_users[df_users['Username'].astype(str) == u_input]
            if not user_row.empty and str(user_row.iloc[0]['Password']) == p_input:
                st.session_state["user_id"] = u_input
                st.session_state["user_name"] = user_row.iloc[0]['Fullname']
                st.rerun()
            else: st.error("Sai tài khoản hoặc mật khẩu!")
else:
    # --- GIAO DIỆN CHÍNH ---
    with st.sidebar:
        st.image(LOGO_URL, width=100)
        st.info(f"Cán bộ: **{st.session_state.user_name}**")
        st.divider()
        menu = st.radio("CHỨC NĂNG", ["🚀 Cấp số văn bản", "🔍 Nhật ký & Quản lý", "📊 Báo cáo tháng", "⚙️ Quản trị Admin"])
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()

    # 1. CẤP SỐ VĂN BẢN
    if menu == "🚀 Cấp số văn bản":
        st.markdown("<h1>🚀 Cấp số văn bản mới</h1>", unsafe_allow_html=True)
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("📁 Loại văn bản", list(LOAI_VB_DICT.keys()))
                ngay_van_ban = st.date_input("📅 Ngày tháng văn bản", date.today())
                nguoi_ky = st.selectbox("✍️ Người ký", DANH_SACH_NGUOI_KY)
            with c2:
                chuc_vu = st.selectbox("🎓 Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("📝 Trích yếu nội dung")
            
            if st.session_state.user_id == "admin":
                with st.expander("🛠 Chế độ Admin"):
                    is_chen = st.checkbox("Kích hoạt chèn số")
                    so_hieu_tuy_chinh = st.text_input("Nhập số hiệu (Vd: 01a/BC-THQOB)")

            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                trich_yeu_moi = trich_yeu.strip().lower()
                is_dup = df_vanban['Trích yếu'].astype(str).str.lower().str.strip().eq(trich_yeu_moi).any()
                
                if is_dup and st.session_state.user_id != "admin":
                    st.error("🚫 Nội dung này đã lấy số trước đó!")
                else:
                    if st.session_state.user_id == "admin" and is_chen and so_hieu_tuy_chinh:
                        so_hieu_final = so_hieu_tuy_chinh
                    else:
                        ky_hieu = LOAI_VB_DICT[loai_chon]
                        so_moi = len(df_vanban[df_vanban["Loại văn bản"] == loai_chon]) + 1
                        so_hieu_final = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                    
                    new_row = pd.DataFrame([{"Loại văn bản": loai_chon, "Số hiệu": so_hieu_final, "Ngày văn bản": ngay_van_ban.strftime("%d/%m/%Y"), "Trích yếu": trich_yeu.strip(), "Người thực hiện": st.session_state.user_name, "Người ký": nguoi_ky, "Chức vụ": chuc_vu, "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"), "Tháng": ngay_van_ban.strftime("%m/%Y")}])
                    
                    updated_df = pd.concat([df_vanban, new_row], ignore_index=True)
                    conn.update(spreadsheet=URL_DATA, data=updated_df)
                    st.cache_data.clear() # Xóa cache để cập nhật dữ liệu mới ngay lập tức
                    st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu_final}")
                    st.rerun()

    # 2. NHẬT KÝ & XÓA
    elif menu == "🔍 Nhật ký & Quản lý":
        st.markdown("<h1>🔍 Nhật ký văn bản</h1>", unsafe_allow_html=True)
        st.dataframe(df_vanban, use_container_width=True, hide_index=True)
        if st.session_state.user_id == "admin":
            st.divider()
            so_xoa = st.text_input("Nhập Số hiệu chính xác để xóa:")
            if st.button("❌ Xác nhận xóa"):
                updated_df = df_vanban[df_vanban["Số hiệu"] != so_xoa]
                conn.update(spreadsheet=URL_DATA, data=updated_df)
                st.cache_data.clear()
                st.success("Đã xóa!")
                st.rerun()

    # (Các phần Báo cáo và Admin Reset mật khẩu giữ nguyên logic cũ)
