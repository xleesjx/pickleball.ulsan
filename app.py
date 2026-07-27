import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page configuration for Mobile View
st.set_page_config(
    page_title="울산피클볼협회 회원 인증",
    page_icon="🏓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS: Ultra-compact Mobile UI & Perfect Alignment
st.markdown("""
<style>
    /* Hide Streamlit Header & Footer */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Background & Container setup for Mobile Single Screen */
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 400px !important;
    }

    /* Input Form Mobile Tuning */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 16px 18px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid #cbd5e1;
    }
    div[data-testid="stForm"] label {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stForm"] input {
        padding: 6px 10px !important;
        font-size: 0.95rem !important;
    }

    /* Result Card Layout (Flexbox List) */
    .mobile-card {
        background-color: #ffffff;
        border: 2px solid #22c55e;
        border-radius: 18px;
        padding: 18px 16px;
        box-shadow: 0 8px 20px rgba(34, 197, 94, 0.12);
    }
    
    .status-pill {
        display: inline-block;
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 800;
        font-size: 0.85rem;
        padding: 4px 14px;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Mobile Compact List Item */
    .mobile-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed #e2e8f0;
    }
    .mobile-row:last-child {
        border-bottom: none;
    }
    .row-label {
        color: #64748b;
        font-weight: 600;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .row-value {
        color: #0f172a;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: right;
        word-break: keep-all;
    }

    /* Button Mobile Optimization */
    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 800;
        font-size: 1rem;
        padding: 0.65rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'auth_result' not in st.session_state:
    st.session_state.auth_result = None

# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면 (모바일 스크롤 최소화)
# ----------------------------------------------------
if st.session_state.page == 'input':
    st.markdown("<h3 style='text-align: center; color: #0f172a; font-weight: 800; margin-top: 0px; margin-bottom: 2px;'>울산피클볼협회</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem; margin-bottom: 12px;'>회원 인증 서비스</p>", unsafe_allow_html=True)

    try:
        config_df = load_data("설정")
        facility_list = config_df.iloc[:, 0].dropna().tolist()
        if not facility_list:
            facility_list = ["참바른병원"]
    except Exception:
        facility_list = ["참바른병원"]

    with st.form("auth_form", clear_on_submit=False):
        selected_facility = st.selectbox("🏥 이용할 협약기관", facility_list)
        user_name = st.text_input("👤 이름", placeholder="예: 홍길동").strip()
        birth_input = st.text_input("📅 생년월일 6자리", placeholder="예: 980101", max_chars=6).strip()
        phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="예: 1234", max_chars=4).strip()
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("회원 인증 조회")

    if submit_button:
        if not user_name:
            st.warning("이름을 입력해주세요.")
        elif not birth_input.isdigit() or len(birth_input) != 6:
            st.error("생년월일은 6자리 숫자로 입력해주세요. (예: 980101)")
        elif not phone_last4.isdigit() or len(phone_last4) != 4:
            st.error("전화번호 뒷자리는 4자리 숫자로 입력해주세요. (예: 1234)")
        else:
            with st.spinner("회원 정보 확인 중..."):
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
                        try:
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
                        except Exception:
                            pass

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
                        st.error("❌ 일치하는 회원 정보가 없습니다.")
                        try:
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
                        except Exception:
                            pass

                except Exception as e:
                    st.error(f"데이터베이스 연결 오류: {str(e)}")

# ----------------------------------------------------
# PAGE 2: 회원 인증 완료 결과 전용 화면 (모바일 1화면 최적화)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    st.markdown("<h3 style='text-align: center; color: #0f172a; font-weight: 800; margin-top: 0px; margin-bottom: 12px;'>울산피클볼협회</h3>", unsafe_allow_html=True)
    
    # 100% 밀착 Flexbox 구조
    st.markdown(f"""
    <div class="mobile-card">
        <div style="text-align: center;">
            <span class="status-pill">✓ 모바일 회원 인증 완료</span>
            <div style="font-size: 1.6rem; font-weight: 800; color: #0f172a; margin-top: 2px;">
                {res['name']} <span style="font-size: 1.1rem; font-weight: normal; color: #475569;">회원님</span>
            </div>
            <div style="font-size: 0.9rem; font-weight: 700; color: #2563eb; margin-bottom: 12px;">
                🏥 {res['facility']} 이용 승인
            </div>
        </div>
        
        <div class="mobile-row">
            <span class="row-label">소속 클럽</span>
            <span class="row-value">{res['clubs']}</span>
        </div>
        <div class="mobile-row">
            <span class="row-label">회원 자격</span>
            <span class="row-value" style="color: #16a34a;">{res['status']}</span>
        </div>
        <div class="mobile-row">
            <span class="row-label">생년월일</span>
            <span class="row-value">{res['birth']}</span>
        </div>
        <div class="mobile-row">
            <span class="row-label">연락처</span>
            <span class="row-value">{res['phone']}</span>
        </div>
        <div class="mobile-row">
            <span class="row-label">가입일</span>
            <span class="row-value">{res['join_date']}</span>
        </div>
        <div class="mobile-row">
            <span class="row-label">인증 일시</span>
            <span class="row-value" style="font-size: 0.8rem; color: #64748b; font-weight: 500;">{res['time']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 다른 회원 조회하기"):
        st.session_state.page = 'input'
        st.session_state.auth_result = None
        st.rerun()
