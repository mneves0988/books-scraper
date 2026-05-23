import json
import csv
import os
import psycopg2


def save_json(books, filepath):
    """
    Salva a lista de livros em um arquivo JSON.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    print(f"JSON salvo em: {filepath}")


def save_csv(books, filepath):
    """
    Salva a lista de livros em um arquivo CSV.
    """
    if not books:
        return

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)
    print(f"CSV salvo em: {filepath}")


def save_postgres(books):
    """
    Salva a lista de livros no PostgreSQL.
    Lê as credenciais das variáveis de ambiente.
    """
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "books"),
        user=os.getenv("POSTGRES_USER", "scraper"),
        password=os.getenv("POSTGRES_PASSWORD", "scraper"),
    )

    cursor = conn.cursor()

    # Cria a tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(10, 2),
            rating INTEGER,
            availability TEXT,
            url TEXT UNIQUE,
            description TEXT,
            genre TEXT,
            target_audience TEXT
        )
    """)

    # Insere os livros — ignora duplicatas pelo url
    for book in books:
        cursor.execute("""
            INSERT INTO books (title, price, rating, availability, url, description, genre, target_audience)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """, (
            book["title"],
            book["price"],
            book["rating"],
            book["availability"],
            book["url"],
            book.get("description", ""),
            book.get("genre", "Unknown"),
            book.get("target_audience", "Unknown"),
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"PostgreSQL: {len(books)} livros salvos.")
