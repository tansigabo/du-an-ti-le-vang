import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- Cấu hình trang ---
st.set_page_config(page_title="Công cụ Đo Tỉ Lệ Vàng (KHKT)", layout="centered")
st.title("📐 Công cụ Đo Tỉ Lệ Vàng Đa Điểm")
st.write("Tải ảnh lên và **click liên tiếp 2 điểm** để vẽ một đoạn Tỉ lệ vàng. Bạn có thể đo nhiều đoạn liên tục.")

# --- Hằng số và Hàm tính toán ---
PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700  # Giới hạn chiều rộng ảnh để đảm bảo ảnh không bị tràn

def ve_ty_le_vang_on_image(image, p1_disp, p2_disp):
    """
    Vẽ đoạn Tỉ lệ vàng lên ảnh (toạ độ trên ảnh HIỂN THỊ).
    p1_disp, p2_disp là tuple tọa độ %trên ảnh hiển thị%.
    """
    draw = ImageDraw.Draw(image)
    A = np.array(p1_disp)
    B = np.array(p2_disp)
    vec = B - A
    C1 = A + vec / PHI
    C2 = A + vec * (PHI - 1)

    A_int = tuple(A.astype(int))
    B_int = tuple(B.astype(int))
    C1_int = tuple(C1.astype(int))
    C2_int = tuple(C2.astype(int))

    # Vẽ đoạn nối, điểm tỉ lệ, điểm mốc
    draw.line([A_int, B_int], fill="white", width=2)
    r = 8
    draw.ellipse((C1_int[0]-r, C1_int[1]-r, C1_int[0]+r, C1_int[1]+r), fill="#00ffff", outline="black")
    draw.ellipse((C2_int[0]-5, C2_int[1]-5, C2_int[0]+5, C2_int[1]+5), fill="#00ffff", outline="black")
    r_dot = 4
    draw.ellipse((A_int[0]-r_dot, A_int[1]-r_dot, A_int[0]+r_dot, A_int[1]+r_dot), fill="red")
    draw.ellipse((B_int[0]-r_dot, B_int[1]-r_dot, B_int[0]+r_dot, B_int[1]+r_dot), fill="red")

    return image

# --- Session state ---
if 'clicks' not in st.session_state:
    st.session_state['clicks'] = []  # lưu toạ độ ảnh GỐC (original)
if 'uploaded_img_data' not in st.session_state:
    st.session_state['uploaded_img_data'] = None

# --- Upload Ảnh ---
uploaded_file = st.file_uploader("Chọn ảnh của bạn...", type=["jpg", "png", "webp"])

if uploaded_file is not None:
    # Reset khi đổi ảnh
    if st.session_state['uploaded_img_data'] != uploaded_file.name:
        st.session_state['clicks'] = []
        st.session_state['uploaded_img_data'] = uploaded_file.name

    # Đọc ảnh gốc
    image_orig = Image.open(uploaded_file).convert("RGB")

    # --- Tính tỉ lệ hiển thị ---
    display_image = image_orig.copy()
    display_ratio = 1.0  # display_width / original_width
    scale_factor = 1.0   # original_width / display_width

    if image_orig.width > MAX_DISPLAY_WIDTH:
        display_ratio = MAX_DISPLAY_WIDTH / image_orig.width
        scale_factor = 1.0 / display_ratio
        new_height = int(image_orig.height * display_ratio)
        display_image = display_image.resize((MAX_DISPLAY_WIDTH, new_height))
    else:
        # nếu nhỏ hơn giới hạn, dùng kích thước gốc
        display_ratio = 1.0
        scale_factor = 1.0

    # --- Widget click (truyền đúng kích thước hiển thị) ---
    # sử dụng display_image.width để tránh mismatch giữa kích thước widget và ảnh đã resize
    value = streamlit_image_coordinates(display_image, key="click_area", width=display_image.width)

    # Nếu có click, chuyển về toạ độ gốc và lưu (tránh trùng lặp do refresh)
    if value and 'clicks' in st.session_state:
        x_disp, y_disp = value['x'], value['y']
        x_orig = int(round(x_disp * scale_factor))
        y_orig = int(round(y_disp * scale_factor))
        point_orig = (x_orig, y_orig)
        if (not st.session_state['clicks']) or (point_orig != st.session_state['clicks'][-1]):
            st.session_state['clicks'].append(point_orig)
            # không gọi st.rerun() — ta sẽ hiển thị overlay ngay phía dưới

    # --- Chuẩn bị ảnh overlay để hiển thị các điểm / đoạn đã chọn (trên ảnh hiển thị) ---
    overlay = display_image.copy()
    draw = ImageDraw.Draw(overlay)
    # (tuỳ chọn font, dùng font mặc định an toàn)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Vẽ tất cả các đoạn lưu trong session_state
    n_clicks = len(st.session_state['clicks'])
    for i in range(0, (n_clicks // 2) * 2, 2):
        p1_orig = np.array(st.session_state['clicks'][i])
        p2_orig = np.array(st.session_state['clicks'][i+1])
        p1_disp = tuple((p1_orig * display_ratio).astype(int))
        p2_disp = tuple((p2_orig * display_ratio).astype(int))
        overlay = ve_ty_le_vang_on_image(overlay, p1_disp, p2_disp)

        # ghi thêm thông số (ví dụ độ dài đoạn AB theo px gốc)
        AB_len = np.linalg.norm(p2_orig - p1_orig)
        text = f"AB={int(round(AB_len))} px"
        # vẽ text gần trung điểm
        mid = ((p1_disp[0]+p2_disp[0])//2, (p1_disp[1]+p2_disp[1])//2)
        draw.text((mid[0]+6, mid[1]-6), text, fill="white", font=font)

    # Nếu có một điểm lẻ (đã click điểm bắt đầu nhưng chưa click kết thúc), vẽ marker + thông số
    if n_clicks % 2 == 1:
        last_orig = np.array(st.session_state['clicks'][-1])
        last_disp = tuple((last_orig * display_ratio).astype(int))
        r_dot = 5
        draw.ellipse((last_disp[0]-r_dot, last_disp[1]-r_dot, last_disp[0]+r_dot, last_disp[1]+r_dot), fill="orange")
        # hiển thị toạ độ ngay bên cạnh marker
        txt = f"orig: {tuple(last_orig)}\ndisp: {last_disp}"
        draw.text((last_disp[0]+8, last_disp[1]-8), txt, fill="white", font=font)

    # Hiển thị overlay ngay bên dưới (người dùng sẽ thấy annoted image ngay sau khi click)
    st.image(overlay, caption="Ảnh đã ghi chú (marker / đoạn Tỉ lệ vàng / thông số)", use_column_width=True)

    # Thông báo trạng thái
    if n_clicks % 2 == 0:
        st.success(f"Đã đo {n_clicks // 2} đoạn. Click điểm BẮT ĐẦU cho đoạn tiếp theo.")
    else:
        st.info(f"Đã chọn điểm thứ {n_clicks}. Click điểm KẾT THÚC để hoàn thành đoạn.")

    # Nút xóa tất cả
    if st.button("Xóa TẤT CẢ các đoạn đã đo"):
        st.session_state['clicks'] = []
        st.experimental_rerun()
