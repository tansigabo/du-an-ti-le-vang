import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np

# --- Cấu hình trang ---
st.set_page_config(page_title="Công cụ Đo Tỉ Lệ Vàng (KHKT)", layout="centered")
st.title("📐 Công cụ Đo Tỉ Lệ Vàng Đa Điểm")
st.write("Tải ảnh lên và **click liên tiếp 2 điểm** để vẽ một đoạn Tỉ lệ vàng. Bạn có thể đo nhiều đoạn liên tục.")

# --- Hằng số và Hàm tính toán ---
PHI = (1 + 5**0.5) / 2
MAX_DISPLAY_WIDTH = 700 # Giới hạn chiều rộng ảnh để đảm bảo ảnh không bị tràn

def ve_ty_le_vang(image, p1, p2):
    """
    Vẽ đoạn Tỉ lệ vàng lên ảnh.
    p1, p2 phải là tọa độ tương ứng với kích thước của 'image'.
    """
    draw = ImageDraw.Draw(image)
    
    A = np.array(p1)
    B = np.array(p2)
    vec = B - A
    
    # Tính điểm C1, C2
    C1 = A + vec / PHI
    C2 = A + vec * (PHI - 1)
    
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
    # Vẽ điểm mốc (Màu đỏ)
    r_dot = 4
    draw.ellipse((A_int[0]-r_dot, A_int[1]-r_dot, A_int[0]+r_dot, A_int[1]+r_dot), fill="red")
    draw.ellipse((B_int[0]-r_dot, B_int[1]-r_dot, B_int[0]+r_dot, B_int[1]+r_dot), fill="red")
    
    return image

# --- Khởi tạo Session State (Lưu trữ trạng thái) ---
if 'clicks' not in st.session_state:
    st.session_state['clicks'] = [] # Lưu trữ TẤT CẢ các điểm click (Tọa độ ảnh GỐC)
if 'uploaded_img_data' not in st.session_state:
    st.session_state['uploaded_img_data'] = None

# --- Upload Ảnh ---
uploaded_file = st.file_uploader("Chọn ảnh của bạn...", type=["jpg", "png", "webp"])

if uploaded_file is not None:
    # 1. Xử lý khi có ảnh mới
    if st.session_state['uploaded_img_data'] != uploaded_file.name:
        st.session_state['clicks'] = []
        st.session_state['uploaded_img_data'] = uploaded_file.name

    # Đọc ảnh gốc
    image_orig = Image.open(uploaded_file).convert("RGB")
    
    # --- Bắt đầu tính toán Tỉ lệ hiển thị (Display Ratio) ---
    display_image = image_orig.copy()
    display_ratio = 1.0 # Tỉ lệ thu nhỏ (display_width / original_width)
    scale_factor = 1.0  # Tỉ lệ phóng to (original_width / display_width)

    # Logic 1: Đảm bảo ảnh luôn hiển thị full (rescale nếu quá lớn)
    if image_orig.width > MAX_DISPLAY_WIDTH:
        display_ratio = MAX_DISPLAY_WIDTH / image_orig.width
        scale_factor = image_orig.width / MAX_DISPLAY_WIDTH # Tỉ lệ để chuyển từ tọa độ hiển thị -> tọa độ gốc
        new_height = int(image_orig.height * display_ratio)
        display_image = display_image.resize((MAX_DISPLAY_WIDTH, new_height))
    # --- Kết thúc tính toán Tỉ lệ hiển thị ---
    
    # 2. Xử lý các điểm đã click
    
    # Logic 2: Vẽ TẤT CẢ các đoạn Tỉ lệ vàng đã đo
    if len(st.session_state['clicks']) >= 2:
        # Lặp qua các cặp điểm (0, 1), (2, 3), (4, 5), ...
        for i in range(0, len(st.session_state['clicks']) // 2 * 2, 2):
            # p1_orig và p2_orig là tọa độ ảnh GỐC đã lưu
            p1_orig = np.array(st.session_state['clicks'][i])
            p2_orig = np.array(st.session_state['clicks'][i+1])
            
            # Chuyển đổi tọa độ GỐC sang tọa độ HIỂN THỊ để vẽ lên display_image
            p1_disp = tuple((p1_orig * display_ratio).astype(int))
            p2_disp = tuple((p2_orig * display_ratio).astype(int))

            # Vẽ trên ảnh hiển thị
            display_image = ve_ty_le_vang(display_image, p1_disp, p2_disp)
            
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
    # width=None để cho phép Streamlit tự quản lý kích thước trong giới hạn của MAX_DISPLAY_WIDTH đã đặt
    # Chúng ta truyền display_image (có thể đã được resize) vào đây
    value = streamlit_image_coordinates(display_image, key="click_area", width=MAX_DISPLAY_WIDTH)

    # 4. Lưu điểm click mới (đã sửa lỗi)
    if value and 'clicks' in st.session_state:
        # Tọa độ thu được là tọa độ trên ảnh hiển thị (display_image)
        x_disp, y_disp = value['x'], value['y']
        
        # CHUYỂN ĐỔI TỌA ĐỘ HIỂN THỊ SANG TỌA ĐỘ GỐC
        x_orig = int(x_disp * scale_factor)
        y_orig = int(y_disp * scale_factor)
        point_orig = (x_orig, y_orig)
        
        # Kiểm tra điểm click có hợp lệ không (tránh trùng lặp do Streamlit refresh)
        if not st.session_state['clicks'] or point_orig != st.session_state['clicks'][-1]:
            st.session_state['clicks'].append(point_orig)
            st.rerun() # Refresh để cập nhật hình ảnh vẽ mới
