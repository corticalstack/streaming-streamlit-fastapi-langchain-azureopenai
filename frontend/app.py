import streamlit as st
import requests

URL = "http://localhost:8000/chat"

st.title("🤖 Q&A Ask The Bot")
st.subheader("Powered by Streamlit + FastAPI + LangChain + Azure OpenAI")

llm_completion = ""

system_message = st.text_input(
    "System Prompt", value="Assume the role of a friendly advisor"
)
human_message = st.text_input(
    "Ask a Question", value="Prepare a 5-point marketing strategy for a new product"
)

if st.button("Get Answer"):
    result_container = st.empty()
    with requests.post(
        URL,
        params={"system_message": system_message, "human_message": human_message},
        stream=True,
    ) as r:
        for chunk in r.iter_content(None, decode_unicode=True):
            if chunk:
                llm_completion = llm_completion + str(chunk.decode("utf-8"))
                result_container.markdown(f"{llm_completion}")
