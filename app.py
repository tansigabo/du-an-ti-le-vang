import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd

st.set_page_config(page_title="Đo tỉ lệ Dài/Rộng (Nhiều lần - Giữ kết quả)", layout="centered")

MAX_W = 800
R = 8

# Session state
if "points" not in st.session_state:
    st.session_state.points = []          # Điểm đang đo hiện tại (0-4)
if "completed_measurements" not in st.session_state:
    st.session_state.completed_measurements = []  # Các lần đo đã HOÀN THÀNH và đang hiển thị
if "waiting_for_next" not in st.session_state:
    st.session_state.waiting_for_next = False     # Đang chờ click để bắt đầu lần mới
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def draw_point(draw, p, color="red", radius=R):
    draw.ellipse((p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius), fill=color, outline="white", width=3)

def draw_line(draw, p1, p2, color="white", width=4):
    draw.line([p1, p2], fill=color, width=width)

# Upload ảnh
file = st.file_uploader("Upload ảnh lá, vật thể cần đo tỉ lệ", type=["jpg","jpeg","png","webp"])

if file:
    if st.session_state.last_file != file.name:
        # Reset tất cả khi đổi ảnh
        st.session_state.points = []
        st.session_state.completed_measurements = []
        st.session_state.waiting_for_next = False
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size
    scale = MAX_W / w if w > MAX_W else 1
    display_size = (int(w * scale), int(h * scale))
    display_img = img.resize(display_size)

    # Nhận click từ người dùng
    click = streamlit_image_coordinates(display_img, key="pil")

    # Xử lý click
    if click:
        real_x = int(click["x"] / scale)
        real_y = int(click["y"] / scale)
        new_point = (real_x, real_y)

        # Nếu đang chờ click để bắt đầu lần mới → bắt đầu lại từ đầu
        if st.session_state.waiting_for_next:
            st.session_state.points = [new_point]
            st.session_state.waiting_for_next = False
            st.rerun()

        # Nếu đang trong quá trình đo (dưới 4 điểm)
        elif len(st.session_state.points) < 4:
            # Tránh click trùng điểm cuối
            if not st.session_state.points or st.session_state.points[-1] != new_point:
                st.session_state.points.append(new_point)
                st.rerun()

                # Khi vừa đủ 4 điểm → hoàn thành lần đo này
                if len(st.session_state.points) == 4:
                    p1, p2, p3, p4 = st.session_state.points
                    length = round(np.linalg.norm(np.array(p1) - np.array(p2)), 1)
                    width = round(np.linalg.norm(np.array(p3) - np.array(p4)), 1)
                    ratio = round(length / width, 3) if width > 0 else 0

                    # Lưu lần đo hoàn thành
                    st.session_state.completed_measurements.append({
                        "points": st.session_state.points.copy(),
                        "length": length,
                        "width": width,
                        "ratio": ratio
                    })

                    # Chuyển sang trạng thái chờ click để bắt đầu lần mới
                    st.session_state.waiting_for_next = True
                    st.session_state.points = []  # Xóa điểm tạm để không vẽ chồng

    # === VẼ ẢNH ===
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)

    # 1. Vẽ tất cả các lần đo đã hoàn thành (giữ nguyên trên ảnh)
    for meas in st.session_state.completed_measurements:
        pts = meas["points"]
        # Đường dài (xanh lá)
        sp1 = (int(pts[0][0]*scale), int(pts[0][1]*scale))
        sp2 = (int(pts[1][0]*scale), int(pts[1][1]*scale))
        draw_line(draw, sp1, sp2, color="#00ff00", width=5)
        draw_point(draw, sp1, color="#00ff00")
        draw_point(draw, sp2, color="#00ff00")

        # Đường rộng (xanh dương)
        sp3 = (int(pts[2][0]*scale), int(pts[2][1]*scale))
        sp4 = (int(pts[3][0]*scale), int(pts[3][1]*scale))
        draw_line(draw, sp3, sp4, color="#00ffff", width=5)
        draw_point(draw, sp3, color="#00ffff")
        draw_point(draw, sp4, color="#00ffff")

    # 2. Vẽ các điểm đang đo hiện tại (nếu có)
    for i, p in enumerate(st.session_state.points):
        sp = (int(p[0]*scale), int(p[1]*scale))
        color = "#00ff00" if i < 2 else "#00ffff"  # xanh lá = dài, xanh dương = rộng
        draw_point(draw, sp, color=color)

    # Vẽ đoạn đang đo
    if len(st.session_state.points) >= 2:
        sp1 = (int(st.session_state.points[0][0]*scale), int(st.session_state.points[0][1]*scale))
        sp2 = (int(st.session_state.points[1][0]*scale), int(st.session_state.points[1][1]*scale))
        draw_line(draw, sp1, sp2, color="#00ff00", width=4)
    if len(st.session_state.points) == 4:
        sp3 = (int(st.session_state.points[2][0]*scale), int(st.session_state.points[2][1]*scale))
        sp4 = (int(st.session_state.points[3][0]*scale), int(st.session_state.points[3][1]*scale))
        draw_line(draw, sp3, sp4, color="#00ffff", width=4)

    # Hiển thị ảnh
    st.image(overlay, use_column_width=True)

    # === HƯỚNG DẪN ===
    if st.session_state.waiting_for_next:
        st.success("Đo xong lần này! Click bất kỳ đâu trên ảnh để bắt đầu lần đo mới")
    elif len(st.session_state.points) == 0 and not st.session_state.completed_measurements:
        st.info("Bước 1: Click 2 điểm để đo chiều dài (màu xanh lá)")
    elif len(st.session_state.points) < 2:
        st.info("Đang đo chiều dài... Click điểm thứ 2")
    elif len(st.session_state.points) < 4:
        st.info("Đang đo chiều rộng... Click 2 điểm màu xanh dương")
    else:
        st.success("Đã đủ 4 điểm! Đang chờ bạn kiểm tra kết quả...")

    # Hiển thị bảng kết quả
    if st.session_state.completed_measurements:
        st.markdown("---")
        st.subheader(f"Lịch sử đo ({len(st.session_state.completed_measurements)} lần)")

        data = []
        for i, m in enumerate(st.session_state.completed_measurements):
            data.append({
                "Lần": i+1,
                "Dài (px)": m["length"],
                "Rộng (px)": m["width"],
                "Tỉ lệ Dài/Rộng": m["ratio"]
            })
        df = pd.DataFrame(data)
        st.dataframe(df.style.format({
            "Dài (px)": "{:.1f}",
            "Rộng (px)": "{:.1f}",
            "Tỉ lệ Dài/Rộng": "{:.3f}"
        }), use_container_width=True)

        # Thống kê trung bình
        with st.expander("Xem tỉ lệ trung bình"):
            avg = np.mean([m["ratio"] for m in st.session_state.completed_measurements])
            st.metric("Tỉ lệ trung bình", f"{avg:.3f}")

    # Nút xóa tất cả
    if st.button("Xóa tất cả kết quả", type="secondary"):
        st.session_state.completed_measurements = []
        st.session_state.points = []
        st.session_state.waiting_for_next = False
        st.rerun()

else:
    st.info("Vui lòng upload ảnh để bắt đầu đo")
