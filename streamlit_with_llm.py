import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


ENDPOINT = os.getenv('AZURE_PROXY_ENDPOINT')
API_KEY = os.getenv('AZURE_API_KEY')

API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-35-turbo"


if 'message_list' not in st.session_state:
    st.session_state.message_list = [
        {'role': 'system', 'content': 'You are a helpful chat assistant. Provide short responses if possible'}
    ]


class Conversation:
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )

    def __init__(self):
        pass

    def message(self, question):
        q = {
            "role": "user",
            "content": question
        }
        st.session_state.message_list.append(q)
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=st.session_state.message_list,
        )
        a = {
            'role': 'assistant',
            'content': response.choices[0].message.content
        }
        st.session_state.message_list.append(a)

        return response.choices[0].message.content


if __name__ == '__main__':
    st.title('Chatbot')
    conversation = Conversation()
    prompt = st.chat_input('Ask a question')
    if prompt:
        answer = conversation.message(prompt)
        for msg in st.session_state.message_list:
            if msg['role'] == 'user':
                with st.chat_message('user'):
                    st.write(msg['content'])
            elif msg['role'] == 'assistant':
                with st.chat_message('assistant'):
                    st.write(msg['content'])
