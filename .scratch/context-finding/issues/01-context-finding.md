# Context finding

Status: resolved

Finds places in the source text where a term is used, so the card can show it
in real use. A term is a single word or a phrase, as defined in
[making-cards.md](../../making-cards/issues/01-making-cards.md); "word" here always means one single word.
Used by making cards when the user provides a source text; a run without one
skips context finding.

## User scenarios

I give the tool a book and the terms I marked in it. A term can be one word or
several words with commas and dashes in it. For each one the tool finds the
passages where it occurs, even when the text has it in another grammatical
form, and uses those passages when writing the card.

## Acceptance criteria

- **CF-1 Passages.** A found context is a passage of roughly fifty words
  around the place where the term occurs. Near the beginning or end of the
  text it is the first or last fifty words. A passage is one line of text:
  line breaks and runs of spaces in the source come out as single spaces.
- **CF-2 Exact form first.** The term is first searched as written. Only if
  that finds nothing is it searched by dictionary form, so that "went" finds
  "go" and "goes".
- **CF-3 Whole words.** Matching is by whole words, ignoring case. A term does
  not match inside a longer word.
- **CF-8 Punctuation.** Commas, dashes and other punctuation are ignored on
  both sides: a term is found whether or not the text punctuates it the same
  way, and punctuation in the term never causes an error.
- **CF-4 Phrases.** For a term of several words, the closest kind of match
  wins: first the words next to each other in order; if none, the words close
  together in any order, with no more than five other words between the first
  and the last of them; if none, all the words within the same ten-word
  stretch of text.
- **CF-5 Results.** At most five contexts are returned, in the order they
  appear in the text. No passage is returned twice.
- **CF-6 Nothing found.** A term that does not occur in the text gives no
  contexts. This is not an error.
- **CF-7 One source per run.** A run searches only the source text chosen for
  that run, never text from an earlier run.
- **CF-9 Languages.** All of the above holds equally for English, Russian and
  Chinese source text. Dictionary forms (CF-2) follow the language of the
  source text, which is given by the language pair of the run (see MC-1 in
  [making-cards.md](../../making-cards/issues/01-making-cards.md)). Chinese is written without spaces
  between words; it is still matched and measured word by word.
- **CF-10 Repeated runs.** The first run on a source text prepares it for
  searching, which takes a while for a long text. What was prepared is kept:
  a later run on the same text, unchanged and in the same language, does not
  prepare it again. Only what belongs to the texts now in the data folder is
  kept. Whenever a text is prepared, what was kept for a text that has since
  been changed or removed, or kept by an earlier version of the tool, is
  removed.

## Known limits

- The text is cut into ten-word stretches. A term that falls across a cut is
  not found.
- Fewer than ten leftover words at the very end of the text are not searched.
