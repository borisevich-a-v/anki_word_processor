# Making cards

Turns a list of terms into finished cards. A **term** is what one card
teaches: a single word or a phrase of several words. "Word" in the specs
always means one single word, never a term. A source text, when the user
provides one, shows each term in real use. How usage contexts are found is in
[context-finding.md](context-finding.md); looking at, correcting and deleting
the cards is in [card-library.md](card-library.md); getting cards into Anki is
in [export.md](export.md); where the data folder is and what card writing needs
is in [setup.md](setup.md).

## User scenarios

I pick a language pair and a terms file, optionally a source text, and start a
run. Without a source text the examples on the cards are made up. Before
anything is processed I see a report of what the run will do with my file:
which terms already have a card and which do not fit into this run. Then I see
which term is being worked on and how far the run is. At the end I see how
many cards were made and exactly which terms were not, with the reason for
each. The cards are kept: when I open the tool another day they are still
there, and terms that already have a card are not made again.

## Acceptance criteria

### Input

- **MC-1 Choices.** A run takes a language pair and a terms file, and
  optionally a source text file. Files are chosen from the tool's data folder.
  The source text is in the language of the terms: English for English →
  Russian, Russian for Russian → Chinese.
- **MC-21 Choices are remembered.** The tool remembers the last language pair,
  terms file and source text the user chose and offers them again the next
  time the page is opened, as long as the files are still there. Nothing else
  is chosen for the user: with no remembered choice, no terms file is
  preselected and a run cannot be started until one is chosen.
- **MC-22 Not the same file twice.** The terms file and the source text must be
  different files. The user is warned as soon as the same file is chosen for
  both and cannot start the run; a run started anyway ends as a run error
  (MC-13).
- **MC-18 Text files.** The terms file and the source text are UTF-8 text. A
  byte order mark at the start of either is accepted and is not part of the
  first term or of the text.
- **MC-2 Terms file.** Each line of the terms file is one term. A line that
  is empty or has only spaces is not a term: it is ignored and not counted or
  reported anywhere. Spaces at the start and the end of a line
  are not part of the term. A term that appears more than once in the file
  counts once, at its first place; the repeats are ignored the same way. Two
  lines are the same term when they are the same text once those spaces are
  removed, whatever the letter case: "Biceps" and "biceps" are one term. Of
  lines that differ only in case, the first one is kept, as written; a later
  one counts among the ignored repeats.
- **MC-3 Punctuation.** A term may contain punctuation. It is processed like
  any other term and its card keeps the term as written.
- **MC-4 Already has a card.** A term that has a card in the chosen language
  pair is not processed. A card has that term when its term field is the same
  text, whatever the letter case: a card for "Biceps" is a card for "biceps",
  and the card keeps its own spelling. Cards of other language pairs do not
  count. A card library that already holds cards whose terms differ only in
  case stays as it is; each of them makes that term count as having a card.
- **MC-5 Limit.** A run processes at most 100 terms. The remaining terms are
  reported as "limit reached" and are picked up by the next run.

### Cards

- **MC-6 One card per term.** Each processed term gives one card with the
  fields of its language pair (below); spaces at the start and the end of a
  field are not kept (also when the field is edited, CL-11). When a source text is given, the card is
  written using up to five usage contexts from it.
- **MC-16 Term on the card.** The card's term field is the term exactly as it
  was in the terms file, whatever form or case card writing would give it.
- **MC-14 No context.** When no source text is given, or the term is not found
  in it, the term still gets a complete card: its example is made up while the
  card is being made, and is stored with the card like any other field.
- **MC-19 Looking things up.** Card writing may look a term up on the web
  when it needs to. What it finds is put in the card's own words: a card
  carries no links and no citations.
- **MC-7 Invalid cards.** A card that breaks a field rule of its language pair
  is not saved, and its term is reported as failed. The rules are the lengths,
  the allowed values and the content rules in the tables below; for English →
  Russian the exercise must have its Russian translation set between
  underscores.
- **MC-8 Failures do not stop the run.** When a term fails, it is reported with
  the reason, nothing is saved for it, and the run continues with the next
  term. The reason is short and in plain words: for a card that broke a field
  rule it names the field and the rule, in the same words as a refused edit
  (CL-4 in [card-library.md](card-library.md)), never a raw technical error
  dump.
- **MC-9 Cards are kept.** A card is saved as soon as it is made and is still
  there after the tool is restarted, unless the user deletes it (CL-7 in
  [card-library.md](card-library.md)). Stopping a run midway keeps the cards
  made so far.

### Feedback

- **MC-15 Pre-run report.** Before the first term of a run is processed, the
  user sees a report on the terms file: how many terms it has, how many will
  be processed in this run, how many already have a card (MC-4) and how many
  are left out by the limit (MC-5), and, when there are any, how many repeated
  lines were ignored (MC-2). The report says which terms file and which
  language pair it is about. The names of those terms are not printed
  by default; the user can open each list when wanted. Processing then starts on its own,
  without waiting for the user. The report stays visible during the run and
  next to the summary. When no term is left to process, the report
  says so and the run ends without making cards; when the file has no terms at
  all, it says only that, without counts. When the user has chosen another language pair,
  terms file or source text after the run, the report and summary are shown
  as belonging to the earlier choices, so they are not taken for the new
  ones. A choice not yet made (MC-21) does not count as another one, and a
  run in progress is never shown as belonging to other choices. What the
  user can act on (copying, running again) is never dimmed.
- **MC-10 Progress.** During a run the user sees how many terms are done, how
  many there are in total, and the current term, how long the run has gone
  on and, once at least one term is done, roughly how long it still needs.
  Until the first term is reached, the user sees that the run is starting.
  The estimate is renewed only when a term is finished, and is based on how long
  the latest terms took, so that it does not rise and fall while a term is being
  made; the first term, which is often slower, is left out of it once
  a second one is finished until three are. It is given in whole minutes
  ("under a minute" when less), because it is not exact enough for seconds.
  The way to cancel (MC-17) is next to the progress. The number of terms done
  stays in sight while the user works down the list of cards.
- **MC-11 Summary.** After a run the user sees the number of cards made (also
  when it is none, including when every term already had a card) and
  every term that was not processed (when the file had no terms there is
  nothing to count and no number is given): failed (with reason, MC-8), limit reached
  or cancelled. Failed terms are listed with their reasons; terms left out by
  the limit or cancelled are given as one line each with their number, and
  their names can be opened.
- **MC-23 After a run.** The user can copy the failed terms, one per line, and
  can start the same run again with one action, which says which file it is
  for and how many terms are left. Such a run makes the terms
  that failed, were cancelled or were left out by the limit, because the
  terms with a card are skipped (MC-4). It uses the language pair, terms file
  and source text the report is about, whatever is chosen on the page now.
- **MC-17 Cancel.** The user can cancel a run at any point after starting
  it. Cards made before the cancel are kept (MC-9). The terms not yet
  processed are reported in the summary as "cancelled" and are picked up by
  the next run. The term being worked on at that moment either gets its
  complete card or is reported as cancelled. From the cancel until the run
  stops, the user sees, said once, that it is being cancelled and that the term
  in hand is being finished, and cannot cancel again. After a cancel a new run
  can be started.
- **MC-12 One run at a time.** Starting a run while another is in progress is
  refused with a message; the running one is not affected.
- **MC-13 Run errors.** If the run cannot proceed at all (for example a file
  cannot be read), the user sees the error instead of a report or summary.
- **MC-20 Leaving the page.** A run does not depend on the page staying open:
  it goes on when the page is closed or reloaded. Opening the page again shows
  the run in progress, or the report and summary (or error) of the last run.
  This is remembered only while the tool is running; after a restart the page
  shows no run.
- **MC-24 First use.** When the data folder has no file to choose from, the
  page says where the folder is and what to put in it. The lists of files follow
  the folder without a button and without reloading the page: they are read
  again when the user comes back to the page and whenever the user goes to
  choose a file, so a file added meanwhile is there to pick. The choices made
  are kept; a chosen file that has been removed from the folder is no longer
  chosen. When there are no cards yet, the empty list says how to get some.

## Language pairs

### English → Russian

| Field | Content | Length |
|---|---|---|
| term | the English term, as in the terms file | 2-100 |
| phonetic transcription | transcription of the term | 3-300 |
| Russian translation | usually one word, sometimes 2-5 | 4-300 |
| explanation | brief meaning in English or Russian, 3-10 words, 15 at most | 5-400 |
| level | one of A1, A2, B1, B2, C1, C2 | |
| example | short English example, up to 10 words | 5-300 |
| exercise | the example with the term replaced by its Russian translation, which is set between underscores, like `He went _заблудился_ astray`; a card without a pair of underscores around some text breaks the rule | 5-300 |

### Russian → Chinese

| Field | Content | Length |
|---|---|---|
| term | the Russian term, as in the terms file | 2-100 |
| first form | dictionary form; infinitive for verbs | 2-100 |
| Chinese translation | usually one word, sometimes 2-5 | 1-300 |
| explanation | brief meaning in Russian, 3-10 words, 15 at most | 1-400 |
| example | 5-20 words, taken from the context when there is one | 1-300 |

Lengths are in characters.

## Open questions

- [NEEDS CLARIFICATION] The explanation of an English → Russian card may be in
  English or in Russian, and cards made by one run mix both. Should it always be
  in one language, and which?

## History

- 001-baseline: spec written to describe existing behavior.
- 002-pre-run-report: added the pre-run report (MC-15) and cancelling a run
  (MC-17); terms that already have a card are now reported (MC-4); "word" replaced by "term" where a
  phrase is also meant.
- 007-unspecified-behaviour: existing behaviour written down. MC-18, MC-19
  and MC-20 added; MC-1 says which language the source text is in; MC-10 and
  MC-17 cover starting and cancelling; field contents of both language pairs
  completed.
- 010-card-library: MC-9 mentions deleting; the card list moved out of
  export.md into card-library.md.
- 012-ux-polish: choices remembered and the same file refused (MC-21, MC-22);
  plain failure reasons (MC-8); report and summary show counts, names on
  request (MC-15, MC-11); elapsed and remaining time, cancel next to progress
  (MC-10); copy failed terms and run again (MC-23); first use (MC-24).
- 013-ux-polish-2: the report names its file and pair, counts ignored repeats,
  is marked once the choices change, and an empty file is said to have no
  terms (MC-15, MC-11).
- 014-ux-polish-3: the exercise rule is stated and enforced (MC-7); the
  estimate does not move between terms (MC-10); a count of none is given too
  (MC-11); run again uses the report's own choices (MC-23); cancelling shows
  the term in hand and cannot be repeated (MC-17); an empty file gets no
  counts (MC-15). Closed: line breaks are replaced by a space (CL-3). Opened:
  language of the explanation.
- 015-ux-polish-4: terms and fields lose surrounding spaces (MC-2, MC-6); the
  old-results mark follows only a choice that was made, never a run in progress
  (MC-15); the estimate leaves out the slow first term and is in minutes, and
  the count stays in sight (MC-10); run again names the terms left (MC-23);
  cancelling is shown once (MC-17). Opened: letter case of terms.
- 016-term-case: terms are compared ignoring letter case (MC-2, MC-4); the first
  spelling is kept. Closed: letter case of terms.
- 018-auto-refresh-files: the lists of files follow the folder by themselves (MC-24).
