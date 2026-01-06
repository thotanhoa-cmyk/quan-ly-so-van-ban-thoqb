import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- CẤU HÌNH ---
MA_TRUONG = "THQOB"
LOGO_URL = "https://i.postimg.cc/mD83m8Yn/logo-edu.png" 
URL_DATA = "https://docs.google.com/spreadsheets/d/1VQZ4uFtvb0Ur4livO5qPy5HGRntETgUOjnGpfgqDXtc/edit?usp=sharing"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"
WEB_URL = "https://sovanbandiqob.streamlit.app/"

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- KẾT NỐI ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=2)
def load_data_cached():
    # Đọc dữ liệu bằng URL trực tiếp để tránh lỗi đồng bộ
    df_vb = conn.read(spreadsheet=URL_DATA, worksheet="0")
    df_us = conn.read(spreadsheet=URL_USERS, worksheet="0")
    return df_vb, df_us

df_vanban, df_users = load_data_cached()

# --- ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        try: st.image(LOGO_URL, width=150)
        except: pass
        st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>TRƯỜNG TIỂU HỌC QUỐC OAI B</h1>", unsafe_allow_html=True)
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
    with st.sidebar:
        st.info(f"Cán bộ: **{st.session_state.user_name}**")
        st.divider()
        st.markdown("<p style='text-align: center;'>📷 QR TRUY CẬP</p>", unsafe_allow_html=True)
        st.image(f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={WEB_URL}", use_container_width=True)
        st.divider()
        menu = st.radio("CHỨC NĂNG", ["🚀 Cấp số văn bản", "🔍 Nhật ký & Quản lý", "📊 Báo cáo tháng", "⚙️ Quản trị Admin"])
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()

    # 1. CẤP SỐ VĂN BẢN
    if menu == "🚀 Cấp số văn bản":
        st.header("🚀 Cấp số văn bản mới")
        with st.form("form_cap_so"):
            loai_chon = st.selectbox("📁 Loại văn bản", ["Công văn", "Quyết định", "Tờ trình", "Thông báo", "Báo cáo", "Giấy mời", "Biên bản", "Kế hoạch", "Hợp đồng", "Quy chế"])
            trich_yeu = st.text_area("📝 Trích yếu nội dung")
            ngay_vb = st.date_input("📅 Ngày văn bản", date.today())
            
            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                if not trich_yeu.strip():
                    st.error("Vui lòng nhập trích yếu!")
                else:
                    # Logic lấy số
                    ky_hieu_dict = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
                    ky_hieu = ky_hieu_dict[loai_chon]
                    so_moi = len(df_vanban[df_vanban["Loại văn bản"] == loai_chon]) + 1
                    so_hieu = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                    
                    new_row = pd.DataFrame([{
                        "Loại văn bản": loai_chon, "Số hiệu": so_hieu, "Ngày văn bản": ngay_vb.strftime("%d/%m/%Y"),
                        "Trích yếu": trich_yeu.strip(), "Người thực hiện": st.session_state.user_name,
                        "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"), "Tháng": ngay_vb.strftime("%m/%Y")
                    }])
                    
                    try:
                        # Cập nhật dữ liệu
                        updated_df = pd.concat([df_vanban, new_row], ignore_index=True)
                        # SỬ DỤNG PHƯƠNG THỨC CẬP NHẬT CƯỠNG ÉP
                        conn.update(spreadsheet=URL_DATA, data=updated_df)
                        st.cache_data.clear()
                        st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu}")
                        st.balloons()
                    except Exception as e:
                        st.error("Hệ thống vẫn chặn quyền ghi.")
                        st.info("Vui lòng kiểm tra lại file Google Sheet: Nút Chia sẻ -> Bất kỳ ai có link -> Phải chọn là 'Người chỉnh sửa'.")

    # 2. NHẬT KÝ
    elif menu == "🔍 Nhật ký & Quản lý":
        st.dataframe(df_vanban, use_container_width=True, hide_index=True)

    # 3. BÁO CÁO
    elif menu == "📊 Báo cáo tháng":
        if not df_vanban.empty:
            list_thang = sorted(df_vanban["Tháng"].unique(), reverse=True)
            thang = st.selectbox("Chọn tháng:", list_thang)
            st.dataframe(df_vanban[df_vanban["Tháng"] == thang], use_container_width=True)
