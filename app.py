import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

# --- Cấu hình trang ---
st.set_page_config(page_title="Công cụ Đo Tỉ Lệ Vàng (KHKT)", layout="centered")
st.title("📐 Công cụ Đo Tỉ Lệ Vàng Đa Điểm")
st.write("Tải ảnh lên và **click liên tiếp 2 điểm** để vẽ một đoạn Tỉ lệ vàng. Bạn có thể đo nhiều đoạn liên tục trên cùng một ảnh.")

# --- Hằng số và Hàm tính toán ---
PHI = (1 + 5**0.5) / 2 # Tỉ lệ vàng Phi ≈ 1.618

def ve_ty_le_vang(image, p1, p2):
    """Vẽ đường thẳng, điểm mốc và các điểm Tỉ lệ vàng trên ảnh."""
    draw = ImageDraw.Draw(image)
    
    A = np.array(p1)
    B = np.array(p2)
    vec = B - A
    
    # Tính điểm Tỉ lệ vàng: chia đoạn AB theo tỉ lệ PHI:1
    C1 = A + vec / PHI
    C2 = A + vec * (PHI - 1) # Điểm đối xứng với C1 (C2 chia đoạn BA theo tỉ lệ PHI:1)
    
    # Chuyển về tọa độ nguyên
    C1_int = tuple(C1.astype(int))
    C2_int = tuple(C2.astype(int))
    A_int = tuple(A.astype(int))
    B_int = tuple(B.astype(int))
    
    # Vẽ đường nối (Màu trắng mờ)
    draw.line([A_int, B_int], fill="white", width=2)
    
    # Vẽ điểm tỉ lệ vàng (Màu xanh lơ)
    r = 8
    draw.ellipse((C1_int[0]-r, C1_int[1]-r, C1_int[0]+r, C1_int[1]+r), fill="#00ffff", outline="black")
    draw.ellipse((C2_int[0]-5, C2_int[1]-5, C2_int[0]+5, C2_int[1]+5), fill="#00ffff", outline="black")
    
    # Vẽ điểm mốc (Màu đỏ - P1, P2)
    r_dot = 4
    draw.ellipse((A_int[0]-r_dot, A_int[1]-r_dot, A_int[0]+r_dot, A_int[1]+r_dot), fill="red")
    draw.ellipse((B_int[0]-r_dot, B_int[1]-r_dot, B_int[0]+r_dot, B_int[1]+r_dot), fill="red")
    
    return image

# --- Khởi tạo Session State (Lưu trữ trạng thái) ---
if 'clicks' not in st.session_state:
    st.session_state['clicks'] = [] # Lưu trữ TẤT CẢ các điểm click
if 'uploaded_img_data' not in st.session_state:
    st.session_state['uploaded_img_data'] = None

# --- Upload Ảnh ---
uploaded_file = st.file_uploader("Chọn ảnh của bạn...", type=["jpg", "png", "webp"])

if uploaded_file is not None:
    # 1. Xử lý khi có ảnh mới (reset các điểm click)
    if st.session_state['uploaded_img_data'] != uploaded_file.name:
        st.session_state['clicks'] = []
        st.session_state['uploaded_img_data'] = uploaded_file.name

    # Đọc ảnh gốc
    image = Image.open(uploaded_file).convert("RGB")
    display_image = image.copy()
        
    # 2. Xử lý các điểm đã click
    # Logic 2: Vẽ TẤT CẢ các đoạn Tỉ lệ vàng đã đo (từng cặp 2 điểm)
    if len(st.session_state['clicks']) >= 2:
        # Lặp qua các cặp điểm (0, 1), (2, 3), (4, 5), ...
        for i in range(0, len(st.session_state['clicks']) // 2 * 2, 2):
            p1 = st.session_state['clicks'][i]
            p2 = st.session_state['clicks'][i+1]
            display_image = ve_ty_le_vang(display_image, p1, p2)
            
    # Hiển thị thông báo hướng dẫn
    num_clicks = len(st.session_state['clicks'])
    if num_clicks % 2 == 0:
        st.success(f"Đã đo {num_clicks // 2} đoạn. Hãy Click điểm BẮT ĐẦU cho đoạn tiếp theo.")
    else:
        st.info(f"Đã chọn điểm thứ {num_clicks}. Hãy Click điểm KẾT THÚC.")

    # Nút xóa tất cả các đoạn đã vẽ
    if st.button("Xóa TẤT CẢ các đoạn đã đo"):
        st.session_state['clicks'] = []
        st.rerun()

    # 3. Widget click ảnh và lưu điểm
    # Sử dụng width=None để Streamlit tự động scale ảnh vừa với khung.
    value = streamlit_image_coordinates(display_image, key="click_area")

    # 4. Lưu điểm click mới
    if value and 'clicks' in st.session_state:
        point = (value['x'], value['y'])
        
        # Kiểm tra điểm click có hợp lệ không (tránh trùng lặp do Streamlit refresh)
        if not st.session_state['clicks'] or point != st.session_state['clicks'][-1]:
            st.session_state['clicks'].append(point)
            st.rerun() # Refresh để cập nhật hình ảnh vẽ mới
