"""making-cards.md, as the user sees it in the browser."""

import threading

from playwright.sync_api import expect

from core import config
from web import app as ui
from core.store import db

SOURCE = (
    "The old smith said that his sons went astray many years ago "
    "and he never heard from them again after that winter."
)


def start_run(page, terms: str = "terms.txt", source: str = "source.txt") -> None:
    page.select_option("#source", source)
    page.select_option("#terms", terms)
    page.click("#run")


def stored_terms() -> list[str]:
    return [r[0] for r in db.fetchall("SELECT word FROM cards_ru ORDER BY rowid")]


def test_choices_come_from_the_data_folder(app, data):
    """MC-1: language pair, terms file and source text are offered for choosing;
    the source text can be left out."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\n")
    page = app()

    expect(page.locator("#plugin option")).to_have_text(
        ["English → Russian", "Russian → Chinese"]
    )
    expect(page.locator("#terms option")).to_have_text(
        ["Choose a file…", "source.txt", "terms.txt"]
    )
    expect(page.locator("#terms")).to_have_value("")  # nothing is chosen for the user
    expect(page.locator("#source option")).to_have_text(
        ["(none)", "source.txt", "terms.txt"]
    )
    expect(page.locator("#source")).to_have_value("")


def test_page_says_term_not_word(app):
    """002 naming, HP-7: the user reads "term" and "terms file", never "word" (help included)."""
    page = app()

    expect(page.locator("body")).to_contain_text("Terms file")
    expect(page.locator("body")).not_to_contain_text("word", ignore_case=True)


def test_run_makes_one_card_per_term(app, data):
    """MC-6, MC-11: every term gets a card and the summary says how many."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    page = app()

    start_run(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#summary .err")).to_have_count(0)
    expect(page.locator("#body tr")).to_have_count(2)
    expect(page.locator("#body tr b")).to_have_text(["smith", "astray"])
    assert stored_terms() == ["astray", "smith"]


def test_card_is_written_from_the_context(app, data, llm):
    """MC-6: the usage context from the source text reaches card writing."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\n")
    page = app()

    start_run(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    assert "his sons went astray" in llm.prompts[0]


def test_run_without_a_source_text(app, data, llm):
    """MC-1, MC-14: a run needs no source text; the card is complete, its example made up."""
    data("terms.txt", "astray\n")
    page = app()

    page.select_option("#terms", "terms.txt")
    page.click("#run")

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#body tr td")).to_contain_text(["example of astray"])
    assert "make the example up" in llm.prompts[0]


def test_blank_lines_repeats_and_punctuation(app, data):
    """MC-2, MC-3, MC-16: blank lines and repeats are not terms; a term with punctuation
    gets a card that shows it exactly as written."""
    data("terms.txt", "well, then; go — now\n\n   \nastray\nwell, then; go — now\n")
    page = app()

    start_run(page, source="")

    expect(page.locator("#report")).to_contain_text(
        "Terms in the file: 2. To process in this run: 2."
    )
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#body tr b")).to_have_text(["astray", "well, then; go — now"])


def test_report_is_shown_before_processing_and_stays(
    app, data, seed_cards, llm, monkeypatch
):
    """MC-15: the report names the totals, the terms with a card and those over the limit,
    is there while the run goes, and stays next to the summary."""
    monkeypatch.setattr(config, "MAX_CARDS_TO_PROCESS", 2)
    seed_cards("astray", "winter")
    data("terms.txt", "astray\nsmith\nwinter\nsons\nheard\nagain\n")
    llm.hold()
    page = app()

    start_run(page, source="")

    report = page.locator("#report")
    expect(report).to_contain_text("Terms in the file: 6. To process in this run: 2.")
    expect(report).to_contain_text("Already have a card: 2")
    expect(report.locator("details[open]")).to_have_count(0)  # names only on request
    expect(report.locator("ul").nth(0).locator("li")).to_have_text(["astray", "winter"])
    expect(report).to_contain_text("Limit reached: 2")
    expect(report.locator("ul").nth(1).locator("li")).to_have_text(["heard", "again"])
    expect(page.locator("#msg")).to_have_text("0/2 — smith")
    assert stored_terms() == ["astray", "winter"]

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(report).to_contain_text("Terms in the file: 6. To process in this run: 2.")
    expect(report.locator("li")).to_have_count(4)


def test_report_when_nothing_is_left_to_process(app, data, seed_cards, llm):
    """MC-15: with no term left the report says so and the run ends without making cards."""
    seed_cards("astray", "smith")
    data("terms.txt", "astray\nsmith\n")
    page = app()

    start_run(page, source="")

    expect(page.locator("#report")).to_contain_text("No term is left to process")
    expect(page.locator("#summary")).to_contain_text("Cards made: 0")
    assert llm.prompts == []
    assert stored_terms() == ["astray", "smith"]


def test_progress_is_shown_during_a_run(app, data, llm):
    """MC-10: done, total and the current term are visible while the run goes."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    llm.hold()
    page = app()

    start_run(page)

    expect(page.locator("#bar")).to_be_visible()
    expect(page.locator("#msg")).to_have_text("0/2 — astray")

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#bar")).to_be_hidden()


def test_term_with_a_card_is_not_made_again(app, data, seed_cards, llm):
    """MC-4: a term that already has a card is skipped."""
    seed_cards("astray")
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    page = app()

    start_run(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    assert len(llm.prompts) == 1
    assert stored_terms() == ["astray", "smith"]


def test_terms_over_the_limit_are_reported(app, data, monkeypatch):
    """MC-5, MC-11: terms beyond the limit are named and left for the next run."""
    monkeypatch.setattr(config, "MAX_CARDS_TO_PROCESS", 1)
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    page = app()

    start_run(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#summary")).to_contain_text("Limit reached: 1 left")
    expect(page.locator("#summary details li")).to_have_text(["smith"])
    assert stored_terms() == ["astray"]

    start_run(page)
    expect(page.locator("#body tr")).to_have_count(2)
    assert stored_terms() == ["astray", "smith"]


def test_failed_term_is_reported_and_the_run_goes_on(app, data):
    """MC-8, MC-11: a failure is shown with its reason; later terms still get cards."""
    data("source.txt", SOURCE)
    data("terms.txt", "fail-first\nastray\n")
    page = app()

    start_run(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#summary .err li")).to_have_text(["fail-first — LLM is down"])
    assert stored_terms() == ["astray"]


def test_invalid_card_is_not_saved(app, data):
    """MC-7: a card that breaks a field rule is reported as failed and not kept."""
    data("source.txt", SOURCE)
    data("terms.txt", "bad-level\nastray\n")
    page = app()

    start_run(page)

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#summary .err")).to_contain_text(
        "bad-level — level must be one of A1, A2, B1, B2, C1 or C2"
    )
    expect(page.locator("#summary .err")).not_to_contain_text("validation error")
    assert stored_terms() == ["astray"]


def test_cards_are_still_there_after_reopening(app, data):
    """MC-9: cards made by a run are shown when the tool is opened again."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    page = app()
    start_run(page)
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")

    page = app()

    expect(page.locator("#body tr b")).to_have_text(["smith", "astray"])


def test_cancel_keeps_the_cards_made_and_reports_the_rest(app, data, llm):
    """MC-17, MC-11: after a cancel the cards made so far stay, the other terms are
    reported as cancelled, and the next run makes them."""
    data("terms.txt", "astray\nsmith\nwinter\n")
    llm.hold()
    page = app()
    expect(page.locator("#cancel")).to_be_hidden()

    start_run(page, source="")
    expect(page.locator("#msg")).to_have_text("0/3 — astray")
    page.click("#cancel")
    expect(page.locator("#msg")).to_contain_text("Finishing the term in hand")
    expect(page.locator("#cancel")).to_have_text("Cancelling…")
    expect(page.locator("#msg")).not_to_contain_text("Cancelling")  # MC-17: said once
    llm.release()

    expect(page.locator("#summary")).to_contain_text("Cards made: 1")
    expect(page.locator("#summary")).to_contain_text("Cancelled: 2 left")
    expect(page.locator("#summary details li")).to_have_text(["smith", "winter"])
    expect(page.locator("#cancel")).to_be_hidden()
    assert stored_terms() == ["astray"]

    page.click("#run")
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    assert stored_terms() == ["astray", "smith", "winter"]


def test_run_with_an_empty_data_folder_shows_an_error(app):
    """MC-13: with no terms file to choose, starting a run shows an error."""
    page = app()
    expect(page.locator("#terms option")).to_have_count(1)  # only "Choose a file…"

    page.click("#run")

    expect(page.locator("#msg .err")).to_contain_text("No terms file")
    expect(page.locator("#report")).to_be_empty()
    expect(page.locator("#summary")).to_be_empty()

    page.click("#run")  # the failed run does not block the next one
    expect(page.locator("#note")).to_be_empty()


def test_run_shows_that_it_is_starting(app):
    """MC-10: until the first term is reached, the user sees that the run is starting."""
    ui._job = ui.Job(state="running")  # started, no term reached yet
    page = app()

    expect(page.locator("#msg")).to_have_text("Starting…")


def test_run_does_not_depend_on_the_page(app, data, llm):
    """MC-20: a run goes on when the page is reloaded; the page opened again shows the
    run in progress, and afterwards the report and summary of the last run."""
    data("terms.txt", "astray\nsmith\n")
    llm.hold()
    page = app()
    start_run(page, source="")
    expect(page.locator("#msg")).to_have_text("0/2 — astray")

    page = app()
    expect(page.locator("#msg")).to_have_text("0/2 — astray")
    expect(page.locator("#report")).to_contain_text("Terms in the file: 2.")
    page.goto("about:blank")  # nobody is looking
    llm.release()
    for thread in threading.enumerate():
        if "run_job" in thread.name:
            thread.join(timeout=30)
    assert stored_terms() == ["astray", "smith"]

    page = app()
    expect(page.locator("#report")).to_contain_text("Terms in the file: 2.")
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    expect(page.locator("#body tr.new b")).to_have_text(["smith", "astray"])


def test_second_run_is_refused_while_one_is_going(app, data, llm):
    """MC-12: starting a run during a run gives a message and does not disturb it."""
    data("source.txt", SOURCE)
    data("terms.txt", "astray\nsmith\n")
    llm.hold()
    page = app()
    start_run(page)
    expect(page.locator("#msg")).to_have_text("0/2 — astray")

    page.click("#run")
    expect(page.locator("#note")).to_have_text("A run is already in progress")
    expect(page.locator("#msg")).to_have_text("0/2 — astray")

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")
    assert stored_terms() == ["astray", "smith"]


def test_unreadable_file_shows_an_error(app, data):
    """MC-13: when the run cannot proceed, the user sees the error, not a report or summary."""
    data("source.txt", SOURCE)
    data("terms.bin", b"\xff\xfe\xff\xff not text")
    page = app()

    start_run(page, terms="terms.bin")

    expect(page.locator("#msg .err")).not_to_be_empty()
    expect(page.locator("#report")).to_be_empty()
    expect(page.locator("#summary")).to_be_empty()
    expect(page.locator("#body tr")).to_have_count(0)


def test_choices_are_remembered_and_nothing_else_is_chosen(app, data):
    """MC-21: the last language pair, terms file and source text are offered again."""
    data("a.txt", "astray\n")
    data("b.txt", "smith\n")
    page = app()
    expect(page.locator("#terms")).to_have_value("")

    page.select_option("#plugin", label="Russian → Chinese")
    page.select_option("#terms", "b.txt")
    page.select_option("#source", "a.txt")

    page = app()
    expect(page.locator("#terms")).to_have_value("b.txt")
    expect(page.locator("#source")).to_have_value("a.txt")
    expect(page.locator("#plugin")).to_have_value("1")
    expect(page.locator("#cardstitle")).to_have_text("Cards: Russian → Chinese")

    page.evaluate("localStorage.clear()")
    page.reload()
    expect(page.locator("#terms")).to_have_value("")


def test_the_same_file_twice_is_warned_about_and_cannot_start(app, data):
    """MC-22: the same file as terms and source gives a warning and no run."""
    data("terms.txt", "astray\n")
    page = app()

    page.select_option("#terms", "terms.txt")
    page.select_option("#source", "terms.txt")

    expect(page.locator("#samewarn")).to_contain_text("must be different files")
    expect(page.locator("#run")).to_be_disabled()
    page.select_option("#source", "")
    expect(page.locator("#samewarn")).to_be_empty()
    expect(page.locator("#run")).to_be_enabled()


def test_the_same_file_twice_is_a_run_error(app, data):
    """MC-22, MC-13: a run started with the same file twice (the page's warning bypassed)
    shows the error."""
    data("terms.txt", "astray\n")
    page = app()
    page.select_option("#terms", "terms.txt")
    page.select_option("#source", "terms.txt")
    page.evaluate("document.getElementById('run').disabled = false")

    page.click("#run")

    expect(page.locator("#msg .err")).to_contain_text("different files")
    assert stored_terms() == []


def test_progress_shows_elapsed_time_and_a_cancel_next_to_it(app, data, llm):
    """MC-10: elapsed time during the run; cancel sits in the progress line."""
    data("terms.txt", "astray\nsmith\n")
    llm.hold()
    page = app()
    start_run(page, source="")
    expect(page.locator("#msg")).to_have_text("0/2 — astray")

    expect(page.locator("p.progress #timing")).to_contain_text("Elapsed 0:")
    expect(page.locator("p.progress #cancel")).to_be_visible()
    expect(page.locator("#timing")).not_to_contain_text("left")  # no term done yet

    llm.release()
    expect(page.locator("#summary")).to_contain_text("Cards made: 2")


def test_remaining_time_is_estimated_when_a_term_is_done_and_does_not_move_between():
    """MC-10: the estimate comes from the latest terms, is renewed only when a term is
    finished, and so does not climb while a term is being made."""
    job = ui.Job(state="running", started=0.0)
    job.start_term(0, 3, "a", now=0)
    assert "left" not in job.timing(now=5)  # no term done yet
    job.start_term(1, 3, "b", now=20)
    assert job.timing(now=21) == "Elapsed 0:21, under a minute left"
    assert job.timing(now=50) == "Elapsed 0:50, under a minute left"  # no climb
    job.start_term(2, 20, "c", now=60)  # 2 terms done: the first one is left out
    assert job.timing(now=61) == "Elapsed 1:01, about 12 min left"  # 40 s * 18


def test_the_estimate_follows_only_the_latest_terms():
    """MC-10: an old slow start does not weigh on the estimate for ever."""
    job = ui.Job(state="running", started=0.0)
    now = 0.0
    job.start_term(0, 20, "t0", now=now)
    for n in range(1, 8):
        now += 100 if n == 1 else 10
        job.start_term(n, 20, f"t{n}", now=now)

    assert job.timing(now=now) == f"Elapsed {ui.clock(now)}, about 2 min left"


def test_copy_failed_terms_and_run_again(app, data, llm, context):
    """MC-23: failed terms can be copied one per line, and the same run started again."""
    data("terms.txt", "fail-first\nastray\nfail-second\n")
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page = app()
    start_run(page, source="")
    expect(page.locator("#summary")).to_contain_text("Cards made: 1")

    page.click("#copyfailed")

    expect(page.locator("#cardmsg")).to_have_text("Failed terms copied")
    assert page.evaluate("navigator.clipboard.readText()") == "fail-first\nfail-second"

    before = len(llm.prompts)
    page.click("#again")
    expect(page.locator("#summary")).to_contain_text("Failed: 2")
    assert len(llm.prompts) == before + 2  # only the failed terms were tried again
    assert stored_terms() == ["astray"]


def test_first_use_says_where_to_put_files_and_finds_them(app, data):
    """MC-24: with no files the page says where the folder is; a new file is found when the
    user goes to choose, without reloading, and the choices made are kept."""
    page = app()
    expect(page.locator("#filehint")).to_contain_text(str(config.DATA_FOLDER))
    expect(page.locator("#empty")).to_contain_text("No cards yet")

    data("terms.txt", "astray\n")
    page.locator("#terms").dispatch_event("pointerdown")

    expect(page.locator("#terms option")).to_have_text(["Choose a file…", "terms.txt"])
    expect(page.locator("#filehint")).to_be_empty()
