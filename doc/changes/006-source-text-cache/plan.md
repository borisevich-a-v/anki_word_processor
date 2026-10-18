# 006 Source text cache: plan

The cache stays as it is: one file per prepared text in `data/.cache`, named
by a hash of the format version, the language and the text.

- `src/search.py`: after a text is prepared and its file written, every other
  cache file is checked against the files now in the data folder. For each
  readable file there, in each language, the name its cache file would have is
  computed; cache files with any other name are deleted. The file just written
  is always kept.
- This runs only when a text is prepared (a cache miss), never on a hit, so a
  run on an unchanged text costs nothing extra. Hashing the data folder takes
  milliseconds next to the seconds of preparing a text.
- Files of an earlier format version carry another hash, so they are deleted
  by the same rule; no separate handling.
- `src/config.py`: the encoding a terms file or source text is read in gets
  one name, because the cleanup must read the data folder exactly as a run
  does. `src/process_words.py` uses it.
- The 12 unreadable files in the developer's `data/.cache` are deleted by
  hand as part of this change.

## Tests

`tests/test_search.py`, CF-10: an unchanged text is prepared once; a changed
file, a removed file and a file of unknown origin lose their cache files when
a text is next prepared, and the files of texts still in the data folder stay.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: CF-10 written first. It names no file or format. |
| II. Core and frontend | Served: all of it is in the core; nothing is printed. |
| III. Tested offline | Served: CF-10 has tests; they need no network. |
| IV. No new technology | None added. |
