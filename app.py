import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH ---
PASSWORD = "truongquocoaib" 
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB" 

LOAI_VB_DICT = {
    "Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", 
    "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", 
    "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"
}

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Loại văn bản", "Số hiệu", "Trích yếu", "Người lấy", "Ngày tạo"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Cấp số văn bản TH Quốc Oai B", layout="wide")

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
            nguoi_lay = st.text_input("Người thực hiện")
        with col2:
            trich_yeu = st.text_area("Trích yếu nội dung (Cần nhập chính xác)")
        submit = st.form_submit_button("🔥 LẤY SỐ HIỆU")

    if submit:
        if not trich_yeu or not nguoi_lay:
            st.error("⚠️ Vui lòng điền đủ thông tin!")
        else:
            df = pd.read_csv(DATA_FILE)
            
            # --- KIỂM TRA TRÙNG TRÍCH YẾU ---
            # Chuyển về chữ thường và xóa khoảng trắng thừa để so sánh chính xác hơn
            trich_yeu_check = trich_yeu.strip().lower()
            is_duplicate = df['Trích yếu'].str.strip().str.lower().eq(trich_yeu_check).any()
            
            if is_duplicate:
                st.error("🚫 CẢNH BÁO TRÙNG LẶP!")
                st.warning(f"Nội dung trích yếu này đã tồn tại trong hệ thống. Vui lòng kiểm tra lại lịch sử bên dưới hoặc liên hệ Admin để được hỗ trợ!")
            else:
                ky_hieu_loai = LOAI_VB_DICT[loai_chon]
                df_loai_nay = df[df["Loại văn bản"] == loai_chon]
                so_tiep_theo = len(df_loai_nay) + 1
                so_hieu_full = f"{so_tiep_theo:02d}/{ky_hieu_loai}-{MA_TRUONG}"
                
                new_data = {
                    "Loại văn bản": loai_chon,
                    "Số hiệu": so_hieu_full,
                    "Trích yếu": trich_yeu.strip(),
                    "Người lấy": nguoi_lay.strip(),
                    "Ngày tạo": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"✅ Đã cấp số: {so_hieu_full}")
                st.balloons()

    # --- HIỂN THỊ NHẬT KÝ ---
    st.divider()
    st.subheader("📋 Nhật ký cấp số")
    df_show = pd.read_csv(DATA_FILE)
    
    if not df_show.empty:
        df_display = df_show.copy()
        df_display.insert(0, 'STT', range(1, len(df_display) + 1))
        st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
        
        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Tải file Excel", data=csv, file_name=f"so_van_ban_{MA_TRUONG}.csv")
    else:
        st.write("Chưa có dữ liệu.")

    # --- CHẾ ĐỘ XÓA (ADMIN) ---
    with st.expander("🛠 Chế độ xóa số lấy nhầm"):
        index_to_delete = st.number_input("Nhập STT muốn xóa:", min_value=1, max_value=len(df_show) if not df_show.empty else 1, step=1)
