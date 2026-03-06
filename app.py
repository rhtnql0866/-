import streamlit as st
import requests
import json
import os

# --- 1. 환경 설정 (모바일 최적화) ---
st.set_page_config(page_title="포켓몬고 상성 도우미", page_icon="⚔️", layout="centered")

# --- 2. 데이터 및 사전 정의 ---
TYPE_KO = {
    "normal": "노말", "fire": "불꽃", "water": "물", "grass": "풀", 
    "electric": "전기", "ice": "얼음", "fighting": "격투", "poison": "독", 
    "ground": "땅", "flying": "비행", "psychic": "에스퍼", "bug": "벌레", 
    "rock": "바위", "ghost": "고스트", "dragon": "드래곤", "dark": "악", 
    "steel": "강철", "fairy": "페어리"
}

COUNTER_POKEMON = {
    "fire": ["레시라무", "파이어", "번치코"],
    "water": ["가이오가", "대짱이", "킹크랩"],
    "grass": ["종이신도", "자루도", "이상해꽃"],
    "electric": ["전수목", "제크로무", "에레키블"],
    "ice": ["맘모꾸리", "글레이시아", "가라르 불비달마"],
    "fighting": ["테라키온", "매시붕", "괴력몬"],
    "poison": ["텅비드", "로즈레이드", "독개굴"],
    "ground": ["그란돈", "한카리아스", "거대코뿌리"],
    "flying": ["레쿠쟈", "돈크로우", "이벨타르"],
    "psychic": ["뮤츠", "후파", "에스바번"],
    "bug": ["매시붕", "불카모스", "핫삼"],
    "rock": ["거대코뿌리", "테라키온", "램파드"],
    "ghost": ["기라티나", "샹델라", "팬텀"],
    "dragon": ["펄기아", "디아루가", "레쿠쟈"],
    "dark": ["삼삼드래", "다크라이", "마기라스"],
    "steel": ["메타그로스", "디아루가", "몰드류"],
    "fairy": ["제르네아스", "가디안", "토게키스"]
}

# --- 3. 데이터 로드 함수 ---
@st.cache_data
def load_pokemon_dict():
    if os.path.exists('pokemon_names.json'):
        with open('pokemon_names.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

pokemon_dict = load_pokemon_dict()

# --- 4. 앱 화면 구성 ---
st.title("⚔️ 포켓몬고 상성 도우미")

if pokemon_dict:
    # 검색창
    target = st.text_input("포켓몬 이름을 입력하세요", placeholder="예: 망나뇽, 리자몽")

    if target:
        english_name = pokemon_dict.get(target)
        if english_name:
            try:
                # API 호출
                res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{english_name}").json()
                types = [t['type']['name'] for t in res['types']]
                ko_types = [TYPE_KO.get(t, t) for t in types]
                
                st.subheader(f"🔍 {target} ({' / '.join(ko_types)})")
                
                # 상성 계산
                multipliers = {}
                for t in types:
                    type_data = requests.get(f"https://pokeapi.co/api/v2/type/{t}").json()
                    for w in type_data['damage_relations']['double_damage_from']:
                        multipliers[w['name']] = multipliers.get(w['name'], 1.0) * 1.6
                    for r in type_data['damage_relations']['half_damage_from']:
                        multipliers[r['name']] = multipliers.get(r['name'], 1.0) * 0.625
                    for n in type_data['damage_relations']['no_damage_from']:
                        multipliers[n['name']] = multipliers.get(n['name'], 1.0) * 0.39

                # 결과 출력 - 공격/방어 탭 구분 (모바일 가독성)
                tab1, tab2 = st.tabs(["🔴 공격 (약점)", "🔵 방어 (내성)"])

                with tab1:
                    d_weak = [n for n, m in multipliers.items() if m > 2.0]
                    weak = [n for n, m in multipliers.items() if 1.5 < m <= 2.0]
                    
                    if d_weak:
                        st.error("**💀 이중 약점 (x2.56)**")
                        for dw in d_weak:
                            st.write(f"**{TYPE_KO.get(dw, dw)}**: {', '.join(COUNTER_POKEMON.get(dw, ['?']))}")
                    
                    st.warning("**🔸 일반 약점 (x1.60)**")
                    for w in weak:
                        st.write(f"**{TYPE_KO.get(w, w)}**: {', '.join(COUNTER_POKEMON.get(w, ['?']))}")

                with tab2:
                    resist = [n for n, m in multipliers.items() if m < 1.0]
                    if resist:
                        resist.sort(key=lambda x: multipliers[x])
                        for r in resist:
                            m = multipliers[r]
                            tag = "🛡️ 매우강함" if m < 0.5 else "✅ 반감"
                            st.write(f"{tag} (x{m:.2f}): **{TYPE_KO.get(r, r)}**")
                    else:
                        st.write("특별한 내성이 없습니다.")

            except:
                st.error("데이터를 가져오는 중 오류가 발생했습니다.")
        else:
            st.error("도감에 없는 이름입니다. 한글 이름을 확인해 주세요.")
else:
    st.warning("먼저 'make_list.py'를 실행하여 사전 파일을 생성해 주세요.")
