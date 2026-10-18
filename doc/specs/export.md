# Export

Lets the user choose cards and write them to a file that Anki imports, saved
where the user wants. How cards are made is in
[making-cards.md](making-cards.md); the list of cards, and changing or
deleting them, is in [card-library.md](card-library.md).

## User scenarios

After a run I see my cards (see [card-library.md](card-library.md)), with the
new ones marked; nothing is selected for me, so no selection can be exported or
deleted by mistake. I select the new cards with one click, and older ones too if
I want, press export, say where to save the file and under what name, and import that
file into Anki.

## Acceptance criteria

### Selecting

- **EX-3 Selection.** The user can select and unselect single cards, a
  stretch of cards between two clicked ones, a range of ids, all cards,
  and the cards made in the last run. The number of selected
  cards is shown, next to the number of cards in the list and on the
  buttons that act on the selection.
- **EX-10 How selecting works.** Clicking anywhere on a card selects it, or
  unselects it if it was selected. Clicking a card with Shift held selects
  every card from the previously clicked one to this one; it never unselects.
  A range of ids includes both ends; with the first id left empty it starts
  at the oldest card, with the last id left empty it runs to the newest.
  Selecting a range, all cards or the cards of the last run replaces the
  selection instead of adding to it.
- **EX-4 After a run.** When a run finishes, the cards it made are marked as
  new. The run selects nothing and changes no selection: a selection made
  before or during the run stays as it is. A card stays marked as new, selected
  or not, also when the page is opened or reloaded later. Selecting the cards of
  the last run (EX-3) is one action away; when there are none to select, the user is
  told so (and told if the last run made none). A run that makes no cards leaves
  the marks of the run before as they were. If the user is looking at the cards of
  another language pair when the run finishes, that list and its selection are
  left as they are; the cards of the run are marked when the user goes back to
  the run's language pair.

### Exporting

- **EX-5 Where to save.** Export asks the user where to save the file and
  under what name, and writes the selected cards to one file there. The
  suggested name is `ankicards_` followed by the date and time of the export
  as `YYYYMMDD_HHMMSS`, and `.tsv`, for example
  `ankicards_20261004_153045.tsv`; the user may change it. Replacing an
  existing file is the user's decision, the same as in any save dialog. Where
  the browser does not let a web page ask for a place, it saves the file under
  the suggested name where it keeps downloads, and the user is told that this
  is what happened.
- **EX-6 Format.** The file is tab-separated UTF-8 text with one card per line
  in id order, the fields in the order given in
  [making-cards.md](making-cards.md), and no id. The file tells Anki that it
  is tab-separated, so commas and semicolons inside fields are never taken
  for separators.
- **EX-9 Scripts.** Latin, Cyrillic and Chinese text all come out in the file
  exactly as on the card, also when they are mixed in one card.
- **EX-7 Result.** After exporting, the user sees how many cards were written
  and the name of the file, right beside the export button. The result is short, on one
  line, and is gone as soon as the user changes the selection, edits or deletes
  a card.
- **EX-11 Cancelled.** If the user leaves the save dialog without saving,
  nothing is written and the user is told so, plainly as a choice and not
  as an error.
- **EX-8 Nothing selected.** Exporting with no cards selected asks for
  nothing, writes nothing and says so.

## History

- 001-baseline: spec written to describe existing behaviour.
- 007-unspecified-behaviour: existing behaviour written down. EX-10 added;
  EX-3 shows the size of the list; EX-4 covers a run finishing while another
  language pair is shown; EX-5 and EX-7 name the export file.
- 009-save-dialog: EX-5 rewritten: the user chooses where to save and the
  name, which defaults to `ankicards_<date>_<time>.tsv`, instead of one fixed
  file per language pair in the data folder. EX-11 added; EX-7, EX-8 adjusted.
- 010-card-library: EX-1 and EX-2 moved to card-library.md (CL-1, CL-2).
- 012-ux-polish: nothing is selected when the page is opened later (EX-4); the
  selection count is on the buttons (EX-3); EX-5, EX-7, EX-11 say where and how
  the result is shown.
- 013-ux-polish-2: new cards stay marked when selected (EX-4); the export
  result sits beside the export button (EX-7).
- 014-ux-polish-3: a run no longer selects its cards (EX-4); the export result
  is short and goes away when the selection or the cards change (EX-7).
- 015-ux-polish-4: selecting the last run says when there is nothing to select;
  a run of no cards keeps the earlier marks (EX-4).
