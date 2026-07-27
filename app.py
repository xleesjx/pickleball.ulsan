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

# Custom CSS for Design Matching the Sample Screenshots
st.markdown("""
<style>
    /* Streamlit 브랜드 및 기본 헤더/푸터 숨기기 */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 전체 배경색 */
    .stApp {
        background-color: #eef2f6;
    }
    
    /* 모바일 중심 메인 컨테이너 */
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 420px !important;
    }

    /* 카드 컨테이너 스타일 (시안 스타일 반영) */
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 24px !important;
        padding: 24px 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #ffffff !important;
    }

    /* 입력 필드 라벨 */
    div[data-testid="stForm"] label {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 4px !important;
    }

    /* 입력 창 테두리 라운드 */
    div[data-testid="stForm"] input, div[data-testid="stForm"] div[data-baseweb="select"] {
        border-radius: 12px !important;
    }

    /* 주요 메인 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: 800;
        font-size: 1.05rem;
        padding: 0.75rem;
        border-radius: 14px;
        border: none;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }

    /* 결과 카드 하단 다시 인증하기 버튼 (연한 스타일) */
    .secondary-btn > button {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        box-shadow: none !important;
    }
    .secondary-btn > button:hover {
        background-color: #dbeafe !important;
    }

    /* 결과 테이블 CSS */
    .res-box {
        background-color: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 16px;
        padding: 12px 16px;
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
        font-size: 0.9rem;
        font-weight: 600;
    }
    .res-val {
        color: #0f172a;
        font-size: 0.95rem;
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

# 1. Google Sheets Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'auth_result' not in st.session_state:
    st.session_state.auth_result = None

# 로고 출력 공통 함수
def show_logo():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 12px;">
        <div style="display: inline-block; width: 64px; height: 64px; background-color: #ffffff; border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 8px; vertical-align: middle;">
            <svg viewBox="0 0 100 100" width="48" height="48">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#15803d" stroke-width="4"/>
                <text x="50" y="38" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">ULSAN</text>
                <text x="50" y="55" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">PICKLEBALL</text>
                <text x="50" y="70" font-size="9" fill="#16a34a" text-anchor="middle">SINCE 2023</text>
            </svg>
        </div>
        <h2 style="font-weight: 800; color: #0f172a; margin-top: 10px; margin-bottom: 0px; font-size: 1.35rem;">울산피클볼협회</h2>
        <p style="font-weight: 700; color: #1e293b; margin-top: 2px; margin-bottom: 2px; font-size: 1.1rem;">회원인증</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면 (시안 1 스타일)
# ----------------------------------------------------
if st.session_state.page == 'input':
    # 상단 카드 영역 시작
    with st.container():
        show_logo()
        st.markdown('<p style="text-align: center; color: #64748b; font-size: 0.85rem; margin-bottom: 18px;">회원 정보를 입력하고 자격을 확인하세요</p>', unsafe_allow_html=True)

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
            
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
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
# PAGE 2: 회원 인증 완료 결과 화면 (시안 2 스타일)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    with st.container():
        show_logo()
        
        # 제출용 조회 결과 상단 배지
        st.markdown(f'''
        <div style="text-align: center; margin-bottom: 16px;">
            <span style="background-color: #eff6ff; color: #2563eb; font-weight: 700; font-size: 0.85rem; padding: 6px 16px; border-radius: 20px;">
                {res['facility']} 제출용 조회 결과
            </span>
        </div>
        
        <div style="text-align: center; margin-bottom: 8px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 52px; height: 52px; background-color: #dcfce7; border-radius: 50%;">
                <span style="color: #16a34a; font-size: 1.6rem; font-weight: bold;">✓</span>
            </div>
        </div>
        
        <div style="text-align: center; font-size: 1.35rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">
            회원 인증 완료
        </div>
        <div style="text-align: center; font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">
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
        ''', unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        
        # 시안 하단 연한 파란색 버튼 스타일
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("다시 인증하기"):
            st.session_state.page = 'input'
            st.session_state.auth_result = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
