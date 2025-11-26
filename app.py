import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="Kiểm tra điểm tỉ lệ vàng", layout="centered")
st.title("📐 Kiểm tra điểm gần tỉ lệ vàng (A–B–M)")
st.write("Chọn **A (đầu)** → **B (cuối)** → hệ thống vẽ đường thẳng nét đứt → sau đó chọn **M**, chương trình sẽ ép M vào đúng đường thẳng AB.")

PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700

def ve_diem(draw, p, color, r=5):
    draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)

def ve_duong_dut(draw, p1, p2, step=12):
    """Vẽ đường thẳng nét đứt từ p1 đến p2"""
    x1, y1 = p1
    x2, y2 = p2
    length = int(np.linalg.norm(np.array(p2)-np.array(p1)))
    for i in range(0, length, step*2):
        t1 = i/length
        t2 = min((i+step)/length, 1)
        xa, ya = x1 + (x2-x1)*t1, y1 + (y2-y1)*t1
        xb, yb = x1 + (x2-x1)*t2, y1 + (y2-y1)*t2
        draw.line([(xa, ya), (xb, yb)], fill="white", width=2)

def ep_diem_len_doan(A, B, M):
    """Chiếu điểm M lên đoạn thẳng AB"""
    A = np.array(A, float)
    B = np.array(B, float)
    M = np.array(M, float)
    AB = B - A
    t = np.dot(M - A, AB) / np.dot(AB, AB)
    t = max(0, min(1, t))     # ép nằm trong đoạn [0,1]
    return A + t*AB

if 'clicks' not in st.session_state:
    st.session_state['clicks'] = []
if 'uploaded_img_data' not in st.session_state:
    st.session_state['uploaded_img_data'] = None

uploaded_file = st.file_uploader("Chọn ảnh...", type=["jpg", "png", "webp"])

if uploaded_file:
    if st.session_state['uploaded_img_data'] != uploaded_file.name:
        st.session_state['clicks'] = []
        st.session_state['uploaded_img_data'] = uploaded_file.name

    image_orig = Image.open(uploaded_file).convert("RGB")

    # Resize nếu cần
    display_image = image_orig.copy()
    if image_orig.width > MAX_DISPLAY_WIDTH:
        ratio = MAX_DISPLAY_WIDTH / image_orig.width
        scale_factor = 1 / ratio
        display_image = display_image.resize((MAX_DISPLAY_WIDTH, int(image_orig.height * ratio)))
    else:
        ratio = 1.0
        scale_factor = 1.0

    # CLICK
    value = streamlit_image_coordinates(display_image, key="click_area", width=display_image.width)

    # Lưu click
    if value:
        x_disp, y_disp = value["x"], value["y"]
        x_orig = int(x_disp * scale_factor)
        y_orig = int(y_disp * scale_factor)
        pt = (x_orig, y_orig)
        if not st.session_state['clicks'] or st.session_state['clicks'][-1] != pt:
            st.session_state['clicks'].append(pt)

    clicks = st.session_state['clicks']
    overlay = display_image.copy()
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    # --- VẼ A ---
    if len(clicks) >= 1:
        A = np.array(clicks[0])
        A_disp = tuple((A * ratio).astype(int))
        ve_diem(draw, A_disp, "red")

    # --- VẼ B + đường nét đứt ---
    if len(clicks) >= 2:
        B = np.array(clicks[1])
        B_disp = tuple((B * ratio).astype(int))
        ve_diem(draw, B_disp, "red")

        # Vẽ đường thẳng nét đứt A–B
        ve_duong_dut(draw, A_disp, B_disp)

    # --- XỬ LÝ M ---
    if len(clicks) >= 3:
        A = np.array(clicks[0])
        B = np.array(clicks[1])
        M_raw = np.array(clicks[2])

        # Chiếu M lên đoạn AB
        M = ep_diem_len_doan(A, B, M_raw)

        # Tính điểm tỉ lệ vàng C
        C = A + (B - A) / PHI

        # Convert sang hiển thị
        M_disp = tuple((M * ratio).astype(int))
        C_disp = tuple((C * ratio).astype(int))
        ve_diem(draw, M_disp, "blue")
        ve_diem(draw, C_disp, "yellow")

        # Tính % sai lệch
        AC = np.linalg.norm(C - A)
        AM = np.linalg.norm(M - A)
        percent = abs(AM - AC) / AC * 100
        percent_text = f"{percent:.1f}%"

        # Hiển thị số %
        draw.text((M_disp[0] + 5, M_disp[1] - 5), percent_text, fill="white", font=font)

    st.image(overlay, caption="Ảnh sau khi đánh dấu", use_column_width=True)

    if st.button("Xóa"):
        st.session_state['clicks'] = []
        st.rerun()
