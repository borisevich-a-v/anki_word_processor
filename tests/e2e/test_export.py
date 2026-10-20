"""export.md, as the user sees it in the browser."""

import re

from playwright.sync_api import Page, expect

from core import config
from core.store import db

TERMS = ("alpha", "bravo", "charlie", "delta", "echo")


# A native save dialog cannot be driven, so the page's dialog is replaced by one that
# records what it was asked for and "saves" under `chosen` (or is left, when null).
STUB_DIALOG = """chosen => {
  window.dialogCalls = []; window.saved = null;
  window.showSaveFilePicker = async options => {
    window.dialogCalls.push(options);
    if (chosen === null) throw new DOMException('left', 'AbortError');
    return { name: chosen, createWritable: async () => ({
      write: async blob => { window.saved = await blob.text(); }, close: async () => {} }) };
  };
}"""


def stub_dialog(page: Page, chosen: str | None = "mine.tsv") -> None:
    page.evaluate(STUB_DIALOG, chosen)


def saved(page: Page) -> str:
    expect(page.locator("#exmsg")).not_to_be_empty()
    return page.evaluate("window.saved")


def row(page: Page, card_id: int):
    return page.locator(f'#body tr[data-id="{card_id}"]')


def selected_ids(page: Page) -> list[int]:
    return [
        int(i)
        for i in page.locator("#body tr.sel").evaluate_all(
            "rows => rows.map(r => r.dataset.id)"
        )
    ][::-1]  # the list shows the newest first; the ids are returned oldest first


def test_card_list_shows_all_cards_newest_first(app, seed_cards):
    """CL-1, CL-2: every card is listed with its id and fields, the newest first."""
    ids = seed_cards(*TERMS)
    page = app()

    expect(page.locator("#body tr")).to_have_count(5)
    expect(page.locator("#body tr td:nth-child(2)")).to_have_text(
        [str(i) for i in reversed(ids)]
    )
    assert ids == sorted(set(ids))
    expect(row(page, ids[0]).locator("td")).to_have_text(
        [
            "",
            str(ids[0]),
            "alpha",
            "/alpha/",
            "перевод alpha",
            "meaning of alpha",
            "B2",
            "An example with alpha",
            "An example with _alpha_",
        ]
    )
    expect(page.locator("thead th")).to_have_text(
        [
            "select",
            "id",
            "term",
            "phonetic transcription",
            "Russian translation",
            "explanation",
            "level",
            "example",
            "exercise",
        ]
    )


def test_card_list_follows_the_language_pair(app, seed_cards):
    """CL-1: only the cards of the chosen language pair are listed, under its own fields."""
    seed_cards("alpha")
    page = app()
    expect(page.locator("#body tr")).to_have_count(1)

    page.select_option("#plugin", label="Russian → Chinese")
    expect(page.locator("#body tr")).to_have_count(0)
    expect(page.locator("thead th")).to_have_count(0)  # CL-1: no cards, no headings

    page.select_option("#plugin", label="English → Russian")
    expect(page.locator("#body tr")).to_have_count(1)
    expect(page.locator("thead th")).to_have_text(
        [
            "select",
            "id",
            "term",
            "phonetic transcription",
            "Russian translation",
            "explanation",
            "level",
            "example",
            "exercise",
        ]
    )


def test_select_and_unselect_a_single_card(app, seed_cards):
    """EX-3, EX-10: clicking a card selects it, clicking again unselects; the count
    follows, next to the size of the list."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#sel")).to_have_text("0 selected of 5")

    row(page, ids[1]).click()
    expect(page.locator("#sel")).to_have_text("1 selected of 5")
    expect(page.locator("#export")).to_contain_text("Export selected (1)")
    expect(page.locator("#delete")).to_contain_text("Delete selected (1)")
    expect(row(page, ids[1]).locator("input")).to_be_checked()
    assert selected_ids(page) == [ids[1]]

    row(page, ids[1]).click()
    expect(page.locator("#sel")).to_have_text("0 selected of 5")
    assert selected_ids(page) == []


def test_select_a_stretch_between_two_clicked_cards(app, seed_cards):
    """EX-3, EX-10: click one card, shift-click another: everything between is selected."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)

    row(page, ids[1]).click()
    row(page, ids[3]).click(modifiers=["Shift"])

    expect(page.locator("#sel")).to_have_text("3 selected of 5")
    assert selected_ids(page) == ids[1:4]


def test_select_a_range_of_ids(app, seed_cards):
    """EX-3: a from-to range of ids selects exactly those cards."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)

    page.click(".range summary")  # the id range is tucked away
    page.fill("#from", str(ids[2]))
    page.fill("#to", str(ids[4]))
    page.click("#range")

    expect(page.locator("#sel")).to_have_text("3 selected of 5")
    assert selected_ids(page) == ids[2:5]


def test_shift_click_never_unselects(app, seed_cards):
    """EX-10: a Shift-click over selected cards leaves them selected."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)
    row(page, ids[1]).click()
    row(page, ids[3]).click(modifiers=["Shift"])

    row(page, ids[1]).click(modifiers=["Shift"])

    expect(page.locator("#sel")).to_have_text("3 selected of 5")
    assert selected_ids(page) == ids[1:4]


def test_range_of_ids_can_be_open_and_replaces_the_selection(app, seed_cards):
    """EX-10: a range without its first id starts at the oldest card, without its last
    id it runs to the newest; a range replaces the selection."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)
    row(page, ids[0]).click()
    page.click(".range summary")

    page.fill("#from", str(ids[3]))
    page.click("#range")
    expect(page.locator("#sel")).to_have_text("2 selected of 5")
    assert selected_ids(page) == ids[3:]

    page.fill("#from", "")
    page.fill("#to", str(ids[1]))
    page.click("#range")
    expect(page.locator("#sel")).to_have_text("2 selected of 5")
    assert selected_ids(page) == ids[:2]


def test_select_all_and_clear(app, seed_cards):
    """EX-3: all cards can be selected at once, and the selection cleared."""
    ids = seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)

    page.click("#all")
    expect(page.locator("#sel")).to_have_text("5 selected of 5")
    assert selected_ids(page) == ids

    page.click("#none")
    expect(page.locator("#sel")).to_have_text("0 selected of 5")


def test_cards_of_a_run_are_new_and_not_selected(app, seed_cards, data):
    """EX-4, EX-3: after a run its cards are marked new and nothing is selected for the
    user; a selection made before stays; "last run" selects the new cards."""
    old = seed_cards("alpha", "bravo")
    data("terms.txt", "charlie\ndelta\n")
    page = app()
    row(page, old[1]).click()
    page.select_option("#terms", "terms.txt")
    page.click("#run")

    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#sel")).to_have_text("1 selected of 4")
    expect(page.locator("#body tr.new b")).to_have_text(["delta", "charlie"])
    expect(page.locator("#body tr.sel b")).to_have_text(["bravo"])

    page.click("#none")
    expect(page.locator("#delete")).to_contain_text("Delete selected (0)")
    row(page, old[0]).click()
    page.click("#lastrun")
    expect(page.locator("#body tr.sel b")).to_have_text(["delta", "charlie"])


def test_nothing_is_selected_when_the_page_is_opened_later(app, data):
    """EX-4: after a reload the cards of the last run are still marked new, but nothing
    is selected, so an old selection cannot be exported or deleted by mistake."""
    data("terms.txt", "charlie\ndelta\n")
    page = app()
    page.select_option("#terms", "terms.txt")
    page.click("#run")
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#sel")).to_have_text("0 selected of 2")
    page.click("#lastrun")
    expect(page.locator("#sel")).to_have_text("2 selected of 2")

    page = app()

    expect(page.locator("#body tr.new b")).to_have_text(["delta", "charlie"])
    expect(page.locator("#sel")).to_have_text("0 selected of 2")
    expect(page.locator("#export")).to_contain_text("Export selected (0)")


def test_run_finishing_while_another_language_pair_is_shown(app, data, llm):
    """EX-4: the list of the other pair and its selection are left as they are; the
    cards of the run are marked new when the user goes back to its pair."""
    db.execute(
        "INSERT INTO cards_cn (word, first_form, chinese_translation, explanation, example)"
        " VALUES ('кузнец', 'кузнец', '铁匠', 'мастер', 'пример')"
    )
    data("terms.txt", "charlie\ndelta\n")
    llm.hold()
    page = app()
    page.select_option("#terms", "terms.txt")
    page.click("#run")
    expect(page.locator("#msg")).to_have_text("0/2 — charlie")
    page.select_option("#plugin", label="Russian → Chinese")
    page.locator("#body tr").click()
    expect(page.locator("#sel")).to_have_text("1 selected of 1")

    with page.expect_response(lambda r: "after_run" in r.url):
        llm.release()

    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#body tr b")).to_have_text(["кузнец"])
    expect(page.locator("#sel")).to_have_text("1 selected of 1")

    page.select_option("#plugin", label="English → Russian")
    expect(page.locator("#body tr.new b")).to_have_text(["delta", "charlie"])


def test_export_writes_the_selected_cards(app, seed_cards):
    """EX-5, EX-6, EX-7: the selected cards go to the file the user saves,
    tab-separated, one per line in id order, without the id; the count and name are shown."""
    ids = seed_cards(*TERMS)
    page = app()
    stub_dialog(page, "mine.tsv")
    row(page, ids[3]).click()
    row(page, ids[0]).click()

    page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Saved 2 cards")
    expect(page.locator("#exmsg")).to_contain_text("mine.tsv")
    lines = saved(page).splitlines()
    assert lines[0] == "#separator:tab"
    assert [line.split("\t") for line in lines[1:]] == [
        [
            "alpha",
            "/alpha/",
            "перевод alpha",
            "meaning of alpha",
            "B2",
            "An example with alpha",
            "An example with _alpha_",
        ],
        [
            "delta",
            "/delta/",
            "перевод delta",
            "meaning of delta",
            "B2",
            "An example with delta",
            "An example with _delta_",
        ],
    ]


def test_export_asks_where_to_save_with_a_default_name(app, seed_cards):
    """EX-5: the save dialog is offered ankicards_<date>_<time>.tsv, and nothing
    is put in the data folder."""
    seed_cards(*TERMS)
    page = app()
    stub_dialog(page)
    page.click("#all")

    page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Saved 5 cards")
    [options] = page.evaluate("window.dialogCalls")
    assert re.fullmatch(r"ankicards_\d{8}_\d{6}\.tsv", options["suggestedName"])
    assert list(config.DATA_FOLDER.iterdir()) == []


def test_leaving_the_save_dialog_saves_nothing(app, seed_cards):
    """EX-11: leaving the dialog writes nothing and says so."""
    seed_cards(*TERMS)
    page = app()
    stub_dialog(page, None)
    page.click("#all")

    page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Cancelled, nothing saved")
    expect(page.locator("#exmsg")).not_to_have_class("err")
    assert page.evaluate("window.saved") is None


def test_without_a_save_dialog_the_file_is_downloaded(app, seed_cards):
    """EX-5: where the browser has no save dialog for pages, the file is downloaded under the default name."""
    seed_cards(*TERMS)
    page = app()
    page.evaluate("window.showSaveFilePicker = undefined")
    page.click("#all")

    with page.expect_download() as download:
        page.click("#export")

    assert re.fullmatch(
        r"ankicards_\d{8}_\d{6}\.tsv", download.value.suggested_filename
    )
    lines = open(download.value.path(), encoding="utf-8").read().splitlines()
    assert lines[0] == "#separator:tab" and len(lines) == 6
    expect(page.locator("#exmsg")).to_contain_text("Saved 5 cards")
    expect(page.locator("#exmsg")).to_contain_text("to Downloads as ankicards_")


def test_export_with_nothing_selected(app, seed_cards):
    """EX-8: exporting an empty selection writes nothing and says so."""
    seed_cards(*TERMS)
    page = app()
    expect(page.locator("#body tr")).to_have_count(5)
    stub_dialog(page)

    page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Nothing selected")
    assert page.evaluate("window.dialogCalls") == []


def test_mixed_scripts_are_shown_and_exported_as_on_the_card(app, data):
    """EX-9, CL-1: a Russian → Chinese card with all three scripts is listed and exported unchanged."""
    data("terms.txt", "кузнец, 铁匠 (smith)\n")
    page = app()
    page.select_option("#plugin", label="Russian → Chinese")
    page.select_option("#terms", "terms.txt")
    page.click("#run")
    expect(page.locator("#body tr b")).to_have_text(["кузнец, 铁匠 (smith)"])
    page.click("#lastrun")
    stub_dialog(page)

    page.click("#export")

    expect(page.locator("#exmsg")).to_contain_text("Saved 1 card")
    lines = saved(page).split("\n")
    assert lines[1].split("\t")[0] == "кузнец, 铁匠 (smith)"
    assert lines[1].split("\t") == page.locator("#body tr td").all_inner_texts()[2:]
