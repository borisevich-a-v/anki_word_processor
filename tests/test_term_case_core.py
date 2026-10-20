"""Terms are compared ignoring letter case (change 016), at the core API."""

from typing import Any, cast

from core.card_library import edit_card, list_cards
from core.fake_llm import FakeLLM
from core.languages import En2RuPlugin
from core.making_cards import make_cards, plan_run, read_terms, read_terms_counted
from core.store import db

PLUGIN = En2RuPlugin()


def add(word: str) -> int:
    return db.execute(
        "INSERT INTO cards_ru (word, phonetic_transcription, russian_translation,"
        " explanation, level, example, exercise) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (word, "/x/ ok", "перевод", "explanation", "B2", "An example", "An _пример_"),
    )


def test_case_variants_in_a_file_are_one_term_first_kept(data):
    """MC-2: lines differing only in case are one term; the first spelling is kept and the rest counted."""
    path = data("t.txt", "alpha\nBiceps\n  biceps \nBICEPS\nbeta\nALPHA\n")
    assert read_terms_counted(path) == (["alpha", "Biceps", "beta"], 3)
    assert read_terms(data("u.txt", "biceps\nBiceps\n")) == ["biceps"]


def test_case_folding_is_unicode(data):
    """MC-2: case is folded the Unicode way, not just ASCII."""
    path = data("t.txt", "Ёж\nёж\nStraße\nSTRASSE\n")
    assert read_terms(path) == ["Ёж", "Straße"]
    assert read_terms_counted(path)[1] == 2


def test_a_card_in_another_case_counts_as_existing():
    """MC-4: a card for "Biceps" is a card for "biceps"; non-ASCII letters too."""
    add("Biceps")
    add("Ёж")
    assert PLUGIN.is_processed("biceps")
    assert PLUGIN.is_processed("ёж")
    assert not PLUGIN.is_processed("triceps")
    report = plan_run(PLUGIN, ["biceps", "BICEPS ", "ёж", "triceps"])
    assert report.existing == ["biceps", "BICEPS ", "ёж"]
    assert report.to_process == ["triceps"]


def test_run_skips_a_term_with_a_card_in_another_case_and_keeps_spelling(data):
    """MC-4: not made again; the existing card keeps its spelling. MC-16: new cards keep the file's spelling."""
    add("Biceps")
    path = data("t.txt", "biceps\nAlpha\nalpha\n")
    result = make_cards(PLUGIN, cast(Any, FakeLLM()), path)
    assert len(result.made) == 1
    assert [c[1] for c in list_cards(PLUGIN)] == ["Biceps", "Alpha"]


def test_cards_in_another_language_pair_do_not_count():
    """MC-4: only the chosen pair counts (case does not change that)."""
    from core.languages import PLUGINS

    other = next(p for p in PLUGINS if p.TABLE_NAME != PLUGIN.TABLE_NAME)
    db.execute(
        f"INSERT INTO {PLUGIN.TABLE_NAME} (word, phonetic_transcription,"
        " russian_translation, explanation, level, example, exercise)"
        " VALUES ('Zed', 'x', 'x', 'x', 'B2', 'x', 'x')"
    )
    assert not other().is_processed("zed")


def test_edit_to_another_cards_term_in_other_case_is_refused():
    """CL-4: a term may not equal another card's term in any letter case."""
    add("Biceps")
    other = add("triceps")
    res = edit_card(PLUGIN, other, 0, "BICEPS")
    assert not res.ok and res.error == "Another card has this term"
    assert [c[1] for c in list_cards(PLUGIN)] == ["Biceps", "triceps"]


def test_edit_only_the_case_of_own_term_is_allowed():
    """CL-4: changing only the letter case of a card's own term is allowed."""
    card = add("biceps")
    res = edit_card(PLUGIN, card, 0, "Biceps")
    assert res.ok
    assert [c[1] for c in list_cards(PLUGIN)] == ["Biceps"]


def test_existing_case_variant_cards_are_tolerated():
    """MC-4: a store that already holds "biceps" and "Biceps" keeps both and nothing fails."""
    a, b = add("biceps"), add("Biceps")
    assert PLUGIN.is_processed("BiCePs")
    assert edit_card(PLUGIN, a, 2, "другой").ok  # other fields stay editable
    assert edit_card(PLUGIN, b, 0, "Biceps").ok  # unchanged term
    assert not edit_card(PLUGIN, b, 0, "biceps").ok  # the other's term
    assert len(list_cards(PLUGIN)) == 2
