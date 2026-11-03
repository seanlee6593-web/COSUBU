import streamlit as st
import json
import os
import random
import pandas as pd

st.set_page_config(page_title="스마트 영단어장", layout="centered")

VOCAB_FILE = "vocabulary.json"
WRONG_FILE = "wrong_words.json"

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

if 'vocab' not in st.session_state:
    st.session_state['vocab'] = load_data(VOCAB_FILE)

if 'wrong_vocab' not in st.session_state:
    raw_wrong = load_data(WRONG_FILE)
    upgraded_wrong = {}
    
    for word, data in raw_wrong.items():

        if not isinstance(data, dict):
            upgraded_wrong[word] = {"meaning": data, "count": 1}
        else:
            upgraded_wrong[word] = data
            
    st.session_state['wrong_vocab'] = upgraded_wrong


if 'current_quiz' not in st.session_state:
    st.session_state['current_quiz'] = None
if 'score' not in st.session_state:
    st.session_state['score']=0
if 'current_wrong_quiz' not in st.session_state:
    st.session_state['current_wrong_quiz'] = None





tab1, tab2, tab3, tab4, tab5= st.tabs([" 단어 추가", " 랜덤 퀴즈", "오답 노트", "전체 목록", "단어 삭제"])


with tab1:
    st.header("새 단어 추가하기")
    
  
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
            
    st.divider()
    
   
    st.subheader("2. 엑셀 파일로 한 번에 대량 추가")
    st.info("엑셀 파일 형식 가이드: A열에는 '영어 단어', B열에는 '한글 뜻'을 적어주세요. (첫 번째 줄은 제목으로 간주하고 무시합니다)")
    

    uploaded_file = st.file_uploader("단어장 엑셀 파일(.xlsx)을 업로드하세요.", type=["xlsx"])
    
    if uploaded_file is not None:
        if st.button("엑셀 데이터 단어장에 넣기", type="primary"):
            try:
                
                df = pd.read_excel(uploaded_file)
                
                added_count = 0 
                
              
                for index, row in df.iterrows():
            
                    if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                        eng_word = str(row.iloc[0]).strip()
                        kor_word = str(row.iloc[1]).strip()
                        
                        st.session_state['vocab'][eng_word] = kor_word
                        added_count += 1
                        
        
                save_data(st.session_state['vocab'], VOCAB_FILE)
                
                st.success(f"엑셀 파일에서 총 {added_count}개의 단어를 성공적으로 추가했습니다.")
                
            except Exception as e:
                st.error(f"오류 발생  상세 내용: {e}")

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
                st.success("정답입니다!")
                st.session_state['current_quiz'] = None
            else:
                st.error(f"틀렸습니다! 정답은 **{correct_answer}** 입니다.")
                
                if quiz_word in st.session_state['wrong_vocab']:
                    st.session_state['wrong_vocab'][quiz_word]['count'] += 1
                else:
                    st.session_state['wrong_vocab'][quiz_word] = {"meaning": correct_answer, "count": 1}
                    
                save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                st.warning("이 단어는 '오답 노트'에 기록되었습니다.")
                st.session_state['current_quiz'] = None 
          

with tab3:
 
    st.header("오답 노트 복습")
    
    if len(st.session_state['wrong_vocab']) == 0:
        st.success("오답 노트가 비어있습니다.")
    else:
   
        hard_words = []
        for eng, data in st.session_state['wrong_vocab'].items():
            if data['count'] >= 3:
                hard_words.append({"영어": eng, "한글": data['meaning'], "틀린 횟수": f"🚨 {data['count']}회"})
        
        if hard_words:
            st.subheader("집중 복습이 필요한 단어 (3회 이상 틀림)")
            st.dataframe(hard_words, use_container_width=True)
            st.divider()

     
        if st.button("오답 문제 뽑기"):
        
            priority_words = [w for w, d in st.session_state['wrong_vocab'].items() if d['count'] >= 3]
            normal_words = [w for w, d in st.session_state['wrong_vocab'].items() if d['count'] < 3]
            
           
            if priority_words:
                st.session_state['current_wrong_quiz'] = random.choice(priority_words)
            else:
                st.session_state['current_wrong_quiz'] = random.choice(normal_words)
                
 
        if st.session_state['current_wrong_quiz']:
            wrong_quiz_word = st.session_state['current_wrong_quiz']
            word_data = st.session_state['wrong_vocab'][wrong_quiz_word]
            wrong_correct = word_data['meaning']
            wrong_count = word_data['count']
            
            st.error(f"### Q.'{wrong_quiz_word}' 의 뜻은?")
            
            wrong_user_answer = st.text_input("정답 입력:", key="wrong_quiz_answer")
            
            if st.button("오답 정답 확인"):
                if wrong_user_answer == wrong_correct:
                    st.success("정답입니다! 오답 노트에서 완전히 삭제합니다.")
                    del st.session_state['wrong_vocab'][wrong_quiz_word]
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    st.session_state['current_wrong_quiz'] = None
                else:
                    st.error(f"틀렸습니다! 정답은 **{wrong_correct}** 입니다.")
                    st.session_state['wrong_vocab'][wrong_quiz_word]['count'] += 1
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    st.session_state['current_wrong_quiz'] = None

with tab4:
    st.header("전체 단어 목록")
  
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

    st.header("전체 단어 목록 및 관리")
    
    if len(st.session_state['vocab']) > 0:
        
        st.dataframe(
            [{"영어": eng, "한글": kor} for eng, kor in st.session_state['vocab'].items()],
            use_container_width=True
        )
        
        st.divider()
        st.subheader("단어 삭제하기")
        
       
        words_list = list(st.session_state['vocab'].keys())
        
        
        delete_target = st.selectbox("삭제할 단어를 선택하세요:", words_list)
        
     
        if st.button("선택한 단어 삭제"):
            
         
            if delete_target and delete_target in st.session_state['vocab']:
                
        
                del st.session_state['vocab'][delete_target]
                save_data(st.session_state['vocab'], VOCAB_FILE)
                
              
                if delete_target in st.session_state['wrong_vocab']:
                    del st.session_state['wrong_vocab'][delete_target]
                    save_data(st.session_state['wrong_vocab'], WRONG_FILE)
                    
                st.success(f"'{delete_target}' 단어가 성공적으로 삭제되었습니다.")
                
                st.rerun() 
            else:
                st.warning("이미 삭제되었거나 선택된 단어가 없습니다.")
                
    else:
        st.info("현재 저장된 단어가 없습니다. 단어를 먼저 추가해 주세요.")       
