import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Đo tỉ lệ Dài / Rộng", layout="centered")

MAX_W = 800
R = 7

if "points" not in st.session_state:
    st.session_state.points = []
if "measurements" not in st.session_state:
    pass
else:
    st.session_state.measurements = {"length": None, "width": None, "ratio": None}
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def draw_point(draw, p, color="red", radius=R):
    draw.ellipse((p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius), fill=color, outline="white", width=2)

def draw_line(draw, p1, p2, color="white"):
    draw.line([p1, p2], fill=color, width=3)

file = st.file_uploader("Upload ảnh cần đo tỉ lệ", type=["jpg","jpeg","png","webp"])

if file:
    if st.session_state.last_file != file.name:
        st.session_state.points = []
        st.session_state.measurements = {"length": None, "width": None, "ratio": None}
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size
    scale = MAX_W / w if w > MAX_W else 1
    display_size = (int(w * scale), int(h * scale))
    display_img = img.resize(display_size)

    click = streamlit_image_coordinates(display_img, key="pil")

    if click:
        real_x = int(click["x"] / scale)
        real_y = int(click["y"] / scale)
        point = (real_x, real_y)
        if not st.session_state.points or st.session_state.points[-1] != point:
            st.session_state.points.append(point)
            if len(st.session_state.points) > 4:
                st.session_state.points = st.session_state.points[-4:]

    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)
    points = st.session_state.points

    colors = ["lime", "lime", "cyan", "cyan"]
    for i, p in enumerate(points):
        scaled_p = (int(p[0]*scale), int(p[1]*scale))
        draw_point(draw, scaled_p, color=colors[i])

    if len(points) >= 2:
        p1 = (int(points[0][0]*scale), int(points[0][1]*scale))
        p2 = (int(points[1][0]*scale), int(points[1][1]*scale))
        draw_line(draw, p1, p2, "lime")
        length_px = np.linalg.norm(np.array(points[0]) - np.array(points[1]))
        st.session_state.measurements["length"] = round(length_px, 1)

    if len(points) >= 4:
        p3 = (int(points[2][0]*scale), int(points[2][1]*scale))
        p4 = (int(points[3][0]*scale), int(points[3][1]*scale))
        draw_line(draw, p3, p4, "cyan")
        width_px = np.linalg.norm(np.array(points[2]) - np.array(points[3]))
        st.session_state.measurements["width"] = round(width_px, 1)
        ratio = st.session_state.measurements["length"] / st.session_state.measurements["width"]
        st.session_state.measurements["ratio"] = round(ratio, 3)

    st.image(overlay, use_column_width=True)st.markdown("### Hướng dẫn")
    if len(points) < 2:
        st.info("Bước 1: Click 2 điểm để đo **chiều dài**")
    elif len(points) < 4:
        st.info("Bước 2: Click tiếp 2 điểm để đo **chiều rộng**")
    else:
        st.success("Đo xong!")

    m = st.session_state.measurements
    col1, col2, col3 = st.columns(3)
    with col1:
        if m["length"]:
            st.metric("Chiều dài", f"{m['length']} px")
    with col2:
        if m["width"]:
            st.metric("Chiều rộng", f"{m['width']} px")
    with col3:
        if m["ratio"]:
            st.metric("Tỉ lệ Dài/Rộng", m["ratio"])

    if st.button("Xóa tất cả điểm", type="primary"):
        st.session_state.points = []
        st.session_state.measurements = {"length": None, "width": None, "ratio": None}
        st.rerun()

else:
    st.info("Vui lòng upload ảnh để bắt đầu")
