import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(layout="wide")
st.title("🔍 Kiểm tra tỉ lệ vàng trên đoạn thẳng")

uploaded_file = st.file_uploader("Tải ảnh lên", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    w, h = img.size

    # Dùng font mặc định (Không lỗi trên Streamlit)
    font = ImageFont.load_default()

    st.image(img, caption="Ảnh gốc", use_column_width=True)

    # Lưu các điểm người dùng chọn
    if "all_segments" not in st.session_state:
        st.session_state.all_segments = []  # lưu nhiều đoạn
    if "current_points" not in st.session_state:
        st.session_state.current_points = []  # điểm của đoạn hiện tại

    click = st.image(img, caption="Chọn điểm", use_column_width=True)

    # Input click:
    event = st.get_event("click")

    if event and uploaded_file:
        x = int(event.x * w)
        y = int(event.y * h)

        # Xử lý chọn điểm
        if len(st.session_state.current_points) < 2:
            st.session_state.current_points.append((x, y))

        elif len(st.session_state.current_points) == 2:
            # Kiểm tra xem điểm thứ 3 có nằm trên đường thẳng AB không
            (x1, y1), (x2, y2) = st.session_state.current_points

            # Tính khoảng cách từ điểm C đến đoạn AB
            A = np.array([x1, y1])
            B = np.array([x2, y2])
            C = np.array([x, y])

            AB = B - A
            AC = C - A

            # Tính t bằng hình chiếu
            t = np.dot(AC, AB) / np.dot(AB, AB)
            if 0 <= t <= 1:
                C_projected = A + t * AB
                st.session_state.current_points.append(tuple(C_projected.astype(int)))
            else:
                st.warning("⚠ Điểm thứ 3 phải nằm trên đoạn thẳng!")

    # Khi có 3 điểm → xử lý
    if len(st.session_state.current_points) == 3:
        (x1, y1), (x2, y2), (xm, ym) = st.session_state.current_points

        # Tính điểm tỉ lệ vàng
        AB = np.array([x2 - x1, y2 - y1])
        golden_ratio = 1 / 1.61803398875
        G = np.array([x1, y1]) + golden_ratio * AB
        G = tuple(G.astype(int))

        # Tính phần trăm lệch
        A = np.array([x1, y1])
        B = np.array([x2, y2])
        M = np.array([xm, ym])
        GM = np.array(G)

        total_len = np.linalg.norm(B - A)
        dist_mid = np.linalg.norm(M - A)
        dist_golden = np.linalg.norm(GM - A)

        percent = (dist_mid / dist_golden) * 100

        # Vẽ lên ảnh
        draw_img = img.copy()
        draw = ImageDraw.Draw(draw_img)

        # Vẽ đường AB
        draw.line((x1, y1, x2, y2), fill="yellow", width=3)

        # Vẽ các điểm
        draw.ellipse((x1-6, y1-6, x1+6, y1+6), fill="red")
        draw.ellipse((x2-6, y2-6, x2+6, y2+6), fill="red")
        draw.ellipse((xm-6, ym-6, xm+6, ym+6), fill="cyan")  # điểm giữa
        draw.ellipse((G[0]-6, G[1]-6, G[0]+6, G[1]+6), fill="green")  # điểm tỉ lệ vàng

        # Ghi thông số
        draw.text((xm+10, ym), f"{percent:.1f}%", fill="cyan", font=font)

        st.image(draw_img, caption="Kết quả", use_column_width=True)

        # Nút lưu đoạn này và tiếp tục đo đoạn mới
        if st.button("Đo đoạn tiếp theo"):
            st.session_state.all_segments.append({
                "A": (x1, y1),
                "B": (x2, y2),
                "Mid": (xm, ym),
                "Golden": G,
                "Percent": percent
            })
            st.session_state.current_points = []  # reset cho đoạn mới

    # Hiển thị danh sách các đoạn đã đo
    if st.session_state.all_segments:
        st.subheader("📌 Các đoạn đã đo")
        for i, seg in enumerate(st.session_state.all_segments, 1):
            st.write(f"**Đoạn {i}:** {seg['Percent']:.1f}% so với tỉ lệ vàng")
