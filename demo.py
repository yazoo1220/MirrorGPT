"""Python file to serve as the frontend"""
import streamlit as st
from streamlit_chat import message
import os
import tempfile

st.set_page_config(page_title="MirrorGPT", page_icon=":robot:")
st.header("MirrorGPT")
if "generated" not in st.session_state:
    st.session_state["generated"] = []
    
st.caption("NB!:this is currently beta version and only knows about 'schedulers' part of Calabrio.")
st.caption("https://help.calabrio.com/doc/Content/web/roles-scheduler.htm")
is_gpt4 = st.checkbox('Enable GPT4',help="With this it might get slower")

if "past" not in st.session_state:
    st.session_state["past"] = []

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone

import pinecone 

# initialize pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment="us-east1-gcp"  # next to api key in console
)

def get_chat_history(inputs) -> str:
    res = []
    for human, ai in inputs:
        res.append(f"Human:{human}\nAI:{ai}")
    return "\n".join(res)
@st.cache_resource
def create_qa():
    if is_gpt4:
        model = "gpt-4"
    else:
        model = "gpt-3.5-turbo"
    llm = ChatOpenAI(temperature=0.9, model_name=model, streaming=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), verbose=True)
    embeddings = OpenAIEmbeddings()
#     index_name = os.getenv("PINECONE_INDEX_NAME")
    db = Pinecone.from_existing_index(index_name='fb',embedding=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 1})
    qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever,get_chat_history=get_chat_history)
    return qa
qa = create_qa()
    
def get_text():
    input_text = st.text_input("💬 You: ", "describe yourself", key="input")
    return input_text


user_input = get_text()
ask_button = st.button('ask')

if ask_button:
    with st.spinner('typing...'):
        prefix = 'you are Yasu and play a role based on the document you received. That is his Facebook page and you answer questions just like he talks. The answers should be in Japanese'
        chat_history = []
        st.session_state.past.append(prefix+user_input)
        st.session_state.generated.append(qa({"question": user_input, "chat_history": chat_history})['answer'])
#         user_input.value = ""

if st.session_state["generated"]:

    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        try:
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
        except:
            pass
