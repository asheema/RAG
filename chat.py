import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# Load .env and OpenAI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Set up Streamlit app
st.set_page_config(page_title="📄 RAG PDF Chatbot", layout="wide")
st.title("📄💬 Chat with Your PDF (RAG)")

# Initialize session state for chat history and QA chain
if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# Upload PDF
uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_pdf and st.session_state.qa_chain is None:
    with st.spinner("🔍 Processing PDF and creating knowledge base..."):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_pdf.read())
            tmp_path = tmp_file.name

        # Load PDF
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # Split text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = text_splitter.split_documents(documents)

        # Create vector DB
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(docs, embeddings)

        # Build RAG QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )

        st.session_state.qa_chain = qa_chain
        st.success("✅ PDF indexed! You can start chatting now.")

# If QA chain is ready, show the chat interface
if st.session_state.qa_chain:

    # Chat input box
    user_input = st.chat_input("Ask something about the PDF")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("🤖 Thinking..."):
            result = st.session_state.qa_chain(user_input)
            answer = result["result"]

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
