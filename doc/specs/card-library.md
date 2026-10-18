# Card library

The cards the user has made: looking at them, correcting them and removing
the ones that are not wanted. How cards are made, and the fields and field
rules of each language pair, are in [making-cards.md](making-cards.md);
choosing cards and getting them into Anki is in [export.md](export.md).

## User scenarios

After a run I look through the cards. I notice a wrong translation and fix it
right in the list. Cards I do not want I select and delete.

## Acceptance criteria

### Browsing

- **CL-1 Card list.** For the chosen language pair the user sees all its
  cards, newest first, each with its id and its fields. The list says which
  language pair it shows, and the user can tell that the cards can be edited.
  A list with no cards has no column headings.
- **CL-2 Ids.** A card's id is unique within its language pair, larger than
  the id of every card made before it, including cards that have since been
  deleted, and never changes. The id of a deleted card is never given to
  another card.

### Editing

- **CL-3 Editing a card.** The user can change any field of a card, the term
  included, directly in the list. The card keeps its id and its place in the
  list, and stays selected or not selected as it was.
- **CL-4 Rules for an edit.** An edited card must still obey the field rules
  of its language pair (MC-7 in [making-cards.md](making-cards.md)), and its
  term must not be the term of another card of the same language pair (MC-4
  there). An edit that breaks a rule is refused: the user sees which rule, and
  the card stays as it was. When the rule broken is one of another field of the
  card (an older card may have such a field), the user is told that this other
  field has to be fixed too, and which rule it breaks, and sees which field it is.
- **CL-5 Abandoning an edit.** The user can leave an edit without changing the
  card, with Escape.
- **CL-11 Saving an edit.** Enter saves an edit. So does leaving the field in any other
  way, by clicking elsewhere or with Tab, which moves on to the next field of
  the card for editing; nothing is saved when the value is unchanged. A
  refused edit (CL-4), an empty value included, stays open with the reason
  shown when it was asked for with Enter or Tab; when the user leaves the
  field by clicking elsewhere the edit ends, the card stays as it was and the
  reason is shown. No other action starts on top of a field that is being
  edited. A field is edited in a box that shows long text in full. A field is
  one line: a line break typed or pasted into it is replaced by a space, and
  spaces at its start and end are not kept.
- **CL-6 Edits are kept.** An accepted edit is saved at once and is still
  there after the tool is restarted.

### Deleting

- **CL-7 Deleting selected cards.** The user can delete the selected cards
  (selecting is in [export.md](export.md), EX-3). Before anything is removed
  the user is asked to confirm, in a question that has to be answered before
  anything else is done, and is told how many cards will be deleted (in the
  singular for one) and which: their terms, the first few and how many more
  there are. When that is every card of the language pair, the user is told so
  plainly. Anything
  but confirming removes nothing. Deleting is kept apart from exporting so
  that one is not taken for the other.
- **CL-8 Nothing selected.** Deleting with no cards selected removes nothing
  and says so.
- **CL-9 Gone for good.** Deleted cards leave the list and the selection, are
  not recoverable and stay gone after the tool is restarted; the counts shown
  (EX-3) follow. Files exported earlier are not touched. A term whose card was
  deleted has no card any more (MC-4), so a later run may make it again.

### Keyboard and messages

- **CL-12 Keyboard.** Every card can be reached with the keyboard, and the
  card in focus is visible. Space selects or unselects it, Enter starts
  editing its first field, Delete asks to delete the selected cards (CL-7),
  and the arrow keys move between cards. After cards are deleted the focus
  goes to the card nearest to the deleted ones, or to the delete button when
  no card is left.
- **CL-13 Messages.** The outcome of an edit or a delete is shown at once,
  close to the action, and goes away by itself after a few seconds, a reason for a refused edit after
  about eight. Every message can be closed
  by the user, with a button or with Escape. A message never covers the card
  being edited or the cards below it.

### Runs

- **CL-10 During a run.** Editing and deleting work while a run is going; a
  run only adds cards, and a card of the run that is deleted simply leaves the
  list and the selection. The list shows each card as soon as it is made, not
  only when the run ends; the selection, the focus, the place in the list and a
  field being edited are not disturbed by that. While a field is being edited the list waits for it,
  and says that it waits and how many new cards there are; when the editing
  ends, the list is brought up to date, also if the run has ended meanwhile.

## History

- 010-card-library: spec written. CL-1 and CL-2 moved here from export.md
  (EX-1, EX-2); CL-2 also covers deleted cards. Editing (CL-3 to CL-6) and
  deleting (CL-7 to CL-10) are new.
- 012-ux-polish: the list names its language pair, editing is discoverable
  and saves when left (CL-1, CL-5, CL-11); confirming a delete is a question
  to answer first (CL-7); keyboard and messages (CL-12, CL-13).
- 013-ux-polish-2: the question says when every card goes (CL-7); leaving a
  refused edit abandons it, nothing else starts over an open edit (CL-11);
  focus after a delete (CL-12); messages can be closed (CL-13).
- 014-ux-polish-3: a field is one line, closed (CL-11); the question names the
  cards (CL-7); messages keep clear of the editing (CL-13); the list follows a
  run card by card (CL-10).
- 015-ux-polish-4: a refused edit names another field that must be fixed (CL-4);
  a waiting list says so (CL-10); errors go away by themselves (CL-13); fields
  lose surrounding spaces (CL-11); an empty list has no headings (CL-1).
- 016-term-case: a term may not equal another card's term in any letter case
  (CL-4).
- 017-help: the tips that were next to the list moved to the help ([help.md](help.md)).
- 019-newest-first: the list shows the newest card first (CL-1).
