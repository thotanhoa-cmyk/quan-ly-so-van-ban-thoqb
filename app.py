import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CẤU HÌNH HỆ THỐNG ---
DATA_FILE = "data_so_van_ban.csv"
MA_TRUONG = "THQOB"
# Link ảnh logo trường (Đã được chuyển hướng để hiển thị trực tiếp)
LOGO_URL = "https://thttquocoaib-hanoi.edu.vn/uploads/thttquocoaib-hanoi/news/2021_12/logo_baiviet.jpg" 

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
                              "Người thực hiện", "Người ký", "Chức vụ", "Ngày tạo hệ thống", "Tháng"])
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Hệ thống Văn bản TH Quốc Oai B", layout="wide", page_icon="🏫")

# --- GIAO DIỆN CSS NÂNG CAO ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e6e9ef;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        border: 1px solid #1e3a8a;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 { color: #1e3a8a !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stDataFrame { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .login-box {
        padding: 30px;
        border-radius: 15px;
        background: white;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- QUẢN LÝ ĐĂNG NHẬP ---
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if st.session_state["user_id"] is None:
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=150)
        st.markdown("<h2 style='margin-bottom: 0;'>TRƯỜNG TIỂU HỌC</h2>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin-top: 0;'>THỊ TRẤN QUỐC OAI B</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666;'>Hệ thống quản lý văn bản nội bộ</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            u_input = st.text_input("👤 Tên đăng nhập", placeholder="Nhập tài khoản...")
            p_input = st.text_input("🔑 Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            if st.button("ĐĂNG NHẬP HỆ THỐNG"):
                if u_input in USERS_CONFIG and USERS_CONFIG[u_input][0] == p_input:
                    st.session_state["user_id"] = u_input
                    st.session_state["user_name"] = USERS_CONFIG[u_input][1]
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu, vui lòng thử lại!")
else:
    user_id = st.session_state["user_id"]
    user_name = st.session_state["user_name"]
    
    # Sidebar Cá nhân hóa
    with st.sidebar:
        st.image(LOGO_URL, width=100)
        st.markdown(f"### TH QUỐC OAI B")
        st.info(f"Xin chào: **{user_name}**")
        st.divider()
        menu = st.radio("DANH MỤC QUẢN LÝ", ["🚀 Cấp số văn bản", "🔍 Nhật ký lưu trữ", "📊 Báo cáo & Thống kê"])
        st.divider()
        if st.button("🚪 Đăng xuất"):
            st.session_state["user_id"] = None
            st.rerun()

    # --- TAB 1: LẤY SỐ VĂN BẢN (GIỮ NGUYÊN LOGIC CHẶN TRÙNG) ---
    if menu == "🚀 Cấp số văn bản":
        st.markdown("<h1>🚀 Đăng ký cấp số mới</h1>", unsafe_allow_html=True)
        with st.form("form_cap_so", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                loai_chon = st.selectbox("📁 Loại văn bản", list(LOAI_VB_DICT.keys()))
                st.text_input("👤 Người thực hiện", value=user_name, disabled=True)
                ngay_van_ban = st.date_input("📅 Ngày tháng văn bản", date.today())
            with c2:
                nguoi_ky = st.selectbox("✍️ Người ký", DANH_SACH_NGUOI_KY)
                chuc_vu = st.selectbox("🎓 Chức vụ", DANH_SACH_CHUC_VU)
                trich_yeu = st.text_area("📝 Trích yếu nội dung", placeholder="Nhập nội dung vắn tắt của văn bản...")

            if user_id == "admin":
                with st.expander("🛠 Chế độ Admin (Chèn số)"):
                    is_chen = st.checkbox("Kích hoạt chèn số hiệu tùy chỉnh")
                    so_hieu_tuy_chinh = st.text_input("Số hiệu muốn chèn (Vd: 05a/CV-THQOB)")

            if st.form_submit_button("🔥 XÁC NHẬN CẤP SỐ"):
                df = pd.read_csv(DATA_FILE)
                trich_yeu_moi = trich_yeu.strip().lower()
                is_dup = df['Trích yếu'].apply(lambda x: str(x).strip().lower()).eq(trich_yeu_moi).any()

                if not trich_yeu.strip():
                    st.error("Vui lòng nhập trích yếu!")
                elif is_dup and user_id != "admin":
                    so_cu = df[df['Trích yếu'].apply(lambda x: str(x).strip().lower()) == trich_yeu_moi]['Số hiệu'].values[0]
                    st.error(f"🚫 TRÙNG TRÍCH YẾU: Nội dung này đã lấy số {so_cu} trước đó.")
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

    # --- TAB 2: NHẬT KÝ (SẮP XẾP ĐA TẦNG) ---
    elif menu == "🔍 Nhật ký lưu trữ":
        st.markdown("<h1>🔍 Nhật ký văn bản</h1>", unsafe_allow_html=True)
        df_view = pd.read_csv(DATA_FILE)
        search = st.text_input("🔍 Tìm nhanh (Số hiệu, trích yếu, người ký...)", placeholder="Nhập từ khóa tìm kiếm...")
        
        if search:
            df_view = df_view[df_view.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        if not df_view.empty:
            df_view = df_view.sort_values(by=["Loại văn bản", "Số hiệu"], ascending=[True, True])
            df_display = df_view.copy()
            df_display.insert(0, 'STT', range(1, len(df_display) + 1))
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        if user_id == "admin" and not df_view.empty:
            with st.expander("🛠 QUẢN TRỊ: Xóa dòng dữ liệu"):
                id_to_del = st.text_input("Nhập Số hiệu chính xác để xóa:")
                if st.button("❌ XÁC NHẬN XÓA"):
                    df_origin = pd.read_csv(DATA_FILE)
                    df_origin = df_origin[df_origin["Số hiệu"] != id_to_del]
                    df_origin.to_csv(DATA_FILE, index=False)
                    st.success("Đã xóa dữ liệu thành công.")
                    st.rerun()

    # --- TAB 3: THỐNG KÊ & BÁO CÁO THÁNG ---
    elif menu == "📊 Báo cáo & Thống kê":
        st.markdown("<h1>📊 Thống kê & Xuất báo cáo</h1>", unsafe_allow_html=True)
        df_tk = pd.read_csv(DATA_FILE)
        
        if not df_tk.empty:
            thang_hien_tai = date.today().strftime("%m/%Y")
            df_thang = df_tk[df_tk["Tháng"] == thang_hien_tai]
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Tổng văn bản (Năm)", len(df_tk))
            with c2:
                st.metric(f"Văn bản tháng {thang_hien_tai}", len(df_thang))
            with c3:
                csv_thang = df_thang.to_csv(index=False).encode('utf-8-sig')
                st.download_button(f"📥 TẢI BÁO CÁO THÁNG {thang_hien_tai}", data=csv_thang, file_name=f"BC_Thang_{thang_hien_tai.replace('/','_')}.csv")
            
            st.divider()
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("Số lượng theo cán bộ")
                st.bar_chart(df_tk["Người thực hiện"].value_counts())
            with col_r:
                st.subheader("Tỉ lệ loại văn bản")
                st.write(df_tk["Loại văn bản"].value_counts())
