"""card-library.md, at the core API."""

import sqlite3
from typing import Any, cast

from core.card_library import delete_cards, edit_card, list_cards
from core.languages import En2RuPlugin, Ru2CnPlugin
from core.making_cards import make_cards
from core.store import Database, db
from core.fake_llm import FakeLLM

EN_CARD = (
    "naive",
    "/naɪˈiːv/",
    "наивный",
    "доверчивый — простой",
    "B2",
    "A naive, simple cafe",
    "A _наивный_, simple cafe",
)
CN_CARD = ("кузнец", "кузнец", "铁匠", "тот, кто куёт", "Старый кузнец сказал")


def add(table: str, card: tuple) -> int:
    columns = [c[1] for c in db.fetchall(f"PRAGMA table_info({table})")][1:]
    return db.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(card))})",
        card,
    )


def test_cards_are_listed_newest_first_with_id_and_fields():
    """CL-1: the cards of the chosen pair only, newest first, each with its id and fields."""
    first = add("cards_ru", EN_CARD)
    second = add("cards_ru", ("later", *EN_CARD[1:]))
    other = add("cards_cn", CN_CARD)

    assert list_cards(En2RuPlugin(), newest_first=True) == [
        (second, "later", *EN_CARD[1:]),
        (first, *EN_CARD),
    ]
    assert list_cards(En2RuPlugin()) == [
        (first, *EN_CARD),
        (second, "later", *EN_CARD[1:]),
    ]
    assert list_cards(Ru2CnPlugin()) == [(other, *CN_CARD)]


def test_ids_grow_and_never_change(data):
    """CL-2: every new card gets an id above all earlier ones; earlier ids stay."""
    llm = cast(Any, FakeLLM())
    first = make_cards(En2RuPlugin(), llm, data("a.txt", "one\ntwo\n")).made
    before = list_cards(En2RuPlugin())

    second = make_cards(
        En2RuPlugin(), llm, data("b.txt", "three\nfail-four\nfive\n")
    ).made

    assert len(set(first + second)) == 4
    assert first + second == sorted(first + second)
    assert list_cards(En2RuPlugin())[:2] == before


def test_the_id_of_a_deleted_card_is_not_given_again():
    """CL-2, CL-9: deleting the newest card does not let the next card take its id."""
    plugin = En2RuPlugin()
    ids = [add("cards_ru", (t, *EN_CARD[1:])) for t in ("one", "two")]
    assert delete_cards(plugin, [ids[1]]) == 1

    newer = add("cards_ru", ("three", *EN_CARD[1:]))

    assert newer > ids[1]


def test_ids_of_old_tables_are_kept_by_the_move_to_explicit_ids(tmp_path):
    """CL-2: a card table made before ids were explicit keeps every card's id when it is
    rebuilt, a copy of the database is made first, and later ids stay above the old ones."""
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE cards_x (word, other)")
    con.executemany("INSERT INTO cards_x VALUES (?, ?)", [("a", "1"), ("b", "2")])
    con.execute("DELETE FROM cards_x WHERE word='a'")
    con.commit()
    con.close()

    old = Database(path)
    old.ensure_cards_table("cards_x", ["word", "other"])
    old.execute("INSERT INTO cards_x (word, other) VALUES ('c', '3')")

    assert old.fetchall("SELECT * FROM cards_x ORDER BY id") == [
        (2, "b", "2"),
        (3, "c", "3"),
    ]
    assert (tmp_path / "old.db.bak").exists()
    old.ensure_cards_table(
        "cards_x", ["word", "other"]
    )  # a second start changes nothing
    assert len(old.fetchall("SELECT * FROM cards_x")) == 2


def test_edit_changes_a_field_and_keeps_id_and_place():
    """CL-3, CL-6: any field, the term included, can be changed; the card keeps its id and
    place; the change is in the store at once."""
    plugin = En2RuPlugin()
    ids = [add("cards_ru", (t, *EN_CARD[1:])) for t in ("one", "two", "three")]

    assert edit_card(plugin, ids[1], 2, "другое").ok
    assert edit_card(plugin, ids[1], 0, "twelve").ok

    cards = list_cards(plugin)
    assert [c[0] for c in cards] == ids
    assert cards[1][1:] == ("twelve", EN_CARD[1], "другое", *EN_CARD[3:])
    assert cards[0][1] == "one" and cards[2][1] == "three"


def test_an_edit_that_breaks_a_field_rule_is_refused_with_the_reason():
    """CL-4: length and allowed values of the language pair are enforced; the card stays."""
    plugin = En2RuPlugin()
    card = add("cards_ru", EN_CARD)

    too_short = edit_card(plugin, card, 2, "ab")
    bad_level = edit_card(plugin, card, 4, "Z9")
    too_long = edit_card(plugin, card, 0, "x" * 101)

    assert not too_short.ok and "Russian translation" in too_short.error
    assert "at least 4" in too_short.error
    assert not bad_level.ok and "level" in bad_level.error and "A1" in bad_level.error
    assert (
        not too_long.ok and "term" in too_long.error and "at most 100" in too_long.error
    )
    assert list_cards(plugin) == [(card, *EN_CARD)]


def test_the_rules_are_those_of_the_cards_language_pair():
    """CL-4: a Russian → Chinese card may have a one-character translation."""
    card = add("cards_cn", CN_CARD)

    assert edit_card(Ru2CnPlugin(), card, 2, "铁").ok


def test_a_term_cannot_become_the_term_of_another_card():
    """CL-4: the same text as another card's term of this pair is refused; another pair
    does not count; keeping the own term is fine."""
    plugin = En2RuPlugin()
    one = add("cards_ru", ("one", *EN_CARD[1:]))
    add("cards_ru", ("two", *EN_CARD[1:]))
    add("cards_cn", ("three", *CN_CARD[1:]))

    clash = edit_card(plugin, one, 0, "two")

    assert not clash.ok and "term" in clash.error
    assert edit_card(plugin, one, 0, "one").ok
    assert edit_card(plugin, one, 0, "three").ok


def test_editing_a_missing_card_is_refused():
    """CL-4, CL-9: a card deleted meanwhile cannot be edited."""
    assert not edit_card(En2RuPlugin(), 12345, 2, "наивный").ok


def test_delete_removes_only_the_given_cards_of_the_pair():
    """CL-7, CL-9: the cards given are gone, the others and the other pair stay."""
    plugin = En2RuPlugin()
    ids = [add("cards_ru", (t, *EN_CARD[1:])) for t in ("one", "two", "three")]
    other = add("cards_cn", CN_CARD)

    assert delete_cards(plugin, [ids[0], ids[2], 999]) == 2

    assert [c[0] for c in list_cards(plugin)] == [ids[1]]
    assert [c[0] for c in list_cards(Ru2CnPlugin())] == [other]
    assert delete_cards(plugin, []) == 0


def test_a_term_of_a_deleted_card_can_be_made_again(data):
    """CL-9, MC-4: with its card gone, the term is processed by the next run."""
    plugin = En2RuPlugin()
    llm = cast(Any, FakeLLM())
    first = make_cards(plugin, llm, data("a.txt", "one\n")).made
    assert make_cards(plugin, llm, data("b.txt", "one\n")).made == []

    delete_cards(plugin, first)
    again = make_cards(plugin, llm, data("c.txt", "one\n")).made

    assert len(again) == 1 and again[0] > first[0]


def test_a_minimum_of_one_character_is_worded_as_not_empty():
    """CL-4, MC-8: the reason for an empty value is grammatical, never "at least 1 characters"."""
    plugin = Ru2CnPlugin()
    card = add("cards_cn", CN_CARD)

    empty = edit_card(plugin, card, 2, "")

    assert not empty.ok
    assert empty.error == "Chinese translation must not be empty"


def test_an_edit_cannot_take_the_underscores_out_of_the_exercise():
    """CL-4, MC-7: the exercise must keep its translation between underscores; the
    card stays as it was."""
    card = add("cards_ru", EN_CARD)

    result = edit_card(En2RuPlugin(), card, 6, "A naive, simple cafe")

    assert not result.ok
    assert result.error == (
        "exercise must have its Russian translation set between underscores, like _this_"
    )
    assert list_cards(En2RuPlugin())[0][7] == EN_CARD[6]
