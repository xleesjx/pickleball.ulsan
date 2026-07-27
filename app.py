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

# Custom CSS for Modern UI & Hiding Streamlit Branding
st.markdown("""
<style>
    /* Streamlit 브랜드 및 헤더/푸터 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 기본 배경 */
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }

    /* 입력 폼 영역 깔끔한 카드로 감싸기 */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }

    /* 결과 출력 카드 컨테이너 */
    .result-card {
        background-color: #ffffff;
        border: 2px solid #22c55e;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(34, 197, 94, 0.12);
    }

    /* 테이블 행 정렬 보장 */
    .info-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .info-table tr {
        border-bottom: 1px dashed #e2e8f0;
    }
    .info-table tr:last-child {
        border-bottom: none;
    }
    .info-table td {
        padding: 12px 4px;
        vertical-align: middle;
    }
    .td-label {
        color: #64748b;
        font-weight: 600;
        font-size: 0.95rem;
        text-align: left;
        width: 35%;
    }
    .td-value {
        color: #0f172a;
        font-weight: 700;
        font-size: 1rem;
        text-align: right;
        width: 65%;
    }

    /* 버튼 스타일 */
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
    st.markdown("<h2 style='text-align: center; color: #0f172a; font-weight: 800; margin-bottom: 4px;'>울산피클볼협회 회원 인증</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem; margin-bottom: 24px;'>협약기관 이용을 위한 본인 확인 서비스</p>", unsafe_allow_html=True)

    # 이용기관 목록 불러오기
    try:
        config_df = load_data("설정")
        facility_list = config_df.iloc[:, 0].dropna().tolist()
        if not facility_list:
            facility_list = ["참바른병원"]
    except Exception:
        facility_list = ["참바른병원"]

    # 입력 폼 시작
    with st.form("auth_form", clear_on_submit=False):
        selected_facility = st.selectbox("🏥 이용할 협약기관", facility_list)
        user_name = st.text_input("👤 이름", placeholder="홍길동").strip()
        birth_input = st.text_input("📅 생년월일 6자리 (예: 980101)", placeholder="831215", max_chars=6).strip()
        phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="2328", max_chars=4).strip()
        
        st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
        submit_button = st.form_submit_button("회원 인증 조회")

    # 버튼 클릭 처리
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

                        # 결과 화면 세션 저장
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
# PAGE 2: 회원 인증 완료 결과 전용 화면 (줄맞춤 완벽 보장)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    st.markdown("<h2 style='text-align: center; color: #0f172a; font-weight: 800; margin-bottom: 16px;'>울산피클볼협회</h2>", unsafe_allow_html=True)
    
    # HTML Table 구조로 구현하여 완벽한 행 높이 정렬
    st.markdown(f"""
    <div class="result-card">
        <div style="background-color: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.9rem; padding: 6px 16px; border-radius: 20px; text-align: center; width: fit-content; margin: 0 auto 12px auto;">
            ✓ 회원 인증 완료
        </div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 4px;">
            {res['name']} 회원님
        </div>
        <div style="font-size: 0.95rem; color: #64748b; text-align: center; margin-bottom: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;">
            🏥 {res['facility']} 이용 승인
        </div>
        
        <table class="info-table">
            <tr>
                <td class="td-label">소속 클럽</td>
                <td class="td-value">{res['clubs']}</td>
            </tr>
            <tr>
                <td class="td-label">회원 자격</td>
                <td class="td-value" style="color: #22c55e;">{res['status']}</td>
            </tr>
            <tr>
                <td class="td-label">생년월일</td>
                <td class="td-value">{res['birth']}</td>
            </tr>
            <tr>
                <td class="td-label">연락처</td>
                <td class="td-value">{res['phone']}</td>
            </tr>
            <tr>
                <td class="td-label">가입일</td>
                <td class="td-value">{res['join_date']}</td>
            </tr>
            <tr>
                <td class="td-label">인증 일시</td>
                <td class="td-value" style="font-size: 0.85rem; color: #64748b; font-weight: 500;">{res['time']}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    
    if st.button("🔄 다른 회원 조회하기"):
        st.session_state.page = 'input'
        st.session_state.auth_result = None
        st.rerun()
