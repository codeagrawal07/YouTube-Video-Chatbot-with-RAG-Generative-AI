import streamlit as st
from dotenv import load_dotenv
import YouTubeTranscript as ytscript
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

load_dotenv()

st.set_page_config(page_title="YouTube Video Chatbot", layout="wide")

st.title("🎬 Chat with YouTube Video")

# Helper to format docs for retriever
def format_docs(retrieved_context):
    return "\n\n".join(doc.page_content for doc in retrieved_context)

# Build your LangChain pipeline
def build_chain(transcript):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunk = splitter.create_documents([transcript])
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma.from_documents(chunk, embedding, persist_directory="./Database_db")
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":3})
    llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
    parser = StrOutputParser()
    prompt = PromptTemplate(
        template=(
            "You are a helpful assistant.\n"
            "Answer ONLY from the provided transcript context.\n"
            "If the context is insufficient, just say you don't know.\n\n"
            "{context}\n\nQuestion: {question}"
        ), 
        input_variables=['context', 'question']
    )
    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })
    main_chain = parallel_chain | prompt | llm | parser
    return main_chain

# Sidebar: Input video URL and fetch transcript
with st.sidebar:
    st.header("Load YouTube Transcript")
    youtube_url = st.text_input("Enter YouTube URL", key="sidebar_url")
    if st.button("Load Transcript"):
        with st.spinner("Fetching transcript..."):
            transcript = ytscript.extract_transcript_details(youtube_url)
            if transcript:
                st.session_state["main_chain"] = build_chain(transcript)
                st.session_state["messages"] = []
                st.session_state["transcript_loaded"] = True
                st.success("Transcript loaded! You may start chatting below.")
            else:
                st.error("Failed to fetch transcript. Check the URL.")
    add_vertical_space(5)
    st.write('Made with ❤️ by ABHISHEK AGRAWAL')
    add_vertical_space(3)
    linkedin_url = "https://www.linkedin.com/in/abhishek07122002//"  
    st.markdown(
    f"""
    <a href="{linkedin_url}" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" 
             width="50" height="50">
    </a>
    """,
    unsafe_allow_html=True
)          

# Initialize or check session_state variables    
if "main_chain" not in st.session_state:
    st.session_state["main_chain"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "transcript_loaded" not in st.session_state:
    st.session_state["transcript_loaded"] = False

# Main chat window UI
if st.session_state["transcript_loaded"]:
    colored_header('💬 ChatBot Conversation', '', 'green-50')
    add_vertical_space(1)

    # Display previous messages from session state as a chat
    for chat in st.session_state["messages"]:
        message(chat['user'], is_user=True)
        message(chat['ai'], is_user=False)

    # User input field
    user_input = st.text_input("Type your message...", key="user_input")
    if st.button("Send"):
        if user_input:
            with st.spinner("AI is thinking..."):
                try:
                    answer = st.session_state["main_chain"].invoke(user_input)
                except Exception as e:
                    answer = "Sorry, an error occurred: " + str(e)
            # Save the chat to state
            st.session_state["messages"].append({"user": user_input, "ai": answer})
            st.rerun()  # Refresh for updated chat display

else:
    st.info("Enter a YouTube video URL on the sidebar and load transcript to start chatting.")
