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
    Vẽ đoạn thẳng và các điểm Tỉ lệ vàng lên ảnh, đồng thời hiển thị thông số.
    """
    draw = ImageDraw.Draw(image)
    
    A = np.array(p1)
    B = np.array(p2)
    vec = B - A
    
    # Tính toán tọa độ các điểm C1, C2
    # C1 là điểm chia gần B (tỷ lệ 1/PHI), C2 là điểm chia gần A (tỷ lệ PHI-1)
    C1 = A + vec / PHI
    C2 = A + vec * (PHI - 1)
    
    # Chuyển về tọa độ nguyên (int) cho việc vẽ
    C1_int = tuple(C1.astype(int))
    C2_int = tuple(C2.astype(int))
    A_int = tuple(A.astype(int))
    B_int = tuple(B.astype(int))
    
    # 1. TÍNH TOÁN KHOẢNG CÁCH (PIXEL)
    L_AB = np.linalg.norm(vec) # Chiều dài đoạn AB
    L_AC1 = np.linalg.norm(C1 - A) # Chiều dài đoạn AC1 (Đoạn lớn)
    L_C1B = np.linalg.norm(B - C1) # Chiều dài đoạn C1B (Đoạn nhỏ)
    
    # 2. VẼ ĐƯỜNG VÀ ĐIỂM
    # Vẽ đường nối (Màu trắng mờ)
    draw.line([A_int, B_int], fill="white", width=2)
    
    # Vẽ điểm tỉ lệ vàng (Màu xanh lơ)
    r = 8
    # Điểm C1 (Điểm chia)
    draw.ellipse((C1_int[0]-r, C1_int[1]-r, C1_int[0]+r, C1_int[1]+r), fill="#00ffff", outline="black")
    # Điểm C2 (Điểm còn lại, vẽ nhỏ hơn)
    draw.ellipse((C2_int[0]-5, C2_int[1]-5, C2_int[0]+5, C2_int[1]+5), fill="#00ffff", outline="black")
    
    # Vẽ điểm mốc A, B (Màu đỏ)
    r_dot = 4
    draw.ellipse((A_int[0]-r_dot, A_int[1]-r_dot, A_int[0]+r_dot, A_int[1]+r_dot), fill="red")
    draw.ellipse((B_int[0]-r_dot, B_int[1]-r_dot, B_int[0]+r_dot, B_int[1]+r_dot), fill="red")
    
    # 3. VẼ THÔNG SỐ (TEXT)
    # Sử dụng màu tương phản (vàng, xanh lơ) để dễ đọc trên nền ảnh
    
    # Thông số cho điểm A (START)
    draw.text((A_int[0] + 10, A_int[1] - 20), f"A: ({A_int[0]}, {A_int[1]})", fill="yellow")
    
    # Thông số cho điểm B (END)
    draw.text((B_int[0] + 10, B_int[1] - 20), f"B: ({B_int[0]}, {B_int[1]})", fill="yellow")
    
    # Thông số Chiều dài (Đoạn AB - ở giữa)
    mid_point = ((A_int[0] + B_int[0]) // 2, (A_int[1] + B_int[1]) // 2)
    draw.text((mid_point[0], mid_point[1] - 30), f"L_TOTAL (AB): {L_AB:.1f} px", fill="white")
    
    # Thông số Điểm chia C1 và Chiều dài đoạn Tỉ lệ vàng
    
    # Tọa độ C1
    draw.text((C1_int[0] + 10, C1_int[1] - 20), f"C1: ({C1_int[0]}, {C1_int[1]})", fill="#00ffff")
    
    # Chiều dài AC1 (Đoạn lớn)
    draw.text((C1_int[0] + 10, C1_int[1] + 10), f"AC1 (Lớn): {L_AC1:.1f} px", fill="#00ffff")
    
    # Chiều dài C1B (Đoạn nhỏ)
    draw.text((C1_int[0] + 10, C1_int[1] + 30), f"C1B (Nhỏ): {L_C1B:.1f} px", fill="#00ffff")
    
    return image

# --- Khởi tạo Session State (Lưu trữ trạng thái) ---
if 'clicks' not in st.session_state:
    st.session_state['clicks'] = [] # Lưu trữ TẤT CẢ các điểm click
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
    image = Image.open(uploaded_file).convert("RGB")
    
    # Logic 1: Đảm bảo ảnh luôn hiển thị full (rescale nếu quá lớn)
    display_image = image.copy()
    if display_image.width > MAX_DISPLAY_WIDTH:
        ratio = MAX_DISPLAY_WIDTH / display_image.width
        new_height = int(display_image.height * ratio)
        display_image = display_image.resize((MAX_DISPLAY_WIDTH, new_height))
    
    # 2. Xử lý các điểm đã click
    
    # Logic 2: Vẽ TẤT CẢ các đoạn Tỉ lệ vàng đã đo
    if len(st.session_state['clicks']) >= 2:
        # Lặp qua các cặp điểm (0, 1), (2, 3), (4, 5), ...
        for i in range(0, len(st.session_state['clicks']) // 2 * 2, 2):
            p1 = st.session_state['clicks'][i]
            p2 = st.session_state['clicks'][i+1]
            # CHÚ Ý: Hàm ve_ty_le_vang giờ đây vẽ cả text thông số
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
    # width=None để cho phép Streamlit tự quản lý kích thước trong giới hạn của MAX_DISPLAY_WIDTH đã đặt
    value = streamlit_image_coordinates(display_image, key="click_area", width=MAX_DISPLAY_WIDTH)

    # 4. Lưu điểm click mới
    if value and 'clicks' in st.session_state:
        point = (value['x'], value['y'])
        
        # Kiểm tra điểm click có hợp lệ không (tránh trùng lặp do Streamlit refresh)
        if not st.session_state['clicks'] or point != st.session_state['clicks'][-1]:
            st.session_state['clicks'].append(point)
            st.rerun() # Refresh để cập nhật hình ảnh vẽ mới
