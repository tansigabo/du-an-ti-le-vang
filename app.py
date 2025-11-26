import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="Kiểm tra tỉ lệ vàng", layout="centered")
st.title("📐 Công cụ kiểm tra điểm gần tỉ lệ vàng (A–B–M) — Đo nhiều đoạn liên tục")

st.markdown("""
### 👉 Hướng dẫn:
- **Bước 1:** Click chọn điểm **A**  
- **Bước 2:** Click chọn điểm **B**  
    → Hệ thống sẽ vẽ đường thẳng nét đứt  
- **Bước 3:** Click điểm **M**  
    → Hệ thống tự ép M vào đường AB và tính % lệch tỉ lệ vàng  
- Sau khi đo xong, chương trình tự động chuyển sang đo đoạn tiếp theo.
""")

PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700

# ==============================
# Hàm vẽ
# ==============================
def ve_diem(draw, p, color, r=4):
    """Vẽ điểm nhỏ"""
    draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)

def ve_duong_dut(draw, p1, p2, step=14):
    """Vẽ đường thẳng nét đứt"""
    x1, y1 = p1
    x2, y2 = p2
    length = int(np.linalg.norm(np.array(p2)-np.array(p1)))
    for i in range(0, length, step*2):
        t1 = i / length
        t2 = min((i + step) / length, 1)
        xa, ya = x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1
        xb, yb = x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2
        draw.line([(xa, ya), (xb, yb)], fill="white", width=2)

def ep_diem(A, B, M):
    """Chiếu điểm M lên AB"""
    A = np.array(A, float)
    B = np.array(B, float)
    M = np.array(M, float)
    AB = B - A
    t = np.dot(M - A, AB) / np.dot(AB, AB)
    t = max(0, min(1, t))
    return A + t * AB

# ==============================
# Session state
# ==============================
if "clicks" not in st.session_state: st.session_state.clicks = []
if "results" not in st.session_state: st.session_state.results = []
if "last_image" not in st.session_state: st.session_state.last_image = None

# ==============================
# Upload ảnh
# ==============================
uploaded_file = st.file_uploader("Chọn ảnh...", type=["jpg", "png", "webp"])

if uploaded_file:

    # Reset khi đổi ảnh
    if st.session_state.last_image != uploaded_file.name:
        st.session_state.clicks = []
        st.session_state.results = []
        st.session_state.last_image = uploaded_file.name

    img = Image.open(uploaded_file).convert("RGB")

    # Resize hiển thị
    display_img = img.copy()
    if img.width > MAX_DISPLAY_WIDTH:
        ratio = MAX_DISPLAY_WIDTH / img.width
        scale_back = img.width / MAX_DISPLAY_WIDTH
        display_img = display_img.resize((MAX_DISPLAY_WIDTH, int(img.height * ratio)))
    else:
        ratio = 1.0
        scale_back = 1.0

    # Lấy click
    click = streamlit_image_coordinates(display_img, key="click_area", width=display_img.width)

    if click:
        x = int(click["x"] * scale_back)
        y = int(click["y"] * scale_back)
        if not st.session_state.clicks or st.session_state.clicks[-1] != (x, y):
            st.session_state.clicks.append((x, y))

    clicks = st.session_state.clicks
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)

    font = ImageFont.truetype("arial.ttf", size=14) if "arial.ttf" else ImageFont.load_default()

    # ==============================
    # VẼ A
    # ==============================
    if len(clicks) >= 1:
        A = np.array(clicks[0])
        A_disp = tuple((A * ratio).astype(int))
        ve_diem(draw, A_disp, "red")

    # ==============================
    # VẼ B + đường nét đứt
    # ==============================
    if len(clicks) >= 2:
        B = np.array(clicks[1])
        B_disp = tuple((B * ratio).astype(int))
        ve_diem(draw, B_disp, "red")
        ve_duong_dut(draw, A_disp, B_disp)

    # ==============================
    # Xử lý M
    # ==============================
    if len(clicks) == 3:
        M_raw = np.array(clicks[2])
        M = ep_diem(A, B, M_raw)

        C = A + (B - A) / PHI

        # Chuyển sang tọa độ hiển thị
        M_disp = tuple((M * ratio).astype(int))
        C_disp = tuple((C * ratio).astype(int))

        ve_diem(draw, M_disp, "cyan")
        ve_diem(draw, C_disp, "yellow")

        # Lệch %
        AC = np.linalg.norm(C - A)
        AM = np.linalg.norm(M - A)
        percent = abs(AM - AC) / AC * 100

        draw.text((M_disp[0] + 10, M_disp[1] - 10), f"{percent:.1f}%", fill="white", font=font)

        # Lưu kết quả
        st.session_state.results.append({
            "A": tuple(A.astype(int)),
            "B": tuple(B.astype(int)),
            "M": tuple(M.astype(int)),
            "Golden": tuple(C.astype(int)),
            "Sai lệch (%)": round(percent, 2),
        })

        # Reset để đo đoạn tiếp theo
        st.session_state.clicks = []

    # ==============================
    # Hiển thị ảnh
    # ==============================
    st.image(overlay, caption="Ảnh sau khi đo", use_column_width=True)

    # ==============================
    # BẢNG KẾT QUẢ
    # ==============================
    if st.session_state.results:
        st.subheader("📌 Kết quả các đoạn đã đo")
        st.table(st.session_state.results)

    # ==============================
    # Nút xóa
    # ==============================
    if st.button("Xóa tất cả"):
        st.session_state.clicks = []
        st.session_state.results = []
        st.rerun()
