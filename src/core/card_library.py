"""The cards the user keeps: listing, correcting and deleting them."""

from dataclasses import dataclass

from pydantic import ValidationError

from core.languages.base import Plugin
from core.store import db


@dataclass(frozen=True)
class EditResult:
    ok: bool
    error: str = ""  # why the edit was refused
    value: str = ""  # what the field holds now (the value without surrounding spaces)
    fix: int | None = None  # another field of the card that has to be fixed first


def list_cards(plugin: Plugin, newest_first: bool = False) -> list[tuple]:
    """All cards as (id, *fields), oldest first unless newest_first."""
    order = "DESC" if newest_first else "ASC"
    return db.fetchall(f"SELECT * FROM {plugin.TABLE_NAME} ORDER BY id {order}")


def describe_error(plugin: Plugin, error: ValidationError, which: int = 0) -> str:
    """A broken field rule (the first by default), in plain words naming the field as the user knows it."""
    first = error.errors()[which]
    field = plugin.FIELDS[
        list(plugin.AnkiCard.model_fields).index(str(first["loc"][0]))
    ]
    ctx = first.get("ctx", {})
    match first["type"]:
        case "string_too_short":
            least = ctx["min_length"]
            why = (
                "must not be empty"
                if least == 1
                else f"must have at least {least} characters"
            )
        case "string_too_long":
            why = f"must have at most {ctx['max_length']} characters"
        case "literal_error":
            why = f"must be one of {ctx['expected']}".replace("'", "")
        case "value_error":
            why = str(ctx["error"])
        case _:
            why = first["msg"]
    return f"{field} {why}"


def edit_card(plugin: Plugin, card_id: int, field: int, value: str) -> EditResult:
    """Sets one field (by its place in the card) of a card, if the card stays valid."""
    card = db.fetchone(f"SELECT * FROM {plugin.TABLE_NAME} WHERE id=?", (card_id,))
    if card is None:
        return EditResult(False, "This card no longer exists")
    names = list(plugin.AnkiCard.model_fields)
    fields = dict(zip(names, card[1:]))
    value = value.strip()
    if value == fields[names[field]]:
        return EditResult(True, value=value)
    if field == 0 and plugin.is_processed(value, except_id=card_id):
        return EditResult(False, "Another card has this term")
    fields[names[field]] = value
    try:
        plugin.AnkiCard.model_validate(fields)
    except ValidationError as e:
        errors = e.errors()
        own = [i for i, x in enumerate(errors) if x["loc"][0] == names[field]]
        if own:
            return EditResult(False, describe_error(plugin, e, own[0]))
        other = names.index(str(errors[0]["loc"][0]))
        why = describe_error(plugin, e)
        return EditResult(
            False,
            f"fix the {plugin.FIELDS[other]} field too, this card breaks its rule: {why}",
            fix=other,
        )
    db.execute(
        f"UPDATE {plugin.TABLE_NAME} SET {names[field]}=? WHERE id=?", (value, card_id)
    )
    return EditResult(True, value=value)


def delete_cards(plugin: Plugin, ids: list[int]) -> int:
    """Removes the cards with these ids for good; returns how many there were."""
    existing = [card[0] for card in list_cards(plugin) if card[0] in set(ids)]
    marks = ", ".join("?" * len(existing))
    if existing:
        db.execute(
            f"DELETE FROM {plugin.TABLE_NAME} WHERE id IN ({marks})", tuple(existing)
        )
    return len(existing)
