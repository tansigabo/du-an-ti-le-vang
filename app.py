import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# --- Cấu hình trang ---
st.set_page_config(page_title="Công cụ Đo Tỉ Lệ Vàng (KHKT)", layout="centered")
st.title("📐 Công cụ Đo Tỉ Lệ Vàng Đa Điểm")
st.write("Tải ảnh lên và **click liên tiếp 2 điểm** để vẽ một đoạn Tỉ lệ vàng. Bạn có thể đo nhiều đoạn liên tục.")

# --- Hằng số và Hàm tính toán ---
PHI = (1 + 5**0.5) / 2 # Hằng số Tỉ lệ vàng (~1.61803)
MAX_DISPLAY_WIDTH = 700 # Giới hạn chiều rộng ảnh để đảm bảo ảnh không bị tràn

# Cố gắng load font mặc định cơ bản nhất (bitmap font) để tránh lỗi phông chữ.
# KHÔNG cố gắng load font hệ thống (như arial) để đảm bảo tính tương thích tuyệt đối.
font_basic = ImageFont.load_default()
font_size = 14 # Giữ kích thước font nhỏ để dễ đọc

def ve_ty_le_vang(image, p1, p2):
    """
    Vẽ đoạn thẳng và các điểm Tỉ lệ vàng lên ảnh, đồng thời hiển thị các thông số số học.
    - p1 = Điểm A (Đầu mút, điểm bắt đầu)
    - p2 = Điểm C (Đầu mút, điểm kết thúc)
    - B = Điểm Tỉ lệ vàng chia đoạn AC sao cho BC/AB = PHI (Đoạn BC lớn hơn AB)
    """
    draw = ImageDraw.Draw(image)
    
    A = np.array(p1)
    C = np.array(p2)
    vec = C - A # Vector AC
    
    # Tính toán tọa độ điểm B (Điểm Tỉ lệ vàng)
    B = A + vec / PHI 
    
    # Chuyển về tọa độ nguyên (int) cho việc vẽ
    B_int = tuple(B.astype(int))
    A_int = tuple(A.astype(int))
    C_int = tuple(C.astype(int))
    
    # 1. TÍNH TOÁN KHOẢNG CÁCH (PIXEL)
    L_BC = np.linalg.norm(C - B) # Chiều dài đoạn Lớn (từ B đến C)
    L_AB = np.linalg.norm(B - A) # Chiều dài đoạn Nhỏ (từ A đến B)
    
    ratio = L_BC / L_AB if L_AB != 0 else 0
    
    # Tính sai số phần trăm so với PHI chuẩn
    error_percent = abs((ratio - PHI) / PHI) * 100 if PHI != 0 else 0
    
    # 2. VẼ ĐƯỜNG VÀ ĐIỂM
    
    # Vẽ đường nối (Màu trắng mờ)
    draw.line([A_int, C_int], fill="white", width=2)
    
    # Bán kính điểm
    r_main = 8 # Bán kính cho điểm B (Tỉ lệ vàng)
    r_dot = 4 # Bán kính cho điểm A, C (Đầu mút)

    # Vẽ điểm tỉ lệ vàng B (Màu xanh lơ)
    draw.ellipse((B_int[0]-r_main, B_int[1]-r_main, B_int[0]+r_main, B_int[1]+r_main), fill="#00ffff", outline="black")
    
    # Vẽ điểm mốc A, C (Màu đỏ)
    draw.ellipse((A_int[0]-r_dot, A_int[1]-r_dot, A_int[0]+r_dot, A_int[1]+r_dot), fill="red")
    draw.ellipse((C_int[0]-r_dot, C_int[1]-r_dot, C_int[0]+r_dot, C_int[1]+r_dot), fill="red")
    
    # 3. VẼ THÔNG SỐ (CHỈ CÓ SỐ VÀ KÝ HIỆU CƠ BẢN)
    
    # Vị trí hiển thị thông số, điều chỉnh để không che điểm B
    text_x = B_int[0] + 15
    text_y = B_int[1] - 40 
    
    # Nhãn điểm A, C, B (Giữ lại để người dùng phân biệt)
    draw.text((A_int[0] - 25, A_int[1] - 25), "A", fill="yellow", font=font_basic)
    draw.text((C_int[0] + 10, C_int[1] - 25), "C", fill="yellow", font=font_basic)
    draw.text((B_int[0] + 10, B_int[1] - 25), "B (GR)", fill="#00ffff", font=font_basic) # GR = Golden Ratio

    # Hiển thị Tỉ lệ vàng (R = Ratio)
    # R: 1.62
    draw.text((text_x, text_y), 
              f"R: {ratio:.2f}", 
              fill="white", font=font_basic) 
    
    # Hiển thị Sai số (Error)
    # E: 1.5%
    draw.text((text_x, text_y + 20), 
              f"E: {error_percent:.1f}%", 
              fill="red" if error_percent > 5 else "#00ff00", font=font_basic)
    
    # Hiển thị độ dài đoạn Lớn (L = Large)
    # L: 125 px
    draw.text((text_x, text_y + 40), 
              f"L: {L_BC:.0f} px", 
              fill="#cccccc", font=font_basic)
    
    # Hiển thị độ dài đoạn Nhỏ (S = Small)
    # S: 77 px
    draw.text((text_x, text_y + 60), 
              f"S: {L_AB:.0f} px", 
              fill="#cccccc", font=font_basic)
    
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
        ratio_scale = MAX_DISPLAY_WIDTH / display_image.width
        new_height = int(display_image.height * ratio_scale)
        display_image = display_image.resize((MAX_DISPLAY_WIDTH, new_height))
    
    # 2. Xử lý các điểm đã click
    
    # Logic 2: Vẽ TẤT CẢ các đoạn Tỉ lệ vàng đã đo
    if len(st.session_state['clicks']) >= 2:
        # Lặp qua các cặp điểm (0, 1), (2, 3), (4, 5), ...
        for i in range(0, len(st.session_state['clicks']) // 2 * 2, 2):
            p1 = st.session_state['clicks'][i]
            p2 = st.session_state['clicks'][i+1]
            display_image = ve_ty_le_vang(display_image, p1, p2)
            
    # Hiển thị thông báo hướng dẫn (vẫn cần tiếng Việt)
    num_clicks = len(st.session_state['clicks'])
    if num_clicks % 2 == 0:
        st.success(f"Đã đo {num_clicks // 2} đoạn. Hãy Click điểm BẮT ĐẦU (A) cho đoạn tiếp theo.")
    else:
        st.info(f"Đã chọn điểm thứ {num_clicks}. Hãy Click điểm KẾT THÚC (C).")

    # Nút xóa tất cả các đoạn đã vẽ
    if st.button("Xóa TẤT CẢ các đoạn đã đo"):
        st.session_state['clicks'] = []
        st.rerun()

    # 3. Widget click ảnh và lưu điểm
    value = streamlit_image_coordinates(display_image, key="click_area", width=MAX_DISPLAY_WIDTH)

    # 4. Lưu điểm click mới
    if value and 'clicks' in st.session_state:
        point = (value['x'], value['y'])
        
        # Kiểm tra điểm click có hợp lệ không (tránh trùng lặp do Streamlit refresh)
        if not st.session_state['clicks'] or point != st.session_state['clicks'][-1]:
            st.session_state['clicks'].append(point)
            st.rerun() # Refresh để cập nhật hình ảnh vẽ mới
