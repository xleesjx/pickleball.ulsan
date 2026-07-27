import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page configuration for Mobile Optimization
st.set_page_config(
    page_title="클럽 회원 인증",
    page_icon="🎫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Mobile Friendly UI
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.6rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .card-title {
        color: #2e7d32;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.3rem 0;
        border-bottom: 1px solid #eee;
    }
    .info-label {
        color: #666;
        font-weight: 500;
    }
    .info-value {
        color: #333;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to read data safely
@st.cache_data(ttl=60)
def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

# Main App Header
st.title("🎫 회원 인증 서비스")
st.caption("협약기관 이용을 위한 회원 인증 페이지입니다.")

try:
    # Load '설정' sheet for institutional list
    config_df = load_data("설정")
    # Assuming institutional names are in the first column of '설정' sheet
    facility_list = config_df.iloc[:, 0].dropna().tolist()
    if not facility_list:
        facility_list = ["기본 협약기관"]
except Exception:
    facility_list = ["참바른병원"]  # Fallback option if setup sheet is missing

# Input Form
with st.form("auth_form", clear_on_submit=False):
    selected_facility = st.selectbox("🏥 이용할 기관 선택", facility_list)
    
    user_name = st.text_input("👤 이름", placeholder="홍길동").strip()
    
    birth_input = st.text_input("📅 생년월일 (6자리)", placeholder="예: 980101", max_chars=6).strip()
    
    phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="예: 1234", max_chars=4).strip()
    
    submit_button = st.form_submit_button("회원 인증 조회")

# Logic Execution on Submit
if submit_button:
    # 2. Validation Checks
    if not user_name:
        st.warning("이름을 입력해주세요.")
    elif not birth_input.isdigit() or len(birth_input) != 6:
        st.error("생년월일은 6자리 숫자로 정확히 입력해주세요. (예: 980101)")
    elif not phone_last4.isdigit() or len(phone_last4) != 4:
        st.error("전화번호 뒷자리는 4자리 숫자로 정확히 입력해주세요. (예: 1234)")
    else:
        with st.spinner("회원 정보를 조회하는 중입니다..."):
            try:
                # Load '통합관리' sheet
                members_df = load_data("통합관리")
                
                # Normalize Data for precise comparison
                members_df['이름_clean'] = members_df['이름'].astype(str).str.strip()
                members_df['생년월일_clean'] = members_df['생년월일'].astype(str).str.strip()
                
                # Extract last 4 digits from phone number column
                members_df['연락처_뒷자리'] = members_df['연락처'].astype(str).str.replace('-', '').str.strip().str[-4:]

                # Filter condition (Name, Birthdate, Phone Last 4 Digits)
                matched = members_df[
                    (members_df['이름_clean'] == user_name) &
                    (members_df['생년월일_clean'] == birth_input) &
                    (members_df['연락처_뒷자리'] == phone_last4)
                ]

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 3. Handle Matched Result
                if not matched.empty:
                    # Multi-club handling (Duplicate registration)
                    clubs = matched['소속 클럽'].dropna().unique().tolist()
                    matched_clubs_str = ", ".join(clubs)
                    
                    first_row = matched.iloc[0]
                    member_status = first_row.get('회원상태', '정회원')
                    join_date = first_row.get('가입일', '-')
                    full_phone = first_row.get('연락처', f"010-****-{phone_last4}")

                    # Display UI Success Card
                    st.success("✅ 회원 인증이 완료되었습니다!")
                    
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">인증 회원 정보</div>
                        <div class="info-row"><span class="info-label">이용기관</span><span class="info-value">{selected_facility}</span></div>
                        <div class="info-row"><span class="info-label">이름</span><span class="info-value">{user_name}</span></div>
                        <div class="info-row"><span class="info-label">소속 클럽</span><span class="info-value">{matched_clubs_str}</span></div>
                        <div class="info-row"><span class="info-label">생년월일</span><span class="info-value">{birth_input}</span></div>
                        <div class="info-row"><span class="info-label">연락처</span><span class="info-value">{full_phone}</span></div>
                        <div class="info-row"><span class="info-label">회원상태</span><span class="info-value">{member_status}</span></div>
                        <div class="info-row"><span class="info-label">가입일</span><span class="info-value">{join_date}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Log to '이용기록' Sheet
                    log_entry = pd.DataFrame([{
                        "조회일시": current_time,
                        "입력이름": user_name,
                        "입력생년월일": birth_input,
                        "입력전화번호뒷자": phone_last4,
                        "결과": "성공",
                        "매칭클럽": matched_clubs_str,
                        "이용기관": selected_facility
                    }])
                    
                    # Append log to Google Sheet
                    conn.append(worksheet="이용기록", data=log_entry)

                else:
                    # Failed Match
                    st.error("❌ 일치하는 회원 정보가 없습니다. 입력 정보를 다시 확인하시거나 관리자에게 문의하세요.")
                    
                    # Log failure to '이용기록' Sheet
                    log_entry = pd.DataFrame([{
                        "조회일시": current_time,
                        "입력이름": user_name,
                        "입력생년월일": birth_input,
                        "입력전화번호뒷자": phone_last4,
                        "결과": "실패",
                        "매칭클럽": "-",
                        "이용기관": selected_facility
                    }])
                    conn.append(worksheet="이용기록", data=log_entry)

            except Exception as e:
                st.error("데이터를 불러오는 중 오류가 발생했습니다. 구글 시트 연결 설정을 확인해주세요.")
                # st.write(e) # Uncomment for debugging
