import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB"
LOGO_URL = "http://truongtieuhocthitranquocoaib.edu.vn/upload/101647/20260105/ESTD2_5e92c.png" 

USERS_CONFIG = {
    "hao": ["hao2026", "Phạm Thị Hảo"],
    "thopham": ["thopham2026", "Phạm Xuân Thọ"],
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
                              "Người thực hiện", "Người ký", "Chức vụ", "Ngày tạo hệ thống", "Tháng"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- CSS NÂNG CAO ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .btn-delete>div>button { background-color: #ff4b4b !important; color: white !important; }
    h1, h2, h3 { color: #1e3a8a !important; text-align: center; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- QUẢN LÝ ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    _, col_m, _ = st.columns([1, 1.5, 1])
    with col_m:
        st.image(LOGO_URL, width=150)
        st.markdown("<h1>TRƯỜNG TIỂU HỌC QUỐC OAI B</h1>", unsafe_allow_html=True)
        u_input = st.text_input("👤 Tên đăng nhập")
        p_input = st.text_input("🔑 Mật khẩu", type="password")
        if st.button("ĐĂNG NHẬP"):
            if u_input in USERS_CONFIG and USERS_CONFIG[u_input][0] == p_input:
                st.session_state["user_id"] = u_input
                st.session_state["user_name"] = USERS_CONFIG[u_input][1]
                st.rerun()
            else:
                st.error("Thông tin đăng nhập không chính xác!")
else:
    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]
    
    with st.sidebar:
        st.image(LOGO_URL, width=100)
        st.info(f"Cán bộ: **{user_name}**")
        menu = st.sidebar.selectbox("MENU QUẢN LÝ", ["🚀 Lấy số văn bản", "🔍 Nhật ký văn bản", "📊 Báo cáo & Thống kê"])
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()

    # --- TAB 1: LẤY SỐ ---
    if menu == "🚀 Lấy số văn bản":
        st.markdown("<h1>🚀 Đăng ký cấp số văn bản mới</h1>", unsafe_allow_html=True)
        with st.form("form_cap_so"):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("📁 Loại văn bản", list(LOAI_VB_DICT.keys()))
                st.text_input("👤 Người thực hiện lấy số văn bản", value=user_name, disabled=True)
                ngay_van_ban = st.date_input("📅 Ngày tháng văn bản", date.today())
            with c2:
                nguoi_ky = st.selectbox("✍️ Người ký", DANH_SACH_NGUOI_KY)
                chuc_vu = st.selectbox("🎓 Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("📝 Trích yếu nội dung")

            if user_id == "admin":
                with st.expander("🛠 Chế độ Admin (Chèn số)"):
                    is_chen = st.checkbox("Kích hoạt chèn số tùy chỉnh")
                    so_hieu_tuy_chinh = st.text_input("Số hiệu chèn (Vd: 01a/BC-THQOB)")

            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                df = pd.read_csv(DATA_FILE)
                trich_yeu_moi = str(trich_yeu).strip().lower()
                is_dup = df['Trích yếu'].apply(lambda x: str(x).strip().lower()).eq(trich_yeu_moi).any()

                if not trich_yeu.strip():
                    st.error("Vui lòng nhập trích yếu!")
                elif is_dup and user_id != "admin":
                    so_cu = df[df['Trích yếu'].apply(lambda x: str(x).strip().lower()) == trich_yeu_moi]['Số hiệu'].values[0]
                    st.error(f"🚫 TRÙNG LẶP: Nội dung này đã lấy số {so_cu}.")
                else:
                    if user_id == "admin" and is_chen and so_hieu_tuy_chinh:
                        so_hieu_final = so_hieu_tuy_chinh
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
                        "Ngày tạo hệ thống": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Tháng": ngay_van_ban.strftime("%m/%Y")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df = df.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"✅ ĐÃ CẤP SỐ: {so_hieu_final}")
                    st.balloons()

    # --- TAB 2: NHẬT KÝ & XÓA ---
    elif menu == "🔍 Nhật ký văn bản":
        st.markdown("<h1>🔍 Nhật ký lưu trữ văn bản</h1>", unsafe_allow_html=True)
        df_view = pd.read_csv(DATA_FILE)
        search = st.text_input("🔍 Tìm kiếm nhanh (Số hiệu, nội dung, người thực hiện...)", placeholder="Nhập từ khóa...")
        if search:
            df_view = df_view[df_view.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        if not df_view.empty:
            df_view = df_view.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
            df_display = df_view.copy()
            df_display.insert(0, 'STT', range(1, len(df_display) + 1))
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        if user_id == "admin":
            st.divider()
            st.subheader("🛠 QUYỀN HẠN ADMIN")
            col_del_1, col_del_2 = st.columns([3, 1])
            with col_del_1:
                id_to_del = st.text_input("Nhập Số hiệu muốn xóa chính xác:", key="del_input")
            with col_del_2:
                st.markdown("<div class='btn-delete'>", unsafe_allow_html=True)
                btn_delete = st.button("❌ XÓA SỐ NÀY", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            if btn_delete:
                df_origin = pd.read_csv(DATA_FILE)
                if id_to_del in df_origin["Số hiệu"].values:
                    df_origin = df_origin[df_origin["Số hiệu"] != id_to_del]
                    df_origin.to_csv(DATA_FILE, index=False)
                    st.success(f"Đã xóa thành công số hiệu: {id_to_del}")
                    st.rerun()
                else:
                    st.error("Không tìm thấy số hiệu này!")

    # --- TAB 3: BÁO CÁO TỔNG HỢP (NĂM & THÁNG) ---
    elif menu == "📊 Báo cáo & Thống kê":
        st.markdown("<h1>📊 Trung tâm dữ liệu & Báo cáo</h1>", unsafe_allow_html=True)
        df_raw = pd.read_csv(DATA_FILE)
        
        if df_raw.empty:
            st.info("Chưa có dữ liệu để báo cáo.")
        else:
            # 1. Thống kê Tổng quan (Năm)
            st.subheader("🗓 Tổng quan năm 2026")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tổng văn bản đã cấp", len(df_raw))
            with c2:
                most_user = df_raw["Người thực hiện"].mode()[0] if not df_raw.empty else "N/A"
                st.metric("Cán bộ tích cực nhất", most_user)
            with c3:
                # Tải toàn bộ sổ văn bản năm
                csv_year = df_raw.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tải Sổ Văn Bản Cả Năm (Excel)", data=csv_year, file_name="So_Van_Ban_2026.csv", use_container_width=True)
            
            st.divider()
            
            # 2. Báo cáo chi tiết theo Tháng
            st.subheader("📂 Chi tiết theo Tháng")
            list_thang = sorted(df_raw["Tháng"].unique(), reverse=True)
            thang_chon = st.selectbox("Chọn tháng muốn xem báo cáo:", list_thang)
            
            df_thang = df_raw[df_raw["Tháng"] == thang_chon]
            
            col_m1, col_m2 = st.columns([2, 1])
            with col_m1:
                st.write(f"**Danh sách văn bản tháng {thang_chon}:**")
                st.dataframe(df_thang[["Số hiệu", "Ngày văn bản", "Trích yếu", "Người thực hiện"]], use_container_width=True, hide_index=True)
            with col_m2:
                st.write(f"**Hành động:**")
                st.metric(f"Số lượng trong tháng", len(df_thang))
                csv_month = df_thang.to_csv(index=False).encode('utf-8-sig')
                st.download_button(f"📥 Tải Báo Cáo Tháng {thang_chon}", data=csv_month, file_name=f"Bao_cao_thang_{thang_chon.replace('/','_')}.csv", use_container_width=True)

            st.divider()
            
            # 3. Biểu đồ thống kê
            st.subheader("📈 Biểu đồ xu hướng")
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.write("**Số lượng văn bản theo từng tháng:**")
                df_counts = df_raw.groupby("Tháng").size().reset_index(name='Số lượng')
                st.bar_chart(df_counts.set_index("Tháng"))
            with chart_col2:
                st.write("**Tỷ lệ các loại văn bản:**")
                st.write(df_raw["Loại văn bản"].value_counts())
