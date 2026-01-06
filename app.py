import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- 1. CẤU HÌNH HỆ THỐNG ---
MA_TRUONG = "THQOB"
LOGO_URL = "ESTD2.png"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"
WEB_URL = "https://sovanbandiqob.streamlit.app/"
DANH_SACH_LOAI = ["Công văn", "Quyết định", "Tờ trình", "Thông báo", "Báo cáo", "Giấy mời", "Biên bản", "Kế hoạch", "Hợp đồng", "Quy chế"]

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- 2. KẾT NỐI DỮ LIỆU TỐI ƯU ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600)
def load_data_fast():
    df_vb = conn.read(worksheet="Data")
    df_us = conn.read(spreadsheet=URL_USERS, worksheet="Sheet1")
    return df_vb, df_us

df_vanban, df_users = load_data_fast()

# --- 3. CSS GIAO DIỆN ---
st.markdown("""<style>.main { background-color: #f0f2f6; } .stButton>button { border-radius: 8px; font-weight: bold; background-color: #1e3a8a; color: white; }</style>""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# --- 4. KIỂM TRA ĐĂNG NHẬP ---
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
    with st.sidebar:
        st.image(LOGO_URL, width=80)
        st.info(f"Cán bộ: **{st.session_state.user_name}**")
        st.divider()
        st.markdown("<p style='text-align: center;'>📷 QR TRUY CẬP</p>", unsafe_allow_html=True)
        st.image(f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={WEB_URL}")
        st.divider()
        menu = st.radio("CHỨC NĂNG", ["🚀 Cấp số văn bản", "🔍 Nhật ký & Quản lý", "📊 Báo cáo tháng", "⚙️ Quản trị Admin"])
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()

    # --- CHỨC NĂNG 1: CẤP SỐ VĂN BẢN ---
    if menu == "🚀 Cấp số văn bản":
        st.header("🚀 Cấp số văn bản mới")
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("📁 Loại văn bản", DANH_SACH_LOAI)
                ngay_vb = st.date_input("📅 Ngày văn bản", date.today())
                nguoi_ky = st.selectbox("✍️ Người ký", ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"])
            with c2:
                chuc_vu = st.selectbox("🎓 Chức vụ", ["Hiệu trưởng", "Phó Hiệu trưởng"])
                trich_yeu = st.text_area("📝 Trích yếu nội dung")
            
            if st.session_state.user_id == "admin":
                with st.expander("🛠 Admin: Chèn số hiệu tùy chỉnh"):
                    is_chen = st.checkbox("Kích hoạt chèn số")
                    so_hieu_tuy_chinh = st.text_input("Số hiệu tùy chỉnh (Vd: 01a/BC-THQOB)")

            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                # 1. Kiểm tra để trống
                if not trich_yeu.strip():
                    st.error("⚠️ Vui lòng nhập trích yếu!")
                # 2. KIỂM TRA TRÙNG TRÍCH YẾU (Tính năng mới bổ sung)
                elif not df_vanban.empty and trich_yeu.strip() in df_vanban["Trích yếu"].values:
                    st.warning("❌ Nội dung trích yếu này đã được cấp số rồi. Vui lòng kiểm tra lại nhật ký!")
                else:
                    ky_hieu_dict = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
                    ky_hieu = ky_hieu_dict[loai_chon]
                    
                    if st.session_state.user_id == "admin" and is_chen and so_hieu_tuy_chinh:
                        so_hieu_final = so_hieu_tuy_chinh
                    else:
                        so_moi = len(df_vanban[df_vanban["Loại văn bản"] == loai_chon]) + 1
                        so_hieu_final = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                    
                    new_row = pd.DataFrame([{
                        "Loại văn bản": loai_chon, "Số hiệu": so_hieu_final, "Ngày văn bản": ngay_vb.strftime("%d/%m/%Y"),
                        "Trích yếu": trich_yeu.strip(), "Người thực hiện": st.session_state.user_name,
                        "Người ký": nguoi_ky, "Chức vụ": chuc_vu, "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"), "Tháng": ngay_vb.strftime("%m/%Y")
                    }])
                    
                    conn.update(worksheet="Data", data=pd.concat([df_vanban, new_row], ignore_index=True))
                    st.cache_data.clear()
                    st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu_final}")
                    st.rerun()

        # TRA CỨU NHANH
        st.divider()
        st.subheader("📑 Tra cứu số hiệu đã cấp")
        tab_names = ["Tất cả"] + DANH_SACH_LOAI
        tabs = st.tabs(tab_names)
        for i, tab in enumerate(tabs):
            with tab:
                if tab_names[i] == "Tất cả":
                    df_tab = df_vanban.tail(10)[::-1]
                else:
                    df_tab = df_vanban[df_vanban["Loại văn bản"] == tab_names[i]].sort_values(by="Số hiệu", ascending=False)
                if not df_tab.empty:
                    st.table(df_tab[["Số hiệu", "Ngày văn bản", "Trích yếu", "Người ký"]].head(10))
                else:
                    st.info(f"Chưa có dữ liệu cho {tab_names[i]}.")

    # --- CHỨC NĂNG 2:
