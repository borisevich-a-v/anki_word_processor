"""Round-three findings of the UX polish (change 014), as the user sees them in the browser."""

from playwright.sync_api import Page, expect

from core.card_library import list_cards
from core.languages import En2RuPlugin

TERMS = ("alpha", "bravo", "charlie")


def start(page: Page, terms: str = "terms.txt", source: str = "") -> None:
    page.select_option("#source", source)
    page.select_option("#terms", terms)
    page.click("#run")


def row(page: Page, card_id: int):
    return page.locator(f'#body tr[data-id="{card_id}"]')


def cell(page: Page, card_id: int, field: int):
    return row(page, card_id).locator(f'td[data-field="{field}"]')


def box(page: Page, selector: str) -> dict:
    found = page.locator(selector).bounding_box()
    assert found
    return dict(found)


def no_sideways_scroll(page: Page) -> bool:
    return page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )


# ---- the table follows the run


def test_cards_appear_in_the_table_as_they_are_made(
    app, data, seed_cards, llm, page: Page
):
    """CL-10: while a run goes on, each card shows up when its term is finished, and the
    selection made meanwhile stays."""
    [old] = seed_cards("old")
    data("terms.txt", "alpha\nbravo\ncharlie\n")
    llm.hold(after=1)
    app()
    row(page, old).click()
    start(page)

    expect(page.locator("#msg")).to_have_text("1/3 — bravo")
    expect(page.locator("#body tr b")).to_have_text(["alpha", "old"])
    expect(page.locator("#sel")).to_have_text("1 selected of 2")
    expect(row(page, old).locator("input")).to_be_checked()

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 3")
    expect(page.locator("#body tr b")).to_have_text(
        ["charlie", "bravo", "alpha", "old"]
    )
    expect(page.locator("#sel")).to_have_text("1 selected of 4")


def test_the_table_does_not_replace_an_open_editor(
    app, data, seed_cards, llm, page: Page
):
    """CL-10, CL-11: a field being edited stays open while the run adds cards; the list
    catches up when the editor is closed."""
    [old] = seed_cards("old")
    data("terms.txt", "alpha\nbravo\n")
    llm.hold()
    app()
    start(page)
    expect(page.locator("#msg")).to_have_text("0/2 — alpha")
    cell(page, old, 1).dblclick()
    area = cell(page, old, 1).locator("textarea")
    area.fill("/typed/")

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(area).to_be_visible()
    assert page.locator("#body tr").count() == 1

    area.press("Escape")
    expect(page.locator("#body tr b")).to_have_text(["bravo", "alpha", "old"])


# ---- cards that break the exercise rule


def test_a_card_without_underscores_fails_with_a_plain_reason(app, data, page: Page):
    """MC-7, MC-8: the exercise has to have its translation between underscores; a term
    whose card lacks them is shown as failed, with the reason, and nothing is saved."""
    data("terms.txt", "plain-exercise\nalpha\n")
    app()

    start(page)

    expect(page.locator("#failed")).to_contain_text(
        "plain-exercise — exercise must have its Russian translation set between underscores"
    )
    assert [c[1] for c in list_cards(En2RuPlugin())] == ["alpha"]


# ---- run again


def test_run_again_uses_the_choices_of_the_report(app, data, page: Page):
    """MC-23: whatever is chosen now, even nothing in a browser that remembers nothing,
    run again repeats the run the report is about."""
    data("terms.txt", "fail-one\nfail-two\n")
    data("other.txt", "bravo\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Failed: 2")

    page.select_option("#terms", "other.txt")
    page.click("#again")
    expect(page.locator("#summary")).to_contain_text("Failed: 2")
    expect(page.locator("#report")).to_contain_text("terms.txt")

    page.evaluate("localStorage.clear()")
    app()
    expect(page.locator("#terms")).to_have_value("")
    expect(page.locator("#again")).to_contain_text("terms.txt")
    page.click("#again")
    expect(page.locator("#summary")).to_contain_text("Failed: 2")
    expect(page.locator("#msg")).not_to_contain_text("No terms file chosen")


# ---- cancel


def test_cancelling_shows_a_busy_state_and_cannot_be_repeated(
    app, data, llm, page: Page
):
    """MC-17: once cancelled, the user sees the term in hand being finished, cancel is
    off and the bar is busy, until the run stops."""
    data("terms.txt", "alpha\nbravo\n")
    llm.hold()
    app()
    start(page)
    expect(page.locator("#msg")).to_have_text("0/2 — alpha")

    page.click("#cancel")

    expect(page.locator("#cancel")).to_be_disabled()
    expect(page.locator("#msg")).to_contain_text("Finishing the term in hand")
    expect(page.locator("#msg")).not_to_contain_text("Cancelling")
    expect(page.locator("#msg")).to_contain_text("alpha")
    assert page.locator("#bar").get_attribute("value") is None  # busy, not a count

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cancelled: 1")
    expect(page.locator("#cancel")).to_have_count(0)


# ---- deleting


def test_the_delete_question_names_the_cards(app, seed_cards, page: Page):
    """CL-7: one card is "1 card" and is named; several name the first few and say how
    many more."""
    ids = seed_cards("alpha", "bravo", "charlie", "delta", "echo")
    app()

    row(page, ids[0]).click()
    page.click("#delete")
    question = page.locator("#confirmq")
    expect(question).to_contain_text("Delete 1 card ")
    expect(question).to_contain_text("alpha")
    expect(question).not_to_contain_text("cards")
    page.keyboard.press("Escape")

    page.click("#all")
    page.click("#delete")
    expect(question).to_contain_text("Delete 5 cards")
    expect(question).to_contain_text("echo, delta, charlie and 2 more")


# ---- messages


def test_the_error_message_does_not_cover_the_rows_below(app, seed_cards, page: Page):
    """CL-13: the reason for a refused edit sits away from the card being edited and
    from the cards under it."""
    ids = seed_cards(*TERMS)
    app()
    cell(page, ids[0], 2).dblclick()
    area = cell(page, ids[0], 2).locator("textarea")
    area.fill("")
    area.press("Enter")

    toast = page.locator("#cardmsg")
    expect(toast).to_contain_text("Not changed")
    shown, below = box(page, "#cardmsg"), box(page, f'#body tr[data-id="{ids[1]}"]')
    assert shown["y"] + shown["height"] < below["y"]


def test_the_export_message_goes_when_the_selection_or_the_cards_change(
    app, seed_cards, page: Page
):
    """EX-7: the result of an export is gone after a change of the selection, an edit or
    a delete; it is short."""
    ids = seed_cards(*TERMS)
    page.add_init_script("delete window.showSaveFilePicker")
    app()
    page.click("#all")

    def export() -> None:
        with page.expect_download():
            page.click("#export")
        expect(page.locator("#exmsg")).to_contain_text("Saved 3 cards to Downloads as ")

    export()
    assert box(page, "#exmsg")["height"] < 30  # one line
    row(page, ids[0]).click()
    expect(page.locator("#exmsg")).to_have_text("")

    page.click("#all")
    export()
    cell(page, ids[0], 5).dblclick()
    cell(page, ids[0], 5).locator("textarea").fill("changed")
    cell(page, ids[0], 5).locator("textarea").press("Enter")
    expect(page.locator("#cardmsg")).to_have_text("Card changed")
    expect(page.locator("#exmsg")).to_have_text("")

    page.click("#all")
    export()
    page.click("#delete")
    page.click("#yes")
    expect(page.locator("#cardmsg")).to_contain_text("Deleted cards: 3")
    expect(page.locator("#exmsg")).to_have_text("")


# ---- the report


def test_an_empty_file_says_only_that_it_has_no_terms(app, data, page: Page):
    """MC-15: no counts are given for a file without terms."""
    data("terms.txt", "\n\n")
    app()

    start(page)

    expect(page.locator("#report")).to_contain_text("The file has no terms")
    expect(page.locator("#report")).not_to_contain_text("Terms in the file")


def test_every_term_with_a_card_still_says_cards_made_none(
    app, data, seed_cards, page: Page
):
    """MC-11: the number of cards made is given also when it is none."""
    seed_cards("alpha")
    data("terms.txt", "alpha\n")
    app()

    start(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 0")


# ---- layout


def test_no_blank_gap_between_the_choices_and_the_report(app, data, page: Page):
    """Layout: lines for messages take room only while they have text."""
    data("terms.txt", "alpha\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    for width in (1280, 420):
        size = {"width": width, "height": 800}
        page.set_viewport_size({"width": width, "height": 800})
        page.reload()
        expect(page.locator("#report")).to_contain_text("terms.txt")
        run = box(page, "#run")
        gap = box(page, "#report p.for")["y"] - (run["y"] + run["height"])
        assert gap < 24, (size, gap)


def test_empty_message_lines_take_no_room_on_a_phone(app, seed_cards, page: Page):
    """Layout: the empty export message does not add a line under the buttons."""
    seed_cards(*TERMS)
    page.set_viewport_size({"width": 420, "height": 800})
    app()

    assert box(page, ".bar2")["height"] < 100


def test_the_old_results_note_is_not_stretched_on_a_wide_screen(app, data, page: Page):
    """Layout: at 1920 px the note about old results keeps a readable width."""
    data("terms.txt", "alpha\n")
    data("other.txt", "bravo\n")
    page.set_viewport_size({"width": 1920, "height": 900})
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")

    page.select_option("#terms", "other.txt")

    expect(page.locator("#stale")).to_be_visible()
    assert box(page, "#stale")["width"] < 900


def test_a_phone_shows_every_field_of_a_card_without_sideways_scrolling(
    app, seed_cards, page: Page
):
    """Layout: at 420 px each card is a stack of labelled fields inside the screen."""
    ids = seed_cards(*TERMS)
    page.set_viewport_size({"width": 420, "height": 800})
    app()

    assert no_sideways_scroll(page)
    assert page.evaluate("list.scrollWidth <= list.clientWidth")
    listing = box(page, "#list")
    for field in range(7):
        found = box(page, f'#body tr[data-id="{ids[0]}"] td[data-field="{field}"]')
        assert found["x"] >= listing["x"]
        assert found["x"] + found["width"] <= listing["x"] + listing["width"] + 1
    assert cell(page, ids[0], 6).get_attribute("data-label") == "exercise"
    cell(page, ids[0], 1).dblclick()  # editing still works in the stacked layout
    expect(cell(page, ids[0], 1).locator("textarea")).to_be_visible()
