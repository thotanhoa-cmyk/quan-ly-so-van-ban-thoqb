import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- CẤU HÌNH ---
MA_TRUONG = "THQOB"
# Sử dụng link logo dự phòng ổn định hơn
LOGO_URL = "ESTD2.png" 
URL_DATA = "https://docs.google.com/spreadsheets/d/1VQZ4uFtvb0Ur4livO5qPy5HGRntETgUOjnGpfgqDXtc/edit?usp=sharing"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"

LOAI_VB_DICT = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
DANH_SACH_NGUOI_KY = ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"]
DANH_SACH_CHUC_VU = ["Hiệu trưởng", "Phó Hiệu trưởng"]

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- KẾT NỐI DỮ LIỆU TỐI ƯU ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=10)
def load_data_cached():
    df_vb = conn.read(spreadsheet=URL_DATA, worksheet="0")
    df_us = conn.read(spreadsheet=URL_USERS, worksheet="0")
    return df_vb, df_us

df_vanban, df_users = load_data_cached()

# --- CSS ---
st.markdown("""<style>.main { background-color: #f0f2f6; } .stButton>button { border-radius: 8px; font-weight: bold; background-color: #1e3a8a; color: white; } h1, h2 { color: #1e3a8a !important; text-align: center; }</style>""", unsafe_allow_html=True)

# --- ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        try: st.image(LOGO_URL, width=150)
        except: st.markdown("## 🏫 TH QUỐC OAI B")
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
    with st.sidebar:
        try: st.image(LOGO_URL, width=100)
        except: pass
        st.info(f"Cán bộ: **{st.session_state.user_name}**")
        # Tìm đoạn này trong file app.py của bạn:
    with st.sidebar:
        try: 
            st.image(LOGO_URL, width=100)
        except: 
            pass
        st.info(f"Cán bộ: **{st.session_state.user_name}**")
                # --- ĐOẠN MÃ QR MỚI CHÈN VÀO ĐÂY ---
        st.divider()
        st.markdown("<p style='text-align: center; font-weight: bold;'>📷 QUÉT QR TRÊN DI ĐỘNG</p>", unsafe_allow_html=True)
        
        # Link tạo mã QR tự động
        qr_link = "https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=https://sovanbandiqob.streamlit.app/"
        st.image(qr_link, caption="Mở Zalo để quét mã", use_container_width=True)
        st.divider()
        # --- HẾT ĐOẠN QR ---

        menu = st.radio("CHỨC NĂNG", ["🚀 Lấy số văn bản", "🔍 Nhật ký & Quản lý", "📊 Báo cáo tháng", "⚙️ Quản trị Admin"])
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()
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
                elif not trich_yeu.strip():
                    st.error("Vui lòng nhập trích yếu!")
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
                    st.cache_data.clear()
                    st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu_final}")
                    st.rerun()

    # 2. NHẬT KÝ & XÓA
    elif menu == "🔍 Nhật ký & Quản lý":
        st.markdown("<h1>🔍 Nhật ký văn bản</h1>", unsafe_allow_html=True)
        search = st.text_input("🔍 Tìm kiếm nhanh...")
        df_show = df_vanban.copy()
        if search:
            df_show = df_show[df_show.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        
        if st.session_state.user_id == "admin":
            st.divider()
            st.subheader("🛠 QUYỀN ADMIN: XÓA SỐ")
            so_xoa = st.text_input("Nhập Số hiệu chính xác để xóa:")
            if st.button("❌ Xác nhận xóa"):
                updated_df = df_vanban[df_vanban["Số hiệu"] != so_xoa]
                conn.update(spreadsheet=URL_DATA, data=updated_df)
                st.cache_data.clear()
                st.success("Đã xóa!")
                st.rerun()

    # 3. BÁO CÁO THÁNG (ĐÃ PHỤC HỒI)
    elif menu == "📊 Báo cáo tháng":
        st.markdown("<h1>📊 Báo cáo quản trị</h1>", unsafe_allow_html=True)
        if not df_vanban.empty:
            list_thang = sorted(df_vanban["Tháng"].unique(), reverse=True)
            thang_chon = st.selectbox("Chọn tháng báo cáo:", list_thang)
            df_thang = df_vanban[df_vanban["Tháng"] == thang_chon]
            
            c1, c2 = st.columns(2)
            with c1: st.metric(f"Văn bản tháng {thang_chon}", len(df_thang))
            with c2:
                csv = df_thang.to_csv(index=False).encode('utf-8-sig')
                st.download_button(f"📥 Tải báo cáo Excel tháng {thang_chon}", data=csv, file_name=f"BC_{thang_chon}.csv")
            st.dataframe(df_thang, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu.")

    # 4. QUẢN TRỊ ADMIN (ĐÃ PHỤC HỒI)
    elif menu == "⚙️ Quản trị Admin":
        if st.session_state.user_id == "admin":
            st.markdown("<h1>⚙️ Quản lý tài khoản</h1>", unsafe_allow_html=True)
            st.dataframe(df_users, hide_index=True)
            st.divider()
            st.subheader("🔑 Reset mật khẩu người dùng")
            user_select = st.selectbox("Chọn tài khoản:", df_users['Username'].tolist())
            new_pass = st.text_input("Mật khẩu mới:", type="password")
            if st.button("Cập nhật mật khẩu"):
                df_users.loc[df_users['Username'] == user_select, 'Password'] = new_pass
                conn.update(spreadsheet=URL_USERS, data=df_users)
                st.success(f"Đã đổi mật khẩu cho {user_select} thành công!")
        else:
            st.warning("Bạn không có quyền truy cập mục này.")
