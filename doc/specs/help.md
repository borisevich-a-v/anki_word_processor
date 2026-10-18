# Help

Telling the user how to use the tool, inside the tool. What the tool does is in
the other specs; help only describes it and adds no behaviour of its own. The
keys of the card list are in [card-library.md](card-library.md) (CL-12).

## User scenarios

I open the tool for the first time and do not know where to start. I press F1
and read how to go from a terms file to cards imported into Anki. Later I
forget how a field is edited or what the green mark means, and look it up
without leaving the page or losing my place.

## Acceptance criteria

- **HP-1 Opening and closing.** There is a help button, always in view, and
  F1 does the same as the button. Help opens in front of the page. It is
  closed with its own close button, with Escape, by clicking outside it, or
  with F1 pressed while it is open. A click inside it, its margins included,
  does not close it. F1 does not open the browser's own help.
- **HP-2 Nothing else on the page.** The page itself carries no usage tips;
  they are in help only.
- **HP-3 How to use the tool.** Help tells how to use the tool from start to
  end: where the terms file and the optional source text come from and what each
  is for, choosing the language pair, making cards, what the report and the
  progress mean, stopping a run and running again for the terms left,
  selecting cards, editing a field and how it is saved, deleting, exporting for
  Anki and importing the file there, and what the mark on the cards of the last
  run means. It names the folder the files go into.
- **HP-4 Keys.** Help lists the keys of the card list (CL-12 in
  [card-library.md](card-library.md)) and those of editing (CL-11 there),
  and F1 itself. On a device without a keyboard the keys are left out.
- **HP-5 Reading it.** Help is read from its start each time it opens. It
  scrolls when it is longer than the screen, with the close button always in
  reach, and fits a phone's screen.
- **HP-6 Leaves the work alone.** Help changes no selection, no focus in the
  list and no field being edited. F1 pressed while a field is being edited or
  a delete is being asked about opens nothing.
- **HP-7 Wording.** Help uses the words the page uses ("term", "terms file"),
  as in [making-cards.md](making-cards.md).

## History

- 017-help: spec written (the tips of the card list moved here and grew into
  a how-to); clicking outside closes it (HP-1).
