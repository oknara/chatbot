import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="GPT-4o-mini 챗봇", page_icon="💬")
st.title("💬 GPT-4o-mini 챗봇")
st.caption("OpenAI API를 활용한 Streamlit 챗봇입니다.")

MODEL = "gpt-4o-mini"

# ─────────────────────────────────────────────
# API 키 로드
# Streamlit Community Cloud의 Secrets에 OPENAI_API_KEY 등록 필요
# (앱 설정 > Secrets 에서 OPENAI_API_KEY = "sk-..." 형식으로 입력)
# ─────────────────────────────────────────────
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "Streamlit Community Cloud의 Secrets에 키를 등록해주세요."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# ─────────────────────────────────────────────
# 사이드바 옵션
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    system_prompt = st.text_area(
        "System Prompt",
        value="당신은 친절하고 도움이 되는 AI 어시스턴트입니다.",
        height=100,
    )
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────
# 대화 기록 초기화
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────────
# 사용자 입력 처리
# ─────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 어시스턴트 응답 생성 (스트리밍)
    with st.chat_message("assistant"):
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages += [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                temperature=temperature,
                stream=True,
            )
            response = st.write_stream(stream)
        except Exception as e:
            response = f"오류가 발생했습니다: {e}"
            st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
