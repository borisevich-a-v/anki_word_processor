# process_anki

A local, single-user tool that prepares Anki cards. You give it a list of
terms and, optionally, a source text where the terms are used; an LLM writes
one card per term, and the cards are exported to a file Anki imports.

Language pairs: English → Russian and Russian → Chinese. Runs on macOS and
Windows.

## Setup

Needs [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Put your OpenAI API key into a `.env` file in the project root:

```
OPENAI_API_KEY=...
```

## Use

```
uv run src/run.py
```

On Windows, `run.bat` does the same. The tool prints the address of its page;
open it in the browser.

Terms files and source texts are read from the `data/prod` folder. When you
export, the browser asks where to save the file; the suggested name is
`ankicards_<date>_<time>.tsv`. A terms file has one term per line. The cards are kept in
`data/prod/internal.db`. In the card list, double-click a field to edit it (Enter saves,
Escape cancels); select cards and press Delete selected to remove them.

### Stage profile (for trying things out)

```
PROCESS_ANKI_PROFILE=stage uv run src/run.py
```

It uses `data/stage` and `data/stage/internal.db`, so your real cards are
untouched, and its page (port 8766, marked STAGE) can be open beside the real
one (port 8765). Cards are written by a stand-in, with no key and no network;
a term starting `fail-` or `bad-` gives a failed or an invalid card. To use the
real LLM there, add `PROCESS_ANKI_REAL_LLM=1`; `PROCESS_ANKI_MODEL=<model>`
picks the model (default `gpt-5-nano`).

If you used an earlier version, move your files and `internal.db` into
`data/prod/` once.

## Development

What the tool does is described in [.scratch](.scratch) (one folder per aspect) and
[doc/specs](doc/specs). How changes are
made, and the commands for the tests and checks, are in
[AGENTS.md](AGENTS.md). `make` lists shortcuts for them and for starting
the tool (`make run`, `make stage`, `make check`, ...).
