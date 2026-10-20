"""Making cards: turns the terms of a terms file into saved cards."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError
from core import config

from core.card_library import describe_error
from core.context_finding import SourceText
from core.languages import Plugin, CardT
from core.terms import term_key


@dataclass(frozen=True)
class RunReport:
    """What a run will do with the terms file, known before the first term is processed."""

    total: int  # terms in the file
    to_process: list[str]
    existing: list[str]  # already have a card
    over_limit: list[str]  # left for a later run
    duplicates: int = 0  # repeated lines of the file that were ignored


@dataclass
class RunResult:
    made: list[int] = field(default_factory=list)  # ids of the cards made
    failed: list[tuple[str, str]] = field(default_factory=list)  # (term, reason)
    limit_reached: list[str] = field(default_factory=list)
    cancelled: list[str] = field(default_factory=list)


def read_terms_counted(terms_file: Path) -> tuple[list[str], int]:
    """The terms of the file, and how many repeated lines were dropped."""
    lines = terms_file.read_text(encoding=config.TEXT_ENCODING).splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    # the first of lines that differ only in letter case is the one kept
    first: dict[str, str] = {}
    for line in lines:
        first.setdefault(term_key(line), line)
    terms = list(first.values())
    return terms, len(lines) - len(terms)


def read_terms(terms_file: Path) -> list[str]:
    """One term per line; blank lines and repeats of an earlier line (in any letter case) are dropped."""
    return read_terms_counted(terms_file)[0]


def plan_run(plugin: Plugin, terms: list[str], duplicates: int = 0) -> RunReport:
    existing = [t for t in terms if plugin.is_processed(t)]
    new = [t for t in terms if t not in set(existing)]
    return RunReport(
        total=len(terms),
        to_process=new[: config.MAX_CARDS_TO_PROCESS],
        existing=existing,
        over_limit=new[config.MAX_CARDS_TO_PROCESS :],
        duplicates=duplicates,
    )


def card_request(term: str, contexts: list[str]) -> str:
    request = f"<TARGET WORD>{term}</TARGET WORD>"
    if not contexts:
        return request + "\nThere is no context of usage: make the example up."
    numbered = "\n".join(f"[[{i + 1}]]: {c}" for i, c in enumerate(contexts))
    return request + f"\n<CONTEXT OF USAGE>\n{numbered}\n</CONTEXT OF USAGE>"


def write_card(
    plugin: Plugin[CardT],
    llm: OpenAI,
    term: str,
    contexts: list[str],
    model: str = config.PROD_MODEL,
) -> CardT:
    written = llm.responses.parse(
        model=model,
        tools=[{"type": "web_search"}],
        input=plugin.PROMPT.format(input_card=card_request(term, contexts)),
        text_format=plugin.AnkiCard,
    ).output_parsed
    if not written:
        raise ValueError("Empty card")
    # the card carries the term as written in the terms file, whatever came back
    return plugin.AnkiCard.model_validate({**written.model_dump(), "word": term})


def make_cards(
    plugin: Plugin,
    llm: OpenAI,
    terms_file: Path,
    source_file: Path | None = None,
    *,
    on_report: Callable[[RunReport], None] | None = None,
    on_progress: Callable[[int, int, str], None] | None = None,
    should_cancel: Callable[[], bool] | None = None,
    model: str = config.PROD_MODEL,
) -> RunResult:
    """One run. Raises when it cannot proceed at all; a failing term does not raise.

    on_report is called once, before any term is processed.
    on_progress(done, total, term) is called before each term.
    should_cancel is asked before each term; True leaves the rest unprocessed.
    """
    if source_file and source_file.resolve() == terms_file.resolve():
        raise ValueError("The terms file and the source text must be different files")
    terms, duplicates = read_terms_counted(terms_file)
    source_text = (
        source_file.read_text(encoding=config.TEXT_ENCODING) if source_file else None
    )

    report = plan_run(plugin, terms, duplicates)
    if on_report:
        on_report(report)
    result = RunResult(limit_reached=list(report.over_limit))
    if not report.to_process:
        return result

    source = (
        SourceText(plugin.SOURCE_LANGUAGE, source_text)
        if source_text is not None
        else None
    )
    total = len(report.to_process)
    for done, term in enumerate(report.to_process):
        if should_cancel and should_cancel():
            result.cancelled = report.to_process[done:]
            break
        if on_progress:
            on_progress(done, total, term)
        try:
            contexts = source.find(term) if source else []
            card = write_card(plugin, llm, term, contexts, model)
            result.made.append(plugin.save_card(card))
        except ValidationError as e:
            result.failed.append((term, describe_error(plugin, e)))
        except Exception as e:
            result.failed.append((term, str(e) or type(e).__name__))
    return result
