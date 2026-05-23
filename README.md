# 📚 Books Scraper

Scraper automatizado do site [books.toscrape.com](http://books.toscrape.com) desenvolvido como desafio técnico para o Programa Trainee Crawler/RPA & IA.

Coleta dados de 1000 livros, enriquece as descrições com IA (OpenAI) e persiste os dados em JSON, CSV e PostgreSQL.

---

## 🚀 Como rodar localmente

### Sem Docker

**Pré-requisitos:** Python 3.12+

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd books-scraper

# Instale as dependências
pip install -r requirements.txt

# Configure a chave da OpenAI
export OPENAI_API_KEY="sua-chave-aqui"

# Rode o scraper
python -m scraper.main
```

Os arquivos serão salvos em `output/books.json` e `output/books.csv`.

### Com Docker

```bash
# Build da imagem
docker build -t books-scraper .

# Rode o container
docker run --rm \
  -e OPENAI_API_KEY="sua-chave-aqui" \
  -v $(pwd)/output:/app/output \
  books-scraper
```

### Com Docker Compose (scraper + PostgreSQL)

```bash
# Configure a chave da OpenAI no ambiente
export OPENAI_API_KEY="sua-chave-aqui"

# Sobe os serviços
docker-compose up --build
```

O scraper aguarda o PostgreSQL estar saudável antes de iniciar. Os dados são persistidos no volume `postgres_data`.

---

## 📊 Estrutura dos dados extraídos

### Schema JSON / CSV

| Campo | Tipo | Descrição |
|---|---|---|
| `title` | string | Título completo do livro |
| `price` | float | Preço em libras (sem símbolo) |
| `rating` | integer | Avaliação de 1 a 5 |
| `availability` | string | Disponibilidade (ex: "In stock") |
| `url` | string | URL da página de detalhe |
| `description` | string | Descrição limpa extraída via IA |
| `genre` | string | Gênero inferido pela IA (ex: Fiction, Thriller) |
| `target_audience` | string | Público-alvo inferido pela IA (ex: Adult, Young Adult) |

### Exemplo de registro

```json
{
  "title": "Scott Pilgrim's Precious Little Life",
  "price": 52.29,
  "rating": 5,
  "availability": "In stock",
  "url": "http://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life_987/index.html",
  "description": "Scott Pilgrim's life is totally sweet. He's 23 years old, in a band, and dating a cute high school girl.",
  "genre": "Graphic Novel",
  "target_audience": "Young Adult"
}
```

---

## ⚙️ Como o pipeline funciona

O pipeline GitLab CI/CD é definido em `.gitlab-ci.yml` e possui 4 stages:

**lint** — Roda o `flake8` no código Python com limite de 120 caracteres por linha. O job falha se houver erros de estilo ou qualidade.

**test** — Roda os testes unitários com `pytest`. O job falha se qualquer teste quebrar. Os testes cobrem as funções de parsing isoladamente, sem necessidade de internet.

**build** — Builda a imagem Docker e faz push para o GitLab Container Registry. Usa variáveis automáticas do GitLab (`$CI_REGISTRY_IMAGE`, `$CI_COMMIT_SHORT_SHA`) para tagear a imagem com o hash do commit.

**deploy** — Simula o deploy no AWS ECS com os comandos `aws ecs update-service`. Roda **apenas na branch `main`** para evitar deploys acidentais.

O pipeline usa cache de dependências pip entre execuções para acelerar os builds.

---

## 🧠 Decisões técnicas

**Python em vez de Go**
O desafio sugeria Go, mas optei por Python por ter ecossistema mais maduro para scraping (`requests` + `BeautifulSoup`) e integração trivial com APIs de IA. Para o volume de dados deste desafio (1000 livros), a diferença de performance é irrelevante. Go seria vantagem em scraping de alta escala.

**Separação de responsabilidades**
O código foi dividido em módulos com responsabilidades claras: `parser.py` (extração), `ai_enricher.py` (enriquecimento com IA), `saver.py` (persistência) e `main.py` (orquestração). Isso facilita testes unitários e manutenção.

**IA para limpeza e enriquecimento**
O site `books.toscrape.com` duplica o texto das descrições no HTML. Em vez de usar heurísticas frágeis para detectar a duplicação, optei por usar a OpenAI (`gpt-4o-mini`) para limpar o texto e extrair informações estruturadas (gênero e público-alvo) simultaneamente. O modelo `gpt-4o-mini` foi escolhido pelo custo baixo e velocidade.

**Fallback em caso de erro da IA**
Se a API da OpenAI falhar ou retornar JSON inválido, o sistema usa a descrição crua como fallback em vez de travar. Isso garante que o scraper complete mesmo com falhas pontuais.

**PostgreSQL via docker-compose**
O banco de dados só é ativado quando a variável `POSTGRES_HOST` está definida, mantendo o scraper funcional localmente sem Docker.

**Delay entre requisições**
1 segundo de delay entre cada requisição para respeitar o servidor, conforme as regras do desafio.

---

## 🔮 O que faria diferente com mais tempo

**Scraping**
- Concorrência com `asyncio` + `aiohttp` para reduzir o tempo de coleta de ~20 minutos para ~2 minutos
- Retry automático com backoff exponencial para requisições que falham
- Detecção de mudanças no site para reprocessar apenas livros novos ou alterados

**Anti-bot**
- Rotação de User-Agents
- Delays aleatórios em vez de fixos
- Suporte a proxies para sites com proteção mais agressiva

**Observabilidade**
- Logs estruturados em JSON com nível de severidade
- Métricas de execução (tempo por página, taxa de erro, total coletado)
- Alertas em caso de falha no pipeline

**IA**
- Cache local das respostas da IA para evitar reprocessar livros já enriquecidos
- Prompt mais elaborado para extrair mais campos (idioma original, ano de publicação, tags)
- Avaliação da qualidade das classificações com amostra manual

---

## 🤖 Como usei IA neste desafio

Usei Claude (Anthropic) como assistente principal durante todo o desenvolvimento.

**Estruturação do projeto**
Pedi para o Claude me ajudar a organizar a estrutura de arquivos e o fluxo do scraper antes de escrever qualquer código. Isso me ajudou a pensar em separação de responsabilidades e testabilidade desde o início.

**Geração de código**
A maior parte do código foi gerada ou ajustada com auxílio do Claude — `parser.py`, `saver.py`, `main.py`, `Dockerfile`, `.gitlab-ci.yml`. Em cada caso revisei, entendi e ajustei conforme necessário.

**Debugging**
Quando o scraper retornou o erro `ValueError: could not convert string to float: 'Â51.77'`, o Claude identificou o problema de encoding e sugeriu usar `re.sub` para limpar o símbolo de moeda. O mesmo ocorreu com o problema de descrições duplicadas.

**O que funcionou bem**
Usar IA para gerar a estrutura inicial e o boilerplate foi muito eficiente. O Claude também foi útil para explicar conceitos novos (multi-stage build, healthcheck no docker-compose) de forma contextualizada.

**O que exigiu ajuste**
A lógica de detecção de texto duplicado nas descrições precisou de várias iterações — as primeiras abordagens sugeridas pelo Claude não funcionaram para todos os casos. A solução final (usar a própria OpenAI para limpar o texto) foi uma decisão conjunta após analisar o problema mais a fundo.