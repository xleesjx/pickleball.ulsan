import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="울산피클볼협회 회원 인증",
    page_icon="🏓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS: Modern 2026 App UI Style & Hide Streamlit Branding
st.markdown("""
<style>
    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Background & Container */
    .stApp {
        background-color: #f1f5f9;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 440px;
    }

    /* Input Form Styling */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.8rem;
        border-radius: 14px;
        border: none;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

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
    st.markdown("<h2 style='text-align: center; color: #0f172a; font-weight: 800; margin-bottom: 2px;'>울산피클볼협회</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.95rem; font-weight: 600; margin-bottom: 24px;'>모바일 회원 인증 서비스</p>", unsafe_allow_html=True)

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
        birth_input = st.text_input("📅 생년월일 6자리 (예: 980101)", placeholder="980101", max_chars=6).strip()
        phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="1234", max_chars=4).strip()
        
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("회원 인증 조회")

    if submit_button:
        if not user_name:
            st.warning("이름을 입력해주세요.")
        elif not birth_input.isdigit() or len(birth_input) != 6:
            st.error("생년월일은 6자리 숫자로 입력해주세요. (예: 980101)")
        elif not phone_last4.isdigit() or len(phone_last4) != 4:
            st.error("전화번호 뒷자리는 4자리 숫자로 입력해주세요. (예: 1234)")
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
                        st.error("❌ 일치하는 회원 정보가 없습니다. 입력한 정보를 확인해 주세요.")
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
                    st.error(f"데이터베이스 연결 중 오류가 발생했습니다: {str(e)}")

# ----------------------------------------------------
# PAGE 2: 회원 인증 완료 결과 전용 화면 (Native Pure UI)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    st.markdown("<h3 style='text-align: center; color: #64748b; font-size: 1rem; font-weight: 700; margin-bottom: 12px;'>울산피클볼협회</h3>", unsafe_allow_html=True)
    
    # 렌더링 깨짐 현상을 방지하기 위한 Pure Streamlit Container
    with st.container(border=True):
        st.success("✓ 모바일 회원 인증 완료")
        st.markdown(f"<h1 style='text-align: center; color: #0f172a; margin-top: 10px; margin-bottom: 2px;'>{res['name']} <span style='font-size: 1.2rem; font-weight: normal;'>회원님</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #2563eb; font-weight: 700; margin-bottom: 15px;'>🏥 {res['facility']} 이용 승인</p>", unsafe_allow_html=True)
        
        st.divider()

        # Pure Native Metrics/Columns로 완벽한 줄맞춤
        items = [
            ("소속 클럽", res['clubs']),
            ("회원 자격", res['status']),
            ("생년월일", res['birth']),
            ("연락처", res['phone']),
            ("가입일", res['join_date']),
            ("인증 일시", res['time'])
        ]

        for label, val in items:
            c1, c2 = st.columns([4, 6])
            with c1:
                st.markdown(f"<p style='color: #64748b; font-weight: 600; margin: 0;'>{label}</p>", unsafe_allow_html=True)
            with c2:
                if label == "회원 자격":
                    st.markdown(f"<p style='text-align: right; color: #16a34a; font-weight: 800; margin: 0;'>{val}</p>", unsafe_allow_html=True)
                elif label == "인증 일시":
                    st.markdown(f"<p style='text-align: right; color: #94a3b8; font-size: 0.85rem; margin: 0;'>{val}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='text-align: right; color: #0f172a; font-weight: 700; margin: 0;'>{val}</p>", unsafe_allow_html=True)
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 다른 회원 조회하기"):
        st.session_state.page = 'input'
        st.session_state.auth_result = None
        st.rerun()
