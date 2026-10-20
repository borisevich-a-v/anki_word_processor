"""making-cards.md, at the core API."""

from typing import Any

import pytest

from core import config
from core.store import db
from core.fake_llm import FakeLLM
from core.languages import En2RuPlugin, Ru2CnPlugin
from core.making_cards import RunReport, make_cards, read_terms

SOURCE = (
    "The old smith said that his sons went astray many years ago "
    "and he never heard from them again after that winter."
)


@pytest.fixture
def llm() -> Any:
    return FakeLLM()


def stored(table: str = "cards_ru") -> list[tuple]:
    return [row[1:] for row in db.fetchall(f"SELECT * FROM {table} ORDER BY id")]


def stored_terms(table: str = "cards_ru") -> list[str]:
    return [row[0] for row in stored(table)]


def test_blank_lines_are_not_terms(data):
    """MC-2: empty lines and lines of spaces are ignored and counted nowhere."""
    terms = data("terms.txt", "astray\n\n   \n\t\nsmith\n\n")

    assert read_terms(terms) == ["astray", "smith"]


def test_repeated_term_counts_once_at_its_first_place(data, llm):
    """MC-2: a repeated line is one term, whatever its letter case; the first spelling is kept."""
    terms = data("terms.txt", "astray\nsmith\nastray\nAstray\nsmith\n")
    reports: list[RunReport] = []

    result = make_cards(En2RuPlugin(), llm, terms, on_report=reports.append)

    assert reports[0].total == 2
    assert stored_terms() == ["astray", "smith"]
    assert len(result.made) == 2


def test_terms_file_with_windows_line_ends_and_a_byte_order_mark(data):
    """MC-18, MC-2: a terms file saved on Windows gives the same terms."""
    terms = data("terms.txt", "﻿astray\r\nsmith\r\n".encode())

    assert read_terms(terms) == ["astray", "smith"]


def test_byte_order_mark_is_not_part_of_the_term_or_the_text(data, llm):
    """MC-18: a byte order mark at the start of either file reaches neither the card
    nor the context."""
    terms = data("terms.txt", ("\ufeff" + "old\n").encode())
    source = data("source.txt", ("\ufeff" + SOURCE).encode())

    make_cards(En2RuPlugin(), llm, terms, source)

    assert stored_terms() == ["old"]
    assert "[[1]]: The old smith" in llm.prompts[0]
    assert "\ufeff" not in llm.prompts[0]


@pytest.mark.parametrize(
    "term",
    ["well, then", "no; never", "mother-in-law", "a | b", "what?!", "it's — fine"],
)
def test_term_with_punctuation_gets_a_card(data, llm, term):
    """MC-3: a term with punctuation is processed and its card keeps it as written."""
    terms = data("terms.txt", term + "\n")
    source = data("source.txt", SOURCE)

    result = make_cards(En2RuPlugin(), llm, terms, source)

    assert result.failed == []
    assert stored_terms() == [term]


def test_term_with_a_card_is_not_processed(data, llm):
    """MC-4: a term with a card in the chosen pair is skipped, whatever its letter case; other text is not."""
    make_cards(En2RuPlugin(), llm, data("first.txt", "astray\n"))
    llm.prompts.clear()
    reports: list[RunReport] = []

    result = make_cards(
        En2RuPlugin(),
        llm,
        data("terms.txt", "astray\nAstray\nastray s\n"),
        on_report=reports.append,
    )

    assert reports[0].existing == ["astray"]
    assert reports[0].to_process == ["astray s"]
    assert len(llm.prompts) == 1
    assert len(result.made) == 1


def test_cards_of_another_language_pair_do_not_count(data, llm):
    """MC-4: a card of the same term in another language pair does not stop it."""
    terms = data("terms.txt", "кузнец\n")
    make_cards(Ru2CnPlugin(), llm, terms)

    result = make_cards(En2RuPlugin(), llm, terms)

    assert len(result.made) == 1
    assert stored_terms("cards_cn") == ["кузнец"]
    assert stored_terms("cards_ru") == ["кузнец"]


def test_limit(data, llm, monkeypatch):
    """MC-5: at most the limit is processed; the rest is "limit reached" and done by the next run."""
    monkeypatch.setattr(config, "MAX_CARDS_TO_PROCESS", 2)
    terms = data("terms.txt", "one\ntwo\nthree\nfour\nfive\n")

    first = make_cards(En2RuPlugin(), llm, terms)
    assert first.limit_reached == ["three", "four", "five"]
    assert stored_terms() == ["one", "two"]

    second = make_cards(En2RuPlugin(), llm, terms)
    assert second.limit_reached == ["five"]
    assert stored_terms() == ["one", "two", "three", "four"]


def test_the_limit_is_one_hundred():
    """MC-5: a run processes at most 100 terms."""
    assert config.MAX_CARDS_TO_PROCESS == 100


def test_one_card_per_term_with_the_fields_of_the_pair(data, llm):
    """MC-6: each term gives one card with all the fields of its language pair."""
    make_cards(
        En2RuPlugin(),
        llm,
        data("terms.txt", "astray\nsmith\n"),
        data("source.txt", SOURCE),
    )
    make_cards(Ru2CnPlugin(), llm, data("ru.txt", "кузнец\n"))

    assert [len(row) for row in stored("cards_ru")] == [7, 7]
    assert [len(row) for row in stored("cards_cn")] == [5]
    assert all(
        value for row in stored("cards_ru") + stored("cards_cn") for value in row
    )


def test_card_is_written_from_up_to_five_contexts(data, llm):
    """MC-6: the usage contexts from the source text reach card writing, five at most."""
    pad = " ".join(f"pad{i}" for i in range(60))
    source = " ".join(
        f"in place number{i} the smith said nothing at all today {pad}"
        for i in range(8)
    )

    make_cards(
        En2RuPlugin(), llm, data("terms.txt", "smith\n"), data("source.txt", source)
    )

    assert "<CONTEXT OF USAGE>" in llm.prompts[0]
    assert "[[5]]: " in llm.prompts[0]
    assert "[[6]]: " not in llm.prompts[0]


def test_card_keeps_the_term_as_in_the_file(data, llm):
    """MC-16: the term field is the term as written, whatever card writing returned."""
    terms = data("terms.txt", "went astray\n")

    make_cards(En2RuPlugin(), llm, terms)  # the stand-in returns "WENT ASTRAY"
    again = make_cards(En2RuPlugin(), llm, terms)

    assert stored_terms() == ["went astray"]
    assert again.made == []


@pytest.mark.parametrize(
    "source",
    [None, "Nothing in this text is about the term at all, not a single word."],
)
def test_no_context_still_gives_a_complete_card(data, llm, source):
    """MC-14: without a source text, or with the term not in it, the example is made up and stored."""
    source_file = data("source.txt", source) if source else None

    result = make_cards(En2RuPlugin(), llm, data("terms.txt", "astray\n"), source_file)

    assert len(result.made) == 1
    assert "make the example up" in llm.prompts[0]
    assert "<CONTEXT OF USAGE>" not in llm.prompts[0]
    [card] = stored()
    assert card[5] == "example of astray"


@pytest.mark.parametrize("plugin", [En2RuPlugin, Ru2CnPlugin])
def test_card_writing_may_use_the_web_but_not_cite_it(data, llm, plugin):
    """MC-19: card writing is given web search, and is asked for no links and no citations."""
    make_cards(plugin(), llm, data("terms.txt", "кузнец\n"))

    assert llm.tools == [[{"type": "web_search"}]]
    assert "do not add citation, do not add links" in llm.prompts[0]


def test_what_is_asked_of_an_english_russian_card(data, llm):
    """Language pairs, English → Russian: the explanation is in English or Russian and
    3-10 words, 15 at most; the translation in the exercise stands between underscores."""
    make_cards(En2RuPlugin(), llm, data("terms.txt", "astray\n"))

    asked = llm.prompts[0]
    assert "explanation - brief meaning of the word. Usually 3-10 words." in asked
    assert "15 words is a hard limit" in asked
    assert "# english or russian" in asked
    assert '"exercise": "His sons went _неправильный путь_"' in asked


def test_what_is_asked_of_a_russian_chinese_card(data, llm):
    """Language pairs, Russian → Chinese: the explanation is in Russian and 3-10 words,
    15 at most."""
    make_cards(Ru2CnPlugin(), llm, data("terms.txt", "кузнец\n"))

    asked = llm.prompts[0]
    assert "explanation - brief meaning of the word. Usually 3-10 words." in asked
    assert "15 words is a hard limit. Should be in Russian." in asked


def test_invalid_card_is_not_saved(data, llm):
    """MC-7: a card that breaks a field rule is not saved and its term is reported as failed."""
    result = make_cards(En2RuPlugin(), llm, data("terms.txt", "bad-level\nx\nastray\n"))

    assert [term for term, _ in result.failed] == [
        "bad-level",
        "x",
    ]  # "x" is too short a term
    assert "level" in result.failed[0][1]
    assert stored_terms() == ["astray"]


def test_failure_reason_is_in_plain_words(data, llm):
    """MC-8: a card that broke a field rule is reported with the field and the rule, as a
    refused edit would say it, not as a raw validation error."""
    result = make_cards(En2RuPlugin(), llm, data("terms.txt", "bad-level\nx\n"))

    assert result.failed == [
        ("bad-level", "level must be one of A1, A2, B1, B2, C1 or C2"),
        ("x", "term must have at least 2 characters"),
    ]


def test_the_same_file_cannot_be_terms_and_source(data, llm):
    """MC-22: the same file as terms file and source text is a run error, nothing is made."""
    same = data("terms.txt", "astray\n")

    with pytest.raises(ValueError, match="different files"):
        make_cards(En2RuPlugin(), llm, same, same)

    assert llm.prompts == [] and stored() == []


def test_failure_does_not_stop_the_run(data, llm):
    """MC-8: a failed term is reported with its reason, saves nothing, and the run goes on."""
    result = make_cards(
        En2RuPlugin(), llm, data("terms.txt", "fail-first\nastray\nfail-third\nsmith\n")
    )

    assert result.failed == [
        ("fail-first", "LLM is down"),
        ("fail-third", "LLM is down"),
    ]
    assert stored_terms() == ["astray", "smith"]


def test_card_is_saved_as_soon_as_it_is_made(data, llm):
    """MC-9: when the second term is being worked on, the first card is already kept."""
    seen: list[list[str]] = []

    make_cards(
        En2RuPlugin(),
        llm,
        data("terms.txt", "astray\nsmith\n"),
        on_progress=lambda done, total, term: seen.append(stored_terms()),
    )

    assert seen == [[], ["astray"]]


def test_report_comes_before_the_first_term(data, llm, monkeypatch):
    """MC-15: the report has the totals, the terms with a card and those over the limit,
    and is given before anything is processed."""
    monkeypatch.setattr(config, "MAX_CARDS_TO_PROCESS", 2)
    make_cards(En2RuPlugin(), llm, data("first.txt", "astray\n"))
    llm.prompts.clear()
    events: list[Any] = []

    make_cards(
        En2RuPlugin(),
        llm,
        data("terms.txt", "one\nastray\ntwo\nthree\n"),
        on_report=lambda report: events.append((report, len(llm.prompts))),
        on_progress=lambda done, total, term: events.append(term),
    )

    assert events == [
        (
            RunReport(
                total=4,
                to_process=["one", "two"],
                existing=["astray"],
                over_limit=["three"],
            ),
            0,
        ),
        "one",
        "two",
    ]


def test_nothing_left_to_process(data, llm):
    """MC-15: with every term done already, the report says so and no card is made."""
    terms = data("terms.txt", "astray\n")
    make_cards(En2RuPlugin(), llm, terms)
    llm.prompts.clear()
    reports: list[RunReport] = []

    result = make_cards(
        En2RuPlugin(), llm, terms, data("source.txt", SOURCE), on_report=reports.append
    )

    assert reports == [
        RunReport(total=1, to_process=[], existing=["astray"], over_limit=[])
    ]
    assert result.made == [] and llm.prompts == []


def test_progress(data, llm):
    """MC-10: progress gives terms done, the total and the current term."""
    progress: list[tuple[int, int, str]] = []

    make_cards(
        En2RuPlugin(),
        llm,
        data("terms.txt", "astray\nsmith\n"),
        on_progress=lambda done, total, term: progress.append((done, total, term)),
    )

    assert progress == [(0, 2, "astray"), (1, 2, "smith")]


def test_summary_names_every_term_not_processed(data, llm, monkeypatch):
    """MC-11, MC-17: the result has the cards made and the failed, limit-reached and cancelled terms."""
    monkeypatch.setattr(config, "MAX_CARDS_TO_PROCESS", 4)
    terms = data("terms.txt", "astray\nfail-two\nthree\nfour\nfive\n")

    result = make_cards(
        En2RuPlugin(), llm, terms, should_cancel=lambda: len(llm.prompts) == 2
    )

    assert len(result.made) == 1
    assert result.failed == [("fail-two", "LLM is down")]
    assert result.cancelled == ["three", "four"]
    assert result.limit_reached == ["five"]


def test_cancelled_terms_are_picked_up_by_the_next_run(data, llm):
    """MC-17, MC-9: cards made before a cancel are kept; the rest is made by the next run."""
    terms = data("terms.txt", "astray\nsmith\nwinter\n")

    first = make_cards(
        En2RuPlugin(), llm, terms, should_cancel=lambda: len(llm.prompts) == 1
    )
    assert first.cancelled == ["smith", "winter"]
    assert stored_terms() == ["astray"]

    second = make_cards(En2RuPlugin(), llm, terms)
    assert second.cancelled == []
    assert stored_terms() == ["astray", "smith", "winter"]


@pytest.mark.parametrize("broken", ["terms", "source"])
def test_unreadable_file_stops_the_run_before_the_report(data, llm, broken):
    """MC-13: a file that cannot be read is an error, with no report and no cards."""
    files = {
        "terms": data("terms.txt", "astray\n"),
        "source": data("source.txt", SOURCE),
    }
    files[broken] = data("broken.bin", b"\xff\xfe\xff\xff not text")
    reports: list[RunReport] = []

    with pytest.raises(UnicodeDecodeError):
        make_cards(
            En2RuPlugin(),
            llm,
            files["terms"],
            files["source"],
            on_report=reports.append,
        )

    assert reports == [] and stored() == []


RULES = {
    En2RuPlugin: {
        "word": (2, 100),
        "phonetic_transcription": (3, 300),
        "russian_translation": (4, 300),
        "explanation": (5, 400),
        "example": (5, 300),
        "exercise": (5, 300),
    },
    Ru2CnPlugin: {
        "word": (2, 100),
        "first_form": (2, 100),
        "chinese_translation": (1, 300),
        "explanation": (1, 400),
        "example": (1, 300),
    },
}


def filled(name: str, length: int) -> str:
    """A value of exactly this length; the exercise carries its underscores."""
    if name == "exercise":
        return "_" + "x" * (length - 2) + "_"
    return "x" * length


@pytest.mark.parametrize("plugin", RULES)
def test_field_rules_of_the_language_pairs(plugin):
    """MC-7, Language pairs: every field accepts its shortest and longest length and nothing beyond."""
    rules = RULES[plugin]
    valid = {name: filled(name, low) for name, (low, _) in rules.items()}
    if plugin is En2RuPlugin:
        valid["level"] = "C1"
    card = plugin.AnkiCard
    assert set(card.model_fields) == set(valid)
    assert len(plugin.FIELDS) == len(valid)

    card(**valid)
    for name, (low, high) in rules.items():
        card(**{**valid, name: filled(name, high)})
        for length in (low - 1, high + 1):
            with pytest.raises(ValueError):
                card(**{**valid, name: filled(name, length)})
    if plugin is En2RuPlugin:
        for level in ("A1", "A2", "B1", "B2", "C1", "C2"):
            card(**{**valid, "level": level})
        with pytest.raises(ValueError):
            card(**{**valid, "level": "C3"})


def test_report_counts_repeated_lines_that_were_ignored(data, llm):
    """MC-15, MC-2: the report says how many repeated lines were ignored."""
    terms = data("terms.txt", "astray\nsmith\nastray\n\nsmith\nastray\n")
    reports: list[RunReport] = []

    make_cards(En2RuPlugin(), llm, terms, on_report=reports.append)

    assert reports[0].total == 2
    assert reports[0].duplicates == 3


@pytest.mark.parametrize(
    "exercise", ["He went astray", "He went _ _ astray", "He _went astray", "__"]
)
def test_exercise_without_its_translation_between_underscores_is_not_saved(
    data, llm, exercise
):
    """MC-7, MC-8: an exercise without text between a pair of underscores breaks the
    field rule; nothing is saved and the reason is plain."""
    fields = {
        "word": "astray",
        "phonetic_transcription": "/x/ /y/",
        "russian_translation": "заблудился",
        "explanation": "lost the way",
        "level": "C1",
        "example": "He went astray",
        "exercise": exercise,
    }
    with pytest.raises(ValueError):
        En2RuPlugin.AnkiCard(**fields)

    result = make_cards(
        En2RuPlugin(), llm, data("terms.txt", "plain-exercise\nastray\n")
    )

    assert result.failed == [
        (
            "plain-exercise",
            "exercise must have its Russian translation set between underscores, like _this_",
        )
    ]
    assert stored_terms() == ["astray"]
    assert "_" in stored()[0][-1]


def test_the_prompt_asks_for_the_underscores():
    """MC-7: the writer is told how the exercise is marked."""
    assert "between underscores" in En2RuPlugin.PROMPT
