import psycopg2
from psycopg2.extras import execute_values
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from consume_api.insert_data_in_database.make_chunks import carregar_e_dividir_chunks
from dotenv import load_dotenv
import os
from pydantic import SecretStr
import json
from loguru import logger

# PGPASSWORD=senha123 psql -h localhost -U postgres -d rag_db

load_dotenv()
raw_api = os.getenv("CHAVE_API_GOOGLE")
api_key = SecretStr(raw_api) if raw_api else None

# to me connect aqui ao database postgresql
logger.info("🔌 Conectando ao PostgreSQL...")
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="rag_db",
    user="postgres",
    password="senha123"
)
cur = conn.cursor()
logger.success("✅ Conexão estabelecida!")


logger.info("\n📄 Carregando chunks do arquivo...")
chunks = carregar_e_dividir_chunks("data_example/wiki_nexus_monitor.txt")
logger.success(f"✅ {len(chunks)} chunks carregados")


embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    api_key=api_key
)
logger.success("✅ Modelo de embeddings criado!")


embeddings = []
for i, chunk in enumerate(chunks):
    embedding = embedding_model.embed_query(chunk.page_content)
    embeddings.append(embedding)
logger.success(f"\n✅ {len(embeddings)} embeddings gerados!")

# Preparar dados para inserção
dados = []
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    metadata_dict = {"source": "wiki"}  # ← Dicionário Python
    metadata_json = json.dumps(metadata_dict)  # ← Converter para string JSON
    dados.append((
        "wiki_nexus_monitor.txt",
        chunk.page_content,
        i,
        "SEÇÃO_DESCONHECIDA",
        embedding,
        metadata_json  # ← Agora é string JSON, não dict
    ))
logger.success("✅ Dados preparados!")

# Inserir dados na tabela
logger.info("\n💾 Inserindo dados no banco...")
execute_values(
    cur,
    """
    INSERT INTO documentos
    (document_id, chunk_text, chunk_index, section, embedding, metadata)
    VALUES %s
    """,
    dados
)
conn.commit()
logger.success(f"✅ {len(dados)} registros inseridos!")

# Fechar conexão
cur.close()
conn.close()
logger.info("\n👋 Conexão fechada!")
