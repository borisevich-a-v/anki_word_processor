"""Context finding: the passages of a source text where a term is used."""

import hashlib
import json
import re
import sqlite3
from functools import cache
from pathlib import Path

import spacy
from spacy import Language

from core import config
from core.languages.base import SpacyPipeline

CACHE_DIR = config.DATA_FOLDER / ".cache"
CACHE_VERSION = 2  # bump when what is stored per stretch changes
STRETCH_WORDS = 10  # the text is searched in stretches of this many words
CONTEXT_WORDS = 50
CONTEXT_WORDS_BEFORE = 20  # words of context before the stretch the term is in
MAX_CONTEXTS = 5
# what the full-text index takes for a word: letters and digits, nothing else
_WORD = re.compile(r"[^\W_]+")
_SPACE_SEPARATED = re.compile(r"\S+")
_LINE = re.compile(r"[^\n]+")

Row = tuple[str, str, str]  # stretch as written, stretch in dictionary forms, context


@cache
def get_nlp(lang: SpacyPipeline) -> Language:
    # models are slow to load; only dictionary forms are needed from them
    return spacy.load(lang, disable=["parser", "ner"])


def lemmatize(nlp: Language, text: str) -> str:
    return " ".join(
        lemma
        for t in nlp(text)
        if (lemma := (t.lemma_ or t.text).strip()) and _WORD.search(lemma)
    )


def _word_spans(lang: SpacyPipeline, text: str) -> list[tuple[int, int]]:
    """Where each word of the text starts and ends. Punctuation alone is not a word."""
    if lang is not SpacyPipeline.CHINESE:
        return [
            m.span() for m in _SPACE_SEPARATED.finditer(text) if _WORD.search(m.group())
        ]
    # no spaces between Chinese words: the model decides where they are
    nlp = get_nlp(lang)
    spans = []
    for line in _LINE.finditer(text):
        for token in nlp.make_doc(line.group()):
            if _WORD.search(token.text):
                start = line.start() + token.idx
                spans.append((start, start + len(token.text)))
    return spans


def _term_words(lang: SpacyPipeline, term: str) -> list[str]:
    if lang is not SpacyPipeline.CHINESE:
        return _WORD.findall(term)
    return [
        w for token in get_nlp(lang).make_doc(term) for w in _WORD.findall(token.text)
    ]


def _build_rows(lang: SpacyPipeline, text: str) -> list[Row]:
    spans = _word_spans(lang, text)
    stretches: list[str] = []
    contexts: list[str] = []
    for i in range(0, len(spans) - STRETCH_WORDS + 1, STRETCH_WORDS):
        stretches.append(" ".join(text[a:b] for a, b in spans[i : i + STRETCH_WORDS]))
        end = min(max(0, i - CONTEXT_WORDS_BEFORE) + CONTEXT_WORDS, len(spans))
        start = max(0, end - CONTEXT_WORDS)
        contexts.append(" ".join(text[spans[start][0] : spans[end - 1][1]].split()))

    if lang is SpacyPipeline.CHINESE:
        lemmatized = stretches  # Chinese words have one form
    else:
        nlp = get_nlp(lang)
        lemmatized = [lemmatize(nlp, s) for s in stretches]
    return list(zip(stretches, lemmatized, contexts))


def _cache_path(lang: SpacyPipeline, text: str) -> Path:
    digest = hashlib.sha256(f"{CACHE_VERSION}:{lang}:{text}".encode()).hexdigest()
    return CACHE_DIR / f"{digest}.json"


def _rows(lang: SpacyPipeline, text: str) -> list[Row]:
    path = _cache_path(lang, text)
    if path.exists():
        return [
            (r[0], r[1], r[2]) for r in json.loads(path.read_text(encoding="utf-8"))
        ]
    rows = _build_rows(lang, text)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows), encoding="utf-8")
    _drop_stale(keep=path)
    return rows


def _drop_stale(keep: Path) -> None:
    """Delete the cache files that belong to no text now in the data folder."""
    current = {keep}
    for file in config.user_files():
        try:
            text = file.read_text(encoding=config.TEXT_ENCODING)
        except (OSError, ValueError):  # not a text: never a source text
            continue
        current.update(_cache_path(lang, text) for lang in SpacyPipeline)
    for path in CACHE_DIR.glob("*.json"):
        if path not in current:
            path.unlink(missing_ok=True)


def _quote(words: list[str]) -> str:
    return '"' + " ".join(words) + '"'


def _queries(words: list[str]) -> list[str]:
    """Closest kind of match first: adjacent in order, close in any order, same stretch."""
    queries = [_quote(words)]
    if len(words) > 1:
        if len(words) < STRETCH_WORDS - 1:
            span = min(len(words) + 3, STRETCH_WORDS - 1)
            queries.append(f"NEAR({' '.join(_quote([w]) for w in words)}, {span})")
        queries.append(" ".join(_quote([w]) for w in words))
    return queries


class SourceText:
    """One source text, ready to be searched. Every run makes its own."""

    def __init__(self, lang: SpacyPipeline, text: str) -> None:
        self._lang = lang
        self._con = sqlite3.connect(":memory:", check_same_thread=False)
        self._con.execute(
            "CREATE VIRTUAL TABLE text_data USING fts5(original_text, lemmatized_text, context UNINDEXED)"
        )
        self._con.executemany(
            "INSERT INTO text_data VALUES (?, ?, ?)", _rows(lang, text)
        )

    def find(self, term: str) -> list[str]:
        """Up to five passages where the term is used, in text order."""
        if found := self._match("original_text", _term_words(self._lang, term)):
            return found
        if self._lang is SpacyPipeline.CHINESE:
            return []
        dictionary_form = lemmatize(
            get_nlp(self._lang), " ".join(_term_words(self._lang, term))
        )
        return self._match("lemmatized_text", _WORD.findall(dictionary_form))

    def _match(self, column: str, words: list[str]) -> list[str]:
        if not words:
            return []
        sql = f"SELECT context FROM text_data WHERE {column} MATCH ? ORDER BY rowid"
        for query in _queries(words):
            rows = self._con.execute(sql, (query,)).fetchall()
            if rows:
                # neighbouring stretches at the edges of the text share a passage
                return list(dict.fromkeys(r[0] for r in rows))[:MAX_CONTEXTS]
        return []
