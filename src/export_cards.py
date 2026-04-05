"""Export from internal DB into anki format"""

import csv
from pathlib import Path

from db import db
from plugins.base_plugin import Plugin

DATA_FOLDER = Path(__file__).parents[1] / "data"


def export_cards(plugin: Plugin) -> None:
    output_file = DATA_FOLDER / f"{plugin.TABLE_NAME}.tsv"
    rows = db.fetchall(f"SELECT * FROM {plugin.TABLE_NAME}")
    with open(output_file, "w") as f:
        writer = csv.writer(f, delimiter="\t")
        for row in rows:
            writer.writerow(row)
    print(f"Exported {len(rows)} cards to {output_file}")
