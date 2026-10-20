"""The lists of files follow the data folder by themselves (change 018), in the browser."""

from playwright.sync_api import Page, expect


def test_a_file_added_meanwhile_is_there_when_going_to_choose(app, data, page: Page):
    """MC-24: no button; pressing on the terms choice reads the folder again."""
    data("terms.txt", "alpha\n")
    app()
    expect(page.locator("#refresh")).to_have_count(0)
    expect(page.locator("#terms option")).to_have_text(["Choose a file…", "terms.txt"])

    data("later.txt", "bravo\n")
    page.locator("#source").dispatch_event("pointerdown")
    expect(page.locator("#source option")).to_have_text(
        ["(none)", "later.txt", "terms.txt"]
    )
    expect(page.locator("#terms option")).to_have_text(
        ["Choose a file…", "later.txt", "terms.txt"]
    )


def test_a_file_added_meanwhile_is_found_on_return_to_the_page(app, data, page: Page):
    """MC-24: coming back to the window reads the folder again."""
    data("terms.txt", "alpha\n")
    app()
    data("later.txt", "bravo\n")
    page.evaluate("window.dispatchEvent(new Event('focus'))")
    expect(page.locator("#terms option")).to_have_text(
        ["Choose a file…", "later.txt", "terms.txt"]
    )


def test_choices_are_kept_and_a_removed_file_is_unchosen(app, data, page: Page):
    """MC-24: the chosen files stay chosen when the lists change; a file removed from the
    folder is no longer chosen."""
    data("terms.txt", "alpha\n")
    data("src.txt", "x\n")
    app()
    page.select_option("#terms", "terms.txt")
    page.select_option("#source", "src.txt")

    data("new.txt", "y\n")
    page.locator("#terms").dispatch_event("pointerdown")
    expect(page.locator("#terms option")).to_have_count(4)
    expect(page.locator("#terms")).to_have_value("terms.txt")
    expect(page.locator("#source")).to_have_value("src.txt")

    (data("src.txt", "x\n")).unlink()
    page.locator("#terms").dispatch_event("pointerdown")
    expect(page.locator("#source option")).to_have_count(3)
    expect(page.locator("#source")).to_have_value("")
    expect(page.locator("#terms")).to_have_value("terms.txt")


def test_nothing_is_replaced_when_the_files_are_the_same(app, data, page: Page):
    """MC-24: a list that has not changed is left alone (an open choice is not disturbed)."""
    data("terms.txt", "alpha\n")
    app()
    page.evaluate(
        "document.querySelector('#terms option:last-child').dataset.mark = '1'"
    )
    page.locator("#terms").dispatch_event("pointerdown")
    page.wait_for_timeout(300)
    expect(page.locator("#terms option[data-mark]")).to_have_count(1)


def test_the_hint_goes_when_the_first_file_appears_and_the_run_works(
    app, data, page: Page
):
    """MC-24: the first-use hint disappears by itself and the new file can be run."""
    app()
    expect(page.locator("#filehint")).to_contain_text("shows up in the lists by itself")
    data("terms.txt", "astray\n")
    page.locator("#terms").focus()
    expect(page.locator("#filehint")).to_be_empty()
    page.select_option("#terms", "terms.txt")
    page.click("#run")
    expect(page.locator("#report")).to_contain_text("terms.txt")


def test_the_same_file_in_both_lists_is_still_refused_after_a_refresh(
    app, data, page: Page
):
    """MC-24, MC-1: refreshing keeps the check that terms and source differ."""
    data("terms.txt", "alpha\n")
    app()
    page.select_option("#terms", "terms.txt")
    page.select_option("#source", "terms.txt")
    page.locator("#terms").dispatch_event("pointerdown")
    page.wait_for_timeout(300)
    expect(page.locator("#samewarn")).to_contain_text("must be different")
    expect(page.locator("#run")).to_be_disabled()
