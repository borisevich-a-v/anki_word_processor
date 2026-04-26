import hashlib
import json
import re
import sqlite3
from enum import StrEnum
from pathlib import Path

import spacy
from spacy import Language
from pydantic import BaseModel

CACHE_DIR = Path(__file__).parents[1] / "data" / ".cache"
CHUNK_TOKEN_LIMIT = 10  # must match split_text_to_chunks chunk size
_WORD_CHAR = re.compile(r"\w", re.UNICODE)


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


def lemmatize(nlp: Language, text: str) -> str:
    doc = nlp(text)
    return " ".join(
        lemma for t in doc
        if (lemma := t.lemma_.strip()) and _WORD_CHAR.search(lemma)
    )


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


def _fts5_tokens(text: str) -> list[str]:
    return [t for t in text.split() if t]


def _quote(token: str) -> str:
    return '"' + token.replace('"', '""') + '"'


def _fts5_phrase(text: str) -> str | None:
    tokens = _fts5_tokens(text)
    if not tokens:
        return None
    return _quote(" ".join(tokens))


def _fts5_near(text: str) -> str | None:
    tokens = _fts5_tokens(text)
    if len(tokens) < 2:
        return None
    span = min(len(tokens) + 3, CHUNK_TOKEN_LIMIT - 1)
    if len(tokens) >= CHUNK_TOKEN_LIMIT - 1:
        return None
    return f"NEAR({' '.join(_quote(t) for t in tokens)}, {span})"


def _fts5_bag(text: str) -> str | None:
    tokens = _fts5_tokens(text)
    if not tokens:
        return None
    return " ".join(_quote(t) for t in tokens)


def _match(column: str, text: str) -> list[tuple[str, str, str]]:
    sql = f"SELECT * FROM text_data WHERE {column} MATCH ?"
    for query in (_fts5_phrase(text), _fts5_near(text), _fts5_bag(text)):
        if query is None:
            continue
        rows = conn.execute(sql, (query,)).fetchall()
        if rows:
            return rows
    return []


def find_exact_word(word: str) -> list[tuple[str, str, str]]:
    # TODO: return a custom type
    return _match("original_text", word)


def find_word(nlp: Language, word: str) -> list[tuple[str, str, str]]:
    return _match("lemmatized_text", lemmatize(nlp, word))
