print("Running export")

import sqlite3
import csv

OUTPUT_FILE = "anki_output.tsv"

con = sqlite3.connect("internal.db")
cur = con.cursor()

rows = cur.execute(
    "SELECT * FROM cards"
).fetchall()

with open(OUTPUT_FILE, "w") as f:
    writer = csv.writer(f, delimiter="\t")
    for row in rows:
        writer.writerow(row)

print("Finished successful")