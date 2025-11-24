import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Bò Sữa Audit",
    page_icon="🐮",
    layout="centered"
)

# --- CSS TÙY CHỈNH CHO ĐẸP ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🐮 Bò Sữa - Máy Soi Bệnh Ads")
st.info("Chuyên trị Ads đắt - Soi từ Content đến Số liệu")

# --- XỬ LÝ API KEY TỪ SECRETS (BẢO MẬT) ---
# Khi chạy trên web thật, key sẽ được lấy từ hệ thống bảo mật của Streamlit
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    # Fallback cho lúc chạy thử (hoặc bác nhập tay)
    api_key = st.text_input("Nhập Gemini API Key (nếu chưa cấu hình):", type="password")

# --- HÀM PHÂN TÍCH ---
def analyze(prompt, image_data=None):
    if not api_key:
        return "⚠️ Bác chưa nhập API Key hoặc chưa cấu hình Secrets!"
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_instruction = """
    Bạn là "Bò Sữa Marketing" - chuyên gia Facebook Ads thực chiến.
    Phong cách: Gần gũi, thẳng thắn, dùng ẩn dụ 'chăn nuôi', tập trung số liệu.
    Cấu trúc: [Chẩn đoán] -> [Nguyên nhân] -> [Giải pháp hành động].
    """
    
    full_prompt = system_instruction + "\n\n" + prompt
    
    try:
        with st.spinner('🐮 Bò đang nhai lại dữ liệu...'):
            if image_data:
                response = model.generate_content([full_prompt, image_data])
            else:
                response = model.generate_content(full_prompt)
            return response.text
    except Exception as e:
        return f"❌ Lỗi rồi: {str(e)}"

# --- GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["📸 Soi Creative (Ảnh)", "📊 Soi Số Liệu (Data)"])

with tab1:
    uploaded_file = st.file_uploader("Tải ảnh quảng cáo lên đây", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Ảnh quảng cáo cần soi', use_column_width=True)
        
        if st.button("BẮT MẠCH ẢNH NÀY", key="btn_img"):
            result = analyze("Hãy phân tích hình ảnh quảng cáo này. Hook có tốt không? Text có bị nhiều quá không? Đưa ra lời khuyên tối ưu.", image)
            st.markdown("---")
            st.markdown(result)

with tab2:
    data_file = st.file_uploader("Tải ảnh báo cáo / File CSV", type=['png', 'jpg', 'csv', 'txt'])
    data_text = st.text_area("Hoặc nhập bối cảnh/số liệu vào đây:", height=150, placeholder="Ví dụ: Ngân sách 500k, CPM 80k, ra 10 mess nhưng ko chốt được...")
    
    if st.button("BẮT MẠCH SỐ LIỆU", key="btn_data"):
        prompt = f"Phân tích dữ liệu quảng cáo sau. Bối cảnh: {data_text}"
        img_input = None
        
        if data_file:
            if data_file.type.startswith('image'):
                img_input = Image.open(data_file)
                prompt += " (Phân tích dựa trên hình ảnh báo cáo đính kèm)"
            else:
                # Đọc file text/csv
                stringio = io.StringIO(data_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                prompt += f"\n\nDữ liệu file: {file_content}"
        
        result = analyze(prompt, img_input)
        st.markdown("---")
        st.markdown(result)

# --- FOOTER ---
st.markdown("---")
st.caption("Developed by Bò Sữa Marketing")
