import streamlit as st
import pandas as pd
from datetime import datetime, date
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
    df = pd.DataFrame(columns=["Loại văn bản", "Số hiệu", "Ngày văn bản", "Trích yếu", 
                              "Người thực hiện", "Người ký", "Chức vụ", "Hạn xử lý", "Link PDF", "Ngày tạo hệ thống", "Tháng"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Văn phòng số TH Quốc Oai B", layout="wide")

# Hàm tô màu nhắc hạn
def highlight_deadline(row):
    if pd.isna(row['Hạn xử lý']) or row['Hạn xử lý'] == "Không có":
        return [''] * len(row)
    try:
        deadline = datetime.strptime(row['Hạn xử lý'], "%d/%m/%Y").date()
        today = date.today()
        diff = (deadline - today).days
        if diff < 0: return ['background-color: #ffcccc'] * len(row) # Quá hạn (Đỏ)
        elif diff <= 2: return ['background-color: #fff3cd'] * len(row) # Sắp đến hạn (Vàng)
    except: pass
    return [''] * len(row)

# --- QUẢN LÝ ĐĂNG NHẬP ---
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
    st.sidebar.title("Văn phòng Số")
    st.sidebar.success(f"Chào: **{user_name}**")
    menu = st.sidebar.radio("Chức năng:", ["🚀 Lấy số văn bản", "🔍 Nhật ký & Số hóa", "📊 Thống kê & Báo cáo"])
    if st.sidebar.button("Đăng xuất"):
        st.session_state["user_id"] = None
        st.rerun()

    # --- TAB 1: LẤY SỐ VĂN BẢN (Tích hợp Deadline & PDF) ---
    if menu == "🚀 Lấy số văn bản":
        st.subheader("📝 Đăng ký cấp số & Số hóa PDF")
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("Loại văn bản", list(LOAI_VB_DICT.keys()))
                st.text_input("Người thực hiện", value=user_name, disabled=True)
                ngay_van_ban = st.date_input("Ngày tháng thực của văn bản", date.today())
                co_han = st.checkbox("Văn bản này có hạn báo cáo/xử lý?")
                han_xu_ly = "Không có"
                if co_han:
                    han_xu_ly_date = st.date_input("Chọn ngày hạn chót", date.today())
                    han_xu_ly = han_xu_ly_date.strftime("%d/%m/%Y")
            with c2:
                nguoi_ky = st.selectbox("Người ký", DANH_SACH_NGUOI_KY)
                chuc_vu = st.selectbox("Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("Trích yếu nội dung")
                link_pdf = st.text_input("Dán Link File PDF (Google Drive/Dropbox)")

            if user_id == "admin":
                st.divider()
                is_chen = st.checkbox("Kích hoạt chèn số tùy chỉnh")
                so_hieu_tuy_chinh = st.text_input("Nhập số hiệu chèn (Vd: 01a/BC-THQOB)")

            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                df = pd.read_csv(DATA_FILE)
                if not trich_yeu: st.error("Vui lòng nhập trích yếu.")
                else:
                    if user_id == "admin" and is_chen and so_hieu_tuy_chinh: so_hieu_final = so_hieu_tuy_chinh
                    else:
                        ky_hieu = LOAI_VB_DICT[loai_chon]
                        df_loai = df[df["Loại văn bản"] == loai_chon]
                        so_moi = len(df_loai) + 1
                        so_hieu_final = f"{so_moi:02d}/{ky_hieu}-{MA_TRUONG}"
                    
                    new_row = {
                        "Loại văn bản": loai_chon, "Số hiệu": so_hieu_final,
                        "Ngày văn bản": ngay_van_ban.strftime("%d/%m/%Y"),
                        "Trích yếu": trich_yeu.strip(), "Người thực hiện": user_name,
                        "Người ký": nguoi_ky, "Chức vụ": chuc_vu,
                        "Hạn xử lý": han_xu_ly, "Link PDF": link_pdf,
                        "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tháng": ngay_van_ban.strftime("%m/%Y")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df = df.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"✅ Đã cấp số: {so_hieu_final}")
                    st.balloons()

    # --- TAB 2: NHẬT KÝ & SỐ HÓA ---
    elif menu == "🔍 Nhật ký & Số hóa":
        st.subheader("🔍 Nhật ký văn bản số hóa")
        df_view = pd.read_csv(DATA_FILE)
        st.write("💡 :red[Đỏ: Quá hạn] | :orange[Vàng: Sắp đến hạn]")
        search = st.text_input("Tìm kiếm nhanh...")
        if search:
            df_view = df_view[df_view.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        if not df_view.empty:
            df_view = df_view.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
            st.dataframe(df_view.style.apply(highlight_deadline, axis=1), use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("📂 **Mở file PDF:**")
            files_link = df_view[df_view["Link PDF"].notna() & (df_view["Link PDF"] != "")]
            if not files_link.empty:
                sel = st.selectbox("Chọn văn bản để xem:", files_link["Số hiệu"] + " - " + files_link["Trích yếu"])
                link = files_link[files_link["Số hiệu"] == sel.split(" - ")[0]]["Link PDF"].values[0]
                st.markdown(f"🔗 [Mở văn bản: {sel}]({link})")

    # --- TAB 3: THỐNG KÊ & BÁO CÁO THÁNG (Tính năng mới) ---
    elif menu == "📊 Thống kê & Báo cáo":
        st.subheader("📊 Báo cáo và Xuất dữ liệu")
        df_tk = pd.read_csv(DATA_FILE)
        
        if not df_tk.empty:
            # 1. Lọc báo cáo tháng hiện tại
            thang_hien_tai = date.today().strftime("%m/%Y")
            df_thang = df_tk[df_tk["Tháng"] == thang_hien_tai]
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(f"Tổng văn bản tháng {thang_hien_tai}", len(df_thang))
            with c2:
                # Nút tải báo cáo tháng hiện tại
                csv_thang = df_thang.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"📥 Tải Báo cáo Excel Tháng {thang_hien_tai}",
                    data=csv_thang,
                    file_name=f"Bao_cao_thang_{thang_hien_tai.replace('/','_')}.csv",
                    mime='text/csv'
                )
            
            st.write(f"**Danh sách văn bản tháng {thang_hien_tai}:**")
            st.dataframe(df_thang, use_container_width=True, hide_index=True)
            
            st.divider()
            st.write("**Thống kê tổng thể năm:**")
            st.bar_chart(df_tk["Người thực hiện"].value_counts())
            
            # Nút tải toàn bộ dữ liệu năm
            csv_all = df_tk.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải toàn bộ sổ văn bản (File Tổng)", data=csv_all, file_name="So_van_ban_Tong_Hop.csv")
