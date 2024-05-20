import os
import streamlit as st
import docx
import fitz
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


ENDPOINT = os.getenv('AZURE_PROXY_ENDPOINT')
API_KEY = os.getenv('AZURE_API_KEY')

API_VERSION = "2024-02-01"
MODEL_NAME = "gpt-35-turbo"


class Conversation:
    client = AzureOpenAI(
        azure_endpoint=ENDPOINT,
        api_key=API_KEY,
        api_version=API_VERSION
    )

    def __init__(self):
        self.text = None

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

    def extract_text_from_file(self, uploaded_file):
        file_type = uploaded_file.type

        if file_type == "text/plain":
            # Handle TXT file
            text = uploaded_file.read().decode("utf-8")
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Handle DOCX file
            doc = docx.Document(uploaded_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file_type == "application/pdf":
            # Handle PDF file
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text("text")
        else:
            text = "Unsupported file type."

        self.text = text


if __name__ == '__main__':
    st.title('Chatbot')
    conversation = Conversation()
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        conversation.extract_text_from_file(uploaded_file)
        st.session_state.message_list = [
            {
                'role': 'system',
                'content': f"""
                    You are a helpful chat assistant. Please provide a discussion around this document. 
                    {conversation.text}
                """
            }
        ]
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
