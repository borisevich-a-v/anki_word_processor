from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel

from core.store import db
from core.terms import term_key


class SpacyPipeline(StrEnum):
    CHINESE = "zh_core_web_md"
    ENGLISH = "en_core_web_md"
    RUSSIAN = "ru_core_news_md"


CardT = TypeVar("CardT", bound=BaseModel)


class Plugin(ABC, Generic[CardT]):
    NAME: str
    TABLE_NAME: str
    PROMPT: str
    AnkiCard: type[CardT]
    FIELDS: list[str]  # what the user calls each field of a card, in card order
    SOURCE_LANGUAGE: SpacyPipeline

    def is_processed(self, word: str, except_id: int | None = None) -> bool:
        """Whether a card (other than except_id) has this term, in any letter case."""
        key = term_key(word)
        return any(
            term_key(term) == key
            for card_id, term in db.fetchall(f"SELECT id, word FROM {self.TABLE_NAME}")
            if card_id != except_id
        )

    @abstractmethod
    def save_card(self, card: CardT) -> int:
        """Stores the card and returns its id."""
