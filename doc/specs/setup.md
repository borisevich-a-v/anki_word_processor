
# Setup

What the tool needs from the user's machine before it can be used: where it
reads and writes files, where it keeps the cards, and how it is allowed to
write cards. What is done with these is in
[making-cards.md](making-cards.md) and [export.md](export.md).

## User scenarios

I put my terms files and source texts into one folder next to the tool. I give the tool my OpenAI API key
once and do not enter it again. When I start the tool it tells me the address
of its page, and I open it in the browser myself.

When I want to try the tool, or hunt a bug, without risking my real cards, I
start it as the stage profile. It has its own files and its own cards, writes
cards without calling any LLM, and its page shows plainly that it is the stage
profile. I can have it open beside the real one.

## Acceptance criteria

- **SU-1 Data folder.** Each profile (SU-5) has its own folder inside the folder
  `data` in the tool's own folder: `data/prod` for the real profile and
  `data/stage` for the stage profile. Terms files and source texts are read
  from the folder of the profile in use; the card store (SU-2), which lies in
  that folder too, is never offered as one of them. Where export files go is the user's
  choice (EX-5 in [export.md](export.md)).
- **SU-2 Card store.** The cards of a profile are kept in one file,
  `internal.db`, inside that profile's folder (SU-1). Removing that file
  removes all cards of that profile and no others.
- **SU-3 API key.** Card writing with a real LLM needs an OpenAI API key. The
  tool takes it from `OPENAI_API_KEY`, set either in the environment or in a
  file `.env` in the tool's own folder. Without a key a run cannot proceed and
  the user sees an error (MC-13 in [making-cards.md](making-cards.md)). The
  stage profile needs no key unless it is told to use the real LLM (SU-6).
- **SU-4 Starting.** When the tool is started it prints the address of its
  page. It does not open a browser.
- **SU-5 Profiles.** The tool runs as one of two profiles: `prod`, the real
  one, and `stage`, for trying and testing by hand. The user picks the profile
  when starting the tool by setting `PROCESS_ANKI_PROFILE`. Unset, the profile
  is `prod`; any value other than `prod` and `stage` is an error and the tool
  does not start. The tool prints the profile it runs as. A profile's folder
  (SU-1) is created when the tool starts, if it is missing. Nothing the stage
  profile does reads or changes anything of the `prod` profile.
- **SU-6 Stage card writer.** The stage profile writes cards without any LLM,
  offline and free: a card is made up from the term, and a term starting with
  `fail-` or `bad-` gives a failed card or a card that breaks a field rule,
  so errors can be tried. If `PROCESS_ANKI_REAL_LLM=1` is set, the stage
  profile uses the real LLM instead (SU-3); then `PROCESS_ANKI_MODEL` may name
  the model, and unset it is `gpt-5-nano`. The `prod` profile always uses the real LLM and
  its own model, and ignores both variables.
- **SU-7 Stage is recognisable and separate.** The page of the stage profile
  says so on every screen (a banner and the page title), and it is served on
  another address than `prod`'s, so both can run at once.

## History

- 007-unspecified-behaviour: spec written to describe existing behaviour,
  except SU-4, which is new: the tool no longer opens the browser.
- 009-save-dialog: SU-1 no longer says export files are written to the data
  folder.
- 011-stage-profile: data and card store move into a folder per profile
  (SU-1, SU-2); profiles, the stage card writer and its marker added (SU-5 to
  SU-7); SU-3 says the stage profile needs no key.
