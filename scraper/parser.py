from bs4 import BeautifulSoup
import re


# Mapeamento de rating por extenso para número
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def parse_rating(class_list):
    """
    Recebe a lista de classes CSS do elemento de rating.
    Ex: ["star-rating", "Three"] → retorna 3
    """
    for word in class_list:
        if word in RATING_MAP:
            return RATING_MAP[word]
    return 0


def parse_price(price_text):
    """
    Recebe o texto do preço com símbolo.
    Ex: "£12.99" → retorna 12.99 (float)
    """
    cleaned = re.sub(r"[^\d.]", "", price_text)
    return float(cleaned)


BASE_CATALOGUE_URL = "http://books.toscrape.com/catalogue/"


def parse_book(article):
    """
    Recebe um elemento BeautifulSoup <article class="product_pod">
    e retorna um dicionário com os dados do livro, incluindo a URL de detalhe.
    """
    title = article.h3.a["title"]
    price = parse_price(article.find("p", class_="price_color").text)
    rating = parse_rating(article.find("p", class_="star-rating")["class"])
    availability = article.find("p", class_="instock").text.strip()

    # O href vem como "../../../a-light-in-the-attic_1000/index.html"
    relative_url = article.h3.a["href"]
    clean_path = relative_url.replace("../", "")
    url = BASE_CATALOGUE_URL + clean_path

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "url": url,
    }


def parse_book_detail(html):
    """
    Recebe o HTML da página de detalhe de um livro
    e retorna a descrição limpa em texto.
    """
    soup = BeautifulSoup(html, "html.parser")

    description_header = soup.find("div", id="product_description")

    if description_header is None:
        return ""

    description = description_header.find_next_sibling("p")

    if description is None:
        return ""

    text = description.get_text(separator=" ").strip()

    # O site duplica o texto separado por \n e adiciona "...more"
    # Basta pegar tudo antes do primeiro \n
    if "\n" in text:
        text = text.split("\n")[0].strip()

    return text
