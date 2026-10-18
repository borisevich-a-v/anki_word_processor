"""Round-four findings of the UX polish (change 015), as the user sees them in the browser."""

from playwright.sync_api import Page, expect

from core.store import db


def start(page: Page, terms: str = "terms.txt") -> None:
    page.select_option("#source", "")
    page.select_option("#terms", terms)
    page.click("#run")


def row(page: Page, card_id: int):
    return page.locator(f'#body tr[data-id="{card_id}"]')


def cell(page: Page, card_id: int, field: int):
    return row(page, card_id).locator(f'td[data-field="{field}"]')


def test_an_open_editor_says_the_list_waits_and_catches_up_after(
    app, data, seed_cards, llm, page: Page
):
    """CL-10: while a field is edited the list says it waits and for how many cards; once
    editing ends the list is up to date, also when the run ended meanwhile."""
    [old] = seed_cards("old")
    data("terms.txt", "alpha\nbravo\ncharlie\n")
    llm.hold(after=1)
    app()
    start(page)
    expect(page.locator("#msg")).to_have_text("1/3 — bravo")
    expect(page.locator("#body tr b")).to_have_text(["alpha", "old"])

    cell(page, old, 2).dblclick()
    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 3")
    expect(page.locator("#paused")).to_contain_text("2 new cards")
    expect(page.locator("#body tr")).to_have_count(2)

    page.keyboard.press("Escape")
    expect(page.locator("#body tr")).to_have_count(4)
    expect(page.locator("#paused")).to_be_hidden()
    expect(page.locator("#sel")).to_have_text("0 selected of 4")


def test_a_refused_edit_names_the_exercise_to_fix(app, seed_cards, page: Page):
    """CL-4: editing another field of a card whose exercise has no underscores says the
    exercise needs fixing too, and marks its cell."""
    [card] = seed_cards("naive")
    db.execute("UPDATE cards_ru SET exercise='no marks here' WHERE id=?", (card,))
    app()

    cell(page, card, 2).dblclick()
    cell(page, card, 2).locator("textarea").fill("другое слово")
    page.keyboard.press("Enter")

    expect(page.locator("#cardmsg")).to_contain_text("fix the exercise field too")
    expect(cell(page, card, 6)).to_have_class("fix")
    expect(cell(page, card, 2).locator("textarea")).to_have_class("bad")


def test_a_refusal_goes_away_by_itself(app, seed_cards, page: Page):
    """CL-13: the reason for a refused edit is gone after about eight seconds, though the
    editor stays open."""
    [card] = seed_cards("naive")
    app()
    cell(page, card, 2).dblclick()
    cell(page, card, 2).locator("textarea").fill("ab")
    page.keyboard.press("Enter")
    expect(page.locator("#cardmsg")).to_contain_text("Not changed")

    expect(page.locator("#cardmsg")).to_be_hidden(timeout=12000)
    expect(cell(page, card, 2).locator("textarea")).to_be_visible()


def test_an_edit_shows_the_field_without_surrounding_spaces(
    app, seed_cards, page: Page
):
    """CL-11: the field is saved and shown without spaces at its ends."""
    [card] = seed_cards("naive")
    app()
    cell(page, card, 2).dblclick()
    cell(page, card, 2).locator("textarea").fill("  другое  ")
    page.keyboard.press("Enter")
    expect(cell(page, card, 2)).to_have_text("другое")


def test_no_remembered_choice_does_not_dim_the_report(app, data, page: Page):
    """MC-15: with no choice made in this browser, the results are not marked as belonging
    to other choices, and what can be acted on is never dimmed."""
    data("terms.txt", "fail-one\nalpha\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Failed: 1")
    page.evaluate("localStorage.clear()")
    app()
    expect(page.locator("#terms")).to_have_value("")
    expect(page.locator("#status")).not_to_have_class("stale")
    expect(page.locator("#report")).to_have_css("opacity", "1")

    page.select_option("#terms", "terms.txt")  # a choice, the same as the report
    expect(page.locator("#status")).not_to_have_class("stale")
    data("other.txt", "x\n")
    page.locator("#terms").dispatch_event("pointerdown")
    expect(page.locator("#terms option")).to_have_count(3)
    page.select_option("#terms", "other.txt")
    expect(page.locator("#status")).to_have_class("stale")
    expect(page.locator("#again")).to_have_css("opacity", "1")


def test_a_run_in_progress_is_not_dimmed(app, data, llm, page: Page):
    """MC-15: a run in progress is never shown as belonging to other choices."""
    data("terms.txt", "alpha\nbravo\n")
    data("other.txt", "x\n")
    llm.hold()
    app()
    start(page)
    expect(page.locator("#msg")).to_have_text("0/2 — alpha")
    page.select_option("#terms", "other.txt")
    expect(page.locator("#report")).to_have_css("opacity", "1")
    llm.release()


def test_select_last_run_says_when_there_is_nothing(app, data, seed_cards, page: Page):
    """EX-4: selecting the last run says so when it selects nothing; a run that made no
    cards keeps the marks of the run before."""
    seed_cards("old")
    data("terms.txt", "alpha\n")
    app()
    page.click("#lastrun")
    expect(page.locator("#exmsg")).to_have_text("No cards of the last run in this list")

    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#body tr.new")).to_have_count(1)

    start(page)  # nothing left to make
    expect(page.locator("#report")).to_contain_text("No term is left")
    expect(page.locator("#summary")).to_contain_text("Cards made: 0")
    expect(page.locator("#summary")).to_contain_text("still mark")
    expect(page.locator("#body tr.new")).to_have_count(1)
    page.click("#lastrun")
    expect(page.locator("#sel")).to_have_text("1 selected of 2")


def test_select_last_run_says_the_run_made_no_cards(app, data, seed_cards, page: Page):
    """EX-4: when the last run made no cards, the user is told so."""
    seed_cards("alpha")
    data("terms.txt", "alpha\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 0")
    page.click("#lastrun")
    expect(page.locator("#exmsg")).to_have_text("The last run made no cards")


def test_run_again_says_how_many_terms_are_left(app, data, page: Page):
    """MC-23: the action names the file and the number of terms left, also after a cancel."""
    data("terms.txt", "fail-one\nalpha\nfail-two\n")
    app()
    start(page)
    expect(page.locator("#again")).to_have_text(
        "Run again with terms.txt: 2 terms left"
    )


def test_the_cards_title_follows_the_run(app, data, llm, page: Page):
    """MC-10: the number of terms done is repeated in the title of the cards, which stays
    in sight."""
    data("terms.txt", "alpha\nbravo\n")
    llm.hold(after=1)
    app()
    start(page)
    expect(page.locator("#cardprogress")).to_have_text("making 1/2")
    assert (
        page.evaluate(
            "getComputedStyle(document.getElementById('cardstitle')).position"
        )
        == "sticky"
    )
    llm.release()
    expect(page.locator("#cardprogress")).to_have_text("")
