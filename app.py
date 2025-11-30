import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Kiểm tra tỉ lệ vàng", layout="centered")

PHI = (1 + 5**0.5) / 2  # Tỉ lệ vàng chính xác: ≈1.618033988749895
MAX_W = 700
R = 6

if "clicks" not in st.session_state:
    st.session_state.clicks = []
if "ketqua" not in st.session_state:
    st.session_state.ketqua = []
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def diem(draw, p, color="red"):
    draw.ellipse((p[0]-R, p[1]-R, p[0]+R, p[1]+R), fill=color, outline="black", width=2)

def duong(draw, p1, p2, color="white"):
    draw.line([p1, p2], fill=color, width=3)

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
        display_img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    else:
        display_img = img.copy()

    click = streamlit_image_coordinates(display_img, key="click")

    if click:
        x = int(click["x"] / scale)
        y = int(click["y"] / scale)
        new_point = (x, y)
        if not st.session_state.clicks or st.session_state.clicks[-1] != new_point:
            st.session_state.clicks.append(new_point)
            if len(st.session_state.clicks) > 2:
                st.session_state.clicks = st.session_state.clicks[-2:]  # Chỉ giữ 2 điểm gần nhất

    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)
    clicks = st.session_state.clicks

    # Vẽ điểm A
    if len(clicks) >= 1:
        a_scaled = (int(clicks[0][0] * scale), int(clicks[0][1] * scale))
        diem(draw, a_scaled, "red")
        st.write(f"**A**: ({clicks[0][0]}, {clicks[0][1]})")

    # Khi có đủ 2 điểm → tính và vẽ C (điểm chia tỉ lệ vàng)
    if len(clicks) >= 2:
        A = np.array(clicks[0], dtype=float)
        B = np.array(clicks[1], dtype=float)
        b_scaled = (int(B[0] * scale), int(B[1] * scale))

        diem(draw, b_scaled, "red")
        duong(draw, a_scaled, b_scaled)

        # Tính điểm C sao cho AC/CB = PHI (AC > CB)
        C = A + (B - A) / PHI
        c_scaled = (int(C[0] * scale), int(C[1] * scale))
        diem(draw, c_scaled, "yellow")
        duong(draw, a_scaled, c_scaled, "yellow")
        duong(draw, c_scaled, b_scaled, "lime")

        # Tính khoảng cách chính xác (dùng tọa độ gốc, không scale)
        AC = np.linalg.norm(C - A)
        CB = np.linalg.norm(B - C)
        ratio = AC / CB

        # Hiển thị tỉ lệ với độ chính xác cao
        st.session_state.ketqua.append({
            "A": clicks[0],
            "B": clicks[1],
            "C (tỉ lệ vàng)": (round(C[0]), round(C[1])),
            "AC": round(AC, 4),
            "CB": round(CB, 4),
            "AC/CB": f"{ratio:.12f}",  # Hiện 12 chữ số thập phân
            "So với Φ": f"{abs(ratio - PHI):.12f} ← sai số"
        })

        # Hiển thị thông tin ngay lập tức
        st.write("**Điểm chia tỉ lệ vàng C**:")
        st.write(f"→ Tọa độ: ({round(C[0])}, {round(C[1])})")
        st.write(f"→ **AC/CB = {ratio:.12f}**")
        st.write(f"→ Tỉ lệ vàng chuẩn (φ) = {PHI:.12f}")
        st.write(f"→ **Độ lệch**: {abs(ratio - PHI):.12f}")

    st.image(overlay, use_column_width=True)

    if st.session_state.ketqua:
        st.write("### Lịch sử các phép đo tỉ lệ vàng")
        st.dataframe(st.session_state.ketqua, use_container_width=True)

    if st.button("Xóa hết kết quả"):
        st.session_state.clicks = []
        st.session_state.ketqua = []
        st.rerun()
