import hashlib
import json
import sqlite3
from enum import StrEnum
from pathlib import Path

import spacy
from spacy import Language
from pydantic import BaseModel

CACHE_DIR = Path(__file__).parents[1] / "data" / ".cache"


def _cache_path(text: str) -> Path:
    digest = hashlib.sha256(text.encode()).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _load_cache(text: str) -> list[tuple] | None:
    path = _cache_path(text)
    if path.exists():
        return [tuple(row) for row in json.loads(path.read_text(encoding="utf-8"))]
    return None


def _save_cache(text: str, rows: list[tuple]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(text).write_text(json.dumps(rows), encoding="utf-8")

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
    # TODO reduce context length, to make it cheaper for LLM

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



def ingest_text(nlp: Language, text: str) -> None:
    if cached := _load_cache(text):
        conn.executemany(
            "INSERT INTO text_data(original_text, lemmatized_text, context) VALUES (?, ?, ?)",
            cached,
        )
        conn.commit()
        return

    chunks = split_text_to_chunks(text)
    rows = []
    for chunk in chunks:
        lemmatized = lemmatize(nlp, chunk.chunk)
        conn.execute(
            "INSERT INTO text_data(original_text, lemmatized_text, context) VALUES (?, ?, ?)",
            (chunk.chunk, lemmatized, chunk.context),
        )
        rows.append((chunk.chunk, lemmatized, chunk.context))
    conn.commit()
    _save_cache(text, rows)


def find_exact_word(word: str) -> list[tuple[str, str, str]]:
    # TODO: return a custom type
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
