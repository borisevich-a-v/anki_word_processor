import csv

from openai import OpenAI
from pydantic import BaseModel, Field

from dotenv import load_dotenv

import sqlite3

con = sqlite3.connect("tutorial.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cards(word, phonetic_transcription, russian_translation, explanation, level, example, exercise)")

load_dotenv()

client = OpenAI()


class AnkiCard(BaseModel):
    word: str = Field(min_length=2, max_length=25)
    phonetic_transcription: str = Field(min_length=3, max_length=300)
    russian_translation: str = Field(min_length=4, max_length=300)
    explanation: str = Field(min_length=5, max_length=300)
    level: str = Field(min_length=2, max_length=3)
    example: str = Field(min_length=5, max_length=300)
    exercise: str = Field(min_length=5, max_length=300)


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
6. example - Example with context. A short example, up to 10 words.
7. exercise - The same example as in the p.7 but with the target world replaced with russian translation

Use search, but do not add citation, I need your reformulated results

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
"""


def process_cards(card) -> AnkiCard:
    result = client.responses.parse(
        model="gpt-5-mini",
        tools=[{"type": "web_search_preview"}],
        input=prompt.format(input_card=str(card)),
        text_format=AnkiCard,
    ).output_parsed
    return result

def save_card(card: AnkiCard, index: int) -> None:
    cur.execute(
        f"INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?)",
        (card.word, card.phonetic_transcription, card.russian_translation, card.explanation, card.level, card.example, card.exercise)
    )
    con.commit()
    print("saved to SQL")

def is_processed(word: str) -> bool:
    res = cur.execute(f"""SELECT 1 FROM cards WHERE word="{word}" """).fetchone()
    return bool(res)


def main():
    cards = []
    with open("anki_clean_nohtml.tsv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, row in enumerate(reader):
            word = row[0]
            if not is_processed(word):
                cards.append(row)
            else:
                print(f"Skipping {word}")


    for card, _ in zip(cards, range(30)):
        print(f"Processing {card[0]}")
        processed_card = process_cards(card)
        save_card(processed_card, i)

main()
