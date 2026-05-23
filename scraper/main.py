import os
import time
import requests
from bs4 import BeautifulSoup
from scraper.parser import parse_book, parse_book_detail
from scraper.saver import save_json, save_csv, save_postgres
from scraper.ai_enricher import enrich_book


BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 50
DELAY = 1  # segundo entre requisições


def get_html(url):
    """
    Faz a requisição HTTP e retorna o HTML da página.
    """
    headers = {"User-Agent": "books-scraper/1.0 (trainee-challenge)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = "utf-8"  # força encoding correto
    return response.text


def scrape_page(url):
    """
    Faz a requisição de uma página de listagem e retorna lista de livros.
    """
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article", class_="product_pod")
    return [parse_book(article) for article in articles]


def scrape_book_detail(book):
    """
    Acessa a página de detalhe do livro, extrai a descrição crua
    e usa IA para limpar e enriquecer os dados.
    """
    html = get_html(book["url"])
    description_raw = parse_book_detail(html)

    if description_raw:
        enriched = enrich_book(description_raw)
        book["description"] = enriched.get("description", description_raw)
        book["genre"] = enriched.get("genre", "Unknown")
        book["target_audience"] = enriched.get("target_audience", "Unknown")
    else:
        book["description"] = ""
        book["genre"] = "Unknown"
        book["target_audience"] = "Unknown"

    return book


def scrape_all_pages():
    """
    Percorre todas as páginas, coleta os livros e suas descrições.
    """
    all_books = []

    for page_num in range(1, TOTAL_PAGES + 1):
        url = BASE_URL.format(page_num)
        print(f"Coletando página {page_num}/{TOTAL_PAGES}...")

        books = scrape_page(url)

        for i, book in enumerate(books):
            print(f"  Detalhe {i + 1}/{len(books)}: {book['title'][:40]}")
            book = scrape_book_detail(book)
            all_books.append(book)
            time.sleep(DELAY)

    return all_books


def main():
    print("Iniciando scraper...")
    books = scrape_all_pages()
    print(f"\nTotal de livros coletados: {len(books)}")

    save_json(books, "output/books.json")
    save_csv(books, "output/books.csv")

    # Salva no PostgreSQL se as variáveis de ambiente estiverem configuradas
    if os.getenv("POSTGRES_HOST"):
        save_postgres(books)

    print("Concluído!")
