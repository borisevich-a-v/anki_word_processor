"""setup.md SU-7: how the stage profile shows on the page."""

from playwright.sync_api import expect

from web import app as ui


def test_stage_page_says_so(app, monkeypatch):
    """SU-7: the page of the stage profile has a banner and a title prefix."""
    monkeypatch.setitem(ui.templates.env.globals, "stage", True)
    page = app()

    expect(page.locator("#stage")).to_be_visible()
    expect(page).to_have_title("[STAGE] Anki card builder")


def test_prod_page_has_no_marker(app):
    """SU-7: the real profile's page is unmarked."""
    page = app()

    expect(page.locator("#stage")).to_have_count(0)
    expect(page).to_have_title("Anki card builder")
