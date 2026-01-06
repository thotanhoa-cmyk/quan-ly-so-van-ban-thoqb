import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- CẤU HÌNH ---
MA_TRUONG = "THQOB"
LOGO_URL = "ESTD2.png" 
URL_DATA = "https://docs.google.com/spreadsheets/d/1VQZ4uFtvb0Ur4livO5qPy5HGRntETgUOjnGpfgqDXtc/edit?usp=sharing"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"
WEB_URL = "https://sovanbandiqob.streamlit.app/"

LOAI_VB_DICT = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
DANH_SACH_NGUOI_KY = ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"]
DANH_SACH_CHUC_VU = ["Hiệu trưởng", "Phó Hiệu trưởng"]

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- KẾT NỐI SỬ DỤNG SECRETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def load_data_cached():
    # Đọc dữ liệu từ Sheets sử dụng Secrets
    df_vb = conn.read(spreadsheet=URL_DATA, worksheet="0")
    df_us = conn.read(spreadsheet=URL_USERS, worksheet="0")
    return df_vb, df_us

df_vanban, df_users = load_data_cached()

# --- GIAO DIỆN ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        try: st.image(LOGO_URL, width=150)
        except: pass
        st.markdown("<h1 style='text-align: center;'>TRƯỜNG TIỂU HỌC QUỐC OAI B</h1>", unsafe_allow_html=True)
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
    # Sidebar
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

    # --- 1. CẤP SỐ VĂN BẢN ---
    if menu == "🚀 Cấp số văn bản":
        st.header("🚀 Cấp số văn bản mới")
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("📁 Loại văn bản", list(LOAI_VB_DICT.keys()))
                ngay_van_ban = st.date_input("📅 Ngày tháng", date.today())
                nguoi_ky = st.selectbox("✍️ Người ký", DANH_SACH_NGUOI_KY)
            with c2:
                chuc_vu = st.selectbox("🎓 Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("📝 Trích yếu")
            
            if st.session_state.user_id == "admin":
                with st.expander("🛠 Admin chèn số"):
                    is_chen = st.checkbox("Kích hoạt")
                    so_hieu_tuy_chinh = st.text_input("Số hiệu tùy chỉnh")

            if st.form_submit_button("🔥 XÁC NHẬN"):
                if not trich_yeu.strip():
                    st.error("Vui lòng nhập trích yếu!")
                else:
                    ky_hieu = LOAI_VB_DICT[loai_chon]
                    so_moi = len(df_vanban[df_vanban["Loại văn bản"] == loai_chon]) + 1
                    so_hieu = so_hieu_tuy_chinh if (st.session_state.user_id == "admin" and is_chen) else f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                    
                    new_data = pd.DataFrame([{
                        "Loại văn bản": loai_chon, "Số hiệu": so_hieu, "Ngày văn bản": ngay_van_ban.strftime("%d/%m/%Y"),
                        "Trích yếu": trich_yeu.strip(), "Người thực hiện": st.session_state.user_name,
                        "Người ký": nguoi_ky, "Chức vụ": chuc_vu, "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tháng": ngay_van_ban.strftime("%m/%Y")
                    }])
                    
                    try:
                        # Ghi dữ liệu lên Sheets
                        updated_df = pd.concat([df_vanban, new_data], ignore_index=True)
                        conn.update(spreadsheet=URL_DATA, data=updated_df)
                        st.cache_data.clear()
                        st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu}")
                        st.balloons()
                    except Exception as e:
                        st.error("Lỗi: Không có quyền ghi. Hãy kiểm tra xem bạn đã đặt Google Sheet ở chế độ 'Editor' (Người chỉnh sửa) chưa?")

    # --- 2. NHẬT KÝ ---
    elif menu == "🔍 Nhật ký & Quản lý":
        st.header("🔍 Nhật ký văn bản")
        st.dataframe(df_vanban, use_container_width=True, hide_index=True)
        if st.session_state.user_id == "admin":
            st.divider()
            so_xoa = st.text_input("Nhập số hiệu cần xóa:")
            if st.button("Xóa dòng này"):
                df_new = df_vanban[df_vanban["Số hiệu"] != so_xoa]
                conn.update(spreadsheet=URL_DATA, data=df_new)
                st.cache_data.clear()
                st.rerun()

    # --- 3. BÁO CÁO ---
    elif menu == "📊 Báo cáo tháng":
        st.header("📊 Báo cáo")
        if not df_vanban.empty:
            list_thang = sorted(df_vanban["Tháng"].unique(), reverse=True)
            thang = st.selectbox("Chọn tháng:", list_thang)
            df_th = df_vanban[df_vanban["Tháng"] == thang]
            st.metric("Số lượng văn bản", len(df_th))
            st.dataframe(df_th, use_container_width=True)
            csv = df_th.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải về Excel", data=csv, file_name=f"BC_{thang}.csv")

    # --- 4. ADMIN ---
    elif menu == "⚙️ Quản trị Admin":
        if st.session_state.user_id == "admin":
            st.header("⚙️ Quản lý mật khẩu")
            st.dataframe(df_users, hide_index=True)
            u_sel = st.selectbox("Chọn tài khoản:", df_users['Username'].tolist())
            p_new = st.text_input("Mật khẩu mới:", type="password")
            if st.button("Đổi mật khẩu"):
                df_users.loc[df_users['Username'] == u_sel, 'Password'] = p_new
                conn.update(spreadsheet=URL_USERS, data=df_users)
                st.success("Đã cập nhật!")
