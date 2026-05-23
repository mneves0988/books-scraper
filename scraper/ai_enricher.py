from openai import OpenAI
import json

client = OpenAI()


def enrich_book(description_raw):
    """
    Recebe a descrição crua do livro (com possível duplicação e ...more)
    e usa a OpenAI para retornar dados estruturados e limpos.
    """
    prompt = f"""
Você receberá a descrição crua de um livro extraída de um site.
O texto pode estar duplicado e pode terminar com "...more".

Retorne APENAS um JSON válido, sem texto adicional, sem markdown, sem explicações.

O JSON deve ter exatamente estas chaves:
- "description": descrição limpa, sem duplicação e sem "...more".
Se o texto estiver duplicado, mantenha apenas a primeira ocorrência completa.
- "genre": gênero do livro em inglês
(ex: Fiction, Non-Fiction, Thriller, Mystery, Romance, Self-Help, History, Science, Fantasy, Biography)
- "target_audience": público-alvo em inglês (ex: Adult, Young Adult, Children, Academic)

Descrição crua:
{description_raw[:1000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()
        return json.loads(raw)

    except (json.JSONDecodeError, Exception) as e:
        print(f"  ⚠️  Erro ao enriquecer descrição: {e}. Usando fallback.")
        return {
            "description": description_raw[:500],
            "genre": "Unknown",
            "target_audience": "Unknown",
        }
