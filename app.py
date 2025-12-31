import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH ---
PASSWORD = "truongquocoaib" 
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB" 

# Danh mục đầy đủ các loại văn bản và ký hiệu tương ứng
LOAI_VB_DICT = {
    "Công văn": "CV",
    "Quyết định": "QĐ",
    "Tờ trình": "TTr",
    "Thông báo": "TB",
    "Báo cáo": "BC",
    "Giấy mời": "GM",
    "Biên bản": "BB",
    "Kế hoạch": "KH",
    "Hợp đồng": "HĐ",
    "Quy chế": "QC"
}

# Khởi tạo file dữ liệu
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Loại văn bản", "Số hiệu", "Trích yếu", "Người lấy", "Ngày tạo"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Cấp số văn bản TH Quốc Oai B", layout="wide")

# Kiểm tra đăng nhập
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Hệ thống nội bộ - Trường TH Quốc Oai B")
    pwd = st.text_input("Nhập mật khẩu đơn vị:", type="password")
    if st.button("Đăng nhập"):
        if pwd == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mật khẩu không đúng!")
else:
    st.title(f"📝 Quản lý cấp số văn bản năm {datetime.now().year}")

    with st.form("form_lay_so"):
        col1, col2 = st.columns(2)
        with col1:
            loai_chon = st.selectbox("Chọn loại văn bản:", list(LOAI_VB_DICT.keys()))
            nguoi_lay = st.text_input("Người thực hiện (Ví dụ: Nguyễn Văn A)")
        with col2:
            trich_yeu = st.text_area("Trích yếu nội dung (Ghi tóm tắt nội dung văn bản)")
        
        submit = st.form_submit_button("🔥 LẤY SỐ HIỆU")

    if submit:
        if not trich_yeu or not nguoi_lay:
            st.error("⚠️ Vui lòng điền đủ 'Người thực hiện' và 'Trích yếu'!")
        else:
            df = pd.read_csv(DATA_FILE)
            ky_hieu_loai = LOAI_VB_DICT[loai_chon]
            
            # Tự động tìm số tiếp theo của riêng loại văn bản đó
            df_loai_nay = df[df["Loại văn bản"] == loai_chon]
            so_tiep_theo = len(df_loai_nay) + 1
            
            # Định dạng: 01/QĐ-THQOB
            so_hieu_full = f"{so_tiep_theo:02d}/{ky_hieu_loai}-{MA_TRUONG}"
            
            new_data = {
                "Loại văn bản": loai_chon,
                "Số hiệu": so_hieu_full,
                "Trích yếu": trich_yeu,
                "Người lấy": nguoi_lay,
                "Ngày tạo": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            
            st.success(f"✅ Đã cấp số thành công cho {loai_chon}!")
            st.code(so_hieu_full, language="text")
            st.balloons()

    # --- BẢNG THỐNG KÊ ---
    st.divider()
    st.subheader("📋 Nhật ký cấp số gần đây")
    
    # Đọc lại dữ liệu để hiển thị
    df_show = pd.read_csv(DATA_FILE)
    if not df_show.empty:
        # Hiển thị từ mới nhất đến cũ nhất
        st.dataframe(df_show.iloc[::-1], use_container_width=True)
        
        # Cho phép tải Excel
        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Tải file Excel tổng hợp", data=csv, file_name=f"so_van_ban_{MA_TRUONG}.csv")
    else:
        st.write("Chưa có dữ liệu nào được cấp.")
# --- CHẾ ĐỘ XÓA DỮ LIỆU (CHỈ DÀNH CHO ADMIN) ---
    st.divider()
    with st.expander("🛠 Chế độ chỉnh sửa (Dành cho Admin)"):
        st.warning("Cẩn thận: Thao tác xóa sẽ không thể khôi phục!")
        df_edit = pd.read_csv(DATA_FILE)
        
        # Chọn dòng muốn xóa
        row_to_delete = st.number_input("Nhập chỉ số dòng muốn xóa (Số thứ tự ở cột ngoài cùng bên trái bảng lịch sử):", 
                                        min_value=0, max_value=len(df_edit)-1, step=1)
        
        if st.button("❌ XÁC NHẬN XÓA DÒNG NÀY"):
            df_edit = df_edit.drop(df_edit.index[row_to_delete])
            df_edit.to_csv(DATA_FILE, index=False)
            st.success("Đã xóa dòng thành công! Vui lòng F5 lại trang.")
            st.rerun()
