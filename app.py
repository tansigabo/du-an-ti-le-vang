import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="Kiểm tra tỉ lệ vàng đơn giản", layout="centered")
# st.title("Kiểm tra Tỷ lệ Vàng (A–C–B)")

# Tỷ lệ Vàng PHI ≈ 1.618
PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700

# ==============================
# Các hàm vẽ
# ==============================
def ve_diem(draw, p, color, r=8):
    """Vẽ điểm dưới dạng hình tròn."""
    draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)

def ve_duong(draw, p1, p2, color="white", width=3):
    """Vẽ đường thẳng liền."""
    draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=color, width=width)

# ==============================
# Khởi tạo session state
# ==============================
# clicks chỉ lưu 0, 1 hoặc 2 điểm (A, B)
if "clicks" not in st.session_state:
    st.session_state.clicks = []

# results lưu kết quả của các đoạn đã đo
if "results" not in st.session_state:
    st.session_state.results = []

if "last_image" not in st.session_state:
    st.session_state.last_image = None

# ==============================
# Tải ảnh
# ==============================
uploaded_file = st.file_uploader("Chọn ảnh...", type=["jpg", "png", "webp"])

if uploaded_file:

    # Reset khi đổi ảnh
    if st.session_state.last_image != uploaded_file.name:
        st.session_state.clicks = []
        st.session_state.results = []
        st.session_state.last_image = uploaded_file.name

    img = Image.open(uploaded_file).convert("RGB")

    # Xử lý resize ảnh
    display_img = img.copy()
    if img.width > MAX_DISPLAY_WIDTH:
        ratio = MAX_DISPLAY_WIDTH / img.width
        scale_back = 1 / ratio
        display_img = display_img.resize((MAX_DISPLAY_WIDTH, int(img.height * ratio)))
    else:
        ratio = 1
        scale_back = 1

    # Lấy click
    click = streamlit_image_coordinates(display_img, key="img_click", width=display_img.width)

    if click:
        x, y = click["x"], click["y"]
        # Chuyển tọa độ hiển thị về tọa độ ảnh gốc
        x = int(x * scale_back)
        y = int(y * scale_back)
        
        # Thêm điểm nếu nó khác với điểm cuối cùng (tránh click đúp)
        if not st.session_state.clicks or st.session_state.clicks[-1] != (x, y):
            st.session_state.clicks.append((x, y))

    clicks = st.session_state.clicks
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)

    # ==============================
    # Xử lý A – C – B
    # ==============================
    if len(clicks) >= 1:
        A = np.array(clicks[0])
        A_disp = tuple((A * ratio).astype(int))
        # Điểm A: Đỏ
        ve_diem(draw, A_disp, "red")

    if len(clicks) == 2:
        B = np.array(clicks[1])
        B_disp = tuple((B * ratio).astype(int))
        
        # Điểm B: Đỏ
        ve_diem(draw, B_disp, "red")
        
        # Vẽ đoạn AB
        ve_duong(draw, A_disp, B_disp)

        # Tính Điểm Tỷ lệ Vàng C (chia đoạn AB theo tỉ lệ vàng, AC là đoạn lớn)
        # AC = (1/PHI) * AB
        # C = A + (B - A) / PHI 
        C = A + (B - A) / PHI

        # Tính độ dài
        AB_len = np.linalg.norm(B - A)
        AC_len = np.linalg.norm(C - A) # Độ dài đoạn lớn
        CB_len = np.linalg.norm(B - C) # Độ dài đoạn nhỏ

        # Convert C sang tọa độ hiển thị
        C_disp = tuple((C * ratio).astype(int))

        # Điểm C (Tỷ lệ Vàng): Vàng
        ve_diem(draw, C_disp, "yellow")

        # Lưu kết quả
        st.session_state.results.append({
            "A": tuple(A.astype(int)),
            "B": tuple(B.astype(int)),
            "Điểm Tỷ lệ Vàng C": tuple(C.astype(int)),
            "Đoạn Lớn (AC)": f"{AC_len:.2f} px",
            "Đoạn Nhỏ (CB)": f"{CB_len:.2f} px",
            "Tỷ lệ (AC/CB)": f"{AC_len/CB_len:.3f}",
        })

        # Reset để đo đoạn tiếp theo
        st.session_state.clicks = []

    st.image(overlay, use_column_width=True)

    # ==============================
    # BẢNG KẾT QUẢ
    # ==============================
    if st.session_state.results:
        st.subheader("📏 Kết quả các đoạn đã đo")
        st.dataframe(st.session_state.results)
        
    # ==============================
    # Xóa toàn bộ
    # ==============================
    if st.button("Xóa tất cả"):
        st.session_state.clicks = []
        st.session_state.results = []
        st.rerun()
