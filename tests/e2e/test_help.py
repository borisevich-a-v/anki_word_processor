"""Help (change 017), as the user sees it in the browser."""

from playwright.sync_api import Page, expect


def test_the_page_has_no_tips_and_the_button_opens_the_help(
    app, seed_cards, page: Page
):
    """HP-1, HP-2: no tips on the page; the help button shows them, a close button hides them."""
    seed_cards("alpha")
    app()
    expect(page.locator("#help")).to_be_hidden()
    expect(page.locator("main")).not_to_contain_text("Double-click or double-tap")
    expect(page.locator("details#tips")).to_have_count(0)
    page.click("#helpbtn")
    expect(page.locator("#help")).to_be_visible()
    expect(page.locator("#help")).to_contain_text("Click or tap a card to select it")
    expect(page.locator("#help")).to_contain_text("A green bar on the left")
    page.click("#helpclose")
    expect(page.locator("#help")).to_be_hidden()


def test_f1_opens_and_closes_the_help_and_escape_closes_it(app, seed_cards, page: Page):
    """HP-1: F1 does what the button does; F1 or Escape closes the help."""
    seed_cards("alpha")
    app()
    page.keyboard.press("F1")
    expect(page.locator("#help")).to_be_visible()
    page.keyboard.press("F1")
    expect(page.locator("#help")).to_be_hidden()
    page.keyboard.press("F1")
    expect(page.locator("#help")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#help")).to_be_hidden()


def test_help_does_not_disturb_the_list(app, seed_cards, page: Page):
    """HP-6: opening help changes no selection; F1 over an open edit opens nothing."""
    [card] = seed_cards("alpha")
    app()
    page.click("#all")
    expect(page.locator("#sel")).to_have_text("1 selected of 1")
    page.keyboard.press("F1")
    page.keyboard.press("Escape")
    expect(page.locator("#sel")).to_have_text("1 selected of 1")

    page.locator(f'#body tr[data-id="{card}"] td[data-field="2"]').dblclick()
    page.keyboard.press("F1")
    expect(page.locator("#help")).to_be_hidden()
    expect(page.locator("#body textarea")).to_be_visible()


def test_help_explains_the_whole_flow(app, seed_cards, page: Page):
    """HP-3, HP-4, HP-7: help covers files, making cards, selecting, editing, deleting and exporting."""
    seed_cards("alpha")
    app()
    page.keyboard.press("F1")
    for text in (
        "terms file",
        "source text",
        "Make cards",
        "Cancel",
        "Select last run",
        "Double-click",
        "Delete selected",
        "Export selected",
        "Import",
        "Enter saves",
    ):
        expect(page.locator("#help")).to_contain_text(text)


def test_help_scrolls_and_fits_a_phone(app, seed_cards, page: Page):
    """HP-5: on a narrow screen help fits the screen, scrolls, and the close button is in reach."""
    seed_cards("alpha")
    page.set_viewport_size({"width": 380, "height": 600})
    app()
    page.click("#helpbtn")
    box = page.locator("#help").bounding_box()
    assert (
        box
        and box["x"] >= 0
        and box["x"] + box["width"] <= 380
        and box["height"] <= 600
    )
    expect(page.locator("#helpclose")).to_be_in_viewport()
    assert page.evaluate(
        "(b => b.scrollHeight > b.clientHeight)(document.querySelector('#help .helpbody'))"
    )
    page.click("#helpclose")
    expect(page.locator("#help")).to_be_hidden()


def test_help_opens_at_its_start(app, seed_cards, page: Page):
    """HP-5: help is read from the start, also on a small screen."""
    seed_cards("alpha")
    page.set_viewport_size({"width": 380, "height": 500})
    app()
    page.keyboard.press("F1")
    expect(page.locator("#helptitle")).to_be_in_viewport()
    assert page.evaluate("document.querySelector('#help .helpbody').scrollTop") == 0


def test_scripts_are_revalidated_so_a_browser_never_runs_an_old_one(server):
    """HP-1 (bug fix): Safari kept an old script after an update, so the help button did nothing."""
    from urllib.request import urlopen

    with urlopen(server + "/static/app.js") as res:
        assert res.headers["Cache-Control"] == "no-cache"


def test_a_click_outside_closes_the_help_but_one_inside_does_not(
    app, seed_cards, page: Page
):
    """HP-1: clicking outside help closes it; clicking inside, margins included, does not."""
    seed_cards("alpha")
    app()
    page.click("#helpbtn")
    box = page.locator("#help").bounding_box()
    assert box
    page.mouse.click(box["x"] + 4, box["y"] + 4)  # the dialog's own padding
    page.locator("#helptitle").click()
    expect(page.locator("#help")).to_be_visible()
    page.mouse.click(box["x"] - 10, box["y"] + 100)
    expect(page.locator("#help")).to_be_hidden()
    expect(page.locator("#sel")).to_have_text("0 selected of 1")
