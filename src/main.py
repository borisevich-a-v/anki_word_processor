from pathlib import Path

import click
from dotenv import load_dotenv
from openai import OpenAI

from export_cards import export_cards
from plugins import PLUGINS
from process_words import WordsProcessor

load_dotenv()

DATA_FOLDER = Path(__file__).parents[1] / "data"


def pick_plugin():
    click.echo("\nSelect plugin:")
    for i, plugin_cls in enumerate(PLUGINS):
        click.echo(f"  [{i}] {plugin_cls.NAME}")
    idx = click.prompt("Enter number", type=click.IntRange(0, len(PLUGINS) - 1))
    return PLUGINS[idx]()


def pick_file(prompt: str) -> Path:
    files = sorted(DATA_FOLDER.iterdir())
    click.echo(f"\n{prompt}")
    for i, f in enumerate(files):
        click.echo(f"  [{i}] {f.name}")
    idx = click.prompt("Enter number", type=click.IntRange(0, len(files) - 1))
    return files[idx]


def print_summary(result: dict):
    all_issues = (
        result["failed"]
        + [(w, "contains separator character") for w in result["skipped_separator"]]
        + [(w, "limit reached") for w in result["skipped_limit"]]
    )
    click.echo("")
    if not all_issues:
        click.echo(f"All {len(result['processed'])} words processed successfully.")
        return
    click.echo("=" * 40)
    click.echo("WARNING: The following words were NOT processed:")
    for word, reason in all_issues:
        click.echo(f"  - {word!r}  ({reason})")
    click.echo("=" * 40)


@click.command()
def main():
    lang_plugin = pick_plugin()
    source_text = pick_file("Select source text file:")
    words = pick_file("Select words file:")

    llm = OpenAI()

    processor = WordsProcessor(lang_plugin, llm, source_text, words)
    result = processor.process_words()
    export_cards(lang_plugin)
    print_summary(result)


if __name__ == "__main__":
    main()
