import sqlite3
from enum import StrEnum

import spacy
from spacy import Language
from pydantic import BaseModel

conn = sqlite3.connect(":memory:")
conn.execute("DROP TABLE IF EXISTS text_data")
conn.execute(
    "CREATE VIRTUAL TABLE text_data USING fts5(original_text, lemmatized_text, context UNINDEXED)"
)


class SpacyPipeline(StrEnum):
    CHINESE = "zh_core_web_md"
    ENGLISH = "en_core_web_md"
    RUSSIAN = "ru_core_news_md"


def get_nlp(lang: SpacyPipeline) -> Language:
    return spacy.load(lang)


def lemmatize(nlp: Language, text: str):
    doc = nlp(text)
    return " ".join([t.lemma_ for t in doc])


class Chunk(BaseModel):
    chunk: str
    context: str


def split_text_to_chunks(text: str) -> list[Chunk]:
    # not the optimal way to retrieve context, but the simplest

    tokens = text.split()
    res: list[Chunk] = []
    context = tokens[:100]
    tokens = tokens[100:]

    buff = []
    for token in context[:50]:
        buff.append(token)
        if len(buff) == 10:
            chunk = Chunk(chunk=" ".join(buff), context=" ".join(context))
            res.append(chunk)
            buff = []

    for token in tokens:
        context.append(token)
        if len(context) == 110:
            t = context[50:60]
            chunk = Chunk(chunk=" ".join(t), context=" ".join(context))
            res.append(chunk)
            context = context[10:]

    for token in context[50:]:
        buff.append(token)
        if len(buff) == 10:
            chunk = Chunk(chunk=" ".join(buff), context=" ".join(context))
            res.append(chunk)
            buff = []

    return res


def insert_text_chunk(nlp: Language, text: str) -> None:
    data = lemmatize(nlp, text)

    conn.execute(
        "INSERT INTO text_data(original_text, lemmatized_text, context) VALUES (?, ?, ?)",
        (text, data, "metadata"),
    )
    conn.commit()


def find_exact_word(word: str) -> list[tuple[str, str, str]]:
    rows = conn.execute(
        "SELECT * FROM text_data WHERE original_text MATCH ?", (word,)
    ).fetchall()
    return rows


def find_word(nlp: Language, word: str) -> list[tuple[str, str, str]]:
    lemmatized_word = lemmatize(nlp, word)
    rows = conn.execute(
        "SELECT * FROM text_data WHERE lemmatized_text MATCH ?", (lemmatized_word,)
    ).fetchall()
    return rows
