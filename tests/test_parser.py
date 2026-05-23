from bs4 import BeautifulSoup
from scraper.parser import parse_rating, parse_price, parse_book, parse_book_detail

# ── parse_rating ──────────────────────────────────────────────────────────────

def test_parse_rating_three():
    assert parse_rating(["star-rating", "Three"]) == 3

def test_parse_rating_one():
    assert parse_rating(["star-rating", "One"]) == 1

def test_parse_rating_five():
    assert parse_rating(["star-rating", "Five"]) == 5

def test_parse_rating_invalid():
    assert parse_rating(["star-rating"]) == 0


# ── parse_price ───────────────────────────────────────────────────────────────

def test_parse_price_basic():
    assert parse_price("£12.99") == 12.99

def test_parse_price_round():
    assert parse_price("£50.00") == 50.0

def test_parse_price_with_spaces():
    assert parse_price("£ 9.99") == 9.99


# ── parse_book ────────────────────────────────────────────────────────────────

def test_parse_book():
    html = """
    <article class="product_pod">
        <h3><a href="../../../a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
        <p class="star-rating Three"></p>
        <p class="price_color">£51.77</p>
        <p class="instock availability">  In stock  </p>
    </article>
    """
    article = BeautifulSoup(html, "html.parser").find("article")
    book = parse_book(article)

    assert book["title"] == "A Light in the Attic"
    assert book["price"] == 51.77
    assert book["rating"] == 3
    assert book["availability"] == "In stock"
    assert book["url"] == "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


# ── parse_detail ────────────────────────────────────────────────────────────────


def test_parse_book_detail_com_more():
    texto = "Um livro incrível sobre magia e aventura em um mundo fantástico onde tudo é possível e os heróis lutam pelo bem."
    html = f"""
    <div id="product_description"></div>
    <p>{texto}\n{texto} ...more</p>
    """
    description = parse_book_detail(html)
    assert description == texto