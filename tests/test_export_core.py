"""export.md, at the core API."""

from datetime import datetime

from core.store import db
from core.export import default_file_name, export_cards
from core.languages import En2RuPlugin, Ru2CnPlugin

EN_CARD = (
    "naïve, café; résumé",
    "/naɪˈiːv/",
    "наивный, кафе; резюме",
    "доверчивый — «простой»",
    "B2",
    "A naïve, simple café",
    "A _наивный_, simple café",
)
CN_CARD = (
    "кузнец, ёж",
    "кузнец",
    "铁匠;刺猬",
    "тот, кто куёт (铁匠 = smith)",
    "Старый кузнец сказал: «铁匠» — это smith",
)


def add(table: str, card: tuple) -> int:
    columns = [c[1] for c in db.fetchall(f"PRAGMA table_info({table})")][1:]
    return db.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' * len(card))})",
        card,
    )


def lines_of(content: bytes | None) -> list[str]:
    assert content is not None
    return content.decode("utf-8").split("\n")


def test_file_format():
    """EX-6: UTF-8, marked as tab-separated for Anki, one card per line in id order,
    fields in card order, no id."""
    ids = [add("cards_ru", (term, *EN_CARD[1:])) for term in ("one", "two", "three")]

    result = export_cards(En2RuPlugin(), [ids[2], ids[0]])

    assert result.count == 2
    lines = lines_of(result.content)
    assert lines[0] == "#separator:tab"
    assert [line.split("\t") for line in lines[1:-1]] == [
        ["one", *EN_CARD[1:]],
        ["three", *EN_CARD[1:]],
    ]
    assert lines[-1] == ""


def test_default_name_is_ankicards_and_the_time():
    """EX-5: the suggested name is ankicards_YYYYMMDD_HHMMSS.tsv."""
    assert (
        default_file_name(datetime(2026, 10, 4, 15, 30, 45))
        == "ankicards_20261004_153045.tsv"
    )
    card = add("cards_ru", EN_CARD)
    assert export_cards(En2RuPlugin(), [card]).suggested_name.startswith("ankicards_")


def test_export_writes_no_file_of_its_own(data):
    """EX-5: where the file goes is the user's choice; the core leaves the data folder alone."""
    from core import config

    card = add("cards_ru", EN_CARD)
    export_cards(En2RuPlugin(), [card])
    assert list(config.DATA_FOLDER.iterdir()) == []


def test_scripts_and_separators_come_out_as_on_the_card():
    """EX-9, EX-6: Latin, Cyrillic and Chinese, mixed, with commas and semicolons, are written unchanged."""
    ru = add("cards_ru", EN_CARD)
    cn = add("cards_cn", CN_CARD)

    ru_content = export_cards(En2RuPlugin(), [ru]).content
    cn_content = export_cards(Ru2CnPlugin(), [cn]).content

    assert lines_of(ru_content)[1].split("\t") == list(EN_CARD)
    assert lines_of(cn_content)[1].split("\t") == list(CN_CARD)


def test_nothing_selected_writes_nothing():
    """EX-8: with no cards selected there is no content to save."""
    add("cards_ru", EN_CARD)

    result = export_cards(En2RuPlugin(), [])

    assert result.count == 0
    assert result.content is None
