import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Kiểm tra tỉ lệ vàng", layout="centered")

PHI = (1 + 5**0.5) / 2
MAX_W = 700
R = 5

if "clicks" not in st.session_state:
    st.session_state.clicks = []
if "ketqua" not in st.session_state:
    st.session_state.ketqua = []
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def diem(draw, p, color="red"):
    draw.ellipse((p[0]-R, p[1]-R, p[0]+R, p[1]+R), fill=color)

def duong(draw, p1, p2):
    draw.line([p1, p2], fill="white", width=3)

file = st.file_uploader("Chọn ảnh", type=["jpg","jpeg","png","webp"])

if file:
    if st.session_state.last_file != file.name:
        st.session_state.clicks = []
        st.session_state.ketqua = []
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size
    scale = 1
    if w > MAX_W:
        scale = MAX_W / w
        display_img = = img.resize((int(w*scale), int(h*scale)))
    else:
        display_img = img.copy()

    click = streamlit_image_coordinates(display_img, key="click")

    if click:
        x = int(click["x"] / scale)
        y = int(click["y"] / scale)
        if not st.session_state.clicks or st.session_state.clicks[-1] != (x,y):
            st.session_state.clicks.append((x,y))

    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)
    clicks = st.session_state.clicks

    if len(clicks) >= 1:
        a = clicks[0]
        ax, ay = int(a[0]*scale), int(a[1]*scale)
        diem(draw, (ax, ay), "red")

    if len(clicks) >= 2:
        b = clicks[1]
        bx, by = int(b[0]*scale), int(b[1]*scale)
        diem(draw, (bx, by), "red")
        duong(draw, (ax, ay), (bx, by))

        A = np.array(clicks[0])
        B = np.array(clicks[1])
        C = A + (B - A) / PHI

        cx, cy = int(C[0]*scale), int(C[1]*scale)
        diem(draw, (cx, cy), "yellow")

        ac = np.linalg.norm(C - A)
        cb = np.linalg.norm(B - C)

        st.session_state.ketqua.append({
            "A": clicks[0],
            "B": clicks[1],
            "C (tỉ lệ vàng)": (int(C[0]), int(C[1])),
            "AC": round(ac, 2),
            "CB": round(cb, 2),
            "AC/CB": round(ac/cb, 3)
        })

        st.session_state.clicks = []

    st.image(overlay, use_column_width=True)

    if st.session_state.ketqua:
        st.write("### Kết quả đo")
        st.dataframe(st.session_state.ketqua, use_container_width=True)

    if st.button("Xóa hết"):
        st.session_state.clicks = []
        st.session_state.ketqua = []
        st.rerun()
