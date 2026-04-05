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


@click.command()
def main():
    lang_plugin = pick_plugin()
    source_text = pick_file("Select source text file:")
    words = pick_file("Select words file:")

    llm = OpenAI()

    processor = WordsProcessor(lang_plugin, llm, source_text, words)
    processor.process_words()
    export_cards(lang_plugin)


if __name__ == "__main__":
    main()
