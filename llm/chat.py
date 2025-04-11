import streamlit as st
import utils.llm_utils as llm

# Check if API key exists in session state
if "api_key" not in st.session_state or not st.session_state.api_key:
    llm.get_api_key()
    st.error("No API key provided. Reload the page.")

# Rest of your app
if ("api_key" in st.session_state and st.session_state.api_key):
    llm.llm_connect()
    if "llm_conn" not in st.session_state and st.session_state.llm_conn:
        st.error("Connection to Mistral AI failed. Reload the page.")
    else:
        if "history" not in st.session_state:
            st.session_state.history = []

        st.warning("[BETA] This AI chatbot is powered by mistral.ai and public crime and census \
            data. Answers may be inaccurate, inefficient, or biased. Any use or decisions based \
            on such answers should include reasonable practices including human oversight to \
            ensure they are safe, accurate, and suitable for your intended purpose. Interactive \
            Crime Maps is not liable for any actions, losses, or damages resulting from the use \
            of the chatbot. Do not enter any private, sensitive, personal, or regulated data. \
            By using this chatbot, you acknowledge and agree that input you provide and answers \
            you receive (collectively, “Content”) may be used by Interactive Crime Maps and \
            mistral.ai to provide, maintain, develop, and improve their respective offerings.")
        for i, message in enumerate(st.session_state.history):
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prompt = st.chat_input("Ask anything about crimes in England, Wales, and Northern Ireland")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)
            st.session_state.history.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                response_llm = llm.llm_query(st.session_state.history)
                response = st.write_stream(llm.chat_stream(response_llm))
            st.session_state.history.append({"role": "assistant", "content": response})
