from pydantic import BaseModel, Field

from db import db
from plugins import Plugin
from search import get_nlp, SpacyPipeline

TABLE_NAME = 'cards_cn'

db.execute(
    f"CREATE TABLE IF NOT EXISTS {TABLE_NAME}(word, first_form, chinese_translation, explanation, example)"
)


PROMPT = """
Your goal is to change the input card into the desired format.
<Input_card>
{input_card}
</Input_card>

The desired format is an object with
1. word - The word itself
2. first_form - начальная форма слова. Для глаголов это инфинитив.
3. chinese_translation - Translation (to chinese). Usually a single word, sometimes 2-5.
4. explanation - brief meaning of the word. Usually 3-10 words. 15 words is a hard limit. Should be in Russian.
5. example - Example with a context. A short example, up to 5-20 words. If there is a context - use it. Otherwise make it up.

Use search if it's required.
If you used search do not add citation, do not add links, I need you reformulate the search results.

Example:
Input:
['сминает двери', 'Три минуты до звонка. Засовываю ключ в замок, проворачиваю и захожу. Свет не горит, компьютеры выключены – лаборантки еще нет. Пшикаю на перчатки санитайзер – по протоколу. Кофе или туфли? Кофе: переобуться не успею. Включаю кулер. Лампочка загорается, но он не торопится просыпаться. Стягиваю с носа маску, раздеваюсь и сыплю в свою побитую временем чашку растворимый кофе.']

Output (but no comments, no markdown, no trailing texts):
{{
"word": "Пшикаю", # russian
"first_form": "пшикать", # russian
"chinese_translation": "喷", # chinese
"explanation": "Пшикать -- это разговорный глагол, означающий распылять жидкость или газ короткой струёй или мелкими каплями, обычно из баллончика, пульверизатора или спрея; при этом часто слышен звук «пшик»",  # russian
"example": "Пшикаю на перчатки санитайзер", # Russian
}}

Return ONLY valid JSON. No markdown. No comments
"""


class AnkiCard(BaseModel):
    word: str = Field(min_length=2, max_length=100)
    first_form: str = Field(min_length=2, max_length=100)
    chinese_translation: str = Field(min_length=1, max_length=300)
    explanation: str = Field(min_length=1, max_length=400)
    example: str = Field(min_length=1, max_length=300)


class Ru2CnPlugin(Plugin[AnkiCard]):
    NAME = "Russian → Chinese"
    TABLE_NAME = TABLE_NAME
    PROMPT = PROMPT
    AnkiCard = AnkiCard
    nlp = get_nlp(SpacyPipeline.CHINESE)

    def is_processed(self, word: str) -> bool:
        res = db.fetchone(f"SELECT 1 FROM {TABLE_NAME} WHERE word=?", (word,))
        return bool(res)

    def save_card(self, card: AnkiCard) -> None:
        db.execute(
            f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?)",
            (
                card.word,
                card.first_form,
                card.chinese_translation,
                card.explanation,
                card.example,
            ),
        )
        print("saved to SQL")
