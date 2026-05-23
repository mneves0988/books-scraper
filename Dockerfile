# syntax=docker/dockerfile:1

# ── Estágio 1: build ──────────────────────────────────────────────────────────
# Usa imagem completa para instalar dependências
FROM python:3.12-slim AS builder

# Diretório de trabalho
WORKDIR /app

# Copia apenas o requirements primeiro (aproveita cache do Docker)
COPY requirements.txt .

# Instala as dependências no diretório /install
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── Estágio 2: runtime ────────────────────────────────────────────────────────
# Imagem final leve, sem ferramentas de build
FROM python:3.12-slim AS runtime

# Cria usuário não-root por segurança
RUN useradd --create-home appuser

# Diretório de trabalho
WORKDIR /app

# Copia as dependências instaladas do estágio de build
COPY --from=builder /install /usr/local

# Copia o código do projeto
COPY scraper/ ./scraper/
COPY requirements.txt .

# Cria a pasta de output e dá permissão ao usuário
RUN mkdir -p /app/output && chown -R appuser:appuser /app

# Troca para usuário não-root
USER appuser

# Porta padrão (boa prática documentar mesmo sem servidor HTTP)
EXPOSE 8080

# Comando padrão
CMD ["python", "-m", "scraper.main"]