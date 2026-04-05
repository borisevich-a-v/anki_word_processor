from pathlib import Path
from typing import Generic, cast

from openai import OpenAI
import config

from search import find_exact_word, find_word, ingest_text
from plugins import Plugin, CardT


def format_context(data: list[tuple[str, str, str]]) -> str:
    return '\n'.join([f"[[{i + 1}]]: {r[2]}" for i, r in enumerate(data[:5])])


class WordsProcessor(Generic[CardT]):
    def __init__(
            self,
            plugin: Plugin[CardT],
            llm: OpenAI,
            source_text: Path,
            words: Path,
    ) -> None:
        self._plugin = plugin
        self._llm = llm
        self.words = words

        print("Ingesting text")
        ingest_text(self._plugin.nlp, source_text.read_text())

    def process_card(self, card) -> CardT:
        result = self._llm.responses.parse(
            model="gpt-5-mini",
            tools=[{"type": "web_search"}],
            input=self._plugin.PROMPT.format(input_card=str(card)),
            text_format=self._plugin.AnkiCard,  # type: ignore[invalid-argument-type]
        ).output_parsed
        if not result:
            raise ValueError("Empty card")
        return result

    def search_context_for_word(self, word: str) -> str:
        if res := find_exact_word(word):
            return format_context(res)
        if res := find_word(self._plugin.nlp, word):
            return format_context(res)
        return ''

    def get_target_words_from_file(self):
        words_to_process = []

        print("Reading words")
        target_words = self.words.read_text().splitlines()

        for word in target_words:
            if not self._plugin.is_processed(word):
                print("Found a word to process")
                words_to_process.append(word)
            else:
                print(f"Skipping {word}. As it was processed")
        return words_to_process

    def process_words(self):
        words_to_process = self.get_target_words_from_file()

        for word, _ in zip(words_to_process, range(config.MAX_CARDS_TO_PROCESS)):
            print(f"Processing word: {word}")

            card = f"<TARGET WORD>{word}</TARGET WORD>"
            context = self.search_context_for_word(word)
            print(f"For {word} found context: {context}")
            card += f"<CONTEXT OF USAGE>\n{context}\n<CONTEXT OF USAGE>"

            processed_card = self.process_card(card)
            self._plugin.save_card(processed_card)
