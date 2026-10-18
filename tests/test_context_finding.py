"""context-finding.md."""

import pytest

from core import context_finding
from core.languages import En2RuPlugin, Ru2CnPlugin
from core.context_finding import SourceText
from core.languages.base import SpacyPipeline

EN = SpacyPipeline.ENGLISH
RU = SpacyPipeline.RUSSIAN
ZH = SpacyPipeline.CHINESE


def numbered(n: int, prefix: str = "w") -> list[str]:
    return [f"{prefix}{i}" for i in range(n)]


def spread(*sentences: str) -> str:
    """Ten-word sentences, far enough apart that each has a passage of its own."""
    parts = []
    for n, sentence in enumerate(sentences):
        assert sum(any(c.isalnum() for c in w) for w in sentence.split()) == 10
        parts += [sentence, *numbered(60, f"pad{n}x")]
    return " ".join(parts)


def test_passage_is_about_fifty_words_around_the_term():
    """CF-1: a context is some fifty words with the term inside."""
    words = numbered(200)
    source = SourceText(EN, " ".join(words))

    [context] = source.find("w100")

    assert context == " ".join(words[80:130])


def test_passage_at_the_edges_of_the_text():
    """CF-1: near the beginning it is the first fifty words, near the end the last."""
    words = numbered(200)
    source = SourceText(EN, " ".join(words))

    assert source.find("w3") == [" ".join(words[:50])]
    assert source.find("w195") == [" ".join(words[-50:])]


def test_passage_is_one_line():
    """CF-1: line breaks and runs of spaces in the source come out as single spaces."""
    words = numbered(200)
    text = "\n".join("   ".join(words[i : i + 7]) + "  \r\n" for i in range(0, 200, 7))
    source = SourceText(EN, text)

    assert source.find("w100") == [" ".join(words[80:130])]


def test_exact_form_is_searched_first():
    """CF-2: when the term occurs as written, other forms of it are not returned."""
    source = SourceText(
        EN,
        spread(
            "they go to the old market every morning with friends",
            "yesterday they went to the old market with their friends",
        ),
    )

    contexts = source.find("went")

    assert len(contexts) == 1
    assert "yesterday they went" in contexts[0]


def test_dictionary_form_is_searched_when_exact_finds_nothing():
    """CF-2: "went" finds "go" and "goes" when "went" itself is not in the text."""
    source = SourceText(
        EN,
        spread(
            "they go to the old market every morning with friends",
            "she goes to the old market every morning with friends",
        ),
    )

    contexts = source.find("went")

    assert len(contexts) == 2
    assert "they go to" in contexts[0]
    assert "she goes to" in contexts[1]


def test_whole_words_ignoring_case():
    """CF-3: case does not matter; a term inside a longer word is not a match."""
    source = SourceText(
        EN, spread("the Blacksmith sold all the armor he had wrought before")
    )

    assert source.find("blacksmith")
    assert source.find("ARMOR")
    assert source.find("smith") == []
    assert source.find("arm") == []


@pytest.mark.parametrize(
    "term",
    [
        "sons went astray",
        "sons, went astray",
        "sons — went; astray!",
        '"sons" (went) astray...',
    ],
)
def test_punctuation_is_ignored_on_both_sides(term):
    """CF-8: the term is found whether or not the text punctuates it the same way."""
    plain = SourceText(EN, spread("the smith said his sons went astray many years ago"))
    punctuated = SourceText(
        EN, spread('the smith said: his "sons", went — astray; many years ago')
    )

    assert plain.find(term)
    assert punctuated.find(term)


@pytest.mark.parametrize("term", ["—", ",;", '"', "(*)", "a-", 'NEAR("x" OR', "it's"])
def test_punctuation_in_a_term_never_fails(term):
    """CF-8: punctuation in the term never causes an error."""
    source = SourceText(
        EN, spread("the smith said his sons went astray many years ago")
    )

    assert source.find(term) == []


def test_phrase_adjacent_in_order_wins():
    """CF-4: when the words stand next to each other in order, only that is returned."""
    source = SourceText(
        EN,
        spread(
            "we saw that the cat was black and very old",
            "we saw the black cat again on the old roof",
            "black is one two three four five six seven cat",
        ),
    )

    contexts = source.find("black cat")

    assert len(contexts) == 1
    assert "the black cat again" in contexts[0]


def test_phrase_close_together_in_any_order_is_next():
    """CF-4: with no adjacent match, words close together in any order are returned."""
    source = SourceText(
        EN,
        spread(
            "we saw that the cat was black and very old",
            "black is one two three four five six seven cat",
        ),
    )

    contexts = source.find("black cat")

    assert len(contexts) == 1
    assert "the cat was black" in contexts[0]


def test_close_together_is_at_most_five_other_words_between():
    """CF-4: five other words between the first and the last word is close together,
    six is not."""
    source = SourceText(
        EN,
        spread(
            "black one two three four five six cat is here",
            "black one two three four five cat is over here",
        ),
    )

    contexts = source.find("black cat")

    assert len(contexts) == 1
    assert "five cat is over here" in contexts[0]


def test_phrase_within_the_same_stretch_is_last():
    """CF-4: with nothing closer, all the words within one ten-word stretch match."""
    source = SourceText(
        EN,
        spread(
            "black is one two three four five six seven cat",
            "this one has a black dog and nothing else here",
        ),
    )

    contexts = source.find("black cat")

    assert len(contexts) == 1
    assert "black is one two" in contexts[0]


def test_at_most_five_contexts_in_text_order():
    """CF-5: five contexts at most, in the order they appear in the text."""
    source = SourceText(
        EN,
        spread(
            *(
                f"in place number{i} the smith said nothing at all today"
                for i in range(8)
            )
        ),
    )

    contexts = source.find("smith")

    assert len(contexts) == 5
    for i, context in enumerate(contexts):
        assert f"number{i} " in context


def test_no_passage_is_returned_twice():
    """CF-5: two places that share a passage give that passage once."""
    words = numbered(200)
    words[3] = words[25] = "twice"
    source = SourceText(EN, " ".join(words))

    assert source.find("twice") == [" ".join(words[:50])]


def test_term_not_in_the_text():
    """CF-6: a term that does not occur gives no contexts and no error."""
    source = SourceText(EN, " ".join(numbered(200)))

    assert source.find("zebra") == []
    assert source.find("zebra crossing") == []
    assert SourceText(EN, "").find("zebra") == []


def test_each_source_text_is_searched_on_its_own():
    """CF-7: text from an earlier run is never searched."""
    earlier = SourceText(
        EN, spread("the smith said his sons went astray many years ago")
    )
    later = SourceText(
        EN, spread("nothing about that man or his family is written here")
    )

    assert later.find("astray") == []
    assert earlier.find("astray")


def test_russian_source_text():
    """CF-9, CF-2, CF-3, CF-4: Russian is found as written, by dictionary form, and by phrase."""
    source = SourceText(
        RU,
        spread(
            "вчера старый кузнец долго шёл домой через тёмный зимний лес",
            "Она вчера сказала, что кошки — очень умные и ласковые животные",
        ),
    )

    assert "кузнец долго шёл" in source.find("Кузнец")[0]
    assert "кошки — очень умные" in source.find("кошка")[0]
    assert "кошки — очень умные" in source.find("животное")[0]
    assert "кошки — очень умные" in source.find("кошки очень, умные")[0]
    assert source.find("кузнечик") == []
    assert source.find("куз") == []


def test_dictionary_forms_follow_the_language_of_the_source():
    """MC-1, CF-9: the source text is in the language of the terms, English for
    English → Russian and Russian for Russian → Chinese, and is searched in it."""
    english = spread("she goes to the old market every morning with friends")
    russian = spread("Она вчера сказала, что кошки — очень умные и ласковые животные")

    assert SourceText(En2RuPlugin.SOURCE_LANGUAGE, english).find("went")
    assert SourceText(Ru2CnPlugin.SOURCE_LANGUAGE, russian).find("кошка")


CHINESE = "我今天去了北京大学,看见很多学生在读书。老师说明天的天气非常好,我们可以一起去公园散步。"


def test_chinese_source_text_is_matched_word_by_word():
    """CF-9, CF-3, CF-8: Chinese has no spaces, and is still matched by whole words."""
    source = SourceText(ZH, CHINESE)

    [context] = source.find("学生")

    assert context in CHINESE
    assert "很多学生在读书" in context
    assert source.find("学") == []
    assert source.find("老虎") == []
    assert source.find("很多,学生。在") == [context]


def test_chinese_passage_is_measured_in_words():
    """CF-9, CF-1: a Chinese passage is fifty words, not fifty characters or the whole text."""
    filler = "我们今天一起去公园散步。"
    text = filler * 30 + "老师看见很多学生在读书。" + filler * 30
    source = SourceText(ZH, text)

    [context] = source.find("学生")

    assert context in text
    assert 50 < len(context) < 150


def cached() -> int:
    return len(list(context_finding.CACHE_DIR.glob("*.json")))


def test_unchanged_text_is_not_prepared_again(monkeypatch):
    """CF-10: a later run on the same text uses what the first one prepared."""
    prepared = []
    build = context_finding._build_rows
    monkeypatch.setattr(
        context_finding, "_build_rows", lambda *a: prepared.append(a) or build(*a)
    )
    text = " ".join(numbered(200))

    SourceText(EN, text)
    again = SourceText(EN, text)

    assert len(prepared) == 1
    assert again.find("w100") == [" ".join(numbered(200)[80:130])]


def test_texts_in_the_data_folder_stay_prepared(data, monkeypatch):
    """CF-10: preparing one text keeps what belongs to the others in the folder."""
    book, notes = " ".join(numbered(200, "b")), " ".join(numbered(200, "n"))
    data("book.txt", book)
    data("notes.txt", b"\xef\xbb\xbf" + notes.encode())  # with a byte order mark
    SourceText(EN, book)
    SourceText(EN, notes)
    monkeypatch.setattr(
        context_finding, "_build_rows", None
    )  # preparing again would fail

    SourceText(EN, book)
    SourceText(EN, notes)

    assert cached() == 2


def test_what_is_no_longer_needed_is_removed(data):
    """CF-10: a changed text, a removed text and data of unknown origin are dropped."""
    book, notes = " ".join(numbered(200, "b")), " ".join(numbered(200, "n"))
    data("book.txt", book)
    notes_file = data("notes.txt", notes)
    SourceText(EN, book)
    SourceText(EN, notes)
    (context_finding.CACHE_DIR / "from-an-earlier-version.json").write_text("[]")
    assert cached() == 3

    changed = book + " and one more line of the book was added here today"
    data("book.txt", changed)
    SourceText(EN, changed)

    assert cached() == 2  # the changed book and the notes

    notes_file.unlink()
    data("third.txt", " ".join(numbered(200, "t")))
    SourceText(EN, " ".join(numbered(200, "t")))

    assert cached() == 2  # the changed book and the third text
