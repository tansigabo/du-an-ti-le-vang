import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import numpy as np
import io

# Cấu hình trang web
st.set_page_config(page_title="Công cụ Đo Tỉ Lệ Vàng (KHKT)", layout="centered")
st.title("📐 Công cụ Đo Tỉ Lệ Vàng (Fibonacci)")
st.write("Tải ảnh lên và click 2 điểm để xem vị trí tỉ lệ vàng.")

# Hàm vẽ tỉ lệ vàng
def ve_ty_le_vang(image, p1, p2):
    draw = ImageDraw.Draw(image)
    PHI = (1 + 5**0.5) / 2
    
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
    
    # Vẽ đường nối
    draw.line([A_int, B_int], fill="white", width=2)
    
    # Vẽ điểm tỉ lệ vàng (Màu xanh lơ)
    r = 8
    draw.ellipse((C1_int[0]-r, C1_int[1]-r, C1_int[0]+r, C1_int[1]+r), fill="#00ffff", outline="black")
    draw.ellipse((C2_int[0]-5, C2_int[1]-5, C2_int[0]+5, C2_int[1]+5), fill="#00ffff", outline="black")
    # Vẽ điểm mốc (Màu đỏ)
    draw.ellipse((A_int[0]-4, A_int[1]-4, A_int[0]+4, A_int[1]+4), fill="red")
    draw.ellipse((B_int[0]-4, B_int[1]-4, B_int[0]+4, B_int[1]+4), fill="red")
    
    return image

# Quản lý trạng thái click
if 'points' not in st.session_state:
    st.session_state['points'] = []

# Nút upload ảnh
uploaded_file = st.file_uploader("Chọn ảnh của bạn...", type=["jpg", "png", "webp"])

if uploaded_file is not None:
    # Reset điểm nếu người dùng upload ảnh mới
    if 'last_file' not in st.session_state or st.session_state['last_file'] != uploaded_file.name:
        st.session_state['points'] = []
        st.session_state['last_file'] = uploaded_file.name
        
    image = Image.open(uploaded_file).convert("RGB")
    
    # Nếu chưa đủ 2 điểm -> Cho click
    if len(st.session_state['points']) < 2:
        st.info(f"Đã chọn {len(st.session_state['points'])} điểm. Hãy click tiếp vào ảnh.")
        value = streamlit_image_coordinates(image, key=uploaded_file.name + str(len(st.session_state['points']))) # Key phải động
        
        if value:
            point = (value['x'], value['y'])
            # Chỉ thêm điểm nếu không bị trùng do Streamlit rerun
            if not st.session_state['points'] or abs(st.session_state['points'][-1][0] - point[0]) > 5 or abs(st.session_state['points'][-1][1] - point[1]) > 5:
                 st.session_state['points'].append(point)
                 st.rerun()
                
    # Nếu đã đủ 2 điểm -> Vẽ kết quả
    else:
        result = image.copy()
        ve_ty_le_vang(result, st.session_state['points'][0], st.session_state['points'][1])
        st.image(result, caption="Kết quả Tỉ lệ vàng đã được vẽ")
        
        if st.button("Đo lại (Xóa điểm)"):
            st.session_state['points'] = []
            st.rerun()
