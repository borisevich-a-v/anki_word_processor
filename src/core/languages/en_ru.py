import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.store import db
from core.languages import Plugin
from core.languages.base import SpacyPipeline

TABLE_NAME = "cards_ru"

COLUMNS = [
    "word",
    "phonetic_transcription",
    "russian_translation",
    "explanation",
    "level",
    "example",
    "exercise",
]
COLUMN_LIST = ", ".join(COLUMNS)
db.ensure_cards_table(TABLE_NAME, COLUMNS)


prompt = """
Your goal is to change the input card into the desired format.
<Input_card>
{input_card}
</Input_card>

The desired format is an object with
1. word - The word itself
2. phonetic_transcription - just a phonetic transcription for the target word.
3. russian_translation - Translation (to russian). Usually a single word, sometimes 2-5
4. explanation - brief meaning of the word. Usually 3-10 words. 15 words is a hard limit
5. level - How advanced this word is (A1-C2)
6. example - Example with context. A short example, up to 10 words. If there is a context - use it. Otherwise make it up.
7. exercise - The same example as in the previous point but with the target word replaced with its russian translation. The russian translation MUST be set between underscores, like _перевод_ (always a pair of underscores around it)

Use search if it's required. If the word is below C1 usually you don't need search
If you used search do not add citation, do not add links, I need you reformulate the search results.

Example:
Input:
['astray', 'His sons went astray — - ru: в неверном направлении; заблудившись']

Output (but no comments, no markdown, no trailing texts):
{{
"word": "astray", # english
"phonetic_transcription": "/əˈstreɪ/",
"russian_translation": "сбиться с пути", # russian
"explanation": "Сбиться с пути (Отклониться от правильного пути или направления или заблудились.)",  # english or russian
"level": "C1", # Put here just a level (e.g. B2).
"example": "His sons went astray", # english
"exercise": "His sons went _неправильный путь_", # main text is english, the target word in russian.
}}

Return ONLY valid JSON. No markdown. No comments
"""


class AnkiCard(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    word: str = Field(min_length=2, max_length=100)
    phonetic_transcription: str = Field(min_length=3, max_length=300)
    russian_translation: str = Field(min_length=4, max_length=300)
    explanation: str = Field(min_length=5, max_length=400)
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    example: str = Field(min_length=5, max_length=300)
    exercise: str = Field(min_length=5, max_length=300)

    @field_validator("exercise")
    @classmethod
    def translation_between_underscores(cls, value: str) -> str:
        if not re.search(r"_[^_\s][^_]*_", value):
            raise ValueError(
                "must have its Russian translation set between underscores, like _this_"
            )
        return value


class En2RuPlugin(Plugin[AnkiCard]):
    NAME = "English → Russian"
    TABLE_NAME = TABLE_NAME
    PROMPT = prompt
    AnkiCard = AnkiCard
    FIELDS = [
        "term",
        "phonetic transcription",
        "Russian translation",
        "explanation",
        "level",
        "example",
        "exercise",
    ]
    SOURCE_LANGUAGE = SpacyPipeline.ENGLISH

    def save_card(self, card: AnkiCard) -> int:
        return db.execute(
            f"INSERT INTO {TABLE_NAME} ({COLUMN_LIST}) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                card.word,
                card.phonetic_transcription,
                card.russian_translation,
                card.explanation,
                card.level,
                card.example,
                card.exercise,
            ),
        )
