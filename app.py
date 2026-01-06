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
        # Đọc bảng chính - BẮT BUỘC TRANG TÍNH TÊN LÀ: Data
        df_vb = conn.read(worksheet="Data", ttl=0)
        # Đọc bảng tài khoản - BẮT BUỘC TRANG TÍNH TÊN LÀ: Sheet1
        df_us = conn.read(spreadsheet=URL_USERS, worksheet="Sheet1", ttl=0)
        return df_vb, df_us
    except Exception as e:
        st.error(f"Lỗi: Không tìm thấy trang tính phù hợp. Chi tiết: {e}")
        return None, None

df_vanban, df_users = load_data()

# --- CSS ---
st.markdown("""<style>.main { background-color: #f0f2f6; } .stButton>button { border-radius: 8px; font-weight: bold; background-color: #1e3a8a; color: white; }</style>""", unsafe_allow_html=True)

if df_vanban is not None and df_users is not None:
    # --- ĐĂNG NHẬP ---
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
        # --- GIAO DIỆN CHÍNH ---
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

        if menu == "🚀 Cấp số văn bản":
            st.header("🚀 Cấp số văn bản mới")
            with st.form("form_cap_so"):
                c1, c2 = st.columns(2)
                with c1:
                    loai_chon = st.selectbox("📁 Loại văn bản", ["Công văn", "Quyết định", "Tờ trình", "Thông báo", "Báo cáo", "Giấy mời", "Biên bản", "Kế hoạch", "Hợp đồng", "Quy chế"])
                    ngay_vb = st.date_input("📅 Ngày văn bản", date.today())
                    nguoi_ky = st.selectbox("✍️ Người ký", ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"])
                with c2:
                    chuc_vu = st.selectbox("🎓 Chức vụ", ["Hiệu trưởng", "Phó Hiệu trưởng"])
                    trich_yeu = st.text_area("📝 Trích yếu nội dung")
                
                if st.session_state.user_id == "admin":
                    with st.expander("🛠 Admin chèn số"):
                        is_chen = st.checkbox("Kích hoạt chèn số tùy chỉnh")
                        so_hieu_tuy_chinh = st.text_input("Số hiệu tùy chỉnh (Vd: 01a/BC-THQOB)")

                if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                    if not trich_yeu.strip():
                        st.error("Vui lòng nhập trích yếu!")
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
                        
                        try:
                            updated_df = pd.concat([df_vanban, new_row], ignore_index=True)
                            conn.update(worksheet="Data", data=updated_df)
                            st.cache_data.clear()
                            st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu_final}")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi khi lưu dữ liệu: {e}")

        elif menu == "🔍 Nhật ký & Quản lý":
            st.header("🔍 Nhật ký văn bản")
            st.dataframe(df_vanban, use_container_width=True, hide_index=True)
            if st.session_state.user_id == "admin":
                st.divider()
                so_xoa = st.text_input("Nhập số hiệu chính xác để xóa:")
                if st.button("Xóa dòng này"):
                    df_new = df_vanban[df_vanban["Số hiệu"] != so_xoa]
                    conn.update(worksheet="Data", data=df_new)
                    st.cache_data.clear()
                    st.rerun()

        elif menu == "📊 Báo cáo tháng":
            st.header("📊 Báo cáo")
            if not df_vanban.empty:
                list_thang = sorted(df_vanban["Tháng"].unique(), reverse=True)
                thang_sel = st.selectbox("Chọn tháng:", list_thang)
                df_th = df_vanban[df_vanban["Tháng"] == thang_sel]
                st.dataframe(df_th, use_container_width=True, hide_index=True)
                csv = df_th.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải báo cáo Excel", data=csv, file_name=f"BC_{thang_sel}.csv")

        elif menu == "⚙️ Quản trị Admin":
            if st.session_state.user_id == "admin":
                st.header("⚙️ Quản lý tài khoản")
                st.dataframe(df_users, hide_index=True)
                u_sel = st.selectbox("Chọn tài khoản:", df_users['Username'].tolist())
                p_new = st.text_input("Mật khẩu mới:", type="password")
                if st.button("Cập nhật mật khẩu"):
                    df_users.loc[df_users['Username'] == u_sel, 'Password'] = p_new
                    conn.update(spreadsheet=URL_USERS, worksheet="Sheet1", data=df_users)
                    st.success("Đã đổi mật khẩu!")
