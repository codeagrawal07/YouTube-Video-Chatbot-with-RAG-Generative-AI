from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

# Helper to format docs for retriever

def format_docs(retrieved_context):
    return "\n\n".join(doc.page_content for doc in retrieved_context)


# Build LangChain pipeline

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
