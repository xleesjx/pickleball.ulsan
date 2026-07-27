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

# 구글 드라이브 로고 원본 파일 ID 적용
FILE_ID = "1qRvmGoexXsmzAu5zpBR0Gb6y7a1hn1bv"
LOGO_URL = f"https://drive.google.com/uc?export=view&id={FILE_ID}"

# ==========================================
# 🎨 최신 트렌드 반영 모바일 최적화 CSS
# ==========================================
st.markdown("""
<style>
/* 1. 스트림릿 기본 UI 요소를 영혼까지 끌어모아 완벽 숨김 */
[data-testid="stHeader"], [data-testid="stToolbar"] {display: none !important;}
footer, #MainMenu {visibility: hidden !important; display: none !important;}
.viewerBadge_container__1X33n, .viewerBadge_link__1S137, [data-testid="stDecoration"] {display: none !important;}

/* 2. 전체 앱 배경색 및 여백 (앱 느낌의 은은한 배경) */
.stApp { background-color: #f3f6f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.main .block-container {
    padding: 0rem 1rem 2rem 1rem !important;
    max-width: 420px !important;
    margin: 0 auto;
}

/* 3. 모던 카드형 디자인 (입력/결과 화면 통일, 부드러운 그림자) */
div[data-testid="stForm"], .result-card {
    background-color: #ffffff !important;
    border-radius: 28px !important;
    padding: 30px 24px !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    border: none !important;
}

/* 4. 입력 폼 최적화 */
div[data-testid="stForm"] label {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #475569 !important;
    margin-bottom: 6px !important;
}

/* 인풋 박스 터치 최적화 및 포커스 애니메이션 */
div[data-testid="stForm"] input, div[data-testid="stForm"] div[data-baseweb="select"] > div {
    border-radius: 16px !important;
    padding: 0.4rem !important;
    border: 1px solid #e2e8f0 !important;
    background-color: #f8fafc !important;
    font-size: 1rem !important;
    color: #0f172a !important;
    transition: all 0.2s ease;
}
div[data-testid="stForm"] input:focus, div[data-testid="stForm"] div[data-baseweb="select"] > div:focus-within {
    border-color: #3b82f6 !important;
    background-color: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* 5. 트렌디한 중앙 정렬 필(Pill) 버튼 */
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] {
    display: flex !important;
    justify-content: center !important;
    margin-top: 18px !important;
}

.stButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 2rem !important;
    border-radius: 9999px !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
    max-width: 220px !important;
}
.stButton > button:hover {
    background-color: #1d4ed8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3) !important;
}

/* 6. 결과 정보 리스트 디자인 */
.res-box {
    background-color: #ffffff;
    border: 1px solid #f1f5f9;
    border-radius: 20px;
    padding: 16px 20px;
    margin-top: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.015);
}
.res-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f8fafc;
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
    font-size: 0.95rem;
    font-weight: 800;
}
.badge-blue {
    background-color: #eff6ff;
    color: #2563eb;
    font-weight: 800;
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 9999px;
}
.badge-green {
    background-color: #f0fdf4;
    color: #16a34a;
    font-weight: 800;
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 9999px;
}
</style>
""", unsafe_allow_html=True)

# Google Sheets 연결
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl=0)

if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'auth_result' not in st.session_state:
    st.session_state.auth_result = None

# ==========================================
# ⚠️ [중요] 코드 노출 방지를 위해 HTML 내 들여쓰기 100% 제거
# ==========================================
def render_header():
    html_header = f"""<div style="text-align: center; margin-top: 10px; margin-bottom: 24px;">
<div style="display: inline-block; width: 84px; height: 84px; background-color: #ffffff; border-radius: 42px; padding: 6px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); margin-bottom: 16px;">
<img src="{LOGO_URL}" style="width: 100%; height: 100%; object-fit: contain; border-radius: 50%;">
</div>
<h2 style="font-weight: 800; color: #0f172a; margin: 0; font-size: 1.5rem; letter-spacing: -0.5px;">울산피클볼협회</h2>
<p style="font-weight: 700; color: #3b82f6; margin-top: 4px; margin-bottom: 0; font-size: 1.05rem;">회원인증 서비스</p>
</div>"""
    st.markdown(html_header, unsafe_allow_html=True)


# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면
# ----------------------------------------------------
if st.session_state.page == 'input':
    with st.container():
        render_header()
        
        html_desc = """<p style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 0; margin-bottom: 20px;">회원 정보를 입력하고 자격을 확인하세요</p>"""
        st.markdown(html_desc, unsafe_allow_html=True)

        try:
            config_df = load_data("설정")
            facility_list = config_df.iloc[:, 0].dropna().tolist()
            if not facility_list:
                facility_list = ["참바른병원"]
        except Exception:
            facility_list = ["참바른병원"]

        with st.form("auth_form", clear_on_submit=False):
            selected_facility = st.selectbox("🏥 협약기관", facility_list)
            user_name = st.text_input("👤 성명", placeholder="홍길동").strip()
            birth_input = st.text_input("📅 생년월일 (6자리, 예: 980301)", placeholder="980301", max_chars=6).strip()
            phone_last4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="1234", max_chars=4).strip()
            
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
# PAGE 2: 회원 인증 완료 결과 화면 (코드 노출 원천 차단)
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    
    with st.container():
        render_header()
        
        # ⚠️ HTML 문자열 안의 들여쓰기를 전부 제거하여 코드 블록 노출 현상을 완전히 해결했습니다.
        result_html = f"""<div class="result-card">
<div style="text-align: center; margin-bottom: 18px;">
<span style="background-color: #eff6ff; color: #2563eb; font-weight: 800; font-size: 0.85rem; padding: 6px 16px; border-radius: 9999px; border: 1px solid #dbeafe;">
{res['facility']} 제출용
</span>
</div>
<div style="text-align: center; margin-bottom: 12px;">
<div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 4px 16px rgba(34, 197, 94, 0.3);">
<span style="color: #ffffff; font-size: 1.8rem; font-weight: bold;">✓</span>
</div>
</div>
<div style="text-align: center; font-size: 1.4rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; letter-spacing: -0.5px;">
인증 완료
</div>
<div style="text-align: center; font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">
정상적으로 회원 정보가 확인되었습니다
</div>
<div class="res-box">
<div class="res-row"><span class="res-label">소속 클럽</span><span class="badge-blue">{res['clubs']}</span></div>
<div class="res-row"><span class="res-label">이름</span><span class="res-val">{res['name']}</span></div>
<div class="res-row"><span class="res-label">생년월일</span><span class="res-val">{res['birth']}</span></div>
<div class="res-row"><span class="res-label">전화번호</span><span class="res-val">{res['phone']}</span></div>
<div class="res-row"><span class="res-label">회원상태</span><span class="badge-green">{res['status']}</span></div>
<div class="res-row"><span class="res-label">가입일</span><span class="res-val">{res['join_date']}</span></div>
</div>
</div>"""
        st.markdown(result_html, unsafe_allow_html=True)

        # 하단 중앙 "다시 인증하기" 버튼 배치
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("다시 인증하기"):
                st.session_state.page = 'input'
                st.session_state.auth_result = None
                st.rerun()
