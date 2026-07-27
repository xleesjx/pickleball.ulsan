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

# Custom CSS for Modern Mobile UI (Pure Native Styling)
st.markdown("""
<style>
    /* Hide Streamlit Header & Footer */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Background & Container setup for Mobile Single Screen */
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 420px !important;
    }

    /* Input Form & Card Containers */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 18px !important;
        padding: 20px 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Form Fields Styling */
    div[data-testid="stForm"] label {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
    }

    /* Mobile Compact Button */
    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 800;
        font-size: 1rem;
        padding: 0.7rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
    }

    /* Metrics & Custom Text Helpers */
    .title-text {
        text-align: center;
        color: #0f172a;
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 2px;
    }
    .subtitle-text {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 14px;
    }
    .user-header {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
        margin-bottom: 2px;
    }
    .facility-header {
        text-align: center;
        font-size: 0.95rem;
        font-weight: 700;
        color: #2563eb;
        margin-bottom: 12px;
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
# PAGE 1: 회원 인증 입력 화면
# ----------------------------------------------------
if st.session_state.page == 'input':
    st.markdown('<div class="title-text">울산피클볼협회</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">회원 인증 서비스</div>', unsafe_allow_html=True)

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
# PAGE 2: 회원 인증 완료 결과 화면 (Streamlit Pure Component)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    st.markdown('<div class="title-text">울산피클볼협회</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">회원 인증 완료</div>', unsafe_allow_html=True)

    # 순수 Streamlit border container 활용 (HTML 코드가 절대 노출되지 않음)
    with st.container(border=True):
        st.success("✓ 모바일 회원 인증이 완료되었습니다.")
        st.markdown(f'<div class="user-header">{res["name"]} <span style="font-size: 1.1rem; font-weight: normal; color: #475569;">회원님</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="facility-header">🏥 {res["facility"]} 이용 승인</div>', unsafe_allow_html=True)
        st.divider()

        # Pure Streamlit Columns로 안전한 레이아웃 구성
        def render_row(label, val, is_highlight=False, is_small=False):
            c1, c2 = st.columns([4, 6])
            with c1:
                st.markdown(f"**{label}**")
            with c2:
                if is_highlight:
                    st.markdown(f":green[**{val}**]")
                elif is_small:
                    st.caption(val)
                else:
                    st.markdown(f"**{val}**")

        render_row("소속 클럽", res['clubs'])
        render_row("회원 자격", res['status'], is_highlight=True)
        render_row("생년월일", res['birth'])
        render_row("연락처", res['phone'])
        render_row("가입일", res['join_date'])
        render_row("인증 일시", res['time'], is_small=True)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 다른 회원 조회하기"):
        st.session_state.page = 'input'
        st.session_state.auth_result = None
        st.rerun()
