import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH ---
PASSWORD = "truongquocoaib"  # Bạn có thể đổi mật khẩu này
DATA_FILE = "data_so_van_ban.csv"

# Khởi tạo file dữ liệu nếu chưa có
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["STT", "Số hiệu", "Loại văn bản", "Trích yếu", "Người lấy", "Ngày tạo"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Hệ thống cấp số văn bản", layout="centered")

# --- GIAO DIỆN ĐĂNG NHẬP ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Đăng nhập hệ thống")
    pwd = st.text_input("Nhập mật khẩu đơn vị:", type="password")
    if st.button("Vào hệ thống"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Sai mật khẩu, vui lòng kiểm tra lại!")
else:
    # --- GIAO DIỆN CHÍNH ---
    st.title("📝 Cấp số văn bản nội bộ")
    st.info(f"Chào mừng bạn! Hệ thống đang quản lý số cho năm {datetime.now().year}")

    with st.form("form_lay_so"):
        col1, col2 = st.columns(2)
        with col1:
            loai_vb = st.selectbox("Loại văn bản", ["Công văn", "Quyết định", "Tờ trình", "Thông báo"])
            ky_hieu = st.text_input("Ký hiệu (Vd: TH-QO)", "TH-QO")
        with col2:
            nguoi_lay = st.text_input("Người soạn thảo")
            
        trich_yeu = st.text_area("Trích yếu nội dung văn bản")
        
        submit = st.form_submit_button("🔥 LẤY SỐ MỚI")

    if submit:
        if not trich_yeu or not nguoi_lay:
            st.warning("Vui lòng điền đầy đủ Trích yếu và Người soạn thảo!")
        else:
            df = pd.read_csv(DATA_FILE)
            
            # Tính số tiếp theo cho loại văn bản đó
            nam_hien_tai = datetime.now().year
            so_tiep_theo = len(df) + 1
            so_hieu_full = f"{so_tiep_theo}/{ky_hieu}"
            
            new_data = {
                "STT": so_tiep_theo,
                "Số hiệu": so_hieu_full,
                "Loại văn bản": loai_vb,
                "Trích yếu": trich_yeu,
                "Người lấy": nguoi_lay,
                "Ngày tạo": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            
            st.success(f"Số văn bản của bạn là: **{so_hieu_full}**")
            st.balloons()

    # --- LỊCH SỬ ---
    st.divider()
    st.subheader("📋 Lịch sử cấp số")
    df_display = pd.read_csv(DATA_FILE)
    st.dataframe(df_display.sort_values(by="STT", ascending=False), use_container_width=True)

    # Nút tải file Excel cho Admin
    csv = df_display.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Tải về file Excel (CSV)", data=csv, file_name="danh_sach_cap_so.csv", mime="text/csv")
    
    if st.button("Đăng xuất"):
        st.session_state["authenticated"] = False
        st.rerun()
