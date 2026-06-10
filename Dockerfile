# Estágio 1 - Build
FROM python:3.11-alpine AS builder

WORKDIR /app

# Instala dependências de sistema necessárias para compilar pacotes no Alpine
RUN apk add --no-cache gcc g++ musl-dev linux-headers

# Cria o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 2 - Runtime
FROM python:3.11-alpine

WORKDIR /app

# Copia o ambiente virtual do estágio de build
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o restante do código do repositório
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando corrigido para rodar o Streamlit na porta e endereço corretos
CMD ["streamlit", "run", "consume_api/interface_main.py", "--server.port=8501", "--server.address=0.0.0.0"]