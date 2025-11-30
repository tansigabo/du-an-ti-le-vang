import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(page_title="Kiểm tra tỉ lệ vàng", layout="centered")

PHI = (1 + 5**0.5) / 2  # Tỉ lệ vàng chính xác: ≈1.618033988749895
MAX_W = 700
R = 6  # Bán kính điểm

# Khởi tạo session_state
if "clicks" not in st.session_state:
    st.session_state.clicks = []
if "ketqua" not in st.session_state:
    st.session_state.ketqua = []
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def diem(draw, p, color="red"):
    draw.ellipse((p[0]-R, p[1]-R, p[0]+R, p[1]+R), fill=color, outline="white", width=2)

def duong(draw, p1, p2, color="white"):
    draw.line([p1, p2], fill=color, width=3)

# Upload ảnh
file = st.file_uploader("Chọn ảnh (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])

if file:
    # Reset khi đổi ảnh mới
    if st.session_state.last_file != file.name:
        st.session_state.clicks = []
        st.session_state.ketqua = []
        st.session_state.last_file = file.name

    img = Image.open(file).convert("RGB")
    w, h = img.size
    scale = MAX_W / w if w > MAX_W else 1.0
    display_img = img.resize((int(w*scale), int(h*scale))) if scale < 1 else img.copy()

    # Nhận click
    click = streamlit_image_coordinates(display_img, key="img_coord")

    if click:
        x = int(click["x"] / scale)
        y = int(click["y"] / scale)
        point = (x, y)
        if not st.session_state.clicks or st.session_state.clicks[-1] != point:
            st.session_state.clicks.append(point)

    # Vẽ overlay
    overlay = display_img.copy()
    draw = ImageDraw.Draw(overlay)
    clicks = st.session_state.clicks

    # Vẽ điểm A (nếu có)
    if len(clicks) >= 1:
        ax, ay = int(clicks[0][0]*scale), int(clicks[0][1]*scale)
        diem(draw, (ax, ay), "red")
        draw.text((ax + 10, ay - 10), "A", fill="white", font_size=20)

    # Khi có đủ 2 điểm → tính điểm C theo tỉ lệ vàng và lưu kết quả
    if len(clicks) >= 2:
        a = clicks[0]
        b = clicks[1]
        bx, by = int(b[0]*scale), int(b[1]*scale)
        diem(draw, (bx, by), "lime")
        draw.text((bx + 10, by - 10), "B", fill="white", font_size=20)

        # Vẽ đường AB
        duong(draw, (ax, ay), (bx, by), "cyan")

        # Tính điểm C theo tỉ lệ vàng (AC/CB = φ)
        A = np.array(clicks[0], dtype=float)
        B = np.array(clicks[1], dtype=float)
        C = A + (B - A) / PHI  # Công thức chính xác chia theo tỉ lệ vàng

        cx, cy = int(C[0]*scale), int(C[1]*scale)
        diem(draw, (cx, cy), "yellow")
        draw.text((cx + 10, cy - 10), "C (tỉ lệ vàng)", fill="yellow")

        # Tính khoảng cách chính xác
        ac = np.linalg.norm(C - A)
        cb = np.linalg.norm(B - C)
        ratio = ac / cb  # Đây chính là φ, nhưng giữ nguyên float để hiển thị đầy đủ

        # Lưu kết quả với tỉ lệ siêu chính xác
        st.session_state.ketqua.append({
            "A": clicks[0],
            "B": clicks[1],
            "C (tỉ lệ vàng)": (int(C[0]), int(C[1])),
            "AC": round(ac, 6),
            "CB": round(cb, 6),
            "AC/CB": ratio,  # Để nguyên → Streamlit sẽ hiện rất nhiều số
            "φ (chính xác)": PHI,
        })

        # Vẽ đường AC và CB để dễ nhìn
        duong(draw, (ax, ay), (cx, cy), "yellow")
        duong(draw, (cx, cy), (bx, by), "magenta")

        # Xóa clicks để chuẩn bị đo cặp mới
        st.session_state.clicks = []

    # Hiển thị ảnh có đánh dấu
    st.image(overlay, use_column_width=True)

    # Hiển thị bảng kết quả
    if st.session_state.ketqua:
        st.write("### Kết quả đo tỉ lệ vàng (AC/CB = φ)")
        # Dùng st.dataframe để hiển thị float đầy đủ chữ số
        df = st.dataframe(
            st.session_state.ketqua,
            use_container_width=True,
            hide_index=False,
            column_config={
                "AC/CB": st.column_config.NumberColumn(
                    "AC/CB (tỉ lệ vàng)",
                    format="%.12f"  # Hiển thị tới 12 chữ số thập phân
                ),
                "φ (chính xác)": st.column_config.NumberColumn(
                    "φ = (1+√5)/2",
                    format="%.12f"
                )
            }
        )

    # Nút xóa hết
    if st.button("Xóa hết kết quả"):
        st.session_state.ketqua = []
        st.session_state.clicks = []
        st.rerun()

else:
    st.info("Vui lòng tải lên một bức ảnh để bắt đầu đo tỉ lệ vàng")
    st.markdown("""
    ### Cách dùng:
    1. Tải ảnh lên  
    2. Click lần lượt 2 điểm **A** và **B**  
    3. Ứng dụng sẽ tự tính điểm **C** sao cho **AC/CB = tỉ lệ vàng ≈ 1.618033988749895**  
    4. Kết quả sẽ hiện đầy đủ chữ số chính xác  
    """)
