import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

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
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
        border-color: #1D4ED8;
    }
    div.stSpinner > div {
        text-align: center;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("<div style='font-size: 40px; text-align: center;'>🐮</div>", unsafe_allow_html=True)
with col2:
    st.title("Bò Sữa - Soi Bệnh Ads")

st.info("Chuyên trị Ads đắt - Soi từ Content đến Số liệu")

# --- XỬ LÝ API KEY TỪ SECRETS (BẢO MẬT) ---
api_key = None
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    with st.expander("⚠️ Chưa cấu hình Key (Bấm vào để nhập thủ công)"):
        api_key = st.text_input("Nhập Gemini API Key:", type="password")

# --- HÀM PHÂN TÍCH ---
def analyze(prompt, image_data=None):
    if not api_key:
        return "⚠️ Bác chưa nhập API Key hoặc chưa cấu hình Secrets trong Streamlit!"
    
    try:
        genai.configure(api_key=api_key)
        
        # Cấu hình Model: Ưu tiên Flash, nếu lỗi thì thử Pro
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_instruction = """
        Bạn là "Bò Sữa Marketing" - chuyên gia Facebook Ads thực chiến.
        Phong cách: Gần gũi, thẳng thắn, dùng ẩn dụ 'chăn nuôi', tập trung số liệu.
        Cấu trúc trả lời bắt buộc:
        1. 🐮 CHẨN ĐOÁN (Nhận xét nhanh về tình trạng)
        2. 🔍 NGUYÊN NHÂN (Tại sao lại bị như thế: Do content, do target hay do kỹ thuật)
        3. 💊 ĐƠN THUỐC (Hành động cụ thể cần làm ngay)
        """
        
        full_prompt = system_instruction + "\n\n" + prompt
        
        with st.spinner('🐮 Bò đang nhai lại dữ liệu... Chờ tí nhé!'):
            # Thêm cấu hình an toàn cho việc tạo nội dung
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
            )
            
            if image_data:
                response = model.generate_content([full_prompt, image_data], generation_config=generation_config)
            else:
                response = model.generate_content(full_prompt, generation_config=generation_config)
            return response.text

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
             return f"❌ **Lỗi phiên bản:** Bác cần cập nhật file `requirements.txt` trên GitHub thành `google-generativeai>=0.8.0` rồi Reboot app nhé!"
        return f"❌ Lỗi rồi bác ơi: {error_msg}"

# --- GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["📸 Soi Creative (Ảnh)", "📊 Soi Số Liệu (Data)"])

with tab1:
    st.write("Tải ảnh quảng cáo (Banner/Video frame) lên để Bò nhận xét độ thu hút.")
    uploaded_file = st.file_uploader("Chọn ảnh từ máy tính", type=['png', 'jpg', 'jpeg'], key="upload_creative")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Ảnh quảng cáo cần soi', use_column_width=True)
        
        if st.button("🐮 BẮT MẠCH ẢNH NÀY", key="btn_img"):
            result = analyze("Hãy phân tích hình ảnh quảng cáo này. Hook (3 giây đầu) có tốt không? Text trên ảnh có bị nhiều quá không? Màu sắc và bố cục có điểm gì sai? Đưa ra lời khuyên tối ưu.", image)
            if "❌" not in result:
                st.success("Đã có kết quả khám bệnh!")
            st.markdown("---")
            st.markdown(result)

with tab2:
    st.write("Tải ảnh chụp báo cáo Ads hoặc nhập số liệu để Bò tìm nguyên nhân đắt.")
    data_file = st.file_uploader("Tải ảnh chụp màn hình báo cáo / File CSV", type=['png', 'jpg', 'csv', 'txt'], key="upload_data")
    data_text = st.text_area("Hoặc nhập bối cảnh/số liệu vào đây:", height=150, placeholder="Ví dụ: Chạy thời trang, Ngân sách 500k/ngày. CPM 80k, CTR 1.5% nhưng không chốt được đơn. Giá Mess đang là 30k...")
    
    if st.button("🐮 BẮT MẠCH SỐ LIỆU", key="btn_data"):
        if not data_file and not data_text:
            st.warning("Bác phải cho Bò ăn 'Cỏ' (Dữ liệu) thì mới có sữa chứ! Tải ảnh hoặc nhập chữ đi.")
        else:
            prompt = f"Phân tích dữ liệu quảng cáo sau theo phong cách Bò Sữa. Bối cảnh người dùng cung cấp: {data_text}"
            img_input = None
            
            if data_file:
                if data_file.type.startswith('image'):
                    img_input = Image.open(data_file)
                    prompt += " (Hãy đọc kỹ các con số trong hình ảnh báo cáo đính kèm để phân tích)."
                else:
                    # Đọc file text/csv
                    stringio = io.StringIO(data_file.getvalue().decode("utf-8"))
                    file_content = stringio.read()
                    prompt += f"\n\nDữ liệu từ file đính kèm:\n{file_content}"
            
            result = analyze(prompt, img_input)
            if "❌" not in result:
                st.success("Đã có kết quả khám bệnh!")
            st.markdown("---")
            st.markdown(result)

# --- FOOTER ---
st.markdown("---")
st.caption("Developed by Bò Sữa Marketing | Powered by Gemini AI")
