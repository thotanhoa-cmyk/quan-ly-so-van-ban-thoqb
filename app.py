import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB"

USERS_CONFIG = {
    "hao": ["hao2026", "Phạm Thị Hảo"],
    "tho": ["tho2026", "Phạm Xuân Thọ"],
    "thaonguyen": ["thaonguyen2026", "Nguyễn Thị Phương Thảo"],
    "thaole": ["thaole2026", "Lê Thị Thảo"],
    "thuy": ["thuy2026", "Đỗ Thị Thúy"],
    "admin": ["admin2026", "Quản trị viên"]
}

LOAI_VB_DICT = {
    "Công văn": "CV", "Quyết định": "QĐ", "Tờ trình": "TTr", 
    "Thông báo": "TB", "Báo cáo": "BC", "Giấy mời": "GM", 
    "Biên bản": "BB", "Kế hoạch": "KH", "Hợp đồng": "HĐ", "Quy chế": "QC"
}

DANH_SACH_NGUOI_KY = ["Phạm Thị Hảo", "Nguyễn Thị Phương Thảo"]
DANH_SACH_CHUC_VU = ["Hiệu trưởng", "Phó Hiệu trưởng"]

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Loại văn bản", "Số hiệu", "Ngày văn bản", "Trích yếu", "Người thực hiện", "Người ký", "Chức vụ", "Ngày tạo hệ thống", "Tháng"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide")

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG - TH QUỐC OAI B")
    u_input = st.text_input("Tên đăng nhập")
    p_input = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if u_input in USERS_CONFIG and USERS_CONFIG[u_input][0] == p_input:
            st.session_state["user_id"] = u_input
            st.session_state["user_name"] = USERS_CONFIG[u_input][1]
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")
else:
    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]
    
    st.sidebar.title("Menu")
    st.sidebar.success(f"Chào: **{user_name}**")
    menu = st.sidebar.radio("Chức năng:", ["🚀 Lấy số văn bản", "🔍 Tra cứu", "📊 Thống kê"])
    if st.sidebar.button("Đăng xuất"):
        st.session_state["user_id"] = None
        st.rerun()

    # --- TAB 1: LẤY SỐ VĂN BẢN ---
    if menu == "🚀 Lấy số văn bản":
        st.subheader("📝 Đăng ký cấp số mới")
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("Loại văn bản", list(LOAI_VB_DICT.keys()))
                st.text_input("Người thực hiện (Cố định)", value=user_name, disabled=True)
                ngay_van_ban = st.date_input("Ngày tháng thực của văn bản", datetime.now())
                
                if user_id == "admin":
                    st.info("🛠 CHẾ ĐỘ ADMIN")
                    is_chen = st.checkbox("Kích hoạt chèn số hiệu tùy chỉnh")
                    so_hieu_tuy_chinh = st.text_input("Nhập số hiệu chèn (Vd: 01a/BC-THQOB)")
            
            with c2:
                nguoi_ky = st.selectbox("Người ký", DANH_SACH_NGUOI_KY)
                chuc_vu = st.selectbox("Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("Trích yếu nội dung")
            
            btn_submit = st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ")

        if btn_submit:
            df = pd.read_csv(DATA_FILE)
            is_dup = df['Trích yếu'].str.strip().str.lower().eq(trich_yeu.strip().lower()).any()
            
            if is_dup:
                if user_id == "admin":
                    st.warning("⚠️ Chú ý: Trích yếu này đã tồn tại, nhưng Admin vẫn có quyền cấp số.")
                else:
                    st.error("🚫 Nội dung này đã có người lấy số! Vui lòng liên hệ Admin.")
                    st.stop()

            if not trich_yeu:
                st.error("Vui lòng nhập trích yếu nội dung.")
            else:
                if user_id == "admin" and is_chen and so_hieu_tuy_chinh:
                    so_hieu_final = so_hieu_tuy_chinh
                else:
                    ky_hieu = LOAI_VB_DICT[loai_chon]
                    df_loai = df[df["Loại văn bản"] == loai_chon]
                    so_moi = len(df_loai) + 1
                    so_hieu_final = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                
                new_row = {
                    "Loại văn bản": loai_chon, 
                    "Số hiệu": so_hieu_final,
                    "Ngày văn bản": ngay_van_ban.strftime("%d/%m/%Y"),
                    "Trích yếu": trich_yeu.strip(), 
                    "Người thực hiện": user_name,
                    "Người ký": nguoi_ky,
                    "Chức vụ": chuc_vu,
                    "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Tháng": ngay_van_ban.strftime("%m/%Y")
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # --- CẢI TIẾN: SẮP XẾP ĐA TẦNG ---
                # Sắp xếp theo Loại văn bản (A-Z) rồi mới đến Số hiệu (A-Z)
                df = df.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
                
                df.to_csv(DATA_FILE, index=False)
                st.success(f"✅ Đã cấp số: {so_hieu_final}")
                st.balloons()

    # --- TAB 2: TRA CỨU ---
    elif menu == "🔍 Tra cứu":
        st.subheader("🔍 Nhật ký văn bản")
        df_view = pd.read_csv(DATA_FILE)
        search = st.text_input("Tìm kiếm nhanh...")
        if search:
            df_view = df_view[df_view.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        if not df_view.empty:
            # Luôn đảm bảo bảng hiển thị đúng nhóm Loại văn bản -> Số hiệu
            df_view = df_view.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
            
            df_display = df_view.copy()
            df_display.insert(0, 'STT', range(1, len(df_display) + 1))
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            csv = df_view.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải file Excel tổng hợp", data=csv, file_name=f"so_van_ban_THQOB.csv")

        if user_id == "admin" and not df_view.empty:
            st.divider()
            st.subheader("🛠 Quyền xóa của Admin")
            id_to_del = st.text_input("Nhập chính xác Số hiệu muốn xóa (Vd: 01a/BC-THQOB):")
            if st.button("❌ XÁC NHẬN XÓA"):
                df_origin = pd.read_csv(DATA_FILE)
                if id_to_del in df_origin["Số hiệu"].values:
                    df_origin = df_origin[df_origin["Số hiệu"] != id_to_del]
                    df_origin.to_csv(DATA_FILE, index=False)
                    st.success(f"Đã xóa số hiệu {id_to_del}")
                    st.rerun()
                else:
                    st.error("Không tìm thấy số hiệu này.")
