import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="클럽 회원 인증",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Modern UI & Hiding Streamlit Branding
st.markdown("""
<style>
    /* Streamlit 브랜드 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 기본 배경 및 여백 설정 */
    .stApp {
        background-color: #f4f6f9;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }

    /* 입력 폼 및 카드 컨테이너 스타일 */
    .custom-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }

    /* 성공 결과 전용 카드 */
    .success-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
        border: 2px solid #22c55e;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(34, 197, 94, 0.15);
        text-align: center;
    }

    .status-badge {
        display: inline-block;
        background-color: #22c55e;
        color: white;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 6px 16px;
        border-radius: 20px;
        margin-bottom: 12px;
    }

    .user-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 4px;
    }

    .facility-name {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 12px;
    }

    /* 정보 테이블 레이아웃 */
    .info-grid {
        text-align: left;
        margin-top: 15px;
    }
    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px dashed #e2e8f0;
    }
    .info-item:last-child {
        border-bottom: none;
    }
    .info-label {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .info-value {
        color: #0f172a;
        font-size: 1rem;
        font-weight: 700;
    }

    /* 버튼 스타일 개편 */
    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.75rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

# 세션 상태 초기화 (페이지 전환용)
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'auth_result' not in st.session_state:
    st.session_state.auth_result = None

# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면
# ----------------------------------------------------
if st.session_state.page == 'input':
    st.markdown("<h2 style='text-align: center; color: #1e293b; font-weight: 800; margin-bottom: 4px;'>클럽 회원 인증</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-bottom: 24px;'>협약기관 이용을 위한 본인 확인 서비스</p>", unsafe_allow_html=True)

    try:
        config_df = load_data("설정")
        facility_list = config_df.iloc[:, 0].dropna().tolist()
        if not facility_list:
            facility_list = ["참바른병원"]
    except Exception:
        facility_list = ["참바른병원"]

    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        selected_facility = st.selectbox("🏥 이용할 협약기관", facility_list)
        user_name = st.text_input("👤 이름", placeholder="홍길동").strip()
        birth_input = st.text_input("📅 생년월일 (6자리)", placeholder="예: 980101", max_chars=6).strip()
        phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="예: 1234", max_chars=4).strip()
        
        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        submit_button = st.button("회원 인증 조회")
        st.markdown('</div>', unsafe_allow_html=True)

    if submit_button:
        if not user_name:
            st.warning("이름을 입력해주세요.")
        elif not birth_input.isdigit() or len(birth_input) != 6:
            st.error("생년월일은 6자리 숫자로 입력해주세요.")
        elif not phone_last4.isdigit() or len(phone_last4) != 4:
            st.error("전화번호 뒷자리는 4자리 숫자로 입력해주세요.")
        else:
            with st.spinner("회원 정보를 확인하고 있습니다..."):
                try:
                    members_df = load_data("통합관리")
                    
                    members_df['이름_clean'] = members_df['이름'].astype(str).str.strip()
                    members_df['생년월일_clean'] = members_df['생년월일'].astype(str).str.strip()
                    members_df['연락처_뒷자리'] = members_df['연락처'].astype(str).str.replace('-', '').str.strip().str[-4:]

                    matched = members_df[
                        (members_df['이름_clean'] == user_name) &
                        (members_df['생년월일_clean'] == birth_input) &
                        (members_df['연락처_뒷자리'] == phone_last4)
                    ]

                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if not matched.empty:
                        clubs = matched['소속 클럽'].dropna().unique().tolist()
                        matched_clubs_str = ", ".join(clubs)
                        
                        first_row = matched.iloc[0]
                        member_status = first_row.get('회원상태', '정회원')
                        join_date = first_row.get('가입일', '-')
                        full_phone = first_row.get('연락처', f"010-****-{phone_last4}")

                        # 로그 기록
                        log_entry = pd.DataFrame([{
                            "조회일시": current_time,
                            "입력이름": user_name,
                            "입력생년월일": birth_input,
                            "입력전화번호뒷자": phone_last4,
                            "결과": "성공",
                            "매칭클럽": matched_clubs_str,
                            "이용기관": selected_facility
                        }])
                        conn.append(worksheet="이용기록", data=log_entry)

                        # 결과 세션 저장 및 페이지 전환
                        st.session_state.auth_result = {
                            "facility": selected_facility,
                            "name": user_name,
                            "clubs": matched_clubs_str,
                            "birth": birth_input,
                            "phone": full_phone,
                            "status": member_status,
                            "join_date": join_date,
                            "time": current_time
                        }
                        st.session_state.page = 'result'
                        st.rerun()

                    else:
                        st.error("❌ 일치하는 회원 정보가 없습니다. 입력한 정보를 확인해 주세요.")
                        
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
                    st.error("데이터베이스 연결 중 오류가 발생했습니다.")

# ----------------------------------------------------
# PAGE 2: 회원 인증 완료 결과 전용 화면
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="success-card">
        <div class="status-badge">✓ 인증 완료</div>
        <div class="user-name">{res['name']} 회원님</div>
        <div class="facility-name">🏥 {res['facility']} 이용 승인</div>
        
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">소속 클럽</span>
                <span class="info-value">{res['clubs']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">회원 자격</span>
                <span class="info-value" style="color: #22c55e;">{res['status']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">생년월일</span>
                <span class="info-value">{res['birth']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">연락처</span>
                <span class="info-value">{res['phone']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">가입일</span>
                <span class="info-value">{res['join_date']}</span>
            </div>
            <div class="info-item">
                <span class="info-label">인증 일시</span>
                <span class="info-value" style="font-size: 0.85rem; color: #64748b;">{res['time']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    if st.button("🔄 다른 회원 조회하기"):
        st.session_state.page = 'input'
        st.session_state.auth_result = None
        st.rerun()
