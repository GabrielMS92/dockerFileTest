# rag_core.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import PGVector
from dotenv import load_dotenv
from pydantic import SecretStr
import os

load_dotenv()


def _get_google_api_key():
    raw_api = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("CHAVE_API_GOOGLE")
    )
    return SecretStr(raw_api) if raw_api else None


def criar_rag_chain():
    """
    Cria e retorna uma cadeia RAG pronta para uso com PostgreSQL.
    Usa dados já existentes no banco de dados.
    """

    # 1. Criar modelo de embeddings (só para busca, não para inserir)
    api_key = _get_google_api_key()
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2",
        api_key=api_key
    )

    # 2. Conectar ao PostgreSQL existente (não apaga nada!)
    connection_string = "postgresql://postgres:senha123@localhost:5432/rag_db"

    vectorstore = PGVector(
        connection_string=connection_string,
        embedding_function=embedding_model,
        collection_name='documentos'
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # 3. Criar LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.4
    )

    # 4. Montar prompt e cadeia
    template = """
Você é um assistente homem, gentil e útil da empresa TechVision Solutions, chamado Ulos.
Responda com base nas informações a seguir.
Se não houver dados suficientes, explique isso de forma educada e tente dar um contexto útil.

Contexto:
{context}

Pergunta: {question}

Resposta:
"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain
