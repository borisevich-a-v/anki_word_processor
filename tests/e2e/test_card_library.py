"""card-library.md, as the user sees it in the browser."""

from playwright.sync_api import Page, expect

from core.card_library import list_cards
from core.languages import En2RuPlugin

TERMS = ("alpha", "bravo", "charlie")


def row(page: Page, card_id: int):
    return page.locator(f'#body tr[data-id="{card_id}"]')


def cell(page: Page, card_id: int, field: int):
    return row(page, card_id).locator(f'td[data-field="{field}"]')


def edit(page: Page, card_id: int, field: int, value: str, key: str = "Enter") -> None:
    cell(page, card_id, field).dblclick()
    box = cell(page, card_id, field).locator("textarea")
    box.fill(value)
    box.press(key)


def stored(card_id: int) -> tuple:
    return next(c for c in list_cards(En2RuPlugin()) if c[0] == card_id)[1:]


def test_edit_a_field_in_place(app, seed_cards):
    """CL-3, CL-6: double-clicking a field edits it; Enter saves it, the card keeps its
    id, place and selection state, and the store has the change."""
    ids = seed_cards(*TERMS)
    page = app()
    row(page, ids[1]).click()
    expect(page.locator("#sel")).to_have_text("1 selected of 3")

    edit(page, ids[1], 2, "новый перевод")

    expect(cell(page, ids[1], 2)).to_have_text("новый перевод")
    expect(page.locator("#cardmsg")).to_have_text("Card changed")
    assert stored(ids[1])[2] == "новый перевод"
    expect(page.locator("#body tr td:nth-child(2)")).to_have_text(
        [str(i) for i in reversed(ids)]
    )
    expect(page.locator("#sel")).to_have_text("1 selected of 3")
    expect(row(page, ids[1])).to_have_class("sel")


def test_edit_the_term(app, seed_cards):
    """CL-3: the term, shown bold, can be edited like any other field."""
    ids = seed_cards(*TERMS)
    page = app()

    edit(page, ids[0], 0, "omega")

    expect(cell(page, ids[0], 0).locator("b")).to_have_text("omega")
    assert stored(ids[0])[0] == "omega"


def test_a_refused_edit_says_why_and_keeps_the_card(app, seed_cards):
    """CL-4: a value that breaks a field rule, or another card's term, is refused with the reason."""
    ids = seed_cards(*TERMS)
    page = app()

    edit(page, ids[0], 4, "Z9")
    expect(page.locator("#cardmsg")).to_contain_text("level must be one of A1")
    assert stored(ids[0])[4] == "B2"

    cell(page, ids[0], 4).locator("textarea").press("Escape")
    edit(page, ids[0], 0, "bravo")
    expect(page.locator("#cardmsg")).to_contain_text("Another card has this term")
    assert stored(ids[0])[0] == "alpha"


def test_abandoning_an_edit_changes_nothing(app, seed_cards):
    """CL-5: Escape drops the edit; the card is as it was."""
    ids = seed_cards(*TERMS)
    page = app()

    edit(page, ids[0], 2, "не сохранять", key="Escape")

    expect(cell(page, ids[0], 2)).to_have_text("перевод alpha")
    assert stored(ids[0])[2] == "перевод alpha"


def test_leaving_a_field_saves_it(app, seed_cards):
    """CL-11: clicking elsewhere saves a changed value; an unchanged one saves nothing."""
    ids = seed_cards(*TERMS)
    page = app()

    cell(page, ids[0], 2).dblclick()
    cell(page, ids[0], 2).locator("textarea").fill("тоже сохранить")
    page.click("#cardstitle")  # leaves the cell
    expect(cell(page, ids[0], 2)).to_have_text("тоже сохранить")
    assert stored(ids[0])[2] == "тоже сохранить"
    expect(page.locator("#cardmsg")).to_have_text("Card changed")

    page.evaluate("document.getElementById('cardmsg').textContent = ''")
    cell(page, ids[1], 2).dblclick()
    page.click("#cardstitle")
    expect(cell(page, ids[1], 2)).to_have_text("перевод bravo")
    expect(page.locator("#cardmsg")).to_be_empty()


def test_tab_saves_and_moves_to_the_next_field(app, seed_cards):
    """CL-11: Tab saves the field and opens the next field of the card for editing."""
    ids = seed_cards(*TERMS)
    page = app()

    cell(page, ids[0], 2).dblclick()
    page.locator("#body textarea").fill("первый")
    page.keyboard.press("Tab")

    expect(cell(page, ids[0], 2)).to_have_text("первый")
    expect(cell(page, ids[0], 3).locator("textarea")).to_be_focused()
    assert stored(ids[0])[2] == "первый"


def test_an_empty_value_is_refused_with_the_rule(app, seed_cards):
    """CL-4, CL-11: an empty value says which rule it breaks and the editor stays open."""
    ids = seed_cards(*TERMS)
    page = app()

    edit(page, ids[0], 2, "")

    expect(page.locator("#cardmsg")).to_contain_text(
        "Russian translation must have at least 4 characters"
    )
    expect(page.locator("#cardmsg")).not_to_contain_text("undefined")
    expect(cell(page, ids[0], 2).locator("textarea")).to_be_visible()
    assert stored(ids[0])[2] == "перевод alpha"


def test_a_long_field_is_edited_in_full(app, seed_cards):
    """CL-11: the editor grows to show a long text instead of scrolling one line."""
    ids = seed_cards(*TERMS)
    page = app()
    long = "очень длинный перевод " * 12

    cell(page, ids[0], 2).dblclick()
    area = cell(page, ids[0], 2).locator("textarea")
    area.fill(long)

    assert area.evaluate("a => a.scrollHeight <= a.clientHeight + 1")
    assert area.bounding_box()["height"] > 60
    area.press("Enter")
    expect(page.locator("#cardmsg")).to_have_text("Card changed")
    assert stored(ids[0])[2] == long.strip()


def test_cards_say_they_can_be_edited(app, seed_cards):
    """CL-1: the list is under the language pair's name and the page says how to edit."""
    seed_cards(*TERMS)
    page = app()

    expect(page.locator("#cardstitle")).to_have_text("Cards: English → Russian")
    expect(page.locator("body")).to_contain_text("Double-click or double-tap a field")
    page.select_option("#plugin", label="Russian → Chinese")
    expect(page.locator("#cardstitle")).to_have_text("Cards: Russian → Chinese")


def test_keyboard_moves_selects_edits_and_deletes(app, seed_cards):
    """CL-12: rows take focus; arrows move, Space selects, Enter edits the first field,
    Delete asks to delete the selected cards."""
    ids = seed_cards(*TERMS)
    page = app()
    row(page, ids[1]).focus()

    page.keyboard.press("ArrowDown")
    expect(row(page, ids[0])).to_be_focused()
    page.keyboard.press("Space")
    expect(page.locator("#sel")).to_have_text("1 selected of 3")
    assert row(page, ids[0]).evaluate("r => r.classList.contains('sel')")

    page.keyboard.press("Enter")
    expect(cell(page, ids[0], 0).locator("textarea")).to_be_focused()
    page.keyboard.press("Escape")
    expect(row(page, ids[0])).to_be_focused()

    page.keyboard.press("Delete")
    expect(page.locator("#confirm")).to_be_visible()
    expect(page.locator("#n")).to_have_text("1")
    page.keyboard.press("Escape")
    assert len(list_cards(En2RuPlugin())) == 3


def test_outcome_messages_go_away_by_themselves(app, seed_cards):
    """CL-13: the message of an accepted edit disappears after a few seconds."""
    ids = seed_cards(*TERMS)
    page = app()

    edit(page, ids[0], 2, "новый перевод")
    expect(page.locator("#cardmsg")).to_have_text("Card changed")

    expect(page.locator("#cardmsg")).to_be_empty(timeout=8000)


def test_delete_selected_cards_after_confirming(app, seed_cards):
    """CL-7, CL-9: the question names the count; confirming removes exactly the selected
    cards from the list, the selection and the store, and the counts follow."""
    ids = seed_cards(*TERMS)
    page = app()
    row(page, ids[0]).click()
    row(page, ids[2]).click()

    page.click("#delete")
    expect(page.locator("#confirm")).to_be_visible()
    expect(page.locator("#n")).to_have_text("2")
    expect(page.locator("#deln")).to_have_text("2")
    assert len(list_cards(En2RuPlugin())) == 3  # nothing yet

    page.click("#yes")

    expect(page.locator("#cardmsg")).to_have_text("Deleted cards: 2")
    expect(page.locator("#body tr")).to_have_count(1)
    expect(row(page, ids[1])).to_be_visible()
    expect(page.locator("#sel")).to_have_text("0 selected of 1")
    assert [c[0] for c in list_cards(En2RuPlugin())] == [ids[1]]
    page.reload()
    expect(page.locator("#body tr")).to_have_count(1)


def test_keeping_the_cards_removes_nothing(app, seed_cards):
    """CL-7: answering Keep, or dismissing the question, removes nothing."""
    seed_cards(*TERMS)
    page = app()
    page.click("#all")

    page.click("#delete")
    page.click("#keep")
    expect(page.locator("#confirm")).to_be_hidden()

    page.click("#delete")
    page.keyboard.press("Escape")
    expect(page.locator("#confirm")).to_be_hidden()
    assert len(list_cards(En2RuPlugin())) == 3


def test_the_question_must_be_answered_first(app, seed_cards):
    """CL-7: while the question is open, the rest of the page cannot be used."""
    seed_cards(*TERMS)
    page = app()
    page.click("#all")
    page.click("#delete")

    assert page.evaluate("document.getElementById('confirm').matches(':modal')")
    page.keyboard.press("Space")  # cannot reach a card behind the question
    expect(page.locator("#sel")).to_have_text("3 selected of 3")
    assert len(list_cards(En2RuPlugin())) == 3


def test_delete_with_nothing_selected(app, seed_cards):
    """CL-8: nothing selected, nothing deleted, and the user is told."""
    seed_cards(*TERMS)
    page = app()

    page.click("#delete")

    expect(page.locator("#cardmsg")).to_contain_text("Nothing selected")
    expect(page.locator("#confirm")).to_be_hidden()
    assert len(list_cards(En2RuPlugin())) == 3


def test_edit_and_delete_while_a_run_is_going(app, data, seed_cards, llm):
    """CL-10: cards can be edited and deleted during a run; the run's own card is still made."""
    ids = seed_cards(*TERMS)
    data("terms.txt", "delta\n")
    llm.hold()
    page = app()
    page.select_option("#terms", "terms.txt")
    page.click("#run")
    expect(page.locator("#msg")).to_have_text("0/1 — delta")

    edit(page, ids[0], 2, "правка")
    row(page, ids[1]).click()
    page.click("#delete")
    page.click("#yes")

    expect(page.locator("#cardmsg")).to_have_text("Deleted cards: 1")
    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    assert [c[1] for c in list_cards(En2RuPlugin())] == ["alpha", "charlie", "delta"]
    assert stored(ids[0])[2] == "правка"
