import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB"

# 1. Danh sách tài khoản người dùng
USERS = {
    "haophamqob": "haophamqob2026",
    "thophamqob": "thophamqob2026",
    "thaonguyenqob": "thaonguyenqob2026",
    "thaoleqob": "thaoleqob2026",
    "huongqob": "huongqob2026",
    "admin": "adminqob2026"
}

# 2. Danh mục loại văn bản
LOAI_VB_DICT = {
    "Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", 
    "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", 
    "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"
}

# 3. Danh sách nhân sự thực hiện và ký duyệt
NHAN_SU = ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo", "Phạm Xuân Thọ", "Lê Thị Thảo", "Hà Thị Thúy Hường"]
NGUOI_KY_LIST = [
    "Phạm Thị Hảo, Hiệu trưởng",
    "Nguyễn Thị Phương Thảo, phó hiệu trưởng"
]

# Khởi tạo dữ liệu file CSV nếu chưa có
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Loại văn bản", "Số hiệu", "Trích yếu", "Người thực hiện", "Người ký", "Ngày tạo", "Tháng"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide")

# --- QUẢN LÝ ĐĂNG NHẬP ---
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG - TH QUỐC OAI B")
    u_input = st.text_input("Tên đăng nhập")
    p_input = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if u_input in USERS and USERS[u_input] == p_input:
            st.session_state["user"] = u_input
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
else:
    # --- GIAO DIỆN SAU ĐĂNG NHẬP ---
    user_now = st.session_state["user"]
    st.sidebar.title("Menu Hệ Thống")
    st.sidebar.info(f"Xin chào: **{user_now}**")
    
    menu = st.sidebar.radio("Chọn chức năng:", ["🚀 Lấy số văn bản", "🔍 Tra cứu & Lịch sử", "📊 Thống kê báo cáo"])
    
    if st.sidebar.button("Đăng xuất"):
        st.session_state["user"] = None
        st.rerun()

    # --- TAB 1: LẤY SỐ VĂN BẢN ---
    if menu == "🚀 Lấy số văn bản":
        st.subheader("📝 Đăng ký cấp số mới")
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("Loại văn bản", list(LOAI_VB_DICT.keys()))
                nguoi_thuc_hien = st.selectbox("Người thực hiện", NHAN_SU)
                if user_now == "admin":
                    is_chen = st.checkbox("Chế độ chèn số (Admin)")
                    so_chen = st.number_input("Số muốn chèn", min_value=1, step=1)
            with c2:
                nguoi_ky_chon = st.selectbox("Người ký và Chức vụ", NGUOI_KY_LIST)
                trich_yeu = st.text_area("Trích yếu nội dung văn bản")
            
            btn_submit = st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ")

        if btn_submit:
            df = pd.read_csv(DATA_FILE)
            # Kiểm tra trùng trích yếu (trừ trường hợp admin chèn số)
            is_dup = df['Trích yếu'].str.strip().str.lower().eq(trich_yeu.strip().lower()).any()
            
            if is_dup and user_now != "admin":
                st.error("🚫 Nội dung này đã có người lấy số! Vui lòng liên hệ Admin.")
            elif not trich_yeu:
                st.warning("Vui lòng nhập trích yếu nội dung.")
            else:
                ky_hieu = LOAI_VB_DICT[loai_chon]
                if user_now == "admin" and is_chen:
                    so_moi = so_chen
                else:
                    df_loai = df[df["Loại văn bản"] == loai_chon]
                    so_moi = len(df_loai) + 1
                
                so_hieu_full = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                now = datetime.now()
                
                new_row = {
                    "Loại văn bản": loai_chon, "Số hiệu": so_hieu_full,
                    "Trích yếu": trich_yeu.strip(), "Người thực hiện": nguoi_thuc_hien,
                    "Người ký": nguoi_ky_chon, "Ngày tạo": now.strftime("%d/%m/%Y %H:%M"),
                    "Tháng": now.strftime("%m/%Y")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"✅ Đã cấp số thành công: {so_hieu_full}")
                st.balloons()

    # --- TAB 2: TRA CỨU & LỊCH SỬ ---
    elif menu == "🔍 Tra cứu & Lịch sử":
        st.subheader("🔍 Tìm kiếm văn bản")
        df_view = pd.read_csv(DATA_FILE)
        
        search = st.text_input("Nhập nội dung cần tìm (Trích yếu, Số hiệu, Người thực hiện...)")
        if search:
            df_view = df_view[df_view.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        df_display = df_view.copy()
        df_display.insert(0, 'STT', range(1, len(df_display) + 1))
        st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)

        if user_now == "admin" and not df_view.empty:
            st.divider()
            st.subheader("🛠 Quyền hạn Admin")
            idx_del = st.number_input("Nhập STT muốn xóa (theo bảng trên)", min_value=1, max_value=len(df_display), step=1)
            if st.button("❌ XÁC NHẬN XÓA"):
                df_origin = pd.read_csv(DATA_FILE)
                # Tìm dòng cần xóa dựa trên Số hiệu duy nhất của bảng đã hiển thị
                row_val = df_display.iloc[len(df_display) - idx_del]
                df_origin = df_origin[df_origin["Số hiệu"] != row_val["Số hiệu"]]
                df_origin.to_csv(DATA_FILE, index=False)
                st.success("Đã xóa thành công!")
                st.rerun()

    # --- TAB 3: THỐNG KÊ BÁO CÁO ---
    elif menu == "📊 Thống kê báo cáo":
        st.subheader("📊 Thống kê tình hình cấp số")
        df_tk = pd.read_csv(DATA_FILE)
        if not df_tk.empty:
            col_tk1, col_tk2 = st.columns(2)
            with col_tk1:
                st.write("**Số lượng theo Người thực hiện:**")
                st.bar_chart(df_tk["Người thực hiện"].value_state_counts() if hasattr(df_tk["Người thực hiện"], "value_state_counts") else df_tk["Người thực hiện"].value_counts())
            with col_tk2:
                st.write("**Số lượng theo Loại văn bản:**")
                st.table(df_tk["Loại văn bản"].value_counts())
            
            st.divider()
            st.write("**Chi tiết số lượng văn bản theo từng tháng:**")
            st.dataframe(df_tk.groupby(["Tháng", "Loại văn bản"]).size().reset_index(name='Số lượng'))
        else:
            st.info("Chưa có dữ liệu để thống kê.")
