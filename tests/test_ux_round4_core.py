"""Round-four findings (change 015), at the core API."""

from typing import Any, cast

from core.card_library import edit_card, list_cards
from core.fake_llm import FakeLLM
from core.languages import En2RuPlugin
from core.making_cards import make_cards, read_terms
from core.store import db

OLD_CARD = (
    "naive",
    "/naɪˈiːv/",
    "наивный",
    "доверчивый — простой",
    "B2",
    "A naive, simple cafe",
    "A naive, simple cafe",  # an old card: no underscores in the exercise
)


def add(card: tuple) -> int:
    return db.execute(
        "INSERT INTO cards_ru (word, phonetic_transcription, russian_translation,"
        " explanation, level, example, exercise) VALUES (?, ?, ?, ?, ?, ?, ?)",
        card,
    )


def test_spaces_around_a_term_are_not_part_of_it(data):
    """MC-2: "biceps " and "biceps" are one term; letter case does not (change 016)."""
    path = data("terms.txt", "biceps\n  biceps \t\nbiceps\nBiceps\n")
    assert read_terms(path) == ["biceps"]


def test_a_card_keeps_no_surrounding_spaces(data):
    """MC-6: no field of a made card starts or ends with a space; the term is trimmed too."""

    class Padded(FakeLLM):
        def _parse(self, **kw):
            out = super()._parse(**kw)
            card = out.output_parsed
            out.output_parsed = type(card)(
                **{k: f"  {v} " for k, v in card.model_dump().items() if k != "level"},
                level="B2",
            )
            return out

    make_cards(En2RuPlugin(), cast(Any, Padded()), data("terms.txt", " alpha \n"))
    [card] = list_cards(En2RuPlugin())
    assert card[1] == "alpha"
    assert all(v == v.strip() for v in card[1:])


def test_an_edit_loses_surrounding_spaces():
    """CL-11: spaces at the start and the end of an edited field are not kept."""
    card = add((*OLD_CARD[:6], "A _naive_, simple cafe"))
    result = edit_card(En2RuPlugin(), card, 2, "  другое  ")
    assert result.ok and result.value == "другое"
    assert list_cards(En2RuPlugin())[0][3] == "другое"
    assert not edit_card(En2RuPlugin(), card, 2, "   ").ok  # only spaces is empty


def test_a_term_with_only_spaces_added_is_the_same_term():
    """CL-4, MC-4: " naive" is the term of the card "naive"."""
    add(OLD_CARD)
    other = add(("other", *OLD_CARD[1:]))
    result = edit_card(En2RuPlugin(), other, 0, " naive ")
    assert not result.ok and "Another card has this term" in result.error


def test_editing_a_field_of_a_card_with_a_broken_exercise_says_to_fix_the_exercise():
    """CL-4: the refusal names the other field that must be fixed, and which one it is."""
    card = add(OLD_CARD)
    result = edit_card(En2RuPlugin(), card, 2, "другое слово")
    assert not result.ok
    assert result.fix == 6
    assert "fix the exercise field too" in result.error
    assert "underscores" in result.error
    assert list_cards(En2RuPlugin())[0][3] == "наивный"
    fixed = edit_card(En2RuPlugin(), card, 6, "A _наивный_, simple cafe")
    assert fixed.ok and fixed.fix is None
