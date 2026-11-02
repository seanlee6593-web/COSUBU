import streamlit as st
import json
import os
import random
import pandas as pd

# ==========================================
# 1. 환경 설정 및 데이터 파일 이름
# ==========================================
st.set_page_config(page_title="스마트 영단어장", page_icon="📖", layout="centered")

VOCAB_FILE = "vocabulary.json"
WRONG_FILE = "wrong_words.json"

# ==========================================
# 2. 파일 입출력 (안전하게 불러오기/저장하기)
# ==========================================
def load_data(file_name):
    if not os.path.exists(file_name):
        return {}
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_data(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. Session State 초기화 (데이터 기억하기)
# ==========================================
# 전체 단어장 불러오기
if 'vocab' not in st.session_state:
    st.session_state['vocab'] = load_data(VOCAB_FILE)
    # 처음 실행해서 파일이 비어있다면 기본 단어 제공
# 오답 노트 불러오기
# ==========================================
# 3. Session State 초기화 (데이터 기억하기)
# ==========================================

# 🌟 오답 노트 불러오기 및 데이터 구조 업그레이드
if 'wrong_vocab' not in st.session_state:
    raw_wrong = load_data(WRONG_FILE)
    upgraded_wrong = {}
    
    for word, data in raw_wrong.items():
        # 예전 방식 데이터(문자열)라면 횟수(count)를 1로 만들어서 구조 변경
        if not isinstance(data, dict):
            upgraded_wrong[word] = {"meaning": data, "count": 1}
        else:
            upgraded_wrong[word] = data
            
    st.session_state['wrong_vocab'] = upgraded_wrong

# 현재 출제된 퀴즈 단어 기억하기
if 'current_quiz' not in st.session_state:
    st.session_state['current_quiz'] = None
if 'score' not in st.session_state:
    st.session_state['score']=0
if 'current_wrong_quiz' not in st.session_state:
    st.session_state['current_wrong_quiz'] = None


# ==========================================
# 4. UI 화면 구성 시작
# ==========================================

# 탭 메뉴 생성
tab1, tab2, tab3, tab4, tab5= st.tabs([" 단어 추가", " 랜덤 퀴즈", "오답 노트", "📚 전체 목록", "단어 삭제"])

# ------------------------------------------
# [탭 1] 새 단어 추가 로직 (엑셀 업로드 포함)
# ------------------------------------------
with tab1:
    st.header("새 단어 추가하기")
    
    # --- 1. 직접 하나씩 입력하는 부분 ---
    st.subheader("직접 추가")
    col1, col2 = st.columns(2)
    
    with col1:
        new_eng = st.text_input("영어 단어 (English):", key="input_eng")
    with col2:
        new_kor = st.text_input("한글 뜻 (Korean):", key="input_kor")
        
    if st.button("한 개씩 저장하기", use_container_width=True):
        if new_eng and new_kor:
            st.session_state['vocab'][new_eng] = new_kor
            save_data(st.session_state['vocab'], VOCAB_FILE)
            st.success(f"'{new_eng}' 단어가 성공적으로 저장되었습니다!")
        else:
            st.warning("영어와 한글 뜻을 모두 입력해 주세요.")
            
    st.divider() # 가로 줄 긋기
    
    # --- 🌟 2. 엑셀 파일로 대량 추가하는 부분 ---
    st.subheader("2. 엑셀 파일로 한 번에 대량 추가")
    st.info("엑셀 파일 형식 가이드: A열에는 '영어 단어', B열에는 '한글 뜻'을 적어주세요. (첫 번째 줄은 제목으로 간주하고 무시합니다)")
    
    # Streamlit의 파일 업로드 위젯
    uploaded_file = st.file_uploader("단어장 엑셀 파일(.xlsx)을 업로드하세요.", type=["xlsx"])
    
    # 파일이 정상적으로 업로드 되었다면
    if uploaded_file is not None:
        if st.button("엑셀 데이터 단어장에 넣기", type="primary"):
            try:
                # pandas를 사용해 엑셀 파일 읽기 (첫 줄은 제목(header)으로 간주)
                df = pd.read_excel(uploaded_file)
                
                added_count = 0 # 몇 개나 추가했는지 세는 카운터
                
                # 엑셀의 모든 줄을 반복하면서 단어장에 추가
                for index, row in df.iterrows():
                    # 엑셀 칸이 비어있지 않은지 확인
                    if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        eng_word = str(row.iloc[0]).strip()
                        kor_word = str(row.iloc[1]).strip()
                        
                        st.session_state['vocab'][eng_word] = kor_word
                        added_count += 1
                        
                # 단어장에 모두 넣은 후 JSON 파일로 덮어쓰기 저장
                save_data(st.session_state['vocab'], VOCAB_FILE)
                
                st.success(f"엑셀 파일에서 총 {added_count}개의 단어를 성공적으로 추가했습니다!")
                
            except Exception as e:
                st.error(f"⚠️ 에러 발생! 상세 내용: {e}")

with tab2:
    st.header("랜덤 단어 퀴즈")
    st.metric("score =",st.session_state['score'])
    
    if st.button("새로운 문제 뽑기 "):
        if len(st.session_state['vocab']) > 0:
            words = list(st.session_state['vocab'].keys())
            st.session_state['current_quiz'] = random.choice(words)
        else:
            st.error("저장된 단어가 없습니다. 단어를 먼저 추가해 주세요.")
            
    st.divider()
    
   
    if st.session_state['current_quiz']:
        quiz_word = st.session_state['current_quiz']
        st.info(f"### Q. '{quiz_word}' 의 뜻은 무엇일까요?")
        
        user_answer = st.text_input("정답 입력:", key="quiz_answer")
        
        if st.button("정답 확인하기"):
            correct_answer = st.session_state['vocab'][quiz_word]
            
            if user_answer == correct_answer:
                st.session_state['score']=st.session_state['score']+1
                st.success("정답입니다!  완벽해요!")
                st.session_state['current_quiz'] = None
            else:
                st.error(f"틀렸습니다! ❌ 정답은 **{correct_answer}** 입니다.")
                
                # 🌟 오답 횟수 누적 로직
                if quiz_word in st.session_state['wrong_vocab']:
                    st.session_state['wrong_vocab'][quiz_word]['count'] += 1
                else:
                    st.session_state['wrong_vocab'][quiz_word] = {"meaning": correct_answer, "count": 1}
                    
                save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                st.warning("이 단어는 '오답 노트'에 기록되었습니다.")
                st.session_state['current_quiz'] = None # 오답일 때도 즉시 종료
          

with tab3:
    # ------------------------------------------
# [탭 3] 오답 노트 복습 (우선순위 알고리즘 적용)
# ------------------------------------------
    st.header("📝 오답 노트 복습")
    
    if len(st.session_state['wrong_vocab']) == 0:
        st.success("오답 노트가 비어있습니다. 모든 단어를 다 외우셨군요! 💯")
    else:
        # 🌟 1. 3회 이상 틀린 '요주의 단어' 분석 및 표(Table) 출력
        hard_words = []
        for eng, data in st.session_state['wrong_vocab'].items():
            if data['count'] >= 3:
                hard_words.append({"영어": eng, "한글": data['meaning'], "틀린 횟수": f"🚨 {data['count']}회"})
        
        if hard_words:
            st.subheader("⚠️ 집중 복습이 필요한 단어 (3회 이상 틀림)")
            st.dataframe(hard_words, use_container_width=True)
            st.divider()

        # 🌟 2. 오답 문제 출제 로직 (우선순위 출제)
        if st.button("오답 문제 뽑기"):
            # 단어를 3번 이상 틀린 그룹과 그 미만 그룹으로 나눕니다.
            priority_words = [w for w, d in st.session_state['wrong_vocab'].items() if d['count'] >= 3]
            normal_words = [w for w, d in st.session_state['wrong_vocab'].items() if d['count'] < 3]
            
            # 요주의 단어가 1개라도 있다면 무조건 우선 출제!
            if priority_words:
                st.session_state['current_wrong_quiz'] = random.choice(priority_words)
                st.toast("🚨 주의! 자주 틀렸던 단어가 우선 출제되었습니다.") # 우측 하단 알림창
            else:
                st.session_state['current_wrong_quiz'] = random.choice(normal_words)
                
        # 3. 오답 퀴즈 진행 화면
        if st.session_state['current_wrong_quiz']:
            wrong_quiz_word = st.session_state['current_wrong_quiz']
            word_data = st.session_state['wrong_vocab'][wrong_quiz_word]
            wrong_correct = word_data['meaning']
            wrong_count = word_data['count']
            
            st.error(f"### Q.'{wrong_quiz_word}' 의 뜻은?")
            
            wrong_user_answer = st.text_input("정답 입력:", key="wrong_quiz_answer")
            
            if st.button("오답 정답 확인"):
                if wrong_user_answer == wrong_correct:
                    st.success("드디어 맞히셨네요! 오답 노트에서 완전히 삭제합니다. 👏")
                    del st.session_state['wrong_vocab'][wrong_quiz_word]
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    st.session_state['current_wrong_quiz'] = None
                else:
                    st.error(f"또 틀렸네요 정답은 **{wrong_correct}** 입니다.")
                    # 또 틀렸으므로 오답 횟수 +1
                    st.session_state['wrong_vocab'][wrong_quiz_word]['count'] += 1
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    st.session_state['current_wrong_quiz'] = None
# ------------------------------------------
# [탭 4] 전체 단어 목록 & 사이드바 통계
# ------------------------------------------
with tab4:
    st.header("전체 단어 목록")
    # 딕셔너리를 예쁜 표(데이터프레임) 형태로 보여줍니다.
    st.dataframe(
        [{"영어": eng, "한글": kor} for eng, kor in st.session_state['vocab'].items()],
        use_container_width=True
    )

with st.sidebar:
    st.subheader("내 학습 현황")
    st.metric(label="총 저장된 단어", value=f"{len(st.session_state['vocab'])} 개")
    st.metric(label="오답 노트 대기열", value=f"{len(st.session_state['wrong_vocab'])} 개")
    st.caption("프로그램을 종료해도 단어는 안전하게 저장됩니다.")



with tab5:
   # ------------------------------------------
# [탭 5] 전체 단어 목록 & 단어 삭제 관리
# ------------------------------------------
    st.header("전체 단어 목록 및 관리")
    
    # 단어장이 비어있지 않을 때만 표와 삭제 기능을 보여줌
    if len(st.session_state['vocab']) > 0:
        
        st.dataframe(
            [{"영어": eng, "한글": kor} for eng, kor in st.session_state['vocab'].items()],
            use_container_width=True
        )
        
        st.divider() # 가로 줄 긋기
        
        st.subheader("️ 단어 삭제하기")
        
        # 현재 저장된 단어들의 목록(리스트) 가져오기
        words_list = list(st.session_state['vocab'].keys())
        
        # 🌟 이 줄이 꼭 있어야 컴퓨터가 delete_target이 뭔지 알 수 있습니다!
        delete_target = st.selectbox("삭제할 단어를 선택하세요:", words_list)
        
        # 버튼을 누르면 삭제 로직 실행
        if st.button("선택한 단어 삭제"):
            
            # 안전장치: delete_target이 비어있지 않고, 단어장 안에 있을 때만 삭제
            if delete_target and delete_target in st.session_state['vocab']:
                
                # 1) 전체 단어장에서 삭제
                del st.session_state['vocab'][delete_target]
                save_data(st.session_state['vocab'], VOCAB_FILE)
                
                # 2) 오답 노트에도 있다면 삭제
                if delete_target in st.session_state['wrong_vocab']:
                    del st.session_state['wrong_vocab'][delete_target]
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    
                st.success(f"'{delete_target}' 단어가 성공적으로 삭제되었습니다! 🗑️")
                
                # 화면 새로고침
                st.rerun() 
            else:
                st.warning("이미 삭제되었거나 선택된 단어가 없습니다.")
                
    else:
        st.info("현재 저장된 단어가 없습니다. 단어를 먼저 추가해 주세요.")    
