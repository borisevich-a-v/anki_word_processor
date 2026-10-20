"""Export from internal DB into anki format"""

import csv
import io
from dataclasses import dataclass
from datetime import datetime

from core.card_library import list_cards
from core.languages.base import Plugin


@dataclass(frozen=True)
class ExportResult:
    count: int
    content: bytes | None  # the file to save; None when no card was selected
    suggested_name: str


def default_file_name(now: datetime) -> str:
    return f"ankicards_{now:%Y%m%d_%H%M%S}.tsv"


def export_cards(plugin: Plugin, ids: list[int]) -> ExportResult:
    """The cards with these ids as the text of a file for Anki; saving it is up to the caller."""
    name = default_file_name(datetime.now())
    wanted = set(ids)
    rows = [card[1:] for card in list_cards(plugin) if card[0] in wanted]
    if not rows:
        return ExportResult(0, None, name)
    out = io.StringIO(newline="")
    out.write("#separator:tab\n")  # read by Anki
    csv.writer(out, delimiter="\t", lineterminator="\n").writerows(rows)
    return ExportResult(len(rows), out.getvalue().encode("utf-8"), name)
