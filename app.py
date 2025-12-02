import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Đo tỉ lệ Dài / Rộng (Nhiều lần)", layout="centered")

MAX_W = 800
R = 7

# Khởi tạo session_state
if "points" not in st.session_state:
    st.session_state.points = []          # 4 điểm hiện tại đang đo
if "history" not in st.session_state:
    st.session_state.history = []         # Danh sách các lần đo đã hoàn thành
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def draw_point(draw, p, color="red", radius=R):
    draw.ellipse((p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius), fill=color, outline="white", width=2)

def draw_line(draw, p1, p2, color="white"):
    draw.line([p1, p2], fill=color, width=3)

# Upload ảnh
file = st.file_uploader("Upload ảnh cần đo tỉ lệ", type=["jpg","jpeg","png","webp"])

if file:
    # Reset khi đổi ảnh mới
    if st.session_state.last_file != file.name:
        st.session_state.points = []
        st.session_state.history = []
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size
    scale = MAX_W / w if w > MAX_W else 1
    display_size = (int(w * scale), int(h * scale))
    display_img = img.resize(display_size)

    # Nhận click
    click = streamlit_image_coordinates(display_img, key="pil")

    if click:
        real_x = int(click["x"] / scale)
        real_y = int(click["y"] / scale)
        point = (real_x, real_y)

        # Chỉ thêm điểm mới nếu khác điểm cuối
        if not st.session_state.points or st.session_state.points[-1] != point:
            st.session_state.points.append(point)

            # Giới hạn tối đa 4 điểm cho lần đo hiện tại
            if len(st.session_state.points) > 4:
                st.session_state.points = st.session_state.points[-4:]

            # Khi đủ 4 điểm → tính toán và lưu kết quả, rồi reset để đo lần mới
            if len(st.session_state.points) == 4:
                p1, p2, p3, p4 = st.session_state.points

                length_px = round(np.linalg.norm(np.array(p1) - np.array(p2)), 1)
                width_px = round(np.linalg.norm(np.array(p3) - np.array(p4)), 1)
                ratio = round(length_px / width_px, 3) if width_px != 0 else 0

                # Lưu vào lịch sử
                st.session_state.history.append({
                    "lần": len(st.session_state.history) + 1,
                    "dài": length_px,
                    "rộng": width_px,
                    "tỉ_lệ": ratio
                })

                # Tự động reset để đo lần tiếp theo
                st.session_state.points = []
                st.rerun()  # Cập nhật giao diện ngay

    # Vẽ overlay
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)
    points = st.session_state.points
    colors = ["lime", "lime", "cyan", "cyan"]

    for i, p in enumerate(points):
        scaled_p = (int(p[0] * scale), int(p[1] * scale))
        draw_point(draw, scaled_p, color=colors[i])

    # Vẽ đoạn dài (xanh lá)
    if len(points) >= 2:
        p1 = (int(points[0][0]*scale), int(points[0][1]*scale))
        p2 = (int(points[1][0]*scale), int(points[1][1]*scale))
        draw_line(draw, p1, p2, "lime")

    # Vẽ đoạn rộng (xanh dương)
    if len(points) >= 4:
        p3 = (int(points[2][0]*scale), int(points[2][1]*scale))
        p4 = (int(points[3][0]*scale), int(points[3][1]*scale))
        draw_line(draw, p3, p4, "cyan")

    # Hiển thị ảnh
    st.image(overlay, use_column_width=True)

    # Hướng dẫn người dùng
    if len(points) < 2:
        st.info("🔴 Bước 1: Click 2 điểm để đo **chiều dài** (màu xanh lá)")
    elif len(points) < 4:
        st.info("🔵 Bước 2: Click tiếp 2 điểm để đo **chiều rộng** (màu xanh dương)")
    else:
        st.success("✅ Đã đo xong! Đang chờ bạn đo lần tiếp theo...")

    # Hiển thị kết quả lần đo hiện tại (nếu đang đo giữa chừng)
    col1, col2, col3 = st.columns(3)
    with col1:
        if len(points) >= 2:
            length = np.linalg.norm(np.array(points[0]) - np.array(points[1]))
            st.metric("Chiều dài (đang đo)", f"{round(length, 1)} px")
    with col2:
        if len(points) >= 4:
            width = np.linalg.norm(np.array(points[2]) - np.array(points[3]))
            st.metric("Chiều rộng (đang đo)", f"{round(width, 1)} px")
    with col3:
        if len(points) >= 4:
            ratio = length / width if width > 0 else 0
            st.metric("Tỉ lệ tạm thời", round(ratio, 3))

    # Nút xóa tất cả (nếu cần)
    if st.button("🗑️ Xóa tất cả kết quả", type="secondary"):
        st.session_state.points = []
        st.session_state.history = []
        st.rerun()

    # === HIỂN THỊ LỊCH SỬ ĐO ===
    if st.session_state.history:
        st.markdown("---")
        st.subheader(f"📊 Lịch sử đo ({len(st.session_state.history)} lần)")
        
        # Tạo bảng đẹp
        import pandas as pd
        df = pd.DataFrame(st.session_state.history)
        df.index = df.index + 1
        st.dataframe(
            df[["lần", "dài", "rộng", "tỉ_lệ"]].style.format({
                "dài": "{:.1f} px",
                "rộng": "{:.1f} px",
                "tỉ_lệ": "{:.3f}"
            }),
            use_container_width=True
        )

        # Thống kê trung bình (tùy chọn)
        with st.expander("📈 Xem thống kê trung bình"):
            avg_ratio = np.mean([x["tỉ_lệ"] for x in st.session_state.history])
            st.metric("Tỉ lệ trung bình Dài/Rộng", f"{avg_ratio:.3f}")

else:
    st.info("👆 Vui lòng upload ảnh để bắt đầu đo tỉ lệ")
