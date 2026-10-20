"""Round-two findings of the UX polish (change 013), as the user sees them in the browser."""

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


# ---- the table follows a finished run


def test_every_answer_of_a_finished_run_refreshes_the_table(app, data, page: Page):
    """EX-4: cancelling a run that has already finished still tells the page to refresh
    the table, so the report and the table never disagree."""
    data("terms.txt", "alpha\nbravo\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")

    answer = page.request.post(page.url + "cancel")

    assert answer.headers.get("hx-trigger") == "run-finished"


# ---- the report says what it is about


def test_report_names_its_file_and_pair_and_the_ignored_repeats(app, data, page: Page):
    """MC-15: the report says which file and pair it is about and counts ignored repeats."""
    data("terms.txt", "alpha\nbravo\nalpha\nalpha\n")
    app()

    start(page)

    report = page.locator("#report")
    expect(report).to_contain_text("terms.txt")
    expect(report).to_contain_text("English → Russian")
    expect(report).to_contain_text("Terms in the file: 2")
    expect(report).to_contain_text("2 repeated lines ignored")


def test_changing_the_choices_marks_the_old_report(app, data, page: Page):
    """MC-15: after another file or pair is chosen the report and summary are marked as
    belonging to the earlier choices; choosing the same again removes the mark."""
    data("terms.txt", "alpha\n")
    data("other.txt", "bravo\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#status")).not_to_have_class("stale")

    page.select_option("#terms", "other.txt")
    expect(page.locator("#status")).to_have_class("stale")
    expect(page.locator("#stale")).to_be_visible()
    expect(page.locator("#stale")).to_contain_text("terms.txt")

    page.select_option("#terms", "terms.txt")
    expect(page.locator("#status")).not_to_have_class("stale")
    page.select_option("#plugin", "1")
    expect(page.locator("#status")).to_have_class("stale")


def test_an_empty_file_has_no_terms_and_no_count(app, data, page: Page):
    """MC-15, MC-11: a file without terms says so; it does not claim cards were made."""
    data("terms.txt", "\n  \n")
    app()

    start(page)

    expect(page.locator("#report")).to_contain_text("The file has no terms")
    expect(page.locator("#report")).not_to_contain_text("No term is left")
    expect(page.locator("#summary")).not_to_contain_text("Cards made")


# ---- layout


def test_a_long_failed_term_stays_inside_its_section(app, data, page: Page):
    """Layout: a 150-character failed term wraps instead of overflowing."""
    data("terms.txt", "fail-" + "x" * 145 + "\n")
    app()

    start(page)

    expect(page.locator("#failed")).to_be_visible()
    over = page.evaluate(
        """() => { const s = document.querySelector('section').getBoundingClientRect();
        return [...document.querySelectorAll('#failed li')]
          .some(li => li.getBoundingClientRect().right > s.right) }"""
    )
    assert not over
    assert no_sideways_scroll(page)


def test_the_page_does_not_scroll_sideways_on_a_narrow_screen(
    app, seed_cards, page: Page
):
    """Layout: at 420 px wide only the table scrolls sideways, not the page; the first
    column stays in view and the table says that it scrolls."""
    seed_cards(*TERMS)
    page.set_viewport_size({"width": 420, "height": 800})
    app()

    assert no_sideways_scroll(page)
    assert page.evaluate(
        "list.scrollWidth <= list.clientWidth"
    )  # nothing scrolls sideways
    page.evaluate("document.getElementById('list').scrollLeft = 300")
    box = page.locator("#body tr td").first.bounding_box()
    list_box = page.locator("#list").bounding_box()
    assert box and list_box and box["x"] < list_box["x"] + 60
    separators = page.locator(".sep")
    assert separators.count() == 0 or not separators.first.is_visible()


def test_table_headers_do_not_break_inside_a_word(app, seed_cards, page: Page):
    """Layout: a very long cell does not squeeze the headers into broken words."""
    ids = seed_cards(*TERMS)
    app()
    cell(page, ids[0], 5).dblclick()
    box = cell(page, ids[0], 5).locator("textarea")
    box.fill("x" * 120)
    box.press("Enter")
    expect(page.locator("#cardmsg")).to_have_text("Card changed")
    heights = page.evaluate(
        "[...document.querySelectorAll('thead th')].map(th => th.getBoundingClientRect().height)"
    )
    assert max(heights) < 40  # every header on one line


def test_the_id_range_does_not_move_the_cards(app, data, page: Page):
    """Layout: opening the id range does not shift the card list (the warning line of
    the choices takes room only while it has text, change 014)."""
    data("terms.txt", "alpha\n")
    app()
    top = box(page, "#cardstitle")["y"]
    page.select_option("#terms", "terms.txt")
    page.select_option("#source", "terms.txt")
    expect(page.locator("#samewarn")).to_be_visible()
    top = box(page, "#cardstitle")["y"]
    bar = box(page, ".bar")["height"]
    page.click(".range summary")
    expect(page.locator("#range")).to_be_visible()
    assert box(page, ".bar")["height"] == bar
    assert box(page, "#cardstitle")["y"] == top


def test_the_export_message_sits_beside_export(app, seed_cards, page: Page):
    """EX-7: the result of an export appears right next to the Export button."""
    seed_cards(*TERMS)
    page.add_init_script("delete window.showSaveFilePicker")
    app()
    page.click("#all")

    with page.expect_download():
        page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Saved 3 cards")
    msg = page.locator("#exmsg").bounding_box()
    export = page.locator("#export").bounding_box()
    assert msg and export
    assert (
        abs((msg["y"] + msg["height"] / 2) - (export["y"] + export["height"] / 2)) < 30
    )
    assert abs(msg["x"] - (export["x"] + export["width"])) < 40


# ---- selecting


def test_new_cards_stay_marked_when_selected(app, data, page: Page):
    """EX-4: a card of the last run is marked as new while it is selected as well."""
    data("terms.txt", "alpha\n")
    app()
    start(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    page.click("#lastrun")
    expect(page.locator("#sel")).to_have_text("1 selected of 1")

    first = page.locator("#body tr").first
    expect(first).to_have_class("new sel")
    mark = first.locator("td").first.evaluate("e => getComputedStyle(e).boxShadow")
    assert mark != "none"


def test_shift_click_does_not_select_page_text(app, seed_cards, page: Page):
    """EX-10: Shift-clicking a stretch of cards does not also select the text."""
    ids = seed_cards(*TERMS)
    app()
    row(page, ids[0]).click()
    row(page, ids[2]).click(modifiers=["Shift"])

    assert page.evaluate("window.getSelection().toString()") == ""


# ---- deleting and editing


def test_the_question_says_when_it_is_every_card(app, seed_cards, page: Page):
    """CL-7: deleting every card of the pair is stated plainly in the question."""
    seed_cards(*TERMS)
    app()
    page.click("#all")
    page.click("#delete")
    expect(page.locator("#allwarn")).to_be_visible()
    expect(page.locator("#allwarn")).to_contain_text("every card")
    page.click("#keep")

    row(page, list_cards(En2RuPlugin())[0][0]).click()  # leaves two selected
    page.click("#delete")
    expect(page.locator("#allwarn")).to_be_hidden()


def test_focus_goes_to_the_nearest_card_after_a_delete(app, seed_cards, page: Page):
    """CL-12: after deleting, focus is on the card nearest to the deleted ones, or on the
    delete button when no card is left."""
    ids = seed_cards(*TERMS)
    app()
    row(page, ids[1]).click()
    page.click("#delete")
    page.click("#yes")
    expect(page.locator("#body tr")).to_have_count(2)
    assert page.evaluate("document.activeElement.dataset.id") == str(ids[0])

    page.click("#all")
    page.click("#delete")
    page.click("#yes")
    expect(page.locator("#body tr")).to_have_count(0)
    assert page.evaluate("document.activeElement.id") == "delete"


def test_leaving_a_refused_edit_abandons_it(app, seed_cards, page: Page):
    """CL-11: clicking elsewhere with a refused value ends the edit, keeps the card and
    says so; nothing starts over an open editor."""
    ids = seed_cards(*TERMS)
    app()
    cell(page, ids[0], 4).dblclick()
    box = cell(page, ids[0], 4).locator("textarea")
    box.fill("Z9")

    page.click("#cardstitle")

    expect(cell(page, ids[0], 4).locator("textarea")).to_have_count(0)
    expect(cell(page, ids[0], 4)).to_have_text("B2")
    expect(page.locator("#cardmsg")).to_contain_text(
        "Not changed: level must be one of"
    )
    assert list_cards(En2RuPlugin())[0][5] == "B2"


def test_delete_while_editing_saves_or_abandons_the_edit_first(
    app, seed_cards, page: Page
):
    """CL-11: pressing Delete over an open editor ends the edit before the question."""
    ids = seed_cards(*TERMS)
    app()
    row(page, ids[2]).click()
    cell(page, ids[0], 4).dblclick()
    cell(page, ids[0], 4).locator("textarea").fill("Z9")

    page.click("#delete")

    expect(page.locator("#body textarea")).to_have_count(0)
    expect(page.locator("#confirm")).to_be_visible()


def test_a_message_can_be_closed(app, seed_cards, page: Page):
    """CL-13: an error message that stays can be closed with its button or with Escape."""
    ids = seed_cards(*TERMS)
    app()
    for close in ("button", "escape"):
        cell(page, ids[0], 4).dblclick()
        box = cell(page, ids[0], 4).locator("textarea")
        box.fill("Z9")
        box.press("Enter")
        expect(page.locator("#cardmsg")).to_contain_text("Not changed")
        page.click("#cardstitle")  # leaves the edit; the message stays
        expect(page.locator("#cardmsg")).to_contain_text("Not changed")
        if close == "button":
            page.click("#cardmsg button")
        else:
            page.keyboard.press("Escape")
        expect(page.locator("#cardmsg")).to_be_empty()


# ---- the run form


def test_enter_in_a_choice_does_not_start_a_run(app, data, page: Page):
    """Accidental runs: Enter in a choice never starts a run."""
    data("terms.txt", "alpha\n")
    app()
    page.select_option("#terms", "terms.txt")
    page.focus("#terms")
    page.keyboard.press("Enter")
    page.wait_for_timeout(700)

    expect(page.locator("#status")).to_have_attribute("data-idle", "")
    assert list_cards(En2RuPlugin()) == []
