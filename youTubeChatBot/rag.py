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
