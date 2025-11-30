import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Đo tỉ lệ Dài / Rộng", layout="centered")

MAX_W = 800          # chiều rộng tối đa hiển thị
R = 7                # bán kính điểm click

# Khởi tạo session state
if "points" not in st.session_state:
    st.session_state.points = []      # danh sách các điểm đã click: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
if "measurements" not in st.session_state:
    st.session_state.measurements = {"length": None, "width": None, "ratio": None}
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def draw_point(draw, p, color="red", radius=R):
    draw.ellipse((p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius), fill=color, outline="white", width=2)

def draw_line(draw, p1, p2, color="white"):
    draw.line([p1, p2], fill=color, width=3)

# Upload ảnh
file = st.file_uploader("Upload ảnh cần đo tỉ lệ", type=["jpg", "jpeg", "png", "webp"])

if file:
    # Reset khi đổi ảnh mới
    if st.session_state.last_file != file.name:
        st.session_state.points = []
        st.session_state.measurements = {"length": None, "width": None, "ratio": None}
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size

    # Resize để hiển thị đẹp (giữ tỉ lệ)
    scale = MAX_W / w if w > MAX_W else 1
    display_size = (int(w * scale), int(h * scale))
    display_img = img.resize(display_size)

    # Lấy tọa độ click
    click = streamlit_image_coordinates(display_img, key="pil")

    if click:
        # Chuyển đổi về tọa độ gốc ảnh thật
        real_x = int(click["x"] / scale)
        real_y = int(click["y"] / scale)
        point = (real_x, real_y)

        # Chỉ thêm điểm mới nếu khác điểm trước đó
        if not st.session_state.points or st.session_state.points[-1] != point:
            st.session_state.points.append(point)
            # Tối đa 4 điểm (2 đoạn)
            if len(st.session_state.points) > 4:
                st.session_state.points = st.session_state.points[-4:]

    # Vẽ overlay
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)

    points = st.session_state.points

    # Vẽ các điểm và đoạn đã chọn
    colors = ["lime", "lime", "cyan", "cyan"]
    for i, p in enumerate(points):
        scaled_p = (int(p[0]*scale), int(p[1]*scale))
        draw_point(draw, scaled_p, color=colors[i])

    # Vẽ đoạn dài (điểm 0 → 1)
    if len(points) >= 2:
        p1 = (int(points[0][0]*scale), int(points[0][1]*scale))
        p2 = (int(points[1][0]*scale), int(points[1][1]*scale))
        draw_line(draw, p1, p2, "lime")
        length_px = np.linalg.norm(np.array(points[0]) - np.array(points[1]))
        st.session_state.measurements["length"] = round(length_px, 1)

    # Vẽ đoạn rộng (điểm 2 → 3)
    if len(points) >= 4:
        p3 = (int(points[2][0]*scale), int(points[2][1]*scale))
        p4 = (int(points[3][0]*scale), int(points[3][1]*scale))
        draw_line(draw, p3, p4, "cyan")
        width_px = np.linalg.norm(np.array(points[2]) - np.array(points[3]))
        st.session_state.measurements["width"] = round(width_px, 1)

        # Tính tỉ lệ
        ratio = st.session_state.measurements["length"] / st.session_state.measurements["width"]
        st.session_state.measurements["ratio"] = round(ratio, 3)

    # Hiển thị ảnh
    st.image(overlay, use_column_width=True)

    # Hiển thị hướng dẫn
    st.markdown("### Hướng dẫn")
    if len(points) < 2:
        st.info("Bước 1: Click 2 điểm để đo **chiều dài** (ví dụ: chiều cao toàn thân hoặc chiều cao khuôn mặt)")
    elif len(points) < 4:
        st.info("Bước 2: Click tiếp 2 điểm để đo **chiều rộng** (ví dụ: rộng vai, rộng hông)")
    else:
        st.success("Đo xong! Bạn có thể click thêm 2 điểm mới để đo lại.")

    # Hiển thị kết quả
    m = st.session_state.measurements
    col1, col2, col3 = st.columns(3)
    with col1:
        if m["length"] is not None:
            st.metric("Chiều dài", f"{m['length']} px")
    with col2:
        if m["width"] is not None:
            st.metric("Chiều rộng", f"{m['width']} px")
    with col3:
        if m["ratio"] is not None:
            st.metric("Tỉ lệ Dài/Rộng", m["ratio"], help="Càng gần 1.618 → càng gần tỉ lệ vàng")

    # Nút xóa
    if st.button("Xóa tất cả điểm", type="primary"):
        st.session_state.points = []
        st.session_state.measurements = {"length": None, "width": None, "ratio": None}
        st.rerun()

else:
    st.info("Vui lòng upload ảnh để bắt đầu đo tỉ lệ cơ thể/khuôn mặt")
    st.markdown("""
    **Cách dùng:**
    1. Upload ảnh đứng thẳng, rõ nét
    2. Click 2 điểm đầu tiên → đo chiều dài chính (thường là chiều cao)
    3. Click 2 điểm tiếp → đo chiều rộng quan trọng (vai, hông, mặt...)
    4. Xem tỉ lệ ngay lập tức!
    """)
