"""The stand-in for card writing, so that no test calls an LLM."""

import re
import threading
from types import SimpleNamespace

_TERM = re.compile(r"<TARGET WORD>(.*?)</TARGET WORD>", re.S)


class FakeLLM:
    """Stands in for the OpenAI client.

    Returns a valid card for the term in the prompt, with the term itself in
    upper case, as a real LLM may change its form. Except: a term starting with
    "fail-" raises, one starting with "bad-" gives a card that breaks a field
    rule. hold() makes calls wait until release(). prompts and tools keep
    what each call was given.
    """

    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.tools: list[list[dict]] = []
        self._open = threading.Event()
        self._open.set()
        self._free = 0  # calls let through before the hold applies
        self.responses = SimpleNamespace(parse=self._parse)

    def hold(self, after: int = 0) -> None:
        self._free = len(self.prompts) + after
        self._open.clear()

    def release(self) -> None:
        self._open.set()

    def _parse(self, *, input: str, text_format, tools=(), **_):
        self.prompts.append(input)
        self.tools.append(list(tools))
        if len(self.prompts) > self._free:
            self._open.wait(timeout=30)
        match = _TERM.search(input)
        assert match, "no term in the prompt"
        term = match.group(1)
        if term.startswith("fail-"):
            raise RuntimeError("LLM is down")
        fields = {name: f"{name} of {term}" for name in text_format.model_fields}
        fields["word"] = term.upper()
        if "exercise" in fields:
            fields["exercise"] = (
                f"exercise of {term}"
                if term.startswith("plain-")
                else f"example of _{term}_"
            )
        bad = term.startswith("bad-")
        if "level" in fields:
            fields["level"] = "Z9" if bad else "B2"
        elif bad:
            fields["explanation"] = ""
        return SimpleNamespace(output_parsed=text_format(**fields))
