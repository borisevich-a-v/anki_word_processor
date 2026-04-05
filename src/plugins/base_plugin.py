from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel
from spacy import Language

CardT = TypeVar('CardT', bound=BaseModel)


class Plugin(ABC, Generic[CardT]):
    NAME: str
    TABLE_NAME: str
    PROMPT: str
    AnkiCard: type[CardT]
    nlp: Language

    @abstractmethod
    def is_processed(self, word: str) -> bool: ...

    @abstractmethod
    def save_card(self, card: CardT) -> None: ...
