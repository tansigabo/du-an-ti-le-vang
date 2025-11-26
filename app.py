import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="Kiểm tra điểm tỉ lệ vàng", layout="centered")
st.title("📐 Kiểm tra điểm gần tỉ lệ vàng")
st.write("Chọn **3 điểm**: Điểm đầu (A), điểm cuối (B), điểm giữa muốn kiểm tra (M).")

PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700

def ve_diem(draw, p, color, r=4):
    draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)

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

    # Widget click
    value = streamlit_image_coordinates(display_image, key="click_area", width=display_image.width)

    # Lưu điểm
    if value:
        x_disp, y_disp = value["x"], value["y"]
        x_orig = int(x_disp * scale_factor)
        y_orig = int(y_disp * scale_factor)
        pt = (x_orig, y_orig)
        if not st.session_state['clicks'] or st.session_state['clicks'][-1] != pt:
            st.session_state['clicks'].append(pt)

    # Tạo overlay
    overlay = display_image.copy()
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    clicks = st.session_state['clicks']

    if len(clicks) >= 1:
        A_disp = tuple((np.array(clicks[0]) * ratio).astype(int))
        ve_diem(draw, A_disp, "red")

    if len(clicks) >= 2:
        B_disp = tuple((np.array(clicks[1]) * ratio).astype(int))
        ve_diem(draw, B_disp, "red")

    if len(clicks) >= 3:
        A = np.array(clicks[0])
        B = np.array(clicks[1])
        M = np.array(clicks[2])

        # Tính điểm tỉ lệ vàng C
        C = A + (B - A) / PHI

        A_disp = (A * ratio).astype(int)
        B_disp = (B * ratio).astype(int)
        M_disp = (M * ratio).astype(int)
        C_disp = (C * ratio).astype(int)

        # Vẽ điểm A, B, M, C
        ve_diem(draw, tuple(A_disp), "red")
        ve_diem(draw, tuple(B_disp), "red")
        ve_diem(draw, tuple(M_disp), "blue")
        ve_diem(draw, tuple(C_disp), "yellow")

        # Tính % sai lệch
        AC = np.linalg.norm(C - A)
        AM = np.linalg.norm(M - A)
        percent = abs(AM - AC) / AC * 100
        percent_text = f"{percent:.1f}%"

        # Ghi con số % cạnh điểm M
        draw.text((M_disp[0] + 5, M_disp[1] - 5), percent_text, fill="white", font=font)

    st.image(overlay, caption="Ảnh với các điểm và thông số", use_column_width=True)

    # Reset
    if st.button("Xóa"):
        st.session_state['clicks'] = []
        st.experimental_rerun()
