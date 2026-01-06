import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date

# --- CẤU HÌNH ---
MA_TRUONG = "THQOB"
LOGO_URL = "ESTD2.png"
URL_USERS = "https://docs.google.com/spreadsheets/d/1iEE9Vvvy-zSy-hNyh9cUmIbhldxVwTt4LcvOLHg9eCA/edit?usp=sharing"
WEB_URL = "https://sovanbandiqob.streamlit.app/"

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- KẾT NỐI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # 1. Đọc bảng chính (Sử dụng Service Account đã cấu hình trong Secrets)
        # Hệ thống sẽ tìm trang tính tên là 'Data' mà bạn vừa đổi
        df_vb = conn.read(worksheet="Data", ttl=0)
        
        # 2. Đọc bảng tài khoản (Sử dụng URL công khai)
        # Thử đọc worksheet đầu tiên bất kể tên là gì để tránh lỗi 'Sheet1'
        df_us = conn.read(spreadsheet=URL_USERS, ttl=0)
        
        return df_vb, df_us
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        st.info("Mẹo: Hãy đảm bảo file Dữ liệu đã đổi tên trang tính thành 'Data'.")
        return None, None

df_vanban, df_users = load_data()

if df_vanban is not None and df_users is not None:
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
                # ChuyểnUsername về dạng chuỗi để so sánh
                user_row = df_users[df_users['Username'].astype(str) == u_input]
                if not user_row.empty and str(user_row.iloc[0]['Password']) == p_input:
                    st.session_state["user_id"] = u_input
                    st.session_state["user_name"] = user_row.iloc[0]['Fullname']
                    st.rerun()
                else: st.error("Sai tài khoản hoặc mật khẩu!")
    else:
        # --- GIAO DIỆN CHÍNH ---
        with st.sidebar:
            st.info(f"Cán bộ: **{st.session_state.user_name}**")
            st.divider()
            menu = st.radio("CHỨC NĂNG", ["🚀 Cấp số văn bản", "🔍 Nhật ký & Quản lý", "📊 Báo cáo tháng"])
            if st.button("🚪 Đăng xuất"):
                st.session_state["user_id"] = None
                st.rerun()

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
                        ky_hieu_dict = {"Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"}
                        ky_hieu = ky_hieu_dict[loai_chon]
                        
                        # Tính toán số thứ tự
                        so_moi = len(df_vanban[df_vanban["Loại văn bản"] == loai_chon]) + 1
                        so_hieu = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                        
                        new_row = pd.DataFrame([{
                            "Loại văn bản": loai_chon, 
                            "Số hiệu": so_hieu, 
                            "Ngày văn bản": ngay_vb.strftime("%d/%m/%Y"),
                            "Trích yếu": trich_yeu.strip(), 
                            "Người thực hiện": st.session_state.user_name,
                            "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                            "Tháng": ngay_vb.strftime("%m/%Y")
                        }])
                        
                        try:
                            updated_df = pd.concat([df_vanban, new_row], ignore_index=True)
                            # Ghi dữ liệu vào đúng worksheet Data
                            conn.update(worksheet="Data", data=updated_df)
                            st.cache_data.clear()
                            st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu}")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu dữ liệu: {e}")

        elif menu == "🔍 Nhật ký & Quản lý":
            st.header("🔍 Nhật ký văn bản")
            st.dataframe(df_vanban, use_container_width=True, hide_index=True)
            
        elif menu == "📊 Báo cáo tháng":
            st.header("📊 Báo cáo")
            if not df_vanban.empty:
                list_thang = sorted(df_vanban["Tháng"].unique(), reverse=True)
                thang_sel = st.selectbox("Chọn tháng:", list_thang)
                df_th = df_vanban[df_vanban["Tháng"] == thang_sel]
                st.dataframe(df_th, use_container_width=True, hide_index=True)
