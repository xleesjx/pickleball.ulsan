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

# 구글 드라이브 로고 ID (구글 공식 CDN 직링크 및 썸네일 백업 적용)
FILE_ID = "1qRvmGoexXsmzAu5zpBR0Gb6y7a1hn1bv"
LOGO_URL = f"https://lh3.googleusercontent.com/d/{FILE_ID}"
LOGO_FALLBACK = f"https://drive.google.com/thumbnail?id={FILE_ID}&sz=w500"

# ==========================================
# 🎨 전역 CSS (입력화면 & 출력화면 상단여백 0px 및 디자인 100% 통일)
# ==========================================
st.markdown("""
<style>
/* 1. 스트림릿 기본 헤더, 툴바, 푸터, 배포 버튼 완벽 차단 */
header[data-testid="stHeader"],
[data-testid="stHeader"], 
[data-testid="stToolbar"], 
[data-testid="stAppDeployButton"],
.stDeployButton,
footer, 
#MainMenu, 
.viewerBadge_container__1X33n, 
[data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
}

/* 2. 최상위 배경 및 모든 컨테이너 상단 여백 0px (모바일 스크롤 완벽 방지) */
.stApp { 
    background-color: #f3f6f9 !important; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
}

div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > section {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.main .block-container, 
[data-testid="stMainBlockContainer"], 
div[data-testid="stAppViewBlockContainer"] {
    padding-top: 0.2rem !important; /* 모바일에서 최상단에 바짝 붙임 */
    padding-bottom: 1.5rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    max-width: 420px !important;
    margin: 0 auto !important;
}

[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

/* 3. 카드형 디자인 (입력 폼 & 출력 카드 디자인 통일) */
div[data-testid="stForm"], .result-card {
    background-color: #ffffff !important;
    border-radius: 28px !important;
    padding: 24px 20px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
    border: none !important;
}

/* 4. 입력 필드 라벨 & 박스 스타일 (출력화면 폰트 가이드와 일치) */
div[data-testid="stForm"] label {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: #475569 !important;
    margin-bottom: 4px !important;
}

div[data-baseweb="input"], div[data-baseweb="select"] > div {
    border-radius: 14px !important;
    border: 1px solid #e2e8f0 !important;
    background-color: #f8fafc !important;
    box-shadow: none !important;
    outline: none !important;
}

div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {
    border-color: #3b82f6 !important;
    background-color: #ffffff !important;
}

div[data-baseweb="base-input"] > input {
    color: #1e293b !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* 영문 안내 문구 숨기기 */
div[data-testid="InputInstructions"], [data-testid="stInputInstruction"] {
    display: none !important;
}

/* 5. 파란색 라운드 버튼 (입력/출력 공통 통일) */
div[data-testid="stFormSubmitButton"] {
    display: flex !important;
    justify-content: center !important;
    margin-top: 10px !important;
}

.stButton {
    display: flex !important;
    justify-content: center !important;
}

.stButton > button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2.5rem !important;
    border-radius: 9999px !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.2s ease !important;
    width: auto !important;
    min-width: 150px !important;
}

.stButton > button:hover {
    background-color: #1d4ed8 !important;
    transform: translateY(-1px);
}

/* 6. 결과 리스트 박스 */
.res-box {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 14px 18px;
    margin-top: 14px;
}
.res-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
}
.res-row:last-child { border-bottom: none; }
.res-label { color: #64748b; font-size: 0.88rem; font-weight: 600; }
.res-val { color: #0f172a; font-size: 0.95rem; font-weight: 800; }
.badge-blue { background-color: #eff6ff; color: #2563eb; font-weight: 800; font-size: 0.82rem; padding: 4px 14px; border-radius: 9999px; }
.badge-green { background-color: #f0fdf4; color: #16a34a; font-weight: 800; font-size: 0.82rem; padding: 4px 14px; border-radius: 9999px; }
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
# ⚠️ 들여쓰기 100% 제거된 헤더 HTML
# ==========================================
def render_header():
    html_header = f"""<div style="text-align: center; margin-top: 0px; margin-bottom: 16px;">
<div style="display: inline-block; width: 80px; height: 80px; background-color: #ffffff; border-radius: 40px; padding: 4px; box-shadow: 0 6px 16px rgba(0,0,0,0.06); margin-bottom: 8px;">
<img src="{LOGO_URL}" onerror="this.onerror=null; this.src='{LOGO_FALLBACK}';" style="width: 100%; height: 100%; object-fit: contain; border-radius: 50%;">
</div>
<h2 style="font-weight: 800; color: #0f172a; margin: 0; font-size: 1.45rem; letter-spacing: -0.5px;">울산피클볼협회</h2>
<p style="font-weight: 700; color: #3b82f6; margin-top: 3px; margin-bottom: 0; font-size: 1rem;">회원인증 서비스</p>
</div>"""
    st.markdown(html_header, unsafe_allow_html=True)


# ----------------------------------------------------
# PAGE 1: 회원 인증 입력 화면
# ----------------------------------------------------
if st.session_state.page == 'input':
    with st.container():
        render_header()
        
        html_desc = """<p style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 0; margin-bottom: 14px;">회원 정보를 입력하고 자격을 확인하세요</p>"""
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
                            "facility": selected_facility, "name": user_name, "clubs": matched_clubs_str,
                            "birth": birth_input, "phone": full_phone, "status": member_status,
                            "join_date": join_date, "time": current_time
                        }
                        st.session_state.page = 'result'
                        st.rerun()
                    else:
                        st.error("❌ 일치하는 회원 정보가 없습니다.")
                except Exception as e:
                    st.error(f"연결 오류: {str(e)}")

# ----------------------------------------------------
# PAGE 2: 회원 인증 완료 결과 화면
# ----------------------------------------------------
elif st.session_state.page == 'result':
    res = st.session_state.auth_result
    with st.container():
        render_header()
        
        result_html = f"""<div class="result-card">
<div style="text-align: center; margin-bottom: 14px;">
<span class="badge-blue">{res['facility']} 제출용</span>
</div>
<div style="text-align: center; margin-bottom: 8px;">
<div style="display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25);">
<span style="color: #ffffff; font-size: 1.5rem; font-weight: bold;">✓</span>
</div>
</div>
<div style="text-align: center; font-size: 1.35rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">인증 완료</div>
<div style="text-align: center; font-size: 0.85rem; color: #64748b; margin-bottom: 14px;">정상적으로 회원 정보가 확인되었습니다</div>
<div class="res-box">
<div class="res-row"><span class="res-label">소속 클럽</span><span class="badge-blue" style="font-size:0.75rem;">{res['clubs']}</span></div>
<div class="res-row"><span class="res-label">이름</span><span class="res-val">{res['name']}</span></div>
<div class="res-row"><span class="res-label">생년월일</span><span class="res-val">{res['birth']}</span></div>
<div class="res-row"><span class="res-label">전화번호</span><span class="res-val">{res['phone']}</span></div>
<div class="res-row"><span class="res-label">회원상태</span><span class="badge-green">{res['status']}</span></div>
<div class="res-row"><span class="res-label">가입일</span><span class="res-val">{res['join_date']}</span></div>
</div>
</div>"""
        st.markdown(result_html, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        if st.button("다시 인증하기"):
            st.session_state.page = 'input'
            st.session_state.auth_result = None
            st.rerun()
