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

# Custom CSS: 상단 여백 제거, 코드 깜빡임 방지, 하단 로고 완전 숨김
st.markdown("""
<style>
    /* Streamlit 기본 헤더, 푸터, 로고, 메뉴 완전 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    .viewerBadge_container__1X33n {display: none !important;}
    
    /* 전체 배경색 */
    .stApp {
        background-color: #eef2f6;
    }
    
    /* 메인 컨테이너 상단 여백(Margin/Padding) 최소화 */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 420px !important;
    }

    /* 카드 컨테이너 스타일 */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 24px !important;
        padding: 20px 18px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #ffffff !important;
    }

    /* 입력 필드 라벨 스타일 */
    div[data-testid="stForm"] label {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 2px !important;
    }

    /* 입력창 및 셀렉트박스 모서리 라운드 */
    div[data-testid="stForm"] input, div[data-testid="stForm"] div[data-baseweb="select"] {
        border-radius: 12px !important;
    }

    /* 메인 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: 800;
        font-size: 1.05rem;
        padding: 0.7rem;
        border-radius: 14px;
        border: none;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }

    /* 다시 인증하기 버튼 (연한 파란색 스타일) */
    .secondary-btn > button {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        box-shadow: none !important;
    }
    .secondary-btn > button:hover {
        background-color: #dbeafe !important;
    }

    /* 결과 리스트 레이아웃 */
    .res-box {
        background-color: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 10px 14px;
        margin-top: 10px;
    }
    .res-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed #e2e8f0;
    }
    .res-row:last-child {
        border-bottom: none;
    }
    .res-label {
        color: #64748b;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .res-val {
        color: #0f172a;
        font-size: 0.92rem;
        font-weight: 700;
    }
    .badge-blue {
        background-color: #dbeafe;
        color: #1d4ed8;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 12px;
    }
    .badge-green {
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Google Drive 로고 이미지 URL (직링크 변환)
LOGO_URL = "https://lh3.googleusercontent.com/d/1qRvmGoexXsmzAu5zpBR0Gb6y7a1hn1bv"

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'auth_result' not in st.session_state:
    st.session_state.auth_result = None

# 상단 협회 로고 출력 (코드 노출 방지 처리)
def show_logo():
    logo_html = f'''
    <div style="text-align: center; margin-bottom: 8px;">
        <img src="{LOGO_URL}" style="width: 70px; height: 70px; object-fit: contain; filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.1)); margin-bottom: 6px;">
        <h2 style="font-weight: 800; color: #0f172a; margin: 0; font-size: 1.3rem;">울산피클볼협회</h2>
        <p style="font-weight: 700; color: #1e293b; margin-top: 2px; margin-bottom: 0; font-size: 1.05rem;">회원인증</p>
    </div>
    '''
    st.markdown(logo_html, unsafe_allow_html=True)

# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면
# ----------------------------------------------------
if st.session_state.page == 'input':
    with st.container():
        show_logo()
        st.markdown('<p style="text-align: center; color: #64748b; font-size: 0.82rem; margin-top: 4px; margin-bottom: 14px;">회원 정보를 입력하고 자격을 확인하세요</p>', unsafe_allow_html=True)

        try:
            config_df = load_data("설정")
            facility_list = config_df.iloc[:, 0].dropna().tolist()
            if not facility_list:
                facility_list = ["참바른병원"]
        except Exception:
            facility_list = ["참바른병원"]

        with st.form("auth_form", clear_on_submit=False):
            selected_facility = st.selectbox("협약기관", facility_list)
            user_name = st.text_input("성명", placeholder="홍길동").strip()
            birth_input = st.text_input("생년월일 (6자리, 예: 980301)", placeholder="980301", max_chars=6).strip()
            phone_last4 = st.text_input("전화번호 뒷 4자리", placeholder="1234", max_chars=4).strip()
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("인증하기")

    if submit_button:
        if not user_name:
            st.warning("성명을 입력해주세요.")
        elif not birth_input.isdigit() or len(birth_input) != 6:
            st.error("생년월일은 6자리 숫자로 입력해주세요.")
        elif not phone_last4.isdigit() or len(phone_last4) != 4:
            st.error("전화번호 뒷자리는 4자리 숫자로 입력해주세요.")
        else:
            with st.spinner("회원 자격 확인 중..."):
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
# PAGE 2: 회원 인증 완료 결과 화면
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    with st.container():
        show_logo()
        
        result_html = f'''
        <div style="text-align: center; margin-top: 4px; margin-bottom: 12px;">
            <span style="background-color: #eff6ff; color: #2563eb; font-weight: 700; font-size: 0.82rem; padding: 5px 14px; border-radius: 20px;">
                {res['facility']} 제출용 조회 결과
            </span>
        </div>
        
        <div style="text-align: center; margin-bottom: 6px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 46px; height: 46px; background-color: #dcfce7; border-radius: 50%;">
                <span style="color: #16a34a; font-size: 1.4rem; font-weight: bold;">✓</span>
            </div>
        </div>
        
        <div style="text-align: center; font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">
            회원 인증 완료
        </div>
        <div style="text-align: center; font-size: 0.82rem; color: #64748b; margin-bottom: 10px;">
            1건의 회원 정보가 확인되었습니다
        </div>
        
        <div class="res-box">
            <div class="res-row">
                <span class="res-label">소속 클럽</span>
                <span class="badge-blue">{res['clubs']}</span>
            </div>
            <div class="res-row">
                <span class="res-label">이름</span>
                <span class="res-val">{res['name']}</span>
            </div>
            <div class="res-row">
                <span class="res-label">생년월일</span>
                <span class="res-val">{res['birth']}</span>
            </div>
            <div class="res-row">
                <span class="res-label">전화번호</span>
                <span class="res-val">{res['phone']}</span>
            </div>
            <div class="res-row">
                <span class="res-label">회원상태</span>
                <span class="badge-green">{res['status']}</span>
            </div>
            <div class="res-row">
                <span class="res-label">가입일</span>
                <span class="res-val">{res['join_date']}</span>
            </div>
        </div>
        '''
        st.markdown(result_html, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("다시 인증하기"):
            st.session_state.page = 'input'
            st.session_state.auth_result = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
